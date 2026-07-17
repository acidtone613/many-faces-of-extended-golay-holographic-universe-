#!/usr/bin/env python3
# RC-143b: The Quantum Clock
# Framework: 24D-DMF v8.4.3
# Date: 2026-07-09

import numpy as np
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")
np.set_printoptions(precision=6, suppress=True)

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

def nearest_deep_hole(v):
    best_dist = float("inf")
    best_s = -1
    for s in range(24):
        h = deep_hole(s)
        dist = np.linalg.norm(v - h)
        if dist < best_dist:
            best_dist = dist
            best_s = s
    return best_s, best_dist

def decompose_cycles(perm, elements):
    visited = set()
    cycles = []
    for s in elements:
        if s in visited:
            continue
        cycle = []
        current = s
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = perm[current]
        cycles.append(cycle)
    return cycles

def U_phase_22_23(v, theta):
    v_new = v.copy()
    v22, v23 = v[22], v[23]
    v_new[22] = np.cos(theta) * v22 - np.sin(theta) * v23
    v_new[23] = np.sin(theta) * v22 + np.cos(theta) * v23
    return v_new

def inverse_tick_vector(v, t):
    if t % 11 == 0:
        v = H_L_on_vector(v)
    v_new = np.zeros_like(v)
    for j in range(23):
        v_new[(inv2 * j) % 23] = v[j]
    v_new[23] = v[23]
    v = v_new
    v_new = np.zeros_like(v)
    v_new[22] = v[0]
    v_new[0:22] = v[1:23]
    v_new[23] = v[23]
    return v_new

B_perm = {}
for s in range(24):
    v = deep_hole(s).copy()
    for t in range(11):
        v = apply_tick_vector(v, t)
    s_after, dist = nearest_deep_hole(v)
    B_perm[s] = s_after
cycles_B = decompose_cycles(B_perm, list(range(24)))
B_cycle_of = {}
for i, c in enumerate(cycles_B):
    for s in c:
        B_cycle_of[s] = i

print("=" * 78)
print("RC-143b: THE QUANTUM CLOCK")
print("=" * 78)

print("[STEP 1] Constructing superposition state...")
superposition = np.zeros(24)
for i in range(24):
    superposition += deep_hole(i)
norm = np.linalg.norm(superposition)
superposition = superposition / norm
print(f"  Norm: {norm:.6f}")
print(f"  Normalized: {np.linalg.norm(superposition):.10f}")
h1_pass = abs(np.linalg.norm(superposition) - 1.0) < 1e-6
print(f"  H1 (Normalized): {'PASS' if h1_pass else 'FAIL'}")

def path_A(k, psi):
    for t in range(k):
        psi = apply_tick_vector(psi, t)
    return psi

def path_B(k, psi, theta, phase_tick):
    for t in range(k):
        if t == phase_tick:
            psi = U_phase_22_23(psi, theta)
        psi = apply_tick_vector(psi, t)
    return psi

def inverse_path(k, psi):
    for t in range(k-1, -1, -1):
        psi = inverse_tick_vector(psi, t)
    return psi

def interference(theta, k, phase_tick):
    psi_A = path_A(k, superposition)
    psi_B = path_B(k, superposition, theta, phase_tick)
    psi_A_inv = inverse_path(k, psi_A)
    psi_B_inv = inverse_path(k, psi_B)
    overlap = np.dot(psi_A_inv, psi_B_inv)
    return np.abs(overlap)**2

k_test = 12
psi_A = path_A(k_test, superposition)
psi_A_inv = inverse_path(k_test, psi_A)
print(f"[STEP 2] Path A + inverse return fidelity: {np.dot(superposition, psi_A_inv):.10f}")
print(f"  Exact return: {np.allclose(superposition, psi_A_inv)}")

print("[STEP 3] H2 - Coherent phase rotation...")
theta_test = np.pi / 4
psi_rot = U_phase_22_23(superposition, theta_test)
phi_before = np.arctan2(superposition[23], superposition[22])
phi_after = np.arctan2(psi_rot[23], psi_rot[22])
phase_shift = phi_after - phi_before
while phase_shift > np.pi: phase_shift -= 2*np.pi
while phase_shift < -np.pi: phase_shift += 2*np.pi
print(f"  Phase shift: {phase_shift:.6f} rad (expected: {theta_test:.6f})")
h2_pass = abs(phase_shift - theta_test) < 1e-6
print(f"  H2 (Coherent): {'PASS' if h2_pass else 'FAIL'}")

print("[STEP 4] Interference pattern...")
k = 12
phase_tick = 6
theta_values = np.array([0, np.pi/6, np.pi/3, np.pi/2, 2*np.pi/3, 5*np.pi/6, np.pi])
I_values = np.array([interference(theta, k, phase_tick) for theta in theta_values])
print(f"  k={k}, phase_tick={phase_tick}")
for t, i in zip(theta_values, I_values):
    print(f"    theta={t:.4f} rad ({np.degrees(t):.1f} deg): I={i:.10f}")

def cos_model(theta, A, B):
    return A + B * np.cos(theta)
popt, pcov = curve_fit(cos_model, theta_values, I_values, p0=[0.5, 0.5])
A_fit, B_fit = popt
perr = np.sqrt(np.diag(pcov))
print(f"  Fit: A={A_fit:.6f}+-{perr[0]:.6f}, B={B_fit:.6f}+-{perr[1]:.6f}")
h3_pass = B_fit > 0.1
print(f"  H3 (Interference B>0.1): {'PASS' if h3_pass else 'FAIL'} (B={B_fit:.6f})")

print("[STEP 5] Collapse to basis state...")
psi = superposition.copy()
exact_collapse = False
collapse_tick = -1
for t in range(100):
    s, dist = nearest_deep_hole(psi)
    if dist < 1e-10:
        exact_collapse = True
        collapse_tick = t
        break
    psi = apply_tick_vector(psi, t)
print(f"  Exact collapse in 100 ticks: {exact_collapse}")
if exact_collapse:
    print(f"  At tick: {collapse_tick}")

psi = superposition.copy()
for t in range(11):
    psi = apply_tick_vector(psi, t)
print(f"  11-tick block fidelity: {np.dot(psi/np.linalg.norm(psi), superposition):.10f}")
print(f"  Exact return: {np.allclose(psi, superposition)}")
h4_pass = exact_collapse
print(f"  H4 (Collapse): {'PASS' if h4_pass else 'FAIL'}")

print("[STEP 6] Commutator analysis...")
psi_test = superposition.copy()
psi_AB = apply_tick_vector(U_phase_22_23(psi_test, theta_test), 0)
psi_BA = U_phase_22_23(apply_tick_vector(psi_test, 0), theta_test)
comm_fid = np.dot(psi_AB, psi_BA)
print(f"  [F, U_theta] fidelity: {comm_fid:.10f}")
print(f"  Commute: {abs(comm_fid - 1.0) < 1e-10}")

print("=" * 78)
print("FINAL VERDICT")
print("=" * 78)
c1_pass = h1_pass
c2_pass = h2_pass
c3_pass = h3_pass
c4_pass = h4_pass
print(f"C1 (Normalized): {'PASS' if c1_pass else 'FAIL'}")
print(f"C2 (Coherent):   {'PASS' if c2_pass else 'FAIL'}")
print(f"C3 (Interference):{'PASS' if c3_pass else 'FAIL'} (B={B_fit:.6f})")
print(f"C4 (Collapse):   {'PASS' if c4_pass else 'FAIL'}")

all_pass = c1_pass and c2_pass and c3_pass and c4_pass
print("=" * 78)
if all_pass:
    print("VERDICT: QUANTUM")
elif c1_pass and c2_pass and c3_pass:
    print("VERDICT: CLASSICAL ANALOG")
else:
    print("VERDICT: CLASSICAL")
print("=" * 78)
print("RC-143b EXECUTION COMPLETE")
