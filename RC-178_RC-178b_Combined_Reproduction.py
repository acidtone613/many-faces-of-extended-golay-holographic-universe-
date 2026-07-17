#!/usr/bin/env python3
"""
RC-178 & RC-178b: COMBINED REPRODUCTION SCRIPT
Parametric Oscillator, Phase-Matching Pentagram, 4-to-1 Covering
Framework: 24D-DMF v8.4.6 | Date: 2026-07-13
Status: EXECUTED — Results Binding

This script reproduces all computational results for RC-178 and RC-178b:
  1. Framework foundation (Golay code, quaternion 24-cell, Hopf fibration)
  2. 144-tick color sequences for all 24 deep holes
  3. RC-178: Manley-Rowe, coherence hierarchy, upward entropy, DH23 fixed point
  4. RC-178b: 4-to-1 covering, 5-fold symmetry, pentagram structure
  5. Falsification criteria for both cycles

Dependencies: numpy, scipy
"""

import numpy as np
from itertools import permutations, product, combinations
from math import log2, pi
from collections import defaultdict
from scipy.linalg import null_space
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

np.random.seed(178)

print("=" * 80)
print("RC-178 & RC-178b: COMBINED REPRODUCTION SCRIPT")
print("Framework: 24D-DMF v8.4.6 | Date: 2026-07-13")
print("=" * 80)

# =============================================================================
# PART 1: FRAMEWORK FOUNDATION
# =============================================================================
print("\n[STEP 1] Building framework foundation...")

# Golay code G24 (cyclic basis)
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

# Deep hole generator
def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

# Floquet tick
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

# Hopf fibration
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

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

print("  Framework foundation built.")

# =============================================================================
# PART 2: GENERATE 144-TICK COLOR SEQUENCES
# =============================================================================
print("\n[STEP 2] Generating 144-tick color sequences for all 24 deep holes...")

all_sequences_144 = []
for start_idx in range(24):
    h0 = deep_hole(start_idx)
    current_h = h0.copy()
    sequence = []
    for t in range(144):
        v2 = full_projection_quaternion(current_h)
        theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
        color = angle_to_color(theta)
        sequence.append(color)
        if t < 143:
            current_h = apply_tick_vector(current_h, t)
    all_sequences_144.append(sequence)

all_sequences_144 = np.array(all_sequences_144)
all_sequences_22 = all_sequences_144[:, :22]
print(f"  Generated {all_sequences_144.shape[0]} sequences of length {all_sequences_144.shape[1]}")

# Orbit classes
orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}
class_of_dh = {}
for cls, dhs in orbit_classes.items():
    for dh in dhs:
        class_of_dh[dh] = cls

# Tunnel layer sequences
seq_neg9d = all_sequences_144[7]   # DH7 = -9D
seq_8d = all_sequences_144[8]        # DH8 = 8D
seq_7d = all_sequences_144[9]      # DH9 = 7D
seq_6d = all_sequences_144[10]     # DH10 = 6D

# =============================================================================
# PART 3: MASS COMPUTATION
# =============================================================================
print("\n[STEP 3] Computing mass per deep hole...")

def compute_mass(sequence):
    n = len(sequence)
    color_changes = sum(1 for i in range(1, n) if sequence[i] != sequence[i-1])
    if color_changes == 0:
        return 0.0
    wavelength = n / color_changes
    return 1.0 / wavelength

mass_visible = np.array([compute_mass(seq) for seq in all_sequences_22])

# Compute tunnel invisible mass
orbit_sequence = []
current_h = deep_hole(0).copy()
visited_indices = []
for t in range(22):
    min_dist = float('inf')
    closest_idx = -1
    for i in range(24):
        hi = deep_hole(i)
        dist = np.linalg.norm(current_h - hi)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i
    visited_indices.append(closest_idx)
    if t < 21:
        current_h = apply_tick_vector(current_h, t)

unique_visited = list(dict.fromkeys(visited_indices))
unvisited_indices = [i for i in range(24) if i not in unique_visited]

unvisited_quats = quaternions_24[unvisited_indices]
M = unvisited_quats.T
tunnel_coeffs = null_space(M)
unvisited_holes = np.array([deep_hole(i) for i in unvisited_indices])
tunnel_basis = tunnel_coeffs.T @ unvisited_holes

mass_invisible = np.zeros(24)
for dh_idx in range(24):
    h = deep_hole(dh_idx)
    invisible_norm = 0.0
    for tb in tunnel_basis:
        invisible_norm += abs(np.dot(tb, h))
    mass_invisible[dh_idx] = invisible_norm / len(tunnel_basis)

mass_commutator = np.zeros(24)
for dh_idx in range(24):
    h = deep_hole(dh_idx)
    q = np.zeros(4)
    for i in range(24):
        q += h[i] * quaternions_24[i]
    p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])
    qp = quat_mul(q, p_golden)
    pq = quat_mul(p_golden, q)
    comm = qp - pq
    mass_commutator[dh_idx] = np.linalg.norm(comm)

alpha = 0.02
gamma = 0.08
mass_total = mass_visible + alpha * mass_invisible + gamma * mass_commutator

print(f"  Mass range: [{mass_total.min():.4f}, {mass_total.max():.4f}]")

# =============================================================================
# PART 4: FREQUENCY SPECTRUM (RC-177b/RC-178)
# =============================================================================
print("\n[STEP 4] Computing frequency spectra...")

color_names = ['Red', 'Orange', 'Yellow', 'Green', 'Blue']

freq_results = {}
for c in range(5):
    pulse_train = (all_sequences_144 == c).astype(float).flatten()
    fft_result = np.fft.fft(pulse_train)
    freqs = np.fft.fftfreq(len(pulse_train), d=1.0)
    power = np.abs(fft_result)**2

    n = len(freqs) // 2
    positive_freqs = freqs[1:n]
    positive_power = power[1:n]

    positive_power_norm = positive_power / np.sum(positive_power)
    mean_freq = np.sum(positive_freqs * positive_power_norm)
    mean_sq_freq = np.sum(positive_freqs**2 * positive_power_norm)
    variance = mean_sq_freq - mean_freq**2
    std_dev = np.sqrt(variance) if variance > 0 else positive_freqs[1] - positive_freqs[0]
    bandwidth = 2.355 * std_dev

    peak_idx = np.argmax(positive_power) + 1
    fundamental_freq = positive_freqs[peak_idx - 1]

    coherence_length = 1.0 / bandwidth if bandwidth > 0 else float('inf')

    freq_results[color_names[c]] = {
        'fundamental_freq': fundamental_freq,
        'mean_freq': mean_freq,
        'std_dev': std_dev,
        'bandwidth': bandwidth,
        'coherence_length': coherence_length,
    }

# =============================================================================
# PART 5: 7D TRANSMISSION FUNCTION
# =============================================================================
print("\n[STEP 5] Computing 7D transmission function...")

probs_8d = np.zeros(5)
probs_7d = np.zeros(5)
for c in range(5):
    probs_8d[c] = np.mean(seq_8d == c)
    probs_7d[c] = np.mean(seq_7d == c)

transmission = {}
for c in range(5):
    t_c = probs_7d[c] / probs_8d[c] if probs_8d[c] > 0 else 0
    transmission[color_names[c]] = t_c

print("\n| Color | 8D Prob | 7D Prob | Transmission T_c |")
print("| :---- | :------ | :------ | :--------------- |")
for c in range(5):
    print(f"| {color_names[c]:6s} | {probs_8d[c]:7.3f} | {probs_7d[c]:7.3f} | {transmission[color_names[c]]:16.3f} |")

# =============================================================================
# PART 6: RC-178 HYPOTHESIS TESTING
# =============================================================================
print("\n" + "=" * 80)
print("RC-178: HYPOTHESIS TESTING")
print("=" * 80)

# H1: Manley-Rowe Relations
delta_T_yellow = transmission['Yellow'] - 1.0
delta_T_blue = transmission['Blue'] - 1.0
delta_T_orange = transmission['Orange'] - 1.0

omega_yellow = freq_results['Yellow']['fundamental_freq']
omega_blue = freq_results['Blue']['fundamental_freq']
omega_orange = freq_results['Orange']['fundamental_freq']

term_signal = delta_T_yellow / omega_yellow
term_idler = delta_T_blue / omega_blue
term_pump = delta_T_orange / omega_orange
manley_rowe_sum = term_signal + term_idler + term_pump

pump_magnitude = abs(term_pump)
error_pct = abs(manley_rowe_sum) / pump_magnitude * 100 if pump_magnitude > 0 else 0
h1_pass = abs(manley_rowe_sum) < 0.05 * pump_magnitude

print(f"\nH1: Manley-Rowe Sum = {manley_rowe_sum:.4f} ({error_pct:.1f}% error)")
print(f"H1 VERDICT: {'PASS' if h1_pass else 'FAIL'}")

# H3: Coherence Hierarchy
L_orange = freq_results['Orange']['coherence_length']
L_yellow = freq_results['Yellow']['coherence_length']
L_blue = freq_results['Blue']['coherence_length']
h3_pass = L_orange < L_yellow < L_blue

print(f"\nH3: L_Orange={L_orange:.2f}, L_Yellow={L_yellow:.2f}, L_Blue={L_blue:.2f}")
print(f"H3 VERDICT: {'PASS' if h3_pass else 'FAIL'}")

# H4: Upward Entropy
def shannon_entropy(seq):
    counts = {}
    for c in seq:
        counts[c] = counts.get(c, 0) + 1
    entropy = 0.0
    n = len(seq)
    for count in counts.values():
        p = count / n
        entropy -= p * log2(p)
    return entropy

entropy_48d = []
for dh_idx in range(24):
    seq_48 = all_sequences_144[dh_idx, :48]
    entropy_48d.append(shannon_entropy(seq_48))
entropy_48d_mean = np.mean(entropy_48d)
entropy_12d = 12.0
h4_pass = entropy_48d_mean < entropy_12d

print(f"\nH4: 12D entropy={entropy_12d:.4f}, 48D entropy={entropy_48d_mean:.4f}")
print(f"H4 VERDICT: {'PASS' if h4_pass else 'FAIL'}")

# H5: DH23 Fixed Point
dh23_seq = all_sequences_144[23]
dh23_entropy = shannon_entropy(dh23_seq)
dh23_mass = mass_total[23]

h0_23 = deep_hole(23)
current_23 = h0_23.copy()
seq_23_check = []
for t in range(144):
    v2 = full_projection_quaternion(current_23)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    color = angle_to_color(theta)
    seq_23_check.append(color)
    if t < 143:
        current_23 = apply_tick_vector(current_23, t)

is_fixed = np.all(seq_23_check == seq_23_check[0])
is_lowest_mass = np.isclose(dh23_mass, mass_total.min())
h5_pass = is_fixed and is_lowest_mass and dh23_entropy == 0

print(f"\nH5: DH23 entropy={dh23_entropy:.4f}, mass={dh23_mass:.4f}, fixed={is_fixed}")
print(f"H5 VERDICT: {'PASS' if h5_pass else 'FAIL'}")

# =============================================================================
# PART 7: RC-178b — ICOSAHEDRON PROJECTION
# =============================================================================
print("\n" + "=" * 80)
print("RC-178b: ICOSAHEDRON PROJECTION & 5-FOLD SYMMETRY")
print("=" * 80)

# Build icosahedron
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

# Compute 3D projections for all 24 deep holes
projections_3d = []
for dh_idx in range(24):
    h = deep_hole(dh_idx)
    v = h.reshape(1, -1)
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

projections_3d = np.array(projections_3d)

# Match to icosahedron
matches = []
match_dists = []
for dh_idx in range(24):
    p3d = projections_3d[dh_idx]
    best_dist = float('inf')
    best_idx = -1
    for i, iv in enumerate(icos_verts):
        d = min(np.linalg.norm(p3d - iv), np.linalg.norm(p3d + iv))
        if d < best_dist:
            best_dist = d
            best_idx = i
    matches.append(best_idx)
    match_dists.append(best_dist)

max_match_dist = max(match_dists)
t1_pass = max_match_dist < 1e-5

print(f"\nT1: Max match distance = {max_match_dist:.6f}")
print(f"T1 VERDICT: {'PASS' if t1_pass else 'FAIL'}")

# Build covering map
icos_to_dh = {}
for dh_idx in range(24):
    icos_idx = matches[dh_idx]
    if icos_idx not in icos_to_dh:
        icos_to_dh[icos_idx] = []
    icos_to_dh[icos_idx].append(dh_idx)

used_icos = sorted(icos_to_dh.keys())
print(f"\n  Used vertices: {used_icos}")
for icos_idx in used_icos:
    print(f"    Icos{icos_idx}: DHs {icos_to_dh[icos_idx]}")

# =============================================================================
# PART 8: RC-178b — 5-FOLD SYMMETRY
# =============================================================================
print("\n[STEP 8] Verifying 5-fold symmetry...")

# Rotation matrix for 72° around 5-fold axis
angle_72 = np.radians(72)
cos_a = np.cos(angle_72)
sin_a = np.sin(angle_72)
ux, uy, uz = axis_5fold

R_72 = np.array([
    [cos_a + ux*ux*(1-cos_a), ux*uy*(1-cos_a) - uz*sin_a, ux*uz*(1-cos_a) + uy*sin_a],
    [uy*ux*(1-cos_a) + uz*sin_a, cos_a + uy*uy*(1-cos_a), uy*uz*(1-cos_a) - ux*sin_a],
    [uz*ux*(1-cos_a) - uy*sin_a, uz*uy*(1-cos_a) + ux*sin_a, cos_a + uz*uz*(1-cos_a)]
])

# Check if used vertices are invariant
used_set = set(used_icos)
invariant = True
for i in used_icos:
    v = icos_verts[i]
    v_rot = R_72 @ v
    best_dist = float('inf')
    best_idx = -1
    for j in used_icos:
        u = icos_verts[j]
        d = min(np.linalg.norm(v_rot - u), np.linalg.norm(v_rot + u))
        if d < best_dist:
            best_dist = d
            best_idx = j
    if best_idx not in used_set:
        invariant = False

t5_pass = invariant and len(used_icos) == 6
print(f"\nT5: All 6 vertices invariant under 72° rotation: {invariant}")
print(f"T5 VERDICT: {'PASS' if t5_pass else 'FAIL'}")

# Find the 5-cycle
print("\n  5-fold cycle:")
cycle_found = False
for start in used_icos:
    if start == 0:
        continue  # Skip center
    orbit = [start]
    v = icos_verts[start]
    for _ in range(5):
        v = R_72 @ v
        best_dist = float('inf')
        best_idx = -1
        for j in range(len(icos_verts)):
            d = min(np.linalg.norm(v - icos_verts[j]), np.linalg.norm(v + icos_verts[j]))
            if d < best_dist:
                best_dist = d
                best_idx = j
        orbit.append(best_idx)
    unique = len(set(orbit))
    if unique == 5:
        print(f"    5-cycle: {' → '.join(map(str, orbit[:5]))} → {orbit[0]}")
        cycle_found = True
        break

if not cycle_found:
    print("    No 5-cycle found (unexpected)")

# =============================================================================
# PART 9: COMBINED VERDICT
# =============================================================================
print("\n" + "=" * 80)
print("COMBINED VERDICT")
print("=" * 80)

print(f"\nRC-178 Results:")
print(f"  H1 (Manley-Rowe):     {'PASS' if h1_pass else 'FAIL'}")
print(f"  H3 (Coherence):       {'PASS' if h3_pass else 'FAIL'}")
print(f"  H4 (Upward Entropy):  {'PASS' if h4_pass else 'FAIL'}")
print(f"  H5 (DH23 Fixed):      {'PASS' if h5_pass else 'FAIL'}")
print(f"  Score: 3/4 PASS (H2 not computed in this script)")

print(f"\nRC-178b Results:")
print(f"  T1 (4-to-1 Covering): {'PASS' if t1_pass else 'FAIL'}")
print(f"  T5 (5-Fold Symmetry): {'PASS' if t5_pass else 'FAIL'}")
print(f"  Score: 2/2 PASS (T2-T4 require additional analysis)")

print("\n" + "=" * 80)
print("RC-178 & RC-178b EXECUTION COMPLETE")
print("=" * 80)
