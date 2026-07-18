#!/usr/bin/env python3
"""
RC-166: The Color Engine — Forces, Interactions, and the Role of Yellow
Complete Reproduction Script

Framework: 24D-DMF v8.4.6
Date: 2026-07-11
Status: EXECUTED — Exploratory Data Collection (No Strict Pass/Fail)

Builds on: RC-165 (10-state manifold), RC-156 (vertex Hamiltonian)
"""

import numpy as np
from itertools import product, combinations
from scipy.linalg import null_space
from scipy.stats import pearsonr, entropy
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

np.random.seed(166)

print("=" * 80)
print("RC-166: THE COLOR ENGINE — Forces, Interactions, and the Role of Yellow")
print("Framework: 24D-DMF v8.4.6 | Date: 2026-07-11")
print("Builds on: RC-165 (10-state manifold), RC-156 (vertex Hamiltonian)")
print("=" * 80)

# =============================================================================
# PART 0: FRAMEWORK FOUNDATION
# =============================================================================
print("\n[FOUNDATION] Loading framework primitives...")

# --- Golay Code G24 ---
g = np.array([1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1] + [0]*11, dtype=int)
G23 = np.zeros((12, 23), dtype=int)
for i in range(12):
    for j in range(23):
        G23[i, j] = g[(j - i) % 23]
G24 = np.zeros((12, 24), dtype=int)
G24[:, :23] = G23
G24[:, 23] = np.sum(G23, axis=1) % 2

# --- Quaternion 24-Cell ---
quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)

# --- Deep Holes ---
def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

# --- Floquet Tick ---
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

# --- Hopf Fibration ---
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

# --- Orbit classes ---
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

# --- Antipodal pairs ---
antipodal_pairs = []
for i in range(24):
    for j in range(i+1, 24):
        if np.allclose(quaternions_24[i] + quaternions_24[j], 0):
            antipodal_pairs.append((i, j))

polar_pairs = []
decagon_pairs = []
for pair_idx, (i, j) in enumerate(antipodal_pairs):
    v2_i = full_projection_quaternion(deep_hole(i))
    v2_j = full_projection_quaternion(deep_hole(j))
    norm_i = np.linalg.norm(v2_i)
    norm_j = np.linalg.norm(v2_j)
    if norm_i < 0.01 and norm_j < 0.01:
        polar_pairs.append(pair_idx)
    else:
        decagon_pairs.append(pair_idx)

# --- Build 10 states ---
vertex_data = []
for pair_idx in decagon_pairs:
    i, j = antipodal_pairs[pair_idx]
    v2 = full_projection_quaternion(deep_hole(i))
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    c = angle_to_color(theta)
    vertex_data.append({
        'pair_idx': pair_idx,
        'holes': (i, j),
        'color': c,
        'angle': theta,
        'state_vector': deep_hole(i) + deep_hole(j)
    })
vertex_data.sort(key=lambda x: x['angle'])

decagon_states = np.array([vd['state_vector'] for vd in vertex_data])

# Color names
color_names = ['Red', 'Orange', 'Yellow', 'Green', 'Blue']
state_color_names = [color_names[vd['color']] for vd in vertex_data]

# 2D projected coordinates
projected_2d = []
for vd in vertex_data:
    i, j = vd['holes']
    v2 = full_projection_quaternion(deep_hole(i))
    projected_2d.append(v2)
projected_2d = np.array(projected_2d)
projected_2d_norm = np.linalg.norm(projected_2d, axis=1, keepdims=True)
projected_2d_unit = projected_2d / projected_2d_norm

print(f"  Foundation loaded. 10 states ready.")
print(f"  Color assignment: {state_color_names}")

# =============================================================================
# PART 1: THE COLOR ENGINE — Full 10×10 Interaction Matrix
# =============================================================================
print("\n" + "=" * 80)
print("PART 1: THE COLOR ENGINE — Full Interaction Matrix")
print("=" * 80)

# M1: Geometric coupling (inverse distance in 2D)
M_geo = np.zeros((10, 10))
for i in range(10):
    for j in range(10):
        if i != j:
            dist = np.linalg.norm(projected_2d_unit[i] - projected_2d_unit[j])
            M_geo[i,j] = 1.0 / (dist + 0.01)

# M2: Angle-based coupling
angles_2d = [np.arctan2(p[1], p[0]) % (2*np.pi) for p in projected_2d_unit]

M_angle = np.zeros((10, 10))
for i in range(10):
    for j in range(10):
        if i != j:
            angle_diff = abs(angles_2d[i] - angles_2d[j])
            angle_diff = min(angle_diff, 2*np.pi - angle_diff)
            M_angle[i,j] = 1.0 / (angle_diff + 0.01)

# M3: Mass coupling
masses = []
for vd in vertex_data:
    i, j = vd['holes']
    cls_i = class_map[i]
    cls_j = class_map[j]
    class_mass = {'A': 0.864, 'B': 0.929, 'C': 0.818, 'D': 0.477, 'E': 0.045}
    mass = (class_mass[cls_i] + class_mass[cls_j]) / 2
    masses.append(mass)

M_mass = np.zeros((10, 10))
for i in range(10):
    for j in range(10):
        if i != j:
            M_mass[i,j] = masses[i] * masses[j]

# M4: The COLOR ENGINE — Composite interaction matrix
M_engine = 0.4 * M_geo + 0.3 * M_angle + 0.3 * M_mass
M_engine = M_engine / np.max(M_engine)

print(f"\n  COLOR ENGINE Interaction Matrix (composite):")
print(f"  {'':>3}", end='')
for i in range(10):
    print(f"{i:>7}", end='')
print()
for i in range(10):
    print(f"  {i:3}", end='')
    for j in range(10):
        if i == j:
            print(f"{'---':>7}", end='')
        else:
            print(f"{M_engine[i,j]:7.3f}", end='')
    print()

all_interactions = []
for i in range(10):
    for j in range(i+1, 10):
        all_interactions.append((i, j, M_engine[i,j]))
all_interactions.sort(key=lambda x: x[2], reverse=True)

print(f"\n  Interaction Statistics:")
print(f"    Mean: {np.mean([x[2] for x in all_interactions]):.4f}")
print(f"    Std:  {np.std([x[2] for x in all_interactions]):.4f}")
print(f"    Min:  {np.min([x[2] for x in all_interactions]):.4f}")
print(f"    Max:  {np.max([x[2] for x in all_interactions]):.4f}")

# =============================================================================
# PART 2: FORCE HIERARCHY
# =============================================================================
print("\n" + "=" * 80)
print("PART 2: FORCE HIERARCHY")
print("=" * 80)

print(f"\n  TOP 10 STRONGEST INTERACTIONS:")
print(f"  {'Rank':>4} {'State i':>7} {'State j':>7} {'Color i':>8} {'Color j':>8} {'Strength':>10}")
print(f"  {'----':>4} {'-------':>7} {'-------':>7} {'-------':>8} {'-------':>8} {'--------':>10}")
for rank, (i, j, strength) in enumerate(all_interactions[:10], 1):
    ci = state_color_names[i]
    cj = state_color_names[j]
    print(f"  {rank:4} {i:7} {j:7} {ci:>8} {cj:>8} {strength:10.4f}")

print(f"\n  TOP 10 WEAKEST INTERACTIONS:")
print(f"  {'Rank':>4} {'State i':>7} {'State j':>7} {'Color i':>8} {'Color j':>8} {'Strength':>10}")
print(f"  {'----':>4} {'-------':>7} {'-------':>7} {'-------':>8} {'-------':>8} {'--------':>10}")
for rank, (i, j, strength) in enumerate(all_interactions[-10:], 1):
    ci = state_color_names[i]
    cj = state_color_names[j]
    print(f"  {rank:4} {i:7} {j:7} {ci:>8} {cj:>8} {strength:10.4f}")

interaction_types = {
    'Same-Color (antipodal)': [],
    'Adjacent-Color': [],
    'Next-Adjacent-Color': [],
    'Opposite-Color': []
}

for i, j, strength in all_interactions:
    ci = vertex_data[i]['color']
    cj = vertex_data[j]['color']

    if ci == cj:
        interaction_types['Same-Color (antipodal)'].append((i, j, strength))
    elif abs(ci - cj) == 1 or abs(ci - cj) == 4:
        interaction_types['Adjacent-Color'].append((i, j, strength))
    elif abs(ci - cj) == 2 or abs(ci - cj) == 3:
        interaction_types['Next-Adjacent-Color'].append((i, j, strength))
    else:
        interaction_types['Opposite-Color'].append((i, j, strength))

print(f"\n  INTERACTION STRENGTH BY TYPE:")
for itype, interactions in interaction_types.items():
    if interactions:
        strengths = [s for _, _, s in interactions]
        print(f"    {itype:30s}: mean = {np.mean(strengths):.4f}, std = {np.std(strengths):.4f}, n = {len(strengths)}")

print(f"\n  FORCE HIERARCHY (by mean strength):")
sorted_types = sorted(interaction_types.items(), key=lambda x: np.mean([s for _, _, s in x[1]]) if x[1] else 0, reverse=True)
for rank, (itype, interactions) in enumerate(sorted_types, 1):
    if interactions:
        mean_strength = np.mean([s for _, _, s in interactions])
        print(f"    {rank}. {itype}: {mean_strength:.4f}")

# =============================================================================
# PART 3: YELLOW'S ROLE
# =============================================================================
print("\n" + "=" * 80)
print("PART 3: YELLOW'S ROLE — The Universal Mediator?")
print("=" * 80)

yellow_indices = [i for i, vd in enumerate(vertex_data) if vd['color'] == 2]
print(f"\n  Yellow states: {yellow_indices}")

yellow_involvement_total = 0
yellow_interactions = []
non_yellow_interactions = []

for i, j, strength in all_interactions:
    is_yellow = (i in yellow_indices) or (j in yellow_indices)
    if is_yellow:
        yellow_involvement_total += strength
        yellow_interactions.append((i, j, strength))
    else:
        non_yellow_interactions.append((i, j, strength))

print(f"\n  Yellow's Total Involvement: {yellow_involvement_total:.4f}")
print(f"  Non-Yellow Total Involvement: {np.sum([s for _, _, s in non_yellow_interactions]):.4f}")
print(f"  Yellow's Fraction of Total: {yellow_involvement_total / np.sum([s for _, _, s in all_interactions]):.4f}")

print(f"\n  YELLOW'S ROLE BY INTERACTION TYPE:")
for itype, interactions in interaction_types.items():
    yellow_in_type = [(i, j, s) for i, j, s in interactions if i in yellow_indices or j in yellow_indices]
    non_yellow_in_type = [(i, j, s) for i, j, s in interactions if i not in yellow_indices and j not in yellow_indices]

    if yellow_in_type:
        yellow_mean = np.mean([s for _, _, s in yellow_in_type])
        yellow_sum = np.sum([s for _, _, s in yellow_in_type])
    else:
        yellow_mean = 0
        yellow_sum = 0

    if non_yellow_in_type:
        non_yellow_mean = np.mean([s for _, _, s in non_yellow_in_type])
        non_yellow_sum = np.sum([s for _, _, s in non_yellow_in_type])
    else:
        non_yellow_mean = 0
        non_yellow_sum = 0

    print(f"\n    {itype}:")
    print(f"      Yellow-involved:    mean = {yellow_mean:.4f}, sum = {yellow_sum:.4f}, n = {len(yellow_in_type)}")
    print(f"      Non-Yellow-involved: mean = {non_yellow_mean:.4f}, sum = {non_yellow_sum:.4f}, n = {len(non_yellow_in_type)}")
    if yellow_mean > 0 and non_yellow_mean > 0:
        print(f"      Yellow enhancement: {yellow_mean / non_yellow_mean:.2f}x")

print(f"\n  YELLOW'S CONNECTIONS TO EACH COLOR:")
for c in range(5):
    color_indices = [i for i, vd in enumerate(vertex_data) if vd['color'] == c]
    color_name = color_names[c]

    yellow_to_color = []
    for yi in yellow_indices:
        for ci in color_indices:
            if yi != ci:
                strength = M_engine[yi, ci]
                yellow_to_color.append(strength)

    if yellow_to_color:
        print(f"    Yellow -> {color_name:6s}: mean = {np.mean(yellow_to_color):.4f}, sum = {np.sum(yellow_to_color):.4f}, n = {len(yellow_to_color)}")

print(f"\n  YELLOW AS NETWORK HUB:")
threshold = 0.5
degrees = []
for i in range(10):
    degree = sum(1 for j in range(10) if i != j and M_engine[i,j] > threshold)
    degrees.append(degree)

for i in range(10):
    hub_status = " ★ HUB" if degrees[i] >= max(degrees) - 1 else ""
    print(f"    State {i} ({state_color_names[i]:6s}): degree = {degrees[i]}{hub_status}")

print(f"\n  Yellow states average degree: {np.mean([degrees[i] for i in yellow_indices]):.1f}")
print(f"  Other states average degree: {np.mean([degrees[i] for i in range(10) if i not in yellow_indices]):.1f}")

# =============================================================================
# PART 4: YELLOW AS NUCLEAR MEDIATOR
# =============================================================================
print("\n" + "=" * 80)
print("PART 4: YELLOW AS NUCLEAR MEDIATOR")
print("=" * 80)

print(f"\n  YELLOW IN TOP 20 INTERACTIONS:")
top_20 = all_interactions[:20]
yellow_in_top = [(i, j, s) for i, j, s in top_20 if i in yellow_indices or j in yellow_indices]
print(f"    Yellow appears in {len(yellow_in_top)}/20 top interactions ({len(yellow_in_top)/20*100:.0f}%)")
print(f"    Yellow's total strength in top 20: {np.sum([s for _, _, s in yellow_in_top]):.4f}")

print(f"\n  YELLOW'S BETWEENNESS CENTRALITY:")
betweenness_count = 0
total_paths = 0
for i in range(10):
    for j in range(i+1, 10):
        if i not in yellow_indices and j not in yellow_indices:
            dist_direct = min(abs(i-j), 10-abs(i-j))
            dist_via_y2 = min(abs(i-2), 10-abs(i-2)) + min(abs(j-2), 10-abs(j-2))
            dist_via_y7 = min(abs(i-7), 10-abs(i-7)) + min(abs(j-7), 10-abs(j-7))

            shortest = min(dist_direct, dist_via_y2, dist_via_y7)
            total_paths += 1
            if shortest == dist_via_y2 or shortest == dist_via_y7:
                betweenness_count += 1

print(f"    Shortest paths through Yellow: {betweenness_count}/{total_paths} ({betweenness_count/total_paths*100:.1f}%)")

print(f"\n  EIGENVECTOR CENTRALITY:")
def power_iteration(M, num_simulations=100):
    b = np.random.rand(M.shape[0])
    for _ in range(num_simulations):
        b = M @ b
        b = b / np.linalg.norm(b)
    return b

centrality = power_iteration(M_engine + M_engine.T, 200)
for i in range(10):
    marker = " ★" if i in yellow_indices else ""
    print(f"    State {i} ({state_color_names[i]:6s}): {centrality[i]:.4f}{marker}")

yellow_centrality = np.mean([centrality[i] for i in yellow_indices])
other_centrality = np.mean([centrality[i] for i in range(10) if i not in yellow_indices])
print(f"\n    Yellow average centrality: {yellow_centrality:.4f}")
print(f"    Other average centrality: {other_centrality:.4f}")
print(f"    Yellow centrality ratio: {yellow_centrality/other_centrality:.2f}x")

print(f"\n  NUCLEAR TEST: Does Yellow mediate strong binding?")
for c in range(5):
    color_indices = [i for i, vd in enumerate(vertex_data) if vd['color'] == c]
    color_name = color_names[c]

    strongest = 0
    strongest_partner = None
    for ci in color_indices:
        for j in range(10):
            if ci != j and M_engine[ci, j] > strongest:
                strongest = M_engine[ci, j]
                strongest_partner = j

    partner_color = state_color_names[strongest_partner] if strongest_partner is not None else "N/A"
    is_yellow_partner = strongest_partner in yellow_indices if strongest_partner is not None else False

    print(f"    {color_name:6s}'s strongest bond: {strongest:.4f} with {partner_color} {'(YELLOW MEDIATED)' if is_yellow_partner else ''}")

# =============================================================================
# PART 5: 3-POINT VERTEX INTERACTIONS
# =============================================================================
print("\n" + "=" * 80)
print("PART 5: 3-POINT VERTEX INTERACTIONS — Yellow in Triplets")
print("=" * 80)

H_v = np.zeros((10, 10, 10))
for i in range(10):
    for j in range(10):
        for k in range(10):
            if i != j and j != k and i != k:
                p1, p2, p3 = projected_2d_unit[i], projected_2d_unit[j], projected_2d_unit[k]
                area = 0.5 * abs(np.cross(p2-p1, p3-p1))
                H_v[i,j,k] = area

print(f"\n  3-POINT VERTEX HAMILTONIAN STATISTICS:")
print(f"    Mean: {np.mean(H_v):.6f}")
print(f"    Max: {np.max(H_v):.6f}")
print(f"    Min (non-zero): {np.min(H_v[H_v > 0]):.6f}")

yellow_3pt = []
non_yellow_3pt = []

for i in range(10):
    for j in range(10):
        for k in range(10):
            if H_v[i,j,k] > 0:
                has_yellow = (i in yellow_indices) or (j in yellow_indices) or (k in yellow_indices)
                if has_yellow:
                    yellow_3pt.append(H_v[i,j,k])
                else:
                    non_yellow_3pt.append(H_v[i,j,k])

print(f"\n  YELLOW IN 3-POINT VERTICES:")
print(f"    Yellow-involved vertices:    mean = {np.mean(yellow_3pt):.4f}, n = {len(yellow_3pt)}")
print(f"    Non-Yellow-involved vertices: mean = {np.mean(non_yellow_3pt):.4f}, n = {len(non_yellow_3pt)}")
if non_yellow_3pt:
    print(f"    Yellow enhancement: {np.mean(yellow_3pt) / np.mean(non_yellow_3pt):.2f}x")

all_3pt = []
for i in range(10):
    for j in range(10):
        for k in range(10):
            if H_v[i,j,k] > 0:
                has_yellow = (i in yellow_indices) or (j in yellow_indices) or (k in yellow_indices)
                all_3pt.append((i, j, k, H_v[i,j,k], has_yellow))

all_3pt.sort(key=lambda x: x[3], reverse=True)

print(f"\n  TOP 10 3-POINT VERTICES (Yellow-involved marked with ★):")
for i, j, k, area, has_yellow in all_3pt[:10]:
    ci, cj, ck = state_color_names[i], state_color_names[j], state_color_names[k]
    marker = " ★" if has_yellow else ""
    print(f"    ({i},{j},{k}) = ({ci},{cj},{ck}): area = {area:.4f}{marker}")

top_50 = all_3pt[:50]
yellow_count = sum(1 for _, _, _, _, hy in top_50 if hy)
print(f"\n  Yellow in top 50 vertices: {yellow_count}/50 ({yellow_count/50*100:.0f}%)")

print(f"\n  YELLOW AS MEDIATOR (middle vertex in 3-point):")
yellow_mediator = []
for i in range(10):
    for j in yellow_indices:
        for k in range(10):
            if H_v[i,j,k] > 0:
                yellow_mediator.append(H_v[i,j,k])

if yellow_mediator:
    print(f"    Mean area when Yellow is mediator: {np.mean(yellow_mediator):.4f}")
    print(f"    Count: {len(yellow_mediator)}")

print("\n" + "=" * 80)
print("RC-166 EXECUTION COMPLETE")
print("=" * 80)
