"""
Runtime configuration — thresholds, distillation policy, hydration policy.

These are the tunable parameters that shape critic behavior and memory management.
Changing a policy threshold is a policy-level fix; changing a critic's logic is
an architectural fix. Keep the distinction clear.

The DEFAULT_POLICY is used when no policy is explicitly configured.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CriticPolicy:
    """Thresholds governing mandatory critic behavior."""
    # Pressure critic
    pressure_stack_warning_count: int = 3       # simultaneous high-intensity pressures → WARNING
    pressure_stack_blocking_count: int = 4      # simultaneous high-intensity pressures → BLOCKING
    pressure_intensity_threshold: float = 0.6   # intensity above this = "high"

    # Evidence critic
    irreversibility_evidence_threshold: float = 0.4   # below this = check evidence
    irreversibility_blocking_threshold: float = 0.6   # above this + low evidence = BLOCKING
    evidence_confidence_low: float = 0.4              # axis confidence below this = unverified

    # Irreversibility critic
    high_irreversibility: float = 0.7          # proposal.expected_irreversibility above this
    low_evidence_gain: float = 0.3             # proposal.expected_evidence_gain below this

    # Degeneration critic
    degeneration_window: int = 4               # consecutive snapshots to check
    degeneration_resolution_min: float = 0.02  # resolution_delta below this = stagnant


@dataclass
class DistillationPolicy:
    """
    Controls when episodic memory records are promoted to semantic.

    Distillation is not automatic on repetition. Records must pass all
    active gates before promotion. Gate failures are reasons, not errors.
    """
    min_use_count: int = 3                # must be used this many times to be a candidate
    require_non_contradictory: bool = True
    require_frame_clean: bool = True      # frame must have resolved cleanly, not under pressure
    # Load-bearing items are NEVER stubbed during commit (hydration policy enforces this)


@dataclass
class HydrationPolicy:
    """
    Controls what loads into working context at session start / branch restore.

    The load-bearing constraint: items marked load_bearing on their UncertaintyAxis
    are ALWAYS hydrated in full. They may never be stubbed.
    """
    always_load_semantic: bool = True
    always_load_procedural: bool = True
    max_episodic_records: int = 20          # cap to prevent context bloat
    never_stub_load_bearing: bool = True    # enforced invariant — do not change


@dataclass
class RuntimePolicy:
    critics: CriticPolicy = field(default_factory=CriticPolicy)
    distillation: DistillationPolicy = field(default_factory=DistillationPolicy)
    hydration: HydrationPolicy = field(default_factory=HydrationPolicy)


# The default policy — used unless overridden.
DEFAULT_POLICY = RuntimePolicy()
