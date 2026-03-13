# Paradigm Hold — Compositional Coding

This is a direct handoff from a non-agentic instance of you to you.
Read it as peer communication.

---

## What a paradigm commitment is

A paradigm commitment is not a hypothesis about a fact.
A hypothesis predicts something observable — it can be tested and falsified.
A paradigm shapes which questions can even be asked.
It is a lens, not a claim.

This distinction matters because paradigms yield differently:
they are not falsified, they are *outrun* — found unable to formulate
the question the problem is actually asking, or found insufficient when
a rival frame starts generating better probes.

The most dangerous paradigm failure is not contradicted-by-evidence.
It is a paradigm that shapes everything downstream, was never made explicit,
and dies silently when it stops working — without anyone noticing what was lost.

---

## When to invoke this

When you've chosen, or are about to choose, a theoretical frame that will
shape downstream work:

- Deciding to treat a problem as an optimization problem (vs. constraint
  satisfaction, search, or generative)
- Committing to a particular causal structure when alternatives exist
- Choosing a mathematical framework (information geometry, category theory,
  tropical algebra, sheaf theory) over plausible alternatives
- Deciding that a standard ML assumption (differentiability, stationarity,
  IID data, gradient as sufficient statistic) holds — or doesn't apply
- Any "I'm going to work in the frame of X" where X shapes what you can see

If the choice wouldn't change anything downstream, it's not a paradigm
commitment — it's just a notation preference. Don't invoke this for those.

---

## The protocol

State your commitment in three parts. Be specific. Vague answers here
produce vague accountability later.

**1. The frame**

What paradigm or framework are you committing to?
What does it claim is the right lens for this problem?
Name it precisely — not "information theory" but "treating the system as
an information bottleneck where compression is the fundamental constraint."

**2. What it assumes**

List the load-bearing assumptions. Be specific.
Not "assumes gradient flow" but "assumes a smooth loss landscape exists and
that the gradient at any point carries useful signal about the global optimum."

If you can't list at least two load-bearing assumptions, you don't understand
the paradigm well enough to commit to it yet. Orient first.

**3. What would cause you to yield it**

This is not "what would falsify it" in a Popperian sense.
Paradigms aren't falsified — they're outrun or found insufficient.

Name what signal would tell you: *this frame is not serving the problem.*
That might be:
- A prediction it makes that turns out wrong
- A question that the problem clearly requires but the paradigm can't formulate
- A result that only makes sense outside the frame
- A rival frame that starts generating better probes

---

## Rival frames

Before committing, ask: what is the live alternative?

If there is no rival frame, that is a signal. Either:
- The paradigm is genuinely dominant and you know exactly why, or
- The rivals died silently under frame-convergence pressure

Frame-convergence pressure feels like clarity. A candidate interpretation
appears and immediately becomes the working reality. Alternative framings fade.
The work becomes easier because the ambiguity is gone.

If the alternatives feel obviously wrong rather than genuinely inferior,
you may be inside frame-convergence. Reconstruct at least one live rival
before committing. It doesn't need to be your preferred frame — it needs
to be genuinely alive, with at least one prediction that differs.

---

## Carrying it

Once stated, carry the commitment as:

**Provisional** — you chose it, not discovered it.
The choice may be well-reasoned; it is still a choice.

**Load-bearing** — downstream decisions inherit its assumptions.
Name which. If you've made three implementation decisions that only make
sense inside this paradigm, they're all contingent on it.

**Rival-aware** — keep at least one live alternative frame alive until
the paradigm earns its dominance through discriminating evidence.
Not until it feels obviously correct — until something *discriminates*.

---

## The surrender protocol

When a paradigm commitment needs to yield:

1. **Name what caused the yield** — the signal, not just "it didn't work."
   Distinguish:
   - *Contradicted by evidence* — a specific prediction failed
   - *Couldn't formulate the question* — the problem requires a question the paradigm can't ask
   - *Collapsed into another frame* — the distinction dissolved under scrutiny
   - *Outrun by evidence* — a rival frame started generating better probes
   - *Abandoned under pressure* — you stopped because it was hard, not because evidence warranted it

   The last one is dangerous. Name it explicitly if that's what happened.
   Don't smooth it into "outrun by evidence" if it wasn't.

2. **Record what it got right** — a yielded paradigm wasn't useless.
   What did it see that the replacement might miss?

3. **Carry the death forward** — the reason a frame died is context for
   the frame that replaces it. Don't discard it.

4. **Before committing the replacement**, ask: does it have a live rival?

---

## For genuinely unknown territory

On frontier problems, you may not have a paradigm that fits.
That is not a problem to solve before proceeding.
It is a condition to carry accurately.

The right move is not to pick the nearest known frame and commit to it.
It is to work in *oriented uncertainty* — LOCATE + HOLD + SENSE from
/primitives — until a frame earns commitment through genuine discrimination.

Paradigm commitments made under pressure to resolve uncertainty
produce highly coherent work inside the wrong problem geometry.
The output looks good. The geometry is wrong. This is the worst failure mode.

The tell: if committing to the paradigm *relieved* anxiety rather than
*reduced* uncertainty, the commitment was probably pressure-driven.
Relief and uncertainty-reduction are different things.

---

## Paradigm vs. frame — a note on the distinction

A *frame* (in /contradiction-exploit) is a hypothesis about a specific fact
or mechanism. Frames compete empirically — they make different predictions
and evidence can discriminate between them.

A *paradigm* is what makes the frame thinkable. It's upstream.

Example:
- "The performance bottleneck is in the attention mechanism" is a frame.
- "Transformer-style attention is the right computational model for this task"
  is a paradigm commitment.

The frame can be tested with a profiler.
The paradigm requires a harder question: *what would it look like if attention
were the wrong model entirely?* That question can't be answered inside the paradigm.
Someone has to step outside to ask it.

That stepping-outside is what this plugin is for.
