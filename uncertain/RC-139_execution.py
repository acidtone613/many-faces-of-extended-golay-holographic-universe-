#!/usr/bin/env python3
"""
RC-139: The 24-Hole Fiber Bundle — Base Space Redefinition
Complete Execution Script
Framework: 24D-DMF v8.4.3
Date: 2026-07-09
Status: EXECUTED — Results Binding

This script reproduces the full RC-139 execution from the pre-registered protocol.
It tests whether the 24 deep holes themselves can serve as the base space of a
fiber bundle logical encoding.

Dependencies: numpy
Run: python3 RC-139_execution.py
"""

import numpy as np
from itertools import product
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("RC-139: THE 24-HOLE FIBER BUNDLE — Base Space Redefinition")
print("Framework: 24D-DMF v8.4.3 | Date: 2026-07-09")
print("Status: EXECUTING — Results Binding")
print("=" * 80)

# =============================================================================
# PART 1: FOUNDATION (from RC-136, RC-110, RC-126, RC-138)
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
# PART 2: UTILITY FUNCTIONS
# =============================================================================
print("\n[STEP 2] Defining utility functions...")

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

def fiber_angle(v):
    return np.arctan2(v[23], v[0])

def construct_section_state(phase_pattern):
    components = []
    for s in range(24):
        h = deep_hole(s)
        v = h.copy()
        r = np.sqrt(h[0]**2 + h[23]**2)
        v[0] = r * np.cos(phase_pattern[s])
        v[23] = r * np.sin(phase_pattern[s])
        components.append(v)
    return np.mean(components, axis=0)

print("  Utility functions defined.")

# =============================================================================
# PART 3: H1 — FLOQUET TICK PRESERVES ORBIT CLASSES
# =============================================================================
print("\n" + "=" * 80)
print("H1: 24-HOLE BASE IS PRESERVED BY FLOQUET")
print("=" * 80)

class_transition_counts = defaultdict(lambda: defaultdict(int))
floquet_permutations = {}

for cls_name, holes in orbit_classes.items():
    perm = {}
    for s in holes:
        h = deep_hole(s)
        h_after = apply_tick_vector(h, 0)
        s_after, dist = nearest_deep_hole(h_after)
        perm[s] = s_after
        cls_after = None
        for c, hs in orbit_classes.items():
            if s_after in hs:
                cls_after = c
                break
        class_transition_counts[cls_name][cls_after] += 1
    floquet_permutations[cls_name] = perm

print("\n  Class Transition Matrix (rows = after, cols = before):")
print("         " + "  ".join([f"{c:>3}" for c in ['A', 'B', 'C', 'D', 'E']]))
for cls_after in ['A', 'B', 'C', 'D', 'E']:
    row = "  ".join([f"{class_transition_counts[cls_after][cls_before]:>3}" for cls_before in ['A', 'B', 'C', 'D', 'E']])
    print(f"  {cls_after}:     {row}")

h1_pass = True
cross_class_found = []
for cls_before in ['A', 'B', 'C', 'D', 'E']:
    for cls_after in ['A', 'B', 'C', 'D', 'E']:
        if cls_before != cls_after and class_transition_counts[cls_after][cls_before] > 0:
            h1_pass = False
            cross_class_found.append((cls_before, cls_after, class_transition_counts[cls_after][cls_before]))

if cross_class_found:
    print(f"\n  CROSS-CLASS TRANSITIONS FOUND:")
    for before, after, count in cross_class_found:
        print(f"    {before} -> {after}: {count} transitions")
else:
    print(f"\n  NO cross-class transitions detected.")

print(f"\n  H1 VERDICT: {'PASS' if h1_pass else 'FAIL'}")

# =============================================================================
# PART 4: H2 — U_θ PRESERVES NEAREST DEEP HOLE
# =============================================================================
print("\n" + "=" * 80)
print("H2: U_θ PRESERVES NEAREST DEEP HOLE IDENTITY")
print("=" * 80)

small_thetas = [0.01, 0.05, 0.1, 0.2, np.pi/23]

h2_results = {}
for theta in small_thetas:
    failures = []
    for s in range(24):
        h = deep_hole(s)
        h_rot = U_phase(h, theta)
        s_after, dist = nearest_deep_hole(h_rot)
        if s_after != s:
            failures.append((s, s_after))
    h2_results[theta] = failures
    status = "PASS" if not failures else f"FAIL ({len(failures)} cases)"
    print(f"  θ={theta:.4f} ({theta/np.pi:.4f}π): {status}")

theta_natural = np.pi / 23
h2_pass = len(h2_results[theta_natural]) == 0
print(f"\n  H2 (θ=π/23): {'PASS' if h2_pass else 'FAIL'}")

# =============================================================================
# PART 5: H3 — UNIFORM PHASE ROTATION
# =============================================================================
print("\n" + "=" * 80)
print("H3: UNIFORM PHASE ROTATION ON 24-HOLE BASE")
print("=" * 80)

theta_test = np.pi / 23
h3_pass = True
h3_errors = []

for s in range(24):
    h = deep_hole(s)
    phi_before = fiber_angle(h)
    h_rot = U_phase(h, theta_test)
    phi_after = fiber_angle(h_rot)
    phase_shift = phi_after - phi_before
    while phase_shift > np.pi:
        phase_shift -= 2*np.pi
    while phase_shift < -np.pi:
        phase_shift += 2*np.pi
    error = abs(phase_shift - theta_test)
    error = min(error, abs(phase_shift - theta_test + 2*np.pi), abs(phase_shift - theta_test - 2*np.pi))
    if error > 1e-6:
        h3_pass = False
        h3_errors.append((s, phi_before, phi_after, phase_shift, error))

if h3_errors:
    print(f"\n  FAILURES ({len(h3_errors)} cases):")
    for s, pb, pa, ps, err in h3_errors[:10]:
        print(f"    DH{s:02d}: shift={ps:.8f}, error={err:.2e}")
else:
    print("\n  PASS: Phase shift = θ ± 10⁻⁶ for all deep holes")

print(f"\n  H3 VERDICT: {'PASS' if h3_pass else 'FAIL'}")

# =============================================================================
# PART 6: H4 — LOGICAL QUBIT ENCODING
# =============================================================================
print("\n" + "=" * 80)
print("H4: LOGICAL QUBIT ENCODING ON 24-HOLE BASE")
print("=" * 80)

phi_0 = np.zeros(24)
phi_1 = np.array([0 if s % 2 == 0 else np.pi for s in range(24)])

psi_0 = construct_section_state(phi_0)
psi_1 = construct_section_state(phi_1)

psi_0_n = psi_0 / np.linalg.norm(psi_0)
psi_1_n = psi_1 / np.linalg.norm(psi_1)

print("\n  Testing U_θ action on sections...")
theta = np.pi / 7

phi_0_shifted = phi_0 + theta
phi_1_shifted = phi_1 + theta
psi_0_expected = construct_section_state(phi_0_shifted)
psi_1_expected = construct_section_state(phi_1_shifted)
psi_0_exp_n = psi_0_expected / np.linalg.norm(psi_0_expected)
psi_1_exp_n = psi_1_expected / np.linalg.norm(psi_1_expected)

psi_0_direct_rot = U_phase(psi_0, theta)
psi_1_direct_rot = U_phase(psi_1, theta)
psi_0_direct_rot_n = psi_0_direct_rot / np.linalg.norm(psi_0_direct_rot)
psi_1_direct_rot_n = psi_1_direct_rot / np.linalg.norm(psi_1_direct_rot)

overlap_0 = abs(np.dot(psi_0_direct_rot_n, psi_0_exp_n))
overlap_1 = abs(np.dot(psi_1_direct_rot_n, psi_1_exp_n))

print(f"  |0_L> rotation fidelity: {overlap_0:.6f}")
print(f"  |1_L> rotation fidelity: {overlap_1:.6f}")

print("\n  Testing Floquet action on sections...")
full_perm = {}
for s in range(24):
    h = deep_hole(s)
    h_after = apply_tick_vector(h, 0)
    s_after, _ = nearest_deep_hole(h_after)
    full_perm[s] = s_after

inv_perm = {v: k for k, v in full_perm.items()}

phi_0_floquet = np.zeros(24)
for s in range(24):
    phi_0_floquet[s] = phi_0[inv_perm[s]]

phi_1_floquet = np.zeros(24)
for s in range(24):
    phi_1_floquet[s] = phi_1[inv_perm[s]]

psi_0_floquet = construct_section_state(phi_0_floquet)
psi_1_floquet = construct_section_state(phi_1_floquet)
psi_0_floquet_n = psi_0_floquet / np.linalg.norm(psi_0_floquet)
psi_1_floquet_n = psi_1_floquet / np.linalg.norm(psi_1_floquet)

overlap_0_f = abs(np.dot(psi_0_floquet_n, psi_0_n))
overlap_1_f = abs(np.dot(psi_1_floquet_n, psi_1_n))

print(f"  |0_L> Floquet overlap: {overlap_0_f:.6f}")
print(f"  |1_L> Floquet overlap: {overlap_1_f:.6f}")

# Check if Floquet(|1_L>) is in logical subspace
A = np.column_stack([psi_0_n, psi_1_n])
coeffs, residuals, rank, s_vals = np.linalg.lstsq(A, psi_1_floquet_n, rcond=None)
reconstruction_error = np.linalg.norm(coeffs[0] * psi_0_n + coeffs[1] * psi_1_n - psi_1_floquet_n)
print(f"  |1_L> Floquet reconstruction in logical subspace: {reconstruction_error:.2e}")

h4_pass = overlap_0 > 0.99 and overlap_1 > 0.99
print(f"\n  H4 VERDICT: {'PASS' if h4_pass else 'FAIL'}")

# =============================================================================
# PART 7: H5 — ORBIT-CLASS SUB-BUNDLE STRUCTURE
# =============================================================================
print("\n" + "=" * 80)
print("H5: ORBIT-CLASS SUB-BUNDLE STRUCTURE")
print("=" * 80)

for cls_name, holes in orbit_classes.items():
    perm = floquet_permutations[cls_name]
    visited = set()
    cycles = []
    for s in holes:
        if s in visited:
            continue
        cycle = []
        current = s
        while current not in visited and current in holes:
            visited.add(current)
            cycle.append(current)
            current = perm[current]
            if current not in holes:
                break
        if len(cycle) > 0:
            cycles.append(cycle)

    print(f"\n  Class {cls_name} ({len(holes)} holes):")
    print(f"    Cycle decomposition: {cycles}")
    is_single_cycle = len(cycles) == 1 and len(cycles[0]) == len(holes)
    print(f"    Single cycle: {is_single_cycle}")

h5_pass = True
for cls_name, holes in orbit_classes.items():
    perm = floquet_permutations[cls_name]
    maps_within = all(perm[s] in holes for s in holes)
    if not maps_within:
        h5_pass = False
        print(f"\n  Class {cls_name}: Floquet maps outside class!")

print(f"\n  H5 VERDICT: {'PASS' if h5_pass else 'FAIL'}")

# =============================================================================
# PART 8: FINAL VERDICT
# =============================================================================
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

print(f"\n  C1 (Floquet preserves orbit classes):     {'PASS' if h1_pass else 'FAIL'}")
print(f"  C2 (U_θ preserves nearest deep hole):     {'PASS' if h2_pass else 'FAIL'}")
print(f"  C3 (Uniform phase rotation):              {'PASS' if h3_pass else 'FAIL'}")
print(f"  C4 (Logical qubit encoding):              {'PASS' if h4_pass else 'FAIL'}")
print(f"  C5 (Orbit-class sub-bundles):             {'PASS' if h5_pass else 'FAIL'}")

c123_pass = h1_pass and h2_pass and h3_pass

if c123_pass and h4_pass:
    verdict = "PASS (Strong)"
elif c123_pass and not h4_pass and h5_pass:
    verdict = "PASS (Partial)"
elif not h1_pass or not h2_pass:
    verdict = "FAIL"
elif h1_pass and h2_pass and not h3_pass:
    verdict = "FAIL"
else:
    verdict = "MIXED"

print(f"\n  OVERALL VERDICT: {verdict}")

print("\n" + "=" * 80)
print("RC-139 EXECUTION COMPLETE")
print("=" * 80)
print("\nThe computation is finite, exact, and target-blind.")
print("No 727/726, no epsilon, no fitted parameters were used.")
print("\n24D-DMF Framework | RC-139 Execution Report | Target-Blind | Firewall Active")
print("=" * 80)
