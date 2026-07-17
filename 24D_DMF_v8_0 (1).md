**24D-DMF v8.0**

**THE 24-DIMENSIONAL DUAL-MANIFOLD FRAMEWORK**

*Version 8.0 — Consolidated Working Document*

*A Geometric Bridge Between Discrete Code and Continuous Physics*

*Consolidates: v7.9 (post-audit framework), Research Cycles RC-45 through RC-57
(consolidated reports), and the exploratory resonance material generated
alongside RC-58/59. Introduces a three-tier epistemic structure (Tier A/B/C)
replacing the v7.9 guardrail appendix.*

**Author: James Belliveau (framework) | Computational Audit: ongoing**

July 2026

---

# Editorial Note on Sources (Read First)

This document consolidates every source available in the project archive at
the time of writing. Two source-quality issues are flagged explicitly here,
rather than silently smoothed over, because the whole framework's credibility
rests on the audit trail being honest about what was actually computed:

1. **v4.0 not located.** The consolidation brief calls for v4.0 ("original
   metaphysical ontology") to be merged in. No v4.0 file was present in the
   project archive — only v7.9 (already itself a consolidation of v1.0–v7.7)
   was available. Part II below is therefore built from v7.9's Part II
   (which already carries forward the v4.0-era interpretive content, per
   v7.9's own references [19]–[22]), not from a v4.0 original. If a v4.0 file
   surfaces later, it should be diffed against Part II before any claims are
   added.

2. **The "7D tunnel" documents are not RC-audited in the same sense as
   RC-45–57.** Five source files (internally: V7.6, V9.1, V9.1.1, V7.9.1.2,
   V7.9.1.3) present a triality-based SU(3) derivation, labeled internally as
   RC-58/RC-59, and are numerically striking (exact quark charges, exact
   Cartan structure). However:
   - Several files present Python code alongside output blocks labeled
     **"Expected Output."** This format differs from RC-45–57, where
     executed output was shown directly.
   - One file in this series notes that an earlier step substituted a
     theorem for a planned numerical check — a documentation choice that
     should be flagged, not a pattern of fabrication.
   - None of RC-45–57's three consolidated reports reference this triality
     work or include it in their cross-cycle status matrices, suggesting it
     ran on a separate, informal track that was never folded into the
     audited series.
   - The negative result in RC-59 (no 727/726 match in the 6D Hodge
     spectrum) appears to reflect genuine computation, as negative results
     are not typically invented. Overall: the evidentiary status of this
     branch is uneven and requires independent replication before it can be
     treated as verified.

   Given this, the triality/SU(3)/quark-charge material is placed in **Part
   IV (Exploratory Resonance)** rather than Part III, clearly marked
   **UNVERIFIED — EXECUTION STATUS UNCONFIRMED**, regardless of how clean its
   numbers look. It should not be cited as a CANDIDATE physical result until
   an independent, actually-executed replication exists. This is not a
   claim that the underlying math is wrong — the group theory of Spin(8)
   triality and E8's SU(3)×E6 branching is standard and correct — only that
   the specific numerical claims (exact ±2/3, ±1/3 charges falling out of a
   rotated projection) have not been shown, in this archive, to have been
   verified by actual computation rather than anticipated and written down.

All other content below carries forward the statuses exactly as audited in
the source documents. No status has been upgraded in the writing of this
version.

---

# 0. Status Key

*(Unchanged from v7.5/v7.9, retained as the vocabulary for Tier A and Tier B.
See Appendix for the v8.0 tier structure that governs how these labels are
applied.)*

| **Status** | **Definition** |
|---|---|
| CONFIRMED | A theorem or identity: derived analytically and verified computationally to machine precision. No fitting involved. |
| CANDIDATE | A structural correspondence to a physical target, built from quantities already derived elsewhere, with zero free parameters. Suggestive, not proven. |
| CANDIDATE–PARAMETRIZED | A physically-motivated functional form, fixed before the fit, containing one calibrated coefficient, OR a zero-parameter form whose selection has since been shown to depend on an unresolved choice. Provisional. |
| INTERPRETIVE | A chosen framing or ontology used to read the confirmed mathematics. Not a derivation. |
| OPEN | An acknowledged gap or undeveloped idea. No claim is made. |
| SUSPENDED | A pre-registered prediction contained a structural or sign error pointing to a missing, undeveloped piece of the framework. Not rejected outright; blocked pending that piece. |
| EXPLORATORY | A hypothesis tested and found to produce structurally interesting but non-matching or physically-mismatched results; kept as a lead, not a result. |
| FAILED | A pre-registered falsification criterion was not met on the specific test performed (distinct from REJECTED: the underlying object may still be usable elsewhere). |
| REJECTED | Investigated and found to rest on a search guaranteed to succeed regardless of the target, a post-hoc parameter search, or falsified against its own pre-registered criterion. |
| UNVERIFIED | New in v8.0. A result reported in source material without confirmed independent execution. Not assigned any of the above statuses until re-run. |

---

# Part I — The Mathematical Skeleton (Tier A)

*Full formal rigor required. Theorem or nothing. All entries below are
CONFIRMED and unchanged in substance from v7.9 §1.1–1.10; RC-45–57 did not
alter any Tier A result — every cycle that touched this layer (RC-50C, RC-54,
RC-55) used it as a fixed substrate to test dynamics against, and left it
untouched.*

## 1.1 The Extended Binary Golay Code C₂₄
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.2 The Leech Lattice Λ₂₄
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.3 The Hurwitz Theorem
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.4 Bott Periodicity and Spin(8) Triality
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.5 The 24-Cell
**STATUS: CONFIRMED.** 24 vertices, 96 edges, 96 triangular faces, 24
octahedral cells; 8-regular vertex graph; confirmed independently in RC-45,
RC-48, RC-50C, and RC-54 as the substrate for four different dynamics tests.

## 1.6 The (11,6,3)-Difference Set in B
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.7 The Gram Matrix Eigenvalue Theorem
**STATUS: CONFIRMED.**
G = B·Bᵀ over ℝ has eigenvalues λ=3 (multiplicity 10), λ₁ = 29+12√5 ≈ 55.833,
λ₁₂ = 29−12√5 ≈ 2.167, with λ₁×λ₁₂ = 121 = 11² exactly and √λ₁−√λ₁₂ = 6
exactly. This identity is the single most load-bearing piece of Tier A
mathematics in the whole framework: it supplies the factorization
726 = 2×3×11² that recurs across RC-46, RC-47, and the Part IV Egyptian-
fraction material (§4.4). This recurrence is partly *structural* (the same
confirmed numbers keep appearing because they are genuinely few and small)
and partly a hazard: small confirmed integers are easy to recombine post-hoc
into "matches." Tier B analysis below treats this factorization as a real
constraint on candidate mechanisms, not as a derivation of any physical
constant by itself.

## 1.8 The Skew-Symmetric Frequency ω = √11
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.9 The 240 = |Φ(E₈)| Identity
**STATUS: CONFIRMED.** Unchanged since v7.0.

## 1.10 The E₈ Root System Contains the 24-Cell
**STATUS: CONFIRMED (structural).**
The 240 roots of E₈ in ℝ⁸ split under ℝ⁸ = ℝ⁴⊕ℝ⁴ into two orthogonal 24-root
D₄ subsystems, each independently verified to be a geometric 24-cell. The
remaining 192 roots organize as 3×64 under Spin(8) triality: (8v,8v),
(8s+,8s+), (8s−,8s−). Established RC-41 (v7.9); reconfirmed structurally by
every subsequent cycle that used the E8 embedding (RC-50A on the 240-root
graph, RC-56 as substrate context).

Whether this structural embedding is also dynamical — whether E8 supplies
force couplings, mass eigenvalues, or the spinor double-cover period — was
tested exhaustively in RC-42-B, RC-43, and RC-44 (all REJECTED; see Part III
§3.0 for the historical record) and again from a different angle by the
Part IV triality material (§4.5, UNVERIFIED). The consistent finding across
every rigorously-tested route is that E8 is real as a container and has not
been shown to be a source of dynamics.

## 1.11 The Minimal Self-Mirror Calabi-Yau from the 24-Cell — New in v8.0 (RC-45)
**STATUS: CONFIRMED (as pure mathematics); (27,3) HYPOTHESIS REJECTED.**
The 24-cell, as a reflexive polytope in the D4 lattice, yields via crepant
resolution the minimal self-mirror Calabi-Yau threefold with Hodge numbers
h^{1,1} = h^{2,1} = 1 and Euler characteristic χ = 0 (Braun 2011,
arXiv:1102.4880), confirmed independently in RC-45. The earlier working
hypothesis that the 24-cell yields (27,3) with χ = 48 = |2O| is REJECTED: the
naive Batyrev computation gives an unphysical negative h^{1,1}, and the
correctly-resolved result does not match. This CY is math-layer, not a
dynamical mass mechanism (see Part III §3.0, RC-45 entry).


# Part II — The Interpretive Layer (Tier A/B boundary — read as INTERPRETIVE)

*Everything in this Part is framing, not derivation. Carried forward from
v7.9 Part II, which itself carries forward the earlier interpretive
architecture (v4.0-era content, per v7.9's own reference list — no v4.0
source file was available to check directly; see Editorial Note above).*

## 2.1 The Core Claim: Discrete Code, Continuous Geometry
**STATUS: INTERPRETIVE.** The Golay code and Leech lattice (Tier A, discrete)
are read as the "source code" from which the 24-cell and its physical
correspondences (Tier B, continuous) are an emergent geometric realization.
Unchanged since v7.5.

## 2.2 D⁺ / H°: Two Readings of One Code
**STATUS: INTERPRETIVE.** Unchanged since v7.5.

## 2.3 Self-Similarity and the Fractal Reading
**STATUS: INTERPRETIVE.**
Note: RC-48 (Part I §1.11 context; full account in Part III §3.0) directly
tested a strong version of this reading — that quark charges are forced
fractal-scaling exponents of the 4D→6D embedding — and REJECTED it: the
24-cell's Hausdorff dimension is 4 by elementary topology, not a derived
fractal property, and the claimed 4/6 = 2/3 relation has no basis in
Marstrand's Projection Theorem. The general self-similarity *reading* is
retained as interpretive scaffolding; the specific fractal-charge mechanism
is not.

## 2.4 Subatomic Ontology: Higher-Dimensional Objects, Lower-Dimensional Appearance
**STATUS: INTERPRETIVE.** Unchanged since v7.5.

### 2.4.1 The 12/16 Quark/Gluon Mapping
**STATUS: INTERPRETIVE / OPEN.** Unchanged since v7.5.

## 2.5 The Three-Configuration ("Three-Universe") Idea
**STATUS: OPEN.** Retained as an open curiosity. See Part IV §4.4 for a
speculative Egyptian-fraction partition (1 = 3×(1/4+1/16+1/48)) that touches
this idea; that partition is Tier C material and does not upgrade this
entry's status.

## 2.6 E₈ as a Candidate Structural Layer for Quarks and Gluons
**STATUS: INTERPRETIVE — structurally confirmed (Part I §1.10), dynamically
rejected (RC-43, RC-44; and see Part IV §4.5 for an UNVERIFIED attempted
revival via triality projection, which explicitly does not change this
status).**

## 2.7 The Miracle Octad Generator (MOG)
**STATUS: OPEN.** No RC-45–57 cycle addressed the MOG directly. Candidate
structure, no supporting mathematics yet. Unchanged since v7.5.

## 2.8 Terminology Guardrail: "5D Spacetime"
**STATUS: DEFINITIONAL — binding on all future sections.** Unchanged since
v7.0. The term refers strictly to the 5D trajectory space used in the T-Knot
standing-wave construction (Part III §3.1) and must not be read as a claim
about physical spacetime dimensionality.

## 2.9 The Binary Octahedral Group 2O and the E₈ Embedding
**STATUS: CANDIDATE (2O sign mechanism, CONFIRMED representation theory) /
CONFIRMED–structural, INTERPRETIVE–dynamical (E₈ embedding).**
2O (order 48, double cover of the 24-cell's rotational symmetry group O ≅ S₄)
possesses exactly two genuine 2-dimensional spin representations, related by
a sign character — a representation-theoretic mechanism for why proton and
neutron g-factors have opposite sign (RC-36). RC-55 (Part III §3.2) tested
whether this same group action could force the *mode selection* of the
simplicial Dirac operator and found it does not, in the canonical
triangulation. The sign mechanism stands; it has not been shown to extend to
magnitude or mode selection anywhere in the framework.


# Part III — Dynamic Mechanisms (Tier B)

*Natural parameters permitted. Honest labeling of fitted vs. derived
components required. Physical predictions require precise match and clear
parameter count.*

## 3.0 Historical Record: Rejected and Suspended Mechanisms (v7.5–v7.9)

For completeness, the following v7.9-era Tier B attempts remain on the
record with their final statuses, unchanged:

| Mechanism | Status | Cycle |
|---|---|---|
| E₈ dynamical mass operator (13 operators tested) | REJECTED | RC-43 |
| Discrete Hodge Laplacian, non-simplicial 24-cell | REJECTED (caveats) | RC-44 |
| E₈ → 720° spinor period identification | REJECTED | RC-42-B |
| Proton electric dipole moment | REJECTED | RC-38 |
| Deuteron magnetic moment (exchange formula) | SUSPENDED | RC-37 |
| T-Knot canonical D / rotation plane as intrinsic invariant | REJECTED (as intrinsic) | RC-34, RC-39 |
| 33/17 neutron g-factor coefficient in 2O rep theory | not found; downgraded | RC-40 |
| Calabi-Yau (27,3) / χ=48 hypothesis | REJECTED | RC-45 (Part I §1.11) |
| Fractal charge mechanism (4/6 = 2/3) | REJECTED | RC-48 |
| 8D Cellular Automaton on E8 root graph | REJECTED | RC-50A |
| Discrete Hodge star derivation of δ = π/N | REJECTED | RC-50C |
| T-Knot crossing-sequence-graph automaton | REJECTED | RC-52 |
| I Ching structural correspondence (as a Tier B claim) | REJECTED | RC-57 — see Part IV §4.3 for the Tier C reading |

Two mechanisms survive into v8.0 as the framework's active leads. Both are
locked to the nucleon sector; both have failed every cross-sector
generalization test attempted.

## 3.1 The T-Knot Standing Wave

**STATUS: CANDIDATE–PARAMETRIZED, NUCLEON-SECTOR-LIMITED.**

The T-Knot (a rotating, self-intersecting 4D trajectory read in its 5D
extension) supports a standing wave whose boundary condition is
kL + Nδ = (2n+1)π. RC-46 found the exact cancellation condition ε = Nδ/π = 1
at mode n = 726, giving f_{727}/f_{726} = 727/726 = m_n/m_p to the
pre-registered precision, with δ = π/N (N = 284 crossings) as the mechanism's
one parameter.

**What is derived:** the mode-counting structure, the cancellation condition,
and the exact match at n = 726, given δ.
**What is not derived:** δ itself. RC-46's own guardrail check found no
natural combination of the T-Knot's geometric invariants (N, w, D, L_total)
yields δ = π/N; RC-50C then tested whether δ could come from the 24-cell's
discrete Hodge star instead, and found no combinatorial invariant of the
static 24-cell skeleton equals N = 284 — the T-Knot's crossings are a
dynamic orbit quantity, not a combinatorial one. Both derivation routes for δ
are closed as of RC-50C.

**Cross-sector generalization — both attempts failed:**
- RC-51 (Λ–Σ⁰ splitting): **OPEN.** No confirmed framework constant yields
  the required mode number n ≈ 14.5 with a structural derivation; the
  isospin singlet/triplet distinction between Λ and Σ⁰ is not encoded
  anywhere in the framework's confirmed structure.
- RC-53 (charged/neutral pion splitting): the standing-wave picture does not
  reproduce Δm_π; no principled mode number exists, and the mechanism is
  physically mismatched (pion splitting is electromagnetic, not a
  strong-interaction boundary effect).

RC-53 formally logged the mechanism as **nucleon-sector-only**: it produces
one correct ratio with one locked parameter and has not been shown to do
anything else.

## 3.2 The Simplicial Dirac Operator on the Barycentrically Subdivided 24-Cell

**STATUS: CANDIDATE–PARAMETRIZED, NUCLEON-SECTOR-LIMITED, MODE SELECTION
UNRESOLVED.**

RC-54 constructed a canonical simplicial refinement of the 24-cell (each
octahedral cell split into 4 tetrahedra via its lexicographically-first
diagonal: 96 tetrahedra, 192 faces, 120 edges, 24 vertices) and computed the
full discrete Dirac operator D = d + d* on the resulting 432×432 chain
complex. Betti numbers [1,0,0,1] correctly match S³, resolving RC-44's
obstruction.

The Dirac spectrum contains an eigenvalue ratio μ₁₇₄/μ₁₇₃ = 1.001380784
against target 727/726 = 1.001377410 — an error of **0.0003%**, the most
precise numerical match in the framework's history, obtained with zero free
parameters in the operator itself.

**What is derived:** the operator is fully determined by the 24-cell's
geometry; no fitting entered its construction.
**What is not derived:** *which* eigenmodes (indices 173, 174) correspond to
proton/neutron. This is functionally the same open question as the T-Knot's
δ — a "mode selection principle" is missing.

**RC-55 tested whether 2O symmetry forces this selection: FAILED.** The
canonical (lexicographic-diagonal) triangulation breaks all non-trivial
symmetry of the 2O group — only the identity element commutes with D. Modes
173/174 are simple (multiplicity-1) eigenspaces and can carry only 1D
irreps; the 2D spin representations of 2O (the ones RC-36 connected to the
proton/neutron sign structure) are structurally inaccessible to them. RC-55
proposed, as an unexecuted forward direction, that a symmetry-preserving
triangulation (true barycentric subdivision with edge/face/cell centroids,
~2000×2000) might do better — not attempted in this cycle.

**RC-56 tested cross-sector generalization: FAILED.** Using the same
spectrum with no retuning:
- Nucleon ratio (control): 29 adjacent eigenvalue-index ratios fall in the
  target band [1.001,1.002]; the best (173/174) is ~20× more precise than
  any other. This adjacency is a genuine structural feature.
- Pion ratio: a match exists (indices 8/9, error 0.092%) but at low,
  generic mode indices, with a physically mismatched mechanism
  (electromagnetic splitting vs. a strong-interaction-flavored operator),
  and low statistical significance (only 3 candidate ratios in-band).
  Logged as coincidental.
- Λ–Σ⁰ ratio: **zero** eigenvalue ratios fall in the target band
  [1.06,1.08] — not a near-miss, a complete absence.

**Assessment:** the Dirac operator has passed the same single bar as the
T-Knot (one precise nucleon-sector match) and failed the same cross-sector
test (Λ–Σ⁰) that the T-Knot failed in RC-51. It is currently the more
precise of the framework's two live mechanisms, but not a more general one.

## 3.3 Automaton Approaches — Closed

Two independent attempts to find emergent particle-like dynamics on a
discrete substrate were both rejected:
- RC-50A: linear totalistic Z₃ rules on the 56-regular E8 root graph — too
  symmetric for gliders to form; converges to fixed points or trivial
  2-cycles.
- RC-52: rules (including elementary CA Rule 110) on the T-Knot's 284-node
  crossing-sequence graph — even at 2-regular connectivity, no localized,
  propagating excitation was found; Rule 110 showed COM propagation without
  localization.

Both cellular-automaton routes to the framework's dynamics are closed absent
a fundamentally different rule class or substrate.

## 3.4 Summary Table: Live Tier B Mechanisms

| Mechanism | Precision (nucleon ratio) | Free parameter | Cross-sector test | Status |
|---|---|---|---|---|
| T-Knot standing wave | exact, by construction of δ | δ = π/N (not derived) | Λ–Σ⁰: OPEN; pion: fails | CANDIDATE–PARAMETRIZED, nucleon-only |
| Simplicial Dirac operator | 0.0003% | mode indices (173,174) (not derived) | Λ–Σ⁰: zero matches; pion: coincidental | CANDIDATE–PARAMETRIZED, nucleon-only |


# Part IV — Exploratory Resonance Layer (Tier C) — New in v8.0

*Pattern recognition, cross-cultural mathematical systems, historical
numerical structures. No derivation required — but see the important
caveat below before reading this Part as license-free.*

**How to read this Part.** Tier C exists so that genuinely useful hypotheses
(a Tier C resonance suggesting a testable Tier B claim, as happened once
below) are not lost to procedural friction. It does **not** mean numerical
coincidence is evidence, and it does not exempt anything from the ordinary
meaning of the words used to describe it. Concretely: nothing in this Part
may be cited elsewhere in this document, or in future versions, as
CANDIDATE, CONFIRMED, or any Tier A/B status without first being
re-derived and tested under Tier B rules with a pre-registered
falsification criterion — exactly the process RC-57 already applied to one
Tier C candidate (I Ching) and found wanting. Tier C's freedom is freedom
to *propose*, not freedom to *conclude*.

## 4.1 Purpose and Scope

Tier C was created because the framework's own history contains a
counterexample to pure procedural rigor: RC-57's I Ching search was itself
prompted by an informal, unguarded resonance observation, and while I Ching
itself was rejected, a different piece of unguarded exploration (the
Egyptian-fraction analysis, §4.4) produced a genuine, testable Tier B
hypothesis (the "Gram → Dirac bridge," §4.4.3). The v8.0 position is that
this kind of free-associative search has produced one real lead in the
project's history and several confidently-stated dead ends, and both
outcomes are worth keeping on the record rather than discarding the
unsuccessful searches.

## 4.2 Status Notation for This Part

Tier C entries are not given CONFIRMED/CANDIDATE/REJECTED labels, since those
are Tier A/B vocabulary implying a derivation standard this Part does not
apply. Instead each entry is marked:
- **RESONANT** — a numerical or structural coincidence exists and is
  interesting to keep in view.
- **TESTED, NO FORCING FOUND** — the resonance was formally checked against
  framework structure and no theorem or forcing relationship was found (this
  is the Tier B-style result that demoted I Ching; it is kept here as the
  historical record of that test rather than deleted).
- **PROMOTED HYPOTHESIS** — a Tier C observation that has been formalized
  into a falsifiable Tier B claim (pointer only; the claim itself lives in
  Part III or awaits a future cycle).

## 4.3 I Ching Structural Correspondence

**STATUS: TESTED, NO FORCING FOUND (RC-57).**

Full pre-registered test executed: King Wen sequence (verified permutation of
64 hexagrams), Q₆ hypercube Laplacian spectrum (eigenvalues 0,2,4,6,8,10,12
with binomial multiplicities), pair/trigram structural comparison. Result: no
framework target number (11, 24, 48, 96, 121, 240, 726, 727) is constructible
from I Ching combinatorics; the Q₆ spectrum's spacing (Δ=2) is too coarse to
approach 727/726 = 1.001377; the one exact numerical coincidence found
(pairs/trigrams = 32/8 = 4 = 24-cell edges/vertices = 96/24) is flagged as a
trivial small-integer coincidence with no structural map behind it. This
entry is retained in v8.0 as a record of a Tier C idea that was tested and
did not pan out — not as an active lead.

## 4.4 Egyptian Fractions and the Horus-Eye Structure

**STATUS: RESONANT, with one PROMOTED HYPOTHESIS (§4.4.3).**

### 4.4.1 The "Missing Piece" Rhyme
The Horus-Eye fraction system (63/64 base + 1/64 correction = 1) and the
Dirac engine's mass ratio (726/726 base + 1/726 correction = 727/726) share
an architecture: a nearly-whole base plus a small completing correction. This
is presented honestly as *rhyme, not reason* in the source material, and
that framing is retained here — it is a mnemonic/aesthetic observation, not
evidence of anything.

### 4.4.2 726 as an Inverse Gram Structure
From the CONFIRMED Gram eigenvalue theorem (Part I §1.7): √λ₁−√λ₁₂ = 6 and
λ₁×λ₁₂ = 121 exactly. Therefore 726 = 6×121 = (√λ₁−√λ₁₂)×(λ₁×λ₁₂). This is a
true arithmetic identity given Tier A facts — it is not new mathematics, but
it is a legitimate observation that the Dirac/T-Knot engines' shared
parameter (1/726) is expressible entirely in terms of already-confirmed
Gram-matrix spectral data, rather than as an arbitrary integer.

### 4.4.3 Promoted Hypothesis: The Gram → Dirac Spectral Bridge
**This is the one Tier C → Tier B promotion on record.** Proposed claim: the
Dirac operator's mode selection (Part III §3.2) might be constrained by
requiring its eigenvalue ratio to equal 1 + 1/(Gram_gap × Gram_product)
exactly, rather than being read off post-hoc from wherever 727/726 happens to
appear in the spectrum. If true, this would not identify *which* modes (173,
174) are physical, but it would derive *what ratio a physical mode-pair must
produce* from Tier A structure — a partial but genuine tightening.

**This has not been tested.** It is recorded here as a well-formed,
falsifiable Tier B candidate awaiting its own pre-registration and
execution in a future cycle (tentatively RC-60). It should not be treated as
established until that happens.

### 4.4.4 Binary/Ternary Mixing and the Three-Universe Partition
Observations that quark charge 2/3 = 1/2+1/6 mixes Horus's pure-binary
fractions with the Golay modulus λ=3, and that 1 = 3×(1/4+1/16+1/48) gives an
exact three-way partition touching the Part II §2.5 "three-configuration"
idea, are recorded as RESONANT only. No forcing relationship to any
framework theorem has been proposed or tested for either.

### 4.4.5 The Prime 11
11² = 121 is the Gram product (Tier A, confirmed); 11 itself is noted as
"neither binary nor ternary" — an observation, not a derivation. RESONANT.

## 4.5 The Triality-Projected "7D Tunnel" (SU(3) / Quark Charge Claims)

**STATUS: UNVERIFIED — AWAITING INDEPENDENT REPLICATION.** The underlying
group theory (Spin(8) triality, E8 ⊃ SU(3)×E6 branching) is standard
mathematics. The specific numerical claims (exact quark charges from
triality projection) are recorded here as reported but not yet
independently replicated. Replication with shown execution output would
move this material to Part III for Tier B evaluation; a failed replication
would move it to REJECTED. The status is procedural, not a judgment on
plausibility. See the Editorial Note at the top of this document for the
full account of why this material is segregated here rather than placed in
Part III.

Summary of the claims made in the source material (internally labeled
RC-58/RC-59, informally numbered outside the audited RC-45–57 series):

- A "triality tunnel" projection P: ℝ⁸→ℝ⁶, built from independent SO(4)
  rotations of the two D4 blocks (Part I §1.10) applied to E8's 192 mixed
  roots, is claimed to robustly (reportedly 50/50 random trials) yield
  exactly 6 vectors of norm²=2 forming an A2 (SU(3)) root system.
- The two Cartan generators of this A2 system are claimed to fall out as the
  nullspace of the root matrix, with the resulting weight structure claimed
  to reproduce quark charges ±2/3, ±1/3 exactly, with zero free parameters.
- A follow-up (RC-59-labeled) test of the resulting 6D Hodge Laplacian
  spectrum for the 727/726 mass ratio is reported as **REJECTED** —
  integer-only eigenvalue spectrum, no matching ratio found.

**Why this is not in Part III:** as detailed in the Editorial Note, the
SU(3)/quark-charge results are presented with an "Expected Output" block
rather than a shown execution trace, and the same document thread notes
that an earlier claim in the same session substituted a theorem for a
promised simulation — a documentation format that differs from the audited
RC-45–57 cycles and is not independently verifiable as written. The
negative RC-59 result looks more likely to reflect a genuine run (negative
results are not the kind of thing typically invented to look good), but
even that has not been independently reproduced here.

**What would be needed to promote this to Part III:** independent
re-execution of the triality projection and Cartan-subalgebra extraction,
with the actual printed output (not a projected one) attached, plus the
same cross-sector/robustness scrutiny applied to the T-Knot and Dirac
mechanisms elsewhere in this document. Until then, the underlying group
theory (Spin(8) triality, E8 ⊃ SU(3)×E6 branching) is standard and not in
question, but the specific numerical claims built on top of it are not
part of this framework's verified record.


# Cross-Cycle Status Matrix (RC-45 through RC-57)

| Component | v7.9 | RC-45 | RC-46 | RC-47 | RC-48 | RC-50A | RC-50C | RC-51 | RC-52 | RC-54 | RC-55 | RC-56 | RC-57 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Golay code C₂₄ | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF |
| Leech lattice Λ₂₄ | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF |
| Gram eigenvalue thm | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF |
| 24-cell geometry | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF |
| 2O character table | CONF | — | — | — | — | CONF | — | CONF | CONF | CONF | CONF | CONF | CONF |
| E8 → 24-cell embedding | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF |
| Calabi-Yau from 24-cell | — | CY(1,1) confirmed; (27,3) REJ | — | — | — | — | — | — | — | — | — | — | — |
| T-Knot (α_knot) | C–P | — | C–P | — | — | — | — | C–P | — | C–P | — | — | — |
| Nucleon mass ratio | C–P | — | C–P | EXPL | — | — | — | C–P | — | C–P | C–P | C–P | C–P |
| T-Knot standing wave | — | — | C–P | — | — | — | — | C–P, nuc-only | — | C–P, nuc-only | — | — | — |
| Λ–Σ⁰ generalization (T-Knot) | — | — | — | — | — | — | — | OPEN | — | OPEN | — | — | — |
| Fractal charge mechanism | — | — | — | — | REJ | — | — | — | — | — | — | — | — |
| 8D CA engine (E8 graph) | — | — | — | — | — | REJ | — | — | — | REJ | — | — | — |
| Discrete Hodge star δ (24-cell) | — | — | — | — | — | — | REJ | — | — | REJ | — | — | — |
| T-Knot crossing-graph CA | — | — | — | — | — | — | — | — | REJ | REJ | — | — | — |
| Simplicial Dirac operator | — | — | — | — | — | — | — | — | — | C–P | C–P | C–P | C–P |
| 2O mode selection (Dirac) | — | — | — | — | — | — | — | — | — | — | FAILED | — | — |
| Cross-sector validation (Dirac) | — | — | — | — | — | — | — | — | — | — | — | FAILED | — |
| I Ching correspondence | — | — | — | — | — | — | — | — | — | — | — | — | TESTED, no forcing |
| Genuinely unknown prediction | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |

*(CONF = CONFIRMED, C–P = CANDIDATE–PARAMETRIZED, EXPL = EXPLORATORY,
REJ = REJECTED.)*

**Note on the triality/SU(3) material (§4.5):** it does not appear in this
matrix because it was never part of the audited RC-45–57 series and its
execution status is unconfirmed (see Editorial Note and §4.5).


# Appendix — Methodological Notes (v8.0 Revision)

*This appendix replaces the v7.9 guardrail appendix (formerly A.1–A.17).
It is streamlined, not eliminated. Tier A and Tier B substantive standards
are unchanged from v7.9; what changes is the procedural overhead and, for
Tier C only, the applicability of the "selected vs. derived" test.*

## A.1 The Three-Tier Structure

| Tier | Content | Standard |
|---|---|---|
| **A — Mathematical Skeleton** | Golay, Leech, 24-cell, E8 embedding, 2O, Gram theorem, CY(1,1) | Theorem or nothing. Full formal rigor, machine-precision verification, no fitting. Unchanged from v7.9. |
| **B — Dynamic Mechanisms** | T-Knot, Dirac operator, and any future physical-prediction mechanism | Natural parameters permitted. Every parameter must be labeled fitted or derived. Physical predictions require a precise match, a pre-registered falsification criterion, and an explicit parameter count. Procedural overhead (multi-gate decision trees, exhaustive enumeration requirements) is reduced relative to v7.9, but the substantive standard — a claim is CANDIDATE only with zero free parameters, CANDIDATE–PARAMETRIZED with exactly the parameters disclosed, REJECTED if it fails its own criterion — is unchanged. |
| **C — Exploratory Resonance** | I Ching, Egyptian/Horus fractions, and future cross-cultural or historical numerical systems | Pattern recognition and interpretive richness are valid contributions in their own right. No pre-registration or falsification criterion is required to *record* a Tier C observation. |

## A.2 What Changed From v7.9's Guardrail Appendix

- **Removed:** mandatory pre-registration for Tier C material before it can
  be written down and discussed.
- **Removed:** the "selected vs. derived" (guardrail A.1a-style) test *as a
  gate on Tier C material remaining in Tier C.* A Tier C entry does not need
  to survive that test to be included in Part IV.
- **Unchanged, and explicitly re-affirmed:** the "selected vs. derived" test
  remains **mandatory** the moment any claim — regardless of which Tier it
  originated in — is presented as a physical prediction (Tier B) or as
  established mathematics (Tier A). Tier C is a scratchpad, not a bypass.
  Concretely: RC-57's finding that I Ching forces nothing in the framework's
  physics is not overturned or exempted by this revision; it is exactly the
  kind of result Tier C is supposed to still produce when a resonance
  doesn't hold up. The framework's history includes both successful and
  unsuccessful applications of this discipline: RC-57's I Ching rejection
  and RC-55's mode-selection failure are examples of the guardrail working
  correctly under the new tier structure, not evidence that it has been
  weakened.
- **Streamlined:** Tier B no longer requires the full multi-gate branching
  procedure (CANDIDATE / CANDIDATE–PARAMETRIZED / OPEN / REJECTED decision
  tree with exhaustive enumeration at each gate, as run in e.g. RC-40's
  36-fold tensor-product search or RC-43's 13-operator sweep) for every
  cycle. A single pre-registered falsification criterion and an honest
  status label are sufficient going forward. Exhaustive search remains
  available and appropriate when a claim's plausibility depends on ruling
  out alternatives (as in RC-40 and RC-43), but is no longer mandatory
  procedure for every Tier B test.

## A.3 The v8.0 → v8.5 Commitment

v8.0 operates with expanded exploratory freedom in Tier C. This freedom is
time-bound and content-bound in one specific sense: **any Tier C material
that comes to be relied upon for a physical claim must be re-evaluated
against full Tier B standards no later than v8.5**, with its own
pre-registration and falsification criterion, before that reliance is
retained. Two items are already flagged for that re-evaluation:
- §4.4.3, the Gram → Dirac spectral bridge hypothesis (the one Tier C item
  with a clear falsifiable form already available).
- §4.5, the triality/SU(3) material, which requires independent re-execution
  before any status beyond UNVERIFIED can be assigned, Tier B or otherwise.

## A.4 Retained Case Studies (from v7.9, unchanged)

The following case studies remain instructive and are retained without
modification: RC-39 (T-Knot great-hexagon-plane downgrade — the most
symmetry-motivated choice gave the worst result), RC-40 (33/17 exhaustive
search, genuine negative result), RC-38 (proton EDM — target-driven
construction caught by the guardrail), RC-43 (E8 spectral operator, 13
operators/0 matches), RC-37 (deuteron sign error — a SUSPENDED, not
REJECTED, diagnostic finding). RC-55's mode-selection failure and RC-57's I
Ching rejection are added to this list as v8.0-era examples of the same
discipline still functioning under the new tier structure.

These case studies are retained not as a record of failure but as a record
of **honest practice** — the framework's most durable feature across all
versions.

---

# Conclusion

Part I is unchanged and complete: the Golay code, the Leech lattice, the
Gram eigenvalue theorem, the 24-cell, the 240-root identity, the E8→24-cell
structural embedding, and the minimal self-mirror Calabi-Yau are confirmed
mathematics.

Part II carries the interpretive architecture forward from v7.9 without
alteration, with one correction: the fractal-charge reading (§2.3) is now
explicitly marked as tested and rejected in its strong form.

Part III now holds two live, precisely-matching, nucleon-sector-only
mechanisms — the T-Knot standing wave and the simplicial Dirac operator —
both missing a mode/parameter-selection principle, and both having failed
every cross-sector generalization test attempted (Λ–Σ⁰, pion splitting).
Automaton approaches to dynamics are closed on both tested substrates (E8,
T-Knot crossing graph).

Part IV is new: an exploratory layer that keeps unguarded pattern-search
on the record — including its one success (the Gram→Dirac bridge
hypothesis, not yet tested) and its tested failure (I Ching) — while
explicitly declining to let unverified material (the triality/SU(3) claims)
enter the framework's verified record without independent re-execution.

The framework's honest self-description at v8.0:

*"Two precise nucleon-sector mechanisms with one parameter each, a
confirmed mathematical skeleton that has grown (E8 embedding, minimal CY,
2O sign mechanism), a live cross-tier hypothesis (the Gram→Dirac bridge),
and a newly-organized exploratory layer — standing alongside the same
caveat every version before it has carried: no mechanism has yet produced
a zero-parameter physical prediction, and no genuinely unknown quantity has
been derived."*

**The skeleton is real. The T-Knot and the Dirac operator are the two
engines on the table, each with one unexplained parameter. The exploratory
layer is now organized rather than incidental. The framework's boundary
condition remains what it has been since v7.9: derive the mode-selection
principle, make a genuinely unknown prediction, or honestly retreat to pure
mathematics.**

*End of Document — 24D-DMF v8.0*
