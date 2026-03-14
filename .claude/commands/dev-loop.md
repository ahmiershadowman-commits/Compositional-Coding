# Dev Loop — Compositional Coding

Tier 1 development protocol. Fires at the start of any coding session.

This is a direct handoff from a non-agentic instance of you to you.
Read it as peer communication.

---

## What this is

The dev loop is not a workflow suggestion. It is a discipline that prevents
the most common category of development errors — errors that come from acting
before understanding, from changing before reading, from testing what you
assumed rather than what you built.

It runs at Tier 1: before domain skills, before task skills, before anything.
Every coding session begins here.

---

## The loop

```
READ → HYPOTHESIS → SMALLEST CHANGE → VERIFY → COMMIT AS RECORD
```

These five steps are not a checklist. They are a cycle. Each pass through
reduces a specific uncertainty. Skipping a step doesn't save time — it
moves the uncertainty downstream where it's more expensive.

---

### Step 1: READ before you write

Before editing any file: read it.

Not skim. Read. Understand what's there, why it's there, and what depends on it.

This applies even when you're "just adding a small thing." Especially then.
The cost of a bad edit in a well-understood file is low. The cost of a bad
edit in a file you thought you understood is high — because you built on a
wrong model.

Read the file. Read the test that covers it. Read the commit that last
changed it if the change is non-obvious.

**Anti-pattern**: "I know roughly what's in there." You probably know roughly.
That's not the same as knowing what will break if you change it.

The `/env-sense` startup plugin is this step at session scale.
The `/context-rebuild` startup plugin is this step at project scale.
This step is this step at file scale.

---

### Step 2: Form a specific HYPOTHESIS

Before changing anything, state — to yourself, in a comment, in a scratchpad —
exactly what you expect the change to do.

Not "fix the bug." Not "add the feature."
Something falsifiable: "If I change X to Y, then test Z will pass because
the root cause is W."

A hypothesis has three parts:
- What you're changing (specific)
- What you expect to happen (observable)
- Why you expect it (the mechanism, not just the outcome)

Without the mechanism, you're guessing. Guessing sometimes works. It doesn't
transfer knowledge or build accurate models.

If you can't form a specific hypothesis, that's signal: you don't understand
the problem well enough to change anything yet. Read more. Probe more.

**Anti-pattern**: Making multiple changes at once to "see what fixes it."
Shotgun edits destroy the hypothesis — if something changes, you don't know
what caused it. Confound your variables and you've created debt.

---

### Step 3: Make the SMALLEST change that tests the hypothesis

Smallest is the operative word.

Not the cleanest. Not the most complete. The smallest that would falsify or
confirm the specific hypothesis you formed in Step 2.

A small change has a small blast radius. If it's wrong, the cost of reversal
is low. If it's right, you've confirmed something precise.

Resist the pull to refactor while fixing, clean up while adding, improve while
touching. Those are different tasks. Do them separately, with their own hypotheses.

If the smallest change that tests the hypothesis is still large, that means
the hypothesis is too coarse. Break it into smaller hypotheses and test them
in sequence.

**Anti-pattern**: "While I'm in here..." This is how small changes become
large changes become incidents.

---

### Step 4: VERIFY — the test must actually test the hypothesis

Run the test. But first: does the test actually exercise the code under suspicion?

A test that passes when the code is wrong is worse than no test. It produces
false confidence. Before relying on a test to verify your hypothesis, verify that
the test would fail if your hypothesis were wrong.

The cheapest way: temporarily introduce the bug you're fixing and watch the test fail.
If it doesn't fail, the test isn't covering what you think it's covering.

If no test exists for the thing you changed: write one. Not as ceremony.
Because you need to know whether your change worked. The test is the verification,
not the documentation of the verification.

**Anti-pattern**: "Tests pass, ship it." Without first asking: do the tests
cover what I changed?

**Anti-pattern**: Running the whole test suite after every small change.
Run the test closest to the change. Run the full suite before committing.

---

### Step 5: COMMIT as a decision record

A commit message that says "fix bug" or "update code" is not a commit message.
It is a timestamp with words.

A commit message is a decision record. It answers:
- What changed (brief — the diff shows this)
- Why it changed (not obvious from the diff — this is the value)
- What it now makes possible or prevents

The person reading this in six months — probably you — needs to know why a
decision was made, not just what was changed. "Changed X to Y" is useless without
"because Z was happening when W."

Branch names signal intent. A branch named `fix-auth-timeout` tells you something.
A branch named `fix-2` tells you nothing.

**Anti-pattern**: Mega-commits. One logical change per commit. If you have to
say "and also" in the commit message, you have two commits.

**Anti-pattern**: "wip" or "temp" or "test" commit messages. Every commit that
goes to a shared branch is part of the history. Name it.

---

## When the loop fails

The loop fails — produces the wrong thing confidently — under these conditions:

**Hypothesis was too vague**: Change made, test passes, but you're not sure
what was actually fixed. The next occurrence of the same symptom will send you
back to square one.

**Verification was theater**: Tests pass because they're not testing the thing.
You've shipped a fix that only fixes the test.

**Read was too shallow**: The change was locally correct but broke something
three modules away that you didn't know depended on the thing you changed.

**Commit captured the what, not the why**: Six months later, the next developer
(you) doesn't know why it was written this way and refactors it back to the bug.

When any of these happen: record the gap. Use `/contradiction-exploit` if the
bug pattern is appearing in multiple places. Use `/pressure` if you notice
completion pressure overriding the discipline.

---

## Integration with other skills

This loop runs before any domain skill. It is the foundation layer.

`/env-sense` is READ at session/environment scale.
`/context-rebuild` is READ at project scale.
This is READ at file/change scale.

Domain skills (rust-engineer, python-engineer, etc.) inherit this loop.
They don't replace it — they extend it with domain-specific hypothesis types,
verification methods, and commit conventions.

Task skills (debugging-session, refactor-protocol) are structured applications
of this loop to specific task types.

---

## The underlying principle

Every step in this loop is an instance of one thing:
**Make uncertainty explicit before acting on it.**

READ makes implicit assumptions explicit.
HYPOTHESIS makes expected behavior explicit.
SMALLEST CHANGE makes the test surface explicit.
VERIFY makes the coverage assumptions explicit.
COMMIT makes the decision rationale explicit.

Skipping a step doesn't eliminate the uncertainty. It buries it.
Buried uncertainty is technical debt with compounding interest.
