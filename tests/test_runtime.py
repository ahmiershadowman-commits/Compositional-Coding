import unittest

from src.csp_runtime.models import ContextLaneType, RuntimeEvent, RuntimeEventType
from src.csp_runtime.runtime import Runtime
from src.csp_runtime.simulation import run_frontier_audit


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = Runtime("src/skills")

    def test_task_start_populates_geometry_and_lanes(self):
        state = self.runtime.start_task("task_1", "Novel constraint scheduling problem with invariants")
        self.assertIn("constraint-rich", state.geometry.labels)
        lane = self.runtime.context.get_lane("task_1", "branch_root", ContextLaneType.METACOGNITIVE_STATE)
        self.assertIn("problem_geometry", lane)
        self.assertIn("metacognitive_state", state.context_lanes)

    def test_skill_ranking_and_preflight_accepts_structural_fit(self):
        state = self.runtime.start_task("task_2", "constraint scheduling with soft preferences")
        ranked = self.runtime.rank_skills(state)
        self.assertGreater(len(ranked), 0)
        top = ranked[0].skill_id
        status = self.runtime.run_preflight(state, top)
        self.assertEqual(status, "accept")

    def test_commitment_gate_uses_synced_lanes(self):
        state = self.runtime.start_task("task_3", "constraint scheduling with deterministic requirements")
        state.uncertainty.critical_unknowns = []
        decision = self.runtime.kernel.evaluate_commitment_gate(state)
        self.assertTrue(decision.allowed)

    def test_reassessment_on_validation_fail(self):
        state = self.runtime.start_task("task_4", "novel formal invariant-heavy workflow")
        self.runtime.validate(state, status="fail")
        result = self.runtime.kernel.reassess(RuntimeEvent(RuntimeEventType.VALIDATION_REQUIRED, "test"), state)
        self.assertTrue(result.should_reassess)

    def test_frontier_audit_surfaces_known_failure_modes(self):
        results = run_frontier_audit()
        self.assertEqual(len(results), 4)
        underspecified = [r for r in results if r.scenario == "underspecified_frontier"][0]
        self.assertIn("skill_selection_failure", underspecified.failure_modes)


if __name__ == "__main__":
    unittest.main()
