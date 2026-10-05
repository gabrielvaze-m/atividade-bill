"""
PARTE 3 - Iluminação e sombreamento (pipeline fixo do OpenGL).
"""
from OpenGL.GL import (
    glEnable, glDisable, glLightfv, glMaterialfv, glMaterialf, glColorMaterial,
    glLightModelfv, glShadeModel, GL_LIGHTING, GL_LIGHT0, GL_AMBIENT, GL_DIFFUSE,
    GL_SPECULAR, GL_POSITION, GL_COLOR_MATERIAL, GL_FRONT_AND_BACK,
    GL_AMBIENT_AND_DIFFUSE, GL_SHININESS, GL_NORMALIZE, GL_LIGHT_MODEL_AMBIENT,
    GL_FLAT, GL_SMOOTH,
)

POSICAO_LUZ = (3.0, 4.0, 5.0, 1.0)   # luz pontual no espaço do mundo


def configurar_iluminacao():
    """Habilita GL_LIGHTING e GL_LIGHT0 com componentes ambiente/difusa/especular."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)           # mantém normais unitárias após escala
    glShadeModel(GL_FLAT)            # sombreamento por face

    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.20, 0.20, 0.20, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.90, 0.90, 0.90, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.00, 1.00, 1.00, 1.0))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.10, 0.10, 0.10, 1.0))

    # glColor passa a definir ambiente + difusa do material
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.6, 0.6, 0.6, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 40.0)


def posicionar_luz():
    """Deve ser chamado com a matriz de VISÃO carregada (luz fixa no mundo)."""
    glLightfv(GL_LIGHT0, GL_POSITION, POSICAO_LUZ)


def ligar_luz(ligada):
    (glEnable if ligada else glDisable)(GL_LIGHTING)


def usar_suave(suave):
    glShadeModel(GL_SMOOTH if suave else GL_FLAT)
