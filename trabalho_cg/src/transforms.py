"""
PARTE 2 - Transformações geométricas em coordenadas homogêneas (4x4).

Convenção: vetores coluna, matrizes no formato "linha x coluna" do NumPy.
Para enviar ao OpenGL (column-major) usamos a transposta (ver `para_opengl`).
"""
import numpy as np


def translacao(tx, ty, tz):
    """T(tx, ty, tz)"""
    m = np.identity(4, dtype=np.float64)
    m[0, 3], m[1, 3], m[2, 3] = tx, ty, tz
    return m


def escala(sx, sy, sz):
    """S(sx, sy, sz)"""
    return np.diag([sx, sy, sz, 1.0]).astype(np.float64)


def rotacao_x(theta):
    """Rx(theta) - theta em radianos."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0, 0],
                     [0, c, -s, 0],
                     [0, s, c, 0],
                     [0, 0, 0, 1]], dtype=np.float64)


def rotacao_y(theta):
    """Ry(theta) - theta em radianos."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, 0, s, 0],
                     [0, 1, 0, 0],
                     [-s, 0, c, 0],
                     [0, 0, 0, 1]], dtype=np.float64)


def rotacao_z(theta):
    """Rz(theta) - theta em radianos."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0, 0],
                     [s, c, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]], dtype=np.float64)


def compor_modelo(T, R, S):
    """
    Composição M = T · R · S.
    Com vetores coluna, o ponto sofre primeiro a ESCALA, depois a ROTAÇÃO e
    por fim a TRANSLAÇÃO. Assim o objeto gira e escala em torno da própria
    origem (sem deslocamentos indesejados).
    """
    return T @ R @ S


def _normalizar(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def look_at(olho, alvo, cima):
    """Matriz de Visão (equivalente ao gluLookAt): Mundo -> Câmera."""
    olho = np.asarray(olho, dtype=np.float64)
    alvo = np.asarray(alvo, dtype=np.float64)
    cima = np.asarray(cima, dtype=np.float64)

    f = _normalizar(alvo - olho)        # direção para frente
    s = _normalizar(np.cross(f, cima))  # direita
    u = np.cross(s, f)                  # cima real

    m = np.identity(4, dtype=np.float64)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -np.dot(s, olho)
    m[1, 3] = -np.dot(u, olho)
    m[2, 3] = np.dot(f, olho)
    return m


def frustum(esq, dir_, baixo, topo, perto, longe):
    """Matriz de projeção em perspectiva (equivalente ao glFrustum)."""
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = 2.0 * perto / (dir_ - esq)
    m[0, 2] = (dir_ + esq) / (dir_ - esq)
    m[1, 1] = 2.0 * perto / (topo - baixo)
    m[1, 2] = (topo + baixo) / (topo - baixo)
    m[2, 2] = -(longe + perto) / (longe - perto)
    m[2, 3] = -2.0 * longe * perto / (longe - perto)
    m[3, 2] = -1.0
    return m


def perspectiva(fov_graus, aspecto, perto, longe):
    """Projeção em perspectiva (equivalente ao gluPerspective)."""
    topo = perto * np.tan(np.radians(fov_graus) / 2.0)
    direita = topo * aspecto
    return frustum(-direita, direita, -topo, topo, perto, longe)


def para_opengl(m):
    """Converte matriz NumPy 4x4 para o formato column-major do OpenGL."""
    return np.ascontiguousarray(m.T, dtype=np.float32)
