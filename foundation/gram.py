import numpy as np
from scipy.linalg import eigh

QR0 = {0, 1, 3, 4, 5, 9}

B_sym = np.zeros((12, 12), dtype=int)
for i in range(11):
    for j in range(11):
        if (i + j) % 11 in QR0:
            B_sym[i, j] = 1
B_sym[11, :] = 1
B_sym[:, 11] = 1
B_sym[11, 11] = 0

G_float = (B_sym @ B_sym.T).astype(float)

GRAM_LAMBDA_1 = 29 + 12 * np.sqrt(5)
GRAM_LAMBDA_12 = 29 - 12 * np.sqrt(5)

def gram_eigenvalues():
    eigvals, _ = eigh(G_float)
    return eigvals

def gram_ratio():
    return GRAM_LAMBDA_12 / GRAM_LAMBDA_1
