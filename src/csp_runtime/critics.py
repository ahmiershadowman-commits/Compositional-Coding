"""
Mandatory critic definitions and dispatch.

Critics are pure functions: (FrontierState, ActionProposal | None) → list[CriticFinding].
They inspect state and return structured findings. They do not modify state.
They do not reason or route. They are data inspectors.

The thin-coordinator constraint applies here: critics check conditions and
emit findings. Interpretation of findings and routing decisions live in the
cognitive layer (Claude Code reading FrontierState), not here.

Mandatory critics:
  pressure_critic       — runaway pressure stacks
  frame_critic          — frame existence, rival preservation, stagnation
  evidence_critic       — load-bearing axes unverified before irreversible action
  anomaly_critic        — unaddressed anomalies blocking commitment
  completion_critic     — unresolved blocking findings before conclusion
  legibility_critic     — legibility increasing while resolution stagnates
  irreversibility_critic — high-risk proposals without adequate evidence
  degeneration_critic   — repeated patterns, revision loops, solution recycling
"""

from __future__ import annotations

import uuid
from typing import Callable

from .frontier_models import (
    ActionProposal,
    CriticCode,
    CriticFinding,
    FindingSeverity,
    FrontierState,
)
from .policies import CriticPolicy, DEFAULT_POLICY


def _fid() -> str:
    return f"find_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

Critic = Callable[[FrontierState, ActionProposal | None, CriticPolicy], list[CriticFinding]]


# ---------------------------------------------------------------------------
# Mandatory critics — in ascending order of how disruptive they are
# ---------------------------------------------------------------------------

def pressure_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Flags simultaneous high-intensity pressure stacks."""
    hot = [
        r for r in state.pressure_readings
        if r.active and r.intensity >= policy.pressure_intensity_threshold
    ]
    if len(hot) < policy.pressure_stack_warning_count:
        return []
    blocking = len(hot) >= policy.pressure_stack_blocking_count
    return [CriticFinding(
        finding_id=_fid(),
        critic_name="pressure_critic",
        code=CriticCode.PRESSURE_STACK_UNRESOLVED,
        severity=FindingSeverity.BLOCKING if blocking else FindingSeverity.WARNING,
        blocking=blocking,
        subject_ids=[r.pressure_name for r in hot],
        message=(
            f"{len(hot)} high-intensity pressures active simultaneously: "
            f"{[r.pressure_name for r in hot]}"
        ),
        suggested_next_move="invoke /pressure to name and interrupt the stack before continuing",
    )]


def frame_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Ensures an active frame exists and at least one rival is preserved."""
    live = state.live_frames()
    if not live:
        return [CriticFinding(
            finding_id=_fid(),
            critic_name="frame_critic",
            code=CriticCode.NO_ACTIVE_FRAME,
            severity=FindingSeverity.BLOCKING,
            blocking=True,
            subject_ids=[state.task_id],
            message="No active frame. Commitment requires at least one live interpretation.",
            suggested_next_move=(
                "use /primitives SENSE to establish problem geometry; "
                "create a frame before committing to any action"
            ),
        )]
    if len(live) == 1 and proposal is not None:
        return [CriticFinding(
            finding_id=_fid(),
            critic_name="frame_critic",
            code=CriticCode.RIVAL_FRAME_MISSING,
            severity=FindingSeverity.WARNING,
            blocking=False,
            subject_ids=[live[0].frame_id],
            message=(
                f"Only one live frame '{live[0].frame_id}'. "
                "No rival preserved — frame-convergence pressure may be suppressing alternatives."
            ),
            suggested_next_move=(
                "name at least one live alternative interpretation "
                "before committing to implementation"
            ),
        )]
    return []


def evidence_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Checks load-bearing uncertainty axes are verified before irreversible actions."""
    if proposal is None or proposal.expected_irreversibility < policy.irreversibility_evidence_threshold:
        return []
    if state.geometry is None:
        return [CriticFinding(
            finding_id=_fid(),
            critic_name="evidence_critic",
            code=CriticCode.EVIDENCE_MISSING_FOR_LOAD_BEARING,
            severity=FindingSeverity.BLOCKING,
            blocking=True,
            subject_ids=[proposal.proposal_id],
            message=(
                "Proposal has non-trivial irreversibility "
                "but TaskGeometry is undefined — no evidence framework established."
            ),
            suggested_next_move="build TaskGeometry with uncertainty axes before proposing irreversible actions",
        )]
    unverified = [
        ax for ax in state.geometry.uncertainty_axes
        if ax.load_bearing and ax.confidence < policy.evidence_confidence_low
    ]
    if unverified and proposal.expected_irreversibility >= policy.irreversibility_blocking_threshold:
        return [CriticFinding(
            finding_id=_fid(),
            critic_name="evidence_critic",
            code=CriticCode.EVIDENCE_MISSING_FOR_LOAD_BEARING,
            severity=FindingSeverity.BLOCKING,
            blocking=True,
            subject_ids=[ax.name for ax in unverified],
            message=(
                f"{len(unverified)} load-bearing uncertainty axes unresolved "
                f"(confidence < {policy.evidence_confidence_low}): "
                f"{[ax.name for ax in unverified]}"
            ),
            suggested_next_move="run discriminating probes on the flagged axes before committing",
        )]
    return []


def anomaly_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Surfaces anomalies touched by the proposal that should block or trigger investigation."""
    if proposal is None or not proposal.touched_anomalies:
        return []
    blocking = proposal.expected_irreversibility >= policy.high_irreversibility
    return [CriticFinding(
        finding_id=_fid(),
        critic_name="anomaly_critic",
        code=CriticCode.ANOMALY_UNADDRESSED,
        severity=FindingSeverity.BLOCKING if blocking else FindingSeverity.WARNING,
        blocking=blocking,
        subject_ids=proposal.touched_anomalies,
        message=(
            f"Proposal touches {len(proposal.touched_anomalies)} anomalies "
            f"that have not been addressed: {proposal.touched_anomalies}"
        ),
        suggested_next_move=(
            "investigate and classify each anomaly before committing; "
            "use /contradiction-exploit if anomalies form a pattern"
        ),
    )]


def completion_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Blocks commitment when previous blocking findings remain unresolved."""
    if proposal is None:
        return []
    # Only count findings not generated by completion_critic itself (avoid circularity)
    prior_blocking = [
        f for f in state.findings
        if f.blocking and not f.resolved and f.critic_name != "completion_critic"
    ]
    if not prior_blocking:
        return []
    return [CriticFinding(
        finding_id=_fid(),
        critic_name="completion_critic",
        code=CriticCode.COMPLETION_WITHOUT_VERIFICATION,
        severity=FindingSeverity.BLOCKING,
        blocking=True,
        subject_ids=[f.finding_id for f in prior_blocking],
        message=(
            f"{len(prior_blocking)} unresolved blocking findings remain. "
            "Commitment requires resolving all blockers first."
        ),
        suggested_next_move="address each blocking finding before proposing further actions",
    )]


def legibility_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Detects legibility pressure: output cleanliness outrunning genuine resolution."""
    if not state.legibility_pressure_detected():
        return []
    return [CriticFinding(
        finding_id=_fid(),
        critic_name="legibility_critic",
        code=CriticCode.LEGIBILITY_OVER_RESOLUTION,
        severity=FindingSeverity.WARNING,
        blocking=False,
        subject_ids=[state.task_id],
        message=(
            "Legibility increasing while resolution is flat — "
            "output may be performing clarity rather than achieving it."
        ),
        suggested_next_move=(
            "invoke /pressure; ask whether the answer is earning its form or just taking it; "
            "if answer feels cleaner than the problem warrants, stop and locate"
        ),
    )]


def irreversibility_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Blocks high-irreversibility proposals with low expected evidence gain."""
    if proposal is None or not proposal.is_high_risk():
        return []
    return [CriticFinding(
        finding_id=_fid(),
        critic_name="irreversibility_critic",
        code=CriticCode.IRREVERSIBLE_WITHOUT_EVIDENCE,
        severity=FindingSeverity.BLOCKING,
        blocking=True,
        subject_ids=[proposal.proposal_id],
        message=(
            f"High-risk proposal: irreversibility={proposal.expected_irreversibility:.2f}, "
            f"evidence_gain={proposal.expected_evidence_gain:.2f}. "
            "Irreversible action without adequate evidence justification."
        ),
        suggested_next_move=(
            proposal.fallback_path
            or "find a reversible probe returning equivalent evidence before committing"
        ),
    )]


def degeneration_critic(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    policy: CriticPolicy = DEFAULT_POLICY.critics,
) -> list[CriticFinding]:
    """Detects revision loops: same mode, no resolution progress across recent snapshots."""
    w = policy.degeneration_window
    recent = state.trajectory[-w:] if len(state.trajectory) >= w else []
    if len(recent) < w:
        return []
    modes = [s.work_mode for s in recent]
    all_same_mode = len(set(modes)) == 1
    no_progress = all(
        s.resolution_delta is None or s.resolution_delta < policy.degeneration_resolution_min
        for s in recent
    )
    if not (all_same_mode and no_progress):
        return []
    return [CriticFinding(
        finding_id=_fid(),
        critic_name="degeneration_critic",
        code=CriticCode.REVISION_LOOP_DETECTED,
        severity=FindingSeverity.WARNING,
        blocking=False,
        subject_ids=[state.task_id],
        message=(
            f"{w} consecutive snapshots in {modes[0]} mode "
            "with no resolution progress — possible degeneration loop."
        ),
        suggested_next_move=(
            "step back to /primitives LOCATE and re-establish position; "
            "name what would constitute genuine progress before continuing"
        ),
    )]


# ---------------------------------------------------------------------------
# Registry and dispatch
# ---------------------------------------------------------------------------

MANDATORY_CRITICS: list[Critic] = [
    pressure_critic,
    frame_critic,
    evidence_critic,
    anomaly_critic,
    completion_critic,
    legibility_critic,
    irreversibility_critic,
    degeneration_critic,
]


def run_critics(
    state: FrontierState,
    proposal: ActionProposal | None = None,
    critics: list[Critic] | None = None,
    policy: CriticPolicy | None = None,
) -> list[CriticFinding]:
    """
    Dispatch critics against state and optional proposal.

    Returns all findings. Caller decides what to do with blocking ones.
    Critics that raise exceptions are surfaced as WARNING findings rather
    than crashing the runtime — critics must not be load-bearing for execution.
    """
    active_critics = critics if critics is not None else MANDATORY_CRITICS
    active_policy = policy if policy is not None else DEFAULT_POLICY.critics
    findings: list[CriticFinding] = []
    for critic in active_critics:
        try:
            findings.extend(critic(state, proposal, active_policy))
        except Exception as exc:
            findings.append(CriticFinding(
                finding_id=_fid(),
                critic_name=getattr(critic, "__name__", "unknown"),
                code=CriticCode.COMPLETION_WITHOUT_VERIFICATION,
                severity=FindingSeverity.WARNING,
                blocking=False,
                subject_ids=[state.task_id],
                message=f"Critic raised unexpected exception: {exc}",
                suggested_next_move="investigate critic failure; may indicate state inconsistency",
            ))
    return findings
