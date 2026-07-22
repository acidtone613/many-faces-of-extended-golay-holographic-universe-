#!/usr/bin/env python3
"""
RC-186: QGP INTERACTION TENSOR — 4D & 5D MANIFOLD COUPLING
Framework: 24D-DMF v8.4.6 | Date: 2026-07-21
"""

import numpy as np
from itertools import product, combinations
from math import log2
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

np.random.seed(186)

print("=" * 80)
print("RC-186: QGP INTERACTION TENSOR — 4D & 5D MANIFOLD COUPLING")
print("Framework: 24D-DMF v8.4.6 | Date: 2026-07-21")
print("=" * 80)

# =============================================================================
# FRAMEWORK FOUNDATION (from RC-185 / RC-122)
# =============================================================================
phi = (1 + np.sqrt(5)) / 2

# Quaternion 24-cell
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

axis_5fold = np.array([0, 1, phi])
axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
e1_s = e1_s / np.linalg.norm(e1_s)
e2_s = np.cross(axis_5fold, e1_s)
e2_s = e2_s / np.linalg.norm(e2_s)

def quaternion_from_24d(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))):
        q += v[0, i] * quaternions_24[i]
    return q

def full_projection_quaternion(v_24d):
    q = quaternion_from_24d(v_24d)
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

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

def project_root_to_color(r_8d):
    v_24d = np.pad(r_8d, (0, 16))
    v2 = full_projection_quaternion(v_24d)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    color = angle_to_color(theta)
    q = quaternion_from_24d(v_24d)
    q_norm = np.linalg.norm(q)
    return color, theta, v2, q_norm

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

def mutual_information(seq1, seq2, bins=5):
    joint = np.zeros((bins, bins))
    for a, b in zip(seq1, seq2):
        joint[a, b] += 1
    joint /= len(seq1)
    marginal1 = np.sum(joint, axis=1)
    marginal2 = np.sum(joint, axis=0)
    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            if joint[i, j] > 0 and marginal1[i] > 0 and marginal2[j] > 0:
                mi += joint[i, j] * log2(joint[i, j] / (marginal1[i] * marginal2[j]))
    return mi

def shannon_entropy(seq):
    counts = Counter(seq)
    entropy = 0.0
    n = len(seq)
    for count in counts.values():
        if count > 0:
            p = count / n
            entropy -= p * log2(p)
    return entropy

# =============================================================================
# GENERATE E8 ROOT SYSTEM
# =============================================================================
print("\n[STEP 1] Generating E8 root system...")

roots = []
for pos in combinations(range(8), 2):
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            r = np.zeros(8)
            r[pos[0]] = s1
            r[pos[1]] = s2
            roots.append(r)

for signs in product([0.5, -0.5], repeat=8):
    if sum(1 for s in signs if s < 0) % 2 == 0:
        roots.append(np.array(signs))

roots = np.array(roots)
print(f"  Total E8 roots: {len(roots)}")

# =============================================================================
# FILTER MIXED ROOTS (192)
# =============================================================================
print("\n[STEP 2] Filtering mixed roots (192)...")

mixed = []
for r in roots:
    nonzero = np.where(np.abs(r) > 1e-10)[0]
    if not (len(nonzero) == 2 and all(nz < 4 for nz in nonzero)):
        if not (len(nonzero) == 2 and all(nz >= 4 for nz in nonzero)):
            mixed.append(r)

mixed = np.array(mixed)
print(f"  Mixed roots: {len(mixed)}")

# =============================================================================
# TASK 1: 4D BULK INTERACTION (Pressure Map)
# =============================================================================
print("\n" + "=" * 80)
print("TASK 1: 4D BULK INTERACTION (Pressure Map)")
print("=" * 80)

print("\n[STEP 3] Building 24-cell skeleton...")
vertices = quaternions_24

edges = []
for i in range(24):
    for j in range(i+1, 24):
        dot = np.dot(vertices[i], vertices[j])
        if abs(dot - 0.5) < 1e-6:
            edges.append((i, j))
print(f"  Edges found: {len(edges)} (expected: 96)")

edge_set = set(edges)
faces = []
for i in range(24):
    for j in range(i+1, 24):
        if (i, j) not in edge_set:
            continue
        for k in range(j+1, 24):
            if (i, k) in edge_set and (j, k) in edge_set:
                faces.append((i, j, k))
print(f"  Faces found: {len(faces)} (expected: 96)")

print("\n[STEP 4] Projecting 192 roots to 4D quaternion space...")
q_4d_list = []
for r in mixed:
    v_24d = np.pad(r, (0, 16))
    q = quaternion_from_24d(v_24d)
    q_4d_list.append(q)
q_4d_array = np.array(q_4d_list)
print(f"  Quaternion array shape: {q_4d_array.shape}")

print("\n[STEP 5] Computing distances to 24-cell skeleton...")
min_dist_vertices = []
nearest_vertex = []
for q in q_4d_array:
    dists = np.linalg.norm(vertices - q, axis=1)
    min_dist_vertices.append(dists.min())
    nearest_vertex.append(dists.argmin())
min_dist_vertices = np.array(min_dist_vertices)
nearest_vertex = np.array(nearest_vertex)

def dist_point_to_segment(p, a, b):
    ab = b - a
    t = np.dot(p - a, ab) / np.dot(ab, ab)
    t = np.clip(t, 0, 1)
    closest = a + t * ab
    return np.linalg.norm(p - closest)

min_dist_edges = []
for q in q_4d_array:
    min_d = float('inf')
    for (i, j) in edges:
        d = dist_point_to_segment(q, vertices[i], vertices[j])
        if d < min_d:
            min_d = d
    min_dist_edges.append(min_d)
min_dist_edges = np.array(min_dist_edges)

def dist_point_to_face_plane(p, v0, v1, v2):
    a = v1 - v0
    b = v2 - v0
    e1 = a / np.linalg.norm(a)
    b_proj = np.dot(b, e1) * e1
    e2 = b - b_proj
    if np.linalg.norm(e2) > 1e-10:
        e2 = e2 / np.linalg.norm(e2)
    else:
        return np.linalg.norm(p - v0)
    diff = p - v0
    proj = np.dot(diff, e1) * e1 + np.dot(diff, e2) * e2
    residual = diff - proj
    return np.linalg.norm(residual)

min_dist_faces = []
for q in q_4d_array:
    min_d = float('inf')
    for (i, j, k) in faces:
        d = dist_point_to_face_plane(q, vertices[i], vertices[j], vertices[k])
        if d < min_d:
            min_d = d
    min_dist_faces.append(min_d)
min_dist_faces = np.array(min_dist_faces)

print(f"  Mean dist to vertices: {min_dist_vertices.mean():.4f}")
print(f"  Mean dist to edges:    {min_dist_edges.mean():.4f}")
print(f"  Mean dist to faces:    {min_dist_faces.mean():.4f}")

vertex_occupancy = np.zeros(24)
for nv in nearest_vertex:
    vertex_occupancy[nv] += 1

vertex_cluster_fraction = np.mean(min_dist_vertices < 0.1)
print(f"\n  Roots within 0.1 of a vertex: {vertex_cluster_fraction*100:.1f}%")
if vertex_cluster_fraction > 0.5:
    print("  INTERPRETATION: Roots behave as PARTICLES (clustered at vertices)")
else:
    print("  INTERPRETATION: Roots behave as FIELD (spread across edges/faces)")

# =============================================================================
# TASK 2: 5D DYNAMIC COUPLING (Flow vs Binding)
# =============================================================================
print("\n" + "=" * 80)
print("TASK 2: 5D DYNAMIC COUPLING (Flow vs Binding)")
print("=" * 80)

MATTER_HOLES = [0, 11, 1, 4, 10, 22, 2, 6, 14, 7, 16]
DARK_MATTER_HOLES = [3, 5, 8, 9, 12, 13, 15, 17, 18, 19, 20, 21, 23]

print(f"\n[STEP 6] Matter holes: {MATTER_HOLES}")
print(f"  Dark Matter holes: {DARK_MATTER_HOLES}")

print("\n[STEP 7] Evolving deep holes through 22-tick Floquet...")

matter_colors = np.zeros((len(MATTER_HOLES), 22), dtype=int)
dark_colors = np.zeros((len(DARK_MATTER_HOLES), 22), dtype=int)

for idx, h_i in enumerate(MATTER_HOLES):
    v = deep_hole(h_i)
    for t in range(22):
        color, theta, v2, q_norm = project_root_to_color(v[:8])
        matter_colors[idx, t] = color
        if t < 21:
            v = apply_tick_vector(v, t)

for idx, h_i in enumerate(DARK_MATTER_HOLES):
    v = deep_hole(h_i)
    for t in range(22):
        color, theta, v2, q_norm = project_root_to_color(v[:8])
        dark_colors[idx, t] = color
        if t < 21:
            v = apply_tick_vector(v, t)

print("\n[STEP 8] Computing 5D Unity MI curve...")
MI_t = []
for t in range(22):
    mi = mutual_information(matter_colors[:, t], dark_colors[:, t])
    MI_t.append(mi)
MI_t = np.array(MI_t)

dMI_dt = np.diff(MI_t)

print(f"  MI(t) range: [{MI_t.min():.4f}, {MI_t.max():.4f}] bits")
print(f"  dMI/dt range: [{dMI_dt.min():.4f}, {dMI_dt.max():.4f}] bits/tick")

print("\n[STEP 9] Evolving 192 mixed roots through 22 ticks...")
root_colors = np.zeros((192, 22), dtype=int)
root_2d = np.zeros((192, 22, 2))

for idx, r in enumerate(mixed):
    v = np.zeros(24)
    v[:8] = r
    for t in range(22):
        color, theta, v2, q_norm = project_root_to_color(v[:8])
        root_colors[idx, t] = color
        root_2d[idx, t] = v2
        if t < 21:
            v = apply_tick_vector(v, t)

print("\n[STEP 10] Computing color density and entropy...")
rho_c = np.zeros((22, 5))
for t in range(22):
    counts = Counter(root_colors[:, t])
    for c in range(5):
        rho_c[t, c] = counts.get(c, 0) / 192.0

entropy_ensemble = np.array([shannon_entropy(root_colors[:, t]) for t in range(22)])

drho_dt = np.diff(rho_c, axis=0)

print("\n[STEP 11] Computing dynamic correlations...")
correlations = []
for c in range(5):
    if np.std(drho_dt[:, c]) > 1e-12 and np.std(dMI_dt) > 1e-12:
        corr = np.corrcoef(drho_dt[:, c], dMI_dt)[0, 1]
    else:
        corr = 0.0
    correlations.append(corr)

drho_total_dt = np.sum(np.abs(drho_dt), axis=1)
if np.std(drho_total_dt) > 1e-12 and np.std(dMI_dt) > 1e-12:
    overall_corr = np.corrcoef(drho_total_dt, dMI_dt)[0, 1]
else:
    overall_corr = 0.0

color_names = ['Red', 'Orange', 'Yellow', 'Green', 'Blue']
print(f"\n  Color correlation with dMI/dt:")
for c in range(5):
    print(f"    {color_names[c]}: {correlations[c]:+.4f}")
print(f"  Overall (|d\u03c1/dt| vs dMI/dt): {overall_corr:+.4f}")

max_corr = max(abs(c) for c in correlations)
if max_corr > 0.5:
    driver_color = color_names[np.argmax(np.abs(correlations))]
    print(f"\n  INTERPRETATION: {driver_color} flow is {'DRIVING' if correlations[np.argmax(np.abs(correlations))] > 0 else 'RESPONDING TO'} Unity binding")
elif overall_corr > 0.5:
    print(f"\n  INTERPRETATION: QGP flow is DRIVING Unity binding (overall corr = {overall_corr:+.4f})")
elif overall_corr < -0.5:
    print(f"\n  INTERPRETATION: QGP flow is RESPONDING to Unity binding (overall corr = {overall_corr:+.4f})")
else:
    print(f"\n  INTERPRETATION: QGP and Unity are ORTHOGONAL systems (max |corr| = {max_corr:.4f})")

# =============================================================================
# TASK 3: ENSEMBLE GEODESIC (Mean Trajectory)
# =============================================================================
print("\n" + "=" * 80)
print("TASK 3: ENSEMBLE GEODESIC (Mean Trajectory)")
print("=" * 80)

centroid = np.mean(root_2d, axis=0)
variance = np.mean(np.sum((root_2d - centroid[None, :, :])**2, axis=2), axis=0)

print("\n[STEP 12] Computing deep-hole orbit projection...")
visited_holes = [0, 11, 1, 4, 10, 22, 2, 6, 14, 7, 16]
dh_orbit_2d = []
for h_i in visited_holes:
    v = deep_hole(h_i)
    color, theta, v2, q_norm = project_root_to_color(v[:8])
    dh_orbit_2d.append(v2)
dh_orbit_2d = np.array(dh_orbit_2d)

dist_to_orbit = []
for t in range(22):
    dists = np.linalg.norm(dh_orbit_2d - centroid[t], axis=1)
    dist_to_orbit.append(dists.min())
dist_to_orbit = np.array(dist_to_orbit)
mean_dist_to_orbit = np.mean(dist_to_orbit)

print(f"\n  Mean distance from centroid to deep-hole orbit: {mean_dist_to_orbit:.4f}")
print(f"  Variance at Tick 11 (H_L): {variance[11]:.4f}")
print(f"  Max variance: {variance.max():.4f} at tick {variance.argmax()}")

if mean_dist_to_orbit < 0.1:
    print("  INTERPRETATION: QGP is SLAVED to deep-hole dynamics")
elif mean_dist_to_orbit > 0.5:
    print("  INTERPRETATION: QGP has INDEPENDENT flow")
else:
    print("  INTERPRETATION: QGP shows PARTIAL coupling to deep-hole orbit")

if variance[11] == variance.max():
    print("  INTERPRETATION: Ensemble maximally spread at H_L reset (Tick 11)")

# =============================================================================
# SAVE CSV DATA
# =============================================================================
print("\n[STEP 13] Saving CSV outputs...")

np.savetxt('/mnt/agents/output/task1_vertex_occupancy.csv',
           np.column_stack([np.arange(24), vertex_occupancy]),
           delimiter=',', header='vertex_index,occupancy', comments='')

task2_data = np.column_stack([np.arange(5), correlations])
np.savetxt('/mnt/agents/output/task2_correlations.csv',
           task2_data, delimiter=',', header='color,correlation_with_dMI_dt', comments='')

task3_data = np.column_stack([np.arange(22), centroid[:, 0], centroid[:, 1], variance, dist_to_orbit])
np.savetxt('/mnt/agents/output/task3_centroid_trajectory.csv',
           task3_data, delimiter=',', header='tick,centroid_x,centroid_y,variance,dist_to_orbit', comments='')

print("  CSV files saved.")

# =============================================================================
# VISUALIZATION
# =============================================================================
print("\n[STEP 14] Generating visualization...")

try:
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(20, 14))

    # Task 1A: Distance histograms
    ax1 = plt.subplot(3, 3, 1)
    max_d = max(min_dist_vertices.max(), min_dist_edges.max(), min_dist_faces.max())
    bins = np.linspace(0, max_d, 30)
    ax1.hist(min_dist_vertices, bins=bins, alpha=0.5, label='Vertices', color='red')
    ax1.hist(min_dist_edges, bins=bins, alpha=0.5, label='Edges', color='green')
    ax1.hist(min_dist_faces, bins=bins, alpha=0.5, label='Faces', color='blue')
    ax1.axvline(x=0.1, color='black', linestyle='--', label='Cluster threshold')
    ax1.set_xlabel('Minimum Distance')
    ax1.set_ylabel('Count')
    ax1.set_title('Task 1A: Distance to 24-Cell Skeleton')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Task 1B: Vertex occupancy heatmap
    ax2 = plt.subplot(3, 3, 2)
    im2 = ax2.imshow(vertex_occupancy.reshape(1, 24), cmap='YlOrRd', aspect='auto')
    ax2.set_xticks(range(24))
    ax2.set_xticklabels([str(i) for i in range(24)], fontsize=7)
    ax2.set_yticks([])
    ax2.set_xlabel('Deep Hole Index')
    ax2.set_title('Task 1B: Vertex Occupancy Heatmap')
    plt.colorbar(im2, ax=ax2)

    # Task 2A: MI vs Entropy
    ax3 = plt.subplot(3, 3, 4)
    ticks = np.arange(22)
    ax3_twin = ax3.twinx()
    ax3.plot(ticks, MI_t, 'b-o', label='MI(Matter,Dark)', markersize=5)
    ax3_twin.plot(ticks, entropy_ensemble, 'r-s', label='Ensemble Entropy', markersize=5)
    ax3.axvline(x=11, color='orange', linestyle=':', alpha=0.7, label='H_L Reset')
    ax3.set_xlabel('Tick')
    ax3.set_ylabel('MI (bits)', color='blue')
    ax3_twin.set_ylabel('Entropy (bits)', color='red')
    ax3.set_title('Task 2A: MI vs Ensemble Entropy')
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    ax3.grid(alpha=0.3)

    # Task 2B: Correlation matrix
    ax4 = plt.subplot(3, 3, 5)
    corr_matrix = np.array(correlations).reshape(5, 1)
    im4 = ax4.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    ax4.set_yticks(range(5))
    ax4.set_yticklabels(['Red', 'Orange', 'Yellow', 'Green', 'Blue'])
    ax4.set_xticks([0])
    ax4.set_xticklabels(['dMI/dt'])
    ax4.set_title('Task 2B: Color Correlation with dMI/dt')
    for i in range(5):
        ax4.text(0, i, f'{correlations[i]:+.3f}', ha='center', va='center',
                color='white' if abs(correlations[i]) > 0.5 else 'black', fontsize=12, fontweight='bold')
    plt.colorbar(im4, ax=ax4)

    # Task 2C: Scatter plot
    ax5 = plt.subplot(3, 3, 6)
    ax5.scatter(dMI_dt, drho_total_dt, c=range(21), cmap='viridis', s=60, edgecolors='black')
    ax5.set_xlabel('dMI/dt (bits/tick)')
    ax5.set_ylabel('|d\u03c1/dt| (total)')
    ax5.set_title(f'Task 2C: Scatter (r={overall_corr:+.3f})')
    ax5.grid(alpha=0.3)

    # Task 3A: Trajectory overlay
    ax6 = plt.subplot(3, 3, 7)
    theta_circle = np.linspace(0, 2*np.pi, 100)
    ax6.plot(np.cos(theta_circle), np.sin(theta_circle), 'k--', alpha=0.3, linewidth=1)
    ax6.scatter(dh_orbit_2d[:, 0], dh_orbit_2d[:, 1], c='red', s=200, marker='o',
                edgecolors='black', label='Deep-Hole Orbit', zorder=5)
    for idx, h_i in enumerate(visited_holes):
        ax6.annotate(str(h_i), (dh_orbit_2d[idx, 0], dh_orbit_2d[idx, 1]),
                    fontsize=8, ha='center', va='center', color='white', fontweight='bold')
    scatter = ax6.scatter(centroid[:, 0], centroid[:, 1], c=range(22), cmap='cool', s=50, zorder=4)
    ax6.plot(centroid[:, 0], centroid[:, 1], 'k-', alpha=0.5, linewidth=1, zorder=3)
    plt.colorbar(scatter, ax=ax6, label='Tick')
    ax6.set_xlabel('X')
    ax6.set_ylabel('Y')
    ax6.set_title('Task 3A: Centroid vs Deep-Hole Orbit')
    ax6.legend()
    ax6.set_aspect('equal')
    ax6.grid(alpha=0.3)

    # Task 3B: Variance
    ax7 = plt.subplot(3, 3, 8)
    ax7.plot(ticks, variance, 'k-o', markersize=5, linewidth=2)
    ax7.axvline(x=11, color='orange', linestyle=':', alpha=0.7, label='H_L Reset')
    ax7.fill_between(ticks, variance, alpha=0.3, color='purple')
    ax7.set_xlabel('Tick')
    ax7.set_ylabel('Variance')
    ax7.set_title('Task 3B: Ensemble Variance Over Time')
    ax7.legend()
    ax7.grid(alpha=0.3)

    # Summary panel
    ax8 = plt.subplot(3, 3, 9)
    ax8.axis('off')
    summary_text = f"""RC-186 SUMMARY
─────────────────────────────
Task 1 — 4D Bulk:
  Vertex cluster (<0.1): {vertex_cluster_fraction*100:.1f}%
  Mean dist (V/E/F): {min_dist_vertices.mean():.3f} / {min_dist_edges.mean():.3f} / {min_dist_faces.mean():.3f}

Task 2 — 5D Coupling:
  Max |color corr|: {max_corr:.4f} ({color_names[np.argmax(np.abs(correlations))]})
  Overall corr: {overall_corr:+.4f}

Task 3 — Geodesic:
  Mean dist to orbit: {mean_dist_to_orbit:.4f}
  Variance at Tick 11: {variance[11]:.4f}
  Max variance: {variance.max():.4f} (tick {variance.argmax()})
"""
    ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig('/mnt/agents/output/RC-186_QGP_Interaction_Tensor.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  Visualization saved.")

except ImportError:
    print("  matplotlib not available — skipping visualization")

# =============================================================================
# FINAL SUMMARY TABLE
# =============================================================================
print("\n" + "=" * 80)
print("RC-186 FINAL SUMMARY TABLE")
print("=" * 80)

interp_task1 = 'PARTICLES' if vertex_cluster_fraction > 0.5 else 'FIELD'
interp_task2 = 'DRIVING' if overall_corr > 0.5 else ('RESPONDING' if overall_corr < -0.5 else 'ORTHOGONAL')
interp_task3 = 'SLAVED' if mean_dist_to_orbit < 0.1 else ('INDEPENDENT' if mean_dist_to_orbit > 0.5 else 'PARTIAL')

print(f"""
| Metric | Value | Interpretation |
|--------|-------|----------------|
| Vertex cluster fraction | {vertex_cluster_fraction*100:.1f}% | {interp_task1} |
| Mean dist to vertices | {min_dist_vertices.mean():.4f} | Bulk proximity |
| Mean dist to edges | {min_dist_edges.mean():.4f} | Edge proximity |
| Mean dist to faces | {min_dist_faces.mean():.4f} | Face proximity |
| Red correlation | {correlations[0]:+.4f} | {'DRIVING' if correlations[0] > 0.5 else ('RESPONDING' if correlations[0] < -0.5 else 'NEUTRAL')} |
| Orange correlation | {correlations[1]:+.4f} | {'DRIVING' if correlations[1] > 0.5 else ('RESPONDING' if correlations[1] < -0.5 else 'NEUTRAL')} |
| Yellow correlation | {correlations[2]:+.4f} | {'DRIVING' if correlations[2] > 0.5 else ('RESPONDING' if correlations[2] < -0.5 else 'NEUTRAL')} |
| Green correlation | {correlations[3]:+.4f} | {'DRIVING' if correlations[3] > 0.5 else ('RESPONDING' if correlations[3] < -0.5 else 'NEUTRAL')} |
| Blue correlation | {correlations[4]:+.4f} | {'DRIVING' if correlations[4] > 0.5 else ('RESPONDING' if correlations[4] < -0.5 else 'NEUTRAL')} |
| Overall correlation | {overall_corr:+.4f} | {interp_task2} |
| Mean dist to DH orbit | {mean_dist_to_orbit:.4f} | {interp_task3} |
| Variance at Tick 11 | {variance[11]:.4f} | {'MAX' if variance[11] == variance.max() else 'Not max'} |
| Max variance (tick) | {variance.max():.4f} ({variance.argmax()}) | Spread peak |

RC-186 STATUS: COMPLETE
""")
print("=" * 80)
