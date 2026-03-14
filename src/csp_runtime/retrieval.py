"""
Memory retrieval and context hydration.

hydrate_context() builds the working context for a branch at session start
or after a significant state change. It respects the hydration policy:
  - semantic records always load (distilled, compact by design)
  - procedural records always load (skills, workflows, critic rules)
  - episodic records are capped to prevent context bloat
  - load-bearing items are NEVER stubbed

The geometry retrieval overlay (inferential-distance-based ranking) is a
future Phase E addition. This module handles the policy-governed loading;
the overlay will extend it without replacing it.
"""

from __future__ import annotations

from .policies import HydrationPolicy, DEFAULT_POLICY
from .store import Store


def hydrate_context(
    store: Store,
    branch_id: str,
    policy: HydrationPolicy | None = None,
) -> dict:
    """
    Build working context for a branch.

    Returns a dict with keys: working, semantic, episodic, procedural,
    blocking_findings, open_anomalies.

    Episodic records are trimmed to the most recent max_episodic_records.
    Semantic and procedural always load in full.
    """
    p = policy or DEFAULT_POLICY.hydration

    episodic_all = store.get_memories(branch_id, "episodic")
    # Most recent first (store orders by created_at ASC, so take tail)
    episodic = episodic_all[-p.max_episodic_records:] if len(episodic_all) > p.max_episodic_records else episodic_all

    return {
        "working": store.get_memories(branch_id, "working"),
        "semantic": store.get_memories(branch_id, "semantic") if p.always_load_semantic else [],
        "episodic": episodic,
        "procedural": store.get_memories(branch_id, "procedural") if p.always_load_procedural else [],
        "blocking_findings": store.get_blocking_findings(branch_id),
        "open_anomalies": store.get_open_anomalies(branch_id),
        "hydration_policy": {
            "episodic_loaded": len(episodic),
            "episodic_total": len(episodic_all),
            "capped": len(episodic_all) > p.max_episodic_records,
        },
    }


def get_high_curvature_memories(
    context: dict,
    top_n: int = 3,
) -> list[dict]:
    """
    Approximate high-curvature retrieval from hydrated context.

    Curvature proxy: used_count. Records referenced more often are
    more likely to be load-bearing. This is a metric approximation —
    the full geometry overlay (Phase E) will use inferential distance.
    """
    candidates = context.get("semantic", []) + context.get("procedural", [])
    return sorted(candidates, key=lambda r: r.get("used_count", 0), reverse=True)[:top_n]
