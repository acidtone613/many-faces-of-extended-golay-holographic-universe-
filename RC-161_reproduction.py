#!/usr/bin/env python3
"""
RC-161: Mass Operator from the Shattering Geometry
Complete Reproduction Script

Framework: 24D-DMF v8.4.3
Date: 2026-07-11
Status: EXECUTED — Results Binding

Builds on: RC-155c (gauge dynamics), RC-156 (interaction engine),
           RC-122/125b (orbit geometry), RC-160 (loop corrections)
"""

import numpy as np
from itertools import product, combinations
from scipy.linalg import null_space
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

np.random.seed(161)

print("=" * 78)
print("RC-161: MASS OPERATOR FROM THE SHATTERING GEOMETRY")
print("Framework: 24D-DMF v8.4.3 | Date: 2026-07-11")
print("=" * 78)

# =============================================================================
# PART 0: FRAMEWORK FOUNDATION (from RC-156)
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

# Orbits
all_sequences = []
all_visited = []
for start_idx in range(24):
    current_h = deep_hole(start_idx).copy()
    visited = []
    sequence = []
    for t in range(22):
        min_dist = float('inf')
        closest_idx = -1
        for i in range(24):
            hi = deep_hole(i)
            dist = np.linalg.norm(current_h - hi)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
        visited.append(closest_idx)
        v2 = full_projection_quaternion(deep_hole(closest_idx))
        theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
        sequence.append(angle_to_color(theta))
        if t < 21:
            current_h = apply_tick_vector(current_h, t)
    all_sequences.append(sequence)
    all_visited.append(visited)

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

def compute_wavelength(sequence):
    if len(sequence) < 2:
        return 1.0
    changes = 1
    for i in range(1, len(sequence)):
        if sequence[i] != sequence[i-1]:
            changes += 1
    return len(sequence) / changes

wavelength_by_hole = {}
visible_mass_by_hole = {}
for i in range(24):
    wavelength_by_hole[i] = compute_wavelength(all_sequences[i])
    visible_mass_by_hole[i] = 1.0 / wavelength_by_hole[i]

orbit_visited = all_visited[0]
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
    invisible = np.linalg.norm(tunnel_basis_norm @ h)
    invisible_mass_by_hole[i] = invisible

commutator_norm_by_pair = {}
for pair_idx, (i, j) in enumerate(antipodal_pairs):
    q = quaternions_24[i]
    qp = quat_mul(q, p_golden)
    pq = quat_mul(p_golden, q)
    comm = qp - pq
    commutator_norm_by_pair[pair_idx] = np.linalg.norm(comm)

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
    vertex_data.append({
        'pair_idx': pair_idx,
        'holes': (i, j),
        'color': c,
        'angle': theta,
        'mass': total_mass,
        'class_i': class_map[i],
        'class_j': class_map[j],
    })
vertex_data.sort(key=lambda x: x['mass'])

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
    orbit_sequence.append({'tick': t, 'closest_deep_hole': closest_idx})
    visited_indices.append(closest_idx)
    if t < 99:
        current_h = apply_tick_vector(current_h, t)

period = None
for p in range(1, 50):
    if all(visited_indices[t] == visited_indices[t + p] for t in range(len(visited_indices) - p)):
        period = p
        break

unique_visited_orbit = list(dict.fromkeys(visited_indices[:period]))

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

shattering_data = []
for vd in vertex_data:
    i, j = vd['holes']
    steps_i = [step for step, idx in enumerate(unique_visited_orbit) if idx == i]
    steps_j = [step for step, idx in enumerate(unique_visited_orbit) if idx == j]
    weights_i = [edge_lengths_3d[step % len(edge_lengths_3d)] for step in steps_i] if steps_i else [0]
    weights_j = [edge_lengths_3d[step % len(edge_lengths_3d)] for step in steps_j] if steps_j else [0]
    mean_weight = np.mean(weights_i + weights_j) if (weights_i or weights_j) else 0
    shattering_data.append({
        'pair_idx': vd['pair_idx'],
        'color': vd['color'],
        'mass': vd['mass'],
        'mean_edge_weight': mean_weight,
        'class_i': vd['class_i'],
        'class_j': vd['class_j'],
    })

color_detail = {}
for c in range(5):
    states = [sd for sd in shattering_data if sd['color'] == c]
    if states:
        amps = [s['mean_edge_weight'] for s in states]
        masses = [s['mass'] for s in states]
        color_detail[c] = {
            'amps': amps,
            'masses': masses,
            'mean_amp': np.mean(amps),
            'std_amp': np.std(amps),
            'cv': np.std(amps) / np.mean(amps) if np.mean(amps) > 0 else 0,
            'mean_mass': np.mean(masses),
            'mass_range': max(masses) - min(masses),
            'n': len(states),
        }

structural_map = {
    0: {'name': 'Red',    'interaction': 'Higgs / Mass', 'gauge': 'SU(2)xU(1)', 'ssb_index': 2, 'color_hex': '#e74c3c'},
    1: {'name': 'Orange', 'interaction': 'Gravity',      'gauge': 'None',       'ssb_index': 1, 'color_hex': '#e67e22'},
    2: {'name': 'Yellow', 'interaction': 'QCD',          'gauge': 'SU(3)',      'ssb_index': 0, 'color_hex': '#f1c40f'},
    3: {'name': 'Green',  'interaction': 'QED',          'gauge': 'U(1)',       'ssb_index': 0, 'color_hex': '#2ecc71'},
    4: {'name': 'Blue',   'interaction': 'Weak',         'gauge': 'SU(2)',      'ssb_index': 3, 'color_hex': '#3498db'},
}

vertex_3pt = {}
for seq in all_sequences:
    for t in range(len(seq) - 2):
        c1, c2, c3 = seq[t], seq[t+1], seq[t+2]
        if c1 != c2 or c2 != c3:
            key = (c1, c2, c3)
            vertex_3pt[key] = vertex_3pt.get(key, 0) + 1

print("  Foundation and vertex dynamics loaded.")

# =============================================================================
# RC-161: 5×5 MASS OPERATOR
# =============================================================================
print("\n" + "=" * 78)
print("RC-161: 5×5 MASS OPERATOR")
print("=" * 78)

A_diagonal = {0: 1.0000, 1: 1.3764, 2: 0.8507, 3: 0.5257, 4: 0.5257}

vertex_hamiltonian_final = {}
for (c1, c2, c3), count in vertex_3pt.items():
    a1 = A_diagonal[c1]
    a2 = A_diagonal[c2]
    a3 = A_diagonal[c3]
    shatter = abs(a2 - a1) * abs(a3 - a2)
    vertex_hamiltonian_final[(c1, c2, c3)] = {'count': count, 'shatter': shatter}

M_final = np.zeros((5, 5))
for i in range(5):
    for j in range(5):
        if i == j:
            continue
        shatters_ij = [vertex_hamiltonian_final[(c1,c2,c3)]['shatter']
                       for (c1,c2,c3) in vertex_hamiltonian_final if c1==i and c2==j]
        shatters_ji = [vertex_hamiltonian_final[(c1,c2,c3)]['shatter']
                       for (c1,c2,c3) in vertex_hamiltonian_final if c1==j and c2==i]
        mean_ij = np.mean(shatters_ij) if shatters_ij else 0
        mean_ji = np.mean(shatters_ji) if shatters_ji else 0
        M_final[i,j] = 0.5 * (mean_ij + mean_ji)

D_final = np.diag([A_diagonal[c] for c in range(5)])
M_operator = D_final + M_final

eigvals_final, eigvecs_final = np.linalg.eigh(M_operator)
sorted_eigvals = sorted(eigvals_final)

print("\n[STEP 1] Base Amplitudes")
for c in range(5):
    print(f"  {structural_map[c]['name']:6s}: {A_diagonal[c]:.4f}")

print("\n[STEP 2] Coupling Matrix M (5×5)")
print("        Red      Orange   Yellow   Green    Blue")
for i in range(5):
    row = f"{structural_map[i]['name']:6s}"
    for j in range(5):
        row += f"  {M_final[i,j]:8.6f}"
    print(row)

print("\n[STEP 3] Mass Operator eigenvalues (unscaled):")
for i, ev in enumerate(sorted_eigvals):
    print(f"  λ_{i+1} = {ev:.6f}")

experimental = {
    'electron': 0.000511, 'muon': 0.105658, 'tau': 1.77686,
    'up': 0.0022, 'down': 0.0047, 'strange': 0.095,
    'charm': 1.275, 'bottom': 4.18, 'top': 172.76,
    'W': 80.377, 'Z': 91.1876, 'higgs': 125.25,
}

lambda_tau = experimental['tau'] / sorted_eigvals[2]
scaled_tau = np.array(sorted_eigvals) * lambda_tau

print("\n[STEP 4] Tau-matched scaling:")
for i, ev in enumerate(scaled_tau):
    print(f"  m_{i+1} = {ev:.6e} GeV")

print(f"\n  Tau: pred={scaled_tau[2]:.5f}, exp=1.77686, err={abs(scaled_tau[2]-1.77686)/1.77686*100:.3f}%")
print(f"  Electron: pred={scaled_tau[0]:.6e}, exp=0.000511")
if scaled_tau[0] > 0:
    print(f"  mu/e ratio: {scaled_tau[1]/scaled_tau[0]:.2f} (target 206.77)")

print("\n" + "=" * 78)
print("RC-161 VERDICT: REJECTED")
print("=" * 78)
print("Compression ratio too small (~4.7 vs needed ~3.4×10^5)")
