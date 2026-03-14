"""
Tests for the Phase D frontier cognition runtime.

Covers:
  - FrontierState predicates (conservative, legibility pressure)
  - Store CRUD and event emission
  - Individual mandatory critics
  - Commitment gate (allow and block cases)
  - Router.propose() lifecycle
  - Distillation gate (evaluate and distill_branch)
"""

import tempfile
import unittest
from pathlib import Path

from src.csp_runtime.commitment import evaluate_commitment
from src.csp_runtime.critics import (
    anomaly_critic,
    completion_critic,
    degeneration_critic,
    evidence_critic,
    frame_critic,
    irreversibility_critic,
    legibility_critic,
    pressure_critic,
    run_critics,
)
from src.csp_runtime.distillation import distill_branch, evaluate_distillation
from src.csp_runtime.frontier_models import (
    ActionProposal,
    ActionType,
    BranchType,
    CriticCode,
    FindingSeverity,
    Frame,
    FrontierState,
    GapIssueLevel,
    GapType,
    MetacognitiveFinding,
    ParadigmCommitment,
    ParadigmDeathReason,
    ProblemShape,
    PressureReading,
    TaskGeometry,
    TrajectorySnapshot,
    UncertaintyAxis,
    WorkMode,
)
from src.csp_runtime.policies import DEFAULT_POLICY
from src.csp_runtime.router import Router
from src.csp_runtime.store import Store


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_state(task_id: str = "task_1", branch_id: str = "br_test") -> FrontierState:
    """A clean state with two live frames — passes frame_critic baseline."""
    f1 = Frame(
        frame_id="f1",
        description="Frame one",
        assumptions=["assumes locality"],
        predictions=["predicts X"],
        evidence_for=[],
        evidence_against=[],
        confidence=0.6,
    )
    f2 = Frame(
        frame_id="f2",
        description="Frame two",
        assumptions=["assumes non-locality"],
        predictions=["predicts Y"],
        evidence_for=[],
        evidence_against=[],
        confidence=0.4,
    )
    return FrontierState(
        task_id=task_id,
        branch_id=branch_id,
        frames={"f1": f1, "f2": f2},
    )


def _minimal_proposal(
    action_type: ActionType = ActionType.PROBE,
    irreversibility: float = 0.1,
    evidence_gain: float = 0.8,
    anomalies: list[str] | None = None,
) -> ActionProposal:
    return ActionProposal(
        proposal_id="prop_test",
        action_type=action_type,
        payload_ref="ref::noop",
        rationale="test proposal",
        frame_id="f1",
        expected_evidence_gain=evidence_gain,
        expected_irreversibility=irreversibility,
        touched_anomalies=anomalies or [],
    )


def _tmp_store() -> Store:
    """Create a Store backed by a temp file (auto-cleaned by test teardown)."""
    tmp = tempfile.mktemp(suffix=".db")
    return Store(db_path=tmp)


# ---------------------------------------------------------------------------
# FrontierState predicate tests
# ---------------------------------------------------------------------------

class TestFrontierStatePredicates(unittest.TestCase):

    def test_legibility_pressure_not_detected_with_no_trajectory(self):
        state = _minimal_state()
        self.assertFalse(state.legibility_pressure_detected())

    def test_legibility_pressure_detected(self):
        state = _minimal_state()
        # Two snapshots: legibility rising, resolution flat
        state.trajectory = [
            TrajectorySnapshot(
                snapshot_id="s1",
                work_mode=WorkMode.IMPLEMENTING,
                shape=ProblemShape.FORMAL,
                resolution_delta=0.01,
                legibility_delta=0.2,
            ),
            TrajectorySnapshot(
                snapshot_id="s2",
                work_mode=WorkMode.IMPLEMENTING,
                shape=ProblemShape.FORMAL,
                resolution_delta=0.01,
                legibility_delta=0.3,
            ),
        ]
        self.assertTrue(state.legibility_pressure_detected())

    def test_legibility_pressure_not_detected_when_resolution_progresses(self):
        state = _minimal_state()
        state.trajectory = [
            TrajectorySnapshot(
                snapshot_id="s1",
                work_mode=WorkMode.IMPLEMENTING,
                shape=ProblemShape.FORMAL,
                resolution_delta=0.2,
                legibility_delta=0.2,
            ),
        ]
        self.assertFalse(state.legibility_pressure_detected())

    def test_should_enter_conservative_on_abandoned_paradigm(self):
        state = _minimal_state()
        p = ParadigmCommitment(
            paradigm_id="par1",
            description="abandoned paradigm",
            assumptions=[],
            yield_signals=[],
            rival_frame_ids=[],
            confidence=0.0,
            alive=False,
            death_reason=ParadigmDeathReason.ABANDONED_UNDER_PRESSURE,
        )
        state.paradigms["par1"] = p
        should, reason = state.should_enter_conservative()
        self.assertTrue(should)
        self.assertIn("abandoned under pressure", reason)

    def test_should_enter_conservative_on_two_blocking_findings(self):
        state = _minimal_state()
        for i in range(2):
            state.findings.append(MetacognitiveFinding(
                finding_id=f"find_{i}",
                severity=FindingSeverity.BLOCKING,
                blocks_commitment=True,
                description="blocker",
                provenance="test",
                evidence=[],
            ))
        should, reason = state.should_enter_conservative()
        self.assertTrue(should)
        self.assertIn("blocking findings", reason)

    def test_enter_conservative_sets_mode(self):
        state = _minimal_state()
        # Force two blocking findings
        for i in range(2):
            state.findings.append(MetacognitiveFinding(
                finding_id=f"find_{i}",
                severity=FindingSeverity.BLOCKING,
                blocks_commitment=True,
                description="blocker",
                provenance="test",
                evidence=[],
            ))
        state.enter_conservative()
        self.assertTrue(state.is_conservative)
        self.assertEqual(state.work_mode, WorkMode.CONSERVATIVE)


# ---------------------------------------------------------------------------
# Store tests
# ---------------------------------------------------------------------------

class TestStore(unittest.TestCase):

    def setUp(self):
        self.store = _tmp_store()

    def tearDown(self):
        self.store.close()

    def test_create_and_get_session(self):
        sid = self.store.create_session("test session")
        self.assertTrue(sid.startswith("sess_"))
        row = self.store.get_session(sid)
        self.assertIsNotNone(row)
        self.assertEqual(row["description"], "test session")

    def test_create_branch_emits_event(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "Is X true?")
        self.assertTrue(bid.startswith("br_"))
        events = self.store.get_events(branch_id=bid, event_type="branch_forked")
        self.assertEqual(len(events), 1)

    def test_save_and_load_state(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "intent")
        state = _minimal_state(branch_id=bid)
        self.store.save_state(sid, bid, state)
        loaded = self.store.load_latest_state(bid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["task_id"], "task_1")

    def test_add_and_get_memory(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "intent")
        rid = self.store.add_memory(bid, "episodic", {"key": "val"})
        self.assertTrue(rid.startswith("mem_"))
        records = self.store.get_memories(bid, "episodic")
        self.assertEqual(len(records), 1)

    def test_add_finding_and_get_blocking(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "intent")
        self.store.add_finding(
            branch_id=bid,
            critic_name="frame_critic",
            code="no_active_frame",
            severity="blocking",
            blocking=True,
            subject_ids=["task_1"],
            message="no frame",
        )
        blocking = self.store.get_blocking_findings(bid)
        self.assertEqual(len(blocking), 1)
        self.store.resolve_finding(blocking[0]["finding_id"])
        self.assertEqual(len(self.store.get_blocking_findings(bid)), 0)

    def test_add_proposal_commit_and_block(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "intent")
        pid = self.store.add_proposal(
            branch_id=bid,
            action_type="probe",
            payload_ref="ref::noop",
            rationale="testing",
            frame_id="f1",
            expected_evidence_gain=0.8,
            expected_irreversibility=0.1,
        )
        self.assertTrue(pid.startswith("prop_"))
        self.store.commit_proposal(pid, bid)
        events = self.store.get_events(branch_id=bid, event_type="commitment_made")
        self.assertEqual(len(events), 1)

    def test_add_gap_and_high_recurrence(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "intent")
        self.store.add_gap(
            branch_id=bid,
            gap_type="missed_cue",
            issue_level="policy",
            loop_stage="probing",
            mode="probing",
            missed_cue="anomaly signal ignored",
            observed_behavior="committed anyway",
            better_behavior="investigate first",
            recurrence_risk=0.8,
        )
        high = self.store.get_high_recurrence_gaps(threshold=0.7)
        self.assertEqual(len(high), 1)
        self.assertEqual(high[0]["recurrence_risk"], 0.8)

    def test_add_anomaly_resolve(self):
        sid = self.store.create_session()
        bid = self.store.create_branch(sid, "probe", "intent")
        aid = self.store.add_anomaly(bid, "unexpected output distribution")
        open_anoms = self.store.get_open_anomalies(bid)
        self.assertEqual(len(open_anoms), 1)
        self.store.resolve_anomaly(aid)
        self.assertEqual(len(self.store.get_open_anomalies(bid)), 0)


# ---------------------------------------------------------------------------
# Critic tests
# ---------------------------------------------------------------------------

class TestCritics(unittest.TestCase):

    def test_pressure_critic_no_findings_when_below_threshold(self):
        state = _minimal_state()
        state.pressure_readings = [
            PressureReading("legibility", active=True, intensity=0.7, tell="output too clean"),
            PressureReading("completion", active=True, intensity=0.7, tell="rushing to end"),
        ]
        # 2 hot < warning_count=3 → no findings
        findings = pressure_critic(state)
        self.assertEqual(findings, [])

    def test_pressure_critic_warning_at_three(self):
        state = _minimal_state()
        state.pressure_readings = [
            PressureReading("legibility", active=True, intensity=0.7, tell="clean output"),
            PressureReading("completion", active=True, intensity=0.7, tell="rushing"),
            PressureReading("frame_convergence", active=True, intensity=0.7, tell="tunnel vision"),
        ]
        findings = pressure_critic(state)
        self.assertEqual(len(findings), 1)
        self.assertFalse(findings[0].blocking)  # WARNING not BLOCKING at 3

    def test_pressure_critic_blocking_at_four(self):
        state = _minimal_state()
        state.pressure_readings = [
            PressureReading(name, active=True, intensity=0.7, tell="signal")
            for name in ["legibility", "completion", "frame_convergence", "competence"]
        ]
        findings = pressure_critic(state)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocking)

    def test_frame_critic_blocks_with_no_frames(self):
        state = FrontierState(task_id="t", branch_id="b")
        findings = frame_critic(state)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, CriticCode.NO_ACTIVE_FRAME)
        self.assertTrue(findings[0].blocking)

    def test_frame_critic_warns_single_frame_with_proposal(self):
        state = FrontierState(task_id="t", branch_id="b")
        state.frames["f1"] = Frame(
            frame_id="f1", description="only frame",
            assumptions=[], predictions=[], evidence_for=[], evidence_against=[],
            confidence=0.7,
        )
        proposal = _minimal_proposal()
        findings = frame_critic(state, proposal)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, CriticCode.RIVAL_FRAME_MISSING)
        self.assertFalse(findings[0].blocking)

    def test_frame_critic_passes_with_two_frames(self):
        state = _minimal_state()
        findings = frame_critic(state)
        self.assertEqual(findings, [])

    def test_evidence_critic_skips_low_irreversibility(self):
        state = _minimal_state()
        proposal = _minimal_proposal(irreversibility=0.2)
        findings = evidence_critic(state, proposal)
        self.assertEqual(findings, [])

    def test_evidence_critic_blocks_no_geometry(self):
        state = _minimal_state()
        state.geometry = None
        proposal = _minimal_proposal(irreversibility=0.6)
        findings = evidence_critic(state, proposal)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocking)

    def test_evidence_critic_blocks_low_confidence_load_bearing_axis(self):
        state = _minimal_state()
        state.geometry = TaskGeometry(
            shape=ProblemShape.FORMAL,
            shape_confidence=0.7,
            uncertainty_axes=[
                UncertaintyAxis(
                    name="causal_structure",
                    confidence=0.2,  # below threshold of 0.4
                    falsifier="run causal experiment",
                    load_bearing=True,
                )
            ],
        )
        proposal = _minimal_proposal(irreversibility=0.8)  # >= blocking threshold 0.6
        findings = evidence_critic(state, proposal)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, CriticCode.EVIDENCE_MISSING_FOR_LOAD_BEARING)
        self.assertTrue(findings[0].blocking)

    def test_anomaly_critic_skips_no_anomalies(self):
        state = _minimal_state()
        proposal = _minimal_proposal(anomalies=[])
        findings = anomaly_critic(state, proposal)
        self.assertEqual(findings, [])

    def test_anomaly_critic_blocks_high_irreversibility(self):
        state = _minimal_state()
        proposal = _minimal_proposal(irreversibility=0.9, anomalies=["anom_1"])
        findings = anomaly_critic(state, proposal)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocking)

    def test_completion_critic_blocks_unresolved_prior(self):
        from src.csp_runtime.frontier_models import CriticFinding
        state = _minimal_state()
        # Add a prior blocking finding (from a different critic)
        prior = CriticFinding(
            finding_id="find_prior",
            critic_name="frame_critic",
            code=CriticCode.NO_ACTIVE_FRAME,
            severity=FindingSeverity.BLOCKING,
            blocking=True,
            subject_ids=["t"],
            message="no frame",
            resolved=False,
        )
        state.findings.append(prior)
        proposal = _minimal_proposal()
        findings = completion_critic(state, proposal)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocking)

    def test_legibility_critic_fires_on_legibility_pressure(self):
        state = _minimal_state()
        state.trajectory = [
            TrajectorySnapshot("s1", work_mode=WorkMode.IMPLEMENTING,
                               shape=ProblemShape.FORMAL,
                               resolution_delta=0.01, legibility_delta=0.25),
            TrajectorySnapshot("s2", work_mode=WorkMode.IMPLEMENTING,
                               shape=ProblemShape.FORMAL,
                               resolution_delta=0.01, legibility_delta=0.20),
        ]
        findings = legibility_critic(state)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, CriticCode.LEGIBILITY_OVER_RESOLUTION)

    def test_irreversibility_critic_blocks_high_risk_proposal(self):
        state = _minimal_state()
        proposal = _minimal_proposal(irreversibility=0.85, evidence_gain=0.1)
        findings = irreversibility_critic(state, proposal)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocking)
        self.assertEqual(findings[0].code, CriticCode.IRREVERSIBLE_WITHOUT_EVIDENCE)

    def test_irreversibility_critic_passes_low_risk(self):
        state = _minimal_state()
        proposal = _minimal_proposal(irreversibility=0.3, evidence_gain=0.8)
        findings = irreversibility_critic(state, proposal)
        self.assertEqual(findings, [])

    def test_degeneration_critic_fires_on_loop(self):
        state = _minimal_state()
        # 4 snapshots, same mode, no resolution progress
        state.trajectory = [
            TrajectorySnapshot(f"s{i}", work_mode=WorkMode.IMPLEMENTING,
                               shape=ProblemShape.FORMAL,
                               resolution_delta=0.005, legibility_delta=None)
            for i in range(4)
        ]
        findings = degeneration_critic(state)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, CriticCode.REVISION_LOOP_DETECTED)

    def test_degeneration_critic_passes_with_progress(self):
        state = _minimal_state()
        state.trajectory = [
            TrajectorySnapshot(f"s{i}", work_mode=WorkMode.IMPLEMENTING,
                               shape=ProblemShape.FORMAL,
                               resolution_delta=0.1, legibility_delta=None)
            for i in range(4)
        ]
        findings = degeneration_critic(state)
        self.assertEqual(findings, [])

    def test_run_critics_catches_exception(self):
        """A crashing critic should not take down run_critics."""
        state = _minimal_state()

        def bad_critic(s, p, pol):
            raise RuntimeError("simulated critic crash")

        findings = run_critics(state, None, critics=[bad_critic])
        self.assertEqual(len(findings), 1)
        self.assertIn("simulated critic crash", findings[0].message)
        self.assertFalse(findings[0].blocking)


# ---------------------------------------------------------------------------
# Commitment gate tests
# ---------------------------------------------------------------------------

class TestCommitmentGate(unittest.TestCase):

    def test_allows_clean_probe(self):
        state = _minimal_state()
        proposal = _minimal_proposal(action_type=ActionType.PROBE)
        allowed, findings, reason = evaluate_commitment(state, proposal)
        self.assertTrue(allowed)
        self.assertIn("passed", reason)

    def test_blocks_implement_in_conservative_mode(self):
        state = _minimal_state()
        state.is_conservative = True
        state.conservative_reason = "test reason"
        state.work_mode = WorkMode.CONSERVATIVE
        proposal = _minimal_proposal(action_type=ActionType.IMPLEMENT)
        allowed, findings, reason = evaluate_commitment(state, proposal)
        self.assertFalse(allowed)
        self.assertIn("conservative mode", reason)

    def test_allows_probe_in_conservative_mode(self):
        state = _minimal_state()
        state.is_conservative = True
        state.conservative_reason = "test reason"
        state.work_mode = WorkMode.CONSERVATIVE
        proposal = _minimal_proposal(action_type=ActionType.PROBE)
        allowed, findings, reason = evaluate_commitment(state, proposal)
        self.assertTrue(allowed)

    def test_blocks_high_risk_proposal(self):
        state = _minimal_state()
        proposal = _minimal_proposal(
            action_type=ActionType.IMPLEMENT,
            irreversibility=0.9,
            evidence_gain=0.05,
        )
        allowed, findings, reason = evaluate_commitment(state, proposal)
        self.assertFalse(allowed)
        blockers = [f for f in findings if f.blocking]
        self.assertGreater(len(blockers), 0)

    def test_blocks_with_no_active_frame(self):
        state = FrontierState(task_id="t", branch_id="b")  # no frames
        proposal = _minimal_proposal(action_type=ActionType.IMPLEMENT)
        allowed, findings, reason = evaluate_commitment(state, proposal)
        self.assertFalse(allowed)
        self.assertIn("frame_critic", reason)


# ---------------------------------------------------------------------------
# Distillation tests
# ---------------------------------------------------------------------------

class TestDistillation(unittest.TestCase):

    def test_evaluate_distillation_fails_below_min_use(self):
        record = {"used_count": 1, "contradictory": 0}
        promote, reason = evaluate_distillation(record)
        self.assertFalse(promote)
        self.assertIn("not yet reused", reason)

    def test_evaluate_distillation_fails_contradictory(self):
        record = {"used_count": 5, "contradictory": 1}
        promote, reason = evaluate_distillation(record)
        self.assertFalse(promote)
        self.assertIn("contradictory", reason)

    def test_evaluate_distillation_passes(self):
        record = {"used_count": 5, "contradictory": 0}
        promote, reason = evaluate_distillation(record)
        self.assertTrue(promote)
        self.assertIn("passes distillation gate", reason)

    def test_distill_branch_promotes_qualifying_records(self):
        store = _tmp_store()
        sid = store.create_session()
        bid = store.create_branch(sid, "probe", "test")

        # Add an episodic record that qualifies (used 3+ times, non-contradictory)
        rid = store.add_memory(bid, "episodic", {"insight": "thing learned"})
        for _ in range(3):
            store.increment_memory_use(rid)

        promoted = distill_branch(store, bid)
        self.assertIn(rid, promoted)

        # Should now have a semantic record
        semantic = store.get_memories(bid, "semantic")
        self.assertEqual(len(semantic), 1)
        store.close()

    def test_distill_branch_skips_under_threshold(self):
        store = _tmp_store()
        sid = store.create_session()
        bid = store.create_branch(sid, "probe", "test")

        rid = store.add_memory(bid, "episodic", {"note": "not reused"})
        # used_count stays at 0

        promoted = distill_branch(store, bid)
        self.assertEqual(promoted, [])
        store.close()


# ---------------------------------------------------------------------------
# Router lifecycle tests
# ---------------------------------------------------------------------------

class TestRouterLifecycle(unittest.TestCase):

    def setUp(self):
        self.store = _tmp_store()
        self.router = Router(self.store)

    def tearDown(self):
        self.store.close()

    def test_start_session_emits_event(self):
        sid = self.router.start_session("integration test")
        self.assertTrue(sid.startswith("sess_"))
        events = self.store.get_events(event_type="session_started")
        self.assertEqual(len(events), 1)

    def test_fork_branch(self):
        sid = self.router.start_session()
        bid = self.router.fork_branch(sid, BranchType.PROBE.value, "Is X causal?")
        self.assertTrue(bid.startswith("br_"))

    def test_propose_allowed_persists_and_returns(self):
        sid = self.router.start_session()
        bid = self.router.fork_branch(sid, BranchType.PROBE.value, "probe intent")
        state = _minimal_state(branch_id=bid)
        proposal = _minimal_proposal(action_type=ActionType.PROBE)

        allowed, findings, reason = self.router.propose(sid, state, proposal)
        self.assertTrue(allowed)

        # State should be persisted
        loaded = self.store.load_latest_state(bid)
        self.assertIsNotNone(loaded)

    def test_propose_blocked_persists_findings(self):
        sid = self.router.start_session()
        bid = self.router.fork_branch(sid, BranchType.IMPLEMENTATION.value, "implement X")
        # State with NO frames — frame_critic will block
        state = FrontierState(task_id="t", branch_id=bid)
        proposal = _minimal_proposal(action_type=ActionType.IMPLEMENT)

        allowed, findings, reason = self.router.propose(sid, state, proposal)
        self.assertFalse(allowed)
        blocking_in_db = self.store.get_blocking_findings(bid)
        self.assertGreater(len(blocking_in_db), 0)

    def test_record_gap_persists(self):
        sid = self.router.start_session()
        bid = self.router.fork_branch(sid, BranchType.PROBE.value, "probe")
        state = _minimal_state(branch_id=bid)

        gid = self.router.record_gap(
            state=state,
            gap_type=GapType.MISSED_CUE,
            issue_level=GapIssueLevel.POLICY,
            loop_stage="probing",
            missed_cue="anomaly signal present",
            observed_behavior="committed without investigation",
            better_behavior="investigate anomaly first",
            recurrence_risk=0.75,
        )
        self.assertTrue(gid.startswith("gap_"))
        high = self.store.get_high_recurrence_gaps(threshold=0.7)
        self.assertEqual(len(high), 1)

    def test_distill_via_router(self):
        sid = self.router.start_session()
        bid = self.router.fork_branch(sid, BranchType.PROBE.value, "probe")

        # Add qualifying episodic record
        rid = self.store.add_memory(bid, "episodic", {"learned": "structure"})
        for _ in range(3):
            self.store.increment_memory_use(rid)

        promoted = self.router.distill(bid)
        self.assertIn(rid, promoted)

        # Router emits MEMORY_PROMOTED event
        events = self.store.get_events(branch_id=bid, event_type="memory_promoted")
        self.assertEqual(len(events), 1)


if __name__ == "__main__":
    unittest.main()
