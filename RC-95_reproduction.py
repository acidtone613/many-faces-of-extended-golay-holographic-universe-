#!/usr/bin/env python3
"""
RC-95: Turyn Z2 as Isospin Breaking — Full Reproduction Script
Framework: 24D-DMF v8.3.5
Date: 2026-07-05

This script tests whether the Z2 in PGL(2,7) that interchanges the two
Turyn faces C ↔ D is a Golay automorphism (in M24).

Expected output: R_24 preserves Turyn code: False
                 All block permutations: False
                 Verdict: REJECTED
"""

import numpy as np

# ============================================================
# STEP 1: Build the two [8,4,4] extended QR codes C and D
# ============================================================

# Generator polynomials for cyclic [7,4,3] codes over F2
g_Q = np.array([1, 0, 1, 1])   # x^3 + x + 1 (QR code)
g_N = np.array([1, 1, 0, 1])   # x^3 + x^2 + 1 (NQR code)

def build_cyclic_code(g, n):
    """Build cyclic code from generator polynomial"""
    k = n - len(g) + 1
    G = np.zeros((k, n), dtype=int)
    for i in range(k):
        G[i, i:i+len(g)] = g
    return G

def extend_code(G):
    """Extend code by adding overall parity bit"""
    n = G.shape[1]
    parity = np.sum(G, axis=1) % 2
    return np.hstack([G, parity.reshape(-1, 1)])

C = extend_code(build_cyclic_code(g_Q, 7))  # [8,4,4] QR
D = extend_code(build_cyclic_code(g_N, 7))  # [8,4,4] NQR

print("=" * 60)
print("STEP 1: Codes C and D constructed")
print(f"C shape: {C.shape}, D shape: {D.shape}")

# Verify self-duality
assert np.all((C @ C.T) % 2 == 0), "C not self-dual"
assert np.all((D @ D.T) % 2 == 0), "D not self-dual"
print("Self-duality: VERIFIED")

# Verify weight distributions
for name, code in [("C", C), ("D", D)]:
    k = code.shape[0]
    weights = {}
    for bits in range(2**k):
        coeffs = np.array([(bits >> i) & 1 for i in range(k)])
        cw = (coeffs @ code) % 2
        w = int(np.sum(cw))
        weights[w] = weights.get(w, 0) + 1
    print(f"{name} weight distribution: {dict(sorted(weights.items()))}")

# ============================================================
# STEP 2: PSL(2,7) generators and Z2
# ============================================================

def mobius_S(x):
    """x -> -1/x mod 7, with infinity handling"""
    if x == 7: return 0
    elif x == 0: return 7
    else: return (-pow(x, -1, 7)) % 7

def mobius_T(x):
    """x -> x+1 mod 7, infinity fixed"""
    return 7 if x == 7 else (x + 1) % 7

def mobius_reflection(x):
    """x -> -x mod 7, the Z2 element in PGL(2,7) \ PSL(2,7)"""
    return 7 if x == 7 else (-x) % 7

S_perm = [mobius_S(x) for x in range(8)]
T_perm = [mobius_T(x) for x in range(8)]
R_perm = [mobius_reflection(x) for x in range(8)]

print("
" + "=" * 60)
print("STEP 2: Permutations computed")
print(f"S (order 2): {S_perm}")
print(f"T (order 7): {T_perm}")
print(f"R (order 2): {R_perm}")

# Verify PSL(2,7) preserves C and D
def is_code_preserved(code, perm):
    """Check if permutation preserves code as a set"""
    k = code.shape[0]
    codewords = {tuple((np.array([(bits >> i) & 1 for i in range(k)]) @ code) % 2) 
                 for bits in range(2**k)}
    permuted = {tuple(cw[perm[i]] for i in range(len(cw))) for cw in codewords}
    return codewords == permuted

assert is_code_preserved(C, S_perm), "S does not preserve C"
assert is_code_preserved(C, T_perm), "T does not preserve C"
assert is_code_preserved(D, S_perm), "S does not preserve D"
assert is_code_preserved(D, T_perm), "T does not preserve D"
print("PSL(2,7) preserves C and D: VERIFIED")

# Verify R interchanges C and D
def permute_code_set(code, perm):
    k = code.shape[0]
    codewords = [tuple((np.array([(bits >> i) & 1 for i in range(k)]) @ code) % 2) 
                 for bits in range(2**k)]
    return {tuple(cw[perm[i]] for i in range(len(cw))) for cw in codewords}

C_set = permute_code_set(C, list(range(8)))
D_set = permute_code_set(D, list(range(8)))
R_C_set = permute_code_set(C, R_perm)
R_D_set = permute_code_set(D, R_perm)

assert R_C_set == D_set, "R does not map C to D"
assert R_D_set == C_set, "R does not map D to C"
print("R interchanges C and D: VERIFIED")

# ============================================================
# STEP 3: Build Turyn construction
# ============================================================

C_words = [(np.array([(bits >> i) & 1 for i in range(4)]) @ C) % 2 
           for bits in range(2**4)]
D_words = [(np.array([(bits >> i) & 1 for i in range(4)]) @ D) % 2 
           for bits in range(2**4)]

print("
" + "=" * 60)
print("STEP 3: Building Turyn construction")
print(f"C has {len(C_words)} codewords, D has {len(D_words)} codewords")

turyn_codewords = []
for c in C_words:
    for d1 in D_words:
        for d2 in D_words:
            for offset in [0, 1]:
                d3 = (d1 + d2 + offset) % 2
                if any(np.array_equal(d3, dw) for dw in D_words):
                    codeword = np.concatenate([c + d1, c + d2, c + d3]) % 2
                    turyn_codewords.append(tuple(codeword))

turyn_set = set(turyn_codewords)
print(f"Turyn construction: {len(turyn_set)} codewords")

# Verify this is the Golay code
weights = {}
for cw in turyn_set:
    weights[sum(cw)] = weights.get(sum(cw), 0) + 1

print(f"Weight distribution: {dict(sorted(weights.items()))}")
assert weights == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1},     f"Not Golay code: {weights}"
print("Turyn construction = Golay code: VERIFIED")

# ============================================================
# STEP 4: Test if Z2 preserves the Turyn code
# ============================================================

print("
" + "=" * 60)
print("STEP 4: Testing Z2 preservation")

R_24 = list(R_perm) + [p + 8 for p in R_perm] + [p + 16 for p in R_perm]

def apply_perm(cw, perm):
    return tuple(cw[perm[i]] for i in range(len(cw)))

turyn_permuted = {apply_perm(cw, R_24) for cw in turyn_set}

PRESERVES = (turyn_set == turyn_permuted)
print(f"R_24 preserves Turyn code: {PRESERVES}")

# Test with all block permutations
block_perms = [
    [0, 1, 2], [1, 2, 0], [2, 0, 1],
    [0, 2, 1], [2, 1, 0], [1, 0, 2]
]

def apply_block_perm_and_R(cw, bp):
    blocks = [list(cw[i*8:(i+1)*8]) for i in range(3)]
    permuted = [blocks[bp[i]] for i in range(3)]
    result = []
    for block in permuted:
        result.extend([block[R_perm[i]] for i in range(8)])
    return tuple(result)

print("
Testing block permutations combined with R:")
for bp in block_perms:
    permuted = {apply_block_perm_and_R(cw, bp) for cw in turyn_set}
    match = (turyn_set == permuted)
    print(f"  Block perm {bp}: {match}")

# ============================================================
# VERDICT
# ============================================================

print("
" + "=" * 60)
print("RC-95 VERDICT")
print("=" * 60)
if not PRESERVES:
    print("Falsification Criterion 1 TRIGGERED")
    print("The Z2 in PGL(2,7) \ PSL(2,7) is NOT in M24.")
    print("It does not preserve the Turyn construction of the Golay code.")
    print("
STATUS: REJECTED")
else:
    print("Unexpected: Z2 preserves code. Further analysis needed.")
print("=" * 60)
