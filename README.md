# CSP-Governed Metacognitive Plugin Runtime (MVP)

This repository now contains an initial runtime spine implementing:

- CSP kernel shell with geometry classification, uncertainty tracking, and commitment gating.
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
- `tests/test_runtime.py`: baseline behavior tests.

## Quick check

```bash
python -m unittest discover -s tests -v
```
