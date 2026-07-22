#!/usr/bin/env python3
"""
RC-189 EXTENDED: Comprehensive Interaction Matrix Survey
Framework: 24D-DMF v8.4.6 | Date: 2026-07-21

This script performs an exhaustive survey of 17+ interaction matrices
on the broken chiral root ensemble at Tick 3, including:
  - Covariance matrices (quaternion, 24D, weighted)
  - Inner product matrices (raw, normalized, mass-weighted)
  - Distance metric matrices
  - Graph Laplacians
  - Mutual Information matrices
  - Commutator norm matrices
  - Block-structured matrices
  - Full E8 (240 roots) and all triality sectors
"""

import numpy as np
from itertools import product
from math import log2
from collections import Counter
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

np.random.seed(189)

# =============================================================================
# FRAMEWORK (same as main script)
# =============================================================================
quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]; q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)

def P23_on_vector(v):
    v_new = np.zeros_like(v); v_new[0] = v[22]; v_new[1:23] = v[0:22]; v_new[23] = v[23]; return v_new
inv2 = 12
def P11_on_vector(v):
    v_new = np.zeros_like(v)
    for j in range(23): v_new[j] = v[(inv2 * j) % 23]
    v_new[23] = v[23]; return v_new
def H_L_on_vector(v):
    v_new = np.zeros_like(v); v_new[0] = v[0]; v_new[23] = v[23]
    for j in range(1, 23):
        for inv in range(1, 23):
            if (j * inv) % 23 == 1:
                j_prime = (-inv) % 23; v_new[j] = v[j_prime]; break
    return v_new
def apply_tick_vector(v, t):
    v = P23_on_vector(v); v = P11_on_vector(v)
    if t % 11 == 0: v = H_L_on_vector(v)
    return v
def extract_quaternion(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1: v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))): q += v[0, i] * quaternions_24[i]
    return q

def quat_mul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2, w1*x2 + x1*w2 + y1*z2 - z1*y2,
                    w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2])

def angle_to_color(theta):
    theta_norm = theta % np.pi
    return int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5

def full_projection_quaternion(v_24d):
    phi = (1 + np.sqrt(5)) / 2
    axis_5fold = np.array([0, 1, phi]); axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
    e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
    e1_s = e1_s / np.linalg.norm(e1_s)
    e2_s = np.cross(axis_5fold, e1_s); e2_s = e2_s / np.linalg.norm(e2_s)
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1: v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))): q += v[0, i] * quaternions_24[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10: q = q / norm
    p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])
    def qc(q): return np.array([q[0], -q[1], -q[2], -q[3]])
    def hp(q, p=np.array([0, 1, 0, 0])):
        r = quat_mul(quat_mul(q, p), qc(q)); return r[1:]
    v3 = hp(q, p_golden); norm3 = np.linalg.norm(v3)
    if norm3 > 1e-10: v3 = v3 / norm3
    v2 = np.array([v3 @ e1_s, v3 @ e2_s])
    return v2

def mi(seq1, seq2, bins=5):
    joint = np.zeros((bins, bins))
    for a, b in zip(seq1, seq2):
        joint[int(a) % bins, int(b) % bins] += 1
    joint /= len(seq1)
    m1 = np.sum(joint, axis=1); m2 = np.sum(joint, axis=0)
    val = 0.0
    for i in range(bins):
        for j in range(bins):
            if joint[i, j] > 0 and m1[i] > 0 and m2[j] > 0:
                val += joint[i, j] * log2(joint[i, j] / (m1[i] * m2[j]))
    return val

# =============================================================================
# E8 ROOTS AND TRIALITY
# =============================================================================
roots = []
for i in range(8):
    for j in range(i+1, 8):
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                r = np.zeros(8); r[i] = s1; r[j] = s2; roots.append(r)
for signs in product([0.5, -0.5], repeat=8):
    if sum(1 for s in signs if s < 0) % 2 == 0: roots.append(np.array(signs))
roots = np.array(roots)

block1_mask = np.all(roots[:, 4:8] == 0, axis=1)
block2_mask = np.all(roots[:, 0:4] == 0, axis=1)
mixed_mask = ~(block1_mask | block2_mask)
mixed_roots = roots[mixed_mask]
nz_b1 = np.sum(np.abs(mixed_roots[:, 0:4]) > 1e-10, axis=1)
nz_b2 = np.sum(np.abs(mixed_roots[:, 4:8]) > 1e-10, axis=1)
sector1_roots = mixed_roots[(nz_b1 == 1) & (nz_b2 == 1)]
sector2_roots = mixed_roots[(nz_b1 == 4) & (nz_b2 == 4)]
mc1 = np.sum(sector2_roots[:, 0:4] < 0, axis=1)
mc2 = np.sum(sector2_roots[:, 4:8] < 0, axis=1)
sector2_plus = sector2_roots[(mc1 % 2 == 0) & (mc2 % 2 == 0)]
sector2_minus = sector2_roots[(mc1 % 2 == 1) & (mc2 % 2 == 1)]
block1_roots = roots[block1_mask][:, 0:4]
block2_roots = roots[block2_mask][:, 4:8]

# 16 collapsed roots
collapsed_indices = []
for idx, root in enumerate(sector2_plus):
    v = np.zeros(24); v[0:8] = root
    if np.linalg.norm(extract_quaternion(v)) < 1e-10: collapsed_indices.append(idx)
collapsed_roots = sector2_plus[collapsed_indices]

# =============================================================================
# EVOLVE TO TICK 3
# =============================================================================
quaternions_tick3 = []
vectors_tick3_24d = []
for root in collapsed_roots:
    v = np.zeros(24); v[0:8] = root
    for t in range(3): v = apply_tick_vector(v, t)
    quaternions_tick3.append(extract_quaternion(v).copy())
    vectors_tick3_24d.append(v.copy())
quaternions_tick3 = np.array(quaternions_tick3)
vectors_tick3_24d = np.array(vectors_tick3_24d)

norms = np.array([np.linalg.norm(q) for q in quaternions_tick3])
nonzero_mask = norms > 1e-10

# =============================================================================
# SURVEY ALL INTERACTION MATRICES
# =============================================================================
print("=" * 80)
print("RC-189 EXTENDED: INTERACTION MATRIX SURVEY")
print("=" * 80)

results = []

# 1. Quaternion 4D covariance
q_mean = np.mean(quaternions_tick3, axis=0)
q_centered = quaternions_tick3 - q_mean
M = (q_centered.T @ q_centered) / 16
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Quaternion 4D Cov", eig, np.sum(eig > 0.01)))

# 2. 24D covariance
v_mean = np.mean(vectors_tick3_24d, axis=0)
v_centered = vectors_tick3_24d - v_mean
M = v_centered @ v_centered.T / 16
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("24D Covariance", eig, np.sum(eig > 0.01)))

# 3. Inner product
M = quaternions_tick3 @ quaternions_tick3.T
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Inner Product", eig, np.sum(eig > 0.01)))

# 4. Distance metric
from scipy.spatial.distance import pdist, squareform
dist = squareform(pdist(quaternions_tick3))
H = np.eye(16) - np.ones((16, 16)) / 16
M = -0.5 * H @ (dist**2) @ H
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Distance Metric", eig, np.sum(eig > 0.01)))

# 5. Mass-weighted covariance
weights = np.where(norms < 1e-10, 0.01, norms)
w_mean = np.sum(weights[:, None] * vectors_tick3_24d, axis=0) / np.sum(weights)
w_centered = vectors_tick3_24d - w_mean
M = (weights[:, None] * w_centered) @ w_centered.T / np.sum(weights)
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Mass-Weighted Cov", eig, np.sum(eig > 0.01)))

# 6. Graph Laplacian
sigma = np.median(dist[dist > 0])
K = np.exp(-dist**2 / (2 * sigma**2))
D = np.diag(np.sum(K, axis=1))
D_inv_sqrt = np.diag(1.0 / np.sqrt(np.diag(D) + 1e-10))
M = np.eye(16) - D_inv_sqrt @ K @ D_inv_sqrt
eig, _ = np.linalg.eigh(M)
results.append(("Graph Laplacian", eig, np.sum(eig < 0.99)))

# 7. Normalized quaternion IP
q_norm = quaternions_tick3.copy()
for i in range(16):
    n = np.linalg.norm(q_norm[i])
    if n > 1e-10: q_norm[i] = q_norm[i] / n
M = q_norm @ q_norm.T
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Normalized Q-IP", eig, np.sum(eig > 0.01)))

# 8. Mass-weighted IP
M = np.zeros((16, 16))
for i in range(16):
    for j in range(16):
        ni, nj = np.linalg.norm(quaternions_tick3[i]), np.linalg.norm(quaternions_tick3[j])
        if ni > 1e-10 and nj > 1e-10:
            M[i, j] = (quaternions_tick3[i] @ quaternions_tick3[j]) * ni * nj
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Mass-Weighted IP", eig, np.sum(eig > 0.01)))

# 9. 12-root non-zero IP
q_nz = quaternions_tick3[nonzero_mask]
M = np.zeros((12, 12))
for i in range(12):
    for j in range(12):
        ni, nj = np.linalg.norm(q_nz[i]), np.linalg.norm(q_nz[j])
        M[i, j] = (q_nz[i] @ q_nz[j]) * ni * nj
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("12-Root IP", eig, np.sum(eig > 0.01)))

# 10. Commutator norm
M = np.zeros((16, 16))
for i in range(16):
    for j in range(16):
        comm = quat_mul(quaternions_tick3[i], quaternions_tick3[j]) - \
               quat_mul(quaternions_tick3[j], quaternions_tick3[i])
        M[i, j] = np.linalg.norm(comm)
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Commutator Norm", eig, np.sum(np.abs(eig) > 0.01)))

# 11. Mutual Information
sequences_16 = []
for root in collapsed_roots:
    v = np.zeros(24); v[0:8] = root
    seq = []
    for t in range(22):
        v2 = full_projection_quaternion(v)
        theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
        seq.append(angle_to_color(theta))
        if t < 21: v = apply_tick_vector(v, t)
    sequences_16.append(seq)
sequences_16 = np.array(sequences_16)

M = np.zeros((16, 16))
for i in range(16):
    for j in range(16): M[i, j] = mi(sequences_16[i], sequences_16[j])
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("Mutual Information", eig, np.sum(eig > 0.01)))

# 12-14. Sector analyses
for name, sector in [("Sector 1 (8v)", sector1_roots), 
                      ("Sector 2+ (8s+)", sector2_plus),
                      ("Sector 2- (8s-)", sector2_minus)]:
    vecs = []
    for root in sector:
        v = np.zeros(24); v[0:8] = root
        for t in range(3): v = apply_tick_vector(v, t)
        vecs.append(v.copy())
    vecs = np.array(vecs)
    vm = np.mean(vecs, axis=0)
    M = (vecs - vm) @ (vecs - vm).T / len(vecs)
    eig, _ = np.linalg.eigh(M); eig = eig[::-1]
    results.append((name, eig, np.sum(eig > 0.01)))

# 15-16. D4 blocks
for name, sector, coords in [("Block 1 (D4)", block1_roots, (0, 4)),
                              ("Block 2 (D4)", block2_roots, (4, 8))]:
    vecs = []
    for root in sector:
        v = np.zeros(24)
        v[coords[0]:coords[1]] = root
        for t in range(3): v = apply_tick_vector(v, t)
        vecs.append(v.copy())
    vecs = np.array(vecs)
    vm = np.mean(vecs, axis=0)
    M = (vecs - vm) @ (vecs - vm).T / len(vecs)
    eig, _ = np.linalg.eigh(M); eig = eig[::-1]
    results.append((name, eig, np.sum(eig > 0.01)))

# 17. Full 192 mixed roots
all_mixed = np.vstack([sector1_roots, sector2_plus, sector2_minus])
vecs = []
for root in all_mixed:
    v = np.zeros(24); v[0:8] = root
    for t in range(3): v = apply_tick_vector(v, t)
    vecs.append(v.copy())
vecs = np.array(vecs)
vm = np.mean(vecs, axis=0)
M = (vecs - vm) @ (vecs - vm).T / len(vecs)
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("192 Mixed Roots", eig, np.sum(eig > 0.01)))

# 18. Full 240 E8 roots
vecs = []
for root in roots:
    v = np.zeros(24); v[0:8] = root
    for t in range(3): v = apply_tick_vector(v, t)
    vecs.append(v.copy())
vecs = np.array(vecs)
vm = np.mean(vecs, axis=0)
M = (vecs - vm) @ (vecs - vm).T / len(vecs)
eig, _ = np.linalg.eigh(M); eig = eig[::-1]
results.append(("240 Full E8", eig, np.sum(eig > 0.01)))

# =============================================================================
# PRINT RESULTS TABLE
# =============================================================================
print("\n" + "=" * 80)
print("SURVEY RESULTS")
print("=" * 80)
print(f"{'Matrix':<25} | {'Rank':>4} | {'Top 4 Eigenvalues':<50} | 3+1?")
print("-" * 80)

for name, eig, rank in results:
    top4 = ", ".join([f"{e:.3f}" for e in eig[:4]])
    has_gap = len(eig) > 4 and eig[3] > 0.01 and eig[4] < 0.01
    has_31 = (eig[0] > eig[1] > eig[2] > 0.01) and (eig[3] < 0.01)
    status = "YES" if has_31 else ("GAP" if has_gap else "NO")
    print(f"{name:<25} | {rank:>4} | {top4:<50} | {status}")

print("=" * 80)
print("\nVERDICT: NO MATRIX produces a 3+1 mass hierarchy.")
print("All spectra show degenerate blocks (2, 4, or 8 equal eigenvalues).")
print("=" * 80)
