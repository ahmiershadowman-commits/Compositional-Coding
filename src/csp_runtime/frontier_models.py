"""
Phase A+B schema — Frontier cognition data model.

Designed to cohere with the .claude/commands/paradigm-hold.md protocol.
Replaces ProblemGeometry eventually (Phase C migration); coexists until then.

Key design decisions:
- Scalar confidence is gone from geometry; confidence lives per uncertainty axis.
- Paradigm commitments are not hypotheses — they are lenses. Different lifecycle.
- Frame death reasons are structured; "abandoned under pressure" is a distinct,
  dangerous state that must be distinguishable from "contradicted by evidence."
- FrontierState.should_enter_conservative() is a predicate, not a subsystem.
  It reads internal state directly. No new infrastructure needed.
- SQLite (stdlib sqlite3) will be used in Phase E persistence — zero new deps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Work modes
# ---------------------------------------------------------------------------

class WorkMode(str, Enum):
    ORIENTING = "orienting"         # LOCATE + SENSE — before any commitment
    PROBING = "probing"             # active discrimination, minimal experiments
    IMPLEMENTING = "implementing"   # committed to a path
    VALIDATING = "validating"       # checking implementation against expectations
    REASSESSING = "reassessing"     # something failed or surprised
    CONSERVATIVE = "conservative"   # degraded cognitive state — all outputs advisory


# ---------------------------------------------------------------------------
# Rich problem geometry (replaces ProblemGeometry in Phase C)
# ---------------------------------------------------------------------------

class ProblemShape(str, Enum):
    CONSTRAINT_RICH = "constraint_rich"
    SYSTEMS = "systems"
    FORMAL = "formal"
    NOVEL = "novel"
    MIXED = "mixed"
    UNKNOWN = "unknown"     # genuinely off-distribution — not "novel", truly unknown


@dataclass
class UncertaintyAxis:
    """
    A named dimension of uncertainty — not a scalar, but a direction.

    The old scalar confidence (ProblemGeometry.confidence = 0.65) is gone.
    Confidence is meaningless as a global number. It lives here, per axis,
    with an explicit falsifier so it can actually be tested.
    """
    name: str               # e.g. "representation fit", "causal structure"
    confidence: float       # 0.0–1.0, rough, labeled as such
    falsifier: str          # what would tell us we're wrong on this axis
    load_bearing: bool = True   # if True, must reduce before commit is allowed


@dataclass
class DomainAnalogue:
    """
    A structural bridge to another field.

    The point of BRIDGE (from /primitives) is not to find similarity —
    it's to find which structural property transfers and exactly where it breaks.
    Both fields must be filled. An analogue without a breaks_at is a claim
    of full equivalence, which is almost never true and always dangerous.
    """
    field: str                  # "information geometry", "sheaf theory", "gauge theory"
    preserved_structure: str    # what structural property transfers
    breaks_at: str              # where the analogy fails — ALWAYS fill this


@dataclass
class TaskGeometry:
    """
    Rich problem geometry.

    Replaces: ProblemGeometry(labels: list[str], confidence: float)
    The flat label list and global confidence scalar are gone.

    uncertainty_axes carries the confidence information, per-axis, with falsifiers.
    analogues carries cross-domain bridges found via /bridge-protocol.
    frontier_signal names what makes this off-distribution, if anything.
    """
    shape: ProblemShape
    shape_confidence: float
    uncertainty_axes: list[UncertaintyAxis] = field(default_factory=list)
    analogues: list[DomainAnalogue] = field(default_factory=list)
    is_frontier: bool = False
    frontier_signal: str | None = None     # what signals genuinely off-distribution


# ---------------------------------------------------------------------------
# Paradigm commitments
# (distinct from Frame — a paradigm is a lens, not a hypothesis)
# ---------------------------------------------------------------------------

class ParadigmDeathReason(str, Enum):
    CONTRADICTED_BY_EVIDENCE = "contradicted_by_evidence"
    COULDNT_FORMULATE_QUESTION = "couldnt_formulate_question"   # the strongest signal
    COLLAPSED_INTO_OTHER = "collapsed_into_other"
    OUTRUN_BY_EVIDENCE = "outrun_by_evidence"
    ABANDONED_UNDER_PRESSURE = "abandoned_under_pressure"       # dangerous — triggers conservative


@dataclass
class ParadigmCommitment:
    """
    A theoretical frame in use.

    Not a hypothesis — a lens. Hypotheses predict facts; paradigms shape
    which questions can even be asked. They're yielded differently:
    not falsified, but outrun, found insufficient, or unable to formulate
    the question the problem is actually asking.

    Coheers with .claude/commands/paradigm-hold.md protocol.
    """
    paradigm_id: str
    description: str
    assumptions: list[str]          # load-bearing assumptions — be specific
    yield_signals: list[str]        # what would cause this frame to yield
    rival_frame_ids: list[str]      # live rivals — empty set is a warning sign
    confidence: float               # provisional estimate, not a claim
    alive: bool = True
    death_reason: ParadigmDeathReason | None = None
    collapsed_into: str | None = None   # paradigm_id if collapsed
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def has_live_rival(self) -> bool:
        return len(self.rival_frame_ids) > 0


# ---------------------------------------------------------------------------
# Frame register (competing interpretations / hypotheses)
# Distinct from paradigms: frames predict facts, paradigms shape questions.
# ---------------------------------------------------------------------------

class FrameDeathReason(str, Enum):
    CONTRADICTED_BY_EVIDENCE = "contradicted_by_evidence"
    TOO_VAGUE_TO_DISCRIMINATE = "too_vague_to_discriminate"
    COLLAPSED_INTO_OTHER = "collapsed_into_other"
    SUPERSEDED = "superseded"
    ABANDONED_UNDER_PRESSURE = "abandoned_under_pressure"   # dangerous — always name this


@dataclass
class Frame:
    """
    A competing interpretation or hypothesis about the problem.

    predictions: what this frame would predict *differently* from rivals.
    A frame with no discriminating predictions is not doing cognitive work.
    """
    frame_id: str
    description: str
    assumptions: list[str]
    predictions: list[str]      # discriminating predictions — differs from rivals
    evidence_for: list[str]
    evidence_against: list[str]
    confidence: float
    alive: bool = True
    death_reason: FrameDeathReason | None = None
    collapsed_into: str | None = None   # frame_id if merged


# ---------------------------------------------------------------------------
# Branch typing (audit addendum item 4: branch_intent alongside branch_type)
# ---------------------------------------------------------------------------

class BranchType(str, Enum):
    PROBE = "probe"                 # testing a discriminating question
    FRAME = "frame"                 # exploring a specific interpretation
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    SPECULATIVE = "speculative"     # off-distribution exploration, low commitment


@dataclass
class TypedBranch:
    """
    A branch with explicit type and intent.

    branch_intent is the load-bearing field: what question is this branch
    probing? Without it, branch proliferation produces a graveyard.
    """
    branch_id: str
    branch_type: BranchType
    branch_intent: str              # the specific question this branch is probing
    parent_branch_id: str | None = None
    frame_id: str | None = None     # linked frame, if a FRAME branch
    paradigm_id: str | None = None  # linked paradigm, if relevant
    open: bool = True
    resolution: str | None = None   # how it resolved when closed


# ---------------------------------------------------------------------------
# Metacognitive critic findings (structured — replaces string outputs)
# ---------------------------------------------------------------------------

class FindingSeverity(str, Enum):
    ADVISORY = "advisory"
    WARNING = "warning"
    BLOCKING = "blocking"


@dataclass
class MetacognitiveFinding:
    """
    Structured critic output.

    Replaces string-based critic notes. blocks_commitment is explicit.
    provenance is required — findings that can't be traced to a source
    can't be evaluated or resolved.
    """
    finding_id: str
    severity: FindingSeverity
    blocks_commitment: bool
    description: str
    provenance: str                 # which critic or check produced this
    evidence: list[str]
    suggested_action: str | None = None


# ---------------------------------------------------------------------------
# Pressure tracking
# ---------------------------------------------------------------------------

@dataclass
class PressureReading:
    """Instantaneous pressure detection. Named pressures from /pressure taxonomy."""
    pressure_name: str      # e.g. "legibility", "completion", "frame_convergence"
    active: bool
    intensity: float        # 0.0–1.0, rough, acknowledged as such
    tell: str               # what observable triggered this reading


@dataclass
class TrajectorySnapshot:
    """
    Point-in-time cognitive state snapshot.

    The key signal: legibility_delta increasing while resolution_delta is flat
    or declining = legibility pressure active. This is the primary detection
    mechanism for output that looks like progress but isn't.

    Deltas are None on the first snapshot (no prior to diff against).
    """
    snapshot_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    work_mode: WorkMode = WorkMode.ORIENTING
    shape: ProblemShape = ProblemShape.UNKNOWN
    shape_confidence: float = 0.0
    uncertainty_axis_count: int = 0
    live_frame_count: int = 0
    live_paradigm_count: int = 0
    active_pressures: list[str] = field(default_factory=list)
    resolution_delta: float | None = None   # genuine uncertainty reduction vs prior snapshot
    legibility_delta: float | None = None   # output cleanliness vs prior snapshot


# ---------------------------------------------------------------------------
# Aggregate frontier state
# ---------------------------------------------------------------------------

@dataclass
class FrontierState:
    """
    Full cognitive state for a frontier task.

    Read by the commitment gate (Phase D) and conservative fallback.
    The conservative fallback is a predicate here, not a subsystem —
    it reads internal state directly. No new infrastructure needed.

    Coexists with RuntimeState until Phase C migration.
    """
    task_id: str
    branch_id: str
    work_mode: WorkMode = WorkMode.ORIENTING
    geometry: TaskGeometry | None = None
    paradigms: dict[str, ParadigmCommitment] = field(default_factory=dict)
    frames: dict[str, Frame] = field(default_factory=dict)
    branches: dict[str, TypedBranch] = field(default_factory=dict)
    findings: list[MetacognitiveFinding] = field(default_factory=list)
    trajectory: list[TrajectorySnapshot] = field(default_factory=list)
    pressure_readings: list[PressureReading] = field(default_factory=list)
    is_conservative: bool = False
    conservative_reason: str | None = None

    # --- Accessors ---

    def blocking_findings(self) -> list[MetacognitiveFinding]:
        return [f for f in self.findings if f.blocks_commitment]

    def live_frames(self) -> list[Frame]:
        return [f for f in self.frames.values() if f.alive]

    def live_paradigms(self) -> list[ParadigmCommitment]:
        return [p for p in self.paradigms.values() if p.alive]

    def paradigms_without_rivals(self) -> list[ParadigmCommitment]:
        """Live paradigms with no registered rival. A warning sign."""
        return [p for p in self.live_paradigms() if not p.has_live_rival()]

    # --- Pressure detection ---

    def legibility_pressure_detected(self) -> bool:
        """
        True if recent trajectory shows legibility increasing while
        resolution is flat or declining.

        Uses last 3 snapshots. Needs at least 2 to have any deltas.
        """
        recent = [s for s in self.trajectory[-3:] if s.legibility_delta is not None]
        if not recent:
            return False
        legibility_up = any(s.legibility_delta > 0.1 for s in recent)
        resolution_stagnant = all(
            s.resolution_delta is None or s.resolution_delta < 0.05
            for s in recent
        )
        return legibility_up and resolution_stagnant

    # --- Conservative fallback ---

    def should_enter_conservative(self) -> tuple[bool, str | None]:
        """
        Conservative mode triggers when the system can't maintain cognitive
        state coherently. Returns (should_enter, reason).

        This is the honesty feature: a system that degrades gracefully and
        marks conclusions advisory under degraded conditions is more
        trustworthy than one that maintains confident output regardless.

        Triggers on:
        1. Legibility pressure signal (output cleanliness outrunning resolution)
        2. Paradigm abandoned under pressure (not evidence)
        3. Multiple unresolved blocking findings
        """
        if self.legibility_pressure_detected():
            return True, "legibility increasing while resolution stagnant — outputs advisory"
        dangerous_death = any(
            not p.alive and p.death_reason == ParadigmDeathReason.ABANDONED_UNDER_PRESSURE
            for p in self.paradigms.values()
        )
        if dangerous_death:
            return True, "paradigm abandoned under pressure without evidence — retrace before continuing"
        blocking = self.blocking_findings()
        if len(blocking) >= 2:
            return True, f"{len(blocking)} blocking findings unresolved — commitment gate closed"
        return False, None

    def enter_conservative(self) -> None:
        """Apply conservative mode based on current state."""
        should, reason = self.should_enter_conservative()
        if should:
            self.is_conservative = True
            self.conservative_reason = reason
            self.work_mode = WorkMode.CONSERVATIVE
