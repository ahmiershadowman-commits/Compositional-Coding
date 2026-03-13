from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .models import ContextLaneType


@dataclass
class LogEvent:
    event_type: str
    task_id: str
    branch_id: str
    active_csp_mode: list[str]
    confidence: float
    details: dict[str, Any] = field(default_factory=dict)
    skill_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LogStore:
    def __init__(self) -> None:
        self._events: list[LogEvent] = []

    def append(self, event: LogEvent) -> None:
        self._events.append(event)

    def query(self, query_filter: dict[str, Any]) -> list[LogEvent]:
        return [
            e
            for e in self._events
            if all(getattr(e, k) == v for k, v in query_filter.items() if hasattr(e, k))
        ]

    def summarize(self, task_id: str, branch_id: str | None = None) -> dict[str, Any]:
        events = [e for e in self._events if e.task_id == task_id and (branch_id is None or e.branch_id == branch_id)]
        return {"count": len(events), "event_types": sorted(set(e.event_type for e in events))}


class PatternDB:
    def __init__(self, entries: list[dict[str, Any]] | None = None) -> None:
        self._entries = {e["pattern_id"]: e for e in (entries or [])}

    def search(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        family = query.get("family")
        return [e for e in self._entries.values() if family is None or e.get("family") == family]

    def get(self, pattern_id: str) -> dict[str, Any]:
        return self._entries[pattern_id]

    def suggest_alternatives(self, pattern_id: str) -> list[dict[str, Any]]:
        alt_ids = self._entries.get(pattern_id, {}).get("alternatives", [])
        return [self._entries[i] for i in alt_ids if i in self._entries]


class DecisionStore:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}
        self._counter = 0

    def create(self, record: dict[str, Any]) -> str:
        self._counter += 1
        rid = f"dec_{self._counter:05d}"
        self._records[rid] = {**record, "decision_id": rid}
        return rid

    def update(self, decision_id: str, patch: dict[str, Any]) -> None:
        if decision_id not in self._records:
            raise KeyError(f"Decision '{decision_id}' not found in store")
        self._records[decision_id].update(patch)

    def find_related(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        task_id = query.get("task_id")
        return [r for r in self._records.values() if task_id is None or r.get("task_id") == task_id]


class ValidationLibrary:
    def __init__(self, recipes: list[dict[str, Any]] | None = None) -> None:
        self._recipes = {r["recipe_id"]: r for r in (recipes or [])}

    def match(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        tags = set(query.get("tags", []))
        if not tags:
            return list(self._recipes.values())
        return [r for r in self._recipes.values() if tags.intersection(set(r.get("tags", [])))]

    def run(self, recipe_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if recipe_id not in self._recipes:
            raise KeyError(f"Validation recipe '{recipe_id}' not found")
        recipe = self._recipes[recipe_id]
        status = "pass" if data.get("status", "pass") == "pass" else "fail"
        return {"recipe_id": recipe_id, "status": status, "steps": recipe.get("steps", [])}


class ContextManager:
    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, dict[str, Any]]] = {}
        self._branch_count = 0

    def _ensure_task(self, task_id: str, branch_id: str) -> None:
        self._tasks.setdefault(task_id, {})
        self._tasks[task_id].setdefault(branch_id, {lane.value: {} for lane in ContextLaneType})

    def get_lane(self, task_id: str, branch_id: str, lane: ContextLaneType) -> dict[str, Any]:
        self._ensure_task(task_id, branch_id)
        return self._tasks[task_id][branch_id][lane.value]

    def pack_for_skill(self, task_id: str, branch_id: str, required_lanes: list[ContextLaneType]) -> dict[str, Any]:
        self._ensure_task(task_id, branch_id)
        return {lane.value: self._tasks[task_id][branch_id][lane.value] for lane in required_lanes}

    def update_lane(self, task_id: str, branch_id: str, lane: ContextLaneType, patch: dict[str, Any]) -> None:
        current = self.get_lane(task_id, branch_id, lane)
        current.update(patch)

    def branch(self, task_id: str, from_branch_id: str, reason: str) -> str:
        self._ensure_task(task_id, from_branch_id)
        self._branch_count += 1
        to_branch = f"branch_{self._branch_count:03d}"
        self._tasks[task_id][to_branch] = copy.deepcopy(self._tasks[task_id][from_branch_id])
        self._tasks[task_id][to_branch][ContextLaneType.METACOGNITIVE_STATE.value]["branch_reason"] = reason
        return to_branch

    def merge(self, task_id: str, source_branch_ids: list[str], target_branch_id: str) -> dict[str, Any]:
        self._ensure_task(task_id, target_branch_id)
        merged_from = []
        for source in source_branch_ids:
            if source not in self._tasks.get(task_id, {}):
                continue
            merged_from.append(source)
            for lane, payload in self._tasks[task_id][source].items():
                self._tasks[task_id][target_branch_id][lane].update(payload)
        return {"merged_from": merged_from, "target": target_branch_id}

    def summarize(self, task_id: str, branch_id: str, lane: ContextLaneType) -> dict[str, Any]:
        payload = self.get_lane(task_id, branch_id, lane)
        return {"lane": lane.value, "keys": sorted(payload.keys()), "hot": lane in {ContextLaneType.ACTIVE_TASK, ContextLaneType.METACOGNITIVE_STATE}}
