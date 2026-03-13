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
        words = set(text.replace("/", " ").replace("-", " ").split())
        labels = ["mixed"]
        if any(k in text for k in ["constraint", "satisfy", "schedule", "sat", "smt"]):
            labels.append("constraint-rich")
        if any(k in words for k in ["latency", "throughput", "protocol", "cache"]) or "i/o" in text or " io " in f" {text} ":
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
        if "systems" in geometry.labels:
            patterns.append(CSPPatternActivation("trace-driven-diagnosis", "systems signals require trace-minded reasoning"))
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
        meta_lane = state.context_lanes.get("metacognitive_state", {})
        has_compare = any(p in state.active_patterns for p in ["response-pathway-analysis", "constraint-lens", "trace-driven-diagnosis"])
        has_validation_path = "validation_plan" in meta_lane
        has_critical_unknowns = bool((state.uncertainty.critical_unknowns if state.uncertainty else []))
        if has_compare and has_validation_path and not has_critical_unknowns:
            return CommitmentDecision(True, "comparison done, validation path present, uncertainty reduced")
        return CommitmentDecision(False, "need probe/formalization before implementation")

    def detect_abstraction_leak(self, state: RuntimeState, artifacts: dict) -> list[LeakReport]:
        leaks: list[LeakReport] = []
        if artifacts.get("direct_impl_without_probe"):
            leaks.append(LeakReport("implementation happened without probe evidence", "high"))
        if artifacts.get("validation") and artifacts["validation"].get("status") == "fail":
            leaks.append(LeakReport("implementation/representation mismatch surfaced in validation", "medium"))
        return leaks

    def decide_next_action(self, state: RuntimeState) -> NextAction:
        decision = self.evaluate_commitment_gate(state)
        if decision.allowed:
            return NextAction(RuntimeEventType.IMPLEMENTATION_READY, decision.reason)
        return NextAction(RuntimeEventType.PROBE_REQUIRED, decision.reason)

    def reassess(self, after: RuntimeEvent, state: RuntimeState) -> ReassessmentResult:
        validation_state = state.context_lanes.get("metacognitive_state", {}).get("validation", {})
        if after.event_type == RuntimeEventType.VALIDATION_REQUIRED and validation_state.get("status") == "fail":
            return ReassessmentResult(True, "validation failed")
        if after.event_type == RuntimeEventType.REASSESSMENT_REQUIRED:
            return ReassessmentResult(True, "explicit reassessment requested")
        return ReassessmentResult(False, "no reassessment trigger")
