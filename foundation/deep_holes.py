import numpy as np

def deep_hole(i):
    h = np.ones(24) * 0.5
    h[i] = -0.5
    return h

orbit_classes = {
    'A': [1, 2, 6, 8, 14, 17, 19, 20],
    'B': [0, 4, 7, 10, 11, 16, 22],
    'C': [3, 9, 12, 13, 15, 18],
    'D': [5, 21],
    'E': [23]
}

class_map = {}
for label, indices in orbit_classes.items():
    for i in indices:
        class_map[i] = label

def compute_deep_hole_orbit():
    from .floquet import apply_tick_vector
    visited = []
    current = deep_hole(0).copy()
    for t in range(100):
        visited.append(current.copy())
        current = apply_tick_vector(current, t)
    return np.array(visited)

def compute_wavelength(seq):
    if len(seq) < 2:
        return 1.0
    changes = 1 + sum(1 for i in range(1, len(seq)) if seq[i] != seq[i-1])
    return len(seq) / changes
