"""
Aplicação interativa 3D - Computação Gráfica e Visão Computacional
Python 3 + PyOpenGL + GLFW + OpenCV + NumPy

Execução (na raiz do projeto):  python src/main.py
"""
import sys
import numpy as np
import glfw


from OpenGL.GL import (
    glClear, glClearColor, glEnable, glViewport, glMatrixMode, glLoadMatrixf,
    glColor3f, glDisable, glPointSize, glBegin, glEnd, glVertex3fv,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_LESS, glDepthFunc,
    GL_PROJECTION, GL_MODELVIEW, GL_LIGHTING, GL_POINTS, GL_CULL_FACE,
)

import transforms as tf
import lighting
import color_utils
from geometry import Piramide
from trackball import Trackball
import quaternion as quat

LARGURA, ALTURA = 900, 700


class App:
    def __init__(self):
        self.piramide = Piramide()
        inicial = quat.multiplicar(
            quat.de_eixo_angulo((0, 1, 0), np.radians(30)),
            quat.de_eixo_angulo((1, 0, 0), np.radians(-25)),
        )
        self.trackball = Trackball(inicial)

        self.posicao = np.array([0.0, 0.0, 0.0])
        self.escala = 1.0
        self.cor = [0.85, 0.35, 0.20]          # RGB
        self.luz_ligada = True
        self.suave = False
        self.indice_faixa = -1
        self.window = None

    # ------------------------------------------------------------------
    def iniciar_janela(self):
        if not glfw.init():
            raise RuntimeError("Falha ao inicializar o GLFW.")
        self.window = glfw.create_window(LARGURA, ALTURA, "Piramide 3D - Trackball", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Falha ao criar a janela / contexto OpenGL.")
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        glfw.set_mouse_button_callback(self.window, self.cb_mouse_botao)
        glfw.set_cursor_pos_callback(self.window, self.cb_mouse_move)
        glfw.set_key_callback(self.window, self.cb_teclado)

        # Teste de profundidade (superfícies 3D corretas)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_CULL_FACE)               # descarta faces de trás
        glClearColor(0.08, 0.09, 0.12, 1.0)
        lighting.configurar_iluminacao()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def cb_mouse_botao(self, window, botao, acao, mods):
        if botao != glfw.MOUSE_BUTTON_LEFT:
            return
        if acao == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            w, h = glfw.get_window_size(window)
            self.trackball.iniciar(x, y, w, h)
        elif acao == glfw.RELEASE:
            self.trackball.finalizar()

    def cb_mouse_move(self, window, x, y):
        if self.trackball.arrastando:
            w, h = glfw.get_window_size(window)
            self.trackball.arrastar(x, y, w, h)

    def cb_teclado(self, window, tecla, scancode, acao, mods):
        if acao != glfw.PRESS:
            return
        shift = bool(mods & glfw.MOD_SHIFT)
        passo = -0.1 if shift else 0.1

        if tecla == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif tecla in (glfw.KEY_1, glfw.KEY_2, glfw.KEY_3):
            canal = {glfw.KEY_1: 0, glfw.KEY_2: 1, glfw.KEY_3: 2}[tecla]
            self.cor[canal] = float(np.clip(self.cor[canal] + passo, 0.0, 1.0))
            h, s, v = color_utils.rgb_para_hsv(self.cor)
            print(f"RGB={tuple(round(c, 2) for c in self.cor)} -> "
                  f"HSV=({h:.0f}°, {s:.2f}, {v:.2f})")
        elif tecla == glfw.KEY_H:
            self.indice_faixa = (self.indice_faixa + 1) % len(color_utils.FAIXAS_HSV)
            nome, cor = color_utils.gerar_mascara_hsv(self.indice_faixa)
            self.cor = list(cor)
            print(f"Máscara HSV OpenCV: {nome} -> RGB={tuple(round(c, 2) for c in cor)} "
                  f"(imagem salva em output/mascara_hsv.png)")
        elif tecla == glfw.KEY_L:
            self.luz_ligada = not self.luz_ligada
            lighting.ligar_luz(self.luz_ligada)
        elif tecla == glfw.KEY_F:
            self.suave = not self.suave
            lighting.usar_suave(self.suave)
        elif tecla == glfw.KEY_SPACE:
            self.trackball.resetar()
            self.posicao[:] = 0.0
            self.escala = 1.0

    def processar_teclas_continuas(self, dt):
        v = 2.0 * dt
        g = lambda k: glfw.get_key(self.window, k) == glfw.PRESS
        if g(glfw.KEY_A): self.posicao[0] -= v
        if g(glfw.KEY_D): self.posicao[0] += v
        if g(glfw.KEY_W): self.posicao[1] += v
        if g(glfw.KEY_S): self.posicao[1] -= v
        if g(glfw.KEY_Q): self.posicao[2] -= v
        if g(glfw.KEY_E): self.posicao[2] += v
        if g(glfw.KEY_Z): self.escala = max(0.2, self.escala - 1.0 * dt)
        if g(glfw.KEY_X): self.escala = min(3.0, self.escala + 1.0 * dt)

    # ------------------------------------------------------------------
    def desenhar(self):
        fb_w, fb_h = glfw.get_framebuffer_size(self.window)
        if fb_w == 0 or fb_h == 0:           # janela minimizada
            return
        glViewport(0, 0, fb_w, fb_h)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Projeção em perspectiva
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(tf.para_opengl(tf.perspectiva(45.0, fb_w / fb_h, 0.1, 50.0)))

        # Matriz de Visão (Mundo -> Câmera)
        glMatrixMode(GL_MODELVIEW)
        visao = tf.look_at((0.0, 0.0, 6.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        glLoadMatrixf(tf.para_opengl(visao))
        lighting.posicionar_luz()
        self.desenhar_marcador_luz()

        # Matriz de Modelo: M = T · R · S  (R vem do quaternio do trackball)
        T = tf.translacao(*self.posicao)
        R = self.trackball.matriz()
        S = tf.escala(self.escala, self.escala, self.escala)
        modelo = tf.compor_modelo(T, R, S)

        glLoadMatrixf(tf.para_opengl(visao @ modelo))
        glColor3f(*self.cor)
        self.piramide.desenhar()

    def desenhar_marcador_luz(self):
        """Ponto amarelo mostrando onde está a luz."""
        estava_ligada = self.luz_ligada
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.95, 0.4)
        glPointSize(8.0)
        glBegin(GL_POINTS)
        glVertex3fv(np.array(lighting.POSICAO_LUZ[:3], dtype=np.float32))
        glEnd()
        if estava_ligada:
            glEnable(GL_LIGHTING)

    # ------------------------------------------------------------------
    def executar(self):
        self.iniciar_janela()
        color_utils.testar_conversao()
        self.imprimir_ajuda()

        anterior = glfw.get_time()
        while not glfw.window_should_close(self.window):
            agora = glfw.get_time()
            dt, anterior = agora - anterior, agora
            glfw.poll_events()
            self.processar_teclas_continuas(dt)
            self.desenhar()
            glfw.swap_buffers(self.window)
        glfw.terminate()

    @staticmethod
    def imprimir_ajuda():
        print("\n=== CONTROLES ===")
        print("Mouse (botão esquerdo + arrastar): rotação via Trackball/Quaternios")
        print("W/A/S/D: mover em Y/X | Q/E: mover em Z | Z/X: escala")
        print("1/2/3: aumenta R/G/B (com SHIFT diminui) e mostra HSV")
        print("H: aplica cor de máscara HSV gerada com OpenCV (cicla faixas)")
        print("L: liga/desliga luz | F: flat/smooth | ESPAÇO: resetar | ESC: sair\n")


def main():
    try:
        App().executar()
    except Exception as e:
        print("Erro:", e)
        glfw.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
