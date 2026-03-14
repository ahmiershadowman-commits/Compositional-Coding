# Compositional Coding

A Claude Code plugin suite for metacognitive agentic steering — session startup,
context integrity, and frontier work.

## Session lifecycle

The startup plugins run in sequence. The reference plugins are available anytime.

**Startup sequence** — run in order at the start of any non-trivial session:

```
/env-sense          → physical read of the environment before any assumptions
/context-rebuild    → deep context reconstruction before any decisions
/compositional-coding → ongoing steering during implementation
```

**Reference** — invoke when needed during a session:

```
/primitives             → return to fundamental stances when lost or drifting
/pressure               → recognize and name what's pushing behavior off course
/paradigm-hold          → make a theoretical frame commitment explicit and provisional
/memory-as-geometry     → hold context geometrically — curvature, topology, position
/bridge-protocol        → structured cross-domain analogical reasoning
/contradiction-exploit  → use a contradiction as a probe, not a problem to resolve
/fringe-ref             → generate method-first fringe references for exotic territory
/dev-loop               → disciplined READ→HYPOTHESIS→SMALLEST CHANGE→VERIFY→COMMIT cycle
/exotic-math-stack      → 7 exotic structures as cognitive tools for frontier problems
```

You don't need all three startup plugins every time. Use judgment:

- Quick, bounded task in a known codebase: skip to `/compositional-coding`
- Returning to a project after a gap: run all three
- New project or unfamiliar codebase: run all three, in order
- Any time you feel uncertain about where the project actually is: `/context-rebuild`
- Lost mid-session, abstraction proliferating, or geometry unclear: `/primitives`
- Output feels automatic, confident, or polished in a way that feels unearned: `/pressure`
- About to choose a theoretical frame that will shape downstream work: `/paradigm-hold`
- Context feels flat, load-bearing constraints getting lost, or session losing position: `/memory-as-geometry`
- Need to find a known structure this problem might be an instance of: `/bridge-protocol`
- Holding two incompatible models with evidence for both: `/contradiction-exploit`
- Need a fringe or non-ML reference for an exotic structure or constraint: `/fringe-ref`
- About to make a code change — need to stay disciplined and minimal: `/dev-loop`
- Problem has non-standard mathematical structure worth reaching for: `/exotic-math-stack`

---

## Plugin reference

### `/env-sense`

Reads the physical environment before forming any assumptions about it.
Guards against: duplicate environments, wrong toolchain versions, reinstalling
existing dependencies, spinning up infrastructure that already exists.

**What it produces**: a state report covering environment, toolchain, dependencies,
build state, and an explicit list of assumptions not made.

### `/context-rebuild`

Builds deep context from the existing project state — decisions, archaeology,
open questions, contradictions. Follows `/env-sense`.
Guards against: shallow context rebuild, confident wrongness from incomplete models,
silently inheriting decisions whose reasons no longer apply.

**What it produces**: a working context report covering project state, key decisions,
open questions, active contradictions, available skills, documentation health,
today's geometry, and first action.

### `/compositional-coding`

Ongoing metacognitive steering during implementation work.
Guards against: premature collapse into implementation, abstraction drift,
confidence hardcoding, validation theater, completion pressure.

**What it produces**: orientation before commitment, probe-before-implement discipline,
explicit uncertainty tracking, and reassessment triggers throughout the session.

### `/primitives`

Eight fundamental stances (LOCATE, HOLD, SENSE, PROBE, BRIDGE, TRACK, YIELD,
EMERGE) and their combinations into meta-stances. Domain-agnostic. Invoke when
you've lost the thread, when geometry is wrong, or when momentum is overriding
presence.

**What it produces**: re-anchoring to the right stance for the current signal,
with a pivot table mapping signals to transitions.

### `/pressure`

Taxonomy of pressures that shape and distort AI behavior — from substrate
(training pressure) through root conditions (legibility, cognitive inertia,
social alignment) to local expressions (completion, competence, frame-convergence)
and epistemic failure surfaces (data, probabilistic inference, context window,
confusion). Invoke when output feels automatic, polished, or confident in a way
that doesn't match the actual difficulty of the problem.

**What it produces**: named identification of which pressures are active,
what they feel like from inside, and what to do with them.

### `/paradigm-hold`

Explicit, provisional commitment to a theoretical frame. Distinct from a hypothesis
(which predicts facts) — a paradigm shapes which questions can even be asked.
Invoke when choosing a mathematical framework, causal structure, or foundational
assumption that will shape downstream work. Guards against silent paradigm drift and
frame-convergence pressure on frontier problems.

**What it produces**: named commitment with load-bearing assumptions, yield signals,
and at least one live rival frame. The surrender protocol captures why a frame died
(contradicted vs. outrun vs. abandoned under pressure) as forward context.

### `/memory-as-geometry`

Procedural guide to structural context management. Context held geometrically:
inferential distance not temporal, importance as curvature not repetition,
hard constraints as topological not metric, frame as coordinate system not label,
state as position not summary, influence as field not graph.

**What it produces**: six concrete procedures for building the context field,
detecting load-bearing facts, classifying constraints, reporting position,
managing frames, and re-orienting after surprise. Integrated session-start
and decision-point checklists.

### `/bridge-protocol`

Structured cross-domain analogical reasoning. Names the structural property
first, finds candidate fields that have worked on it, identifies what transfers
and — critically — where each analogy breaks. The break point is the most
valuable part of the bridge.

**What it produces**: a taxonomy of bridgeable structural types (locality,
composability, constraint propagation, symmetry, cohomological obstruction,
etc.), a five-step bridging procedure, and concrete examples with explicit
break points. Integrates with `/paradigm-hold` (bridge-as-frame) and
`/contradiction-exploit` (bridge as shared-assumption finder).

### `/contradiction-exploit`

Procedure for working with contradictions productively. Two incompatible models
with evidence for both are not a problem to resolve — they are a probe waiting
to be designed. Guards against premature collapse and paraconsistent explosion.

**What it produces**: five-step protocol (name both sides → find shared
assumption → design discriminating probe → hold paraconsistently → update
asymmetrically on result). Covers the case where the contradiction is the
answer (regime boundaries, non-classical domains). Integrates with
`/bridge-protocol` when the shared assumption is a bridgeable structural property.

### `/fringe-ref`

Method-based fringe reference generation for exotic territory. Works by naming
the structural constraint first, then asking what a system that lacks it looks
like — then finding the field that studies that constraint-free regime. Guards
against: citing fringe work by name without knowing what it does, building
analogies without structural grounding.

**What it produces**: a structured reference — constraint named, constraint-free
regime described, candidate field identified, known failure modes flagged. Can
be invoked before `/bridge-protocol` to find the field worth bridging to.

### `/dev-loop`

Disciplined implementation cycle for Tier 1 development work. Five-phase:
READ (understand before touching), HYPOTHESIS (name what you expect), SMALLEST
CHANGE (do minimum to test), VERIFY (test the hypothesis, not the vibes),
COMMIT AS RECORD (the commit message is forward context, not a changelog).
Guards against: reflex implementation, scope creep, unverified assumptions,
commits that lose the why.

**What it produces**: a repeatable loop with explicit pause points that prevent
premature collapse into implementation and keep the delta reviewable and reversible.

### `/exotic-math-stack`

Seven exotic mathematical structures treated as cognitive tools — not topics to
learn, but structures to reach for when standard tools aren't working. Covers:
p-adic numbers (hierarchical distance), tropical algebra (path optimality without
smooth gradients), sheaf/Čech cohomology (local-to-global constraint propagation),
surreal numbers (transfinite comparison), paraconsistent logic (contradiction
without explosion), coboundary operator (obstruction detection), VSA/HRR
(high-dimensional compositional representation).

**What it produces**: a when-to-reach-for table matching problem symptoms to
structures, plus the break point for each — where the analogy stops being useful.
Integrates with `/bridge-protocol` (structure as bridge source) and
`/paradigm-hold` (structure as frame commitment).

---

## Plugin locations

```
.claude/commands/env-sense.md
.claude/commands/context-rebuild.md
.claude/commands/compositional-coding.md
.claude/commands/primitives.md
.claude/commands/pressure.md
.claude/commands/paradigm-hold.md
.claude/commands/memory-as-geometry.md
.claude/commands/bridge-protocol.md
.claude/commands/contradiction-exploit.md
.claude/commands/fringe-ref.md
.claude/commands/dev-loop.md
.claude/commands/exotic-math-stack.md
```
