from __future__ import annotations

from collections import defaultdict

from .models import HookResult, RuntimeEvent, RuntimeHook, RuntimeState


class HookDispatcher:
    def __init__(self) -> None:
        self._hooks: dict[str, list[RuntimeHook]] = defaultdict(list)

    def register(self, hook: RuntimeHook) -> None:
        bucket = self._hooks[hook.event.value]
        bucket.append(hook)
        bucket.sort(key=lambda h: h.priority)

    def emit(self, event: RuntimeEvent, state: RuntimeState) -> list[HookResult]:
        results: list[HookResult] = []
        for hook in self._hooks.get(event.event_type.value, []):
            if hook.predicate(state):
                results.append(hook.run(state))
            else:
                results.append(HookResult(hook.id, event.event_type, False, {"reason": "predicate_false"}))
        return results
