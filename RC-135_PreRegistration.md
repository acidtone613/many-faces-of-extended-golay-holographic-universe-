================================================================================
RC-135 PRE-REGISTRATION
The Logical Core: Is Class B Closed Under the Non-Clifford Phase?
Framework: 24D-DMF v8.4.3
Date: 2026-07-08
Status: PRE-REGISTERED — Results Binding Upon Execution
================================================================================

TITLE
-----
The Logical Core: Is Class B Closed Under the Non-Clifford Phase?

BACKGROUND
----------
RC-134 established that the Degeneracy Hypothesis is rejected for Class D and E:
DH23 is an exact fixed point (delta = 0.000000), and Class D basins are genuine
dynamical features (gamma = 0.000000 for all epsilon in [0.1, 0.5]). The
discretization heuristic correctly identifies orbit classes but produces sampling
artifacts for internal transition counts within non-degenerate orbits.

RC-134 Synthesis identified the remaining gate before holography: proving that
Class B is the "logical subspace" of the engine — the subset of deep holes that
is closed under the engine's unitary evolution and therefore serves as the
computational core of any holographic dictionary.

The non-Clifford phase, first identified in RC-117, introduces angles of
pi/23 and 2*pi/23 into the Floquet evolution. If Class B is the logical
subspace, this phase should map Class B holes to Class B holes. If it leaks
into Class A, C, D, or E, then Class B is not the full logical subspace.

RC-135 tests this closure property directly.

================================================================================
1. DEFINITIONS
================================================================================

1.1 Non-Clifford Phase Operator
--------------------------------
For angle theta, the non-Clifford phase operator U_phase(theta) acts on a
24D vector v as a diagonal rotation in the plane spanned by coordinates
(0, 23) — the P23-cycle origin and the fixed-point anchor:

  U_phase(theta): v -> v'
  where:
    v'[0]  = cos(theta) * v[0] - sin(theta) * v[23]
    v'[23] = sin(theta) * v[0] + cos(theta) * v[23]
    v'[i]  = v[i] for i in {1, ..., 22}

This is a rotation in the (0, 23) plane that leaves coordinates 1-22 unchanged.
The angles tested are:
  theta_1 = pi / 23  (fundamental phase)
  theta_2 = 2*pi / 23 (harmonic phase)

RATIONALE: Coordinate 0 is the "origin" of the P23 cycle, and coordinate 23 is
the fixed-point anchor. Rotating in this plane introduces a non-Clifford phase
that couples the cyclic dynamics to the fixed point without disturbing the
intermediate coordinates.

1.2 Phase-Modified Floquet Tick
--------------------------------
For tick t and phase angle theta, the modified tick is:

  T_phase(t, theta) = T(t) o U_phase(theta)

applied as:
  1. Apply U_phase(theta) to v
  2. Apply standard Floquet tick T(t) = P23 -> P11 -> H_L (if t % 11 == 0)

1.3 Class B Closure
--------------------
Class B is "closed under phase theta" if, for every Class B start s, the
orbit under T_phase(t, theta) visits only holes in the Class B union set:

  Union_B = {0, 4, 7, 10, 11, 16, 22}

1.4 Leakage Score
------------------
For start s, phase theta, and N ticks:

  Lambda(s, theta, N) = (1/N) * |{ t in {0,...,N-1} : nearest(v_t) not in Union_B }|

where nearest(v_t) is the index of the closest deep hole template to v_t.

================================================================================
2. PRE-REGISTERED HYPOTHESES
================================================================================

H1 (Fundamental phase closure)
-------------------------------
For theta = pi/23 and N = 253:
  For all s in Class B: Lambda(s, pi/23, 253) = 0.0

RATIONALE: If Class B is the logical subspace, the fundamental non-Clifford
phase should preserve the basin. Any leakage would indicate that Class B is
not closed under the full engine dynamics.

H2 (Harmonic phase closure)
----------------------------
For theta = 2*pi/23 and N = 253:
  For all s in Class B: Lambda(s, 2*pi/23, 253) = 0.0

RATIONALE: The harmonic phase is a stronger test. If closure holds for both
the fundamental and harmonic phases, the property is structural, not accidental.

H3 (Class B maximizes closure)
-------------------------------
For theta = pi/23:
  Median Lambda(Class B) < Median Lambda(Class ACDE)

RATIONALE: Even if no class is perfectly closed, Class B should show the
minimum leakage. If another class (e.g., Class A) shows less leakage, then
Class B is not the natural logical subspace.

================================================================================
3. FALSIFICATION CRITERIA
================================================================================

Criterion    Description                              Trigger for Falsification
---------    -----------                              -------------------------
F1           Fundamental phase leaks from Class B     Exists s in Class B with
                                                      Lambda(s, pi/23, 253) > 0
F2           Harmonic phase leaks from Class B        Exists s in Class B with
                                                      Lambda(s, 2*pi/23, 253) > 0
F3           Another class is more closed             Median Lambda(Class B) >=
                                                      Median Lambda(any other class)

PASS CONDITION: F1, F2, and F3 all triggered.
FAIL CONDITION: Any of F1-F3 fails.

================================================================================
4. METHODOLOGY
================================================================================

STEP 1: Define phase operator
  Implement U_phase(theta) as a rotation in the (0, 23) plane.

STEP 2: Modified orbit computation
  For each phase theta in {pi/23, 2*pi/23}:
    For each start s in {0, ..., 23}:
      a. Initialize v = deep_hole(s)
      b. For t = 0, ..., 252:
           i.   Apply U_phase(theta) to v
           ii.  Record nearest deep hole
           iii. Apply standard Floquet tick T(t) to v
      c. Compute Lambda(s, theta, 253)

STEP 3: Closure analysis
  For each theta:
    a. Check if Lambda = 0 for all Class B starts (H1, H2)
    b. Compute median Lambda for each orbit class (H3)

STEP 4: Falsification evaluation
  Evaluate F1-F3 against computed data.

================================================================================
5. EXPECTED OUTCOMES
================================================================================

If Class B is the logical subspace:
  H1 passes: Lambda = 0 for all Class B starts at theta = pi/23
  H2 passes: Lambda = 0 for all Class B starts at theta = 2*pi/23
  H3 passes: Class B has strictly lower median leakage than all other classes
  F1-F3 all triggered

If Class B is not the logical subspace:
  H1 fails: At least one Class B start leaks under pi/23
  H2 fails: At least one Class B start leaks under 2*pi/23
  H3 fails: Another class (possibly Class A) shows less leakage
  At least one of F1-F3 fails

================================================================================
6. HONEST LIMITATIONS
================================================================================

1. The non-Clifford phase definition (rotation in the (0, 23) plane) is
   motivated by the structure of the engine but is not derived from first
   principles. Alternative phase definitions (e.g., rotation in other
   coordinate planes) are possible and would require separate tests.

2. The phase angles pi/23 and 2*pi/23 are chosen to resonate with the P23
   cycle order. There is no a priori guarantee that these are the "correct"
   non-Clifford angles for this system.

3. The test assumes that "logical subspace" means "closed under phase-modified
   Floquet evolution." This is a operational definition, not a proof of
   quantum error-correcting properties.

4. If H1 fails but H3 passes, the result is ambiguous: Class B may be the
   "most closed" subspace without being perfectly closed.

5. The test does not verify that the phase operator is physically realizable
   as a quantum gate. It is a mathematical test of closure, not an
   experimental feasibility study.

================================================================================
7. POST-EXECUTION ANALYSIS (Q1-Q5)
================================================================================

Q1: If H1 fails, which specific Class B start leaks, and to which class does
    it leak?

Q2: Does the leakage occur immediately (first few ticks) or after many ticks?
    This distinguishes between "boundary error" and "dynamical instability."

Q3: If H3 passes but H1/H2 fail, what is the quantitative difference in leakage
    between Class B and the next-best class?

Q4: How does the leakage depend on the phase angle? Is there a critical angle
    where closure transitions to leakage?

Q5: If Class B is not the logical subspace, is there a larger subset of holes
    (e.g., Class A union Class B) that is closed under the phase?

================================================================================
8. CONNECTION TO FRAMEWORK HISTORY
================================================================================

RC-135 builds on and tests:
  RC-134: The fixed-point anchor (DH23) and the rejection of the Degeneracy
          Hypothesis — RC-135 asks what the fixed point implies for the
          logical structure of the remaining orbits.
  RC-132: The Universal Local Arrow Hypothesis — RC-135 asks whether Class B
          is not just locally special but logically closed.
  RC-129: Locality correlations — RC-135 tests whether the local cluster
          property extends to closure under non-Clifford evolution.
  RC-117: Non-Clifford phase identification — RC-135 operationalizes the
          phase as a testable operator.

RC-135 differs from:
  RC-134: No drift or contamination analysis; pure closure test.
  RC-131: No entropy-flow test; focused on phase-modified dynamics.
  RC-128: No correlation analysis; focused on basin closure.

================================================================================
9. VERDICT CATEGORIES
================================================================================

PASS (Strong):    F1-F3 all triggered — Class B is the logical subspace,
                  closed under both fundamental and harmonic non-Clifford phases.

PASS (Partial):   F1 and F2 triggered, F3 fails — Class B is closed but not
                  uniquely so; another class is equally or more closed.

FAIL (Leaky):     F1 or F2 fails — Class B leaks under the non-Clifford phase.

FAIL (Ambiguous): H3 fails but H1/H2 pass — Closure holds but Class B is not
                  the maximally closed subspace.

================================================================================
END OF PRE-REGISTRATION
================================================================================
