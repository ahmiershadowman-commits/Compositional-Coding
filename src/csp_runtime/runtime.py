from __future__ import annotations

import json
from pathlib import Path

from .hooks import HookDispatcher
from .kernel import CSPKernel
from .models import ContextLaneType, RuntimeEvent, RuntimeEventType, RuntimeState, SkillCandidate, TaskInput
from .skills import GenericSkill, SkillRegistry
from .stores import ContextManager, DecisionStore, LogEvent, LogStore, ValidationLibrary


class Runtime:
    def __init__(self, skills_dir: str) -> None:
        self.kernel = CSPKernel()
        self.hooks = HookDispatcher()
        self.context = ContextManager()
        self.logs = LogStore()
        self.decisions = DecisionStore()
        self.validation = ValidationLibrary(
            recipes=[
                {
                    "recipe_id": "val_symbolic_solver_consistency",
                    "tags": ["correctness", "consistency"],
                    "steps": [
                        "check unsat/sat on seed cases",
                        "test contradictory constraint injection",
                        "compare model output against hand-checkable microcase",
                    ],
                }
            ]
        )
        self.skills = SkillRegistry()
        self._load_skills(skills_dir)

    def _load_skills(self, skills_dir: str) -> None:
        for path in Path(skills_dir).glob("*/metadata.json"):
            metadata = json.loads(path.read_text())
            self.skills.register(GenericSkill(metadata))

    def start_task(self, task_id: str, text: str) -> RuntimeState:
        root_branch = "branch_root"
        task_input = TaskInput(task_id=task_id, text=text)
        state = RuntimeState(task_input=task_input, task_id=task_id, branch_id=root_branch)
        geometry = self.kernel.classify_task(task_input, {})
        uncertainty = self.kernel.estimate_uncertainty(task_input, {})
        state.geometry = geometry
        state.uncertainty = uncertainty
        patterns = self.kernel.select_patterns(geometry, state)
        state.active_patterns = [p.pattern for p in patterns]
        self.context.update_lane(task_id, root_branch, ContextLaneType.METACOGNITIVE_STATE, {
            "problem_geometry": geometry.labels,
            "uncertainty": uncertainty.critical_unknowns,
            "validation_plan": ["baseline validation required"],
        })
        self.logs.append(LogEvent(
            event_type="task_received",
            task_id=task_id,
            branch_id=root_branch,
            active_csp_mode=state.active_patterns,
            confidence=uncertainty.confidence,
            details={"geometry": geometry.labels},
        ))
        return state

    def rank_skills(self, state: RuntimeState) -> list[SkillCandidate]:
        labels = set(state.geometry.labels if state.geometry else [])
        candidates = []
        for skill in self.skills.all():
            trigger_overlap = len(labels.intersection(skill.trigger_geometry))
            anti_overlap = len(labels.intersection(skill.anti_trigger_geometry))
            score = max(0.0, trigger_overlap * 0.4 - anti_overlap * 0.6 + 0.2)
            candidates.append(SkillCandidate(skill.id, skill.family, score, [f"trigger_overlap={trigger_overlap}"]))
        return self.kernel.compare_families(state.geometry, candidates).ranked

    def run_preflight(self, state: RuntimeState, skill_id: str) -> str:
        skill = self.skills.get(skill_id)
        result = skill.preflight(state)
        self.logs.append(LogEvent(
            event_type=f"skill_preflight_{result.status}",
            task_id=state.task_id,
            branch_id=state.branch_id,
            active_csp_mode=state.active_patterns,
            confidence=state.uncertainty.confidence if state.uncertainty else 0.0,
            skill_id=skill_id,
            details={"reasons": result.reasons, "missing_data": result.missing_data},
        ))
        return result.status

    def commit_decision(self, state: RuntimeState, selected_skill: str, candidates: list[SkillCandidate]) -> str:
        rid = self.decisions.create(
            {
                "task_id": state.task_id,
                "branch_id": state.branch_id,
                "problem_geometry": state.geometry.labels if state.geometry else [],
                "active_csp_patterns": state.active_patterns,
                "candidates_considered": [c.__dict__ for c in candidates],
                "selected": selected_skill,
                "commitment_gate": self.kernel.evaluate_commitment_gate(state).reason,
                "outcome": "pending",
            }
        )
        state.decision_ids.append(rid)
        return rid

    def validate(self, state: RuntimeState, status: str = "pass") -> dict:
        result = self.validation.run("val_symbolic_solver_consistency", {"status": status})
        self.context.update_lane(state.task_id, state.branch_id, ContextLaneType.ARTIFACT_STATE, {"validation": result})
        self.context.update_lane(state.task_id, state.branch_id, ContextLaneType.METACOGNITIVE_STATE, {"validation": {"status": result["status"]}})
        return result

    def emit(self, event_type: RuntimeEventType, state: RuntimeState, reason: str) -> None:
        event = RuntimeEvent(event_type=event_type, reason=reason)
        self.hooks.emit(event, state)
