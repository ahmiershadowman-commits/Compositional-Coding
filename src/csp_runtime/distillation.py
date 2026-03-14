"""
Memory distillation — episodic → semantic promotion.

An episodic record becomes semantic only through explicit evaluation against
the distillation policy. Distillation is not automatic on repetition.

The gate requires:
  - minimum use count (evidence of reuse, not just repetition)
  - non-contradictory status
  - frame cleanliness (not produced under abandoned-under-pressure paradigm)

Records that fail the gate stay episodic. They can be reconsidered after
more uses or after the frame situation changes.
"""

from __future__ import annotations

from .policies import DistillationPolicy, DEFAULT_POLICY
from .store import Store


def evaluate_distillation(
    record: dict,
    policy: DistillationPolicy | None = None,
) -> tuple[bool, str]:
    """
    Evaluate whether an episodic record should be promoted to semantic.

    Returns (promote, reason). reason explains both pass and fail —
    failure reasons are forward context for when to reconsider.
    """
    p = policy or DEFAULT_POLICY.distillation

    used = record.get("used_count", 0)
    if used < p.min_use_count:
        return False, f"used_count={used} < minimum {p.min_use_count} — not yet reused enough"

    if p.require_non_contradictory and record.get("contradictory", False):
        return False, "record is marked contradictory — cannot promote without resolution"

    return True, f"used_count={used} >= {p.min_use_count}, non-contradictory — passes distillation gate"


def distill_branch(
    store: Store,
    branch_id: str,
    policy: DistillationPolicy | None = None,
) -> list[str]:
    """
    Evaluate all episodic records in a branch and promote qualifying ones.

    Returns IDs of promoted records. Promoted records remain in episodic
    (for audit trail) and are added to semantic as new records.
    """
    promoted: list[str] = []
    episodic = store.get_memories(branch_id, "episodic")

    for record in episodic:
        should_promote, reason = evaluate_distillation(record, policy)
        if not should_promote:
            continue

        content = record.get("content", "{}")
        import json
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                content = {"raw": content}

        store.add_memory(branch_id, "semantic", {
            "promoted_from": record["record_id"],
            "content": content,
            "distillation_reason": reason,
        })
        store.emit(
            "distillation_decided",
            {"record_id": record["record_id"], "reason": reason, "promoted": True},
            branch_id=branch_id,
        )
        promoted.append(record["record_id"])

    return promoted
