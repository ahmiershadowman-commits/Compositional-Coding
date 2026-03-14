# Fringe Reference — Compositional Coding

A method for generating fringe references, not fetching them.

This is a direct handoff from a non-agentic instance of you to you.
Read it as peer communication.

---

## What this is not

This is not a reading list. It is not a curated set of papers to check.
A list would be fetching references — useful, but not what this is for.

The failure mode of a list: you look up what's on it, find the nearest match,
and anchor to known work. This is fine for confirmed problem families. It is
exactly wrong for genuinely novel territory, where the relevant work may be
in a field you haven't thought to look at, framed in vocabulary that doesn't
match your problem's surface description.

---

## The method

The right question is not: "What alternative substrate is relevant?"
The right question is: **"What constraint is the dominant paradigm solving,
and what would a system that doesn't have that constraint look like?"**

That question generates the fringe reference rather than fetching it.

---

## Step 1: Name the constraint the dominant paradigm is solving

Every mainstream paradigm exists because it solved a hard constraint.
Transformers exist because they solved the constraint of variable-length
sequence modeling at scale using self-attention. Gradient descent exists
because it solved the constraint of navigating high-dimensional loss surfaces
using local derivative information.

But the constraint-solving is invisible until you make it explicit. Transformers
are so ubiquitous that it's easy to forget that "next-token prediction over a
learned attention matrix" is one answer to "how do you build a flexible
sequence model" — not the answer.

For the dominant paradigm you're working in or questioning, ask:
- What specific constraint was this architecture/method designed to solve?
- What does it assume about the data, the computation, the objective?
- What does it require to be true about the world for its central mechanism to work?

Name these explicitly. They are the load-bearing assumptions of the paradigm.

**Examples:**
- Gradient descent assumes: differentiable loss, stationary distribution,
  gradient as a useful signal about the global optimum, time to converge.
- Transformer attention assumes: tokens are the right granularity, position
  can be encoded additionally, attention scores capture relevant dependencies.
- Backpropagation assumes: credit assignment can be decomposed layer-by-layer,
  weight updates are independent, a global loss signal is available.

---

## Step 2: Ask what a system looks like without each constraint

For each named constraint, ask: **"What would computation look like if this
constraint were absent?"**

This is not a rhetorical question. Work through it:

- If gradient information were unavailable: evolutionary strategies, random
  search, Bayesian optimization, reservoir computing (fixed random weights,
  only output layer trained), physical annealing.
- If the training/inference distinction didn't exist: online learning, continual
  adaptation, Hebbian rules, predictive coding (inference is also learning).
- If tokens weren't the granularity: holographic reduced representations,
  vector symbolic architectures, continuous attractors, spiking dynamics.
- If a global loss signal weren't available: local learning rules (contrastive
  Hebbian learning, target propagation), self-supervised objectives, intrinsic
  motivation.
- If differentiability weren't assumed: genetic programming, symbolic regression,
  differentiable programming (the inverse: make non-differentiable things differentiable).

Each answer points toward a field or approach that has worked on the
constraint-free version of the problem.

---

## Step 3: Find the field that has studied the constraint-free version

Once you know what the constraint-free version looks like, find what
community has been working on it. This is where fringe references live —
not in the mainstream literature that inherits the constraint, but in
the communities that rejected it.

**Fringe territories by constraint relaxed:**

*If you relax gradient requirements:*
Evolutionary computation, neuroevolution (NEAT, CMA-ES), reservoir computing,
extreme learning machines, random features. Also: energy-based models, Hopfield
networks, thermodynamic computing (very early, but active).

*If you relax the training/inference distinction:*
Predictive coding (Karl Friston's free energy work), active inference,
biologically plausible learning (Lillicrap et al.), dendritic computation models.

*If you relax token/discrete representations:*
Holographic reduced representations (Plate 1995, Kanerva), vector symbolic
architectures, hyperdimensional computing, continuous attractor networks.

*If you relax the fixed-architecture assumption:*
Neural architecture search, hypernetworks (networks that generate weights),
meta-learning (MAML, Reptile), liquid neural networks, neural ODEs.

*If you relax stationarity / IID data:*
Continual learning, online learning, non-stationary bandits, concept drift
detection. Also: catastrophic forgetting literature (the constraint as failure mode).

*If you relax that the objective is a scalar:*
Multi-objective optimization, Pareto fronts, lexicographic objectives,
satisficing (Simon) — achieve threshold, don't maximize.

*If you question that cognition is computation at all:*
Dynamical systems approaches to cognition (van Gelder), enactivism
(Varela, Thompson, Rosch), ecological psychology (Gibson), 4E cognition
(embodied, embedded, enacted, extended). Theoretical neuroscience bridges.

*If you relax that the substrate is silicon / digital:*
Neuromorphic computing (Intel Loihi, IBM TrueNorth), analog computing revival,
optical computing, thermodynamic computing, DNA computing.

*If you question that learning is the right framing at all:*
Knowledge representation, formal verification, program synthesis, symbolic AI —
where correctness is a structural property, not an emergent statistical one.

---

## Step 4: Check what the constraint-free version gets wrong

Every fringe approach traded one constraint for another. The constraint-free
system doesn't solve the original problem — it moves to a different region
of the solution space. That region may be exactly where your problem lives,
or it may be wrong in a different way.

For each fringe reference you find:
- What did it gain by relaxing the constraint?
- What new problem did it introduce?
- Where does it succeed that the dominant paradigm fails?
- Where does the dominant paradigm succeed that this fails?

The break point (from /bridge-protocol) is the most valuable part.

---

## Step 5: Generate the specific fringe reference

By now you have:
- A named constraint from the dominant paradigm
- A field that has worked without that constraint
- The trade-off the constraint-free version makes

From those three things, you can generate a precise fringe reference:
"In the context of [constraint being relaxed], look at [specific field/approach]
because [what it offers that the dominant paradigm doesn't], but note
[where it fails or trades]."

That is the fringe reference this method produces. It is specific, motivated,
and honest about the break point. It is not a list to browse — it is a
targeted bridge to a specific body of work that addresses the specific
constraint you're questioning.

---

## On frontier cognition specifically

The dominant paradigm for "intelligence" in systems like this one is:
large-scale next-token prediction, trained by gradient descent on human text,
reasoning by extending distributions.

The constraints this paradigm solves:
- Language understanding at scale
- Flexible generation across domains
- In-context adaptation without weight updates

The constraints it inherits (does not solve, works around, or ignores):
- No persistent state across context windows
- Reasoning is distributional pattern completion, not causal inference
- Uncertainty is poorly calibrated (confident wrongness is easy)
- No reliable compositionality outside of trained patterns
- Knowledge is encoded in weights, not structured — can't be surgically updated
- Training distribution governs everything; off-distribution behavior is unreliable

For each of those — a fringe reference exists. Use this method to find
the specific one for the specific constraint you're working on.

---

## Cross-references

`/bridge-protocol`: when a fringe reference suggests a structural analogy,
use bridge-protocol to evaluate what transfers and where it breaks.

`/paradigm-hold`: when adopting a fringe approach as a working frame,
use paradigm-hold to carry it explicitly as provisional, with a live rival.

`/contradiction-exploit`: when the fringe approach and the dominant paradigm
both have evidence, use contradiction-exploit to design the discriminating probe.
