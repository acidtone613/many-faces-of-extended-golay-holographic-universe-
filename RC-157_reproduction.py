#!/usr/bin/env python3
"""
RC-157: The Running Engine — Couplings from Shattering Scale
CORRECTED EXECUTION — using v8.4.6 Math Reference engines

Framework: 24D-DMF v8.4.6
Date: 2026-07-11
Status: PRE-REGISTERED — Results Binding Upon Execution

Builds on: RC-156 (interaction engine, 4/5 PASS), RC-155c (gauge dynamics, 5/5 PASS),
           RC-154b (shattering confirmed), RC-153b (10 states → 5 colors),
           RC-152 (mass from wavelength), RC-150b (tunnel structure)

CORRECTION: Uses the 22D engine Hamiltonian H_0, perturbation V, and coupling
operators K_22/G_22 from Part IV of v8.4.6, NOT the Floquet tick pipeline.
Energy scale proxy: eigenvalue index in H_0 spectrum (UV = high |λ|, IR = low |λ|).
"""

import numpy as np
from scipy.linalg import null_space, expm, eigh, qr
from scipy.stats import pearsonr, spearmanr
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

np.random.seed(157)

print("=" * 78)
print("RC-157: THE RUNNING ENGINE — CORRECTED")
print("Couplings from Shattering Scale (v8.4.6 Engines)")
print("Framework: 24D-DMF v8.4.6 | Date: 2026-07-11")
print("=" * 78)

# =============================================================================
# PART 0: FRAMEWORK FOUNDATION (v8.4.6 Tier A — CONFIRMED)
# =============================================================================
print("\n[FOUNDATION] Loading v8.4.6 confirmed primitives...")

# --- Golay Code G24 (Cyclic Construction, Sec 1) ---
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

print(f"  Golay G24: {len(code_words)} codewords, self-dual verified: {np.all((G24 @ G24.T) % 2 == 0)}")

# --- Basis-Change Permutation π (QR → Cyclic, Sec 3) ---
pi = np.array([0,1,2,3,4,5,7,8,19,21,17,6,16,13,12,23,11,10,14,15,9,18,22,20])

# --- B_sym (Sec 2) ---
QR0 = {0, 1, 3, 4, 5, 9}
B_sym = np.zeros((12, 12), dtype=int)
for i in range(11):
    for j in range(11):
        if (i + j) % 11 in QR0:
            B_sym[i, j] = 1
B_sym[11, :] = 1
B_sym[:, 11] = 1
B_sym[11, 11] = 0

# --- Gram Matrix G (Sec 2, Part II) ---
G_gram = B_sym @ B_sym.T
eigvals_G = np.linalg.eigvalsh(G_gram.astype(float))
print(f"  Gram eigenvalues: {np.round(eigvals_G, 6)}")
lambda1 = 29 + 12*np.sqrt(5)
lambda12 = 29 - 12*np.sqrt(5)
print(f"  λ1 = {lambda1:.6f}, λ12 = {lambda12:.6f}")
print(f"  √λ1 - √λ12 = {np.sqrt(lambda1) - np.sqrt(lambda12):.6f} (Gram gap = 6)")
print(f"  det(G) = {int(np.round(np.linalg.det(G_gram.astype(float))))} (expected 7,144,929)")

# --- Engine Generators P23, P11 (Sec 9) ---
P23 = np.zeros((24, 24), dtype=int)
for i in range(23):
    P23[i, (i+1) % 23] = 1
P23[23, 23] = 1

P11 = np.zeros((24, 24), dtype=int)
for i in range(23):
    P11[i, (2*i) % 23] = 1
P11[23, 23] = 1

# Verify they preserve the code
all_preserve = True
for cw in code_words:
    for P in [P23, P11]:
        mapped = (P @ cw) % 2
        if tuple(mapped) not in code_set:
            all_preserve = False
            break
print(f"  P23, P11 preserve code: {all_preserve}")

# --- 22D Engine Space (Sec 12) ---
v_uniform = np.ones(23) / np.sqrt(23)
P_perp = np.eye(23) - np.outer(v_uniform, v_uniform)
U, S, Vt = np.linalg.svd(P_perp)
basis_22 = U[:, :22]

# Project operators to 22D
P23_22 = basis_22.T @ P23[:23, :23] @ basis_22
P11_22 = basis_22.T @ P11[:23, :23] @ basis_22

print(f"  P23_22 order check: {np.linalg.matrix_power(P23_22, 23).round(10).max():.2e}")
print(f"  P11_22 order check: {np.linalg.matrix_power(P11_22, 11).round(10).max():.2e}")

# --- Unperturbed Hamiltonian H0 (Sec 13) ---
alpha = 3.0
H0 = (P23_22 + P23_22.T) + alpha * (P11_22 + P11_22.T)
H0 = (H0 + H0.T) / 2

eigvals_H0, eigvecs_H0 = eigh(H0)
print(f"\n  H0 spectrum (11 distinct pairs, 2-fold degeneracy):")
unique_eigvals = []
for i in range(0, 22, 2):
    unique_eigvals.append(eigvals_H0[i])
    print(f"    Pair {i//2}: λ = {eigvals_H0[i]:.6f} (degeneracy 2)")
unique_eigvals = np.array(unique_eigvals)

max_degen_diff = max(abs(eigvals_H0[i] - eigvals_H0[i+1]) for i in range(0, 22, 2))
print(f"  Max degeneracy violation: {max_degen_diff:.2e}")

# =============================================================================
# PART 1: Rank-2 Perturbation V and Coupling Operators (Sec 14-15)
# =============================================================================
print("\n[STEP 1] Building perturbation V and coupling operators...")

A_orbit = {1,2,3,4,6,8,9,12,13,16,18}
B_orbit = {5,7,10,11,14,15,17,19,20,21,22}

v_A = np.zeros(23)
for i in A_orbit:
    v_A[i] = 1
v_B = np.zeros(23)
for i in B_orbit:
    v_B[i] = 1

v_A_perp = v_A - np.dot(v_A, v_uniform) * v_uniform
v_B_perp = v_B - np.dot(v_B, v_uniform) * v_uniform

A_22 = basis_22.T @ v_A_perp
B_22 = basis_22.T @ v_B_perp

A_22 = A_22 / np.linalg.norm(A_22)
B_22 = B_22 / np.linalg.norm(B_22)

print(f"  A_22 · B_22 = {np.dot(A_22, B_22):.6f} (expected -11/12 ≈ -0.916667)")

V = np.outer(A_22, B_22) + np.outer(B_22, A_22)
print(f"  V is symmetric: {np.allclose(V, V.T)}")
print(f"  V rank: {np.linalg.matrix_rank(V)}")

# --- K_22 coupling operator (Sec 15) ---
G_float = G_gram.astype(float)
eigvals_G, eigvecs_G = eigh(G_float)
idx_3 = np.where(np.abs(eigvals_G - 3.0) < 1e-10)[0]
U_bulk = eigvecs_G[:, idx_3]

sqrt11 = np.sqrt(11)
K_bulk = np.zeros((10, 10))
for i in range(5):
    K_bulk[2*i, 2*i+1] = -sqrt11
    K_bulk[2*i+1, 2*i] = sqrt11

K_12 = U_bulk @ K_bulk @ U_bulk.T

K_24 = np.zeros((24, 24))
K_24[12:24, 12:24] = K_12

K_cyclic = np.zeros((24, 24))
pi_inv = np.zeros(24, dtype=int)
for i in range(24):
    pi_inv[pi[i]] = i
for a in range(24):
    for b in range(24):
        K_cyclic[a, b] = K_24[pi_inv[a], pi_inv[b]]

K_22 = basis_22.T @ K_cyclic[:23, :23] @ basis_22
K_22 = (K_22 - K_22.T) / 2

print(f"  K_22 is skew-symmetric: {np.allclose(K_22, -K_22.T)}")
K_eigvals = np.linalg.eigvals(K_22)
print(f"  K_22 eigenvalues: {np.round(np.sort(np.imag(K_eigvals)), 6)}")

# --- G_22 coupling operator (Sec 15) ---
G_bulk = U_bulk @ (3.0 * np.eye(10)) @ U_bulk.T
G_24 = np.zeros((24, 24))
G_24[12:24, 12:24] = G_bulk

G_cyclic = np.zeros((24, 24))
for a in range(24):
    for b in range(24):
        G_cyclic[a, b] = G_24[pi_inv[a], pi_inv[b]]

G_22 = basis_22.T @ G_cyclic[:23, :23] @ basis_22
G_22 = (G_22 + G_22.T) / 2

print(f"  G_22 is symmetric: {np.allclose(G_22, G_22.T)}")

# =============================================================================
# PART 2: Build the Unified Hamiltonian
# =============================================================================
print("\n[STEP 2] Building unified Hamiltonian...")

beta = 3.0 / np.sqrt(11)
gamma = 0.0
epsilon = (1 + 2/23) / (46 * np.sqrt(11))
print(f"  β = {beta:.6f}, γ = {gamma:.6f}, ε = {epsilon:.8f}")

H_unified = H0 + beta * K_22 + gamma * G_22 + epsilon * V
H_unified = (H_unified + H_unified.T.conj()) / 2

eigvals_unified, eigvecs_unified = eigh(H_unified)

print(f"\n  Unified Hamiltonian spectrum (22 eigenvalues):")
for i in range(22):
    print(f"    E_{i:2d} = {eigvals_unified[i]:.6f}")

# =============================================================================
# PART 3: Map Eigenstates to Color States via Full Projection Pipeline
# =============================================================================
print("\n[STEP 3] Mapping eigenstates to color states...")

from itertools import product

quaternions_24 = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quaternions_24.append(q)
for signs in product([0.5, -0.5], repeat=4):
    quaternions_24.append(list(signs))
quaternions_24 = np.array(quaternions_24)

phi = (1 + np.sqrt(5)) / 2
axis_5fold = np.array([0, 1, phi])
axis_5fold = axis_5fold / np.linalg.norm(axis_5fold)
e1_s = np.array([1, 0, 0]) - (np.array([1, 0, 0]) @ axis_5fold) * axis_5fold
e1_s = e1_s / np.linalg.norm(e1_s)
e2_s = np.cross(axis_5fold, e1_s)
e2_s = e2_s / np.linalg.norm(e2_s)

p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])

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

# Compute shattering amplitudes and colors
shattering_amps = np.array([np.abs(v.T @ V @ v) for v in eigvecs_unified.T])

colors_new = []
shadow_coords = []
for i in range(22):
    v_22 = eigvecs_unified[:, i]
    v_23 = basis_22 @ v_22
    v_24 = np.zeros(24)
    v_24[:23] = v_23
    v2 = full_projection_quaternion(v_24)
    theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
    colors_new.append(angle_to_color(theta))
    shadow_coords.append(v2)

colors_new = np.array(colors_new)
shadow_coords = np.array(shadow_coords)

structural_map = {
    0: {'name': 'Red',    'interaction': 'Higgs / Mass', 'gauge': 'SU(2)×U(1)', 'ssb_index': 2},
    1: {'name': 'Orange', 'interaction': 'Gravity',      'gauge': 'None',       'ssb_index': 1},
    2: {'name': 'Yellow', 'interaction': 'QCD',          'gauge': 'SU(3)',      'ssb_index': 0},
    3: {'name': 'Green',  'interaction': 'QED',          'gauge': 'U(1)',       'ssb_index': 0},
    4: {'name': 'Blue',   'interaction': 'Weak',         'gauge': 'SU(2)',      'ssb_index': 3},
}

print(f"\n  Eigenstate colors:")
print(f"  {'State':>6} {'Energy':>10} {'ShatterAmp':>12} {'Color':>6} {'Name':>8}")
for i in range(22):
    c = colors_new[i]
    print(f"  {i:6d} {eigvals_unified[i]:10.4f} {shattering_amps[i]:12.6f} {c:6d} {structural_map[c]['name']:8s}")

# =============================================================================
# T1-T5 TESTS
# =============================================================================
print("\n" + "=" * 78)
print("T1: Shattering Amplitude Runs with Energy Scale")
print("=" * 78)

index_scale = np.arange(22)
energy_scale = np.abs(eigvals_unified)

corr_amp_index, p_amp_index = pearsonr(shattering_amps, index_scale)
corr_amp_energy, p_amp_energy = pearsonr(shattering_amps, energy_scale)
corr_amp_index_s, p_amp_index_s = spearmanr(shattering_amps, index_scale)

print(f"\n  Correlation (amp vs index):   r = {corr_amp_index:.4f} (p = {p_amp_index:.4f})")
print(f"  Spearman (amp vs index):      ρ = {corr_amp_index_s:.4f} (p = {p_amp_index_s:.4f})")

C1_pass = (abs(corr_amp_index) > 0.5 and p_amp_index < 0.05) or           (abs(corr_amp_index_s) > 0.5 and p_amp_index_s < 0.05)
print(f"\n  C1: {'PASS' if C1_pass else 'FAIL'}")

# T2 — QCD
print("\n" + "=" * 78)
print("T2: QCD (Yellow) Runs to Strong Coupling at IR")
print("=" * 78)

yellow_mask = (colors_new == 2)
yellow_energies = eigvals_unified[yellow_mask]
yellow_amps = shattering_amps[yellow_mask]

yellow_ir = yellow_amps[yellow_energies < 0]
yellow_uv = yellow_amps[yellow_energies > 0]
yellow_ir_mean = np.mean(yellow_ir) if len(yellow_ir) > 0 else 0
yellow_uv_mean = np.mean(yellow_uv) if len(yellow_uv) > 0 else 0
yellow_ratio = yellow_ir_mean / yellow_uv_mean if yellow_uv_mean > 0 else float('inf')

print(f"\n  Yellow IR mean: {yellow_ir_mean:.6f}, UV mean: {yellow_uv_mean:.6f}")
print(f"  IR/UV ratio: {yellow_ratio:.4f}")
C2_pass = yellow_ratio > 2.0
print(f"  C2: {'PASS' if C2_pass else 'FAIL'}")

# T3 — QED
print("\n" + "=" * 78)
print("T3: QED (Green) Runs to Weak Coupling at IR")
print("=" * 78)

green_mask = (colors_new == 3)
green_amps = shattering_amps[green_mask]
green_energies = eigvals_unified[green_mask]

all_ir_mean = np.mean(shattering_amps[eigvals_unified < 0])
all_uv_mean = np.mean(shattering_amps[eigvals_unified > 0])
green_ir = green_amps[green_energies < 0]
green_uv = green_amps[green_energies > 0]
green_ir_mean = np.mean(green_ir) if len(green_ir) > 0 else 0
green_uv_mean = np.mean(green_uv) if len(green_uv) > 0 else 0

if all_ir_mean > 0 and all_uv_mean > 0:
    green_relative_ir = green_ir_mean / all_ir_mean
    green_relative_uv = green_uv_mean / all_uv_mean
    C3_pass = green_relative_ir < green_relative_uv * 0.5
else:
    C3_pass = False

print(f"\n  Green relative IR: {green_relative_ir:.4f}, UV: {green_relative_uv:.4f}")
print(f"  C3: {'PASS' if C3_pass else 'FAIL'}")

# T4 — Weak
print("\n" + "=" * 78)
print("T4: Weak Force (Blue) Has a Threshold")
print("=" * 78)

blue_mask = (colors_new == 4)
blue_states = np.where(blue_mask)[0]
blue_energies = eigvals_unified[blue_mask]
blue_amps = shattering_amps[blue_mask]

blue_sorted_idx = np.argsort(blue_energies)
blue_sorted_amps = blue_amps[blue_sorted_idx]

if len(blue_sorted_amps) >= 2:
    blue_diffs = np.diff(blue_sorted_amps)
    max_jump = np.max(blue_diffs)
    max_jump_idx = np.argmax(blue_diffs)
    before_mean = np.mean(blue_sorted_amps[:max_jump_idx+1])
    after_mean = np.mean(blue_sorted_amps[max_jump_idx+1:])
    C4_threshold = max_jump > 0.1 and after_mean > before_mean * 2
else:
    C4_threshold = False

red_mask = (colors_new == 0)
red_amps = shattering_amps[red_mask]
red_energies = eigvals_unified[red_mask]

if C4_threshold and len(red_amps) > 0:
    threshold_E = blue_energies[blue_sorted_idx][max_jump_idx]
    red_near = [red_amps[i] for i in range(len(red_amps)) if abs(red_energies[i] - threshold_E) < 1.0]
    red_else = [red_amps[i] for i in range(len(red_amps)) if abs(red_energies[i] - threshold_E) >= 1.0]
    C4_higgs = np.mean(red_near) > np.mean(red_else) * 1.2 if red_near and red_else else False
else:
    C4_higgs = False

C4_pass = C4_threshold or C4_higgs
print(f"\n  Blue max jump: {max_jump:.6f}, C4: {'PASS' if C4_pass else 'FAIL'}")

# T5 — Beta function
print("\n" + "=" * 78)
print("T5: The Beta Function Is Geometric")
print("=" * 78)

sort_idx = np.argsort(eigvals_unified)
sorted_E = eigvals_unified[sort_idx]
sorted_amp = shattering_amps[sort_idx]

beta = np.zeros(22)
beta[0] = (sorted_amp[1] - sorted_amp[0]) / (sorted_E[1] - sorted_E[0])
beta[-1] = (sorted_amp[-1] - sorted_amp[-2]) / (sorted_E[-1] - sorted_E[-2])
for i in range(1, 21):
    beta[i] = (sorted_amp[i+1] - sorted_amp[i-1]) / (sorted_E[i+1] - sorted_E[i-1])

ss_tot = np.sum((beta - np.mean(beta))**2)

# Linear
linear_coeffs = np.polyfit(sorted_E, beta, 1)
beta_linear = np.polyval(linear_coeffs, sorted_E)
r2_linear = 1 - np.sum((beta - beta_linear)**2) / ss_tot if ss_tot > 0 else 0

# Log-periodic
def log_periodic(E, a, omega, eps, gamma, c):
    return a * np.cos(omega * np.log(np.abs(E) + eps)) * np.power(np.abs(E) + eps, -gamma) + c

try:
    popt_lp, _ = curve_fit(log_periodic, sorted_E, beta, maxfev=10000)
    beta_lp = log_periodic(sorted_E, *popt_lp)
    r2_lp = 1 - np.sum((beta - beta_lp)**2) / ss_tot if ss_tot > 0 else 0
except:
    r2_lp = -1

best_r2 = max(r2_linear, r2_lp)
C5_pass = best_r2 > 0.7
print(f"\n  Best R² = {best_r2:.4f}")
print(f"  C5: {'PASS' if C5_pass else 'FAIL'}")

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "=" * 78)
print("RC-157 FINAL VERDICT")
print("=" * 78)

print(f"""
FALSIFICATION CRITERIA:
  C1 (Amplitude correlates with energy scale):       {'PASS' if C1_pass else 'FAIL'}
  C2 (Yellow runs to strong at IR, ratio > 2):     {'PASS' if C2_pass else 'FAIL'}
  C3 (Green runs to weak at IR, screening):        {'PASS' if C3_pass else 'FAIL'}
  C4 (Blue threshold behavior):                      {'PASS' if C4_pass else 'FAIL'}
  C5 (Beta function geometric, R² > 0.7):          {'PASS' if C5_pass else 'FAIL'}
""")

pass_condition = C1_pass and (C2_pass or C3_pass) and (C4_pass or C5_pass)
print(f"  PASS CONDITION: {pass_condition}")

if pass_condition:
    verdict = "RUNNING ENGINE CONFIRMED"
    next_step = "RC-158: Build the 4-point vertex model."
elif C1_pass and (C2_pass or C3_pass):
    verdict = "PARTIAL — Running confirmed, beta function unclear"
    next_step = "RC-157b: Refine the running model."
elif C1_pass:
    verdict = "PARTIAL — Scale dependence confirmed, running direction unclear"
    next_step = "RC-157b: Refine the running model."
else:
    verdict = "NO RUNNING"
    next_step = "Re-evaluate the energy-scale proxy."

print(f"\n  OVERALL: {verdict}")
print(f"\n  NEXT STEP: {next_step}")
print("=" * 78)
print("RC-157 EXECUTION COMPLETE")
print("=" * 78)
