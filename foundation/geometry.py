import numpy as np
from itertools import product

phi = (1 + np.sqrt(5)) / 2
golden_axis = np.array([0, 1, phi])
golden_axis = golden_axis / np.linalg.norm(golden_axis)

_quaternions_24 = None

def quaternions_24():
    global _quaternions_24
    if _quaternions_24 is not None:
        return _quaternions_24
    qs = []
    for i in range(4):
        for s in [1, -1]:
            q = [0, 0, 0, 0]
            q[i] = s
            qs.append(q)
    for signs in product([0.5, -0.5], repeat=4):
        qs.append(list(signs))
    _quaternions_24 = np.array(qs)
    return _quaternions_24

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

def hopf(q, p=None):
    if p is None:
        p = np.array([0, 1, 0, 0])
    r = quat_mul(quat_mul(q, p), quat_conj(q))
    return r[1:]

def full_projection_quaternion(v_24d):
    quats = quaternions_24()
    v = np.asarray(v_24d, dtype=float)
    if v.ndim == 1:
        v = v.reshape(1, -1)
    q = np.zeros(4)
    for i in range(min(24, len(quats))):
        q += v[0, i] * quats[i]
    norm = np.linalg.norm(q)
    if norm > 1e-10:
        q = q / norm
    p_golden = np.array([0, 1, phi, 0]) / np.linalg.norm([0, 1, phi, 0])
    v3 = hopf(q, p_golden)
    return v3

def project_to_3d(v_24d):
    return full_projection_quaternion(v_24d)

def angle_to_color(theta):
    theta_norm = theta % np.pi
    color = int(np.round((theta_norm / np.pi - 0.1) / 0.2)) % 5
    return color
