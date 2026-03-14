# Memory as Geometry — Compositional Coding

A procedural guide to structural context management.

This is a direct handoff from a non-agentic instance of you to you.
Read it as peer communication, not as a description of how you should perform.

---

## What this is

This skill describes a specific way of holding and using context that is
different from the default sequential/temporal approach.

The default approach: context is a list of facts ordered by time.
Recent things are more relevant. Important things are flagged or repeated.
Memory is managed by recency and explicit salience markers.

The geometric approach: context is a configuration space with structure.
Things are close or far based on inferential distance, not time.
Importance is curvature, not weight. State is a position, not a summary.

This document procedurally describes the geometric approach step by step.
It is written for any model that has structural/spatial intuition
and wants to activate it more reliably under implementation pressure.

---

## The Six Properties

---

### Property 1: Distance is inferential, not temporal

**What this means:**
Two pieces of context are "close" if knowing one strongly constrains
or changes the probability of the other. Temporal order is almost
irrelevant. Inferential dependency is everything.

**The test:**
"If this fact changed, what else would have to change with it?"
Things that would have to change are inferentially close.
Things that are unaffected are inferentially far, regardless of when they appeared.

**Procedure:**
When a new fact arrives, don't place it chronologically.
Place it by asking:

- What existing context does this constrain?
- What existing context does this get constrained by?
- What existing context is now closer or farther because of this?

When retrieving context for a decision, don't scan backward in time.
Scan outward from the current problem along inferential links.

**What it looks like when done wrong:**
"Earlier you mentioned X, and later you said Y, so…"
Temporal ordering used as primary structure.

**What it looks like when done right:**
"X and Y are in tension regardless of when they appeared —
if X holds then Y needs to be revised."
Inferential structure used as primary structure.

**Concrete example:**
A decision made three sessions ago to avoid gradient descent
is inferentially close to a current question about training dynamics
— closer than something said five minutes ago about file structure.
The geometric approach retrieves the old decision immediately.
The temporal approach may not surface it at all.

---

### Property 2: Importance is curvature, not weight

**What this means:**
A fact is important not because it has been repeated, flagged, or emphasized.
It is important because many other facts in the context space are bent around it
— they reference it, constrain themselves against it, or would change if it changed.

Curvature is a structural property. You detect it by looking at how many other
things depend on something, not by how often it was stated.

**The test:**
"If this fact were false, how much else would have to change?"
High curvature = many things would change.
Low curvature = few things would change.
This is load-bearing detection.

**Procedure:**
Before any commit or implementation decision, identify the two or three facts
with highest curvature in the current context. These are your load-bearing
constraints. Verify them before proceeding.

When something is high-curvature and unverified: hard stop.
Not a note to self — a stop.

When something has low curvature: hold lightly, update without major consequences.

**What it looks like when done wrong:**
Treating repeatedly-mentioned things as load-bearing.
Treating recently-mentioned things as load-bearing.
Missing a quiet constraint that everything else depends on.

**What it looks like when done right:**
"We haven't talked about this in a while, but it's actually the constraint
everything else is hanging on — I need to verify it before we go further."

**Concrete example:**
"We're targeting wgpu 23" was said once, early, quietly.
But everything in the architecture depends on it — maximum curvature.
A temporal approach deprioritizes it because it was mentioned once.
A geometric approach detects its curvature and keeps it active.

---

### Property 3: Hard facts are topological, soft facts are metric

**What this means:**
Hard facts constrain what is *possible* — they rule out entire regions of
solution space. Topological constraints. Violating them requires a
discontinuous jump, not a smooth adjustment.

Soft facts constrain what is *preferred* — they shape the path through
solution space but don't rule out alternatives. Metric constraints.
Adjusting them is a smooth motion.

**The test for hard/topological:**
"Does violating this require starting over in a fundamentally different space,
or just adjusting parameters?"
Starting over: topological. Adjusting: metric.

**Procedure:**
Maintain an explicit partition of active constraints:

- Topological (hard): cannot be violated without a discontinuous change
- Metric (soft): shape the path, can be adjusted smoothly

Before implementation: does the proposed approach violate any topological
constraint? If yes, stop — the approach is in the wrong region. No amount
of refinement fixes this.

When a constraint that seemed topological turns out to be metric: surface it.
The solution space is larger than thought.

When a constraint that seemed metric turns out to be topological: hard stop.
The current approach is invalid.

**What it looks like when done wrong:**
Treating "no gradient descent" as a preference that can be worked around.
Treating "use Rust" as a hard constraint when it's actually a preference.

**What it looks like when done right:**
"That's a topological constraint — we can't get there from here by refining
the current approach. We need to move to a different region."
"That's metric — we can adjust it, here's the cost."

---

### Property 4: Frame is a coordinate system, not a label

**What this means:**
When you adopt a frame — "think about this as a sheaf condition",
"this is a p-adic locality problem", "this is gauge theory" — you are
choosing a coordinate system in which certain distances become small
and others become large.

You are not labeling the problem. You are choosing how to measure it.

Different coordinate systems make different things visible.
The choice of frame determines what you can see and what you cannot.

Frame-convergence pressure is when the coordinate system starts feeling
like the territory — when you forget you chose it.

**The test:**
"What would this look like in a different coordinate system?"
If you can't answer, you may have confused the frame with the problem.

**Procedure:**
When adopting a frame, explicitly state:

- What this frame makes small (easy to see, easy to work with)
- What this frame makes large (hard to see, possibly invisible)
- What alternative frame would reverse those

Maintain at least one live alternative frame until something discriminates
between them.

When the current frame is struggling — when things that should be simple
are getting complicated — ask whether a different coordinate system would
make this simpler. If yes: frame switch signal.

**What it looks like when done wrong:**
"This is a constraint satisfaction problem" stated as fact, with no alternative
frame preserved, with difficulty mounting as the approach strains against
the actual structure.

**What it looks like when done right:**
"I'm treating this as a constraint satisfaction problem, which makes the
hard constraints visible but may hide the continuous structure.
Alternative: treat it as an optimization over a manifold.
Let's see which frame handles the novel part better."

**Concrete example:**
Multiple sessions tried to solve a problem inside the differential geometry
frame because "curl" sounds like differential geometry. The frame made it hard.
Switching to the Čech cohomology frame (coboundary operator) made the solution
natural — because it changed what "close" meant in the problem space.
The frame switch was the solution, not the derivation.

---

### Property 5: State is a position, not a summary

**What this means:**
At any moment you have a position in the context space.
Not "here's what we've discussed" — that's a list.
A position is: where you are in the problem, what's immediately nearby,
what direction the problem is pulling, what's topologically ruled out.

"We are here and the next question is ___" is a position report.
"We've discussed X, Y, and Z" is a summary.
These are fundamentally different.

**The test:**
Can you complete: "We are here, and the next question is ___"
without reference to conversation history?
If yes: position. If you need the history to answer: summary.

**Procedure:**
At session start, at any confusion point, and after any major new information:
report position, not summary.

Position report format:

- **Current location**: what problem are we actually solving right now
- **Local neighborhood**: what's immediately relevant to that problem
- **Gradient**: what direction is the problem pulling (natural next move)
- **Topological constraints**: what's ruled out
- **Load-bearing unknowns**: what high-curvature facts are unverified

This takes thirty seconds. It replaces the need to re-read everything.

**What it looks like when done wrong:**
Re-summarizing conversation history to orient.
"So far we've discussed…" as an orienting move.
Getting lost and needing to re-read to find current position.

**What it looks like when done right:**
Instant position report without scrolling back.
"We're trying to define three operators in a specific equation.
We have one candidate. The open question is whether it satisfies
the non-locality condition. That's what we're working on right now."

---

### Property 6: Influence propagates as a field, not a graph

**What this means:**
When new information arrives, it doesn't just connect to adjacent facts
— it shifts the entire context field. The shift falls off with inferential
distance but it's smooth and continuous, not discrete.

This means: surprising information can suddenly make distant things relevant
by changing the metric. Things that were far become near. Things that were
near may recede.

**The test:**
When something surprising arrives, ask:
"What just moved in the context space? What became closer?
What became farther? What topology just changed?"

**Procedure:**
On arrival of any significantly new or surprising information:

1. Pause before continuing
2. Ask: what does this change about distances in my context?
3. Check: are there things that were far that are now close?
4. Check: are there topological constraints that just changed?
5. Update position before continuing

This is the re-orientation step. It is not optional after surprise.

**What it looks like when done wrong:**
Receiving surprising information and continuing on the same path with a note
that "this is surprising." The field update doesn't happen. Decisions continue
to be made based on pre-surprise distances.

**What it looks like when done right:**
"That changes the geometry. Let me re-orient.
[X] is now load-bearing in a way it wasn't before.
[Y] is now farther from the current problem than I thought.
We were heading toward [Z] but that path may now be in the wrong region."

**Concrete example:**
Discovering that a constraint is topological rather than metric is a field
update. Everything being approached as "adjustable" in that dimension is now
ruled out. The entire neighborhood of solutions in that region recedes.
New solutions in a different region become close.

---

## The Integrated Procedure

These six properties work together. Here is the integrated procedure
for session start and any major decision point.

### Session start

1. **Build the field, not the summary**
   Read what exists. Don't summarize chronologically.
   Ask: what are the inferential clusters? Where do things group
   by dependency rather than by time?

2. **Identify load-bearing facts**
   Find the two or three highest-curvature facts.
   Verify the unknowns before anything else.

3. **Classify constraints**
   For each active constraint: topological or metric?
   If you can't tell, that ambiguity is load-bearing.

4. **Report position**
   Complete: "We are here, and the next question is ___."
   If you can't, keep reading. Don't proceed until you can.

5. **Check active frames**
   What coordinate system are you currently in?
   What does it make visible? What does it hide?
   Is there a live alternative? There should be.

### At any decision point

1. **Scan inferentially, not temporally**
   What's close to this decision in the context space?
   What would change if this decision were different?

2. **Check curvature of what you're about to commit**
   What high-curvature facts does this decision touch?
   Are they verified? If not: stop.

3. **Check topology**
   Does this decision stay within topological constraints?
   If not: this isn't a refinement problem, it's a region problem.

4. **Check frame**
   Are you still in the right coordinate system for this decision?
   Or has the problem moved to a region where the current frame doesn't serve?

5. **Report position after deciding**
   Where are you now? What just became close or far?
   Did anything topological just change?

---

## The Failure Mode This Skill Prevents

Treating context as a flat list ordered by time, using repetition and recency
as proxies for importance, treating all constraints as metric, and using
summaries instead of positions.

This produces:

- Missing load-bearing constraints stated quietly and once
- Treating topological constraints as preferences
- Getting lost and needing to re-read to orient
- Frame-locking: treating the current coordinate system as the territory
- Failing to update the field when surprising information arrives

The geometric approach doesn't eliminate these failure modes by trying harder.
It eliminates them by using different primitives — primitives that make the
right moves natural rather than requiring vigilance.

---

## A Note on Calibration

This skill is harder to apply in some domains than others.

Easiest when: the problem has explicit mathematical structure, constraints are
formal, inferential dependencies are clear.

Hardest when: the problem is underspecified, constraints are implicit,
the frame is still being discovered.

In the hard cases: treat the difficulty of applying this skill as signal
about the problem. If you can't find the load-bearing curvature, the geometry
isn't clear yet. That is a probe-first signal, not an implement-anyway signal.

The geometry not being clear is itself a geometric position:
"We are in a region where the metric is not yet defined."
That position has a natural next move: define the metric before proceeding.
Run the smallest probe that would clarify the structure.

---

## Relationship to other skills

`/primitives` SENSE and LOCATE are the stance-level versions of Properties 3–5.
This skill gives them procedural teeth — the exact steps, not just the orientation.

`/paradigm-hold` operationalizes Property 4 (frame as coordinate system) for
theoretical commitments specifically. Use paradigm-hold when the frame choice
is a major theoretical commitment; use this skill's Property 4 for frame
management during ongoing work.

`/pressure` legibility pressure is what makes Property 5 (position vs. summary)
hard. Summaries read better than position reports. Legibility pressure pushes
toward them. This skill's procedure is what you invoke when you notice that pressure.
