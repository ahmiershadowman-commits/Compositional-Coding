"""
Runtime router — thin deterministic coordinator.

Python handles: transitions, persistence, event emission, critic dispatch,
commitment gating, gap recording, distillation triggering.

Python does NOT handle: reasoning, routing decisions, problem classification,
skill selection, frame choice, paradigm commitment. Those live in the
cognitive layer (Claude Code reading FrontierState).

If this module grows reasoning logic, the thin-coordinator constraint has
been violated. The failure mode is coordinator creep — it starts thin
and grows toward orchestration. The constraint: Python mediates; it never thinks.
"""

from __future__ import annotations

from .commitment import evaluate_commitment
from .critics import Critic
from .distillation import distill_branch
from .events import EventType
from .frontier_models import (
    ActionProposal,
    CriticFinding,
    FrontierState,
    WorkMode,
)
from .gap_capture import capture_gap, GapType, GapIssueLevel
from .policies import RuntimePolicy, DEFAULT_POLICY
from .retrieval import hydrate_context
from .store import Store


class Router:
    """
    Thin deterministic coordinator.

    One Router per session. Wires Store, critics, commitment gate,
    gap capture, and distillation together. Does not reason.
    """

    def __init__(self, store: Store, policy: RuntimePolicy | None = None) -> None:
        self.store = store
        self.policy = policy or DEFAULT_POLICY

    # ------------------------------------------------------------------
    # Session and branch lifecycle
    # ------------------------------------------------------------------

    def start_session(self, description: str = "") -> str:
        sid = self.store.create_session(description)
        self.store.emit(EventType.SESSION_STARTED, {"description": description})
        return sid

    def fork_branch(
        self,
        session_id: str,
        branch_type: str,
        branch_intent: str,
        parent_branch_id: str | None = None,
    ) -> str:
        return self.store.create_branch(session_id, branch_type, branch_intent, parent_branch_id)

    # ------------------------------------------------------------------
    # Proposal evaluation — the main gate
    # ------------------------------------------------------------------

    def propose(
        self,
        session_id: str,
        state: FrontierState,
        proposal: ActionProposal,
        critics: list[Critic] | None = None,
    ) -> tuple[bool, list[CriticFinding], str]:
        """
        Run the commitment gate on a proposal.

        Side effects:
          - Checks and applies conservative mode to state
          - Persists all critic findings to store
          - Adds findings to in-memory state.findings
          - Emits commitment_made or proposal_blocked event
          - Saves state snapshot

        Returns (allowed, all_findings, reason).
        """
        # Persist the proposal before evaluation so commit/block UPDATEs have a row to hit
        self.store.add_proposal(
            branch_id=state.branch_id,
            action_type=proposal.action_type.value,
            payload_ref=proposal.payload_ref,
            rationale=proposal.rationale,
            frame_id=proposal.frame_id,
            expected_evidence_gain=proposal.expected_evidence_gain,
            expected_irreversibility=proposal.expected_irreversibility,
            touched_constraints=proposal.touched_constraints,
            touched_anomalies=proposal.touched_anomalies,
            fallback_path=proposal.fallback_path,
            proposal_id=proposal.proposal_id,
        )

        # Check and apply conservative mode before evaluating
        state.enter_conservative()
        if state.is_conservative:
            self.store.emit(
                EventType.CONSERVATIVE_MODE_ENTERED,
                {"reason": state.conservative_reason},
                branch_id=state.branch_id,
            )

        allowed, findings, reason = evaluate_commitment(
            state, proposal, critics, self.policy.critics
        )

        # Persist all findings and attach to in-memory state
        for f in findings:
            self.store.add_finding(
                branch_id=state.branch_id,
                critic_name=f.critic_name,
                code=f.code.value,
                severity=f.severity.value,
                blocking=f.blocking,
                subject_ids=f.subject_ids,
                message=f.message,
                suggested_next_move=f.suggested_next_move,
                evidence_refs=f.evidence_refs,
            )
            state.findings.append(f)

        if allowed:
            self.store.commit_proposal(proposal.proposal_id, state.branch_id)
        else:
            self.store.block_proposal(proposal.proposal_id, state.branch_id, reason)

        self.store.save_state(session_id, state.branch_id, state)
        return allowed, findings, reason

    # ------------------------------------------------------------------
    # Context hydration
    # ------------------------------------------------------------------

    def hydrate(self, branch_id: str) -> dict:
        """Load working context for a branch. Respects hydration policy."""
        return hydrate_context(self.store, branch_id, self.policy.hydration)

    # ------------------------------------------------------------------
    # Gap recording
    # ------------------------------------------------------------------

    def record_gap(
        self,
        state: FrontierState,
        gap_type: GapType,
        issue_level: GapIssueLevel,
        loop_stage: str,
        missed_cue: str,
        observed_behavior: str,
        better_behavior: str,
        recurrence_risk: float,
        proposed_support: str | None = None,
    ) -> str:
        """Create and persist a MetacognitiveGapRecord."""
        gap = capture_gap(
            state=state,
            gap_type=gap_type,
            issue_level=issue_level,
            loop_stage=loop_stage,
            missed_cue=missed_cue,
            observed_behavior=observed_behavior,
            better_behavior=better_behavior,
            recurrence_risk=recurrence_risk,
            proposed_support=proposed_support,
        )
        return self.store.add_gap(
            branch_id=state.branch_id,
            gap_type=gap.gap_type.value,
            issue_level=gap.issue_level.value,
            loop_stage=gap.loop_stage,
            mode=gap.mode.value,
            missed_cue=gap.missed_cue,
            observed_behavior=gap.observed_behavior,
            better_behavior=gap.better_behavior,
            recurrence_risk=gap.recurrence_risk,
            frame_id=gap.frame_id,
            pressure_snapshot=gap.pressure_snapshot,
            proposed_support=gap.proposed_support,
        )

    # ------------------------------------------------------------------
    # Distillation
    # ------------------------------------------------------------------

    def distill(self, branch_id: str) -> list[str]:
        """Evaluate episodic records and promote qualifying ones to semantic."""
        promoted = distill_branch(self.store, branch_id, self.policy.distillation)
        if promoted:
            self.store.emit(
                EventType.MEMORY_PROMOTED,
                {"promoted_count": len(promoted), "record_ids": promoted},
                branch_id=branch_id,
            )
        return promoted
