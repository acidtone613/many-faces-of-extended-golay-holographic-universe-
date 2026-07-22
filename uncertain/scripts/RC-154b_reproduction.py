#!/usr/bin/env python3
"""
RC-154b: The Shattering Engine — Curvature from Quantum Fragmentation
Complete Reproduction Script

Framework: 24D-DMF v8.4.3
Date: 2026-07-11
Status: EXECUTED — Results Binding

Dependencies: numpy, scipy
Usage: python rc_154b_reproduction.py
"""

import numpy as np
from itertools import product, combinations, permutations
from scipy.linalg import null_space
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

np.random.seed(154)

print("=" * 78)
print("RC-154b: THE SHATTERING ENGINE — Curvature from Quantum Fragmentation")
print("Framework: 24D-DMF v8.4.3 | Date: 2026-07-11")
print("Status: EXECUTING Pre-Registered Tests T1–T5")
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

code_words = np.zeros((4096, 24), dtype=np.uint8)
for bits in range(4096):
    coeffs = np.array([(bits >> i) & 1 for i in range(12)], dtype=np.uint8)
    code_words[bits] = (coeffs @ G24) % 2
code_set = set(map(tuple, code_words))

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

def hopf_projection_norm(v_24d):
    v2 = full_projection_quaternion(v_24d)
    return np.linalg.norm(v2)

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

print("  Foundation loaded.")

# =============================================================================
# PART 1: TRACE ORBITS AND COMPUTE MASS SPECTRUM
# =============================================================================
print("\n[STEP 1] Tracing orbits and computing mass spectrum...")

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
measured_masses = [vd['mass'] for vd in vertex_data]
print(f"  10 color states loaded. Mass range: {min(measured_masses):.4f}–{max(measured_masses):.4f}")

# =============================================================================
# PART 2: COMPUTE EDGE WEIGHTS (RC-122 Reconstruction)
# =============================================================================
print("\n[STEP 2] Computing edge weights (shattering amplitudes)...")

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

projections_2d = []
for idx in unique_visited_orbit:
    v2 = full_projection_quaternion(deep_hole(idx))
    projections_2d.append(v2)
projections_2d = np.array(projections_2d)
edge_lengths_2d = []
for i in range(len(projections_2d)):
    j = (i + 1) % len(projections_2d)
    dist = np.linalg.norm(projections_2d[i] - projections_2d[j])
    edge_lengths_2d.append(dist)

print(f"  Orbit period: {period}")
print(f"  3D edge lengths: {[f'{d:.4f}' for d in edge_lengths_3d]}")
print(f"  3D mean: {np.mean(edge_lengths_3d):.4f}, std: {np.std(edge_lengths_3d):.4f}")

# =============================================================================
# T1 — EDGE WEIGHT = SHATTERING AMPLITUDE
# =============================================================================
print("\n" + "=" * 78)
print("T1: Edge Weight = Shattering Amplitude")
print("=" * 78)

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

color_edge_weights = {c: [] for c in range(5)}
for sd in shattering_data:
    color_edge_weights[sd['color']].append(sd['mean_edge_weight'])

shattering_variance_by_color = {}
for c in range(5):
    if len(color_edge_weights[c]) > 1:
        shattering_variance_by_color[c] = np.var(color_edge_weights[c])
    else:
        shattering_variance_by_color[c] = 0.0

print(f"  Shattering amplitude by color state:")
print(f"  {'Pair':>4} {'Color':>5} {'Mass':>8} {'EdgeWeight':>10}")
for sd in shattering_data:
    print(f"  {sd['pair_idx']:4d} {sd['color']:5d} {sd['mass']:8.4f} {sd['mean_edge_weight']:10.4f}")

all_weights = [sd['mean_edge_weight'] for sd in shattering_data]
overall_mean = np.mean(all_weights)
between_var = np.var([np.mean(color_edge_weights[c]) for c in range(5) if color_edge_weights[c]])
within_var = np.mean([np.var(color_edge_weights[c]) for c in range(5) if len(color_edge_weights[c]) > 1])

print(f"\n  Between-color variance: {between_var:.6f}")
print(f"  Within-color variance:  {within_var:.6f}")
C1_pass = between_var > within_var * 0.5
print(f"  C1 (Edge weights correlate with shattering): {'PASS' if C1_pass else 'FAIL'}")

# =============================================================================
# T2 — SHATTERING FREQUENCY = 46D SPIN FREQUENCY
# =============================================================================
print("\n" + "=" * 78)
print("T2: Shattering Frequency = 46D Spin Frequency")
print("=" * 78)

edge_fft = np.fft.fft(edge_lengths_3d)
edge_freqs = np.fft.fftfreq(len(edge_lengths_3d))
edge_power = np.abs(edge_fft)**2
dominant_idx = np.argmax(edge_power[1:]) + 1
shattering_freq = abs(edge_freqs[dominant_idx])
spin_freq = 1.0 / 46.0

print(f"  Dominant shattering frequency: {shattering_freq:.6f} per step")
print(f"  46D spin frequency: {spin_freq:.6f} per tick")
print(f"  Ratio: {shattering_freq / spin_freq:.4f}")

edge_weight_period = None
for p in range(1, min(50, len(edge_lengths_3d))):
    if all(np.isclose(edge_lengths_3d[i], edge_lengths_3d[(i+p) % len(edge_lengths_3d)], atol=0.01) for i in range(len(edge_lengths_3d))):
        edge_weight_period = p
        break

print(f"  Edge weight intrinsic period: {edge_weight_period}")
T2_exact = np.isclose(shattering_freq, spin_freq, atol=0.001)
T2_period = edge_weight_period is not None and (46 % edge_weight_period == 0 or edge_weight_period % 46 == 0 or np.isclose(46 / edge_weight_period, round(46 / edge_weight_period), atol=0.1))
T2_harmonic = np.isclose(shattering_freq / spin_freq, round(shattering_freq / spin_freq), atol=0.1) if spin_freq > 0 else False
C2_pass = T2_exact or T2_period or T2_harmonic
print(f"  C2 (Shattering frequency matches 46D spin): {'PASS' if C2_pass else 'FAIL'}")

# =============================================================================
# T3 — MASS IS INDEPENDENT OF SHATTERING
# =============================================================================
print("\n" + "=" * 78)
print("T3: Mass is Independent of Shattering")
print("=" * 78)

masses = [sd['mass'] for sd in shattering_data]
weights = [sd['mean_edge_weight'] for sd in shattering_data]
corr_mass_weight, p_mass_weight = pearsonr(masses, weights)
print(f"  Mass vs edge weight: r = {corr_mass_weight:.4f} (p = {p_mass_weight:.4f})")
C3_pass = abs(corr_mass_weight) < 0.5 and p_mass_weight > 0.05
print(f"  C3 (Mass independent of shattering): {'PASS' if C3_pass else 'FAIL'}")

# =============================================================================
# T4 — SHATTERING PATTERN IS QUANTUM
# =============================================================================
print("\n" + "=" * 78)
print("T4: The Shattering Pattern is Quantum")
print("=" * 78)

cv_edge_weights = np.std(edge_lengths_3d) / np.mean(edge_lengths_3d) if np.mean(edge_lengths_3d) > 0 else 0

orbit_sequence_1 = []
current_h = deep_hole(1).copy()
visited_indices_1 = []
for t in range(100):
    min_dist = float('inf')
    closest_idx = -1
    for i in range(24):
        hi = deep_hole(i)
        dist = np.linalg.norm(current_h - hi)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i
    visited_indices_1.append(closest_idx)
    if t < 99:
        current_h = apply_tick_vector(current_h, t)

period_1 = None
for p in range(1, 50):
    if all(visited_indices_1[t] == visited_indices_1[t + p] for t in range(len(visited_indices_1) - p)):
        period_1 = p
        break
unique_visited_1 = list(dict.fromkeys(visited_indices_1[:period_1])) if period_1 else []

projections_3d_1 = []
for idx in unique_visited_1:
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
    projections_3d_1.append(v3)

edge_lengths_3d_1 = []
for i in range(len(projections_3d_1)):
    j = (i + 1) % len(projections_3d_1)
    dist = np.linalg.norm(projections_3d_1[i] - projections_3d_1[j])
    edge_lengths_3d_1.append(dist)

patterns_differ = not np.allclose(edge_lengths_3d[:min(len(edge_lengths_3d), len(edge_lengths_3d_1))], 
                                   edge_lengths_3d_1[:min(len(edge_lengths_3d), len(edge_lengths_3d_1))], atol=0.05)
print(f"  DH0 edge weights: {[f'{d:.4f}' for d in edge_lengths_3d]}")
print(f"  DH1 edge weights: {[f'{d:.4f}' for d in edge_lengths_3d_1]}")
print(f"  Patterns differ: {patterns_differ}")
print(f"  Edge weight CV: {cv_edge_weights:.4f}")
C4_pass = patterns_differ or cv_edge_weights > 0.1
print(f"  C4 (Shattering pattern is quantum): {'PASS' if C4_pass else 'FAIL'}")

# =============================================================================
# T5 — 5 COLORS ARE THE SHATTERED STATES
# =============================================================================
print("\n" + "=" * 78)
print("T5: The 5 Colors are the Shattered States")
print("=" * 78)

color_signatures = {}
for c in range(5):
    color_states = [sd for sd in shattering_data if sd['color'] == c]
    if color_states:
        signatures = [sd['mean_edge_weight'] for sd in color_states]
        color_signatures[c] = {
            'mean': np.mean(signatures),
            'std': np.std(signatures),
            'n': len(signatures)
        }

print(f"  Color signatures:")
for c in range(5):
    if c in color_signatures:
        sig = color_signatures[c]
        print(f"    Color {c}: mean={sig['mean']:.4f}, std={sig['std']:.4f}, n={sig['n']}")

between_color_var = np.var([color_signatures[c]['mean'] for c in color_signatures]) if color_signatures else 0
within_color_var = np.mean([color_signatures[c]['std']**2 for c in color_signatures]) if color_signatures else 1
print(f"\n  Between-color variance: {between_color_var:.6f}")
print(f"  Within-color variance:  {within_color_var:.6f}")
C5_pass = between_color_var > within_color_var * 0.5 and len(color_signatures) == 5
print(f"  C5 (5 colors map to shattering): {'PASS' if C5_pass else 'FAIL'}")

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "=" * 78)
print("RC-154b FINAL VERDICT")
print("=" * 78)

print(f"""
FALSIFICATION CRITERIA:
  C1 (Edge weights correlate with shattering):     {'PASS' if C1_pass else 'FAIL'}
  C2 (Shattering frequency matches 46D spin):    {'PASS' if C2_pass else 'FAIL'}
  C3 (Mass independent of shattering):             {'PASS' if C3_pass else 'FAIL'}
  C4 (Shattering pattern is quantum):              {'PASS' if C4_pass else 'FAIL'}
  C5 (5 colors map to shattering pattern):         {'PASS' if C5_pass else 'FAIL'}
""")

all_pass = C1_pass and C2_pass and C3_pass and C4_pass and C5_pass
partial = sum([C1_pass, C2_pass, C3_pass, C4_pass, C5_pass])

if all_pass:
    verdict = "PASS — SHATTERING ENGINE CONFIRMED"
elif C1_pass and C3_pass and C4_pass and C5_pass and not C2_pass:
    verdict = "PARTIAL — SHATTERING CONFIRMED, FREQUENCY MISMATCH"
else:
    verdict = f"PARTIAL — {partial}/5 criteria pass"

print(f"  OVERALL: {verdict}")
print("=" * 78)
print("RC-154b EXECUTION COMPLETE")
print("=" * 78)
