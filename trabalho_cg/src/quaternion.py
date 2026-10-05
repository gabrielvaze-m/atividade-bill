"""
PARTE 4 - Operações com quaternios unitários q = (w, x, y, z).
"""
import numpy as np


def identidade():
    return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)


def normalizar(q):
    n = np.linalg.norm(q)
    return q / n if n > 0 else identidade()


def de_eixo_angulo(eixo, angulo):
    """Constrói q = (cos(a/2), eixo * sin(a/2)) a partir de eixo e ângulo (rad)."""
    eixo = np.asarray(eixo, dtype=np.float64)
    n = np.linalg.norm(eixo)
    if n == 0:
        return identidade()
    eixo = eixo / n
    s = np.sin(angulo / 2.0)
    return normalizar(np.array([np.cos(angulo / 2.0), *(eixo * s)]))


def multiplicar(a, b):
    """Produto de Hamilton a * b."""
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    ], dtype=np.float64)


def para_matriz(q):
    """Converte quaternio unitário em matriz de rotação 4x4."""
    w, x, y, z = normalizar(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z),     2 * (x * z + w * y),     0],
        [2 * (x * y + w * z),     1 - 2 * (x * x + z * z), 2 * (y * z - w * x),     0],
        [2 * (x * z - w * y),     2 * (y * z + w * x),     1 - 2 * (x * x + y * y), 0],
        [0, 0, 0, 1],
    ], dtype=np.float64)
