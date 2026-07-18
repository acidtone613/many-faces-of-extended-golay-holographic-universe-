#!/usr/bin/env python3
"""
RC-122: The Geometry of the Defect Orbit
Characterizing the Deep Hole Trajectory Under the Floquet Tick
Framework: 24D-DMF v8.4.3
Date: 2026-07-08

Reproduction script for RC-122 execution results.
Dependencies: numpy, matplotlib
"""

import numpy as np
from itertools import permutations, product
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
SEED = 122
np.random.seed(SEED)

# =============================================================================
# PART 1: GOLAY CODE G24 (Cyclic Basis)
# =============================================================================
print("[STEP 1] Building Golay code G24...")

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
print(f"  Self-dual verified: {np.all((G24 @ G24.T) % 2 == 0)}")

# =============================================================================
# PART 2: COCODE
# =============================================================================
def gf2_rref(A):
    A = A.copy() % 2
    m, n = A.shape
    rank = 0
    pivots = []
    for col in range(n):
        pivot = None
        for row in range(rank, m):
            if A[row, col] == 1:
                pivot = row
                break
        if pivot is None:
            continue
        A[[rank, pivot]] = A[[pivot, rank]]
        pivots.append(col)
        for row in range(m):
            if row != rank and A[row, col] == 1:
                A[row] = (A[row] + A[rank]) % 2
        rank += 1
    return A, pivots

G24_rref, pivots = gf2_rref(G24)
free_cols = [c for c in range(24) if c not in pivots]

cocode_basis = []
for fc in free_cols:
    e = np.zeros(24, dtype=np.uint8)
    e[fc] = 1
    cocode_basis.append(e)

cocode_basis_mat = np.array(cocode_basis, dtype=np.uint8)
coset_bits = np.array([[(b >> i) & 1 for i in range(12)] for b in range(4096)], dtype=np.uint8)
cosets_raw = (coset_bits @ cocode_basis_mat) % 2

cosets = np.zeros((4096, 24), dtype=np.uint8)
for i in range(4096):
    reps = (cosets_raw[i] + code_words) % 2
    weights_vec = np.sum(reps, axis=1)
    idx = np.argmin(weights_vec)
    cosets[i] = reps[idx]

# =============================================================================
# PART 3: P23 ORBIT
# =============================================================================
def P23_action(v):
    v_new = np.zeros_like(v)
    v_new[1:23] = v[0:22]
    v_new[0] = v[22]
    v_new[23] = v[23]
    return v_new

e0 = np.zeros(24, dtype=np.uint8)
e0[0] = 1
coset_1_idx = None
for idx in range(4096):
    diff = (e0 + cosets[idx]) % 2
    if tuple(diff) in code_set:
        coset_1_idx = idx
        break

orbit_reps = np.zeros((23, 24), dtype=np.uint8)
current = cosets[coset_1_idx].copy()
for t in range(23):
    orbit_reps[t] = current
    shifted = P23_action(current)
    diffs = (shifted + cosets) % 2
    in_code = np.array([tuple(d) in code_set for d in diffs])
    idx = np.where(in_code)[0]
    if len(idx) > 0:
        current = cosets[idx[0]].copy()

print(f"  P23 orbit length: {len(orbit_reps)}")

# =============================================================================
# PART 4: QUATERNION 24-CELL
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
# PART 5: HOPF FIBRATION AND PROJECTION
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

# =============================================================================
# PART 6: DEEP HOLES AND FLOQUET TICK
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
# PART 7: TRACE THE ORBIT
# =============================================================================
print("\n" + "=" * 70)
print("RC-122: MAIN EXPERIMENT")
print("=" * 70)

print("\n[STEP 5] Tracing deep hole orbit under Floquet tick...")

orbit_sequence = []
current_h = deep_hole(0).copy()
visited_indices = []

for t in range(100):
    min_dist = float('inf')
    closest_idx = -1
    for i in range(24):
        hi = deep_hole(i)
        dist = np.linalg.norm(current_h - hi)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i

    orbit_sequence.append({
        'tick': t,
        'vector': current_h.copy(),
        'closest_deep_hole': closest_idx,
        'distance_to_closest': min_dist
    })
    visited_indices.append(closest_idx)

    if t < 99:
        current_h = apply_tick_vector(current_h, t)

# Find period
period = None
for p in range(1, 50):
    if all(visited_indices[t] == visited_indices[t + p] for t in range(len(visited_indices) - p)):
        period = p
        break

print(f"  Orbit period: {period}")
print(f"  Visited deep hole indices (first period): {visited_indices[:period]}")
print(f"  Number of unique deep holes visited: {len(set(visited_indices[:period]))}")

# =============================================================================
# PART 8: PROJECT ORBIT TO 2D AND 3D
# =============================================================================
print("\n[STEP 6] Projecting orbit to 2D (decagon) and 3D (icosahedron)...")

unique_visited = list(dict.fromkeys(visited_indices[:period]))
print(f"  Unique visited indices in order: {unique_visited}")

projections_2d = []
projections_3d = []
angles_2d = []

for idx in unique_visited:
    hi = deep_hole(idx)
    v2 = full_projection_quaternion(hi)
    projections_2d.append(v2)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    angles_2d.append(theta)

    v = hi.reshape(1, -1)
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
    projections_3d.append(v3)

projections_2d = np.array(projections_2d)
projections_3d = np.array(projections_3d)
angles_2d = np.array(angles_2d)

print(f"  2D projections computed for {len(projections_2d)} points")
print(f"  3D projections computed for {len(projections_3d)} points")

# =============================================================================
# PART 9: COMPUTE EDGE LENGTHS IN EMBEDDING
# =============================================================================
print("\n[STEP 7] Computing edge lengths in embedding spaces...")

edge_lengths_2d = []
for i in range(len(projections_2d)):
    j = (i + 1) % len(projections_2d)
    dist = np.linalg.norm(projections_2d[i] - projections_2d[j])
    edge_lengths_2d.append(dist)

edge_lengths_3d = []
for i in range(len(projections_3d)):
    j = (i + 1) % len(projections_3d)
    dist = np.linalg.norm(projections_3d[i] - projections_3d[j])
    edge_lengths_3d.append(dist)

print(f"  2D edge lengths: {[f'{d:.4f}' for d in edge_lengths_2d]}")
print(f"  3D edge lengths: {[f'{d:.4f}' for d in edge_lengths_3d]}")
print(f"  2D edge length mean: {np.mean(edge_lengths_2d):.4f}, std: {np.std(edge_lengths_2d):.4f}")
print(f"  3D edge length mean: {np.mean(edge_lengths_3d):.4f}, std: {np.std(edge_lengths_3d):.4f}")

# =============================================================================
# PART 10: COLOR MAPPING
# =============================================================================
print("\n[STEP 8] Computing color states...")

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

colors = [angle_to_color(a) for a in angles_2d]
print(f"  Color sequence: {colors}")
print(f"  Unique colors: {sorted(set(colors))}")

# =============================================================================
# PART 11: DISTANCE MATRIX AND EMBEDDING ANALYSIS
# =============================================================================
print("\n[STEP 9] Computing distance matrices...")

dist_matrix_2d = np.zeros((len(projections_2d), len(projections_2d)))
for i in range(len(projections_2d)):
    for j in range(len(projections_2d)):
        dist_matrix_2d[i, j] = np.linalg.norm(projections_2d[i] - projections_2d[j])

dist_matrix_3d = np.zeros((len(projections_3d), len(projections_3d)))
for i in range(len(projections_3d)):
    for j in range(len(projections_3d)):
        dist_matrix_3d[i, j] = np.linalg.norm(projections_3d[i] - projections_3d[j])

print(f"  2D distance matrix shape: {dist_matrix_2d.shape}")
print(f"  3D distance matrix shape: {dist_matrix_3d.shape}")

# =============================================================================
# PART 12: ICOSAHEDRON VERTEX MATCHING
# =============================================================================
print("\n[STEP 10] Matching to icosahedron vertices...")

icos_verts = []
for p in permutations([0, 1, phi], 3):
    for signs in product([-1, 1], repeat=3):
        v = np.array([s * x for s, x in zip(signs, p)])
        v = v / np.linalg.norm(v)
        is_new = True
        for existing in icos_verts:
            if np.linalg.norm(v - existing) < 1e-6 or np.linalg.norm(v + existing) < 1e-6:
                is_new = False
                break
        if is_new:
            icos_verts.append(v)

icos_verts = np.array(icos_verts)
print(f"  Icosahedron vertices: {len(icos_verts)}")

matches = []
match_dists = []
for p3d in projections_3d:
    best_dist = float('inf')
    best_idx = -1
    for i, iv in enumerate(icos_verts):
        d = min(np.linalg.norm(p3d - iv), np.linalg.norm(p3d + iv))
        if d < best_dist:
            best_dist = d
            best_idx = i
    matches.append(best_idx)
    match_dists.append(best_dist)

print(f"  Match distances to icosahedron: {[f'{d:.4f}' for d in match_dists]}")
max_match_dist = max(match_dists)
print(f"  Maximum match distance: {max_match_dist:.4f}")

# =============================================================================
# PART 13: FALSIFICATION CRITERIA
# =============================================================================
print("\n" + "=" * 70)
print("FALSIFICATION CRITERIA")
print("=" * 70)

print("\n  F1: Embedding Existence")
print(f"    Max distance to icosahedron: {max_match_dist:.4f}")
f1_pass = max_match_dist < 0.1
print(f"    Result: {'PASS' if f1_pass else 'FAIL'} (threshold: 0.1)")

print("\n  F2: Constant Step Size")
var_2d = np.var(edge_lengths_2d)
var_3d = np.var(edge_lengths_3d)
print(f"    2D edge length variance: {var_2d:.4f}")
print(f"    3D edge length variance: {var_3d:.4f}")
f2_pass = var_3d < 0.1
print(f"    Result: {'PASS' if f2_pass else 'FAIL'} (threshold: 0.1)")

print("\n  F3: Symmetry Preservation")
unique_colors = sorted(set(colors))
print(f"    Unique colors: {unique_colors}")
print(f"    Number of unique colors: {len(unique_colors)}")
f3_pass = len(unique_colors) == 5
print(f"    Result: {'PASS' if f3_pass else 'FAIL'} (expected: 5)")

# =============================================================================
# PART 14: VERDICT
# =============================================================================
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

all_pass = f1_pass and f2_pass and f3_pass
if all_pass:
    verdict = "PASS (Full) — The orbit embeds in a known geometric structure with 5-fold symmetry."
elif f1_pass and f3_pass:
    verdict = "STRUCTURAL PARTIAL SUCCESS — The orbit embeds in the icosahedron but with variable step size."
else:
    verdict = "FAIL — The orbit does not have a natural geometric embedding."

print(f"  {verdict}")
print(f"\n  F1 (Embedding): {'PASS' if f1_pass else 'FAIL'}")
print(f"  F2 (Constant Step): {'PASS' if f2_pass else 'FAIL'}")
print(f"  F3 (5-Color Symmetry): {'PASS' if f3_pass else 'FAIL'}")

# =============================================================================
# PART 15: VISUALIZATION
# =============================================================================
print("\n[STEP 11] Generating visualization...")

fig = plt.figure(figsize=(18, 14))

color_map = {0: '#e74c3c', 1: '#e67e22', 2: '#f1c40f', 3: '#2ecc71', 4: '#3498db'}
color_names = {0: 'Red', 1: 'Orange', 2: 'Yellow', 3: 'Green', 4: 'Blue'}

# --- Plot 1: 2D Projection with Orbit Path ---
ax1 = fig.add_subplot(2, 3, 1)
decagon_x = [np.cos(2*np.pi*k/10) for k in range(10)] + [np.cos(0)]
decagon_y = [np.sin(2*np.pi*k/10) for k in range(10)] + [np.sin(0)]
ax1.plot(decagon_x, decagon_y, 'k--', alpha=0.2, linewidth=1)

for i in range(len(projections_2d)):
    j = (i + 1) % len(projections_2d)
    ax1.annotate('', xy=projections_2d[j], xytext=projections_2d[i],
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5, lw=1))

for i, (p2d, c) in enumerate(zip(projections_2d, colors)):
    ax1.scatter(p2d[0], p2d[1], c=color_map[c], s=200, edgecolors='black', linewidth=1.5, zorder=5)
    ax1.annotate(f'{unique_visited[i]}', (p2d[0], p2d[1]), 
                fontsize=9, ha='center', va='center', fontweight='bold', color='white', zorder=6)

ax1.set_xlabel('x', fontsize=11)
ax1.set_ylabel('y', fontsize=11)
ax1.set_title('2D Projection: Orbit on Decagon', fontsize=12, fontweight='bold')
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)

# --- Plot 2: 3D Icosahedron with Orbit ---
ax2 = fig.add_subplot(2, 3, 2, projection='3d')
from itertools import combinations
ico_edges = []
for i, j in combinations(range(len(icos_verts)), 2):
    if np.linalg.norm(icos_verts[i] - icos_verts[j]) < 1.2:
        ico_edges.append((i, j))

for i, j in ico_edges:
    ax2.plot3D([icos_verts[i,0], icos_verts[j,0]], 
               [icos_verts[i,1], icos_verts[j,1]], 
               [icos_verts[i,2], icos_verts[j,2]], 'k-', alpha=0.15, lw=0.5)

for i in range(len(projections_3d)):
    j = (i + 1) % len(projections_3d)
    ax2.plot3D([projections_3d[i,0], projections_3d[j,0]],
               [projections_3d[i,1], projections_3d[j,1]],
               [projections_3d[i,2], projections_3d[j,2]], 
               'b-', alpha=0.6, lw=2)

for i, (p3d, c) in enumerate(zip(projections_3d, colors)):
    ax2.scatter(p3d[0], p3d[1], p3d[2], c=color_map[c], s=150, edgecolors='black', linewidth=1.5)

ax2.set_title('3D Projection: Orbit on Icosahedron', fontsize=12, fontweight='bold')
ax2.set_box_aspect([1,1,1])

# --- Plot 3: Edge Length Distribution ---
ax3 = fig.add_subplot(2, 3, 3)
x_pos = range(len(edge_lengths_3d))
bars = ax3.bar(x_pos, edge_lengths_3d, color=[color_map[colors[i]] for i in range(len(colors))], 
               edgecolor='black', alpha=0.8)
ax3.axhline(y=np.mean(edge_lengths_3d), color='red', linestyle='--', label=f'Mean: {np.mean(edge_lengths_3d):.3f}')
ax3.axhline(y=np.mean(edge_lengths_3d) + np.std(edge_lengths_3d), color='red', linestyle=':', alpha=0.5)
ax3.axhline(y=np.mean(edge_lengths_3d) - np.std(edge_lengths_3d), color='red', linestyle=':', alpha=0.5)
ax3.set_xlabel('Edge Index', fontsize=11)
ax3.set_ylabel('3D Edge Length', fontsize=11)
ax3.set_title('Edge Length Distribution (3D)', fontsize=12, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels([f'{unique_visited[i]}->{unique_visited[(i+1)%len(unique_visited)]}' for i in range(len(unique_visited))], 
                    rotation=45, ha='right', fontsize=8)
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# --- Plot 4: Color Sequence Over Orbit ---
ax4 = fig.add_subplot(2, 3, 4)
ticks = range(len(colors))
ax4.scatter(ticks, colors, c=[color_map[c] for c in colors], s=150, edgecolors='black', linewidth=1.5, zorder=5)
for i in range(len(colors) - 1):
    ax4.plot([i, i+1], [colors[i], colors[i+1]], 'k-', alpha=0.5, lw=1.5)
ax4.plot([len(colors)-1, 0], [colors[-1], colors[0]], 'k-', alpha=0.5, lw=1.5)
for i, (t, c) in enumerate(zip(ticks, colors)):
    ax4.annotate(f'DH{unique_visited[i]}', (t, c), textcoords="offset points", 
                xytext=(0, 12), ha='center', fontsize=8)
for c in range(5):
    ax4.axhline(y=c, color='gray', linestyle='--', alpha=0.2)
ax4.set_xlabel('Orbit Step', fontsize=11)
ax4.set_ylabel('Color State', fontsize=11)
ax4.set_title('Color Sequence (5-Color Cycle)', fontsize=12, fontweight='bold')
ax4.set_ylim(-0.5, 4.5)
ax4.set_yticks([0, 1, 2, 3, 4])
ax4.set_yticklabels([color_names[i] for i in range(5)])
ax4.grid(True, alpha=0.3)

# --- Plot 5: Distance Matrix Heatmap ---
ax5 = fig.add_subplot(2, 3, 5)
im = ax5.imshow(dist_matrix_3d, cmap='viridis', aspect='auto')
ax5.set_xticks(range(len(unique_visited)))
ax5.set_yticks(range(len(unique_visited)))
ax5.set_xticklabels([f'DH{i}' for i in unique_visited], fontsize=8)
ax5.set_yticklabels([f'DH{i}' for i in unique_visited], fontsize=8)
ax5.set_xlabel('Deep Hole Index', fontsize=11)
ax5.set_ylabel('Deep Hole Index', fontsize=11)
ax5.set_title('3D Distance Matrix', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax5, label='Euclidean Distance')
for i in range(len(unique_visited)):
    for j in range(len(unique_visited)):
        if i != j:
            ax5.text(j, i, f'{dist_matrix_3d[i,j]:.2f}', ha='center', va='center', 
                    fontsize=6, color='white' if dist_matrix_3d[i,j] > 1.5 else 'black')

# --- Plot 6: Orbit Graph Structure ---
ax6 = fig.add_subplot(2, 3, 6)
n = len(unique_visited)
angles_graph = np.linspace(0, 2*np.pi, n, endpoint=False)
graph_x = np.cos(angles_graph)
graph_y = np.sin(angles_graph)

for i in range(n):
    j = (i + 1) % n
    ax6.annotate('', xy=(graph_x[j], graph_y[j]), xytext=(graph_x[i], graph_y[i]),
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.6, lw=1.5,
                              connectionstyle="arc3,rad=0.1"))

for i, (x, y, c) in enumerate(zip(graph_x, graph_y, colors)):
    circle = plt.Circle((x, y), 0.12, color=color_map[c], ec='black', linewidth=2, zorder=5)
    ax6.add_patch(circle)
    ax6.text(x, y, str(unique_visited[i]), ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white', zorder=6)

for i in range(n):
    j = (i + 1) % n
    mid_x = (graph_x[i] + graph_x[j]) / 2 * 1.3
    mid_y = (graph_y[i] + graph_y[j]) / 2 * 1.3
    ax6.text(mid_x, mid_y, f'{edge_lengths_3d[i]:.2f}', ha='center', va='center',
            fontsize=8, color='darkblue', 
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))

ax6.set_xlim(-1.6, 1.6)
ax6.set_ylim(-1.6, 1.6)
ax6.set_aspect('equal')
ax6.set_title('Orbit Graph: 11-Cycle on Icosahedron', fontsize=12, fontweight='bold')
ax6.axis('off')

plt.tight_layout()
plt.savefig('RC-122_Visualization.png', dpi=200, bbox_inches='tight')
plt.show()

print("\n[Saved] RC-122_Visualization.png")
print("\n" + "=" * 70)
print("RC-122 EXECUTION COMPLETE")
print("=" * 70)
