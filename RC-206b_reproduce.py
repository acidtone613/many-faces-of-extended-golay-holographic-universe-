#!/usr/bin/env python3
"""
RC-206b: ALTERNATIVE DYNAMICS VERIFICATION — Complete Reproduction Script
Tests quantum walk, information geometry, Lindbladian, and synchronization.

Framework: 24D-DMF v8.4.6
Date: 2026-07-22
Dependencies: numpy, pandas, scipy
"""

import numpy as np
import pandas as pd
from scipy.linalg import logm
import warnings
warnings.filterwarnings('ignore')

np.random.seed(206)

print("=" * 78)
print("RC-206b: ALTERNATIVE DYNAMICS VERIFICATION")
print("Framework: 24D-DMF v8.4.6 | Date: 2026-07-22")
print("=" * 78)
print()

# =============================================================================
# SECTION 1: FOUNDATIONAL DATA (from RC-203, RC-204, RC-205b)
# =============================================================================

PHI = (1 + np.sqrt(5)) / 2
A_COLOR = np.array([1.0000, 1.3764, 0.8507, 0.5257, 0.5257])
COLOR_NAMES = ['Red', 'Orange', 'Yellow', 'Green', 'Blue']
SYNC_TICKS = [3, 11, 13, 22, 26, 30, 33, 35, 44]

# Deep hole construction
def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

# Floquet tick operators on 24D vectors
def P23_on_vector(v):
    v_new = np.zeros_like(v)
    v_new[0] = v[22]
    v_new[1:23] = v[0:22]
    v_new[23] = v[23]
    return v_new

def P11_on_vector(v):
    v_new = np.zeros_like(v)
    for j in range(23):
        v_new[j] = v[(12 * j) % 23]
    v_new[23] = v[23]
    return v_new

def H_L_on_vector(v):
    v_new = np.zeros_like(v)
    v_new[0] = v[0]
    v_new[23] = v[23]
    for j in range(1, 23):
        for inv in range(1, 23):
            if (j * inv) % 23 == 1:
                v_new[j] = v[(-inv) % 23]
                break
    return v_new

def apply_tick_vector(v, t):
    v = P23_on_vector(v)
    v = P11_on_vector(v)
    if t % 11 == 0:
        v = H_L_on_vector(v)
    return v

# Quaternion 24-cell vertices
quats = []
for i in range(4):
    for s in [1, -1]:
        q = [0, 0, 0, 0]
        q[i] = s
        quats.append(q)
# Half-integer vertices (even number of minus signs)
for bits in range(16):
    signs = [0.5 if ((bits >> i) & 1) == 0 else -0.5 for i in range(4)]
    quats.append(signs)
QUATERNIONS_24 = np.array(quats)

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

# 5-fold axis for Hopf projection
AXIS_5FOLD = np.array([0, 1, PHI])
AXIS_5FOLD = AXIS_5FOLD / np.linalg.norm(AXIS_5FOLD)
E1_S = np.array([1, 0, 0]) - np.dot(np.array([1, 0, 0]), AXIS_5FOLD) * AXIS_5FOLD
E1_S = E1_S / np.linalg.norm(E1_S)
E2_S = np.cross(AXIS_5FOLD, E1_S)
E2_S = E2_S / np.linalg.norm(E2_S)
P_GOLDEN = np.array([0, 1, PHI, 0]) / np.linalg.norm([0, 1, PHI, 0])

def full_projection_quaternion(v_24d):
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(QUATERNIONS_24))):
        q += v[0, i] * QUATERNIONS_24[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
    v3 = hopf(q, P_GOLDEN)
    norm3 = np.linalg.norm(v3)
    if norm3 > 1e-10:
        v3 = v3 / norm3
    v2 = np.array([np.dot(v3, E1_S), np.dot(v3, E2_S)])
    return v2

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color

# Compute 22-tick color sequences for all 24 deep holes
DH_COLOR_SEQUENCES = np.zeros((24, 22), dtype=int)
for dh_idx in range(24):
    h = deep_hole(dh_idx).copy()
    for t in range(22):
        v2 = full_projection_quaternion(h)
        theta = np.arctan2(v2[1], v2[0]) % (2 * np.pi)
        DH_COLOR_SEQUENCES[dh_idx, t] = angle_to_color(theta)
        h = apply_tick_vector(h, t)

DOMINANT_COLORS = np.array([np.argmax(np.bincount(DH_COLOR_SEQUENCES[dh], minlength=5)) for dh in range(24)])

# Color transition matrix
P_color_raw = np.zeros((5, 5))
for dh in range(24):
    seq = DH_COLOR_SEQUENCES[dh]
    for t in range(len(seq) - 1):
        P_color_raw[seq[t], seq[t+1]] += 1

P_color = P_color_raw / (P_color_raw.sum(axis=1, keepdims=True) + 1e-10)
P_color = (P_color + P_color.T) / 2

# Coupling matrix
K_color = np.zeros((5, 5))
for i in range(5):
    for j in range(5):
        if i == j:
            K_color[i, j] = 0.5
        else:
            diff = abs(A_COLOR[i] - A_COLOR[j])
            K_color[i, j] = np.exp(-diff**2 / (2 * 0.3**2)) * (1 + P_color[i, j])
K_color = (K_color + K_color.T) / 2

# Bulk color distribution over 46 ticks
color_bulk = np.zeros((46, 5))
for t in range(46):
    for dh in range(24):
        c = DH_COLOR_SEQUENCES[dh, t % 22]
        color_bulk[t, c] += A_COLOR[c]
color_bulk = color_bulk / color_bulk.sum(axis=1, keepdims=True)

print("Foundation data loaded:")
print(f"  Deep hole color sequences: {DH_COLOR_SEQUENCES.shape}")
print(f"  Dominant colors: {DOMINANT_COLORS}")
print(f"  Color transition matrix: {P_color.shape}")
print(f"  Bulk color distribution: {color_bulk.shape}")
print()

# =============================================================================
# TASK 1: DISCRETE QUANTUM WALK
# =============================================================================

print("=" * 78)
print("TASK 1: DISCRETE QUANTUM WALK")
print("=" * 78)

# Coin operator: 5×5 unitary from color transitions (polar decomposition)
U_color, s_color, Vh_color = np.linalg.svd(P_color)
C_coin = U_color @ Vh_color

# Verify unitarity
unitarity_error = np.max(np.abs(C_coin.conj().T @ C_coin - np.eye(5)))
print(f"Coin operator C: 5×5, unitarity error = {unitarity_error:.2e}")

# Shift operator: 24×24 permutation from Floquet tick 0
S_shift = np.zeros((24, 24))
for dh in range(24):
    h = deep_hole(dh).copy()
    h_new = apply_tick_vector(h, 0)
    min_dist = float('inf')
    closest = -1
    for i in range(24):
        dist = np.linalg.norm(h_new - deep_hole(i))
        if dist < min_dist:
            min_dist = dist
            closest = i
    S_shift[closest, dh] = 1.0

# Verify permutation
perm_check = np.allclose(S_shift.sum(axis=0), 1) and np.allclose(S_shift.sum(axis=1), 1)
print(f"Shift operator S: 24×24, permutation check = {perm_check}")

# Full walk operator
W_walk = np.kron(S_shift, C_coin)
print(f"Walk operator W: {W_walk.shape}")

# Effective Hamiltonian
H_eff = 1j * logm(W_walk)
herm_check = np.max(np.abs(H_eff - H_eff.conj().T))
print(f"Effective Hamiltonian H_eff: Hermitian check = {herm_check:.2e}")

# Initial state: uniform superposition over holes, Red color
psi0 = np.zeros(120, dtype=complex)
for h in range(24):
    psi0[h * 5 + 0] = 1.0 / np.sqrt(24)

# Evolve for 46 ticks
psi_t = np.zeros((46, 120), dtype=complex)
psi_t[0] = psi0
for t in range(1, 46):
    psi_t[t] = W_walk @ psi_t[t - 1]

# Periodicity check
period_error = np.linalg.norm(psi_t[45] - psi_t[0])
print(f"Periodicity: ||ψ(46) − ψ(0)|| = {period_error:.6f}")

# Discrete Euler-Lagrange residuals
del_residuals = np.zeros(46)
for t in range(1, 45):
    lhs = 1j * (psi_t[t + 1] - psi_t[t - 1]) / 2.0
    rhs = H_eff @ psi_t[t]
    del_residuals[t] = np.linalg.norm(lhs - rhs)

scale_walk = np.mean([np.linalg.norm(psi_t[t]) for t in range(46)])
R_walk_norm = del_residuals / scale_walk

print(f"
Quantum Walk Variational Test:")
print(f"  Raw max residual:      {np.max(del_residuals):.6f}")
print(f"  Normalized max residual: {np.max(R_walk_norm):.6f}  (threshold: 0.1)")
print(f"  Normalized mean residual: {np.mean(R_walk_norm):.6f}")
print(f"  VERDICT: {'PASS' if np.max(R_walk_norm) < 0.1 else 'FAIL'}")
print()

task1_df = pd.DataFrame({
    'Tick': range(46),
    'DEL_Residual_Raw': del_residuals,
    'DEL_Residual_Norm': R_walk_norm,
    'State_Norm': [np.linalg.norm(psi_t[t]) for t in range(46)]
})

# =============================================================================
# TASK 2: INFORMATION GEOMETRY
# =============================================================================

print("=" * 78)
print("TASK 2: INFORMATION GEOMETRY / FISHER METRIC")
print("=" * 78)

# Hellinger coordinates: θ_i(t) = 2√p_i(t)
theta_traj = np.zeros((46, 5))
for t in range(46):
    theta_traj[t] = 2 * np.sqrt(color_bulk[t] + 1e-10)

# Geodesic test: second derivative (acceleration) in θ-space
geo_residuals = np.zeros(46)
for t in range(1, 45):
    accel = theta_traj[t + 1] - 2 * theta_traj[t] + theta_traj[t - 1]
    geo_residuals[t] = np.linalg.norm(accel)

scale_theta = np.mean(np.abs(theta_traj))
R_geo_norm = geo_residuals / scale_theta

print(f"Fisher Metric Geodesic Test:")
print(f"  Raw max residual: {np.max(geo_residuals):.6f}")
print(f"  Norm max residual: {np.max(R_geo_norm):.6f}")
print(f"  Norm mean residual: {np.mean(R_geo_norm):.6f}")

# Fit harmonic potential to covariance dynamics
cov_traj = np.zeros((46, 5, 5))
for t in range(46):
    color_indicators = np.zeros((24, 5))
    for dh in range(24):
        c = DH_COLOR_SEQUENCES[dh, t % 22]
        color_indicators[dh, c] = 1.0
    cov_traj[t] = np.cov(color_indicators.T)

cov_flat = cov_traj.reshape(46, 25)
cov_accel = np.zeros(46)
for t in range(1, 45):
    accel = cov_flat[t + 1] - 2 * cov_flat[t] + cov_flat[t - 1]
    cov_accel[t] = np.linalg.norm(accel)

scale_cov = np.mean(np.abs(cov_flat))
R_cov_norm = cov_accel / scale_cov

best_k_cov, best_res_cov = 0, 1e10
for k in np.linspace(0.001, 1.0, 100):
    residuals = []
    for t in range(1, 45):
        accel = cov_flat[t + 1] - 2 * cov_flat[t] + cov_flat[t - 1]
        force = -k * (cov_flat[t] - np.mean(cov_flat, axis=0))
        residuals.append(np.linalg.norm(accel - force))
    mean_res = np.mean(residuals)
    if mean_res < best_res_cov:
        best_res_cov = mean_res
        best_k_cov = k

R_cov_force = np.zeros(46)
for t in range(1, 45):
    accel = cov_flat[t + 1] - 2 * cov_flat[t] + cov_flat[t - 1]
    force = -best_k_cov * (cov_flat[t] - np.mean(cov_flat, axis=0))
    R_cov_force[t] = np.linalg.norm(accel - force)

R_cov_force_norm = R_cov_force / scale_cov

print(f"
Covariance with harmonic potential (k={best_k_cov:.4f}):")
print(f"  Raw max residual: {np.max(R_cov_force):.6f}")
print(f"  Norm max residual: {np.max(R_cov_force_norm):.6f}")
print(f"  Norm mean residual: {np.mean(R_cov_force_norm):.6f}")
print(f"  VERDICT: {'PASS' if np.max(R_cov_force_norm) < 0.1 else 'FAIL'}")
print()

task2_df = pd.DataFrame({
    'Tick': range(46),
    'Fisher_Accel_Raw': geo_residuals,
    'Fisher_Accel_Norm': R_geo_norm,
    'Cov_Harmonic_Raw': R_cov_force,
    'Cov_Harmonic_Norm': R_cov_force_norm
})

# =============================================================================
# TASK 3: LINDBLADIAN DYNAMICS
# =============================================================================

print("=" * 78)
print("TASK 3: DISSIPATIVE LINDBLADIAN DYNAMICS")
print("=" * 78)

# Hamiltonian from color amplitudes and couplings
H_color = np.zeros((5, 5))
for i in range(5):
    for j in range(5):
        H_color[i, j] = A_COLOR[i] * K_color[i, j] * A_COLOR[j]
H_color = (H_color + H_color.T) / 2

# Dissipators on Red (0) and Blue (4) — high-CV = broken symmetries
L_diss = [np.diag([1.0 if k == i else 0.0 for k in range(5)]) for i in [0, 4]]

def lindblad_step(rho, H, L_list, gamma, dt=1.0):
    """One step of Lindblad evolution."""
    unitary = -1j * dt * (H @ rho - rho @ H)
    dissip = np.zeros((5, 5), dtype=complex)
    for L in L_list:
        L_dag = L.T
        L_rho_Ldag = L @ rho @ L_dag
        anticomm = 0.5 * (L_dag @ L @ rho + rho @ L_dag @ L)
        dissip += gamma * dt * (L_rho_Ldag - anticomm)
    rho_new = rho + unitary + dissip
    rho_new = (rho_new + rho_new.conj().T) / 2
    trace = np.trace(rho_new)
    return rho_new / trace if abs(trace) > 1e-10 else rho_new

# Fit γ by matching to observed distribution at t=22
rho0 = np.diag(color_bulk[0])
observed_final = color_bulk[22 % 22]

best_gamma, best_err = 0, 1e10
for gamma in np.linspace(0.01, 2.0, 200):
    rho = rho0.copy()
    for _ in range(22):
        rho = lindblad_step(rho, H_color, L_diss, gamma)
    err = np.linalg.norm(np.diag(rho).real - observed_final)
    if err < best_err:
        best_err = err
        best_gamma = gamma

print(f"Fitted γ: {best_gamma:.4f}")
print(f"Final state match error: {best_err:.6f}")

# Full evolution
rho_t = np.zeros((46, 5, 5), dtype=complex)
rho_t[0] = rho0
for t in range(1, 46):
    rho_t[t] = lindblad_step(rho_t[t - 1], H_color, L_diss, best_gamma)

# Lindbladian residuals
R_lind = np.zeros(46)
for t in range(1, 45):
    rho_obs = np.diag(color_bulk[t % 22])
    rho_next = np.diag(color_bulk[(t + 1) % 22])
    rho_prev = np.diag(color_bulk[(t - 1) % 22])
    drho = (rho_next - rho_prev) / 2.0

    H_rho = H_color @ rho_obs
    rho_H = rho_obs @ H_color
    unitary = -1j * (H_rho - rho_H)

    dissip = np.zeros((5, 5), dtype=complex)
    for L in L_diss:
        L_dag = L.T
        L_rho_Ldag = L @ rho_obs @ L_dag
        anticomm = 0.5 * (L_dag @ L @ rho_obs + rho_obs @ L_dag @ L)
        dissip += best_gamma * (L_rho_Ldag - anticomm)

    rhs = unitary + dissip
    R_lind[t] = np.linalg.norm(drho - rhs)

scale_lind = np.mean([np.linalg.norm(np.diag(color_bulk[t % 22])) for t in range(46)])
R_lind_norm = R_lind / scale_lind

print(f"
Lindbladian Residuals:")
print(f"  Raw max: {np.max(R_lind):.6f}")
print(f"  Norm max: {np.max(R_lind_norm):.6f}  (threshold: 0.1)")
print(f"  Norm mean: {np.mean(R_lind_norm):.6f}")
print(f"  VERDICT: {'PASS' if np.max(R_lind_norm) < 0.1 else 'FAIL'}")
print()

task3_df = pd.DataFrame({
    'Tick': range(46),
    'Lindblad_Residual_Raw': R_lind,
    'Lindblad_Residual_Norm': R_lind_norm,
    'Gamma_Fitted': [best_gamma] * 46
})

# =============================================================================
# TASK 5: SYNCHRONIZATION ANALYSIS
# =============================================================================

print("=" * 78)
print("TASK 5: SYNCHRONIZATION ANALYSIS")
print("=" * 78)

# Effective Lagrangian from quantum walk
L_eff = np.array([np.real(np.vdot(psi_t[t], H_eff @ psi_t[t])) for t in range(46)])

dL_dt = np.zeros(46)
for t in range(46):
    dL_dt[t] = (L_eff[(t + 1) % 46] - L_eff[(t - 1) % 46]) / 2.0

is_sync = [1 if t in SYNC_TICKS else 0 for t in range(46)]
extrema_type = []
for t in range(46):
    tm1, tp1 = (t - 1) % 46, (t + 1) % 46
    if L_eff[t] > L_eff[tm1] and L_eff[t] > L_eff[tp1]:
        extrema_type.append('MAX')
    elif L_eff[t] < L_eff[tm1] and L_eff[t] < L_eff[tp1]:
        extrema_type.append('MIN')
    elif dL_dt[t] * dL_dt[tm1] < 0:
        extrema_type.append('ZERO')
    else:
        extrema_type.append('NONE')

sync_at_extrema = sum(1 for t in range(46) if is_sync[t] == 1 and extrema_type[t] != 'NONE')
print(f"Sync ticks at extrema of L_eff: {sync_at_extrema}/9")
print(f"Sync tick details:")
for t in SYNC_TICKS:
    print(f"  Tick {t:2d}: L_eff = {L_eff[t]:8.4f}, dL/dt = {dL_dt[t]:8.4f}, type = {extrema_type[t]}")
print()

task5_df = pd.DataFrame({
    'Tick': range(46),
    'L_eff': L_eff,
    'dL_dt': dL_dt,
    'Is_Sync': is_sync,
    'Extrema_Type': extrema_type
})

# =============================================================================
# SAVE OUTPUTS
# =============================================================================

task1_df.to_csv('RC-206b_Task1_QuantumWalk.csv', index=False)
task2_df.to_csv('RC-206b_Task2_InformationGeometry.csv', index=False)
task3_df.to_csv('RC-206b_Task3_Lindbladian.csv', index=False)
task5_df.to_csv('RC-206b_Task5_SyncAnalysis.csv', index=False)

print("=" * 78)
print("RC-206b: ALL OUTPUTS SAVED")
print("=" * 78)
print("  RC-206b_Task1_QuantumWalk.csv")
print("  RC-206b_Task2_InformationGeometry.csv")
print("  RC-206b_Task3_Lindbladian.csv")
print("  RC-206b_Task5_SyncAnalysis.csv")
print()
print("Run complete. See RC-206b_Summary.txt for full interpretation.")
