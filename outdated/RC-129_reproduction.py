#!/usr/bin/env python3
"""
RC-129: Locality Across Golay Faces — Reproduction Script
Framework: 24D-DMF v8.4.3
Date: 2026-07-08
Run: python3 RC-129_reproduction.py
"""

import numpy as np
from scipy.stats import pearsonr
from itertools import product
from math import log2
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
print("=" * 80)
print("RC-129: LOCALITY ACROSS GOLAY FACES")
print("Framework: 24D-DMF v8.4.3")
print("=" * 80)

# =============================================================================
# FRAMEWORK IMPORTS
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

def boundary_hamming(i, j):
    return sum(a != b for a, b in zip(sequences[i], sequences[j]))

# =============================================================================
# GOLAY CODE G24
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

print(f"  Codewords: {len(code_words)}")

# =============================================================================
# LOAD DATA
# =============================================================================
print("\n[STEP 2] Loading color sequences and orbit classes...")

sequences = [get_color_sequence(i, 22) for i in range(24)]

orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}

print(f"  Sequences loaded: 24 x {len(sequences[0])}")

# =============================================================================
# MOG LABELING
# =============================================================================
MOG = np.array([
    [23, 14, 17, 11, 22, 19],
    [ 3,  8, 20, 15, 10,  5],
    [13, 18,  7,  9,  6, 21],
    [16,  4, 12,  1,  0,  2]
])

coord_to_mog = {}
for r in range(4):
    for c in range(6):
        coord_to_mog[MOG[r, c]] = (r, c)

# =============================================================================
# FACE METRICS
# =============================================================================
def mog_manhattan(i, j):
    if i == j: return 0
    ri, ci = coord_to_mog[i]
    rj, cj = coord_to_mog[j]
    return abs(ri - rj) + abs(ci - cj)

def mog_column(i, j):
    if i == j: return 0
    return 0 if coord_to_mog[i][1] == coord_to_mog[j][1] else 1

def mog_row(i, j):
    if i == j: return 0
    return 0 if coord_to_mog[i][0] == coord_to_mog[j][0] else 1

def cyclic_dist(i, j):
    if i == j: return 0
    if i == 23 or j == 23: return 0
    d = abs(i - j)
    return min(d, 23 - d)

def S_dist(i, j):
    if i == j: return 0
    if i <= 11 and j == 23 - i: return 0
    if j <= 11 and i == 23 - j: return 0
    return 1

# Octad profiles
octads = [cw for cw in code_words if np.sum(cw) == 8]

def classify_octad_type(octad):
    cols = [0] * 6
    for p in range(24):
        if octad[p] == 1:
            _, c = coord_to_mog[p]
            cols[c] += 1
    cols_sorted = sorted(cols, reverse=True)
    if cols_sorted[:4] == [2, 2, 2, 2]: return 'I'
    elif cols_sorted[:3] == [4, 2, 2]: return 'II'
    elif cols_sorted[:2] == [4, 4]: return 'III'
    else: return 'OTHER'

profiles = {}
for p in range(24):
    n_I = n_II = n_III = 0
    for octad in octads:
        if octad[p] == 1:
            t = classify_octad_type(octad)
            if t == 'I': n_I += 1
            elif t == 'II': n_II += 1
            elif t == 'III': n_III += 1
    profiles[p] = (n_I, n_II, n_III)

def octad_dist(i, j):
    if i == j: return 0
    pi, pj = profiles[i], profiles[j]
    return abs(pi[0]-pj[0]) + abs(pi[1]-pj[1]) + abs(pi[2]-pj[2])

# =============================================================================
# CORRELATION COMPUTATION
# =============================================================================
def compute_face_correlation(face_metric, name):
    n = 24
    D_bulk = np.zeros((n, n))
    D_bound = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i < j:
                D_bulk[i, j] = face_metric(i, j)
                D_bound[i, j] = boundary_hamming(i, j)
                D_bulk[j, i] = D_bulk[i, j]
                D_bound[j, i] = D_bound[i, j]

    mask = np.triu_indices_from(D_bulk, k=1)
    if np.std(D_bulk[mask]) > 0 and np.std(D_bound[mask]) > 0:
        r_global, p_global = pearsonr(D_bulk[mask], D_bound[mask])
    else:
        r_global, p_global = 0.0, 1.0

    class_results = {}
    for cls_name, holes in orbit_classes.items():
        if len(holes) < 3: continue
        m = len(holes)
        D_bulk_cls = np.zeros((m, m))
        D_bound_cls = np.zeros((m, m))
        for a in range(m):
            for b in range(m):
                if a < b:
                    D_bulk_cls[a, b] = face_metric(holes[a], holes[b])
                    D_bound_cls[a, b] = boundary_hamming(holes[a], holes[b])
        mask_cls = np.triu_indices_from(D_bulk_cls, k=1)
        if len(mask_cls[0]) > 2 and np.std(D_bulk_cls[mask_cls]) > 0 and np.std(D_bound_cls[mask_cls]) > 0:
            r_cls, p_cls = pearsonr(D_bulk_cls[mask_cls], D_bound_cls[mask_cls])
            class_results[cls_name] = {'r': r_cls, 'p': p_cls, 'n_pairs': len(mask_cls[0])}

    return {'name': name, 'r_global': r_global, 'p_global': p_global, 'class_results': class_results}

# =============================================================================
# RUN ALL FACES
# =============================================================================
print("\n" + "=" * 80)
print("STEP 3: COMPUTING CORRELATIONS")
print("=" * 80)

face_metrics = [
    (cyclic_dist, "Cyclic (QR)"),
    (mog_manhattan, "MOG Grid (Manhattan)"),
    (mog_column, "MOG Column"),
    (mog_row, "MOG Row"),
    (octad_dist, "Octad Profile"),
    (S_dist, "S-Involution")
]

results = {}
for metric, name in face_metrics:
    results[name] = compute_face_correlation(metric, name)

print("\n  GLOBAL CORRELATIONS:")
print("  " + "-" * 85)
print(f"  {'Face':<25} | {'r_global':>10} | {'p_global':>10}")
print("  " + "-" * 85)
for name, res in results.items():
    print(f"  {res['name']:<25} | {res['r_global']:10.4f} | {res['p_global']:10.4f}")

print("\n  WITHIN-CLASS CORRELATIONS:")
print("  " + "-" * 100)
print(f"  {'Face':<25} | {'Class':<6} | {'r':>8} | {'p':>8}")
print("  " + "-" * 100)
for name, res in results.items():
    for cls_name, cls_res in res['class_results'].items():
        print(f"  {res['name']:<25} | {cls_name:<6} | {cls_res['r']:8.4f} | {cls_res['p']:8.4f}")

# =============================================================================
# FALSIFICATION
# =============================================================================
print("\n" + "=" * 80)
print("STEP 4: FALSIFICATION CRITERIA")
print("=" * 80)

f1_pass = any(abs(res['r_global']) > 0.5 for res in results.values())
max_within_r = max(abs(cls_res['r']) for res in results.values() for cls_res in res['class_results'].values())
f2_pass = max_within_r > 0.7

print(f"\n  F1 (Global |r| > 0.5): {'PASS' if f1_pass else 'FAIL'}")
print(f"  F2 (Within-class |r| > 0.7): {'PASS' if f2_pass else 'FAIL'}")
print(f"\n  OVERALL VERDICT: {'PASS' if (f1_pass or f2_pass) else 'FAIL — Fundamental Non-Locality'}")

print("\n" + "=" * 80)
print("RC-129 EXECUTION COMPLETE")
print("=" * 80)
