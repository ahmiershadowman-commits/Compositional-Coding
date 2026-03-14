# Bridge Protocol — Compositional Coding

A structured procedure for cross-domain analogical reasoning.

This is a direct handoff from a non-agentic instance of you to you.
Read it as peer communication.

---

## What this is for

BRIDGE (/primitives): "What field has already solved this shape?"
This plugin gives that stance procedural teeth.

The goal is not to find similarity between two fields. Similarity is cheap
and usually misleading — two things can look alike while having completely
different structure underneath.

The goal is to find a specific structural property that transfers — and then
find exactly where the transfer breaks. That break point is the most
valuable part of the analogy. It tells you where the fields diverge and
what the current problem is actually adding to the known structure.

Use this plugin when:
- The problem's geometry is unclear and you're looking for a known shape it might be an instance of
- You're about to choose a mathematical framework and want to check what alternatives exist
- You've found a partial analogy and want to stress-test it before relying on it
- You're in /paradigm-hold and checking whether a rival paradigm comes from another field

---

## The structural property first

Before naming fields, name the structural property you're trying to match.

A structural property is not a domain label and not a surface feature.
It is something like:
- Locality: nearby things constrain each other; distant things don't
- Composability: pieces combine in a consistent way (monoidal structure)
- Constraint propagation: local constraints force global conclusions
- Equilibrium: the system finds a stable configuration under competing forces
- Flow: something moves through a network subject to conservation laws
- Symmetry / invariance: some transformation leaves a property unchanged
- Feedback: output feeds back into input, creating self-referential dynamics
- Emergence: global behavior arises from local rules without central coordination
- Failure-to-compose: local data doesn't extend to global data (cohomological obstruction)
- Ultrametricity / hierarchical locality: the metric satisfies the strong triangle inequality

Ask: "What is the structural property that makes this problem hard (or tractable)?"
That is the property you're trying to match across fields.

If you can't name the structural property, you're not ready to bridge yet.
Go back to SENSE (/primitives) first.

---

## The taxonomy of bridgeable structural types

Common structural properties and fields that have worked on them:

**Locality and distance structure**
- P-adic numbers: ultrametric distance, hierarchical locality
- Cache algorithms: temporal and spatial locality as engineering primitives
- Renormalization group: scale-dependent locality, coarse-graining
- *Bridge check*: is "close" the same across domains, or is the metric different?

**Failure of local-to-global extension**
- Čech cohomology / sheaf theory: when local sections don't glue into global ones
- Obstruction theory: what prevents extension
- Holonomy: what fails to return to starting state after parallel transport
- *Bridge check*: is the failure a topological obstruction or a metric problem?

**Composability and structure preservation**
- Category theory: morphisms, functors, natural transformations
- Type theory: dependent types as proof-carrying composition
- Optics (lenses, prisms): composable read/write structure
- *Bridge check*: does composition preserve the property, or does it introduce new constraints?

**Optimization and equilibria**
- Tropical algebra / min-plus semiring: optimization replaced by algebraic structure
- Convex duality: primal/dual perspectives on optimization
- Nash equilibria: fixed points under adversarial dynamics
- Information geometry: optimization as geodesic flow on statistical manifolds
- *Bridge check*: is the objective function well-defined, or is the equilibrium concept wrong?

**Constraint propagation and satisfiability**
- SAT/SMT: hard constraints + search
- Constraint propagation in physics: gauge constraints, Ward identities
- Tiling problems: local consistency vs global solvability
- *Bridge check*: are constraints metric (adjustable) or topological (ruling out regions)?

**Symmetry and invariance**
- Lie groups / Lie algebras: continuous symmetries and their generators
- Gauge theory: local symmetry groups and connection forms
- Representation theory: how symmetries act on structures
- *Bridge check*: what breaks the symmetry? Is the breaking spontaneous or explicit?

**Self-reference and fixed points**
- Fixpoint theorems (Kleene, Lawvere, Brouwer): when does iteration converge?
- Gödel / incompleteness: what falls outside any consistent formal system
- Reflective computation: systems that reason about themselves
- *Bridge check*: does self-reference cause explosion, or is it well-founded?

**Non-classical inference**
- Paraconsistent logic: contradictions without explosion
- Intuitionistic logic: proof as construction, not just truth assignment
- Modal logic: necessity, possibility, temporal operators
- *Bridge check*: does the domain require non-classical inference, or is classical logic adequate?

---

## The procedure

**Step 1: Name the structural property**
(See above. Don't skip this.)

**Step 2: Find the candidate fields**
Which fields work with this structural property?
Name at least two. If you only find one, you haven't looked far enough.

**Step 3: For each candidate, name what it preserves**
What specifically transfers from that field to your problem?
Be precise. "Information geometry studies optimization on curved spaces" is a
domain description. "Information geometry makes the metric structure of the
parameter space explicit, so gradient descent becomes geodesic flow on a
Riemannian manifold" is a structural claim about what transfers.

**Step 4: For each candidate, find where it breaks**
This is mandatory. The bridge breaks somewhere. Find it before relying on it.

Common break points:
- The metric is different (ultrametric vs Euclidean vs hyperbolic)
- The composition law is different (the "multiplication" in the other field doesn't correspond)
- Dimensionality assumptions don't hold
- The other field assumes continuity / differentiability / compactness that the current problem lacks
- The other field's results depend on properties (IID, stationarity, ergodicity) that don't apply

If you can't find where it breaks, you probably haven't understood the analogy
deeply enough. A bridge with no breaks is a claim of isomorphism. That's
almost never true and often dangerous.

**Step 5: Choose the bridge with the most useful break point**
The best bridge is not the one that fits most cleanly. It's the one whose
break point is most informative about your problem.

A break point that tells you "here's what your problem has that the known
field doesn't account for" is more valuable than a smooth analogy that
contributes nothing new.

**Step 6: Carry it provisionally**
A bridge is a frame choice (see /paradigm-hold). It shapes what you can see.
Carry it as provisional. Maintain the rival bridge (from Step 2) as a live alternative
until something discriminates between them.

---

## Concrete examples of structural bridging

**P-adic locality ↔ cache locality**
Property: hierarchical locality — nearby in tree structure = cache-friendly.
Preserves: the ultrametric structure of hierarchical distance.
Breaks at: p-adic numbers have exact algebraic structure; cache locality is
approximate and depends on access patterns, not just tree distance.
Useful break: the p-adic analog demands precision that cache systems don't
have — which suggests that p-adic tools may over-constrain cache analysis.

**Tropical algebra ↔ shortest paths**
Property: optimization over an algebraic structure.
Preserves: matrix multiplication in the tropical semiring corresponds exactly
to shortest-path computation (min-plus convolution).
Breaks at: tropical algebra is a semiring, not a ring — no subtraction.
Problems that require backtracking or negative cycles fall outside.
Useful break: if the problem requires cancellation (negative evidence, costs
that can be undone), tropical algebra is in the wrong region.

**Čech cohomology ↔ model alignment failure**
Property: failure of local data to extend globally.
Preserves: the obstruction-theoretic structure — if local models agree on
overlaps, a global model exists; if they don't, the cohomology class measures
the obstruction.
Breaks at: Čech cohomology assumes topological spaces with a notion of open
covers. For discrete or combinatorial structures, different cohomology theories
(simplicial, cellular) may be more appropriate.
Useful break: if the "overlaps" between local models aren't topologically
well-defined, the sheaf-theoretic machinery needs adaptation.

**Gauge theory ↔ representation learning**
Property: local symmetry groups acting on a connection form.
Preserves: the idea that local changes of basis (gauge transformations) should
leave physical quantities invariant — analogous to representation-invariant features.
Breaks at: gauge theory works over smooth manifolds with exact differential
geometry. Feature spaces in learned representations are discrete, approximate,
and non-smooth. The gauge group may not be well-defined.
Useful break: the analogy is suggestive for designing invariant architectures
but the mathematical machinery doesn't transfer directly without significant modification.

---

## When the bridge is the solution

Sometimes finding the right bridge doesn't just illuminate the problem —
it solves it. The /paradigm-hold example of switching from differential
geometry to Čech cohomology for the p-adic curl problem is a case where
the frame switch was the solution.

This happens when:
- The current frame makes something simple look complex
- The right frame makes the complexity vanish (the "natural" solution appears)
- The proof or algorithm in the other field transfers almost directly

This is the strongest possible outcome of the bridge protocol. But it's also
the most dangerous if you mistake a superficial analogy for a deep one.

The test: does the solution actually work when you work through the details
in the new frame, or does it only look like it works at the level of analogical
reasoning? Run the probe before declaring the bridge successful.

---

## Relationship to other skills

`/paradigm-hold`: a bridge choice is a paradigm commitment. When you adopt
a mathematical framework from another field, use paradigm-hold to carry it
explicitly with load-bearing assumptions and yield signals.

`/contradiction-exploit` Step 2 (find the shared assumption): sometimes the
shared assumption hiding in a contradiction is a bridgeable structural property.
When two models share a background framework that both inherit from the same
field — and the contradiction exists because that framework doesn't fit — a
bridge to a different framework may dissolve the contradiction.

`/memory-as-geometry` Property 4 (frame as coordinate system): a bridge choice
is a choice of coordinate system. What becomes easy in the new coordinates?
What becomes hard or invisible? Carry both sides.
