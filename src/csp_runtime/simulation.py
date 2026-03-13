from __future__ import annotations

from dataclasses import dataclass

from .models import RuntimeEvent, RuntimeEventType
from .runtime import Runtime


@dataclass
class ScenarioResult:
    scenario: str
    geometry: list[str]
    top_skill: str
    preflight_status: str
    next_action: str
    failure_modes: list[str]


def run_scenario(runtime: Runtime, scenario_name: str, text: str, validation_status: str = "pass") -> ScenarioResult:
    state = runtime.start_task(scenario_name, text)
    ranked = runtime.rank_skills(state)
    top = ranked[0]
    preflight = runtime.run_preflight(state, top.skill_id)
    runtime.commit_decision(state, top.skill_id, ranked)
    runtime.validate(state, status=validation_status)
    action = runtime.kernel.decide_next_action(state).event.value
    reassess = runtime.kernel.reassess(RuntimeEvent(RuntimeEventType.VALIDATION_REQUIRED, "post-validation"), state)

    failures: list[str] = []
    if preflight != "accept":
        failures.append("skill_selection_failure")
    if validation_status == "fail" and not reassess.should_reassess:
        failures.append("reassessment_failure")
    if action == RuntimeEventType.IMPLEMENTATION_READY.value and validation_status == "fail":
        failures.append("commitment_gate_failure")

    return ScenarioResult(
        scenario=scenario_name,
        geometry=state.geometry.labels,
        top_skill=top.skill_id,
        preflight_status=preflight,
        next_action=action,
        failure_modes=failures,
    )


def run_frontier_audit() -> list[ScenarioResult]:
    runtime = Runtime("src/skills")
    scenarios = [
        ("constraint_novel", "Novel constraint scheduling with hard/soft constraints and invariants", "pass"),
        ("systems_perf", "Protocol handshake latency spikes and throughput collapse under load", "pass"),
        ("formal_correctness", "Formal invariant proof for concurrent state-machine transitions", "pass"),
        ("underspecified_frontier", "weird bizarre unclear task", "fail"),
    ]
    return [run_scenario(runtime, name, text, validation) for name, text, validation in scenarios]


if __name__ == "__main__":
    for result in run_frontier_audit():
        print(result)
