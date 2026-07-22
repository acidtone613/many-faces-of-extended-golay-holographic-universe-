#!/usr/bin/env python3
"""
RC-188: THE HIGGS MECHANISM — SYMMETRY BREAKING FROM THE CHIRAL COLLAPSE
Framework: 24D-DMF v8.4.6 | Date: 2026-07-21
Complete self-contained reproduction script.
Dependencies: numpy, matplotlib
"""

import numpy as np
from itertools import product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
import warnings
warnings.filterwarnings('ignore')

np.random.seed(188)

# =============================================================================
# FRAMEWORK FOUNDATION (from RC-184/RC-122/RC-116)
# =============================================================================

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

# Floquet tick operators (24D)
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

# =============================================================================
# TASK 1: Generate E8 Roots and Isolate Collapsed Chiral Roots
# =============================================================================

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

# Split into D4 blocks and mixed roots
block1_roots, block2_roots, mixed_roots = [], [], []
for r in e8_roots:
    nz1, nz2 = np.count_nonzero(r[:4]), np.count_nonzero(r[4:])
    if nz1 > 0 and nz2 == 0:
        block1_roots.append(r)
    elif nz1 == 0 and nz2 > 0:
        block2_roots.append(r)
    else:
        mixed_roots.append(r)

# Triality split: identify Sector 2 (8s+, 8s+)
sector_2_roots, sector_1_roots, sector_3_roots = [], [], []
for r in np.array(mixed_roots):
    nz1, nz2 = np.count_nonzero(r[:4]), np.count_nonzero(r[4:])
    if nz1 == 4 and nz2 == 4:
        mc1, mc2 = np.sum(r[:4] < 0), np.sum(r[4:] < 0)
        if mc1 % 2 == 0 and mc2 % 2 == 0:
            sector_2_roots.append(r)
        elif mc1 % 2 == 1 and mc2 % 2 == 1:
            sector_3_roots.append(r)
        else:
            sector_1_roots.append(r)
    else:
        sector_1_roots.append(r)

sector_2_roots = np.array(sector_2_roots)

# Find 16 collapsed roots (zero quaternion norm)
collapsed_roots, collapsed_indices = [], []
for idx, root in enumerate(sector_2_roots):
    v_24d = np.pad(root, (0, 16))
    q = extract_quaternion(v_24d)
    if np.linalg.norm(q) < 1e-10:
        collapsed_roots.append(root)
        collapsed_indices.append(idx)
collapsed_roots = np.array(collapsed_roots)
n_collapsed = len(collapsed_roots)

print(f"RC-188: Found {n_collapsed} collapsed chiral roots")

# =============================================================================
# TASK 2: Evolve Through Floquet Cycle
# =============================================================================

TICKS = 22
norm_matrix = np.zeros((n_collapsed, TICKS))
phase_matrix = np.zeros((n_collapsed, TICKS))

for r_idx, root in enumerate(collapsed_roots):
    v_24d = np.pad(root, (0, 16))
    current_v = v_24d.copy()
    for t in range(TICKS):
        q = extract_quaternion(current_v)
        norm_matrix[r_idx, t] = np.linalg.norm(q)
        if len(q) >= 2 and (abs(q[0]) > 1e-15 or abs(q[1]) > 1e-15):
            phase_matrix[r_idx, t] = np.arctan2(q[1], q[0])
        if t < TICKS - 1:
            current_v = apply_tick_vector(current_v, t)

variance_curve = np.var(norm_matrix, axis=0)
mean_norm_curve = np.mean(norm_matrix, axis=0)

# =============================================================================
# TASK 3: Detect Phase Transition
# =============================================================================

delta_var = np.diff(variance_curve)
t_star = np.argmax(np.abs(delta_var))
spike_tick = t_star + 1

# =============================================================================
# TASK 4: Mass Proxy
# =============================================================================

Total_Energy = np.sum(variance_curve)
Var_0_10 = np.mean(variance_curve[:11])
Var_12_21 = np.mean(variance_curve[12:])
Delta_Var = Var_12_21 - Var_0_10
M_WZ = Delta_Var / Var_0_10 if Var_0_10 > 1e-15 else float('inf')

# =============================================================================
# TASK 5: Visualization
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.suptitle('RC-188: Higgs Mechanism — Symmetry Breaking from Chiral Collapse', fontsize=14, fontweight='bold')

ticks = np.arange(TICKS)
colors = plt.cm.tab20(np.linspace(0, 1, n_collapsed))

# Plot 1
ax1 = axes[0, 0]
ax1.plot(ticks, variance_curve, 'b-', linewidth=2.5, marker='o', markersize=6, label='Variance Var(t)')
ax1.axvline(x=11, color='r', linestyle='--', linewidth=1.5, alpha=0.7, label='Tick 11 (H_L gate)')
ax1.axvline(x=spike_tick, color='g', linestyle=':', linewidth=2, alpha=0.8, label=f'Tick {spike_tick} (max |ΔVar|)')
ax1.fill_between(ticks, variance_curve, alpha=0.15, color='blue')
ax1.set_xlabel('Tick')
ax1.set_ylabel('Variance of Quaternion Norms')
ax1.set_title('Plot 1: Variance Curve — Symmetry Breaking Detection', fontweight='bold')
ax1.set_xticks(ticks)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', fontsize=9)

# Plot 2
ax2 = axes[0, 1]
for i in range(n_collapsed):
    ax2.plot(ticks, norm_matrix[i], '-', linewidth=1.2, alpha=0.7, color=colors[i])
ax2.axvline(x=11, color='r', linestyle='--', linewidth=1.5, alpha=0.7)
ax2.axvline(x=spike_tick, color='g', linestyle=':', linewidth=2, alpha=0.8)
ax2.set_xlabel('Tick')
ax2.set_ylabel('Quaternion Norm ||q||')
ax2.set_title('Plot 2: Norm Trajectories of 16 Collapsed Roots', fontweight='bold')
ax2.set_xticks(ticks)
ax2.grid(True, alpha=0.3)

# Plot 3
ax3 = axes[1, 0]
im = ax3.imshow(norm_matrix, aspect='auto', cmap='viridis', interpolation='nearest')
ax3.axvline(x=11, color='r', linestyle='--', linewidth=2, alpha=0.8)
ax3.axvline(x=spike_tick, color='white', linestyle=':', linewidth=2, alpha=0.9)
ax3.set_xlabel('Tick')
ax3.set_ylabel('Collapsed Root Index')
ax3.set_title('Plot 3: Norm Heatmap — 16 Roots × 22 Ticks', fontweight='bold')
ax3.set_xticks(ticks)
ax3.set_yticks(range(n_collapsed))
plt.colorbar(im, ax=ax3, label='Quaternion Norm')

# Plot 4
ax4 = axes[1, 1]
for i in range(min(8, n_collapsed)):
    ax4.plot(ticks, phase_matrix[i], '-', linewidth=1.0, alpha=0.5, color=colors[i])
ax4_twin = ax4.twinx()
ax4_twin.bar(np.arange(len(delta_var)) + 0.5, delta_var, width=0.6, alpha=0.3, color='gray')
ax4_twin.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax4_twin.set_ylabel('ΔVar(t)', color='gray')
ax4.axvline(x=11, color='r', linestyle='--', linewidth=1.5, alpha=0.7)
ax4.axvline(x=spike_tick, color='g', linestyle=':', linewidth=2, alpha=0.8)
ax4.set_xlabel('Tick')
ax4.set_ylabel('Phase Angle (rad)')
ax4.set_title('Plot 4: Phase Trajectories (8 roots) + ΔVar Overlay', fontweight='bold')
ax4.set_xticks(ticks)
ax4.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('RC-188_Symmetry_Breaking.png', dpi=150, bbox_inches='tight')
plt.close()

# =============================================================================
# SAVE OUTPUTS
# =============================================================================

with open('collapsed_roots.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Root_Index'] + [f'Dim_{i}' for i in range(8)])
    for idx, root in enumerate(collapsed_roots):
        writer.writerow([idx] + [f'{x:.6f}' for x in root])

with open('variance_curve.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Tick', 'Variance', 'Mean_Norm'])
    for t in range(TICKS):
        writer.writerow([t, f'{variance_curve[t]:.10f}', f'{mean_norm_curve[t]:.10f}'])

with open('norm_matrix.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['Root_Index'] + [f'Tick_{t}' for t in range(TICKS)]
    writer.writerow(header)
    for i in range(n_collapsed):
        writer.writerow([i] + [f'{x:.10f}' for x in norm_matrix[i]])

print(f"\nRC-188 VERDICT: TICK {spike_tick} — REVISION NEEDED")
print(f"  Max variance: {variance_curve.max():.6f} at Tick {np.argmax(variance_curve)}")
print(f"  Mass proxy M_WZ: {M_WZ:.6f}")
print("\nAll outputs saved.")
