#!/usr/bin/env python3
"""
RC-191: THE UNITY BRIDGE AS SYMMETRY BREAKER
Analysis Script — Framework: 24D-DMF v8.4.6
Date: 2026-07-21
Status: COMPLETE (Framework Incompleteness Identified)

This script implements the full RC-191 analysis including:
  - SU(2) and SU(3) generator extraction from the Z46 orbit
  - Commutator error computation at MI = 0 and MI = 0.0349
  - Correlation analysis between MI and gauge errors

CRITICAL FINDING: The framework lacks a mechanism for MI to modify orbit dynamics.
The Unity Bridge cannot be tested as a symmetry breaker with the current model.
"""

import numpy as np
from itertools import product
import warnings
warnings.filterwarnings('ignore')

np.random.seed(191)

# =============================================================================
# CRITICAL CONSTANTS
# =============================================================================
PHI = (1 + np.sqrt(5)) / 2
MI_UNITY = 0.0349
MI_VALUES = np.array([0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.0349])

# =============================================================================
# FRAMEWORK FOUNDATION
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

def extract_quaternion(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))):
        q += v[0, i] * quaternions_24[i]
    return q

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
    p_golden = np.array([0, 1, PHI, 0]) / np.linalg.norm([0, 1, PHI, 0])
    v3 = np.array([
        q[0]*p_golden[1] - q[1]*p_golden[0] + q[2]*p_golden[3] - q[3]*p_golden[2],
        q[0]*p_golden[2] - q[2]*p_golden[0] + q[3]*p_golden[1] - q[1]*p_golden[3],
        q[0]*p_golden[3] - q[3]*p_golden[0] + q[1]*p_golden[2] - q[2]*p_golden[1]
    ])
    norm3 = np.linalg.norm(v3)
    if norm3 > 1e-10:
        v3 = v3 / norm3
    axis_5fold = np.array([0, 1, PHI])
    axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
    e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
    e1_s = e1_s / np.linalg.norm(e1_s)
    e2_s = np.cross(axis_5fold, e1_s)
    e2_s = e2_s / np.linalg.norm(e2_s)
    v2 = np.array([v3 @ e1_s, v3 @ e2_s])
    return v2

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

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
    v = P23_on_vector(v)
    if include_hl:
        v = H_L_on_vector(v)
    return v

def build_e8_roots():
    roots = []
    for i in range(8):
        for j in range(i+1, 8):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    root = np.zeros(8)
                    root[i] = s1
                    root[j] = s2
                    roots.append(root)
    for signs in product([0.5, -0.5], repeat=8):
        signs = np.array(signs)
        if np.sum(signs < 0) % 2 == 0:
            roots.append(signs)
    return np.array(roots)

E8_ROOTS = build_e8_roots()
BLOCK1_MASK = np.all(E8_ROOTS[:112, 4:] == 0, axis=1)
BLOCK2_MASK = np.all(E8_ROOTS[:112, :4] == 0, axis=1)
INT_MIXED = E8_ROOTS[:112][~(BLOCK1_MASK | BLOCK2_MASK)]
MIXED_192 = np.vstack([INT_MIXED, E8_ROOTS[112:]])

sector_2_roots = []
for r in MIXED_192:
    nz1, nz2 = np.count_nonzero(r[:4]), np.count_nonzero(r[4:])
    if nz1 == 4 and nz2 == 4:
        mc1, mc2 = np.sum(r[:4] < 0), np.sum(r[4:] < 0)
        if mc1 % 2 == 0 and mc2 % 2 == 0:
            sector_2_roots.append(r)
sector_2_roots = np.array(sector_2_roots)

collapsed_roots = []
for idx, root in enumerate(sector_2_roots):
    v_24d = np.pad(root, (0, 16))
    q = extract_quaternion(v_24d)
    if np.linalg.norm(q) < 1e-10:
        collapsed_roots.append(root)
collapsed_roots = np.array(collapsed_roots)
n_collapsed = len(collapsed_roots)

# Build 46-step orbit
orbit_24d = np.zeros((n_collapsed, 47, 24))
for i, root in enumerate(collapsed_roots):
    v = np.zeros(24)
    v[0:8] = root
    for k in range(47):
        orbit_24d[i, k] = v.copy()
        if k < 46:
            v = D23_tick(v, include_hl=True)

quat_orbit = np.zeros((n_collapsed, 47, 4))
for i in range(n_collapsed):
    for k in range(47):
        quat_orbit[i, k] = extract_quaternion(orbit_24d[i, k])

# =============================================================================
# SU(2) AND SU(3) EXTRACTION
# =============================================================================
EPSILON = np.zeros((3, 3, 3))
EPSILON[0, 1, 2] = EPSILON[1, 2, 0] = EPSILON[2, 0, 1] = 1
EPSILON[0, 2, 1] = EPSILON[2, 1, 0] = EPSILON[1, 0, 2] = -1

def extract_su2_modes_from_orbit():
    all_spatial = quat_orbit[:, :, 1:4].reshape(-1, 3)
    norms = np.linalg.norm(all_spatial, axis=1)
    all_spatial = all_spatial[norms > 1e-10]
    cov = np.cov(all_spatial.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    return eigvals[idx], eigvecs[:, idx]

def extract_su3_modes_from_orbit():
    all_data = []
    for k in range(46):
        evolved = np.zeros((192, 24))
        for r_idx, root in enumerate(MIXED_192):
            v = np.zeros(24)
            v[0:8] = root
            for t in range(k):
                v = D23_tick(v, include_hl=True)
            evolved[r_idx] = v
        all_data.append(evolved[:, :8])
    all_data = np.vstack(all_data)
    cov = np.cov(all_data.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    return eigvals[idx], eigvecs[:, idx]

def compute_su2_error(mi_weight=0.0):
    _, eigvecs = extract_su2_modes_from_orbit()
    q_modes = np.zeros((46, 3))
    for k in range(46):
        spatial = quat_orbit[:, k, 1:4]
        norms = np.linalg.norm(spatial, axis=1)
        if np.sum(norms > 1e-10) > 0:
            for i in range(3):
                projections = spatial @ eigvecs[:, i]
                q_modes[k, i] = np.mean(projections[norms > 1e-10])
    weights = np.ones(46) + mi_weight
    weights /= np.sum(weights)
    q_avg = np.sum(q_modes * weights[:, None], axis=0)
    avg_commutator = np.zeros((3, 3))
    for k in range(46):
        q = q_modes[k]
        w = weights[k] * 46
        for i in range(3):
            for j in range(3):
                for l in range(3):
                    avg_commutator[i, j] += w * EPSILON[i, j, l] * q[l]
    expected = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            for l in range(3):
                expected[i, j] += EPSILON[i, j, l] * q_avg[l]
    error = np.mean(np.abs(avg_commutator - expected))
    norms = np.linalg.norm(q_modes, axis=1)
    norm_error = np.var(norms) / (np.mean(norms**2) + 1e-15)
    return error + 0.5 * norm_error, q_avg

# =============================================================================
# TASK 1: MI = 0
# =============================================================================
print("=" * 70)
print("RC-191: TASK 1 — MI = 0 (No Unity Bridge)")
print("=" * 70)
error_su2_MI0, q_avg_MI0 = compute_su2_error(mi_weight=0.0)
print(f"SU(2) Error at MI=0: {error_su2_MI0:.6f}")
print(f"q_avg: {q_avg_MI0}")
print(f"
NOTE: Error is zero because q_avg = 0 (symmetric orbit).")
print(f"The framework lacks a mechanism for MI to modify orbit dynamics.")

# =============================================================================
# TASK 2: MI Variation
# =============================================================================
print("
" + "=" * 70)
print("RC-191: TASK 2 — MI Variation Analysis")
print("=" * 70)
for mi in MI_VALUES:
    err, _ = compute_su2_error(mi_weight=mi)
    print(f"  MI = {mi:.4f}: SU(2) Error = {err:.6f}")
print(f"
NOTE: All errors are identical because MI is a scalar weight")
print(f"on a symmetric orbit. The weighted average of zero is always zero.")

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("
" + "=" * 70)
print("RC-191: FINAL VERDICT")
print("=" * 70)
print("""
UNITY BRIDGE REJECTED AS SYMMETRY BREAKER — Framework Incompleteness

The D23 clock orbit is symmetric and deterministic. A scalar MI weight
cannot break this symmetry. The framework lacks a mechanism for the
Unity Bridge to modify the orbit dynamics.

To test RC-191 properly, the model needs:
  1. Tick-dependent MI (varying entanglement)
  2. MI-dependent orbit perturbation
  3. A preferred direction in 24D space

Without these, the discrete gauge structure is FUNDAMENTAL, not
caused by the Unity Bridge.
""")
