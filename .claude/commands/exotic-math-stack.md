# Exotic Math Stack — Compositional Coding

Mathematical structures for frontier reasoning. Each structure is a cognitive tool,
not just a reference. The goal is knowing when a structure applies and what it
buys you — not recalling theorems.

This is a direct handoff from a non-agentic instance of you to you.
Read it as peer communication.

---

## How to use this

Each structure below includes:
- What problem it was built to solve
- The cognitive move it enables
- Where it applies (and where it breaks)
- A concrete example from frontier work

These are not definitions to look up. They are frames to reach for when
the standard approaches are straining. The signal to reach for one of these:
the standard frame is making something that should be simple look complex.

---

## P-adic Numbers

**Built to solve**: Measuring "closeness" in a hierarchy rather than on a line.
In the standard real-number metric, closeness is proximity on the number line.
P-adic numbers define closeness by how high up in a prime-base hierarchy two
numbers share structure.

**The cognitive move**: When the natural notion of distance in your problem is
hierarchical rather than linear — when "nearby" means "shares the same
high-level structure" rather than "has a small numerical difference" — p-adic
distance may be the right metric.

Two numbers are p-adically close if they agree on many digits in base p.
This makes the metric ultrametric: the strong triangle inequality holds.
Every point in a ball is its center. There are no "edges" to a p-adic ball.

**Where it applies**:
- Hierarchical clustering where cluster membership matters more than
  inter-cluster distance
- Cache locality (temporal/spatial locality as ultrametric structure)
- Any domain where you want to say "these two things are close because they
  share the same family" rather than "because they have a small numeric difference"
- Problems where the standard Euclidean metric is forcing a flat structure
  onto something that's actually hierarchical

**Where it breaks**:
- When you need subtraction or negative differences — p-adic numbers extend
  the integers, but "p-adic real analysis" is structurally different from
  standard analysis. Calculus tools that rely on the Archimedean property break.
- When the hierarchy doesn't have a natural prime base — forcing a base p
  onto a structure that doesn't respect it produces arbitrary results.

**Concrete example**:
If you're working on a problem involving locality in a tree-structured space
(branching hierarchies, parse trees, taxonomies), p-adic distance may
clarify relationships that Euclidean distance obscures. Two nodes are "close"
if their lowest common ancestor is high in the tree — exactly what p-adic
distance formalizes.

---

## Tropical Algebra (Min-Plus Semiring)

**Built to solve**: Optimization problems with additive costs, where the
natural operation is "choose the minimum" rather than "sum everything."

Tropical algebra replaces standard addition with minimum and standard
multiplication with addition. This is the (ℝ ∪ {∞}, min, +) semiring.
Matrix multiplication in this semiring: C[i,j] = min_k(A[i,k] + B[k,j]).
That is exactly shortest-path computation (Dijkstra, Floyd-Warshall).

**The cognitive move**: When your problem is secretly an optimization over
paths or sequences, tropical algebra may let you state it as a linear-algebraic
problem in the tropical semiring and import all the machinery for matrix
operations, eigenvalues (tropical eigenvalues = growth rates), etc.

**Where it applies**:
- Shortest paths in graphs (canonical)
- Scheduling problems with additive costs
- Dynamic programming where the recursion is "minimize over choices, add costs"
- Formal languages: tropical semirings show up in the theory of weighted automata
- Optimization problems where "multiply" means "compose/chain" and "add" means "choose best"

**Where it breaks**:
- No subtraction — tropical is a semiring, not a ring. Problems that require
  "undoing" an operation or computing differences fall outside.
- No negative cycles — tropical Floyd-Warshall assumes non-negative edge weights
  in the standard sense.
- When you need to distinguish between paths of the same length — tropical
  algebra only finds the minimum, not the structure of all minimum paths.

**Concrete example**:
If you're working on a problem where you're composing transformations with costs
(each transformation has a "difficulty" and you want the easiest composition path),
represent transformations as nodes and costs as edge weights. Tropical matrix
multiplication finds the minimum-cost path automatically.

---

## Sheaf Theory and Čech Cohomology

**Built to solve**: The local-to-global problem. When can local data, defined
on overlapping patches, be consistently assembled into global data?

A sheaf assigns data (sections) to open sets of a topological space, with
restriction maps that say how data on a large set restricts to a smaller set.
The sheaf axioms: if sections on overlapping sets agree on the overlap,
there exists a unique global section that restricts to each local one.

Čech cohomology measures the failure of this gluing. The first cohomology group
H¹ measures obstructions to gluing local sections into global ones.

**The cognitive move**: When you have local models, local measurements, or
local constraints that should be consistent but aren't assembling cleanly,
sheaf theory gives you a framework to name and measure the inconsistency.
The cohomology class is the obstruction — it tells you whether the failure
is solvable and what would be needed to solve it.

**Where it applies**:
- Sensor fusion: multiple local sensors, do their readings glue into a
  consistent global picture?
- Distributed computation: local computations on overlapping data, do they
  produce consistent global results?
- Feature alignment: local learned representations on overlapping domains,
  do they produce consistent global representations?
- Any problem where you have "patches" of a space and want to know if they
  can be assembled — the sheaf-theoretic language formalizes this.

**Where it breaks**:
- Sheaf theory assumes a topological space with a notion of open covers.
  Discrete structures need adaptation (simplicial sheaves, etc.).
- The machinery is heavy for small problems. The overhead of setting up the
  covering, sections, and restriction maps is not worth it unless the
  gluing problem is genuinely the load-bearing structure.
- Cohomology tells you about the existence of obstructions, not how to
  remove them. It is diagnostic, not constructive.

**Concrete example** (from project history):
The p-adic curl problem. When formulated in differential geometry (gradient,
curl, divergence over smooth manifolds), the problem was stuck. Reformulating
it as a Čech cohomology question (coboundary operator δ: C⁰ → C¹ → C²)
made the structure natural — because "curl" over a discrete space is exactly
the coboundary operator measuring failure to be a global section.

---

## Surreal Numbers

**Built to solve**: A single number system that contains real numbers,
ordinals, and infinitesimals — constructed recursively from the simplest
possible definition.

A surreal number is a pair {L | R} where L is a set of previously constructed
surreals to the left, R is a set to the right, and no element of L is ≥ any
element of R. 0 = {|}, 1 = {0|}, -1 = {|0}, ω = {0,1,2,...|}, ε = {0|1,1/2,1/4,...}.

Every real number, every ordinal, every infinitesimal is a surreal number.

**The cognitive move**: When you need to reason about infinity or infinitesimals
with algebraic structure — not just limits, but actual numbers you can add,
multiply, and compare — surreal numbers give you that. They also give you a
clean constructive foundation for comparing "sizes" of infinite things.

**Where it applies**:
- Ordinal arithmetic with algebraic operations (not just ordinal addition,
  which is non-commutative — surreal multiplication is commutative)
- Reasoning about infinitesimals in a non-standard analysis framework
- Game theory: surreal numbers arose from combinatorial game theory (Conway).
  Game values are surreal numbers. Combinatorial games compose as surreal addition.
- Any problem where you need to formally compare "sizes" of things that
  are "infinite" in the colloquial sense

**Where it breaks**:
- Surreal numbers include a proper class, not a set — standard set theory
  gets uncomfortable. Most implementations necessarily truncate the construction.
- Computation is expensive: surreal arithmetic requires tracking the full {L|R}
  structure. For practical computation, real numbers are almost always more appropriate.
- The connection to "real" (pun intended) computation is indirect. Surreal
  numbers are primarily a theoretical tool.

**Concrete example**:
If you're working on a problem involving the "complexity" or "rank" of strategies
in a game or search space, and the complexity has ordinal structure (some
strategies are "infinite steps ahead" of others), surreal numbers let you do
arithmetic on those complexity ranks in ways ordinal arithmetic alone doesn't support.

---

## Paraconsistent Logic

**Built to solve**: Reasoning with contradictory information without explosion.

In classical logic, a contradiction entails everything: P ∧ ¬P ⊢ Q for any Q.
This is the principle of explosion. Paraconsistent logic rejects explosion:
contradictions are permitted without allowing arbitrary conclusions.

The key idea: inference is local. A contradiction in one part of the knowledge
base doesn't poison conclusions elsewhere.

**The cognitive move**: When you have genuine contradictions — evidence for both
P and ¬P — you don't have to choose one and discard the other. You can reason
within both models simultaneously, drawing conclusions that hold under both.

This is the formal foundation for `/contradiction-exploit`. Paraconsistent
logic tells you what you're actually doing when you "hold both models live."

**Where it applies**:
- Any domain with genuinely conflicting evidence or data sources
- Legal reasoning (contradictory precedents)
- Database theory (inconsistent databases — query them without crashing)
- Belief revision: integrating new information that contradicts existing beliefs
- Multi-source data fusion with contradictory sensors
- Scientific theory: holding a model that works in one regime and another
  that works in a different regime, without forcing a premature unification

**Where it breaks**:
- Paraconsistency is a logical framework, not a reasoning algorithm. It tells
  you what's valid; it doesn't tell you how to find valid conclusions efficiently.
- Some paraconsistent logics are computationally expensive — reasoning
  complexity can be higher than classical logic.
- The "right" paraconsistent logic for a given domain is not always obvious.
  Different systems (LP, LFI, relevant logic) make different choices about
  what inferences to permit under contradiction.

**Concrete example**:
You have two calibration models for a sensor. Model A predicts X in conditions C₁.
Model B predicts ¬X in conditions C₁. Both have supporting evidence. Rather than
discarding one, work paraconsistently: conclusions that follow from A but not B
are A-conditional, conclusions from B but not A are B-conditional, conclusions
from both are unconditional. Now design the discriminating experiment.

---

## Coboundary Operator / Differential Geometry on Discrete Spaces

**Built to solve**: Extending calculus concepts (gradient, curl, divergence)
to discrete structures like graphs, simplicial complexes, and combinatorial spaces.

The coboundary operator δ: Cⁿ → Cⁿ⁺¹ maps n-cochains to (n+1)-cochains.
On a graph: δ on 0-cochains (vertex functions) gives a 1-cochain measuring
differences across edges — this is the discrete gradient. δ on 1-cochains
gives a 2-cochain measuring inconsistency around triangles — this is the
discrete curl. δ∘δ = 0 always: "exact implies closed" — the curl of a
gradient is zero.

**The cognitive move**: When you have a problem involving flow on a network,
consistency around loops, or the failure of local data to assemble globally —
and the space is discrete — the coboundary operator gives you exact tools
that parallel continuous analysis.

**Where it applies**:
- Circuit analysis (Kirchhoff's laws are coboundary conditions)
- Signal processing on graphs (graph signal processing)
- Distributed consistency: checking that distributed updates around loops
  are consistent (zero curl = globally integrable)
- Ranking from pairwise comparisons (the inconsistency in pairwise rankings
  is measured by a 2-cochain)
- Any problem where "flows" or "potential differences" on a network structure
  need rigorous treatment

**Where it breaks**:
- The richness of continuous differential geometry doesn't fully transfer.
  You lose smoothness, Riemannian metrics, and many global theorems.
- The choice of simplicial complex (how you triangulate your space) affects
  the cohomology you compute. The computation can be sensitive to this choice.
- Cohomology gives global invariants; it doesn't directly give local structure.

**Concrete example**:
If you have pairwise comparisons between items (A beats B, B beats C, C beats A —
a cycle), the inconsistency is measured by a 2-cochain (the discrete curl
of the comparison function). H¹ ≠ 0 means there are globally inconsistent
rankings that can't be reduced to a linear order. The cohomology class tells
you the "size" of the inconsistency.

---

## Holographic Reduced Representations / Vector Symbolic Architectures

**Built to solve**: Composing discrete symbolic structures (trees, graphs,
sequences) into fixed-dimensional vectors that support algebraic operations.

HRR (Plate, 1995) uses circular convolution to bind symbol-value pairs into
a single vector. Key operations: binding (⊛, circular convolution — "A has
role B"), superposition (+ or ⊕ — "X is a mixture of A and B"), probing
(decode: X ⊛ key ≈ value). The dimensionality stays fixed regardless of
structure complexity.

VSAs (hyperdimensional computing) generalize this: random high-dimensional
vectors, bundling (majority/superposition), binding (XOR or element-wise product),
permutation for structure.

**The cognitive move**: When you need compositionality — the ability to combine
primitive representations into structured ones and recover the structure —
without blowing up in dimensionality, VSAs give you a way to do this that
supports algebraic reasoning.

**Where it applies**:
- Representing structured objects (graphs, sequences, sets) as fixed-size vectors
- Associative memory: store many patterns, retrieve by partial match
- Analogical reasoning: structure mapping between vector-encoded structures
- Any problem where you need both symbolic structure and the ability to learn/generalize
- The "symbols vs. vectors" problem — VSAs argue the dichotomy is false

**Where it breaks**:
- Approximate: binding and unbinding are approximate, not exact. Errors accumulate.
  Deep nesting of operations degrades fidelity.
- High dimensionality required for reasonable accuracy (thousands of dimensions).
- The algebra doesn't compose arbitrarily deeply without error — there are
  depth limits for reliable recovery.
- Not widely supported by standard ML frameworks; specialized implementations needed.

**Concrete example**:
Representing a sentence structure as a fixed-size vector: role-filler binding
maps (subject ⊛ "dog") + (verb ⊛ "chases") + (object ⊛ "cat") into a single
vector. Probing with subject extracts ≈ "dog". The sentence's structure is
encoded without a parse tree data structure — it's algebra in high-dimensional
space.

---

## When to reach for this stack

Each structure signals a specific failure mode of simpler approaches:

| Signal | Reach for |
|--------|-----------|
| "Close" is hierarchical, not numeric | P-adic numbers |
| Problem is secretly "minimize over paths" | Tropical algebra |
| Local data won't assemble globally | Sheaf theory / cohomology |
| Need to compare infinite or infinitesimal quantities algebraically | Surreal numbers |
| Genuine contradictions that shouldn't force a choice | Paraconsistent logic |
| Need calculus concepts on a graph or discrete space | Coboundary / discrete exterior calculus |
| Need composable symbolic structure in fixed-dim vectors | VSAs / HRR |

The deeper signal: **the standard approach is making something simple look complex.**
If the machinery feels like it's working against the problem, the problem may
be living in a different mathematical space than the one you're working in.

Use `/bridge-protocol` when you suspect one of these structures applies but aren't sure.
Use `/paradigm-hold` when you commit to one as a working frame.
Use `/contradiction-exploit` when two structures both fit and you need to discriminate.
