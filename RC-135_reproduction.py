#!/usr/bin/env python3
"""
RC-135: The Logical Core — Is Class B Closed Under the Non-Clifford Phase?
Reproduction Script
Framework: 24D-DMF v8.4.3
Date: 2026-07-08

This script reproduces the full RC-135 execution from the pre-registered protocol.
It tests whether Class B deep holes are closed under the non-Clifford phase
operator U_phase(theta) composed with the standard Floquet tick T(t).

Dependencies: numpy, scipy
Run: python3 RC-135_reproduction.py
"""

import numpy as np
from scipy.stats import pearsonr
from itertools import permutations, product, combinations
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("RC-135: THE LOGICAL CORE — Is Class B Closed Under the Non-Clifford Phase?")
print("Framework: 24D-DMF v8.4.3 | Date: 2026-07-08")
print("Status: EXECUTING — Results Binding")
print("=" * 80)

# =============================================================================
# PART 1: GOLAY CODE G24 (Cyclic Basis)
# =============================================================================
print("\n[STEP 1] Building Golay code G24...")
g = np.array([1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1] + [0]*11, dtype=int)
G23 = np.zeros((12, 23), dtype=int)
for i in range(12):
    for j in range(23):
        G23[i, j] = g[(j - i) % 23]
G24 = np.zeros((12, 24), dtype=int)
G24[:, :23] = G23
G24[:, 23] = np.sum(G23, axis=1) % 2

code_words = np.zeros((4096, 24), dtype=np.uint8)
for bits in range(4096):
    coeffs = np.array([(bits >> i) & 1 for i in range(12)], dtype=np.uint8)
    code_words[bits] = (coeffs @ G24) % 2
code_set = set(map(tuple, code_words))
print(f"  Codewords: {len(code_words)}")

# =============================================================================
# PART 2: QUATERNION 24-CELL
# =============================================================================
print("\n[STEP 2] Building quaternion 24-cell...")
quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)
print(f"  Total quaternions: {len(quaternions_24)}")

# =============================================================================
# PART 3: HOPF FIBRATION AND PROJECTION PIPELINE
# =============================================================================
print("\n[STEP 3] Building Hopf fibration and projections...")

def quat_mul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])

def quat_conj(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])

def hopf(q, p=np.array([0, 1, 0, 0])):
    r = quat_mul(quat_mul(q, p), quat_conj(q))
    return r[1:]

phi = (1 + np.sqrt(5)) / 2
axis_5fold = np.array([0, 1, phi])
axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
e1_s = e1_s / np.linalg.norm(e1_s)
e2_s = np.cross(axis_5fold, e1_s)
e2_s = e2_s / np.linalg.norm(e2_s)

def project_to_3d(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))):
        q += v[0, i] * quaternions_24[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
    p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])
    v3 = hopf(q, p_golden)
    norm3 = np.linalg.norm(v3)
    if norm3 > 1e-10:
        v3 = v3 / norm3
    return v3

def full_projection_quaternion(v_24d):
    v3 = project_to_3d(v_24d)
    v2 = np.array([v3 @ e1_s, v3 @ e2_s])
    return v2

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

def get_color(v):
    v2 = full_projection_quaternion(v)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    return angle_to_color(theta)

# =============================================================================
# PART 4: DEEP HOLES AND FLOQUET TICK
# =============================================================================
print("\n[STEP 4] Defining deep holes and Floquet tick...")

def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

def P23_on_vector(v):
    v_new = np.zeros_like(v)
    v_new[0] = v[22]
    v_new[1:23] = v[0:22]
    v_new[23] = v[23]
    return v_new

inv2 = 12
def P11_on_vector(v):
    v_new = np.zeros_like(v)
    for j in range(23):
        v_new[j] = v[(inv2 * j) % 23]
    v_new[23] = v[23]
    return v_new

def H_L_on_vector(v):
    v_new = np.zeros_like(v)
    v_new[0] = v[0]
    v_new[23] = v[23]
    for j in range(1, 23):
        for inv in range(1, 23):
            if (j * inv) % 23 == 1:
                j_prime = (-inv) % 23
                v_new[j] = v[j_prime]
                break
    return v_new

def apply_tick_vector(v, t):
    v = P23_on_vector(v)
    v = P11_on_vector(v)
    if t % 11 == 0:
        v = H_L_on_vector(v)
    return v

# =============================================================================
# PART 5: NON-CLIFFORD PHASE OPERATOR
# =============================================================================
print("\n[STEP 5] Defining non-Clifford phase operator...")

def U_phase(v, theta):
    """Rotation in the (0, 23) plane by angle theta."""
    v_new = v.copy()
    v0, v23 = v[0], v[23]
    v_new[0]  = np.cos(theta) * v0 - np.sin(theta) * v23
    v_new[23] = np.sin(theta) * v0 + np.cos(theta) * v23
    return v_new

theta_1 = np.pi / 23
theta_2 = 2 * np.pi / 23
print(f"  theta_1 = pi/23  = {theta_1:.8f}")
print(f"  theta_2 = 2*pi/23 = {theta_2:.8f}")

# =============================================================================
# PART 6: ORBIT CLASSES
# =============================================================================
print("\n[STEP 6] Orbit class definitions...")
orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}
Union_B = set(orbit_classes['B'])

for name, holes in orbit_classes.items():
    print(f"  Class {name}: {holes}")
print(f"\n  Union_B = {sorted(Union_B)}")

# =============================================================================
# PART 7: NEAREST DEEP HOLE FUNCTION
# =============================================================================
print("\n[STEP 7] Precomputing deep hole templates...")
deep_hole_templates = np.array([deep_hole(i) for i in range(24)])

def nearest_deep_hole(v):
    """Find index of closest deep hole template to v."""
    min_dist = float('inf')
    closest_idx = -1
    for i in range(24):
        dist = np.linalg.norm(v - deep_hole_templates[i])
        if dist < min_dist:
            min_dist = dist
            closest_idx = i
    return closest_idx, min_dist

# =============================================================================
# PART 8: MODIFIED ORBIT COMPUTATION
# =============================================================================
print("\n" + "=" * 80)
print("STEP 8: COMPUTING PHASE-MODIFIED ORBITS")
print("=" * 80)

N = 253  # Full engine period

def compute_phase_orbit(start_s, theta, N_ticks):
    """
    Compute orbit under T_phase(t, theta) = T(t) o U_phase(theta).
    Order: U_phase(theta) first, then standard Floquet tick.
    """
    v = deep_hole(start_s).copy()
    nearest_seq = []
    for t in range(N_ticks):
        v = U_phase(v, theta)
        nh, _ = nearest_deep_hole(v)
        nearest_seq.append(nh)
        if t < N_ticks - 1:
            v = apply_tick_vector(v, t)
    return nearest_seq

def compute_lambda(start_s, theta, N_ticks):
    """Compute leakage score Lambda(s, theta, N)."""
    nearest_seq = compute_phase_orbit(start_s, theta, N_ticks)
    leak_count = sum(1 for nh in nearest_seq if nh not in Union_B)
    return leak_count / N_ticks

print("\n  Computing orbits for theta = pi/23...")
results_theta1 = {}
for s in range(24):
    lam = compute_lambda(s, theta_1, N)
    nearest_seq = compute_phase_orbit(s, theta_1, N)
    results_theta1[s] = {
        'lambda': lam,
        'nearest_seq': nearest_seq,
        'unique_visited': sorted(set(nearest_seq))
    }
    if s % 4 == 0 or s in Union_B:
        print(f"    DH{s:02d}: Lambda = {lam:.6f}, visited = {results_theta1[s]['unique_visited']}")

print("\n  Computing orbits for theta = 2*pi/23...")
results_theta2 = {}
for s in range(24):
    lam = compute_lambda(s, theta_2, N)
    nearest_seq = compute_phase_orbit(s, theta_2, N)
    results_theta2[s] = {
        'lambda': lam,
        'nearest_seq': nearest_seq,
        'unique_visited': sorted(set(nearest_seq))
    }
    if s % 4 == 0 or s in Union_B:
        print(f"    DH{s:02d}: Lambda = {lam:.6f}, visited = {results_theta2[s]['unique_visited']}")

# =============================================================================
# PART 9: HYPOTHESIS AND FALSIFICATION EVALUATION
# =============================================================================
print("\n" + "=" * 80)
print("STEP 9: EVALUATING PRE-REGISTERED HYPOTHESES AND FALSIFICATION CRITERIA")
print("=" * 80)

# --- H1: Fundamental phase closure ---
print("\n--- H1: Fundamental Phase Closure (theta = pi/23) ---")
h1_pass = True
for s in orbit_classes['B']:
    lam = results_theta1[s]['lambda']
    status = 'PASS' if lam == 0.0 else 'FAIL'
    if lam > 0:
        h1_pass = False
    print(f"  DH{s:02d}: Lambda = {lam:.6f}  [{status}]")
print(f"\n  H1 VERDICT: {'PASS' if h1_pass else 'FAIL'}")

# --- H2: Harmonic phase closure ---
print("\n--- H2: Harmonic Phase Closure (theta = 2*pi/23) ---")
h2_pass = True
for s in orbit_classes['B']:
    lam = results_theta2[s]['lambda']
    status = 'PASS' if lam == 0.0 else 'FAIL'
    if lam > 0:
        h2_pass = False
    print(f"  DH{s:02d}: Lambda = {lam:.6f}  [{status}]")
print(f"\n  H2 VERDICT: {'PASS' if h2_pass else 'FAIL'}")

# --- H3: Class B maximizes closure ---
print("\n--- H3: Class B Maximizes Closure ---")
class_medians = {}
for cls_name, holes in orbit_classes.items():
    lambdas_t1 = [results_theta1[s]['lambda'] for s in holes]
    lambdas_t2 = [results_theta2[s]['lambda'] for s in holes]
    median_t1 = np.median(lambdas_t1)
    median_t2 = np.median(lambdas_t2)
    class_medians[cls_name] = {'t1': median_t1, 't2': median_t2}
    print(f"  Class {cls_name}: median Lambda (pi/23) = {median_t1:.6f}, median Lambda (2pi/23) = {median_t2:.6f}")

median_B_t1 = class_medians['B']['t1']
median_B_t2 = class_medians['B']['t2']
other_classes = ['A', 'C', 'D', 'E']
h3_t1_pass = all(median_B_t1 < class_medians[c]['t1'] for c in other_classes)
h3_t2_pass = all(median_B_t2 < class_medians[c]['t2'] for c in other_classes)
h3_pass = h3_t1_pass and h3_t2_pass
print(f"\n  H3 VERDICT: {'PASS' if h3_pass else 'FAIL'}")

# =============================================================================
# PART 10: FALSIFICATION CRITERIA
# =============================================================================
print("\n" + "-" * 60)
print("FALSIFICATION CRITERIA")
print("-" * 60)

f1_triggered = not h1_pass
print(f"\nF1 (Fundamental phase leaks from Class B): {'TRIGGERED' if f1_triggered else 'NOT TRIGGERED'}")

f2_triggered = not h2_pass
print(f"F2 (Harmonic phase leaks from Class B): {'TRIGGERED' if f2_triggered else 'NOT TRIGGERED'}")

f3_triggered = not h3_pass
print(f"F3 (Another class is more closed): {'TRIGGERED' if f3_triggered else 'NOT TRIGGERED'}")

# =============================================================================
# PART 11: VERDICT CATEGORIES
# =============================================================================
print("\n" + "=" * 80)
print("PRE-REGISTERED VERDICT CATEGORIES")
print("=" * 80)
print(f"\n  F1: {'TRIGGERED' if f1_triggered else 'NOT TRIGGERED'}")
print(f"  F2: {'TRIGGERED' if f2_triggered else 'NOT TRIGGERED'}")
print(f"  F3: {'TRIGGERED' if f3_triggered else 'NOT TRIGGERED'}")

all_triggered = f1_triggered and f2_triggered and f3_triggered
none_triggered = not f1_triggered and not f2_triggered and not f3_triggered

print(f"\n  PASS (Strong):   {'YES' if none_triggered else 'NO'}")
print(f"  FAIL (Leaky):    {'YES' if (f1_triggered or f2_triggered) else 'NO'}")
print(f"  FAIL (Ambiguous):{'YES' if (not f1_triggered and not f2_triggered and f3_triggered) else 'NO'}")

if all_triggered:
    print(f"\n  OVERALL VERDICT: FAIL (Leaky) — All falsification criteria triggered")
elif none_triggered:
    print(f"\n  OVERALL VERDICT: PASS (Strong) — Class B is the logical subspace")
else:
    print(f"\n  OVERALL VERDICT: MIXED — See individual criteria above")

# =============================================================================
# PART 12: COMPLETE RESULTS TABLE
# =============================================================================
print("\n" + "=" * 80)
print("STEP 12: COMPLETE RESULTS TABLE")
print("=" * 80)
print(f"\n{'Hole':>4} | {'Class':>5} | {'Lambda(pi/23)':>13} | {'Lambda(2pi/23)':>14} | {'Non-B visited':>30}")
print("-" * 80)
for s in range(24):
    cls = '?'
    for c, holes in orbit_classes.items():
        if s in holes:
            cls = c
            break
    lam1 = results_theta1[s]['lambda']
    lam2 = results_theta2[s]['lambda']
    non_B_unique = sorted(set(nh for nh in results_theta1[s]['nearest_seq'] if nh not in Union_B))
    non_B_str = str(non_B_unique) if non_B_unique else 'None'
    print(f"{s:4d} | {cls:>5} | {lam1:13.6f} | {lam2:14.6f} | {non_B_str:>30}")

# =============================================================================
# PART 13: POST-EXECUTION ANALYSIS (Q1-Q5)
# =============================================================================
print("\n" + "=" * 80)
print("STEP 13: POST-EXECUTION ANALYSIS (Q1-Q5)")
print("=" * 80)

print("\n--- Q1: Leakage Targets for Class B Starts ---")
for s in orbit_classes['B']:
    seq = results_theta1[s]['nearest_seq']
    non_B = [nh for nh in seq if nh not in Union_B]
    non_B_unique = sorted(set(non_B))
    targets = {'A': [], 'C': [], 'D': [], 'E': []}
    for nh in non_B_unique:
        for cls_name, holes in orbit_classes.items():
            if nh in holes:
                targets[cls_name].append(nh)
                break
    print(f"  DH{s:02d}: leaks to {non_B_unique}")
    for cls_name, holes in targets.items():
        if holes:
            print(f"    -> Class {cls_name}: {holes}")

print("\n--- Q2: Leakage Timing ---")
for s in orbit_classes['B']:
    seq = results_theta1[s]['nearest_seq']
    first_leak_tick = None
    for t, nh in enumerate(seq):
        if nh not in Union_B:
            first_leak_tick = t
            break
    print(f"  DH{s:02d}: first leak at tick {first_leak_tick}")

print("\n--- Q3: Quantitative Leakage Comparison ---")
all_lambdas_t1 = {s: results_theta1[s]['lambda'] for s in range(24)}
all_lambdas_t2 = {s: results_theta2[s]['lambda'] for s in range(24)}
for cls_name, holes in orbit_classes.items():
    vals_t1 = [all_lambdas_t1[s] for s in holes]
    vals_t2 = [all_lambdas_t2[s] for s in holes]
    print(f"  Class {cls_name}: mean Lambda (pi/23) = {np.mean(vals_t1):.6f}, (2pi/23) = {np.mean(vals_t2):.6f}")

print("\n--- Q4: Critical Angle Analysis ---")
test_angles = np.linspace(0, np.pi/10, 21)
print(f"  Testing {len(test_angles)} angles from 0 to pi/10...")
sample_starts = [0, 4, 11]
for s in sample_starts:
    print(f"\n  DH{s:02d}:")
    for angle in test_angles:
        lam = compute_lambda(s, angle, N)
        print(f"    theta={angle:.6f}: Lambda={lam:.6f}")

print("\n--- Q5: Testing Larger Closed Subsets ---")
Union_AB = set(orbit_classes['A']) | set(orbit_classes['B'])
for s in Union_AB:
    lam = compute_lambda(s, theta_1, N)
print(f"  Class A U B (15 holes): Lambda range computed")

print("\n  Checking 2-hole subsets for closure...")
closed_pairs = []
for pair in combinations(range(24), 2):
    pair_set = set(pair)
    all_closed = True
    for s in pair:
        seq = results_theta1[s]['nearest_seq']
        if not all(nh in pair_set for nh in seq):
            all_closed = False
            break
    if all_closed:
        closed_pairs.append(pair)
if closed_pairs:
    print(f"    Closed pairs: {closed_pairs}")
else:
    print(f"    No closed pairs found.")

print("\n" + "=" * 80)
print("RC-135 EXECUTION COMPLETE")
print("=" * 80)
