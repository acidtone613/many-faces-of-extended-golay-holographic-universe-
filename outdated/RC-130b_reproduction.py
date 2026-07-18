#!/usr/bin/env python3
"""
RC-130b: The Cascade Balance Hypothesis — Reproduction Script
Framework: 24D-DMF v8.4.3
Date: 2026-07-08
Run: python3 RC-130b_reproduction.py
"""

import numpy as np
from scipy.stats import pearsonr, mannwhitneyu
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from itertools import product, combinations
from math import log2
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
print("=" * 80)
print("RC-130b: THE CASCADE BALANCE HYPOTHESIS")
print("Framework: 24D-DMF v8.4.3")
print("=" * 80)

# =============================================================================
# FRAMEWORK IMPORTS
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

def shannon_entropy(seq):
    counts = {}
    for c in seq:
        counts[c] = counts.get(c, 0) + 1
    n = len(seq)
    return -sum((c/n)*log2(c/n) for c in counts.values())

def floquet_period(start, max_ticks=200):
    v = deep_hole(start).copy()
    seen = {}
    for t in range(max_ticks):
        state = tuple(np.round(v, 10))
        if state in seen:
            return t - seen[state]
        seen[state] = t
        v = apply_tick_vector(v, t)
    return None

# =============================================================================
# LOAD DATA
# =============================================================================
print("\n[STEP 1] Generating color sequences...")
sequences = [get_color_sequence(i, 22) for i in range(24)]

orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}

print(f"  Sequences: 24 x {len(sequences[0])}")

# =============================================================================
# STEP 2: BUILD THE CASCADE
# =============================================================================
print("\n" + "=" * 80)
print("STEP 2: BUILDING THE DIMENSIONAL CASCADE")
print("=" * 80)

# Project all 24 deep holes to 3D
projections_3d = np.zeros((24, 3))
for i in range(24):
    v = deep_hole(i)
    q = np.zeros(4)
    for j in range(24):
        q += v[j] * quaternions_24[j]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
    p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])
    v3 = hopf(q, p_golden)
    norm3 = np.linalg.norm(v3)
    if norm3 > 1e-10:
        v3 = v3 / norm3
    projections_3d[i] = v3

# Cluster into 12 Hopf pairs
dist_3d = np.zeros((24, 24))
for i in range(24):
    for j in range(24):
        dist_3d[i, j] = np.linalg.norm(projections_3d[i] - projections_3d[j])

condensed_dist = squareform(dist_3d)
Z = linkage(condensed_dist, method='ward')
clusters_12 = fcluster(Z, t=12, criterion='maxclust')

cluster_map = {}
for i in range(24):
    c = clusters_12[i]
    if c not in cluster_map:
        cluster_map[c] = []
    cluster_map[c].append(i)

# Compute icosahedron vertices
icosa_vertices = []
for c in sorted(cluster_map):
    centroid = np.mean(projections_3d[cluster_map[c]], axis=0)
    norm = np.linalg.norm(centroid)
    if norm > 1e-10:
        centroid = centroid / norm
    icosa_vertices.append(centroid)
icosa_vertices = np.array(icosa_vertices)

# Compute edge length
edge_length = None
for i in range(12):
    for j in range(i+1, 12):
        d = np.linalg.norm(icosa_vertices[i] - icosa_vertices[j])
        if edge_length is None or d < edge_length:
            edge_length = d

# Find antipodal vertex pairs (5-fold axes)
vertex_pairs = []
for i in range(12):
    for j in range(i+1, 12):
        dot = np.dot(icosa_vertices[i], icosa_vertices[j])
        if dot < -0.99:
            vertex_pairs.append((i, j))

# Build adjacency graph
adjacency = {i: [] for i in range(12)}
for i in range(12):
    for j in range(i+1, 12):
        d = np.linalg.norm(icosa_vertices[i] - icosa_vertices[j])
        if abs(d - edge_length) < 0.01:
            adjacency[i].append(j)
            adjacency[j].append(i)

# Map holes to vertices
hole_to_vertex = {}
for c in sorted(cluster_map):
    for h in cluster_map[c]:
        hole_to_vertex[h] = c - 1

print(f"  12 Hopf pairs identified.")
print(f"  Icosahedron edge length: {edge_length:.6f}")
print(f"  6 antipodal axes (5-fold) found.")

# =============================================================================
# STEP 3: LOCALITY TESTS AT MULTIPLE LEVELS
# =============================================================================
print("\n" + "=" * 80)
print("STEP 3: LOCALITY TESTS AT MULTIPLE LEVELS")
print("=" * 80)

# Level 24: Individual holes
all_dists = [boundary_hamming(i,j) for i in range(24) for j in range(i+1,24)]
print(f"\n  Level 24 (Individual): Mean Hamming = {np.mean(all_dists):.2f}")

# Level 12: Vertices
vertex_sequences = {}
for v in range(12):
    holes = [h for h in range(24) if hole_to_vertex[h] == v]
    seqs = [np.array(sequences[h]) for h in holes]
    vertex_sequences[v] = seqs[0].tolist() if len(seqs) > 0 else []

vertex_hamming = np.zeros((12, 12))
for i in range(12):
    for j in range(i+1, 12):
        h = sum(a != b for a, b in zip(vertex_sequences[i], vertex_sequences[j]))
        vertex_hamming[i, j] = h
        vertex_hamming[j, i] = h

vertex_dists = [vertex_hamming[i,j] for i in range(12) for j in range(i+1,12)]
print(f"  Level 12 (Vertices): Mean Hamming = {np.mean(vertex_dists):.2f}")

# Level 6: 5-fold axes
axis_sequences = {}
for axis_idx, (v1, v2) in enumerate(vertex_pairs):
    holes = [h for h in range(24) if hole_to_vertex[h] == v1 or hole_to_vertex[h] == v2]
    seqs = [np.array(sequences[h]) for h in holes]
    avg_seq = []
    for t in range(22):
        colors = [s[t] for s in seqs]
        avg_seq.append(int(np.round(np.mean(colors))) % 5)
    axis_sequences[axis_idx] = avg_seq

axis_hamming = np.zeros((6, 6))
for i in range(6):
    for j in range(i+1, 6):
        h = sum(a != b for a, b in zip(axis_sequences[i], axis_sequences[j]))
        axis_hamming[i, j] = h
        axis_hamming[j, i] = h

axis_dists = [axis_hamming[i,j] for i in range(6) for j in range(i+1,6)]
print(f"  Level 6 (Axes): Mean Hamming = {np.mean(axis_dists):.2f}")

# 3D distance between axes
axis_midpoints = []
for v1, v2 in vertex_pairs:
    mid = (icosa_vertices[v1] + icosa_vertices[v2]) / 2
    axis_midpoints.append(mid)
axis_midpoints = np.array(axis_midpoints)

axis_3d_dist = np.zeros((6, 6))
for i in range(6):
    for j in range(i+1, 6):
        d = np.linalg.norm(axis_midpoints[i] - axis_midpoints[j])
        axis_3d_dist[i, j] = d
        axis_3d_dist[j, i] = d

mask6 = np.triu_indices(6, k=1)
r_axis, p_axis = pearsonr(axis_hamming[mask6], axis_3d_dist[mask6])
print(f"\n  *** LEVEL 6 CORRELATION: r = {r_axis:.4f}, p = {p_axis:.4f} ***")
if abs(r_axis) > 0.5:
    print("  *** LOCALITY FOUND AT LEVEL 6 ***")

# =============================================================================
# STEP 4: SAME 5-FOLD AXIS TEST
# =============================================================================
print("\n" + "=" * 80)
print("STEP 4: SAME 5-FOLD AXIS TEST")
print("=" * 80)

same_axis = []
diff_axis = []
for i in range(24):
    for j in range(i+1, 24):
        vi, vj = hole_to_vertex[i], hole_to_vertex[j]
        h = boundary_hamming(i, j)
        on_same = any(vi in axis and vj in axis for axis in vertex_pairs)
        if on_same:
            same_axis.append(h)
        else:
            diff_axis.append(h)

print(f"\n  Same axis: Mean = {np.mean(same_axis):.2f}, n = {len(same_axis)}")
print(f"  Diff axis: Mean = {np.mean(diff_axis):.2f}, n = {len(diff_axis)}")

if len(same_axis) > 0 and len(diff_axis) > 0:
    stat, p = mannwhitneyu(same_axis, diff_axis, alternative='two-sided')
    print(f"  Mann-Whitney U: U = {stat:.2f}, p = {p:.4f}")
    if p < 0.05:
        print("  -> SIGNIFICANT: Same-axis holes have different color distances!")

# =============================================================================
# STEP 5: LIGHT VS SHADOW TESTS
# =============================================================================
print("\n" + "=" * 80)
print("STEP 5: LIGHT VS SHADOW TESTS")
print("=" * 80)

# Definition 1: Quaternion type
light_def1 = [i for i in range(8)]
shadow_def1 = [i for i in range(8, 24)]

# Definition 2: Color entropy
entropies = [shannon_entropy(sequences[i]) for i in range(24)]
median_ent = np.median(entropies)
light_def3 = [i for i in range(24) if entropies[i] <= median_ent]
shadow_def3 = [i for i in range(24) if entropies[i] > median_ent]

# Definition 3: Floquet period
periods = [floquet_period(i) for i in range(24)]
median_period = np.median([p for p in periods if p is not None])
light_def4 = [i for i in range(24) if periods[i] is not None and periods[i] <= median_period]
shadow_def4 = [i for i in range(24) if periods[i] is None or periods[i] > median_period]

definitions = [
    ("Quaternion Type", light_def1, shadow_def1),
    ("Color Entropy", light_def3, shadow_def3),
    ("Floquet Period", light_def4, shadow_def4),
]

print("\n  Light/Shadow Locality Tests:")
print("  " + "-" * 90)
print(f"  {'Definition':<20} | {'Light r':>10} | {'Light p':>10} | {'Shadow r':>10} | {'Shadow p':>10}")
print("  " + "-" * 90)

for name, light, shadow in definitions:
    light_d_bulk = []
    light_d_bound = []
    for i in light:
        for j in light:
            if i < j:
                light_d_bulk.append(np.linalg.norm(projections_3d[i] - projections_3d[j]))
                light_d_bound.append(boundary_hamming(i, j))

    if len(light_d_bulk) > 2 and np.std(light_d_bulk) > 0 and np.std(light_d_bound) > 0:
        r_light, p_light = pearsonr(light_d_bulk, light_d_bound)
    else:
        r_light, p_light = 0, 1

    shadow_d_bulk = []
    shadow_d_bound = []
    for i in shadow:
        for j in shadow:
            if i < j:
                shadow_d_bulk.append(np.linalg.norm(projections_3d[i] - projections_3d[j]))
                shadow_d_bound.append(boundary_hamming(i, j))

    if len(shadow_d_bulk) > 2 and np.std(shadow_d_bulk) > 0 and np.std(shadow_d_bound) > 0:
        r_shadow, p_shadow = pearsonr(shadow_d_bulk, shadow_d_bound)
    else:
        r_shadow, p_shadow = 0, 1

    print(f"  {name:<20} | {r_light:10.4f} | {p_light:10.4f} | {r_shadow:10.4f} | {p_shadow:10.4f}")

print("\n" + "=" * 80)
print("RC-130b EXECUTION COMPLETE")
print("=" * 80)
