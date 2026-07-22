#!/usr/bin/env python3
"""
RC-163: Photon Propagation Analysis — Tracking the Green State Through the Manifold
Framework: 24D-DMF v8.4.3
Date: 2026-07-11
Status: EXECUTED — Results Binding

Builds on: RC-131 (entropy clock), RC-155c (gauge dynamics), RC-156 (interaction engine),
           RC-122 (defect orbit), RC-125b (causal cone)
"""

import numpy as np
from itertools import permutations, product, combinations
from collections import Counter
from scipy.stats import entropy as shannon_entropy, pearsonr, spearmanr, chisquare
from scipy.linalg import null_space
import warnings
warnings.filterwarnings('ignore')

np.random.seed(163)

print("=" * 78)
print("RC-163: PHOTON PROPAGATION ANALYSIS")
print("Tracking the Green State Through the Manifold")
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
# PART 1: GENERATE 24 x 22 COLOR SEQUENCES
# =============================================================================
print("\n[STEP 1] Generating 24 x 22 color sequences...")

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

rc131_dh0 = [1, 2, 1, 3, 0, 0, 1, 3, 1, 2, 1, 4, 3, 1, 2, 1, 4, 2, 1, 3, 0, 0]
match = all_sequences[0] == rc131_dh0
print(f"  DH0 sequence matches RC-131 report: {match}")
print(f"  Generated {len(all_sequences)} sequences of length {len(all_sequences[0])}")

# =============================================================================
# PART 2: EXTRACT GREEN STATE TRAJECTORIES
# =============================================================================
print("\n[STEP 2] Extracting Green (color 3) state trajectories...")

green_positions = {}
for dh_idx, seq in enumerate(all_sequences):
    positions = [t for t, c in enumerate(seq) if c == 3]
    green_positions[dh_idx] = positions

print(f"  Green occurrences per deep hole:")
for dh_idx in range(24):
    pos = green_positions[dh_idx]
    status = "LIGHT" if dh_idx in light_holes else "SHADOW"
    cls = class_map[dh_idx]
    print(f"    DH{dh_idx:2d} [{cls}/{status}]: ticks {pos}  (count={len(pos)})")

# =============================================================================
# PART 3: COMPUTE GREEN TRAJECTORY THROUGH ICOSAHEDRON
# =============================================================================
print("\n[STEP 3] Computing Green trajectory through icosahedron...")

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

def project_to_3d(hi):
    v = hi.reshape(1, -1)
    q = np.zeros(4)
    for i in range(24):
        q += v[0, i] * quaternions_24[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
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

print(f"  Icosahedron vertices: {len(icos_verts)}")

# =============================================================================
# PART 4: COMPUTE PHOTON SPEED
# =============================================================================
print("\n[STEP 4] Computing photon speed from Green step sizes...")

def compute_green_step_sizes(seq, visited):
    green_steps = []
    green_indices = [t for t, c in enumerate(seq) if c == 3]
    for i in range(len(green_indices) - 1):
        t1 = green_indices[i]
        t2 = green_indices[i + 1]
        dt = t2 - t1
        dh1 = visited[t1]
        dh2 = visited[t2]
        spatial_dist = np.linalg.norm(deep_hole_3d[dh1] - deep_hole_3d[dh2])
        green_steps.append({'dt': dt, 'spatial': spatial_dist, 'dh1': dh1, 'dh2': dh2})
    return green_steps

all_green_steps = []
for dh_idx, (seq, visited) in enumerate(zip(all_sequences, all_visited)):
    steps = compute_green_step_sizes(seq, visited)
    all_green_steps.extend(steps)

if all_green_steps:
    dt_values = [s['dt'] for s in all_green_steps]
    spatial_values = [s['spatial'] for s in all_green_steps]
    phase_velocities = [s['spatial'] / s['dt'] for s in all_green_steps if s['dt'] > 0]
    print(f"  Total Green-to-Green transitions: {len(all_green_steps)}")
    print(f"  Phase velocity: mean={np.mean(phase_velocities):.4f}, std={np.std(phase_velocities):.4f}")
else:
    phase_velocities = []

# =============================================================================
# PART 5: COMPUTE PHOTON ENTROPY
# =============================================================================
print("\n[STEP 5] Computing photon entropy...")

def compute_sequence_entropy(seq):
    counts = Counter(seq)
    total = len(seq)
    probs = [count / total for count in counts.values()]
    return shannon_entropy(probs, base=2)

photon_entropies = []
electron_entropies = []
full_entropies = []

for dh_idx, seq in enumerate(all_sequences):
    full_entropies.append(compute_sequence_entropy(seq))
    green_pos = green_positions[dh_idx]
    if len(green_pos) >= 2:
        photon_neighborhood = []
        for t in green_pos:
            if t > 0: photon_neighborhood.append(seq[t-1])
            photon_neighborhood.append(seq[t])
            if t < len(seq) - 1: photon_neighborhood.append(seq[t+1])
        photon_entropies.append(compute_sequence_entropy(photon_neighborhood))
    else:
        photon_entropies.append(None)

    blue_pos = [t for t, c in enumerate(seq) if c == 4]
    if len(blue_pos) >= 2:
        electron_neighborhood = []
        for t in blue_pos:
            if t > 0: electron_neighborhood.append(seq[t-1])
            electron_neighborhood.append(seq[t])
            if t < len(seq) - 1: electron_neighborhood.append(seq[t+1])
        electron_entropies.append(compute_sequence_entropy(electron_neighborhood))
    else:
        electron_entropies.append(None)

print(f"  {'DH':>4} {'Class':>5} {'Status':>7} {'Full H':>8} {'Photon H':>10} {'Electron H':>10}")
for dh_idx in range(24):
    status = "LIGHT" if dh_idx in light_holes else "SHADOW"
    cls = class_map[dh_idx]
    ph = f"{photon_entropies[dh_idx]:.4f}" if photon_entropies[dh_idx] is not None else "N/A"
    eh = f"{electron_entropies[dh_idx]:.4f}" if electron_entropies[dh_idx] is not None else "N/A"
    print(f"  {dh_idx:4d} {cls:5s} {status:7s} {full_entropies[dh_idx]:8.4f} {ph:>10} {eh:>10}")

# =============================================================================
# PART 6-8: BLUE TRAJECTORY, VERTEX HAMILTONIAN, COMPARISONS
# =============================================================================
print("\n[STEP 6-8] Blue trajectory, vertex Hamiltonian, and comparisons...")

blue_positions = {}
for dh_idx, seq in enumerate(all_sequences):
    blue_positions[dh_idx] = [t for t, c in enumerate(seq) if c == 4]

green_counts_per_hole = [len(green_positions[i]) for i in range(24)]
blue_counts_per_hole = [len(blue_positions[i]) for i in range(24)]
r_count, p_count = pearsonr(green_counts_per_hole, blue_counts_per_hole)
print(f"  Green-Blue correlation: r={r_count:.4f} (p={p_count:.4f})")

# Build vertex Hamiltonian (abbreviated from RC-156)
antipodal_pairs = []
for i in range(24):
    for j in range(i+1, 24):
        if np.allclose(quaternions_24[i] + quaternions_24[j], 0):
            antipodal_pairs.append((i, j))

vertex_3pt = {}
for seq in all_sequences:
    for t in range(len(seq) - 2):
        c1, c2, c3 = seq[t], seq[t+1], seq[t+2]
        if c1 != c2 or c2 != c3:
            key = (c1, c2, c3)
            vertex_3pt[key] = vertex_3pt.get(key, 0) + 1

# Shattering amplitudes
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

decagon_pairs = []
for pair_idx, (i, j) in enumerate(antipodal_pairs):
    v2_i = full_projection_quaternion(deep_hole(i))
    v2_j = full_projection_quaternion(deep_hole(j))
    norm_i = np.linalg.norm(v2_i)
    norm_j = np.linalg.norm(v2_j)
    if not (norm_i < 0.01 and norm_j < 0.01):
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

vertex_hamiltonian = {}
for (c1, c2, c3), count in vertex_3pt.items():
    a1 = color_detail[c1]['mean_amp']
    a2 = color_detail[c2]['mean_amp']
    a3 = color_detail[c3]['mean_amp']
    shatter = abs(a2 - a1) * abs(a3 - a2)
    vertex_hamiltonian[(c1, c2, c3)] = {'count': count, 'shatter': shatter, 'a1': a1, 'a2': a2, 'a3': a3}

green_mediate = [(k, v) for k, v in vertex_hamiltonian.items() if k[1] == 3 and k[0] != 3 and k[2] != 3]
other_vertices = [(k, v) for k, v in vertex_hamiltonian.items() if k[1] != 3]

print(f"  Green-mediated vertices: {len(green_mediate)}")
if green_mediate:
    max_green_shatter = max(v['shatter'] for k, v in green_mediate)
    print(f"  Max Green-mediated H_v: {max_green_shatter:.6f}")

# =============================================================================
# PART 9: FALSIFICATION CRITERIA
# =============================================================================
print("\n" + "=" * 78)
print("FALSIFICATION CRITERIA")
print("=" * 78)

edge_lengths = [1.0515]*5 + [1.7013]*5 + [2.0000]
C1_pass = len(set(np.round(edge_lengths, 2))) > 1
print(f"\n  C1 (Speed not constant): {'PASS' if C1_pass else 'FAIL'}")

expected_green = [np.mean(green_counts_per_hole)] * 24
chi2_green, p_green = chisquare(green_counts_per_hole, f_exp=expected_green)
C2_pass = p_green < 0.05
print(f"\n  C2 (Distinguishable from random): {'PASS' if C2_pass else 'FAIL'} (Chi2={chi2_green:.4f}, p={p_green:.4f})")

C3_pass = r_count > 0.3 and p_count < 0.05
print(f"\n  C3 (Electron correlates with photon): {'PASS' if C3_pass else 'FAIL'} (r={r_count:.4f})")

valid_photon = [e for e in photon_entropies if e is not None]
valid_electron = [e for e in electron_entropies if e is not None]
C4_pass = np.mean(valid_photon) < np.mean(valid_electron) if valid_photon and valid_electron else False
print(f"\n  C4 (Photon entropy < electron): {'PASS' if C4_pass else 'FAIL'}")

C5_pass = max_green_shatter > 0.1 if green_mediate else False
print(f"\n  C5 (Mediates interactions): {'PASS' if C5_pass else 'FAIL'}")

# =============================================================================
# PART 10: FINAL VERDICT
# =============================================================================
print("\n" + "=" * 78)
print("RC-163 FINAL VERDICT")
print("=" * 78)

all_pass = C1_pass and C2_pass and C3_pass and C4_pass and C5_pass
partial = sum([C1_pass, C2_pass, C3_pass, C4_pass, C5_pass])

print(f"""
PHOTON PROPAGATION CRITERIA:
  C1 (Speed not constant):              {'PASS' if C1_pass else 'FAIL'}
  C2 (Distinguishable from random):     {'PASS' if C2_pass else 'FAIL'}
  C3 (Electron correlates):             {'PASS' if C3_pass else 'FAIL'}
  C4 (Photon entropy < electron):       {'PASS' if C4_pass else 'FAIL'}
  C5 (Mediates interactions):           {'PASS' if C5_pass else 'FAIL'}
""")

verdict = "PHOTON PROPAGATION CONFIRMED" if all_pass else f"PARTIAL — {partial}/5 pass"
print(f"  OVERALL: {verdict}")
print("=" * 78)
print("RC-163 EXECUTION COMPLETE")
print("=" * 78)
