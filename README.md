# Compositional Coding Plugin

This repository now contains an initial runtime spine implementing:

- Cognitive Scaffolding Protocol kernel shell with geometry classification, uncertainty tracking, and commitment gating.
- Hook dispatcher and canonical lifecycle event types.
- Lane-based context manager with branch and merge support.
- In-memory log store, pattern DB, decision store, and validation library.
- Skill registry plus five packaged initial skills under `src/skills/`.

## Layout

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
