"""
PARTE 4 - Trackball virtual: mapeia o mouse (2D) para uma hemisfério 3D e
acumula a rotação com quaternios (sem gimbal lock).
"""
import numpy as np
import quaternion as quat


class Trackball:
    def __init__(self, orientacao_inicial=None):
        self._inicial = quat.identidade() if orientacao_inicial is None \
            else quat.normalizar(orientacao_inicial)
        self.orientacao = self._inicial.copy()
        self._vetor_anterior = None

    # ---------- mapeamento 2D -> hemisfério 3D ----------
    @staticmethod
    def mapear_para_hemisferio(px, py, largura, altura):
        """(x, y) em pixels -> vetor unitário (x, y, z) na hemisfério z >= 0."""
        escala = float(max(1, min(largura, altura)))
        x = (2.0 * px - largura) / escala
        y = (altura - 2.0 * py) / escala
        d2 = x * x + y * y
        if d2 <= 1.0:
            z = np.sqrt(1.0 - d2)        # dentro da esfera
        else:
            n = np.sqrt(d2)              # fora: projeta na borda (z = 0)
            x, y, z = x / n, y / n, 0.0
        return np.array([x, y, z], dtype=np.float64)

    # ---------- eventos do mouse ----------
    def iniciar(self, px, py, largura, altura):
        self._vetor_anterior = self.mapear_para_hemisferio(px, py, largura, altura)

    def finalizar(self):
        self._vetor_anterior = None

    @property
    def arrastando(self):
        return self._vetor_anterior is not None

    def arrastar(self, px, py, largura, altura):
        if self._vetor_anterior is None:
            return
        v1 = self._vetor_anterior
        v2 = self.mapear_para_hemisferio(px, py, largura, altura)

        eixo = np.cross(v1, v2)                       # eixo de rotação
        angulo = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))  # ângulo
        if np.linalg.norm(eixo) < 1e-9 or angulo < 1e-9:
            return

        q_novo = quat.de_eixo_angulo(eixo, angulo)
        # Acumula: q_total = q_novo * q_atual
        self.orientacao = quat.normalizar(quat.multiplicar(q_novo, self.orientacao))
        self._vetor_anterior = v2

    def resetar(self):
        self.orientacao = self._inicial.copy()

    def matriz(self):
        """Matriz de rotação 4x4 do quaternio acumulado."""
        return quat.para_matriz(self.orientacao)
