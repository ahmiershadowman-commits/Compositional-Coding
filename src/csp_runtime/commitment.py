"""
Commitment gate — evaluates ActionProposals against FrontierState + CriticFindings.

The gate is a pure function: it inspects state and findings and returns a
decision. It does not modify state. It does not reason or route.

The only logic here is: run critics, collect blockers, check conservative mode,
return (allowed, all_findings, reason). That's it.

If this module grows reasoning logic, the thin-coordinator constraint has
been violated. Move any reasoning back to the cognitive layer.
"""

from __future__ import annotations

from .critics import run_critics, Critic
from .frontier_models import ActionProposal, CriticFinding, FrontierState, ActionType
from .policies import CriticPolicy, DEFAULT_POLICY


def evaluate_commitment(
    state: FrontierState,
    proposal: ActionProposal,
    critics: list[Critic] | None = None,
    policy: CriticPolicy | None = None,
) -> tuple[bool, list[CriticFinding], str]:
    """
    Evaluate whether a proposal can be committed.

    Returns: (allowed, all_findings, reason)
      allowed: True if the gate passes
      all_findings: every finding from every critic (blocking and non-blocking)
      reason: human-readable explanation of the decision

    Conservative mode blocks everything except PROBE actions — the system
    can still gather evidence; it just can't commit to anything irreversible.
    """
    # Conservative mode check — probes are always allowed
    if state.is_conservative and proposal.action_type != ActionType.PROBE:
        return (
            False,
            [],
            f"conservative mode active ({state.conservative_reason}) — "
            "only PROBE actions allowed until cognitive state stabilizes",
        )

    findings = run_critics(state, proposal, critics, policy)
    blockers = [f for f in findings if f.blocking]

    if blockers:
        # Primary blocker is the first one; they are ordered by critic registration
        primary = blockers[0]
        return (
            False,
            findings,
            f"blocked by {primary.critic_name} [{primary.code.value}]: {primary.message}",
        )

    return True, findings, "all critics passed — commitment allowed"
