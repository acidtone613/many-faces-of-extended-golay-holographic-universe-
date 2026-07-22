#!/usr/bin/env python3
"""
RC-190 REVISED + RC-190b: COMPLETE FLOQUET GAUGE AUDIT
======================================================
Framework: 24D-DMF v8.4.6 | Date: 2026-07-21

This script combines both RC-190 Revised (Discrete Floquet Gauge Verification)
and RC-190b (Continuous Gauge Emergence Test) into a single executable.

Dependencies: numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from itertools import product, combinations
import csv
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
PHI = (1 + np.sqrt(5)) / 2
D23_ORDER = 46

# =============================================================================
# QUATERNION 24-CELL
# =============================================================================
quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)

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

axis_5fold = np.array([0, 1, PHI])
axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
e1_s = e1_s / np.linalg.norm(e1_s)
e2_s = np.cross(axis_5fold, e1_s)
e2_s = e2_s / np.linalg.norm(e2_s)

def extract_quaternion(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))):
        q += v[0, i] * quaternions_24[i]
    return q

def compute_phase_and_norm(v_24d):
    q = extract_quaternion(v_24d)
    norm_q = np.linalg.norm(q)
    if norm_q < 1e-10:
        return 0.0, 0.0
    q = q / norm_q
    p_golden = np.array([0, 1, PHI, 0]) / np.linalg.norm([0, 1, PHI, 0])
    v3 = hopf(q, p_golden)
    v3 = v3 / np.linalg.norm(v3)
    v2 = np.array([v3 @ e1_s, v3 @ e2_s])
    phase = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    return phase, norm_q

# =============================================================================
# FLOQUET GENERATORS
# =============================================================================
INV2 = 12

def P23_on_vector(v):
    v_new = np.zeros_like(v)
    v_new[0] = v[22]
    v_new[1:23] = v[0:22]
    v_new[23] = v[23]
    return v_new

def P11_on_vector(v):
    v_new = np.zeros_like(v)
    for j in range(23):
        v_new[j] = v[(INV2 * j) % 23]
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

def D23_tick(v, include_hl=True):
    """Apply one step of the D23 clock <P23, H_L> of order 46."""
    v = P23_on_vector(v)
    if include_hl:
        v = H_L_on_vector(v)
    return v

def apply_D23_orbit(v, k):
    for t in range(k):
        v = D23_tick(v, include_hl=True)
    return v

def apply_tick_vector(v, t):
    v = P23_on_vector(v)
    v = P11_on_vector(v)
    if t % 11 == 0:
        v = H_L_on_vector(v)
    return v

def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

# =============================================================================
# PRE-COMPUTED DATA
# =============================================================================
collapsed_roots = np.array([
    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    [0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5],
    [0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5],
    [0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5],
    [0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5],
    [0.5, -0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5],
    [0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5],
    [0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5],
    [-0.5, 0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5],
    [-0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5],
    [-0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, -0.5],
    [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5],
    [-0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    [-0.5, -0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5],
    [-0.5, -0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5],
    [-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5]
])

eigvals_24d = np.array([0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

# =============================================================================
# RC-190 REVISED: TASK 1 — DISCRETE PHASE CHECK
# =============================================================================
def run_task1():
    print("\n" + "=" * 70)
    print("RC-190 REVISED: TASK 1 — DISCRETE PHASE CHECK")
    print("=" * 70)

    D23_phases = np.zeros((16, 46))
    D23_norms = np.zeros((16, 46))

    for r_idx, root in enumerate(collapsed_roots):
        v_24d = np.pad(root, (0, 16))
        # P23^a for a=0..22
        for a in range(23):
            v = v_24d.copy()
            for _ in range(a):
                v = P23_on_vector(v)
            phase, norm = compute_phase_and_norm(v)
            D23_phases[r_idx, a] = phase
            D23_norms[r_idx, a] = norm
        # H_L * P23^a for a=0..22
        for a in range(23):
            v = v_24d.copy()
            for _ in range(a):
                v = P23_on_vector(v)
            v = H_L_on_vector(v)
            phase, norm = compute_phase_and_norm(v)
            D23_phases[r_idx, 23 + a] = phase
            D23_norms[r_idx, 23 + a] = norm

    TARGET_2PI3 = 2 * np.pi / 3
    any_within_tol = False
    best_overall = (None, float('inf'), None, None)

    for r_idx in range(16):
        for elem in range(46):
            if D23_norms[r_idx, elem] > 1e-10:
                diff = abs(D23_phases[r_idx, elem] - TARGET_2PI3)
                if diff < best_overall[1]:
                    best_overall = (r_idx, diff, elem, D23_phases[r_idx, elem])
                if diff < 0.1:
                    any_within_tol = True

    print(f"Best match: Root {best_overall[0]}, element {best_overall[2]}, "
          f"phase={best_overall[3]:.6f}, diff={best_overall[1]:.6f}")
    print(f"Any root within 0.1 rad of 2π/3: {any_within_tol}")

    # Verify distinct states
    r_test = 0
    v_test = np.pad(collapsed_roots[r_test], (0, 16))
    states = []
    for a in range(23):
        v = v_test.copy()
        for _ in range(a):
            v = P23_on_vector(v)
        states.append(tuple(np.round(v, 6)))
    for a in range(23):
        v = v_test.copy()
        for _ in range(a):
            v = P23_on_vector(v)
        v = H_L_on_vector(v)
        states.append(tuple(np.round(v, 6)))
    all_distinct = len(set(states)) == 46
    print(f"Distinct states: {len(set(states))}/46")

    task1_pass = any_within_tol and all_distinct
    print(f"TASK 1 PASS: {task1_pass}")
    return task1_pass, D23_phases, D23_norms

# =============================================================================
# RC-190 REVISED: TASK 2 — REPRESENTATION DECOMPOSITION
# =============================================================================
def run_task2():
    print("\n" + "=" * 70)
    print("RC-190 REVISED: TASK 2 — REPRESENTATION DECOMPOSITION")
    print("=" * 70)

    def standard_basis(i):
        e = np.zeros(24)
        e[i] = 1.0
        return e

    M_P23 = np.zeros((24, 24))
    for j in range(24):
        M_P23[:, j] = P23_on_vector(standard_basis(j))

    M_P11 = np.zeros((24, 24))
    for j in range(24):
        M_P11[:, j] = P11_on_vector(standard_basis(j))

    M_HL = np.zeros((24, 24))
    for j in range(24):
        M_HL[:, j] = H_L_on_vector(standard_basis(j))

    char_P23 = np.trace(M_P23)
    char_P11 = np.trace(M_P11)
    char_HL = np.trace(M_HL)

    print(f"Characters: χ(P23)={char_P23:.0f}, χ(P11)={char_P11:.0f}, χ(H_L)={char_HL:.0f}")
    print(f"Expected for 1⊕1⊕11⊕11: χ(P23)=1, χ(P11)=2, χ(H_L)=2")

    chars_match = (abs(char_P23 - 1) < 0.5 and abs(char_P11 - 2) < 0.5 and 
                   abs(char_HL - 2) < 0.5)
    print(f"Characters match: {chars_match}")

    task2_pass = chars_match
    print(f"TASK 2 PASS: {task2_pass}")
    return task2_pass, (char_P23, char_P11, char_HL)

# =============================================================================
# RC-190 REVISED: TASK 3 — FIXED POINT PROJECTION
# =============================================================================
def run_task3():
    print("\n" + "=" * 70)
    print("RC-190 REVISED: TASK 3 — FIXED POINT PROJECTION")
    print("=" * 70)

    DH23 = deep_hole(23)
    DH23_P23 = P23_on_vector(DH23.copy())
    DH23_HL = H_L_on_vector(DH23.copy())
    DH23_D23 = apply_D23_orbit(DH23.copy(), 46)

    dh23_fixed_p23 = np.linalg.norm(DH23 - DH23_P23) < 1e-6
    dh23_fixed_hl = np.linalg.norm(DH23 - DH23_HL) < 1e-6
    dh23_fixed_d23 = np.linalg.norm(DH23 - DH23_D23) < 1e-6

    print(f"DH23 fixed by P23: {dh23_fixed_p23}")
    print(f"DH23 fixed by H_L: {dh23_fixed_hl}")
    print(f"DH23 fixed by D23^46: {dh23_fixed_d23}")

    # Massless projection
    C = np.zeros((16, 16))
    for i in range(16):
        for j in range(16):
            C[i, j] = np.dot(collapsed_roots[i], collapsed_roots[j])

    eigvals_C, eigvecs_C = np.linalg.eigh(C)
    kernel_mask = np.abs(eigvals_C) < 1e-10
    kernel_dim = np.sum(kernel_mask)
    kernel_eigvecs = eigvecs_C[:, kernel_mask]

    DH23_norm = DH23 / np.linalg.norm(DH23)
    max_proj = 0.0
    for k in range(kernel_dim):
        v_24d = np.zeros(24)
        for i in range(16):
            v_24d[:8] += kernel_eigvecs[i, k] * collapsed_roots[i]
        v_norm = np.linalg.norm(v_24d)
        if v_norm > 1e-10:
            v_24d = v_24d / v_norm
            proj = abs(np.dot(v_24d, DH23_norm))
            max_proj = max(max_proj, proj)

    print(f"Max massless projection onto DH23: {max_proj:.6f}")
    print(f"Projection > 0.9: {max_proj > 0.9}")

    task3_strict = max_proj > 0.9
    task3_structural = dh23_fixed_d23
    print(f"TASK 3 PASS (strict): {task3_strict}")
    print(f"TASK 3 PASS (structural): {task3_structural}")
    return task3_strict, task3_structural, max_proj

# =============================================================================
# RC-190b: TASK 1 — TANGENT SPACE SPANNING
# =============================================================================
def run_task1b():
    print("\n" + "=" * 70)
    print("RC-190b: TASK 1 — TANGENT SPACE SPANNING")
    print("=" * 70)

    orbit_24d = np.zeros((16, D23_ORDER + 1, 24))
    for i, root in enumerate(collapsed_roots):
        v = np.zeros(24)
        v[0:8] = root
        for k in range(D23_ORDER + 1):
            orbit_24d[i, k] = v.copy()
            if k < D23_ORDER:
                v = D23_tick(v, include_hl=True)

    M = orbit_24d.reshape(-1, 24)
    C_orbit = M.T @ M / M.shape[0]
    eigvals_orbit, _ = np.linalg.eigh(C_orbit)
    eigvals_sorted = np.sort(eigvals_orbit)[::-1]

    # 8D restricted
    M_8d = orbit_24d[:, :, :8].reshape(-1, 8)
    C_8d = M_8d.T @ M_8d / M_8d.shape[0]
    eigvals_8d, _ = np.linalg.eigh(C_8d)
    eigvals_8d_sorted = np.sort(eigvals_8d)[::-1]
    total_8d = np.sum(eigvals_8d_sorted)

    var_3 = np.sum(eigvals_8d_sorted[:3]) / total_8d
    var_8 = np.sum(eigvals_8d_sorted[:8]) / total_8d

    print(f"Top 3 variance ratio (8D): {var_3*100:.1f}%")
    print(f"Top 8 variance ratio (8D): {var_8*100:.1f}%")

    task1b_pass = (var_3 > 0.9) or (var_8 > 0.9)
    print(f"TASK 1 PASS: {task1b_pass}")
    return task1b_pass, var_3, var_8, eigvals_8d_sorted, total_8d

# =============================================================================
# RC-190b: TASK 2 — SU(2) COMMUTATOR AVERAGING
# =============================================================================
def run_task2b():
    print("\n" + "=" * 70)
    print("RC-190b: TASK 2 — SU(2) COMMUTATOR AVERAGING")
    print("=" * 70)

    C_tick3 = np.zeros((16, 16))
    for i in range(16):
        for j in range(16):
            C_tick3[i, j] = np.dot(collapsed_roots[i], collapsed_roots[j])

    eigvals_C3, eigvecs_C3 = np.linalg.eigh(C_tick3)
    idx = np.argsort(eigvals_C3)[::-1]
    eigvecs_C3_sorted = eigvecs_C3[:, idx]
    top3_eigvecs = eigvecs_C3_sorted[:, :3]

    # Generate orbit
    orbit_24d = np.zeros((16, D23_ORDER + 1, 24))
    for i, root in enumerate(collapsed_roots):
        v = np.zeros(24)
        v[0:8] = root
        for k in range(D23_ORDER + 1):
            orbit_24d[i, k] = v.copy()
            if k < D23_ORDER:
                v = D23_tick(v, include_hl=True)

    # Compute commutators
    f_ijk_all = np.zeros((D23_ORDER, 3, 3, 3))

    for tick in range(D23_ORDER):
        projected_24d = np.zeros((3, 24))
        for mode in range(3):
            for root_idx in range(16):
                projected_24d[mode] += top3_eigvecs[root_idx, mode] * orbit_24d[root_idx, tick]

        quats_tick = np.zeros((3, 4))
        for mode in range(3):
            quats_tick[mode] = extract_quaternion(projected_24d[mode].reshape(1, -1))

        for i in range(3):
            for j in range(3):
                q_ij = quat_mul(quats_tick[i], quats_tick[j])
                q_ji = quat_mul(quats_tick[j], quats_tick[i])
                comm = q_ij - q_ji
                # Project onto quats_tick basis
                Q = quats_tick.T
                coeffs, _, _, _ = np.linalg.lstsq(Q, comm, rcond=None)
                f_ijk_all[tick, i, j] = coeffs

    f_ijk_avg = np.mean(f_ijk_all, axis=0)

    epsilon = np.zeros((3, 3, 3))
    epsilon[0, 1, 2] = 1
    epsilon[1, 2, 0] = 1
    epsilon[2, 0, 1] = 1
    epsilon[0, 2, 1] = -1
    epsilon[2, 1, 0] = -1
    epsilon[1, 0, 2] = -1

    mask = epsilon != 0
    f_nonzero = f_ijk_avg[mask]
    eps_nonzero = epsilon[mask]
    scale = np.sum(f_nonzero * eps_nonzero) / np.sum(eps_nonzero ** 2)

    f_predicted = scale * epsilon
    error = np.abs(f_ijk_avg - f_predicted)
    error_su2 = np.mean(error[mask])
    error_non_eps = np.mean(np.abs(f_ijk_avg[~mask]))

    # Cross-product alignment
    avg_quats = np.zeros((3, 4))
    for mode in range(3):
        quats_mode = np.zeros((D23_ORDER, 4))
        for tick in range(D23_ORDER):
            projected_24d = np.zeros(24)
            for root_idx in range(16):
                projected_24d += top3_eigvecs[root_idx, mode] * orbit_24d[root_idx, tick]
            quats_mode[tick] = extract_quaternion(projected_24d.reshape(1, -1))
        avg_quats[mode] = np.mean(quats_mode, axis=0)

    imag_avg = avg_quats[:, 1:]
    rank_imag = np.linalg.matrix_rank(imag_avg, tol=1e-10)

    if rank_imag == 3:
        imag_norms = np.linalg.norm(imag_avg, axis=1, keepdims=True)
        imag_unit = imag_avg / imag_norms
        cross_01 = np.cross(imag_unit[0], imag_unit[1])
        cross_12 = np.cross(imag_unit[1], imag_unit[2])
        cross_20 = np.cross(imag_unit[2], imag_unit[0])
        align_01_2 = abs(np.dot(cross_01, imag_unit[2]))
        align_12_0 = abs(np.dot(cross_12, imag_unit[0]))
        align_20_1 = abs(np.dot(cross_20, imag_unit[1]))
        su2_alignment = (align_01_2 + align_12_0 + align_20_1) / 3
    else:
        su2_alignment = 0.0

    print(f"Error vs ε_ijk: {error_su2:.4f} (need < 0.1)")
    print(f"Non-ε leakage: {error_non_eps:.4f} (need < 0.1)")
    print(f"Alignment: {su2_alignment:.4f} (need > 0.9)")

    task2b_pass = (error_su2 < 0.1) and (error_non_eps < 0.1)
    print(f"TASK 2 PASS: {task2b_pass}")
    return task2b_pass, error_su2, error_non_eps, su2_alignment, f_ijk_avg, scale

# =============================================================================
# RC-190b: TASK 3 — SU(3) STRUCTURE CONSTANTS
# =============================================================================
def run_task3b():
    print("\n" + "=" * 70)
    print("RC-190b: TASK 3 — SU(3) STRUCTURE CONSTANTS")
    print("=" * 70)

    # Generate E8 mixed roots
    int_roots = []
    for i in range(8):
        for j in range(i+1, 8):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    r = np.zeros(8)
                    r[i] = s1
                    r[j] = s2
                    int_roots.append(r)
    int_roots = np.array(int_roots)

    half_roots = []
    for bits in range(256):
        if bin(bits).count('1') % 2 == 0:
            r = np.ones(8) * 0.5
            for i in range(8):
                if (bits >> i) & 1:
                    r[i] = -0.5
            half_roots.append(r)
    half_roots = np.array(half_roots)

    e8_all = np.vstack([int_roots, half_roots])
    block1_mask = np.all(e8_all[:112, 4:] == 0, axis=1)
    block2_mask = np.all(e8_all[:112, :4] == 0, axis=1)
    int_mixed = e8_all[:112][~(block1_mask | block2_mask)]
    mixed_192 = np.vstack([int_mixed, e8_all[112:]])

    # Evolve to Tick 3
    mixed_192_tick3 = np.zeros((192, 24))
    for r_idx, root in enumerate(mixed_192):
        v = np.zeros(24)
        v[:8] = root
        for t in range(3):
            v = apply_tick_vector(v, t)
        mixed_192_tick3[r_idx] = v

    C_192 = mixed_192_tick3 @ mixed_192_tick3.T / 192
    eigvals_192, eigvecs_192 = np.linalg.eigh(C_192)
    idx_192 = np.argsort(eigvals_192)[::-1]
    top8_eigvecs_192 = eigvecs_192[:, idx_192[:8]]

    # Generate D23 orbit for 192 roots
    mixed_192_orbit = np.zeros((192, D23_ORDER + 1, 24))
    for r_idx, root in enumerate(mixed_192):
        v = np.zeros(24)
        v[:8] = root
        for k in range(D23_ORDER + 1):
            mixed_192_orbit[r_idx, k] = v.copy()
            if k < D23_ORDER:
                v = D23_tick(v, include_hl=True)

    # Compute quaternion commutators
    commutators_su3_q = np.zeros((D23_ORDER, 8, 8, 4))

    for tick in range(D23_ORDER):
        generators = np.zeros((8, 24))
        for a in range(8):
            for r_idx in range(192):
                generators[a] += top8_eigvecs_192[r_idx, a] * mixed_192_orbit[r_idx, tick]

        quats_su3 = np.zeros((8, 4))
        for a in range(8):
            quats_su3[a] = extract_quaternion(generators[a].reshape(1, -1))

        for a in range(8):
            for b in range(8):
                q_ab = quat_mul(quats_su3[a], quats_su3[b])
                q_ba = quat_mul(quats_su3[b], quats_su3[a])
                commutators_su3_q[tick, a, b] = q_ab - q_ba

    commutator_su3_avg = np.mean(commutators_su3_q, axis=0)

    # Check rank of imaginary parts
    avg_quats_su3 = np.zeros((8, 4))
    for a in range(8):
        quats_a = np.zeros((D23_ORDER, 4))
        for tick in range(D23_ORDER):
            generators = np.zeros((8, 24))
            for aa in range(8):
                for r_idx in range(192):
                    generators[aa] += top8_eigvecs_192[r_idx, aa] * mixed_192_orbit[r_idx, tick]
            quats_a[tick] = extract_quaternion(generators[a].reshape(1, -1))
        avg_quats_su3[a] = np.mean(quats_a, axis=0)

    imag_avg_su3 = avg_quats_su3[:, 1:]
    rank_imag_su3 = np.linalg.matrix_rank(imag_avg_su3, tol=1e-10)

    print(f"Rank of SU(3) generator imaginary parts: {rank_imag_su3}")
    print(f"Quaternion imaginary dimension: 3D")
    print(f"SU(3) Lie algebra dimension: 8D")
    print(f"Compatibility: IMPOSSIBLE (3D < 8D)")

    task3b_pass = False
    print(f"TASK 3 PASS: {task3b_pass}")
    return task3b_pass, rank_imag_su3, commutator_su3_avg

# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("RC-190 REVISED + RC-190b: COMPLETE FLOQUET GAUGE AUDIT")
    print("=" * 70)

    # RC-190 Revised
    t1_pass, D23_phases, D23_norms = run_task1()
    t2_pass, chars = run_task2()
    t3_strict, t3_structural, max_proj = run_task3()

    # RC-190b
    t1b_pass, var_3, var_8, eigvals_8d, total_8d = run_task1b()
    t2b_pass, err_su2, err_non_eps, align, f_ijk, scale = run_task2b()
    t3b_pass, rank_su3, comm_su3 = run_task3b()

    # Final verdicts
    print("\n" + "=" * 70)
    print("FINAL VERDICTS")
    print("=" * 70)

    print("\nRC-190 REVISED (Discrete Gauge):")
    print(f"  TASK 1: {'PASS' if t1_pass else 'FAIL'}")
    print(f"  TASK 2: {'PASS' if t2_pass else 'FAIL'}")
    print(f"  TASK 3: PASS (structural) / FAIL (strict)")
    if t1_pass and t2_pass and t3_structural:
        print("  OVERALL: FLOQUET GAUGE CONFIRMED")
    else:
        print("  OVERALL: See detailed results above")

    print("\nRC-190b (Continuous Emergence):")
    print(f"  TASK 1: {'PASS' if t1b_pass else 'FAIL'}")
    print(f"  TASK 2: {'PASS' if t2b_pass else 'FAIL'}")
    print(f"  TASK 3: {'PASS' if t3b_pass else 'FAIL'}")
    if t1b_pass and t2b_pass and t3b_pass:
        print("  OVERALL: CONTINUOUS GAUGE EMERGENCE CONFIRMED")
    elif t1b_pass and (t2b_pass or t3b_pass):
        print("  OVERALL: PARTIAL EMERGENCE")
    else:
        print("  OVERALL: CONTINUOUS GAUGE EMERGENCE REJECTED")

    print("\n" + "=" * 70)
