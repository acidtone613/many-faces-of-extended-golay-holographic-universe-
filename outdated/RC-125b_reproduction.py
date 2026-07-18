#!/usr/bin/env python3
"""
RC-125b: The Causal Cone and Information Horizon of the Floquet Engine
Framework: 24D-DMF v8.4.3
Date: 2026-07-08
Seed: 125

Dependencies: numpy, scipy, matplotlib, scikit-learn
"""

import numpy as np
from itertools import permutations, product, combinations
from collections import deque
from scipy.stats import pearsonr, spearmanr
from scipy.sparse.csgraph import shortest_path
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

SEED = 125
np.random.seed(SEED)

print("=" * 70)
print("RC-125b: THE CAUSAL CONE AND INFORMATION HORIZON")
print("Framework: 24D-DMF v8.4.3")
print("Date: 2026-07-08")
print("=" * 70)

# =============================================================================
# PART 1: BUILD GOLAY CODE G24
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
# PART 7: ICOSAHEDRON VERTICES
# =============================================================================
print("\n[STEP 5] Building icosahedron...")

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

n_icos = len(icos_verts)
adj_matrix = np.zeros((n_icos, n_icos))
for i, j in combinations(range(n_icos), 2):
    dist = np.linalg.norm(icos_verts[i] - icos_verts[j])
    if dist < 1.2:
        adj_matrix[i, j] = 1
        adj_matrix[j, i] = 1

print(f"  Icosahedron vertices: {n_icos}")

# =============================================================================
# PART 8: COMPUTE 253-TICK ORBIT AND ARRIVAL TIMES
# =============================================================================
print("\n[STEP 6] Computing 253-tick orbit and arrival times...")

orbit_sequence = []
current_h = deep_hole(0).copy()
visited_indices = []

for t in range(253):
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

    if t < 252:
        current_h = apply_tick_vector(current_h, t)

# Find period
period = None
for p in range(1, 253):
    if all(visited_indices[t] == visited_indices[t + p] for t in range(len(visited_indices) - p)):
        period = p
        break

arrival_times = {}
for t, idx in enumerate(visited_indices):
    if idx not in arrival_times:
        arrival_times[idx] = t

visited = sorted(arrival_times.keys())
unvisited = [j for j in range(24) if j not in arrival_times]

print(f"  Orbit period: {period}")
print(f"  Visited: {len(visited)} of 24")
print(f"  Visited: {visited}")
print(f"  Unvisited: {unvisited}")

# =============================================================================
# PART 9: COMPUTE GRAPH DISTANCES
# =============================================================================
print("\n[STEP 7] Computing graph distances...")

# Quaternion embeddings for deep holes
quaternions_dh = np.zeros((24, 4))
for dh_idx in range(24):
    q = np.zeros(4)
    hi = deep_hole(dh_idx)
    for i in range(24):
        q += hi[i] * quaternions_24[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
    quaternions_dh[dh_idx] = q

# 24-cell graph distances
dist_24cell = squareform(pdist(quaternions_dh, metric='euclidean'))
adj_24cell = np.zeros((24, 24))
for i in range(24):
    neighbors = np.argsort(dist_24cell[i])[1:9]
    for j in neighbors:
        adj_24cell[i, j] = 1
        adj_24cell[j, i] = 1

graph_dist_24cell = shortest_path(adj_24cell, directed=False, unweighted=True)

# Icosahedron mapping
def project_to_3d(hi):
    v = hi.reshape(1, -1)
    q = np.zeros(4)
    for i in range(24):
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

deep_hole_3d = np.array([project_to_3d(deep_hole(i)) for i in range(24)])

dh_to_icos = []
for p3d in deep_hole_3d:
    best_dist = float('inf')
    best_idx = -1
    for i, iv in enumerate(icos_verts):
        d = min(np.linalg.norm(p3d - iv), np.linalg.norm(p3d + iv))
        if d < best_dist:
            best_dist = d
            best_idx = i
    dh_to_icos.append(best_idx)

dh_to_icos = np.array(dh_to_icos)

icos_geodesic = shortest_path(adj_matrix, directed=False, unweighted=True)
graph_dist_icos = np.zeros((24, 24))
for i in range(24):
    for j in range(24):
        graph_dist_icos[i, j] = icos_geodesic[dh_to_icos[i], dh_to_icos[j]]

print("  Graph distances computed.")

# =============================================================================
# PART 10: CORRELATION ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("CORRELATION ANALYSIS")
print("=" * 70)

visited_no_source = [j for j in visited if j != 0]
d24_visited = [graph_dist_24cell[0, j] for j in visited_no_source]
t_visited = [arrival_times[j] for j in visited_no_source]
dicos_visited = [graph_dist_icos[0, j] for j in visited_no_source]

print(f"\n  Visited (excl. source): {visited_no_source}")
print(f"  Arrival times:          {t_visited}")
print(f"  24-cell distances:      {d24_visited}")
print(f"  Icosahedron distances:  {dicos_visited}")

if len(visited_no_source) >= 2:
    r24, p24 = pearsonr(d24_visited, t_visited)
    ricos, picos = pearsonr(dicos_visited, t_visited)
    s24, _ = spearmanr(d24_visited, t_visited)
    sicos, _ = spearmanr(dicos_visited, t_visited)

    print(f"\n  24-cell:     Pearson r={r24:+.4f} (p={p24:.4f}), Spearman ρ={s24:+.4f}")
    print(f"  Icosahedron: Pearson r={ricos:+.4f} (p={picos:.4f}), Spearman ρ={sicos:+.4f}")

    if len(set(d24_visited)) > 1:
        slope_24, intercept_24 = np.polyfit(d24_visited, t_visited, 1)
        print(f"\n  24-cell fit: T = {slope_24:.3f} * d + {intercept_24:.3f}")

    if len(set(dicos_visited)) > 1:
        slope_icos, intercept_icos = np.polyfit(dicos_visited, t_visited, 1)
        print(f"  Icosahedron fit: T = {slope_icos:.3f} * d + {intercept_icos:.3f}")

# =============================================================================
# PART 11: CONE CONNECTEDNESS
# =============================================================================
print("\n" + "=" * 70)
print("CONE CONNECTEDNESS")
print("=" * 70)

visited_set = set(visited)

# BFS from source in 24-cell
queue = deque([0])
connected_24 = {0}
while queue:
    node = queue.popleft()
    for neighbor in range(24):
        if adj_24cell[node, neighbor] == 1 and neighbor in visited_set and neighbor not in connected_24:
            connected_24.add(neighbor)
            queue.append(neighbor)

is_connected_24 = connected_24 == visited_set

# BFS from source in icosahedron
source_icos = dh_to_icos[0]
icos_visited_set = set(dh_to_icos[j] for j in visited)
connected_icos = {source_icos}
queue = deque([source_icos])
while queue:
    node = queue.popleft()
    for neighbor in range(n_icos):
        if adj_matrix[node, neighbor] == 1 and neighbor in icos_visited_set and neighbor not in connected_icos:
            connected_icos.add(neighbor)
            queue.append(neighbor)

is_connected_icos = connected_icos == icos_visited_set

print(f"\n  24-cell:     Connected? {is_connected_24}")
print(f"  Icosahedron: Connected? {is_connected_icos}")

# =============================================================================
# PART 12: FALSIFICATION CRITERIA
# =============================================================================
print("\n" + "=" * 70)
print("FALSIFICATION CRITERIA")
print("=" * 70)

f1_pass = len(unvisited) > 0
f2_pass_24 = r24 > 0.5 and slope_24 > 0 if 'slope_24' in dir() else False
f2_pass_icos = ricos > 0.5 and slope_icos > 0 if 'slope_icos' in dir() else False
f2_pass = f2_pass_24 or f2_pass_icos
f3_pass = is_connected_24 or is_connected_icos

print(f"\n  F1 (Horizon):     {'PASS' if f1_pass else 'FAIL'}")
print(f"  F2 (Finite Speed): {'PASS' if f2_pass else 'FAIL'}")
print(f"  F3 (Connected):   {'PASS' if f3_pass else 'FAIL'}")

score = sum([f1_pass, f2_pass, f3_pass])
print(f"\n  Score: {score}/3")

print("\n" + "─" * 70)
if score == 3:
    verdict = "PASS (Full) — Strong causal locality."
elif f1_pass and f3_pass:
    verdict = "PARTIAL — Horizon + connected cone, but no constant speed."
elif f1_pass:
    verdict = "WEAK — Horizon exists, but disconnected and no constant speed."
else:
    verdict = "FAIL — No horizon, no causal structure."
print(f"  VERDICT: {verdict}")
print("─" * 70)

# =============================================================================
# PART 13: VISUALIZATION
# =============================================================================
print("\n[STEP 8] Generating visualization...")

fig = plt.figure(figsize=(20, 14))

# Plot 1: Arrival time vs 24-cell distance
ax1 = fig.add_subplot(2, 3, 1)
all_d24 = [graph_dist_24cell[0, j] for j in range(24)]
all_t = [arrival_times.get(j, 260) for j in range(24)]
colors = ['green' if j in visited else 'red' for j in range(24)]
ax1.scatter(all_d24, all_t, c=colors, s=100, edgecolors='black', zorder=5)
for j in range(24):
    ax1.annotate(f'DH{j}', (all_d24[j], all_t[j]), textcoords="offset points", 
                xytext=(5, 5), fontsize=8, alpha=0.7)
ax1.set_xlabel('24-Cell Graph Distance from DH0', fontsize=10)
ax1.set_ylabel('Arrival Time (ticks)', fontsize=10)
ax1.set_title(f'Arrival Time vs 24-Cell Distance\n(r={r24:.2f})', fontsize=11, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-5, 265)
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='green', edgecolor='black', label='Visited'),
                   Patch(facecolor='red', edgecolor='black', label='Horizon')]
ax1.legend(handles=legend_elements, loc='upper left')

# Plot 2: Arrival time vs Icosahedron distance
ax2 = fig.add_subplot(2, 3, 2)
all_dicos = [graph_dist_icos[0, j] for j in range(24)]
ax2.scatter(all_dicos, all_t, c=colors, s=100, edgecolors='black', zorder=5)
for j in range(24):
    ax2.annotate(f'DH{j}', (all_dicos[j], all_t[j]), textcoords="offset points", 
                xytext=(5, 5), fontsize=8, alpha=0.7)
ax2.set_xlabel('Icosahedron Graph Distance from DH0', fontsize=10)
ax2.set_ylabel('Arrival Time (ticks)', fontsize=10)
ax2.set_title(f'Arrival Time vs Icosahedron Distance\n(r={ricos:.2f})', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-5, 265)
ax2.legend(handles=legend_elements, loc='upper left')

# Plot 3: 3D Icosahedron
ax3 = fig.add_subplot(2, 3, 3, projection='3d')
for i, j in combinations(range(n_icos), 2):
    if adj_matrix[i, j] == 1:
        ax3.plot3D([icos_verts[i,0], icos_verts[j,0]], 
                   [icos_verts[i,1], icos_verts[j,1]], 
                   [icos_verts[i,2], icos_verts[j,2]], 'k-', alpha=0.15, lw=0.5)

visited_icos = set(dh_to_icos[j] for j in visited)
unvisited_icos = set(dh_to_icos[j] for j in unvisited)

for v in visited_icos:
    ax3.scatter(icos_verts[v,0], icos_verts[v,1], icos_verts[v,2], 
                c='green', s=200, edgecolors='black', linewidth=2, zorder=5)
    dhs_at_v = [j for j in visited if dh_to_icos[j] == v]
    ax3.text(icos_verts[v,0], icos_verts[v,1], icos_verts[v,2], 
             f'V{v}\n{",".join(f"DH{j}" for j in dhs_at_v)}', 
             fontsize=7, ha='center', color='darkgreen')

for v in unvisited_icos:
    ax3.scatter(icos_verts[v,0], icos_verts[v,1], icos_verts[v,2], 
                c='red', s=200, edgecolors='black', linewidth=2, zorder=5, marker='x')
    dhs_at_v = [j for j in unvisited if dh_to_icos[j] == v]
    ax3.text(icos_verts[v,0], icos_verts[v,1], icos_verts[v,2], 
             f'V{v}\n{",".join(f"DH{j}" for j in dhs_at_v)}', 
             fontsize=7, ha='center', color='darkred')

ax3.set_title('Icosahedron: Visited vs Unvisited', fontsize=11, fontweight='bold')
ax3.set_box_aspect([1,1,1])

# Plot 4: 24-Cell graph (MDS layout)
ax4 = fig.add_subplot(2, 3, 4)
mds = MDS(n_components=2, dissimilarity='precomputed', random_state=SEED, normalized_stress=False)
pos_24 = mds.fit_transform(dist_24cell)

for i in range(24):
    for j in range(i+1, 24):
        if adj_24cell[i, j] == 1:
            ax4.plot([pos_24[i,0], pos_24[j,0]], [pos_24[i,1], pos_24[j,1]], 
                     'gray', alpha=0.3, lw=0.5)

for j in range(24):
    if j in visited:
        ax4.scatter(pos_24[j,0], pos_24[j,1], c='green', s=150, edgecolors='black', zorder=5)
        ax4.annotate(f'DH{j}\nT={arrival_times[j]}', (pos_24[j,0], pos_24[j,1]), 
                    textcoords="offset points", xytext=(5, 5), fontsize=7, color='darkgreen')
    else:
        ax4.scatter(pos_24[j,0], pos_24[j,1], c='red', s=150, edgecolors='black', zorder=5, marker='x')
        ax4.annotate(f'DH{j}', (pos_24[j,0], pos_24[j,1]), 
                    textcoords="offset points", xytext=(5, 5), fontsize=7, color='darkred')

ax4.set_title('24-Cell Graph: Visited vs Unvisited', fontsize=11, fontweight='bold')
ax4.set_aspect('equal')
ax4.axis('off')

# Plot 5: Orbit trajectory
ax5 = fig.add_subplot(2, 3, 5)
ticks = range(len(visited_indices[:period]))
ax5.plot(ticks, visited_indices[:period], 'o-', color='steelblue', markersize=6, linewidth=1.5)
ax5.set_xlabel('Tick', fontsize=10)
ax5.set_ylabel('Deep Hole Index', fontsize=10)
ax5.set_title(f'Orbit Trajectory (Period={period})', fontsize=11, fontweight='bold')
ax5.set_yticks(range(24))
ax5.grid(True, alpha=0.3)
for j in range(24):
    if j not in visited:
        ax5.axhline(y=j, color='red', alpha=0.1, linestyle='--')

# Plot 6: Causal cone diagram
ax6 = fig.add_subplot(2, 3, 6)
ax6.fill_between([0, 3], [0, 0], [0, 3*3], alpha=0.2, color='blue', label='Light cone (v=1)')
ax6.fill_between([0, 3], [0, 0], [0, 3*6], alpha=0.1, color='green', label='Actual cone')

for j in visited:
    d = graph_dist_24cell[0, j]
    t = arrival_times[j]
    ax6.scatter(d, t, c='green', s=100, edgecolors='black', zorder=5)
    ax6.annotate(f'DH{j}', (d, t), textcoords="offset points", xytext=(5, 5), fontsize=8)

for j in unvisited:
    d = graph_dist_24cell[0, j]
    ax6.scatter(d, 260, c='red', s=100, marker='x', edgecolors='black', zorder=5)
    ax6.annotate(f'DH{j}', (d, 260), textcoords="offset points", xytext=(5, 5), fontsize=8)

ax6.set_xlabel('24-Cell Graph Distance', fontsize=10)
ax6.set_ylabel('Time (ticks)', fontsize=10)
ax6.set_title('Causal Cone Diagram', fontsize=11, fontweight='bold')
ax6.set_ylim(-5, 270)
ax6.legend(loc='upper left')
ax6.grid(True, alpha=0.3)

plt.suptitle('RC-125b: The Causal Cone and Information Horizon', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('RC-125b_Visualization.png', dpi=200, bbox_inches='tight')
plt.show()

print("\n[Saved] RC-125b_Visualization.png")
print("\n" + "=" * 70)
print("RC-125b EXECUTION COMPLETE")
print("=" * 70)
