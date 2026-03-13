# symbolic-constraint-synthesis preflight

## First questions
- What must persist as invariants?
- What is uncertain enough to require probes before implementation?

## Common false-positive triggers
- Surface-level keyword matches without structural fit.
- Familiar workflows that bypass geometry comparison.

## Missing-information checks
- Required context lanes: active_task, metacognitive_state, pattern_references
- Validation tags required: solver-correctness, model-consistency

## Branch vs commit guidance
- Branch when uncertainty or anti-fit remains unresolved.
- Commit only after at least one alternative family comparison.
