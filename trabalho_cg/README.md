# Aplicação Interativa 3D – Computação Gráfica e Visão Computacional

Pirâmide de base quadrada com iluminação OpenGL, transformações em coordenadas
homogêneas, cores RGB/HSV (OpenCV) e rotação por Trackball com quaternios.

## Como rodar (VS Code, Windows)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```
No VS Code: Ctrl+Shift+P -> "Python: Select Interpreter" -> escolha `.venv`.

## Controles
| Tecla / mouse | Ação |
|---|---|
| Botão esquerdo + arrastar | Rotação (Trackball + quaternios) |
| W/A/S/D e Q/E | Translação |
| Z / X | Escala |
| 1 / 2 / 3 (SHIFT diminui) | Altera R / G / B e imprime o HSV |
| H | Cor a partir de máscara HSV gerada com OpenCV |
| L | Liga/desliga iluminação |
| F | Sombreamento flat/smooth |
| Espaço | Reseta | 
| ESC | Sair |

## Estrutura
- `src/main.py` – janela GLFW, loop, entrada (Partes 1 e 4)
- `src/geometry.py` – pirâmide, normais por produto vetorial (Partes 1 e 3)
- `src/transforms.py` – T, S, Rx, Ry, Rz, M = T·R·S, look_at, perspectiva (Parte 2)
- `src/lighting.py` – GL_LIGHTING / GL_LIGHT0 (Parte 3)
- `src/color_utils.py` – RGB↔HSV e máscara OpenCV (Parte 3)
- `src/quaternion.py`, `src/trackball.py` – quaternios e trackball (Parte 4)
