"""
PARTE 3 - Cores: modelo RGB, conversão para HSV e máscara com OpenCV.
"""
import colorsys
import os
import cv2
import numpy as np

# Faixas HSV (escala do OpenCV: H 0-179, S 0-255): nome, (Hmin,Hmax), (Smin,Smax)
FAIXAS_HSV = [
    ("Laranja", (8, 22), (150, 255)),
    ("Amarelo", (22, 35), (150, 255)),
    ("Verde", (40, 85), (120, 255)),
    ("Ciano", (85, 100), (120, 255)),
    ("Azul", (100, 130), (120, 255)),
    ("Magenta", (140, 170), (120, 255)),
    ("Vermelho", (0, 6), (150, 255)),
]


def rgb_para_hsv(rgb):
    """RGB float [0,1] -> HSV (H em graus 0-360, S e V em 0-1) usando OpenCV."""
    pixel = np.uint8([[[round(c * 255) for c in rgb]]])      # 1x1x3 em RGB
    h, s, v = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)[0, 0]
    return float(h) * 2.0, float(s) / 255.0, float(v) / 255.0


def hsv_para_rgb(hsv):
    """HSV (H graus, S e V 0-1) -> RGB float [0,1] usando OpenCV."""
    h, s, v = hsv
    pixel = np.uint8([[[round(h / 2.0) % 180, round(s * 255), round(v * 255)]]])
    r, g, b = cv2.cvtColor(pixel, cv2.COLOR_HSV2RGB)[0, 0]
    return (r / 255.0, g / 255.0, b / 255.0)


def testar_conversao():
    """Compara a conversão do OpenCV com colorsys (biblioteca padrão)."""
    print("Teste de conversão RGB -> HSV (OpenCV vs colorsys):")
    for rgb in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0.8, 0.4, 0.2)]:
        h, s, v = rgb_para_hsv(rgb)
        hc, sc, vc = colorsys.rgb_to_hsv(*rgb)
        print(f"  RGB={rgb} -> OpenCV HSV=({h:.0f}°, {s:.2f}, {v:.2f}) | "
              f"colorsys=({hc * 360:.0f}°, {sc:.2f}, {vc:.2f})")


def gerar_mascara_hsv(indice, pasta_saida="output"):
    """
    Gera uma imagem HSV (matiz x saturação), aplica uma máscara com limites de
    matiz/saturação via cv2.inRange e devolve a cor média da região mascarada
    (RGB 0-1) para ser usada como material do objeto 3D.
    """
    nome, (h_min, h_max), (s_min, s_max) = FAIXAS_HSV[indice % len(FAIXAS_HSV)]

    # Imagem: colunas = matiz (0-179), linhas = saturação (255 -> 0)
    matiz = np.tile(np.arange(180, dtype=np.uint8), (256, 1))
    satur = np.tile(np.arange(255, -1, -1, dtype=np.uint8).reshape(256, 1), (1, 180))
    valor = np.full((256, 180), 230, dtype=np.uint8)
    hsv = cv2.merge([matiz, satur, valor])

    mascara = cv2.inRange(hsv, (h_min, s_min, 0), (h_max, s_max, 255))
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    resultado = cv2.bitwise_and(rgb, rgb, mask=mascara)

    if cv2.countNonZero(mascara) == 0:
        cor = (0.7, 0.7, 0.7)
    else:
        r, g, b, _ = cv2.mean(rgb, mask=mascara)
        cor = (r / 255.0, g / 255.0, b / 255.0)

    try:
        os.makedirs(pasta_saida, exist_ok=True)
        cv2.imwrite(os.path.join(pasta_saida, "mascara_hsv.png"),
                    cv2.cvtColor(resultado, cv2.COLOR_RGB2BGR))
    except Exception as e:  # salvar a imagem é opcional
        print("Aviso: não foi possível salvar a máscara:", e)

    return nome, cor
