#!/usr/bin/env python3
"""
RC-128: TIME-REVERSAL SYMMETRY TESTS — Three Alternative Hypotheses
Framework: 24D-DMF v8.4.3
Date: 2026-07-08
Status: EXECUTED — Results Binding

Reproduction script. Generates all tables, metrics, and visualizations.
Run: python3 RC-128_reproduction.py

Dependencies: numpy, matplotlib
"""

import numpy as np
from itertools import product
from math import log2
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
SEED = 128
np.random.seed(SEED)

print("=" * 80)
print("RC-128: TIME-REVERSAL SYMMETRY TESTS — Three Alternative Hypotheses")
print("Framework: 24D-DMF v8.4.3")
print("Date: 2026-07-08")
print("=" * 80)

# =============================================================================
# FRAMEWORK: 24D-DMF v8.4.3 (from RC-124/126/127)
# =============================================================================

# Quaternion 24-Cell
quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)

# Hopf Fibration
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

def full_projection_quaternion(v_24d):
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
    v2 = np.array([v3 @ e1_s, v3 @ e2_s])
    return v2

# Deep Holes
def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

# Floquet Tick
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

def apply_tick_vector_shifted(v, t, phase_shift):
    v = P23_on_vector(v)
    v = P11_on_vector(v)
    if (t + phase_shift) % 11 == 0:
        v = H_L_on_vector(v)
    return v

# Color Mapping
def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

def get_color(v):
    v2 = full_projection_quaternion(v)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    return angle_to_color(theta)

def get_color_sequence(start_idx, ticks=22):
    v = deep_hole(start_idx).copy()
    seq = []
    for t in range(ticks):
        seq.append(get_color(v))
        if t < ticks - 1:
            v = apply_tick_vector(v, t)
    return seq

def get_sequence_shifted(start_idx, ticks, phase_shift):
    v = deep_hole(start_idx).copy()
    seq = []
    for t in range(ticks):
        seq.append(get_color(v))
        if t < ticks - 1:
            v = apply_tick_vector_shifted(v, t, phase_shift)
    return seq

# Orbit classes from RC-127
orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}
idx_to_class = {}
for cls, indices in orbit_classes.items():
    for i in indices:
        idx_to_class[i] = cls

print("\n[STEP 0] Framework loaded successfully.")
print(f"  Quaternion 24-cell: {len(quaternions_24)} vertices")
print(f"  Deep holes: 24")
print(f"  Orbit classes: A({len(orbit_classes['A'])}) B({len(orbit_classes['B'])}) C({len(orbit_classes['C'])}) D({len(orbit_classes['D'])}) E({len(orbit_classes['E'])})")

# =============================================================================
# HYPOTHESIS A: H_L Phase-Shifted Schedule
# =============================================================================
print("\n" + "=" * 80)
print("HYPOTHESIS A: H_L Phase-Shifted Schedule")
print("=" * 80)

S0 = [get_sequence_shifted(i, 22, 0) for i in range(24)]
S5 = [get_sequence_shifted(i, 22, 5) for i in range(24)]
S6 = [get_sequence_shifted(i, 22, 6) for i in range(24)]

def time_rev_distance(Sa, Sb):
    return sum(a != b for a, b in zip(Sa, Sb[::-1]))

distances_A5 = [time_rev_distance(S0[i], S5[i]) for i in range(24)]
distances_A6 = [time_rev_distance(S0[i], S6[i]) for i in range(24)]
distances_A56 = [time_rev_distance(S5[i], S6[i]) for i in range(24)]

print("\n  H_A (S5 phase shift): distance distribution")
print("  " + "-" * 60)
print(f"  {'DH':<4} | {'Class':<6} | {'dist(S0, rev(S5))':<20} | {'Pass (≤2)':<10}")
print("  " + "-" * 60)
pass_A5 = sum(1 for i in range(24) if distances_A5[i] <= 2)
for i in range(24):
    print(f"  DH{i:<2d} | {idx_to_class[i]:<6} | {distances_A5[i]:<20} | {'YES' if distances_A5[i] <= 2 else 'NO':<10}")
print("  " + "-" * 60)
print(f"\n  H_A (S5): {pass_A5}/24 pass (threshold: 8/24)")

print("\n  H_A (S6 phase shift): distance distribution")
print("  " + "-" * 60)
print(f"  {'DH':<4} | {'Class':<6} | {'dist(S0, rev(S6))':<20} | {'Pass (≤2)':<10}")
print("  " + "-" * 60)
pass_A6 = sum(1 for i in range(24) if distances_A6[i] <= 2)
for i in range(24):
    print(f"  DH{i:<2d} | {idx_to_class[i]:<6} | {distances_A6[i]:<20} | {'YES' if distances_A6[i] <= 2 else 'NO':<10}")
print("  " + "-" * 60)
print(f"\n  H_A (S6): {pass_A6}/24 pass")

f_A_pass = (pass_A5 >= 8) or (pass_A6 >= 8)
print(f"\n  F_A Result: {'PASS' if f_A_pass else 'FAIL'} (best: {max(pass_A5, pass_A6)}/24)")

# =============================================================================
# HYPOTHESIS B: 144-Tick Period Time-Reversal Symmetry
# =============================================================================
print("\n" + "=" * 80)
print("HYPOTHESIS B: 144-Tick Period Time-Reversal Symmetry")
print("=" * 80)

print("\n  Computing full 144-tick sequences...")
S144 = [get_sequence_shifted(i, 144, 0) for i in range(24)]

def period_symmetry_test(seq):
    n = len(seq) // 2
    direct_mismatch = sum(seq[t] != seq[143 - t] for t in range(72))
    comp_mismatch = sum(seq[t] != (4 - seq[143 - t]) for t in range(72))
    return direct_mismatch, comp_mismatch

symmetry_results = [period_symmetry_test(S144[i]) for i in range(24)]

print("\n  Period symmetry results")
print("  " + "-" * 80)
print(f"  {'DH':<4} | {'Class':<6} | {'Direct':<10} | {'Comp':<10} | {'D%':<8} | {'C%':<8} | {'D-pass':<8} | {'C-pass':<8}")
print("  " + "-" * 80)
direct_pass = 0
comp_pass = 0
for i in range(24):
    dm, cm = symmetry_results[i]
    dp = dm <= 14
    cp = cm <= 14
    if dp: direct_pass += 1
    if cp: comp_pass += 1
    print(f"  DH{i:<2d} | {idx_to_class[i]:<6} | {dm:<10} | {cm:<10} | {dm/72*100:<7.1f}% | {cm/72*100:<7.1f}% | {'YES' if dp else 'NO':<8} | {'YES' if cp else 'NO':<8}")
print("  " + "-" * 80)
print(f"\n  Direct pass: {direct_pass}/24, Complement pass: {comp_pass}/24")

f_B_pass = (direct_pass >= 12) or (comp_pass >= 12)
print(f"\n  F_B Result: {'PASS' if f_B_pass else 'FAIL'} (direct: {direct_pass}/24, comp: {comp_pass}/24)")

# =============================================================================
# HYPOTHESIS C: Color Complement Closure
# =============================================================================
print("\n" + "=" * 80)
print("HYPOTHESIS C: Color Complement Closure")
print("=" * 80)

seq_tuples = [tuple(s) for s in S0]
complement_tuples = [tuple(4 - np.array(s)) for s in S0]

print("\n  Color complement closure test")
print("  " + "-" * 70)
print(f"  {'DH':<4} | {'Class':<6} | {'Initial':<8} | {'Comp Init':<10} | {'In Set?':<8} | {'Match DH':<8}")
print("  " + "-" * 70)

individual_closure = []
match_indices = []
for i in range(24):
    init_color = S0[i][0]
    comp_init = 4 - init_color
    comp_dh = None
    for j in range(24):
        if S0[j][0] == comp_init:
            comp_dh = j
            break
    ct = complement_tuples[i]
    in_set = ct in seq_tuples
    individual_closure.append(in_set)
    match_dh = seq_tuples.index(ct) if in_set else None
    match_indices.append(match_dh)
    print(f"  DH{i:<2d} | {idx_to_class[i]:<6} | {init_color:<8} | {comp_init:<10} | {'YES' if in_set else 'NO':<8} | {match_dh if match_dh is not None else 'N/A':<8}")

closure_count = sum(individual_closure)
print("  " + "-" * 70)
print(f"\n  Closure count: {closure_count}/24")

print("\n  Trajectory complement test")
print("  " + "-" * 70)
print(f"  {'DH':<4} | {'Class':<6} | {'Comp DH':<8} | {'Match?':<8} | {'Distance':<10}")
print("  " + "-" * 70)
trajectory_match_count = 0
for i in range(24):
    init_color = S0[i][0]
    comp_init = 4 - init_color
    comp_dh = None
    for j in range(24):
        if S0[j][0] == comp_init:
            comp_dh = j
            break
    if comp_dh is not None:
        comp_seq = S0[comp_dh]
        expected_comp = [4 - c for c in S0[i]]
        dist = sum(a != b for a, b in zip(comp_seq, expected_comp))
        matches = dist == 0
        if matches: trajectory_match_count += 1
        print(f"  DH{i:<2d} | {idx_to_class[i]:<6} | DH{comp_dh:<2d}     | {'YES' if matches else 'NO':<8} | {dist:<10}")
    else:
        print(f"  DH{i:<2d} | {idx_to_class[i]:<6} | N/A      | {'N/A':<8} | {'N/A':<10}")
print("  " + "-" * 70)
print(f"\n  Trajectory matches: {trajectory_match_count}/24")

f_C_pass = closure_count >= 20
print(f"\n  F_C Result: {'PASS' if f_C_pass else 'FAIL'} ({closure_count}/24)")

# =============================================================================
# DEEP STRUCTURAL ANALYSIS
# =============================================================================
print("\n" + "=" * 80)
print("DEEP STRUCTURAL ANALYSIS")
print("=" * 80)

def pure_engine_tick(v):
    v = P23_on_vector(v)
    v = P11_on_vector(v)
    return v

def reverse_P23(v):
    v_new = np.zeros_like(v)
    v_new[22] = v[0]
    v_new[0:22] = v[1:23]
    v_new[23] = v[23]
    return v_new

def reverse_P11(v):
    v_new = np.zeros_like(v)
    for j in range(23):
        v_new[j] = v[(2 * j) % 23]
    v_new[23] = v[23]
    return v_new

def reverse_pure_engine(v):
    v = reverse_P11(v)
    v = reverse_P23(v)
    return v

all_recovered = True
max_dev = 0
for i in range(24):
    v_orig = deep_hole(i).copy()
    v_fwd = pure_engine_tick(v_orig)
    v_back = reverse_pure_engine(v_fwd)
    dev = np.max(np.abs(v_orig - v_back))
    max_dev = max(max_dev, dev)
    if dev > 1e-10:
        all_recovered = False

print(f"\n  [1] Pure engine reversible: {all_recovered} (max dev: {max_dev:.2e})")

v_test = deep_hole(5).copy()
v_hl = H_L_on_vector(v_test)
v_hl2 = H_L_on_vector(v_hl)
is_involution = np.allclose(v_test, v_hl2)
print(f"  [2] H_L involution: {is_involution} (max dev: {np.max(np.abs(v_test - v_hl2)):.2e})")

v1 = pure_engine_tick(H_L_on_vector(v_test))
v2 = H_L_on_vector(pure_engine_tick(v_test))
commutes = np.allclose(v1, v2)
print(f"  [3] [H_L, Engine] = 0: {commutes} (max dev: {np.max(np.abs(v1 - v2)):.2e})")

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

print(f"\n  F_A (H_L phase shift):  {'PASS' if f_A_pass else 'FAIL'}")
print(f"  F_B (144-tick period):  {'PASS' if f_B_pass else 'FAIL'}")
print(f"  F_C (Color complement): {'PASS' if f_C_pass else 'FAIL'}")

overall = f_A_pass or f_B_pass or f_C_pass
print(f"\n  OVERALL: {'PASS (at least one hypothesis confirmed)' if overall else 'FAIL — Fundamental irreversibility confirmed'}")

print("\n" + "=" * 80)
print("RC-128 EXECUTION COMPLETE")
print("=" * 80)
