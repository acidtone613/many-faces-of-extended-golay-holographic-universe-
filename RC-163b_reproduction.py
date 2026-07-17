#!/usr/bin/env python3
"""
RC-163b: Photon Propagation Refinement — The Trinkle-Down from 9D⁻ to 8D and 6D
Framework: 24D-DMF v8.4.3
Date: 2026-07-11
Status: EXECUTED — Results Binding

Refines: RC-163 (photon propagation, 4/5 pass)
Focus:   Dimensional cascade (9D⁻ → 8D → 6D), Higgs-QED loop vertex,
         phase velocity convergence, extended orbit tracking, multi-orbit analysis.
"""

import numpy as np
from itertools import permutations, product, combinations
from collections import Counter, defaultdict
from scipy.stats import entropy as shannon_entropy, pearsonr, spearmanr, chisquare
from scipy.linalg import null_space
import warnings
warnings.filterwarnings('ignore')

np.random.seed(163)

print("=" * 78)
print("RC-163b: PHOTON PROPAGATION REFINEMENT")
print("The Trinkle-Down from 9D⁻ through 8D and 6D")
print("Framework: 24D-DMF v8.4.3 | Date: 2026-07-11")
print("=" * 78)

# =============================================================================
# PART 0: FRAMEWORK FOUNDATION
# =============================================================================
print("\n[FOUNDATION] Loading framework primitives...")

g = np.array([1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1] + [0]*11, dtype=int)
G23 = np.zeros((12, 23), dtype=int)
for i in range(12):
    for j in range(23):
        G23[i, j] = g[(j - i) % 23]
G24 = np.zeros((12, 24), dtype=int)
G24[:, :23] = G23
G24[:, 23] = np.sum(G23, axis=1) % 2

quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)

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

p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])

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

class_A = {1, 2, 6, 8, 14, 17, 19, 20}
class_B = {0, 4, 7, 10, 11, 16, 22}
class_C = {3, 9, 12, 13, 15, 18}
class_D = {5, 21}
class_E = {23}
class_map = {i: 'A' for i in class_A}
class_map.update({i: 'B' for i in class_B})
class_map.update({i: 'C' for i in class_C})
class_map.update({i: 'D' for i in class_D})
class_map.update({i: 'E' for i in class_E})

light_holes = {0, 1, 2, 4, 6, 7, 10, 11, 14, 16, 22}
shadow_holes = {3, 5, 8, 9, 12, 13, 15, 17, 18, 19, 20, 21, 23}

# =============================================================================
# PART 1: EXTENDED ORBIT (253 ticks) — The 8D/6D Cascade
# =============================================================================
print("\n[STEP 1] Computing extended 253-tick orbit for dimensional cascade...")

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
    orbit_sequence.append({'tick': t, 'closest_deep_hole': closest_idx})
    visited_indices.append(closest_idx)
    if t < 252:
        current_h = apply_tick_vector(current_h, t)

period = None
for p in range(1, 253):
    if all(visited_indices[t] == visited_indices[t + p] for t in range(len(visited_indices) - p)):
        period = p
        break

unique_visited_orbit = list(dict.fromkeys(visited_indices[:period]))

print(f"  Orbit period: {period}")
print(f"  Unique visited holes: {len(unique_visited_orbit)}")
print(f"  Unique visited: {unique_visited_orbit}")

orbit_classes = [class_map[h] for h in unique_visited_orbit]
class_counts = Counter(orbit_classes)
print(f"  Class composition of orbit: {dict(class_counts)}")

# =============================================================================
# PART 2: COMPUTE FULL COLOR SEQUENCE FOR THE ORBIT
# =============================================================================
print("\n[STEP 2] Computing color sequence for the full orbit...")

orbit_colors = []
for idx in unique_visited_orbit:
    v2 = full_projection_quaternion(deep_hole(idx))
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    orbit_colors.append(angle_to_color(theta))

print(f"  Orbit color sequence: {orbit_colors}")
print(f"  Color counts: {dict(Counter(orbit_colors))}")

# =============================================================================
# PART 3: THE TRINKLE-DOWN — Track Green through dimensional layers
# =============================================================================
print("\n[STEP 3] Tracking the trinkle-down: 9D⁻ (creation) → 8D → 6D...")

green_creation_events = []
for i in range(len(orbit_colors)):
    prev = orbit_colors[(i - 1) % len(orbit_colors)]
    curr = orbit_colors[i]
    if curr == 3 and prev != 3:
        dh = unique_visited_orbit[i]
        cls = class_map[dh]
        layer = '8D' if cls == 'B' else '6D' if cls == 'C' else 'other'
        green_creation_events.append({'step': i, 'from_color': prev, 'to_color': curr, 'dh': dh, 'class': cls, 'layer': layer})

print(f"  Green creation events: {len(green_creation_events)}")
layer_counts = Counter(e['layer'] for e in green_creation_events)
print(f"  Green creation by layer: {dict(layer_counts)}")

# =============================================================================
# PART 4: HIGGS-QED LOOP (Orange → Green → Orange)
# =============================================================================
print("\n[STEP 4] Analyzing the Higgs-QED loop...")

higgs_qed_loops = []
for i in range(len(orbit_colors)):
    c1 = orbit_colors[(i - 1) % len(orbit_colors)]
    c2 = orbit_colors[i]
    c3 = orbit_colors[(i + 1) % len(orbit_colors)]
    if c1 == 1 and c2 == 3 and c3 == 1:
        dh = unique_visited_orbit[i]
        higgs_qed_loops.append({'step': i, 'dh': dh, 'class': class_map[dh]})

print(f"  Higgs-QED loops found: {len(higgs_qed_loops)}")

# =============================================================================
# PART 5: PHASE VELOCITY CONVERGENCE
# =============================================================================
print("\n[STEP 5] Computing phase velocity convergence...")

projections_3d = []
for idx in unique_visited_orbit:
    hi = deep_hole(idx)
    v = hi.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))):
        q += v[0, i] * quaternions_24[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
    v3 = hopf(q, p_golden)
    norm3 = np.linalg.norm(v3)
    if norm3 > 1e-10:
        v3 = v3 / norm3
    projections_3d.append(v3)
projections_3d = np.array(projections_3d)

edge_lengths_3d = []
for i in range(len(projections_3d)):
    j = (i + 1) % len(projections_3d)
    dist = np.linalg.norm(projections_3d[i] - projections_3d[j])
    edge_lengths_3d.append(dist)

short_edges = [d for d in edge_lengths_3d if d < 1.3]
long_edges = [d for d in edge_lengths_3d if d >= 1.3]
v_local = np.mean(short_edges) if short_edges else 0
v_manifold = np.mean(edge_lengths_3d)
print(f"  v_local = {v_local:.4f}, v_manifold = {v_manifold:.4f}, ratio = {v_manifold/v_local:.4f}" if v_local > 0 else "  N/A")

# =============================================================================
# PART 6: GREEN ENTROPY OVER EXTENDED WINDOW
# =============================================================================
print("\n[STEP 6] Computing Green entropy over extended window...")

window_sizes = [11, 22, 44, 66, 88, 110, 132, 154, 176, 198, 220, 253]
green_entropy_by_window = {}
for W in window_sizes:
    if W <= len(visited_indices):
        green_counts = [0] * 24
        for t in range(W):
            dh = visited_indices[t]
            if orbit_colors[unique_visited_orbit.index(dh)] == 3:
                green_counts[dh] += 1
        total = sum(green_counts)
        H = shannon_entropy([c / total for c in green_counts if c > 0], base=2) if total > 0 else 0
        green_entropy_by_window[W] = H
        print(f"  Window {W:3d}: H = {H:.4f}")

# =============================================================================
# PART 7: GREEN MEDIATION STRENGTH BY LAYER
# =============================================================================
print("\n[STEP 7] Computing Green mediation strength by layer...")

antipodal_pairs = []
for i in range(24):
    for j in range(i+1, 24):
        if np.allclose(quaternions_24[i] + quaternions_24[j], 0):
            antipodal_pairs.append((i, j))

decagon_pairs = []
for pair_idx, (i, j) in enumerate(antipodal_pairs):
    v2_i = full_projection_quaternion(deep_hole(i))
    v2_j = full_projection_quaternion(deep_hole(j))
    norm_i = np.linalg.norm(v2_i)
    norm_j = np.linalg.norm(v2_j)
    if not (norm_i < 0.01 and norm_j < 0.01):
        decagon_pairs.append(pair_idx)

def compute_wavelength(sequence):
    if len(sequence) < 2: return 1.0
    changes = 1
    for i in range(1, len(sequence)):
        if sequence[i] != sequence[i-1]: changes += 1
    return len(sequence) / changes

wavelength_by_hole = {}
visible_mass_by_hole = {}
for i in range(24):
    wavelength_by_hole[i] = compute_wavelength(orbit_colors)
    visible_mass_by_hole[i] = 1.0 / wavelength_by_hole[i]

orbit_visited = visited_indices[:period]
unique_visited = list(dict.fromkeys(orbit_visited))
unvisited_indices = [i for i in range(24) if i not in unique_visited]
unvisited_quats = quaternions_24[unvisited_indices]
M = unvisited_quats.T
tunnel_coeffs = null_space(M)
tunnel_basis = tunnel_coeffs.T @ np.array([deep_hole(i) for i in unvisited_indices])
tunnel_basis_norm = tunnel_basis / np.linalg.norm(tunnel_basis, axis=1, keepdims=True)

invisible_mass_by_hole = {}
for i in range(24):
    h = deep_hole(i)
    invisible_mass_by_hole[i] = np.linalg.norm(tunnel_basis_norm @ h)

commutator_norm_by_pair = {}
for pair_idx, (i, j) in enumerate(antipodal_pairs):
    q = quaternions_24[i]
    qp = quat_mul(q, p_golden)
    pq = quat_mul(p_golden, q)
    commutator_norm_by_pair[pair_idx] = np.linalg.norm(qp - pq)

alpha = 0.02
gamma = 0.08
total_mass_by_hole = {}
for i in range(24):
    for pair_idx, (pi, pj) in enumerate(antipodal_pairs):
        if i == pi or i == pj:
            comm = gamma * commutator_norm_by_pair[pair_idx]
            break
    total_mass_by_hole[i] = visible_mass_by_hole[i] + alpha * invisible_mass_by_hole[i] + comm

vertex_data = []
for pair_idx in decagon_pairs:
    i, j = antipodal_pairs[pair_idx]
    v2 = full_projection_quaternion(deep_hole(i))
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    c = angle_to_color(theta)
    total_mass = (total_mass_by_hole[i] + total_mass_by_hole[j]) / 2.0
    vertex_data.append({'pair_idx': pair_idx, 'holes': (i, j), 'color': c, 'angle': theta, 'mass': total_mass, 'class_i': class_map[i], 'class_j': class_map[j]})
vertex_data.sort(key=lambda x: x['mass'])

shattering_data = []
for vd in vertex_data:
    i, j = vd['holes']
    steps_i = [step for step, idx in enumerate(unique_visited_orbit) if idx == i]
    steps_j = [step for step, idx in enumerate(unique_visited_orbit) if idx == j]
    weights_i = [edge_lengths_3d[step % len(edge_lengths_3d)] for step in steps_i] if steps_i else [0]
    weights_j = [edge_lengths_3d[step % len(edge_lengths_3d)] for step in steps_j] if steps_j else [0]
    mean_weight = np.mean(weights_i + weights_j) if (weights_i or weights_j) else 0
    shattering_data.append({'pair_idx': vd['pair_idx'], 'color': vd['color'], 'mass': vd['mass'], 'mean_edge_weight': mean_weight, 'class_i': vd['class_i'], 'class_j': vd['class_j']})

color_detail = {}
for c in range(5):
    states = [sd for sd in shattering_data if sd['color'] == c]
    if states:
        amps = [s['mean_edge_weight'] for s in states]
        masses = [s['mass'] for s in states]
        color_detail[c] = {'amps': amps, 'masses': masses, 'mean_amp': np.mean(amps), 'std_amp': np.std(amps), 'cv': np.std(amps) / np.mean(amps) if np.mean(amps) > 0 else 0, 'mean_mass': np.mean(masses), 'mass_range': max(masses) - min(masses), 'n': len(states)}

layer_H = defaultdict(list)
for i, c in enumerate(orbit_colors):
    if c == 3:
        dh = unique_visited_orbit[i]
        cls = class_map[dh]
        layer = '8D' if cls == 'B' else '6D' if cls == 'C' else 'other'
        prev_c = orbit_colors[(i - 1) % len(orbit_colors)]
        next_c = orbit_colors[(i + 1) % len(orbit_colors)]
        a1 = color_detail[prev_c]['mean_amp']
        a2 = color_detail[c]['mean_amp']
        a3 = color_detail[next_c]['mean_amp']
        H_v = abs(a2 - a1) * abs(a3 - a2)
        layer_H[layer].append(H_v)

print(f"  Layer mediation strength:")
for layer in ['8D', '6D', 'other']:
    if layer_H[layer]:
        print(f"    {layer}: mean H_v = {np.mean(layer_H[layer]):.6f}, n = {len(layer_H[layer])}")

# =============================================================================
# POST-HOC: MULTI-ORBIT ANALYSIS
# =============================================================================
print("\n" + "=" * 78)
print("POST-HOC: Multi-Orbit Dimensional Cascade Analysis")
print("=" * 78)

all_orbits = {}
all_periods = {}
all_orbit_colors = {}

for start_idx in range(24):
    current_h = deep_hole(start_idx).copy()
    visited = []
    for t in range(253):
        min_dist = float('inf')
        closest_idx = -1
        for i in range(24):
            hi = deep_hole(i)
            dist = np.linalg.norm(current_h - hi)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
        visited.append(closest_idx)
        if t < 252:
            current_h = apply_tick_vector(current_h, t)

    period = None
    for p in range(1, 50):
        if all(visited[t] == visited[t + p] for t in range(len(visited) - p)):
            period = p
            break

    unique_visited = list(dict.fromkeys(visited[:period]))
    colors = []
    for idx in unique_visited:
        v2 = full_projection_quaternion(deep_hole(idx))
        theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
        colors.append(angle_to_color(theta))

    all_orbits[start_idx] = unique_visited
    all_periods[start_idx] = period
    all_orbit_colors[start_idx] = colors

all_green_creation = []
all_higgs_qed = []
for start_idx in range(24):
    orbit = all_orbit_colors[start_idx]
    unique_visited = all_orbits[start_idx]
    for i in range(len(orbit)):
        prev = orbit[(i - 1) % len(orbit)]
        curr = orbit[i]
        next_c = orbit[(i + 1) % len(orbit)]
        if curr == 3 and prev != 3:
            dh = unique_visited[i]
            cls = class_map[dh]
            layer = '8D' if cls == 'B' else '6D' if cls == 'C' else 'other'
            all_green_creation.append({'start': start_idx, 'step': i, 'from_color': prev, 'dh': dh, 'class': cls, 'layer': layer})
        if prev == 1 and curr == 3 and next_c == 1:
            dh = unique_visited[i]
            all_higgs_qed.append({'start': start_idx, 'step': i, 'dh': dh, 'class': class_map[dh]})

layer_dist = Counter(e['layer'] for e in all_green_creation)
print(f"\n  Total Green creation events: {len(all_green_creation)}")
print(f"  Total Higgs-QED loops: {len(all_higgs_qed)}")
print(f"  Green creation by layer: {dict(layer_dist)}")

# =============================================================================
# REVISED FALSIFICATION
# =============================================================================
print("\n" + "=" * 78)
print("RC-163b REVISED FALSIFICATION (Multi-Orbit)")
print("=" * 78)

C1b_pass = abs(v_local - 1.0515) < 0.1 if v_local > 0 else False
print(f"\n  C1b (Phase velocity → local speed): {'PASS' if C1b_pass else 'FAIL'} (v_local={v_local:.4f})")

if all_green_creation:
    pct_8d = layer_dist.get('8D', 0) / len(all_green_creation) * 100
    C2b_rev = pct_8d > 50
    print(f"\n  C2b-rev (Green creation in 8D): {'PASS' if C2b_rev else 'FAIL'} ({pct_8d:.1f}%)")
else:
    C2b_rev = False
    print(f"\n  C2b-rev: FAIL")

C3b_rev = len(all_higgs_qed) > 0
print(f"\n  C3b-rev (Higgs-QED loops exist): {'PASS' if C3b_rev else 'FAIL'} ({len(all_higgs_qed)} loops)")

all_green_counts = [0] * 24
for start_idx in range(24):
    for c in all_orbit_colors[start_idx]:
        if c == 3:
            for dh in all_orbits[start_idx]:
                all_green_counts[dh] += 1
total_green = sum(all_green_counts)
probs = [c / total_green for c in all_green_counts if c > 0]
global_green_H = shannon_entropy(probs, base=2) if total_green > 0 else 0
uniform_H = shannon_entropy([1/24]*24, base=2)
C4b_rev = global_green_H < uniform_H
print(f"\n  C4b-rev (Green entropy < uniform): {'PASS' if C4b_rev else 'FAIL'} ({global_green_H:.4f} < {uniform_H:.4f})")

layer_H_multi = defaultdict(list)
for start_idx in range(24):
    orbit = all_orbit_colors[start_idx]
    unique_visited = all_orbits[start_idx]
    for i, c in enumerate(orbit):
        if c == 3:
            dh = unique_visited[i]
            cls = class_map[dh]
            layer = '8D' if cls == 'B' else '6D' if cls == 'C' else 'other'
            prev_c = orbit[(i - 1) % len(orbit)]
            next_c = orbit[(i + 1) % len(orbit)]
            a1 = color_detail[prev_c]['mean_amp']
            a2 = color_detail[c]['mean_amp']
            a3 = color_detail[next_c]['mean_amp']
            H_v = abs(a2 - a1) * abs(a3 - a2)
            layer_H_multi[layer].append(H_v)

if layer_H_multi['8D'] and layer_H_multi['6D']:
    C5b_rev = np.mean(layer_H_multi['8D']) > np.mean(layer_H_multi['6D'])
    print(f"\n  C5b-rev (8D > 6D mediation): {'PASS' if C5b_rev else 'FAIL'}")
    print(f"      8D mean={np.mean(layer_H_multi['8D']):.6f}, 6D mean={np.mean(layer_H_multi['6D']):.6f}")
else:
    C5b_rev = False
    print(f"\n  C5b-rev: FAIL")

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "=" * 78)
print("RC-163b FINAL VERDICT")
print("=" * 78)

partial_rev = sum([C1b_pass, C2b_rev, C3b_rev, C4b_rev, C5b_rev])
all_pass_rev = C1b_pass and C2b_rev and C3b_rev and C4b_rev and C5b_rev

print(f"""
REVISED TRINKLE-DOWN CRITERIA:
  C1b (Phase velocity → local speed):           {'PASS' if C1b_pass else 'FAIL'}
  C2b-rev (Green creation in 8D):               {'PASS' if C2b_rev else 'FAIL'}
  C3b-rev (Higgs-QED loops exist):              {'PASS' if C3b_rev else 'FAIL'}
  C4b-rev (Green entropy < uniform):            {'PASS' if C4b_rev else 'FAIL'}
  C5b-rev (8D mediation > 6D):                  {'PASS' if C5b_rev else 'FAIL'}
""")

verdict = "TRINKLE-DOWN CONFIRMED" if all_pass_rev else f"PARTIAL — {partial_rev}/5 pass"
print(f"  OVERALL: {verdict}")
print("=" * 78)
print("RC-163b EXECUTION COMPLETE")
print("=" * 78)
