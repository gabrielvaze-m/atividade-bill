"""
PARTE 1 e 3 - Modelo geométrico (pirâmide de base quadrada) e vetores normais.
"""
import numpy as np
from OpenGL.GL import glBegin, glEnd, glNormal3fv, glVertex3fv, GL_TRIANGLES


class Piramide:
    """Pirâmide de base quadrada definida por lista de vértices e faces."""

    def __init__(self):
        self.vertices = np.array([
            [-1.0, -0.75, -1.0],   # 0 base
            [1.0, -0.75, -1.0],    # 1 base
            [1.0, -0.75, 1.0],     # 2 base
            [-1.0, -0.75, 1.0],    # 3 base
            [0.0, 1.0, 0.0],       # 4 ápice
        ], dtype=np.float32)

        # Cada face é um triângulo (índices dos vértices) em ordem anti-horária
        # vista de fora do objeto (a normal aponta para fora).
        self.faces = [
            (3, 2, 4),  # frente  (+z)
            (2, 1, 4),  # direita (+x)
            (1, 0, 4),  # trás    (-z)
            (0, 3, 4),  # esquerda(-x)
            (0, 1, 2),  # base (triângulo 1)
            (0, 2, 3),  # base (triângulo 2)
        ]
        self.normais = [self.calcular_normal(f) for f in self.faces]

    def calcular_normal(self, face):
        """N = (V1 - V0) x (V2 - V0), normalizado para |N| = 1."""
        v0, v1, v2 = (self.vertices[i] for i in face)
        n = np.cross(v1 - v0, v2 - v0)
        norma = np.linalg.norm(n)
        if norma == 0:
            raise ValueError("Face degenerada: normal nula.")
        return (n / norma).astype(np.float32)

    def desenhar(self):
        """Renderiza a malha com GL_TRIANGLES, associando a normal a cada face."""
        glBegin(GL_TRIANGLES)
        for face, normal in zip(self.faces, self.normais):
            glNormal3fv(normal)
            for i in face:
                glVertex3fv(self.vertices[i])
        glEnd()
