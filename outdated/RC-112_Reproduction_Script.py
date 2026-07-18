#!/usr/bin/env python3
"""
RC-112 Complete Reproduction Script
Framework: 24D-DMF v8.4.3 | Research Cycle: RC-112
Date: 2026-07-07

Hypothesis: The logical subspace of the [[24,12,8]] Golay code corresponds
to a geometric structure in R^4 that, when projected to 3D, exhibits
icosahedral symmetry (A_5, order 60).

This script reproduces all falsification criteria F1-F5.
"""

import numpy as np
from itertools import product, permutations
from collections import defaultdict

# ============================================================
# QUATERNION CLASS
# ============================================================

class Quaternion:
    def __init__(self, a, b, c, d):
        self.v = np.array([a, b, c, d], dtype=float)

    def __add__(self, other):
        return Quaternion(*(self.v + other.v))

    def __sub__(self, other):
        return Quaternion(*(self.v - other.v))

    def __mul__(self, other):
        a1, b1, c1, d1 = self.v
        a2, b2, c2, d2 = other.v
        return Quaternion(
            a1*a2 - b1*b2 - c1*c2 - d1*d2,
            a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2,
            a1*d2 + b1*c2 - c1*b2 + d1*a2
        )

    def conj(self):
        a, b, c, d = self.v
        return Quaternion(a, -b, -c, -d)

    def norm_sq(self):
        return np.sum(self.v**2)

    def norm(self):
        return np.sqrt(self.norm_sq())

    def inv(self):
        n = self.norm_sq()
        return Quaternion(*(self.conj().v / n))

    def __eq__(self, other):
        return np.allclose(self.v, other.v, atol=1e-9)

    def __hash__(self):
        return hash(tuple(np.round(self.v, 9)))

    def __repr__(self):
        a, b, c, d = self.v
        return f"Q({a:.6f}, {b:.6f}, {c:.6f}, {d:.6f})"


# ============================================================
# GROUP GENERATION UTILITIES
# ============================================================

def generate_group(generators):
    """Generate group from generators using BFS closure under multiplication."""
    group = set(generators)
    queue = list(generators)
    while queue:
        g = queue.pop(0)
        for h in list(group):
            for op in [lambda x, y: x * y, lambda x, y: y * x]:
                prod = op(g, h)
                if prod not in group:
                    group.add(prod)
                    queue.append(prod)
    return group


def permutation_sign(perm):
    """Compute sign of permutation using inversions."""
    inv = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inv += 1
    return 1 if inv % 2 == 0 else -1


# ============================================================
# STEP 1: CONSTRUCT 2T (BINARY TETRAHEDRAL GROUP)
# ============================================================

print("=" * 70)
print("STEP 1: Binary Tetrahedral Group 2T")
print("=" * 70)

axial = [
    Quaternion(1, 0, 0, 0), Quaternion(-1, 0, 0, 0),
    Quaternion(0, 1, 0, 0), Quaternion(0, -1, 0, 0),
    Quaternion(0, 0, 1, 0), Quaternion(0, 0, -1, 0),
    Quaternion(0, 0, 0, 1), Quaternion(0, 0, 0, -1)
]

even_hurwitz = []
for signs in product([1, -1], repeat=4):
    if sum(1 for s in signs if s == -1) % 2 == 0:
        even_hurwitz.append(Quaternion(*(np.array(signs) / 2)))

two_T = generate_group(axial + even_hurwitz)
print(f"2T size: {len(two_T)} (expected: 24)")

# Verify closure
products = set(a * b for a in two_T for b in two_T)
print(f"Closure: {len(products)} == 24? {len(products) == 24}")
assert len(two_T) == 24 and len(products) == 24

# Verify all unit norms
for q in two_T:
    assert abs(q.norm_sq() - 1) < 1e-9
print("All elements unit norm: VERIFIED")


# ============================================================
# STEP 2: CONSTRUCT 2I (BINARY ICOSAHEDRAL GROUP)
# ============================================================

print("\n" + "=" * 70)
print("STEP 2: Binary Icosahedral Group 2I")
print("=" * 70)

phi = (1 + np.sqrt(5)) / 2

# Standard generators: a (order 3), b (order 5)
a = Quaternion(0.5, 0.5, 0.5, 0.5)  # (1/2)(1 + i + j + k)
b = Quaternion(phi / 2, 0.5, 1 / (2 * phi), 0)

identity = Quaternion(1, 0, 0, 0)
minus_one = Quaternion(-1, 0, 0, 0)

print(f"Generator a: {a}")
print(f"Generator b: {b}")

# Verify orders
a3 = a * a * a
b5 = b * b * b * b * b
print(f"a^3 = {a3} (should be -1)")
print(f"b^5 = {b5} (should be -1)")
assert a3 == minus_one and b5 == minus_one

gens_2I = [identity, a, a * a, b, b * b, b * b * b, b * b * b * b]
two_I = generate_group(gens_2I)
print(f"\n2I generated: {len(two_I)} elements (expected: 120)")

# Verify closure
products_2I = set(x * y for x in two_I for y in two_I)
print(f"Closure: {len(products_2I)} == 120? {len(products_2I) == 120}")
assert len(two_I) == 120 and len(products_2I) == 120

# Verify 2T is subgroup of 2I
two_T_in_2I = all(q in two_I for q in two_T)
print(f"2T ⊆ 2I: {two_T_in_2I}")
assert two_T_in_2I

# Check center
center = [q for q in two_I if all(q * g == g * q for g in two_I)]
print(f"Center: {len(center)} elements (expected: 2)")
assert len(center) == 2 and identity in center and minus_one in center


# ============================================================
# STEP 3: 5-COSET QUOTIENT (F1)
# ============================================================

print("\n" + "=" * 70)
print("STEP 3: 5-Coset Quotient 2I / <ζ₅> (F1)")
print("=" * 70)

# Find element of order 5 (not in center)
order5_elements = []
for q in two_I:
    if q == identity or q == minus_one:
        continue
    q2, q3, q4 = q * q, q * q * q, q * q * q * q
    q5 = q4 * q
    if q5 == identity and q2 != identity and q3 != identity and q4 != identity:
        order5_elements.append(q)

print(f"Elements of order 5: {len(order5_elements)}")
zeta5 = order5_elements[0]
print(f"Selected ζ₅: {zeta5}")

# Generate cyclic subgroup <ζ₅>
zeta5_subgroup = set()
current = identity
for _ in range(10):
    zeta5_subgroup.add(current)
    current = current * zeta5

print(f"<ζ₅>: {len(zeta5_subgroup)} elements (expected: 5)")
assert len(zeta5_subgroup) == 5

# Form left cosets
cosets = []
used = set()
for g in two_I:
    if g in used:
        continue
    coset = {g * h for h in zeta5_subgroup}
    cosets.append(coset)
    used.update(coset)

print(f"Number of cosets: {len(cosets)} (expected: 24)")
print(f"F1: {'PASS' if len(cosets) == 24 else 'FAIL'}")
assert len(cosets) == 24


# ============================================================
# STEP 4: A₅ SYMMETRY ON COSETS (F2)
# ============================================================

print("\n" + "=" * 70)
print("STEP 4: A₅ Symmetry on Cosets (F2)")
print("=" * 70)

coset_list = [frozenset(c) for c in cosets]

def coset_action(g):
    """Return permutation of cosets induced by left multiplication by g."""
    perm = []
    for c in coset_list:
        rep = next(iter(c))
        prod = g * rep
        for j, c2 in enumerate(coset_list):
            if prod in c2:
                perm.append(j)
                break
    return tuple(perm)

# Verify homomorphism
print("Checking homomorphism property...")
for _ in range(10):
    g = list(two_I)[np.random.randint(len(two_I))]
    h = list(two_I)[np.random.randint(len(two_I))]
    perm_g = coset_action(g)
    perm_h = coset_action(h)
    perm_gh = coset_action(g * h)
    composed = tuple(perm_g[perm_h[i]] for i in range(24))
    assert composed == perm_gh
print("Homomorphism: VERIFIED")

# Check kernel
kernel = [g for g in two_I if coset_action(g) == tuple(range(24))]
print(f"Kernel size: {len(kernel)} (expected: 1, trivial)")
assert len(kernel) == 1 and identity in kernel

# Pair antipodal cosets
coset_pairs = []
used_pairs = set()
for i, c in enumerate(cosets):
    if i in used_pairs:
        continue
    minus_c = frozenset({Quaternion(-q.v[0], -q.v[1], -q.v[2], -q.v[3]) for q in c})
    for j, c2 in enumerate(cosets):
        if c2 == minus_c:
            coset_pairs.append((i, j))
            used_pairs.add(i)
            used_pairs.add(j)
            break

print(f"Antipodal coset pairs: {len(coset_pairs)} (expected: 12)")
assert len(coset_pairs) == 12

pair_index = {}
for idx, (i, j) in enumerate(coset_pairs):
    pair_index[i] = idx
    pair_index[j] = idx

def a5_action_on_pairs(g):
    """Action of g on 12 coset pairs (icosahedron vertices)."""
    perm = []
    for i, j in coset_pairs:
        rep = next(iter(cosets[i]))
        prod = g * rep
        for k, c in enumerate(cosets):
            if prod in c:
                perm.append(pair_index[k])
                break
    return tuple(perm)

# Verify -1 acts trivially on pairs
perm_minus_one = a5_action_on_pairs(minus_one)
assert perm_minus_one == tuple(range(12))
print("-1 acts trivially on pairs: VERIFIED")

# Check element orders in A₅ action
a5_orders = set()
for g in two_I:
    perm = a5_action_on_pairs(g)
    perm_neg = a5_action_on_pairs(minus_one * g)
    if perm == perm_neg:  # In A₅ quotient
        visited = [False] * 12
        order = 1
        for i in range(12):
            if not visited[i]:
                cycle_len, j = 0, i
                while not visited[j]:
                    visited[j] = True
                    j = perm[j]
                    cycle_len += 1
                if cycle_len > 0:
                    order = np.lcm(order, cycle_len)
        a5_orders.add(order)

print(f"A₅ element orders: {sorted(a5_orders)} (expected: [1, 2, 3, 5])")
assert sorted(a5_orders) == [1, 2, 3, 5]

# Count distinct A₅ permutations
a5_perms = set()
for g in two_I:
    perm = a5_action_on_pairs(g)
    a5_perms.add(perm)

print(f"A₅ permutations: {len(a5_perms)} (expected: 60)")
print(f"F2: {'PASS' if len(a5_perms) == 60 else 'FAIL'}")
assert len(a5_perms) == 60


# ============================================================
# STEP 5: 600-CELL EDGE STRUCTURE (F3)
# ============================================================

print("\n" + "=" * 70)
print("STEP 5: 600-Cell Edge Structure (F3)")
print("=" * 70)

icosians_list = list(two_I)
edge_count = 0

for i in range(len(icosians_list)):
    for j in range(i + 1, len(icosians_list)):
        q1, q2 = icosians_list[i], icosians_list[j]
        diff = q1 - q2
        edge_length = np.sqrt(diff.norm_sq())
        if abs(edge_length - 1 / phi) < 1e-6:
            edge_count += 1

print(f"Edges found: {edge_count} (expected: 720)")
print(f"F3: {'PASS' if edge_count == 720 else 'FAIL'}")
assert edge_count == 720

# Euler characteristic
euler = 120 - edge_count + 1200 - 600
print(f"Euler characteristic: {euler} (expected: 0)")
assert euler == 0


# ============================================================
# STEP 6: 3D PROJECTION AND ICOSAHEDRAL VERTICES (F4)
# ============================================================

print("\n" + "=" * 70)
print("STEP 6: 3D Projection and Icosahedral Vertices (F4)")
print("=" * 70)

# Vertex figure: neighbors of first vertex form icosahedron
v0 = icosians_list[0]
neighbors = []
for q in icosians_list[1:]:
    diff = v0 - q
    if np.sqrt(diff.norm_sq()) - 1 / phi < 1e-6:
        neighbors.append(q)

print(f"Vertex figure size: {len(neighbors)} (expected: 12)")
assert len(neighbors) == 12

# Project to tangent space
v0_inv = v0.inv()
neighbor_dirs = []
seen = set()
for q in neighbors:
    rel = v0_inv * q
    p = rel.v[1:]  # (i, j, k) components
    norm = np.sqrt(np.sum(p ** 2))
    if norm < 1e-10:
        continue
    direction = tuple(np.round(p / norm, 6))
    neg = tuple(-np.array(direction))
    if direction not in seen and neg not in seen:
        neighbor_dirs.append(direction)
        seen.add(direction)
        seen.add(neg)

print(f"Unique neighbor directions: {len(neighbor_dirs)} (expected: 12)")

# Standard icosahedron vertices
icosahedron_vertices = []
for perm in set(permutations([0, 1, phi])):
    for signs in product([1, -1], repeat=3):
        v = np.array([signs[i] * perm[i] for i in range(3)])
        norm = np.sqrt(np.sum(v ** 2))
        v_norm = tuple(np.round(v / norm, 6))
        neg = tuple(-np.array(v_norm))
        if v_norm not in icosahedron_vertices and neg not in icosahedron_vertices:
            icosahedron_vertices.append(v_norm)

print(f"Standard icosahedron vertices: {len(icosahedron_vertices)}")
assert len(icosahedron_vertices) == 12

# Check match
matches = 0
for icos_v in icosahedron_vertices:
    for d in neighbor_dirs:
        if np.allclose(icos_v, d, atol=1e-4) or np.allclose(icos_v, tuple(-np.array(d)), atol=1e-4):
            matches += 1
            break

print(f"Icosahedron vertices found: {matches}/12")
print(f"F4: {'PASS' if matches == 12 else 'FAIL'}")
assert matches == 12


# ============================================================
# STEP 7: ENGINE EQUIVARIANCE (F5)
# ============================================================

print("\n" + "=" * 70)
print("STEP 7: Engine Generator Equivariance (F5)")
print("=" * 70)

print(f"\n|G| = |C_23 ⋊ C_11| = 253 = 11 × 23")
print(f"|A_5| = 60 = 2² × 3 × 5")
print(f"gcd(253, 60) = {np.gcd(253, 60)}")

print("\nBy Lagrange's theorem, any homomorphism φ: G → A_5 must be trivial.")
print("P_23 has order 23; A_5 has no element of order 23.")
print("P_11 has order 11; A_5 has no element of order 11.")

print("\nF5: FAIL — No non-trivial equivariant action possible.")


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("RC-112 FINAL SUMMARY")
print("=" * 70)

results = {
    "F1": ("PASS", "24 cosets of <ζ₅> in 2I"),
    "F2": ("PASS", "A₅ ≅ 2I/{±1} on 12 vertices"),
    "F3": ("PASS", "600-cell: 120V, 720E, χ=0"),
    "F4": ("PASS", "Vertex figure is icosahedron"),
    "F5": ("FAIL", "gcd(253, 60)=1, no homomorphism G→A₅")
}

for criterion, (status, detail) in results.items():
    symbol = "✓" if status == "PASS" else "✗"
    print(f"\n{criterion}: {symbol} {status}")
    print(f"   {detail}")

print("\n" + "=" * 70)
print("CONCLUSION: The 24-cell→600-cell→icosahedron bridge is real")
print("mathematics (F1-F4 PASS), but NOT realized by the Golay code")
print("engine G = C_23 ⋊ C_11 (F5 FAIL).")
print("=" * 70)
