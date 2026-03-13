from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .models import ContextLaneType, RuntimeState


@dataclass
class SkillPreflightResult:
    status: str
    reasons: list[str] = field(default_factory=list)
    missing_data: list[str] = field(default_factory=list)


@dataclass
class SkillPlan:
    steps: list[str]


@dataclass
class SkillExecutionResult:
    status: str
    artifacts: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    status: str
    findings: list[str] = field(default_factory=list)


class Skill(Protocol):
    id: str
    family: str
    trigger_geometry: list[str]
    anti_trigger_geometry: list[str]

    def preflight(self, state: RuntimeState) -> SkillPreflightResult: ...
    def required_context_lanes(self) -> list[ContextLaneType]: ...
    def required_references(self) -> list[dict[str, Any]]: ...
    def plan(self, state: RuntimeState) -> SkillPlan: ...
    def execute(self, state: RuntimeState) -> SkillExecutionResult: ...
    def validate(self, result: SkillExecutionResult, state: RuntimeState) -> ValidationResult: ...
    def handoff(self, result: SkillExecutionResult, state: RuntimeState) -> dict[str, Any]: ...


class GenericSkill:
    def __init__(self, metadata: dict[str, Any]) -> None:
        self.id = metadata["id"]
        self.family = metadata["family"]
        self.trigger_geometry = metadata["trigger_geometry"]
        self.anti_trigger_geometry = metadata["anti_trigger_geometry"]
        self._required_context_lanes = [ContextLaneType(l) for l in metadata["required_context_lanes"]]

    def preflight(self, state: RuntimeState) -> SkillPreflightResult:
        labels = set(state.geometry.labels if state.geometry else [])
        anti = labels.intersection(self.anti_trigger_geometry)
        if anti:
            return SkillPreflightResult("reject", [f"anti-trigger matched: {sorted(anti)}"])
        good = labels.intersection(self.trigger_geometry)
        if not good:
            return SkillPreflightResult("defer", ["no strong trigger geometry overlap"])
        return SkillPreflightResult("accept", [f"trigger geometry overlap: {sorted(good)}"])

    def required_context_lanes(self) -> list[ContextLaneType]:
        return self._required_context_lanes

    def required_references(self) -> list[dict[str, Any]]:
        return [{"kind": "pattern", "skill": self.id}]

    def plan(self, state: RuntimeState) -> SkillPlan:
        return SkillPlan(["run preflight", "design minimal probe", "implement", "validate", "handoff"])

    def execute(self, state: RuntimeState) -> SkillExecutionResult:
        return SkillExecutionResult("ok", details={"skill": self.id})

    def validate(self, result: SkillExecutionResult, state: RuntimeState) -> ValidationResult:
        return ValidationResult("pass", ["generic validation pass"]) 

    def handoff(self, result: SkillExecutionResult, state: RuntimeState) -> dict[str, Any]:
        return {"skill": self.id, "status": result.status}


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, GenericSkill] = {}

    def register(self, skill: GenericSkill) -> None:
        self._skills[skill.id] = skill

    def all(self) -> list[GenericSkill]:
        return list(self._skills.values())

    def get(self, skill_id: str) -> GenericSkill:
        return self._skills[skill_id]
