# Compositional Coding

A Claude Code plugin for metacognitive agentic steering on frontier work.

## Usage

Type `/compositional-coding` at the start of any session to activate the steering
prompt. It reorients Claude toward probing before implementing, holding uncertainty
explicitly, and guarding against premature commitment.

## When to use it

- Novel architectures with no clear prior family
- Exotic math or non-standard problem shapes
- Any task where the wrong framing would be expensive to undo
- When you want Claude to orient before it acts, not after

## What it guards against

- Premature collapse into implementation
- Abstraction drift (building infrastructure instead of solving the problem)
- Confidence hardcoding (confidence numbers without derivation)
- Validation theater (checks that always pass)
- Completion pressure (finishing the wrong thing correctly)

## Plugin location

`.claude/commands/compositional-coding.md`
