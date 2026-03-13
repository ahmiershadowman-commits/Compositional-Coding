# CSP-Governed Metacognitive Plugin Runtime (MVP)

This repository contains a runtime spine implementing:

- CSP kernel shell with geometry classification, uncertainty tracking, commitment gating, and reassessment.
- Hook dispatcher and canonical lifecycle event types.
- Lane-based context manager with branch and merge support.
- In-memory log store, pattern DB, decision store, and validation library.
- Skill registry plus five packaged initial skills under `src/skills/`.
- Frontier-audit simulation tooling for failure-mode discovery.

## Layout

- `src/csp_runtime/models.py`: runtime enums and dataclasses.
- `src/csp_runtime/kernel.py`: CSP control logic.
- `src/csp_runtime/hooks.py`: lifecycle hook dispatcher.
- `src/csp_runtime/stores.py`: context + persistence primitives.
- `src/csp_runtime/skills.py`: skill contract, semantic matching, and registry.
- `src/csp_runtime/runtime.py`: orchestrator wiring all modules.
- `src/csp_runtime/simulation.py`: usage simulation and failure-mode surfacing.
- `docs/metacognitive-layer-research.md`: production-grade layer comparison and fix strategy.
- `tests/test_runtime.py`: behavior and regression tests.

## Quick checks

```bash
python -m unittest discover -s tests -v
python scripts/run_frontier_audit.py
```
