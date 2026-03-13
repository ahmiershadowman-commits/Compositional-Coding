import unittest

from src.csp_runtime.models import ContextLaneType
from src.csp_runtime.runtime import Runtime


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = Runtime("src/skills")

    def test_task_start_populates_geometry_and_lanes(self):
        state = self.runtime.start_task("task_1", "Novel constraint scheduling problem with invariants")
        self.assertIn("constraint-rich", state.geometry.labels)
        lane = self.runtime.context.get_lane("task_1", "branch_root", ContextLaneType.METACOGNITIVE_STATE)
        self.assertIn("problem_geometry", lane)

    def test_skill_ranking_and_preflight(self):
        state = self.runtime.start_task("task_2", "constraint scheduling with soft preferences")
        ranked = self.runtime.rank_skills(state)
        self.assertGreater(len(ranked), 0)
        status = self.runtime.run_preflight(state, ranked[0].skill_id)
        self.assertIn(status, {"accept", "defer", "reject"})

    def test_decision_and_validation(self):
        state = self.runtime.start_task("task_3", "novel formal invariant-heavy workflow")
        ranked = self.runtime.rank_skills(state)
        did = self.runtime.commit_decision(state, ranked[0].skill_id, ranked)
        self.assertTrue(did.startswith("dec_"))
        validation = self.runtime.validate(state, status="pass")
        self.assertEqual(validation["status"], "pass")


if __name__ == "__main__":
    unittest.main()
