#!/usr/bin/env python3
"""
RC-138: The Fiber Bundle Logical Encoding — Complete Execution Script
Framework: 24D-DMF v8.4.3
Date: 2026-07-09
Status: EXECUTED — Results Binding

This script reproduces the full RC-138 execution from the pre-registered protocol.
It tests whether the 6-axis 5-fold structure supports a fiber bundle logical encoding.

Dependencies: numpy
Run: python3 RC-138_execution.py
"""

import numpy as np
from itertools import product
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("RC-138: THE FIBER BUNDLE LOGICAL ENCODING")
print("Framework: 24D-DMF v8.4.3 | Date: 2026-07-09")
print("Status: EXECUTING — Results Binding")
print("=" * 80)

# =============================================================================
# PART 1: FOUNDATION (from RC-136, RC-110, RC-126)
# =============================================================================
print("\n[STEP 1] Building framework foundation...")

# --- Golay Code G24 ---
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
print(f"  G24 codewords: {len(code_words)}")

# --- Quaternion 24-Cell ---
quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)
print(f"  Quaternion 24-cell: {len(quaternions_24)} vertices")

# --- Hopf Fibration ---
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

# --- Deep Holes ---
def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

# --- Floquet Tick ---
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

# --- Phase Operator ---
def U_phase(v, theta):
    v_new = v.copy()
    v0, v23 = v[0], v[23]
    v_new[0]  = np.cos(theta) * v0 - np.sin(theta) * v23
    v_new[23] = np.sin(theta) * v0 + np.cos(theta) * v23
    return v_new

# --- Orbit Classes (from RC-126) ---
orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}

print("  Foundation loaded successfully.")

# =============================================================================
# PART 2: CONSTRUCT THE 6-AXIS BASE
# =============================================================================
print("\n[STEP 2] Constructing the 6-axis base from 3D projections...")

projections_3d = np.zeros((24, 3))
for s in range(24):
    projections_3d[s] = project_to_3d(deep_hole(s))

norms = np.linalg.norm(projections_3d, axis=1)
projections_3d_norm = projections_3d.copy()
for i in range(24):
    if norms[i] > 1e-10:
        projections_3d_norm[i] = projections_3d[i] / norms[i]

# Cluster by unique 3D direction (grouping antipodal together)
tolerance = 1e-6
unique_directions = []
axis_map = {}

for s in range(24):
    if s in axis_map:
        continue
    axis_members = [s]
    for t in range(24):
        if t == s or t in axis_map:
            continue
        dot = np.dot(projections_3d_norm[s], projections_3d_norm[t])
        if abs(abs(dot) - 1) < tolerance:
            axis_members.append(t)
    axis_idx = len(unique_directions)
    for member in axis_members:
        axis_map[member] = axis_idx
    unique_directions.append(axis_members)

axes = {i: unique_directions[i] for i in range(len(unique_directions))}
print(f"  Found {len(axes)} unique axes:")
for i, members in enumerate(unique_directions):
    print(f"    Axis {i}: DHs {members}")

def axis_assignment(s):
    for axis_idx, members in axes.items():
        if s in members:
            return axis_idx
    return None

# Verify each deep hole has an axis
for s in range(24):
    assert axis_assignment(s) is not None

# =============================================================================
# PART 3: AXIS ASSIGNMENT FUNCTION
# =============================================================================
print("\n[STEP 3] Defining axis assignment function A(v)...")

def nearest_deep_hole(v):
    best_dist = float('inf')
    best_s = -1
    for s in range(24):
        h = deep_hole(s)
        dist = np.linalg.norm(v - h)
        if dist < best_dist:
            best_dist = dist
            best_s = s
    return best_s, best_dist

def axis_of_state(v):
    s_nearest, _ = nearest_deep_hole(v)
    return axis_assignment(s_nearest)

# Verify consistency for deep holes
all_match = True
for s in range(24):
    if axis_of_state(deep_hole(s)) != axis_assignment(s):
        all_match = False
print(f"  Deep hole axis consistency: {'PASS' if all_match else 'FAIL'}")

# =============================================================================
# PART 4: H1 — AXIS PRESERVATION UNDER FLOQUET
# =============================================================================
print("\n" + "=" * 80)
print("H1: AXIS PRESERVATION UNDER FLOQUET DYNAMICS")
print("=" * 80)

axis_transition_counts = np.zeros((6, 6), dtype=int)
for s in range(24):
    a_before = axis_assignment(s)
    h = deep_hole(s)
    h_after = apply_tick_vector(h, 0)
    a_after = axis_of_state(h_after)
    axis_transition_counts[a_after, a_before] += 1

print("\n  Axis Transition Matrix (rows = after, cols = before):")
print("         " + "  ".join([f"A{a}" for a in range(6)]))
for a_after in range(6):
    row = "  ".join([f"{axis_transition_counts[a_after, a_before]:2d}" for a_before in range(6)])
    print(f"  A{a_after}:  {row}")

def floquet_axis_map(a_before):
    targets = set()
    for s in axes[a_before]:
        h = deep_hole(s)
        h_after = apply_tick_vector(h, 0)
        a_after = axis_of_state(h_after)
        targets.add(a_after)
    return targets

print("\n  Axis-to-axis mapping under Floquet tick (t=0):")
for a in range(6):
    targets = floquet_axis_map(a)
    if len(targets) == 1:
        print(f"    Axis {a} -> Axis {list(targets)[0]}  (deterministic)")
    else:
        print(f"    Axis {a} -> {targets}  (NON-DETERMINISTIC)")

all_deterministic = all(len(floquet_axis_map(a)) == 1 for a in range(6))
if all_deterministic:
    permutation = [list(floquet_axis_map(a))[0] for a in range(6)]
    is_bijection = len(set(permutation)) == 6
    h1_pass = is_bijection
    print(f"\n  Permutation: {permutation}")
    print(f"  Is bijection: {is_bijection}")
else:
    h1_pass = False
    print(f"\n  Mapping is NOT deterministic — cannot be a permutation")

print(f"\n  H1 VERDICT: {'PASS' if h1_pass else 'FAIL'}")

# =============================================================================
# PART 5: H2 — SECTION PRESERVATION BY U_θ
# =============================================================================
print("\n" + "=" * 80)
print("H2: SECTION PRESERVATION BY U_θ")
print("=" * 80)

def fiber_angle(v):
    return np.arctan2(v[23], v[0])

def construct_state_on_axis(a, phi, epsilon=0.01):
    members = axes[a]
    v = np.zeros(24)
    for s in members:
        v += deep_hole(s)
    v = v / len(members)
    current_phi = fiber_angle(v)
    delta = phi - current_phi
    v = U_phase(v, delta)
    return v

theta_test = np.pi / 7
phases_to_test = [0, np.pi/6, np.pi/4, np.pi/3, np.pi/2, 2*np.pi/3, np.pi]

h2_pass = True
h2_failures = []
for a in range(6):
    for phi in phases_to_test:
        v = construct_state_on_axis(a, phi)
        a_before = axis_of_state(v)
        v_rot = U_phase(v, theta_test)
        a_after = axis_of_state(v_rot)
        if a_after != a_before:
            h2_failures.append((a, phi, a_before, a_after))
            h2_pass = False

if h2_failures:
    print(f"\n  FAILURES ({len(h2_failures)} cases):")
    for a, phi, a_b, a_a in h2_failures[:10]:
        print(f"    Axis {a}, φ={phi:.4f}: {a_b} -> {a_a}")
else:
    print("\n  PASS: U_θ preserves axis for all tested phases")

print(f"\n  H2 VERDICT: {'PASS' if h2_pass else 'FAIL'}")

# =============================================================================
# PART 6: H3 — UNIFORM PHASE ROTATION
# =============================================================================
print("\n" + "=" * 80)
print("H3: UNIFORM PHASE ROTATION")
print("=" * 80)

def fiber_displacement(v, s):
    phi_v = fiber_angle(v)
    h_s = deep_hole(s)
    phi_hs = fiber_angle(h_s)
    delta = phi_v - phi_hs
    while delta > np.pi:
        delta -= 2*np.pi
    while delta < -np.pi:
        delta += 2*np.pi
    return delta

h3_pass = True
h3_errors = []
for a in range(6):
    for phi in phases_to_test:
        for s in axes[a]:
            v = construct_state_on_axis(a, phi)
            delta_before = fiber_displacement(v, s)
            v_rot = U_phase(v, theta_test)
            delta_after = fiber_displacement(v_rot, s)
            phase_shift = delta_after - delta_before
            while phase_shift > np.pi:
                phase_shift -= 2*np.pi
            while phase_shift < -np.pi:
                phase_shift += 2*np.pi
            error = abs(phase_shift - theta_test)
            error = min(error, abs(phase_shift - theta_test + 2*np.pi), abs(phase_shift - theta_test - 2*np.pi))
            if error > 1e-6:
                h3_pass = False
                h3_errors.append((a, phi, s, phase_shift, error))

if h3_errors:
    print(f"\n  FAILURES ({len(h3_errors)} cases):")
    for a, phi, s, shift, err in h3_errors[:10]:
        print(f"    Axis {a}, φ={phi:.4f}, ref=DH{s:02d}: shift={shift:.8f}, error={err:.2e}")
else:
    print("\n  PASS: Phase shift = θ ± 10⁻⁶ for all axes and phases")

print(f"\n  H3 VERDICT: {'PASS' if h3_pass else 'FAIL'}")

# =============================================================================
# PART 7: H4 — BASE ERROR CORRECTION
# =============================================================================
print("\n" + "=" * 80)
print("H4: BASE ERROR CORRECTION")
print("=" * 80)

np.random.seed(138)
N_ticks = 22
noise_levels = [0.01, 0.05, 0.1, 0.2]
n_trials = 1000

h4_results = {}
for sigma in noise_levels:
    success_count = 0
    for trial in range(n_trials):
        s = np.random.randint(24)
        a_original = axis_assignment(s)
        v = deep_hole(s).copy()
        noise = np.random.randn(24) * sigma
        noise[0] = 0
        noise[23] = 0
        v = v + noise
        for t in range(N_ticks):
            v = apply_tick_vector(v, t)
        a_final = axis_of_state(v)
        if a_final == a_original:
            success_count += 1
    prob = success_count / n_trials
    h4_results[sigma] = prob
    print(f"    σ = {sigma:.2f}: {success_count}/{n_trials} = {prob:.4f}")

h4_pass = h4_results[0.01] > 0.99
print(f"\n  H4 criterion (σ=0.01, p>0.99): {'PASS' if h4_pass else 'FAIL'}")
print(f"  H4 VERDICT: {'PASS' if h4_pass else 'FAIL'}")

# =============================================================================
# PART 8: FINAL VERDICT
# =============================================================================
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

print(f"\n  C1 (Axis permutation):     {'PASS' if h1_pass else 'FAIL'}")
print(f"  C2 (U_θ preserves axis):   {'PASS' if h2_pass else 'FAIL'}")
print(f"  C3 (Uniform phase):        {'PASS' if h3_pass else 'FAIL'}")
print(f"  C4 (Base error correction): {'PASS' if h4_pass else 'FAIL'}")

if h1_pass and h2_pass and h3_pass and h4_pass:
    verdict = "PASS (Strong)"
elif h1_pass and h2_pass and (h3_pass or h4_pass):
    verdict = "PASS (Partial)"
elif not h1_pass or not h2_pass:
    verdict = "FAIL"
else:
    verdict = "MIXED"

print(f"\n  OVERALL VERDICT: {verdict}")

print("\n" + "=" * 80)
print("RC-138 EXECUTION COMPLETE")
print("=" * 80)
print("\nThe computation is finite, exact, and target-blind.")
print("No 727/726, no epsilon, no fitted parameters were used.")
print("\n24D-DMF Framework | RC-138 Execution Report | Target-Blind | Firewall Active")
print("=" * 80)
