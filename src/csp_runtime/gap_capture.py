"""
Gap capture utilities.

Creates MetacognitiveGapRecord objects from current runtime state.
The gap intelligence lane feeds the eval/regression harness.

Gap capture is called by the router when execution produces unexpected
results, when critics detect degeneration, or when the cognitive layer
explicitly requests gap recording. It is not called automatically on
every critic finding — only on genuine failures or missed cues.
"""

from __future__ import annotations

import uuid

from .frontier_models import (
    FrontierState,
    GapIssueLevel,
    GapType,
    MetacognitiveGapRecord,
    WorkMode,
)


def capture_gap(
    state: FrontierState,
    gap_type: GapType,
    issue_level: GapIssueLevel,
    loop_stage: str,
    missed_cue: str,
    observed_behavior: str,
    better_behavior: str,
    recurrence_risk: float,
    proposed_support: str | None = None,
    frame_id: str | None = None,
) -> MetacognitiveGapRecord:
    """
    Create a MetacognitiveGapRecord from current state.

    The pressure_snapshot is captured automatically from active pressure readings.
    Caller provides the four required answers:
      - what cue was missed (missed_cue)
      - what actually happened (observed_behavior)
      - what should have happened (better_behavior)
      - how likely this is to recur (recurrence_risk 0.0–1.0)
    """
    pressure_snapshot = {
        r.pressure_name: r.intensity
        for r in state.pressure_readings
        if r.active
    }
    return MetacognitiveGapRecord(
        gap_id=f"gap_{uuid.uuid4().hex[:12]}",
        gap_type=gap_type,
        issue_level=issue_level,
        loop_stage=loop_stage,
        mode=state.work_mode,
        missed_cue=missed_cue,
        observed_behavior=observed_behavior,
        better_behavior=better_behavior,
        recurrence_risk=recurrence_risk,
        frame_id=frame_id,
        pressure_snapshot=pressure_snapshot,
        proposed_support=proposed_support,
    )


def classify_issue_level(recurrence_risk: float, gap_type: GapType) -> GapIssueLevel:
    """
    Heuristic for issue level classification.

    High recurrence risk or structural gaps → architectural.
    Moderate recurrence → policy.
    Low recurrence → local.

    Caller should override when they have domain context the heuristic doesn't.
    """
    if gap_type == GapType.SCAFFOLD_ABSENT:
        return GapIssueLevel.ARCHITECTURAL
    if recurrence_risk >= 0.7:
        return GapIssueLevel.ARCHITECTURAL
    if recurrence_risk >= 0.4:
        return GapIssueLevel.POLICY
    return GapIssueLevel.LOCAL
