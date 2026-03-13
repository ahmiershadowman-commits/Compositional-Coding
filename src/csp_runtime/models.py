from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class RuntimeEventType(str, Enum):
    TASK_RECEIVED = "task_received"
    PROBLEM_CLASSIFIED = "problem_classified"
    SKILL_SEARCH_REQUIRED = "skill_search_required"
    SKILL_PREFLIGHT = "skill_preflight"
    PROBE_REQUIRED = "probe_required"
    IMPLEMENTATION_READY = "implementation_ready"
    VALIDATION_REQUIRED = "validation_required"
    REASSESSMENT_REQUIRED = "reassessment_required"
    HANDOFF_PERSIST = "handoff_persist"


class FailureType(str, Enum):
    REPRESENTATION_MISMATCH = "representation_mismatch"
    UPDATE_LAW_ERROR = "update_law_error"
    CONSTRAINT_FAILURE = "constraint_failure"
    SCALING_FAILURE = "scaling_failure"
    NUMERICAL_INSTABILITY = "numerical_instability"
    TOOLING_GAP = "tooling_gap"
    VALIDATION_GAP = "validation_gap"
    EXECUTION_BUG = "execution_bug"
    PROTOCOL_MISMATCH = "protocol_mismatch"
    ABSTRACTION_LEAK = "abstraction_leak"


class ContextLaneType(str, Enum):
    ACTIVE_TASK = "active_task"
    METACOGNITIVE_STATE = "metacognitive_state"
    PROJECT_MEMORY = "project_memory"
    PATTERN_REFERENCES = "pattern_references"
    ARTIFACT_STATE = "artifact_state"
    ARCHIVE_COLD = "archive_cold"


@dataclass
class RuntimeEvent:
    event_type: RuntimeEventType
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TaskInput:
    task_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillCandidate:
    skill_id: str
    family: str
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class ProblemGeometry:
    labels: list[str]
    confidence: float


@dataclass
class UncertaintyRegister:
    critical_unknowns: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class CommitmentDecision:
    allowed: bool
    reason: str


@dataclass
class LeakReport:
    description: str
    severity: str


@dataclass
class ReassessmentResult:
    should_reassess: bool
    reason: str


@dataclass
class RuntimeState:
    task_input: TaskInput
    task_id: str
    branch_id: str
    geometry: ProblemGeometry | None = None
    uncertainty: UncertaintyRegister | None = None
    active_patterns: list[str] = field(default_factory=list)
    context_lanes: dict[str, Any] = field(default_factory=dict)
    decision_ids: list[str] = field(default_factory=list)


@dataclass
class HookResult:
    hook_id: str
    event_type: RuntimeEventType
    executed: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeHook:
    id: str
    event: RuntimeEventType
    predicate: Callable[[RuntimeState], bool]
    run: Callable[[RuntimeState], HookResult]
    priority: int = 100
