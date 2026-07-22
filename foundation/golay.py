import numpy as np

g = np.array([1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1] + [0]*11, dtype=int)

def golay_code_matrix():
    G23 = np.zeros((12, 23), dtype=int)
    for i in range(12):
        for j in range(23):
            G23[i, j] = g[(j - i) % 23]
    G24 = np.zeros((12, 24), dtype=int)
    G24[:, :23] = G23
    G24[:, 23] = np.sum(G23, axis=1) % 2
    return G24

G24 = golay_code_matrix()

def cocode_weight_distribution():
    from itertools import combinations
    C = set()
    for r in range(12):
        for cols in combinations(range(12), r):
            mask = np.zeros(12, dtype=int)
            mask[list(cols)] = 1
            C.add(tuple((mask @ G24) % 2))
    weights = [sum(c) for c in C]
    dist = {w: weights.count(w) for w in sorted(set(weights))}
    return dist
