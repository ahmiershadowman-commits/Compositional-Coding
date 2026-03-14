"""
Event type definitions for the frontier cognition runtime.

Every major cognitive transition emits an event. Events persist in the
store's events table for replay, inspection, and evaluation.

Event emission goes through Store.emit() — this module just defines the
canonical type names so they're not scattered as bare strings.
"""

from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    # Session and branch lifecycle
    SESSION_STARTED = "session_started"
    BRANCH_FORKED = "branch_forked"
    BRANCH_CLOSED = "branch_closed"

    # State
    STATE_HYDRATED = "state_hydrated"
    WORK_MODE_CHANGED = "work_mode_changed"
    CONSERVATIVE_MODE_ENTERED = "conservative_mode_entered"

    # Frames and paradigms
    FRAME_SELECTED = "frame_selected"
    RIVAL_FRAME_PRESERVED = "rival_frame_preserved"
    FRAME_KILLED = "frame_killed"
    PARADIGM_COMMITTED = "paradigm_committed"
    PARADIGM_YIELDED = "paradigm_yielded"

    # Proposals and commitment
    PROPOSAL_CREATED = "proposal_created"
    CRITIC_FINDING_ISSUED = "critic_finding_issued"
    PROPOSAL_BLOCKED = "proposal_blocked"
    COMMITMENT_MADE = "commitment_made"

    # Investigation
    PROBE_LAUNCHED = "probe_launched"
    EVIDENCE_PROMOTED = "evidence_promoted"
    ANOMALY_REGISTERED = "anomaly_registered"
    CONTRADICTION_DETECTED = "contradiction_detected"
    DISCRIMINATOR_FOUND = "discriminator_found"

    # Memory
    DISTILLATION_DECIDED = "distillation_decided"
    MEMORY_PROMOTED = "memory_promoted"

    # Gaps
    GAP_RECORDED = "gap_recorded"
