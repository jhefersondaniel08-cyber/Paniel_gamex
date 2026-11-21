import os

# ==========================================================
# CONFIGURACIÓN GENERAL (Estilo Undertale / Deltarune)
# ==========================================================
# Resolución de la ventana visible (Aumentada a 960x720 para mayor tamaño y comodidad visual)
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720

# Resolución interna virtual (retro pixel scaling 2x crisp integer zoom)
# Similar al clásico 320x240 / 400x300 de Undertale y Deltarune
VIRTUAL_WIDTH = 400
VIRTUAL_HEIGHT = 300

TILE_SIZE = 32
FPS = 60

# Paleta de colores Undertale / Deltarune
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_SOUL_RED = (255, 0, 0)
COLOR_SOUL_GREEN = (40, 245, 95)
COLOR_SAVE_YELLOW = (255, 240, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_UI_BG = (10, 10, 15)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
