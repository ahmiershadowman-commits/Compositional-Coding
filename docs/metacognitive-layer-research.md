# Metacognitive Layer Audit, Failure Modes, and Production-Grade Fix Directions

## Simulated usage findings

Using `scripts/run_frontier_audit.py`, we simulated four scenarios:

1. novel symbolic-constraint workflow
2. systems/protocol performance incident
3. formal verification task
4. underspecified frontier-weird task

### Failure modes observed

- **Skill selection under sparse geometry**: underspecified requests can still return weak top candidates with low confidence and preflight defer/reject behavior.
- **Ontology mismatch risk**: skills often encode long, phrase-like trigger geometry while runtime classification emits compact labels (`constraint-rich`, `systems`, `formal`), which can suppress preflight acceptance unless semantic normalization exists.
- **Commitment gate fragility**: if context lanes are not synchronized into runtime state, commitment checks can silently fail open/closed.
- **Reassessment drift**: reassessment may never trigger if validation status is written to one lane/path while reassessment reads another.

## Production-grade metacognitive layers to borrow from

> This section summarizes well-known patterns from production multi-agent/runtime systems and formal orchestration stacks.

### 1) LangGraph-style explicit state graphs

- **Strength**: deterministic state-machine execution with durable checkpoints.
- **Fix contribution**: model CSP lifecycle as an explicit graph (`orient -> classify -> compare -> preflight -> probe -> implement -> validate -> reassess`), with typed transitions and replay support.
- **Adoption recommendation**: represent each hook event as a graph node; require guard predicates for every edge.

### 2) AutoGen/CrewAI-style multi-agent delegation with evaluator loops

- **Strength**: role-separated planner/executor/critic workflows.
- **Fix contribution**: enforce a mandatory critic pass before commitment, especially for frontier/novel tasks.
- **Adoption recommendation**: introduce a fixed `metacognitive-critic` sub-step that can veto implementation readiness.

### 3) Temporal/Cadence durable workflow engines

- **Strength**: reliable long-running orchestration, retries, idempotence, and event history.
- **Fix contribution**: robustly handle branch retries, probe fan-out, and deterministic replays.
- **Adoption recommendation**: externalize task/branch lifecycle into durable workflows for non-ephemeral execution.

### 4) OpenTelemetry + event-sourced audit pipelines

- **Strength**: globally queryable trace logs, structured spans, and postmortem analysis.
- **Fix contribution**: observability of skill routing, preflight rejections, and failure taxonomy frequencies.
- **Adoption recommendation**: map runtime events to trace spans and enrich with `task_id`, `branch_id`, `failure_type`, `confidence`.

### 5) Rules + model hybrid policy engines

- **Strength**: combines deterministic safety constraints (rules) with adaptive scoring (learned ranking).
- **Fix contribution**: avoid brittle keyword routing while still enforcing hard guardrails.
- **Adoption recommendation**: make skill ranking hybrid: (hard anti-fit rules) + (learned fit score) + (uncertainty reduction objective).

## Frontier-grade compositional/cognitive support to add next

1. **Contradiction cartographer skill**
   - Builds an explicit contradiction graph and tracks unresolved paradoxes.
2. **Hypothesis portfolio manager skill**
   - Maintains multiple competing models with Bayesian-ish confidence updates.
3. **Speculative probe synthesizer skill**
   - Automatically designs smallest discriminating probes to separate candidate substrates.
4. **Ontology bridge skill**
   - Aligns user vocabulary, skill trigger geometry, and runtime labels into a shared concept map.
5. **Anomaly semantics skill**
   - Classifies weird/bizarre outcomes as signal vs artifact vs instrumentation bug.
6. **Non-classical logic playground skill**
   - Supports paraconsistent, modal, or temporal reasoning when contradictions are first-class.
7. **Mechanism-first performance attribution skill**
   - Prevents premature optimization by demanding mechanism evidence before intervention.

## Concrete implementation deltas applied in this revision

- Added semantic normalization in skill scoring/preflight to reduce ontology mismatch.
- Synced context lanes into runtime state and updated commitment gate to read canonical metacognitive lane.
- Fixed reassessment to read validation status from the same lane updated by validation.
- Added a simulation harness that runs multi-scenario frontier audits and surfaces failure-mode tags.

