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
/primitives         → return to fundamental stances when lost or drifting
```

You don't need all three startup plugins every time. Use judgment:

- Quick, bounded task in a known codebase: skip to `/compositional-coding`
- Returning to a project after a gap: run all three
- New project or unfamiliar codebase: run all three, in order
- Any time you feel uncertain about where the project actually is: `/context-rebuild`
- Lost mid-session, abstraction proliferating, or geometry unclear: `/primitives`

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

---

## Plugin locations

```
.claude/commands/env-sense.md
.claude/commands/context-rebuild.md
.claude/commands/compositional-coding.md
.claude/commands/primitives.md
```
