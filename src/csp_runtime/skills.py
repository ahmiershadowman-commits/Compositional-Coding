from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from .models import ContextLaneType, RuntimeState


_TOKEN_SPLIT = re.compile(r"[^a-z0-9]+")
_STOPWORDS = {
    "and",
    "or",
    "the",
    "a",
    "an",
    "with",
    "without",
    "of",
    "to",
    "for",
    "is",
    "are",
    "where",
    "when",
    "low",
    "high",
    "real",
    "time",
}
_SYNONYM_MAP = {
    "constraint": "constraint-rich",
    "constraints": "constraint-rich",
    "combinatorial": "constraint-rich",
    "declarative": "constraint-rich",
    "sat": "constraint-rich",
    "smt": "constraint-rich",
    "formal": "formal",
    "invariant": "formal",
    "proof": "formal",
    "verification": "formal",
    "protocol": "systems",
    "latency": "systems",
    "throughput": "systems",
    "io": "systems",
    "performance": "systems",
    "network": "systems",
    "streaming": "systems",
    "novel": "novel",
    "frontier": "novel",
    "metacognitive": "metacognitive",
    "representation": "metacognitive",
    "reflective": "reflective",
    "macro": "reflective",
    "rewrite": "reflective",
}


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_SPLIT.split(text.lower()) if t and t not in _STOPWORDS]


def _normalize_signals(signals: list[str]) -> set[str]:
    normalized: set[str] = set()
    for signal in signals:
        lowered = signal.lower()
        normalized.add(lowered)
        for token in _tokenize(lowered):
            mapped = _SYNONYM_MAP.get(token)
            if mapped:
                normalized.add(mapped)
    return normalized


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
        self._trigger_signals = _normalize_signals(self.trigger_geometry + [self.family])
        self._anti_signals = _normalize_signals(self.anti_trigger_geometry)

    def score(self, geometry_labels: list[str]) -> tuple[float, int, int]:
        labels = _normalize_signals(geometry_labels)
        trigger_overlap = len(labels.intersection(self._trigger_signals))
        anti_overlap = len(labels.intersection(self._anti_signals))
        score = max(0.0, trigger_overlap * 0.45 - anti_overlap * 0.8 + 0.1)
        return score, trigger_overlap, anti_overlap

    def preflight(self, state: RuntimeState) -> SkillPreflightResult:
        labels = _normalize_signals(state.geometry.labels if state.geometry else [])
        anti = labels.intersection(self._anti_signals)
        if anti:
            return SkillPreflightResult("reject", [f"anti-trigger matched: {sorted(anti)}"])
        good = labels.intersection(self._trigger_signals)
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
