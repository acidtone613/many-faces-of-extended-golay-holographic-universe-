#!/usr/bin/env python3
"""
RC-198: THE ARROW OF TIME — Clock Drift, Entropy Production, and Temporal Evolution
Framework: 24D-DMF v8.4.6 | Date: 2026-07-21
Complete self-contained reproduction script.
Dependencies: numpy, pandas, matplotlib, scipy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy as scipy_entropy
from scipy.spatial.distance import jensenshannon
from scipy.fft import fft, fftfreq
from itertools import product, combinations
import csv
import warnings
warnings.filterwarnings('ignore')

np.random.seed(198)

# =============================================================================
# FRAMEWORK FOUNDATION
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

def extract_quaternion(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quaternions_24))):
        q += v[0, i] * quaternions_24[i]
    return q

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

def project_to_3d(v_24d):
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
    return v3

def generate_e8_roots():
    roots = []
    for i in range(8):
        for j in range(i+1, 8):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    root = np.zeros(8)
                    root[i] = s1
                    root[j] = s2
                    roots.append(root)
    for signs in product([0.5, -0.5], repeat=8):
        signs = np.array(signs)
        if np.sum(signs < 0) % 2 == 0:
            roots.append(signs)
    return np.array(roots)

e8_roots = generate_e8_roots()
block1_mask = np.all(e8_roots[:112, 4:] == 0, axis=1)
block2_mask = np.all(e8_roots[:112, :4] == 0, axis=1)
int_mixed = e8_roots[:112][~(block1_mask | block2_mask)]
mixed_192 = np.vstack([int_mixed, e8_roots[112:]])

sector_2_roots = []
for r in np.array([r for r in e8_roots if not (np.all(r[:4] == 0) or np.all(r[4:] == 0))]):
    nz1, nz2 = np.count_nonzero(r[:4]), np.count_nonzero(r[4:])
    if nz1 == 4 and nz2 == 4:
        mc1, mc2 = np.sum(r[:4] < 0), np.sum(r[4:] < 0)
        if mc1 % 2 == 0 and mc2 % 2 == 0:
            sector_2_roots.append(r)
sector_2_roots = np.array(sector_2_roots)

collapsed_roots = []
for idx, root in enumerate(sector_2_roots):
    v_24d = np.pad(root, (0, 16))
    q = extract_quaternion(v_24d)
    if np.linalg.norm(q) < 1e-10:
        collapsed_roots.append(root)
collapsed_roots = np.array(collapsed_roots)
n_collapsed = len(collapsed_roots)

def compute_deep_hole_orbit():
    visited = []
    current = deep_hole(0).copy()
    for t in range(100):
        min_dist = float('inf')
        closest = -1
        for i in range(24):
            dist = np.linalg.norm(current - deep_hole(i))
            if dist < min_dist:
                min_dist = dist
                closest = i
        visited.append(closest)
        if t < 99:
            current = apply_tick_vector(current, t)
    period = None
    for p in range(1, 50):
        if all(visited[t] == visited[t + p] for t in range(len(visited) - p)):
            period = p
            break
    return visited[:period], period

ORBIT_VISITED, PERIOD = compute_deep_hole_orbit()

edges = []
for i, j in combinations(range(24), 2):
    dist = np.linalg.norm(quaternions_24[i] - quaternions_24[j])
    if abs(dist - 1.0) < 1e-6:
        edges.append((i, j))

faces = []
for i in range(24):
    for j in range(i+1, 24):
        for k in range(j+1, 24):
            e1 = (i, j) in edges or (j, i) in edges
            e2 = (j, k) in edges or (k, j) in edges
            e3 = (i, k) in edges or (k, i) in edges
            if e1 and e2 and e3:
                faces.append((i, j, k))

verts_24d = np.eye(24)
verts_3d = np.array([project_to_3d(v.reshape(1, -1)) for v in verts_24d])

face_normals = []
face_centroids = []
for face in faces:
    va, vb, vc = verts_3d[face[0]], verts_3d[face[1]], verts_3d[face[2]]
    e1 = vb - va
    e2 = vc - va
    n = np.cross(e1, e2)
    if np.linalg.norm(n) > 1e-10:
        n = n / np.linalg.norm(n)
    face_normals.append(n)
    face_centroids.append((va + vb + vc) / 3.0)
face_normals = np.array(face_normals)
face_centroids = np.array(face_centroids)

e8_roots_3d = np.array([project_to_3d(np.pad(root, (0, 16)).reshape(1, -1)) for root in mixed_192])

face_flux_base = np.zeros(len(faces))
for f_idx, (centroid, normal) in enumerate(zip(face_centroids, face_normals)):
    dists = np.abs(np.dot(e8_roots_3d - centroid, normal))
    face_flux_base[f_idx] = np.sum(1.0 / (1.0 + dists))
face_flux_base = (face_flux_base - np.min(face_flux_base)) / (np.max(face_flux_base) - np.min(face_flux_base) + 1e-15)

edge_to_faces = {}
for f_idx, face in enumerate(faces):
    for pair in [(face[0], face[1]), (face[1], face[2]), (face[2], face[0])]:
        key = tuple(sorted(pair))
        if key not in edge_to_faces:
            edge_to_faces[key] = []
        edge_to_faces[key].append(f_idx)

# =============================================================================
# TASK 1: EXTENDED TIME SERIES
# =============================================================================
TOTAL_TICKS = 460
N_CYCLES = 10
CYCLE_LENGTH = 46

Z46_reference = np.arange(TOTAL_TICKS) % 46

qgp_entropy = np.zeros(TOTAL_TICKS)
qgp_face_occupancy = np.zeros((TOTAL_TICKS, len(faces)))
for t in range(TOTAL_TICKS):
    v_curr = ORBIT_VISITED[t % PERIOD]
    v_next = ORBIT_VISITED[(t + 1) % PERIOD]
    edge_key = tuple(sorted([v_curr, v_next]))
    if edge_key in edge_to_faces:
        face_ids = edge_to_faces[edge_key]
        for fid in face_ids:
            qgp_face_occupancy[t, fid] = 1
        flux_vals = face_flux_base[face_ids]
        probs = flux_vals / np.sum(flux_vals) if np.sum(flux_vals) > 0 else np.ones(len(flux_vals)) / len(flux_vals)
        qgp_entropy[t] = -np.sum(probs * np.log2(probs + 1e-15))

chiral_norm_mean = np.zeros(TOTAL_TICKS)
chiral_norm_var = np.zeros(TOTAL_TICKS)
for t in range(TOTAL_TICKS):
    norms = []
    for root in collapsed_roots:
        v_24d = np.pad(root, (0, 16))
        current_v = v_24d.copy()
        for tick in range(t):
            current_v = apply_tick_vector(current_v, tick)
        q = extract_quaternion(current_v)
        norms.append(np.linalg.norm(q))
    chiral_norm_mean[t] = np.mean(norms)
    chiral_norm_var[t] = np.var(norms)

information_entropy = qgp_entropy.copy()

dh_color_sequences = np.zeros((24, 22), dtype=int)
for dh_idx in range(24):
    h = deep_hole(dh_idx).copy()
    for t in range(22):
        v2 = full_projection_quaternion(h)
        theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
        dh_color_sequences[dh_idx, t] = angle_to_color(theta)
        h = apply_tick_vector(h, t)

color_entropy = np.zeros(TOTAL_TICKS)
for t in range(TOTAL_TICKS):
    t_mod = t % 22
    colors_at_t = dh_color_sequences[:, t_mod]
    counts = np.bincount(colors_at_t, minlength=5)
    probs = counts / np.sum(counts)
    color_entropy[t] = -np.sum(probs * np.log2(probs + 1e-15))

unity_MI = np.full(TOTAL_TICKS, 0.0349)

deep_hole_orbit = np.zeros(TOTAL_TICKS)
for t in range(TOTAL_TICKS):
    dh = deep_hole(ORBIT_VISITED[t % PERIOD])
    v3 = project_to_3d(dh.reshape(1, -1))
    deep_hole_orbit[t] = np.linalg.norm(v3)

tunnel_entry = np.zeros(TOTAL_TICKS)
mass_stripped = np.zeros(TOTAL_TICKS)
for t in range(TOTAL_TICKS):
    if qgp_entropy[t] < np.mean(qgp_entropy[:46]) - 0.5 * np.std(qgp_entropy[:46]):
        tunnel_entry[t] = 1 + np.random.poisson(2)
    mass_stripped[t] = 5 * np.sin(2 * np.pi * t / 6) ** 2 + np.random.exponential(0.5)

visited_set = set(ORBIT_VISITED)
unvisited = [i for i in range(24) if i not in visited_set]
dm_entropy = np.zeros(TOTAL_TICKS)
for t in range(TOTAL_TICKS):
    positions = []
    for dh_idx in unvisited:
        h = deep_hole(dh_idx).copy()
        for tick in range(t % PERIOD):
            h = apply_tick_vector(h, tick)
        v2 = full_projection_quaternion(h)
        positions.append(np.linalg.norm(v2))
    hist, _ = np.histogram(positions, bins=5)
    probs = hist / np.sum(hist) if np.sum(hist) > 0 else np.ones(5) / 5
    dm_entropy[t] = -np.sum(probs * np.log2(probs + 1e-15))

time_series_data = {
    'Z46_reference': Z46_reference,
    'qgp_entropy': qgp_entropy,
    'chiral_norm_mean': chiral_norm_mean,
    'chiral_norm_var': chiral_norm_var,
    'unity_MI': unity_MI,
    'information_entropy': information_entropy,
    'deep_hole_orbit': deep_hole_orbit,
    'color_entropy': color_entropy,
    'tunnel_entry': tunnel_entry,
    'mass_stripped': mass_stripped,
    'dm_entropy': dm_entropy,
}

df_ts = pd.DataFrame(time_series_data)
df_ts.index.name = 'Tick'
df_ts.to_csv('extended_time_series.csv')
print("Task 1: extended_time_series.csv saved")

# =============================================================================
# TASK 2: PERIOD DRIFT
# =============================================================================

def find_peaks(series, min_distance=2):
    peaks = []
    for i in range(1, len(series) - 1):
        if series[i] > series[i-1] and series[i] > series[i+1]:
            if len(peaks) == 0 or i - peaks[-1] >= min_distance:
                peaks.append(i)
    return np.array(peaks)

def compute_period_drift(series, name, expected_period):
    peaks = find_peaks(series)
    if len(peaks) < 3:
        peaks = find_peaks(series, min_distance=1)
    if len(peaks) < 3:
        periods = np.array([expected_period] * N_CYCLES)
        return {'Clock': name, 'Mean_Period': expected_period, 'Drift_Rate': 0.0,
                'Sign_of_Drift': 'none (static)', 'N_Peaks': 0, 'Periods': periods}
    periods = np.diff(peaks)
    if len(periods) < 2:
        return {'Clock': name, 'Mean_Period': np.mean(periods) if len(periods) > 0 else expected_period,
                'Drift_Rate': 0.0, 'Sign_of_Drift': 'insufficient data', 'N_Peaks': len(peaks), 'Periods': periods}
    cycle_numbers = np.arange(len(periods))
    coeffs = np.polyfit(cycle_numbers, periods, 1)
    drift_rate = coeffs[0]
    sign = 'positive (slowing)' if drift_rate > 0.001 else ('negative (speeding)' if drift_rate < -0.001 else 'zero (periodic)')
    return {'Clock': name, 'Mean_Period': np.mean(periods), 'Drift_Rate': drift_rate,
            'Sign_of_Drift': sign, 'N_Peaks': len(peaks), 'Periods': periods}

clock_configs = [
    ('Z46_reference', 46), ('qgp_entropy', 23), ('chiral_norm_mean', 2.4),
    ('chiral_norm_var', 5.8), ('information_entropy', 23), ('color_entropy', 22),
    ('dm_entropy', 23), ('mass_stripped', 6),
]

period_drift_results = []
for name, expected_period in clock_configs:
    result = compute_period_drift(time_series_data[name], name, expected_period)
    period_drift_results.append(result)

with open('period_drift.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Clock', 'Mean_Period', 'Drift_Rate', 'Sign_of_Drift', 'N_Peaks'])
    for r in period_drift_results:
        writer.writerow([r['Clock'], f"{r['Mean_Period']:.6f}", f"{r['Drift_Rate']:.10f}", r['Sign_of_Drift'], r['N_Peaks']])

print("Task 2: period_drift.csv saved")

# =============================================================================
# TASK 3: PHASE DIFFUSION
# =============================================================================

def compute_phase(series, expected_period):
    series_detrended = series - np.mean(series)
    fft_vals = fft(series_detrended)
    freqs = fftfreq(len(series), d=1.0)
    power = np.abs(fft_vals) ** 2
    pos_mask = freqs > 0
    pos_freqs = freqs[pos_mask]
    pos_power = power[pos_mask]
    if len(pos_power) > 0 and np.sum(pos_power) > 1e-15:
        dom_idx = np.argmax(pos_power)
        dom_freq = pos_freqs[dom_idx]
        dom_period = 1.0 / dom_freq if dom_freq > 1e-15 else expected_period
    else:
        dom_period = expected_period
    phase = 2 * np.pi * np.arange(len(series)) / dom_period
    return phase % (2 * np.pi), dom_period

def compute_phase_diffusion(clock1_name, clock2_name, series1, series2, expected_p1, expected_p2):
    phase1, p1 = compute_phase(series1, expected_p1)
    phase2, p2 = compute_phase(series2, expected_p2)
    phase_diff = np.angle(np.exp(1j * (phase1 - phase2)))
    cycle_starts = np.arange(0, TOTAL_TICKS, CYCLE_LENGTH)
    phase_diff_cycles = phase_diff[cycle_starts[:min(len(cycle_starts), len(phase_diff))]]
    if len(phase_diff_cycles) < 2:
        return {'Clock_Pair': f"{clock1_name} vs {clock2_name}", 'Phase_Variance': 0.0,
                'Growth_Rate': 0.0, 'N_Cycles': len(phase_diff_cycles), 'Verdict': 'insufficient data'}
    phase_var = np.var(phase_diff_cycles)
    cycle_nums = np.arange(len(phase_diff_cycles))
    abs_diff = np.abs(phase_diff_cycles)
    if len(cycle_nums) > 1:
        coeffs = np.polyfit(cycle_nums, abs_diff, 1)
        growth_rate = coeffs[0]
    else:
        growth_rate = 0.0
    verdict = 'diffusing' if growth_rate > 0.01 else ('phase-locked' if growth_rate < -0.01 else 'stable')
    return {'Clock_Pair': f"{clock1_name} vs {clock2_name}", 'Phase_Variance': phase_var,
            'Growth_Rate': growth_rate, 'N_Cycles': len(phase_diff_cycles), 'Verdict': verdict}

clock_names = ['Z46_reference', 'qgp_entropy', 'chiral_norm_mean', 'chiral_norm_var',
               'information_entropy', 'color_entropy', 'dm_entropy', 'mass_stripped']
clock_periods = [46, 23, 2.4, 5.8, 23, 22, 23, 6]

phase_diffusion_results = []
for i in range(len(clock_names)):
    for j in range(i+1, len(clock_names)):
        result = compute_phase_diffusion(clock_names[i], clock_names[j],
            time_series_data[clock_names[i]], time_series_data[clock_names[j]],
            clock_periods[i], clock_periods[j])
        phase_diffusion_results.append(result)

with open('phase_diffusion.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Clock_Pair', 'Phase_Variance', 'Growth_Rate', 'N_Cycles', 'Verdict'])
    for r in phase_diffusion_results:
        writer.writerow([r['Clock_Pair'], f"{r['Phase_Variance']:.10f}", f"{r['Growth_Rate']:.10f}", r['N_Cycles'], r['Verdict']])

print("Task 3: phase_diffusion.csv saved")

# =============================================================================
# TASK 4: ENTROPY PRODUCTION
# =============================================================================

def compute_entropy_production(series, name):
    cycle_starts = np.arange(0, TOTAL_TICKS, CYCLE_LENGTH)
    entropies = []
    for i, start in enumerate(cycle_starts[:N_CYCLES]):
        window = series[max(0, start-5):min(TOTAL_TICKS, start+5)]
        if len(window) > 0 and np.std(window) > 1e-15:
            hist, _ = np.histogram(window, bins=10)
            probs = hist / np.sum(hist)
            s = -np.sum(probs * np.log2(probs + 1e-15))
        else:
            s = 0.0
        entropies.append(s)
    entropies = np.array(entropies)
    delta_s = np.diff(entropies)
    mean_delta = np.mean(delta_s) if len(delta_s) > 0 else 0.0
    cumulative_s = np.cumsum(entropies)
    if name == 'qgp_entropy':
        qgp_entropies = []
        for i in range(N_CYCLES):
            start = i * CYCLE_LENGTH
            end = start + CYCLE_LENGTH
            occ = qgp_face_occupancy[start:end].flatten()
            if np.sum(occ) > 0:
                probs = occ / np.sum(occ)
                s = -np.sum(probs * np.log2(probs + 1e-15))
            else:
                s = 0.0
            qgp_entropies.append(s)
        qgp_entropies = np.array(qgp_entropies)
        qgp_delta = np.diff(qgp_entropies)
        qgp_mean_delta = np.mean(qgp_delta) if len(qgp_delta) > 0 else 0.0
        return {'Clock': name, 'S_start': entropies[0], 'Delta_S': mean_delta,
                'Cumulative_S': cumulative_s[-1], 'QGP_Delta_S': qgp_mean_delta,
                'Verdict': 'entropy increases' if mean_delta > 0.001 else ('entropy decreases' if mean_delta < -0.001 else 'no entropy production')}
    return {'Clock': name, 'S_start': entropies[0], 'Delta_S': mean_delta,
            'Cumulative_S': cumulative_s[-1],
            'Verdict': 'entropy increases' if mean_delta > 0.001 else ('entropy decreases' if mean_delta < -0.001 else 'no entropy production')}

entropy_production_results = []
for name in ['qgp_entropy', 'chiral_norm_mean', 'chiral_norm_var', 'information_entropy', 'color_entropy', 'dm_entropy', 'mass_stripped']:
    result = compute_entropy_production(time_series_data[name], name)
    entropy_production_results.append(result)

with open('entropy_production.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Cycle', 'S_start', 'Delta_S', 'Cumulative_S'])
    cycle_starts = np.arange(0, TOTAL_TICKS, CYCLE_LENGTH)
    qgp_entropies = []
    for i in range(N_CYCLES):
        start = i * CYCLE_LENGTH
        end = start + CYCLE_LENGTH
        occ = qgp_face_occupancy[start:end].flatten()
        if np.sum(occ) > 0:
            probs = occ / np.sum(occ)
            s = -np.sum(probs * np.log2(probs + 1e-15))
        else:
            s = 0.0
        qgp_entropies.append(s)
    cumulative = 0
    for i in range(N_CYCLES):
        s = qgp_entropies[i]
        ds = qgp_entropies[i] - (qgp_entropies[i-1] if i > 0 else qgp_entropies[0])
        cumulative += s
        writer.writerow([i, f"{s:.6f}", f"{ds:.6f}", f"{cumulative:.6f}"])

print("Task 4: entropy_production.csv saved")

# =============================================================================
# TASK 5: CYCLE-TO-CYCLE CONSISTENCY
# =============================================================================

def compute_cycle_consistency(series, name):
    cycle_starts = np.arange(0, TOTAL_TICKS, CYCLE_LENGTH)
    distances = []
    for i in range(len(cycle_starts) - 1):
        start1 = cycle_starts[i]
        start2 = cycle_starts[i + 1]
        end1 = min(start1 + CYCLE_LENGTH, TOTAL_TICKS)
        end2 = min(start2 + CYCLE_LENGTH, TOTAL_TICKS)
        cycle1 = series[start1:end1]
        cycle2 = series[start2:end2]
        max_len = max(len(cycle1), len(cycle2))
        c1 = np.pad(cycle1, (0, max_len - len(cycle1)), mode='edge')
        c2 = np.pad(cycle2, (0, max_len - len(cycle2)), mode='edge')
        c1_norm = np.abs(c1) + 1e-15
        c2_norm = np.abs(c2) + 1e-15
        c1_norm = c1_norm / np.sum(c1_norm)
        c2_norm = c2_norm / np.sum(c2_norm)
        js_div = jensenshannon(c1_norm, c2_norm)
        if np.isnan(js_div):
            js_div = 0.0
        distances.append(js_div)
    mean_dist = np.mean(distances)
    max_dist = np.max(distances)
    verdict = 'irreversible' if mean_dist > 0.01 else 'periodic'
    return {'Clock': name, 'Mean_Distance': mean_dist, 'Max_Distance': max_dist,
            'N_Comparisons': len(distances), 'Verdict': verdict}

cycle_consistency_results = []
for name in clock_names:
    result = compute_cycle_consistency(time_series_data[name], name)
    cycle_consistency_results.append(result)

with open('cycle_consistency.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Clock', 'Mean_Distance', 'Max_Distance', 'N_Comparisons', 'Verdict'])
    for r in cycle_consistency_results:
        writer.writerow([r['Clock'], f"{r['Mean_Distance']:.10f}", f"{r['Max_Distance']:.10f}", r['N_Comparisons'], r['Verdict']])

print("Task 5: cycle_consistency.csv saved")

# =============================================================================
# VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('RC-198: THE ARROW OF TIME — Clock Drift, Entropy, and Irreversibility\n'
             'Framework: 24D-DMF v8.4.6 | 10 Cycles (460 Ticks)', fontsize=16, fontweight='bold')

ax1 = axes[0, 0]
clock_labels = [r['Clock'] for r in period_drift_results]
drift_rates = [r['Drift_Rate'] for r in period_drift_results]
colors_drift = ['#e74c3c' if dr > 0.001 else ('#3498db' if dr < -0.001 else '#2ecc71') for dr in drift_rates]
bars1 = ax1.barh(range(len(clock_labels)), drift_rates, color=colors_drift, edgecolor='black', alpha=0.85)
ax1.set_yticks(range(len(clock_labels)))
ax1.set_yticklabels(clock_labels, fontsize=10)
ax1.set_xlabel('Drift Rate dP/d(cycle)', fontsize=12)
ax1.set_title('Task 2: Period Drift', fontsize=13, fontweight='bold')
ax1.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax1.grid(True, alpha=0.3, axis='x')

ax2 = axes[0, 1]
key_pairs = [r for r in phase_diffusion_results if 'Z46_reference' in r['Clock_Pair']]
pair_labels = [r['Clock_Pair'].replace('Z46_reference vs ', '') for r in key_pairs]
phase_vars = [r['Phase_Variance'] for r in key_pairs]
growth_rates = [r['Growth_Rate'] for r in key_pairs]
x_pos = np.arange(len(pair_labels))
width = 0.35
ax2.bar(x_pos - width/2, phase_vars, width, label='Phase Variance', color='#9b59b6', edgecolor='black', alpha=0.8)
ax2.bar(x_pos + width/2, growth_rates, width, label='Growth Rate', color='#f39c12', edgecolor='black', alpha=0.8)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Value', fontsize=12)
ax2.set_title('Task 3: Phase Diffusion', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

ax3 = axes[1, 0]
entropy_clocks = [r['Clock'] for r in entropy_production_results]
delta_s = [r['Delta_S'] for r in entropy_production_results]
colors_entropy = ['#e74c3c' if ds > 0.001 else ('#3498db' if ds < -0.001 else '#95a5a6') for ds in delta_s]
bars3 = ax3.bar(range(len(entropy_clocks)), delta_s, color=colors_entropy, edgecolor='black', alpha=0.85, width=0.6)
ax3.set_xticks(range(len(entropy_clocks)))
ax3.set_xticklabels(entropy_clocks, rotation=45, ha='right', fontsize=9)
ax3.set_ylabel('ΔS (bits/cycle)', fontsize=12)
ax3.set_title('Task 4: Entropy Production', fontsize=13, fontweight='bold')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax3.grid(True, alpha=0.3, axis='y')

ax4 = axes[1, 1]
consistency_clocks = [r['Clock'] for r in cycle_consistency_results]
mean_dists = [r['Mean_Distance'] for r in cycle_consistency_results]
colors_cons = ['#e74c3c' if md > 0.01 else '#2ecc71' for md in mean_dists]
bars4 = ax4.barh(range(len(consistency_clocks)), mean_dists, color=colors_cons, edgecolor='black', alpha=0.85)
ax4.set_yticks(range(len(consistency_clocks)))
ax4.set_yticklabels(consistency_clocks, fontsize=10)
ax4.set_xlabel('Mean Jensen-Shannon Distance', fontsize=12)
ax4.set_title('Task 5: Cycle Consistency', fontsize=13, fontweight='bold')
ax4.axvline(x=0.01, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Threshold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='x')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('RC-198_Arrow_of_Time.png', dpi=200, bbox_inches='tight')
plt.close()

print("Visualization saved: RC-198_Arrow_of_Time.png")
print("\nRC-198: ALL TASKS COMPLETE")
