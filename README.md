# CSP-Governed Metacognitive Plugin Runtime (MVP)

This repository now contains an initial runtime spine implementing:

- CSP kernel shell with geometry classification, uncertainty tracking, and commitment gating.
- Hook dispatcher and canonical lifecycle event types.
- Lane-based context manager with branch and merge support.
- In-memory log store, pattern DB, decision store, and validation library.
- Skill registry plus five packaged initial skills under `src/skills/`.

## Layout

### Phase A–D frontier runtime (current)

- `src/csp_runtime/frontier_models.py`: Phase A+B+D schema — FrontierState, TaskGeometry, ParadigmCommitment, Frame, ActionProposal, CriticFinding, MetacognitiveGapRecord.
- `src/csp_runtime/events.py`: canonical EventType enum for all runtime events.
- `src/csp_runtime/policies.py`: CriticPolicy, DistillationPolicy, HydrationPolicy, RuntimePolicy with defaults.
- `src/csp_runtime/store.py`: SQLite persistence layer (stdlib sqlite3, zero new deps) — sessions, branches, states, memory, findings, proposals, gaps, events.
- `src/csp_runtime/critics.py`: 8 mandatory critics (pressure, frame, evidence, anomaly, completion, legibility, irreversibility, degeneration) + run_critics dispatcher.
- `src/csp_runtime/commitment.py`: commitment gate — pure function evaluating proposals against critic findings.
- `src/csp_runtime/gap_capture.py`: MetacognitiveGapRecord creation helpers.
- `src/csp_runtime/distillation.py`: episodic → semantic memory promotion gate.
- `src/csp_runtime/retrieval.py`: context hydration — loads working/episodic/semantic/procedural memory per HydrationPolicy.
- `src/csp_runtime/router.py`: thin deterministic coordinator wiring store, critics, gate, gap capture, and distillation.
- `tests/test_frontier.py`: 48 tests covering all frontier runtime modules.

### Legacy runtime (coexists until Phase C migration)

- `src/csp_runtime/models.py`: runtime enums and dataclasses.
- `src/csp_runtime/kernel.py`: CSP control logic.
- `src/csp_runtime/hooks.py`: lifecycle hook dispatcher.
- `src/csp_runtime/stores.py`: context + persistence primitives.
- `src/csp_runtime/skills.py`: skill contract and generic skill implementation.
- `src/csp_runtime/runtime.py`: orchestrator that wires all modules together.
- `src/csp_runtime/simulation.py`: multi-scenario frontier audit harness.
- `tests/test_runtime.py`: baseline behavior tests.

## Requirements

Python 3.11+. No third-party dependencies — stdlib only.

## Quick check

```bash
python -m unittest discover -s tests -v
```
