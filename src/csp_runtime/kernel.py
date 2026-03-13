from __future__ import annotations

from dataclasses import dataclass

from .models import (
    CommitmentDecision,
    LeakReport,
    ProblemGeometry,
    ReassessmentResult,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeState,
    SkillCandidate,
    TaskInput,
    UncertaintyRegister,
)


@dataclass
class FamilyComparison:
    ranked: list[SkillCandidate]


@dataclass
class CSPPatternActivation:
    pattern: str
    reason: str


@dataclass
class NextAction:
    event: RuntimeEventType
    reason: str


class CSPKernel:
    """Minimal CSP controller that canonicalizes process shape, not conclusions."""

    def classify_task(self, input: TaskInput, context: dict) -> ProblemGeometry:
        text = input.text.lower()
        labels = ["mixed"]
        if any(k in text for k in ["constraint", "satisfy", "schedule", "sat", "smt"]):
            labels.append("constraint-rich")
        if any(k in text for k in ["latency", "throughput", "protocol", "io", "cache"]):
            labels.append("systems")
        if any(k in text for k in ["proof", "invariant", "formal", "model check"]):
            labels.append("formal")
        if any(k in text for k in ["novel", "frontier", "unknown"]):
            labels.append("novel")
        return ProblemGeometry(labels=sorted(set(labels)), confidence=0.65)

    def select_patterns(self, geometry: ProblemGeometry, state: RuntimeState) -> list[CSPPatternActivation]:
        patterns = [CSPPatternActivation("uncertainty-mapping", "always-on CSP baseline")]
        if "constraint-rich" in geometry.labels:
            patterns.append(CSPPatternActivation("constraint-lens", "constraints dominate geometry"))
        if "novel" in geometry.labels:
            patterns.append(CSPPatternActivation("response-pathway-analysis", "novelty requires family comparison"))
        return patterns

    def estimate_uncertainty(self, input: TaskInput, context: dict) -> UncertaintyRegister:
        unknowns = []
        if len(input.text) < 40:
            unknowns.append("task specification may be underspecified")
        if "novel" in input.text.lower():
            unknowns.append("representation fit uncertain")
        confidence = max(0.2, 1.0 - 0.2 * len(unknowns))
        return UncertaintyRegister(critical_unknowns=unknowns, confidence=confidence)

    def compare_families(self, geometry: ProblemGeometry, candidates: list[SkillCandidate]) -> FamilyComparison:
        ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
        return FamilyComparison(ranked=ranked)

    def evaluate_commitment_gate(self, state: RuntimeState) -> CommitmentDecision:
        has_compare = any(p in state.active_patterns for p in ["response-pathway-analysis", "constraint-lens"])
        has_validation_path = "validation_plan" in state.context_lanes.get("metacognitive_state", {})
        if has_compare and has_validation_path and (state.uncertainty and state.uncertainty.confidence >= 0.5):
            return CommitmentDecision(True, "comparison done, validation path present, uncertainty manageable")
        return CommitmentDecision(False, "need probe/formalization before implementation")

    def detect_abstraction_leak(self, state: RuntimeState, artifacts: dict) -> list[LeakReport]:
        leaks: list[LeakReport] = []
        if artifacts.get("direct_impl_without_probe"):
            leaks.append(LeakReport("implementation happened without probe evidence", "high"))
        return leaks

    def decide_next_action(self, state: RuntimeState) -> NextAction:
        decision = self.evaluate_commitment_gate(state)
        if decision.allowed:
            return NextAction(RuntimeEventType.IMPLEMENTATION_READY, decision.reason)
        return NextAction(RuntimeEventType.PROBE_REQUIRED, decision.reason)

    def reassess(self, after: RuntimeEvent, state: RuntimeState) -> ReassessmentResult:
        if after.event_type == RuntimeEventType.VALIDATION_REQUIRED and state.context_lanes.get("validation", {}).get("status") == "fail":
            return ReassessmentResult(True, "validation failed")
        return ReassessmentResult(False, "no reassessment trigger")
