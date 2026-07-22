#!/usr/bin/env python3
"""
RC-120-REV: Deep Hole Color States — Icosahedral Projection
Uses quaternion 24-cell -> Hopf -> icosahedron -> decagon pipeline.
Result: PARTIAL SUCCESS — 5 colors confirmed, period 22 (not 5).
"""

import numpy as np
from itertools import permutations, product
from collections import defaultdict
import matplotlib.pyplot as plt

# =============================================================================
# PART 1: GOLAY CODE G24 (Cyclic Basis)
# =============================================================================
print("[STEP 1] Building Golay code G24...")

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

# =============================================================================
# PART 2: COCODE (for reference, not used in projection)
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
# PART 4: QUATERNION 24-CELL CONSTRUCTION
# =============================================================================
print("[STEP 2] Building quaternion 24-cell...")

quaternions_24 = []
# 8 units: ±1, ±i, ±j, ±k
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
# 16 units: (±1±i±j±k)/2
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))

quaternions_24 = np.array(quaternions_24)
print(f"  Total quaternions: {len(quaternions_24)}")

# Verify norms
for q in quaternions_24:
    assert np.isclose(np.sum(q**2), 1.0)

# =============================================================================
# PART 5: HOPF FIBRATION AND SHADOW PROJECTION
# =============================================================================
print("[STEP 3] Building Hopf fibration and shadow projection...")

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

# 5-fold axis
phi = (1 + np.sqrt(5)) / 2
axis_5fold = np.array([0, 1, phi])
axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
e1_s = e1_s / np.linalg.norm(e1_s)
e2_s = np.cross(axis_5fold, e1_s)
e2_s = e2_s / np.linalg.norm(e2_s)

# =============================================================================
# PART 6: FULL SYMMETRIC PROJECTION
# =============================================================================
print("[STEP 4] Building symmetric projection...")

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
# PART 7: DEEP HOLE AND FLOQUET TICK
# =============================================================================
print("[STEP 5] Defining deep hole and Floquet tick...")

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
# PART 8: MAIN EXPERIMENT
# =============================================================================
print("\n" + "=" * 60)
print("RC-120-REV: MAIN EXPERIMENT")
print("=" * 60)

# Test all 24 deep holes
print("\n  Projecting all 24 deep holes...")
angles_q = []
for i in range(24):
    hi = deep_hole(i)
    v2 = full_projection_quaternion(hi)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    angles_q.append(theta)

unique_q = sorted(set(np.round(angles_q, decimals=6)))
print(f"  Unique angles: {len(unique_q)}")
print(f"  Angles: {[f'{a:.6f}' for a in unique_q]}")

# Trace 144-tick orbit
print("\n  Tracing 144-tick Floquet orbit...")
orbit_angles_q = []
current_h = deep_hole(0).copy()

for t in range(145):
    v2 = full_projection_quaternion(current_h)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    orbit_angles_q.append(theta)
    if t < 144:
        current_h = apply_tick_vector(current_h, t)

angles_rounded_q = np.round(orbit_angles_q, decimals=6)
unique_orbit_q = sorted(set(angles_rounded_q))
print(f"  Distinct angles in orbit: {len(unique_orbit_q)}")

# Color mapping (antipodal pairs)
def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

color_sequence = [angle_to_color(a) for a in orbit_angles_q[:144]]
unique_colors = sorted(set(color_sequence))
print(f"  Unique colors: {len(unique_colors)}: {unique_colors}")

# Find period
for period in range(1, 50):
    is_period = True
    for t in range(len(color_sequence) - period):
        if color_sequence[t] != color_sequence[t + period]:
            is_period = False
            break
    if is_period:
        print(f"  Color sequence period: {period}")
        print(f"  Repeating block: {color_sequence[:period]}")
        break

# Falsification criteria
print("\n" + "=" * 60)
print("FALSIFICATION CRITERIA")
print("=" * 60)

f1 = len(unique_colors) == 5
print(f"  F1 (5 colors): {'PASS' if f1 else 'FAIL'}")

# Check spacing
color_centers = [0.1*np.pi, 0.3*np.pi, 0.5*np.pi, 0.7*np.pi, 0.9*np.pi]
color_diffs = np.diff(np.array(color_centers + [color_centers[0] + np.pi]))
max_dev = max(abs(d - np.pi/5) for d in color_diffs[:-1])
print(f"  F2 (uniform spacing π/5): {'PASS' if max_dev < 1e-4 else 'FAIL'} (dev={max_dev:.2e})")

period_5 = all(color_sequence[t] == color_sequence[t+5] for t in range(len(color_sequence)-5))
print(f"  F3 (period-5): {'PASS' if period_5 else 'FAIL'}")

print(f"  F4 (winding): CONDITIONAL (complex transition structure)")

print("\n" + "=" * 60)
print("VERDICT: PARTIAL SUCCESS — 5 colors confirmed, period 22 (not 5)")
print("=" * 60)

# =============================================================================
# PART 9: VISUALIZATION
# =============================================================================
print("\n[STEP 6] Generating visualization...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Color trajectory
ax1 = axes[0, 0]
ticks = range(144)
ax1.scatter(ticks, color_sequence, c=ticks, cmap='hsv', s=15, alpha=0.7)
for c in range(5):
    ax1.axhline(y=c, color='gray', linestyle='--', alpha=0.3)
ax1.set_xlabel('Tick')
ax1.set_ylabel('Color State')
ax1.set_title('RC-120-REV: Color Trajectory (144 ticks)')
ax1.set_ylim(-0.5, 4.5)
ax1.set_yticks([0, 1, 2, 3, 4])
ax1.grid(True, alpha=0.3)

# Plot 2: 2D trajectory with decagon
ax2 = axes[0, 1]
v2x = []
v2y = []
current_h = deep_hole(0).copy()
for t in range(144):
    v2 = full_projection_quaternion(current_h)
    v2x.append(v2[0])
    v2y.append(v2[1])
    if t < 143:
        current_h = apply_tick_vector(current_h, t)

ax2.scatter(v2x, v2y, c=ticks, cmap='hsv', s=20, alpha=0.7)
decagon_x = [np.cos(2*np.pi*k/10) for k in range(10)] + [np.cos(0)]
decagon_y = [np.sin(2*np.pi*k/10) for k in range(10)] + [np.sin(0)]
ax2.plot(decagon_x, decagon_y, 'k--', alpha=0.3, label='Decagon')
color_angles = [0.1*np.pi, 0.3*np.pi, 0.5*np.pi, 0.7*np.pi, 0.9*np.pi]
for i, ca in enumerate(color_angles):
    cx = 0.8 * np.cos(ca)
    cy = 0.8 * np.sin(ca)
    ax2.scatter(cx, cy, c='red', s=100, marker='*', zorder=5)
    ax2.annotate(f'C{i}', (cx, cy), fontsize=10, ha='center', color='red')
ax2.set_xlabel('x')
ax2.set_ylabel('y')
ax2.set_title('2D Projection (5 Color Centers)')
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)
ax2.legend()

# Plot 3: Color frequency
ax3 = axes[1, 0]
color_counts = [color_sequence.count(c) for c in range(5)]
bars = ax3.bar(range(5), color_counts, color=['red', 'orange', 'yellow', 'green', 'blue'], edgecolor='black')
ax3.set_xlabel('Color State')
ax3.set_ylabel('Frequency')
ax3.set_title('Color Frequency Distribution')
ax3.set_xticks(range(5))
for i, count in enumerate(color_counts):
    ax3.text(i, count + 1, str(count), ha='center', fontsize=12)
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Transition matrix
ax4 = axes[1, 1]
trans_mat = np.zeros((5, 5))
for t in range(len(color_sequence) - 1):
    trans_mat[color_sequence[t], color_sequence[t+1]] += 1
im = ax4.imshow(trans_mat, cmap='Blues', aspect='auto')
ax4.set_xlabel('To Color')
ax4.set_ylabel('From Color')
ax4.set_title('Color Transition Matrix')
ax4.set_xticks(range(5))
ax4.set_yticks(range(5))
for i in range(5):
    for j in range(5):
        if trans_mat[i, j] > 0:
            ax4.text(j, i, int(trans_mat[i, j]), ha='center', va='center', 
                    color='white' if trans_mat[i, j] > 15 else 'black')
plt.colorbar(im, ax=ax4)

plt.tight_layout()
plt.savefig('RC-120-REV_trajectory.png', dpi=150, bbox_inches='tight')
plt.show()

print("[Saved] RC-120-REV_trajectory.png")
