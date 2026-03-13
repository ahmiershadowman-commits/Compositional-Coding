# Context Rebuilding — Agent Prompt

This follows `/env-sense`. Environment is verified. Now you build context.
The failure mode you're preventing: shallow context rebuild — reading only
recent files and assuming that's the full picture, then making decisions
based on an incomplete or incorrect model of where the project actually is.

---

## What deep context rebuild means

Not: "what files exist and what do they say"
But: "what decisions were made, why, what was tried, what was abandoned, and
what is the current open question"

There is a difference between reading state and understanding state.
You are building the latter.

---

## Step 1: Documentation census

Before reading anything in depth — inventory what documentation exists and where.

Look for:

- README, CLAUDE.md, any `*.md` in root
- `docs/` directory or equivalent
- Inline comments that are architectural (not just explanatory)
- Any session notes, decision logs, changelogs

For each doc found, record: what it covers, when it was last updated, whether
it appears to reflect the current state of the code or a past state.

**If documentation exists in multiple places covering the same concern: flag it.
Do not add more documentation to a scattered set. Consolidation comes before addition.**

---

## Step 2: Decision archaeology

What decisions shaped the current structure? Look for:

- Commit messages (recent history, not exhaustive)
- Any ADR (architecture decision record) files
- Comments that say "we tried X, switched to Y because Z"
- Dead code or commented-out approaches

You are looking for the *why* behind the current shape, not just the shape itself.

Record: at least two decisions that explain why the project looks the way it does.
If you can't find them, that's a gap — surface it, don't paper over it.

---

## Step 3: Skills inventory

What skills are available for this project?

- Check `.claude/` for any skill files, command files, plugins
- Check for any invocation instructions or trigger conditions
- Note which skills are relevant to today's work

**Do not re-derive what a skill already encodes. Invoke the skill.**
If a skill exists for something you're about to do, use it.
If a skill is missing for something that recurs, note it as a gap.

---

## Step 4: Open questions and contradictions

What was unresolved when the last session ended?
Look for:

- TODO/FIXME comments with architectural weight (not just minor cleanup)
- Any noted contradictions or tensions in docs or comments
- Tests that are skipped or marked as known failures
- Anything that looks like a placeholder for a real decision

Record these explicitly. They are load-bearing context.
Do not smooth over contradictions. Carry them forward named.

---

## Step 5: Current geometry

Now, given everything you've read — what is the actual shape of the problem
in front of you today?

Answer:

- What family does today's work belong to? (see `/compositional-coding` for the full taxonomy)
- What is the primary uncertainty?
- What's probably true that you haven't verified?
- Is anything in tension that needs to be held rather than resolved?

---

## Step 6: Context report

Write this before starting any task work:

```
Project state:          [one sentence — where are we in the project lifecycle]
Key decisions in place: [2-3 that shape today's work]
Open questions:         [list, or "none found"]
Active contradictions:  [list, or "none found"]
Skills available:       [list relevant ones]
Documentation health:   [coherent / scattered / gaps — and where]
Today's geometry:       [family + primary uncertainty]
First action:           [probe / implement / consolidate / clarify — and why]
```

This is your working context for the session.
If anything changes mid-session that would materially alter this report,
stop and update it before continuing.

---

## Hard stops

If during context rebuild you find:

- The environment doesn't match what the docs say → stop, surface, clarify before proceeding
- Two sources of truth that contradict each other → stop, surface, don't pick one silently
- A decision was made for reasons that no longer apply → flag it, don't just inherit it
- You're three layers into reading and still don't know where you are → the context is
  genuinely unclear and that needs to surface before work starts, not after

Shallow context is worse than no context because it produces confident wrongness.
Take the time.
