import os
import math
import random
import pygame
from configuracion import VIRTUAL_WIDTH, VIRTUAL_HEIGHT
from objetos_mundo import SavePointObject, SignObject, ChestObject, RuinPillar, WillOWisp, TwistedTreeProp, InteriorProp

# ==========================================================
# ESCENAS DE INTERIORES (Habitaciones detalladas estilo Deltarune)
# ==========================================================
class InteriorScene:
    def __init__(self, scene_id, name, return_exterior_pos=None):
        self.scene_id = scene_id
        self.name = name
        self.return_exterior_pos = return_exterior_pos
        self.pixel_w = VIRTUAL_WIDTH
        self.pixel_h = VIRTUAL_HEIGHT

        self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
        self.solid_rects = []
        self.world_objects = []
        self.exit_rect = None

        self._build_scene()

    def _build_scene(self):
        if self.scene_id == "cemetery_entrance":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(base_dir, "Mapa_prueba", "pixilart-drawing.png")
            try:
                raw_surf = pygame.image.load(img_path)
                try:
                    self.surface = raw_surf.convert()
                except Exception:
                    self.surface = raw_surf
                self.pixel_w, self.pixel_h = self.surface.get_size()
            except Exception as e:
                print(f"Aviso cargando pixilart-drawing.png ({e}), usando superficie alternativa.")
                self.pixel_w = 500
                self.pixel_h = 500
                self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
                self.surface.fill((38, 48, 40))
            self._build_cemetery_entrance()
        elif self.scene_id == "cemetery":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_cemetery()
        elif self.scene_id == "cemetery_depths":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_cemetery_depths()
        elif self.scene_id == "eclipse_sanctuary":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_eclipse_sanctuary()

        for obj in self.world_objects:
            if obj.solid_rect:
                self.solid_rects.append(obj.solid_rect)

    def draw_ground(self, surface, camera):
        cx = int(camera.x)
        cy = int(camera.y)
        surface.blit(self.surface, (-cx, -cy))

    # 10. ENTRADA DEL CEMENTERIO (Cargada desde el nuevo mapa de prueba Mapa_prueba/pixilart-drawing.png)
    def _build_cemetery_entrance(self):
        # Límites exteriores del mapa (bordes negros para no salirse de la pantalla)
        self.solid_rects.append(pygame.Rect(0, 0, self.pixel_w, 24))         # Límite superior
        self.solid_rects.append(pygame.Rect(0, 0, 32, self.pixel_h))          # Borde lateral izquierdo
        self.solid_rects.append(pygame.Rect(468, 0, 32, self.pixel_h))        # Borde lateral derecho
        self.solid_rects.append(pygame.Rect(0, 446, self.pixel_w, 54))        # Borde inferior (fondo de la calle)

        # REJAS DE HIERRO CON COLISIÓN COMPLETA (¡No se puede pasar por las rejas!)
        # Reja izquierda: cubre desde el borde izquierdo hasta el poste izquierdo de la puerta (x=32 a 235, y=350 a 406)
        self.solid_rects.append(pygame.Rect(32, 350, 203, 56))
        # Reja derecha: cubre desde el poste derecho de la puerta hasta el borde derecho (x=265 a 468, y=350 a 406)
        self.solid_rects.append(pygame.Rect(265, 350, 203, 56))

        # MARCO DE LA PUERTA (Apenas se pisa por este marco hay cambio de escena inmediato)
        # Situado exactamente en el vano central entre las rejas (x=234..266, y=368..402)
        self.cemetery_gate_rect = pygame.Rect(234, 368, 32, 34)

        # Punto de guardado en la acera (a la derecha de la puerta)
        self.world_objects.append(SavePointObject(x=320, y=406))

        # Cartel de hierro en la acera (a la izquierda de la puerta)
        self.world_objects.append(SignObject(
            x=160, y=406,
            message="* CARTEL DE HIERRO: 'CEMENTERIO DE HOMETOWN. Silencio para los que descansan bajo la tierra.'"
        ))

    # 2. INTERIOR DEL CEMENTERIO (Versión Gótica Monumental, Expandida 800x600 y Hermosa)
    def _build_cemetery(self):
        s = self.surface
        # Fondo base: hierba oscura, fría y musgo nocturno
        s.fill((20, 24, 22))

        # 1. CIELO NOCTURNO CON DEGRADADO ÍNDIGO/VIOLETA (800 px)
        for y in range(76):
            t = y / 76.0
            r = int(8 + (26 - 8) * t)
            g = int(8 + (18 - 8) * t)
            b = int(22 + (42 - 22) * t)
            pygame.draw.line(s, (r, g, b), (0, y), (800, y))

        # Estrellas de distintos brillos y destellos en cruz
        random.seed(42)  # Semilla fija para constelaciones hermosas y estables
        for _ in range(95):
            sx = random.randint(0, 799)
            sy = random.randint(2, 70)
            b_val = random.randint(180, 255)
            s.set_at((sx, sy), (b_val, b_val, b_val - 20))

        # Destellos en cruz para estrellas brillantes
        for csx, csy in [(70, 22), (160, 14), (280, 26), (390, 16), (510, 24), (610, 15), (740, 28)]:
            pygame.draw.line(s, (255, 255, 230), (csx - 2, csy), (csx + 2, csy), 1)
            pygame.draw.line(s, (255, 255, 230), (csx, csy - 2), (csx, csy + 2), 1)

        # Siluetas lejanas en el horizonte (agujas góticas y cipreses)
        horizon_silhouettes = [
            [(25, 76), (32, 54), (39, 76)],
            [(40, 76), (50, 48), (60, 76)],
            [(115, 76), (124, 44), (133, 76)],
            [(280, 76), (290, 52), (300, 76)],
            [(495, 76), (505, 46), (515, 76)],
            [(635, 76), (645, 50), (655, 76)],
            [(755, 76), (764, 42), (773, 76)],
        ]
        for poly in horizon_silhouettes:
            pygame.draw.polygon(s, (14, 12, 22), poly)

        # 2. LUNA LLENA HERMOSA CON HALOS Y CRÁTERES
        moon_cx, moon_cy = 680, 34
        for rad, alpha in [(46, 16), (32, 38), (22, 70)]:
            halo = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo, (200, 220, 255, alpha), (rad, rad), rad)
            s.blit(halo, (moon_cx - rad, moon_cy - rad))

        # Disco lunar y cráteres sutiles
        pygame.draw.circle(s, (246, 244, 230), (moon_cx, moon_cy), 15)
        pygame.draw.circle(s, (220, 216, 202), (moon_cx - 4, moon_cy - 2), 5)
        pygame.draw.circle(s, (214, 210, 196), (moon_cx + 5, moon_cy + 4), 4)
        pygame.draw.circle(s, (210, 206, 192), (moon_cx - 2, moon_cy + 6), 3)

        # Rayos diagonales de luna que bañan las lápidas (volumetric moonlight)
        rays = pygame.Surface((800, 600), pygame.SRCALPHA)
        pygame.draw.polygon(rays, (200, 220, 255, 11), [(moon_cx, moon_cy), (380, 600), (560, 600)])
        pygame.draw.polygon(rays, (200, 220, 255, 7), [(moon_cx, moon_cy), (160, 600), (320, 600)])
        pygame.draw.polygon(rays, (200, 220, 255, 9), [(moon_cx, moon_cy), (580, 600), (760, 600)])
        s.blit(rays, (0, 0))

        # 3. MUROS PERIMETRALES DE PIEDRA LABRADA CON REJAS Y AGUJAS GÓTICAS
        # Muro superior (y=76..100)
        for bx in range(0, 800, 24):
            shade = random.randint(80, 96)
            pygame.draw.rect(s, (shade, shade - 2, shade + 2), (bx, 76, 24, 24))
            pygame.draw.rect(s, (45, 45, 52), (bx, 76, 24, 24), 1)
            pygame.draw.line(s, (shade + 20, shade + 18, shade + 22), (bx + 1, 77), (bx + 22, 77), 1)
            # Agujas góticas de hierro en lo alto del muro
            pygame.draw.line(s, (42, 42, 48), (bx + 12, 62), (bx + 12, 76), 2)
            pygame.draw.circle(s, (60, 60, 70), (bx + 12, 62), 2)

        # Muros laterales (x=0..24 y x=776..800)
        for by in range(76, 600, 20):
            s1 = random.randint(80, 96)
            pygame.draw.rect(s, (s1, s1 - 2, s1 + 2), (0, by, 24, 20))
            pygame.draw.rect(s, (45, 45, 52), (0, by, 24, 20), 1)
            s2 = random.randint(80, 96)
            pygame.draw.rect(s, (s2, s2 - 2, s2 + 2), (776, by, 24, 20))
            pygame.draw.rect(s, (45, 45, 52), (776, by, 24, 20), 1)

        # Muro inferior (con apertura central para salida al sur: x=370..430)
        for bx in range(0, 370, 24):
            s_val = random.randint(80, 96)
            pygame.draw.rect(s, (s_val, s_val - 2, s_val + 2), (bx, 576, 24, 24))
            pygame.draw.rect(s, (45, 45, 52), (bx, 576, 24, 24), 1)
        for bx in range(430, 800, 24):
            s_val = random.randint(80, 96)
            pygame.draw.rect(s, (s_val, s_val - 2, s_val + 2), (bx, 576, 24, 24))
            pygame.draw.rect(s, (45, 45, 52), (bx, 576, 24, 24), 1)

        # Postes de hierro forjado del portal sur
        pygame.draw.rect(s, (55, 55, 65), (364, 568, 8, 32), border_radius=2)
        pygame.draw.circle(s, (80, 85, 95), (368, 566), 4)
        pygame.draw.rect(s, (55, 55, 65), (428, 568, 8, 32), border_radius=2)
        pygame.draw.circle(s, (80, 85, 95), (432, 566), 4)

        # Enredaderas de hiedra oscura que trepan por los muros
        for ix, iy in [(40, 82), (180, 84), (520, 82), (640, 84), (22, 220), (22, 440), (778, 200), (778, 420)]:
            pygame.draw.circle(s, (38, 65, 42), (ix, iy), 5)
            pygame.draw.circle(s, (52, 90, 58), (ix + 2, iy + 2), 3)

        # 4. CAMINOS DE ADOQUINES TEXTURIZADOS Y CRUCE DE AVENIDAS
        # Gran Avenida Central (desde el portal sur hasta la escalinata del mausoleo)
        for gy in range(148, 580, 14):
            for gx in range(374, 426, 16):
                shade = random.randint(66, 80)
                pygame.draw.rect(s, (shade, shade - 3, shade + 3), (gx, gy, 15, 13), border_radius=2)
                pygame.draw.rect(s, (40, 40, 46), (gx, gy, 15, 13), 1, border_radius=2)
                pygame.draw.line(s, (shade + 18, shade + 15, shade + 20), (gx + 1, gy + 1), (gx + 13, gy + 1), 1)

        # Gran Avenida Transversal (Crucero Este-Oeste que conecta todo el cementerio)
        for gx in range(36, 764, 16):
            for gy in range(326, 366, 14):
                shade = random.randint(64, 78)
                pygame.draw.rect(s, (shade, shade - 3, shade + 3), (gx, gy, 15, 13), border_radius=2)
                pygame.draw.rect(s, (40, 40, 46), (gx, gy, 15, 13), 1, border_radius=2)

        # Senderos secundarios hacia las tumbas
        # Hacia Gerson y Crystal (Oeste Norte)
        for gx in range(130, 374, 16):
            for gy in range(180, 206, 13):
                shade = random.randint(60, 74)
                pygame.draw.rect(s, (shade, shade - 3, shade + 3), (gx, gy, 15, 12), border_radius=2)
                pygame.draw.rect(s, (38, 38, 44), (gx, gy, 15, 12), 1, border_radius=2)

        # Hacia la Fuente de la Memoria y Mutt (Este Norte)
        for gx in range(426, 720, 16):
            for gy in range(180, 206, 13):
                shade = random.randint(60, 74)
                pygame.draw.rect(s, (shade, shade - 3, shade + 3), (gx, gy, 15, 12), border_radius=2)
                pygame.draw.rect(s, (38, 38, 44), (gx, gy, 15, 12), 1, border_radius=2)

        # Charcos de agua con reflejos nocturnos en los adoquines
        puddles = [
            (386, 480, 24, 10),
            (406, 260, 20, 8),
            (220, 340, 26, 10),
            (580, 342, 28, 11),
            (160, 192, 18, 7),
            (650, 194, 18, 7)
        ]
        for px, py, pw, ph in puddles:
            pygame.draw.ellipse(s, (28, 42, 60), (px, py, pw, ph))
            pygame.draw.ellipse(s, (45, 65, 90), (px + 2, py + 1, pw - 4, ph - 2), 1)
            pygame.draw.line(s, (180, 210, 255), (px + 4, py + 2), (px + pw - 6, py + 2), 1)

        # Hojas secas otoñales esparcidas
        autumn_colors = [(165, 80, 35), (190, 60, 40), (140, 100, 30), (175, 110, 45)]
        random.seed(101)
        for _ in range(60):
            lx = random.randint(30, 760)
            ly = random.randint(105, 570)
            col = random.choice(autumn_colors)
            pygame.draw.circle(s, col, (lx, ly), 2)

        # MANCHAS DE FLORES SILVESTRES (Florecitas doradas y no-me-olvides celestes)
        for fx, fy in [(150, 215), (170, 212), (185, 216), (235, 214), (390, 520), (412, 528)]:
            # Flores doradas clásicas de Undertale
            pygame.draw.circle(s, (245, 215, 60), (fx, fy), 3)
            pygame.draw.circle(s, (255, 245, 140), (fx, fy), 1)
            pygame.draw.line(s, (45, 110, 50), (fx, fy + 1), (fx, fy + 4), 1)

        for fx, fy in [(245, 210), (260, 212), (275, 208), (550, 210), (565, 214), (580, 209)]:
            # Flores no-me-olvides celestes
            pygame.draw.circle(s, (90, 160, 245), (fx, fy), 3)
            pygame.draw.circle(s, (210, 235, 255), (fx, fy), 1)

        # Hongos bioluminiscentes turquesas y violetas
        for hx, hy in [(70, 235), (74, 239), (480, 250), (700, 290), (110, 510), (660, 510)]:
            pygame.draw.circle(s, (80, 240, 210), (hx, hy), 2)
            pygame.draw.circle(s, (180, 110, 255), (hx + 4, hy + 3), 2)

        # Niebla baja mágica con capas onduladas
        for fy in [310, 430, 530]:
            fog = pygame.Surface((800, 22), pygame.SRCALPHA)
            fog.fill((160, 190, 215, 20))
            s.blit(fog, (0, fy))

        # 5. GRAN MAUSOLEO CATEDRAL GÓTICO (Panteón de la Runa Delta - x: 328..472, y: 64..150)
        # Escalones de mármol desgastado
        pygame.draw.rect(s, (65, 68, 76), (324, 138, 152, 14), border_radius=2)
        pygame.draw.rect(s, (78, 82, 92), (332, 130, 136, 10), border_radius=2)
        pygame.draw.rect(s, (90, 94, 104), (340, 122, 120, 9), border_radius=2)

        # Cuerpo principal de piedra labrada
        pygame.draw.rect(s, (74, 76, 86), (336, 68, 128, 56))
        pygame.draw.rect(s, (50, 52, 60), (336, 68, 128, 56), 2)

        # Columnas clásicas estriadas a los lados
        for col_x in [342, 358, 434, 450]:
            pygame.draw.rect(s, (95, 98, 110), (col_x, 74, 8, 48), border_radius=1)
            pygame.draw.rect(s, (120, 124, 138), (col_x - 1, 72, 10, 3), border_radius=1)
            pygame.draw.rect(s, (120, 124, 138), (col_x - 1, 120, 10, 3), border_radius=1)

        # Puerta gótica entreabierta hacia el Abismo del Cementerio con resplandor carmesí/violeta
        pygame.draw.rect(s, (16, 10, 24), (384, 82, 32, 42), border_radius=2)
        pygame.draw.rect(s, (195, 45, 85), (394, 84, 12, 38))
        pygame.draw.rect(s, (255, 160, 190), (398, 86, 4, 34))
        pygame.draw.rect(s, (52, 48, 56), (384, 82, 32, 42), 1, border_radius=2)
        pygame.draw.arc(s, (52, 48, 56), (384, 72, 32, 20), 0, math.pi, 2)
        # Resplandor místico en los escalones de entrada al Abismo
        pygame.draw.line(s, (235, 70, 110), (385, 123), (415, 123), 2)

        # Frontón triangular superior
        pygame.draw.polygon(s, (84, 86, 98), [(400, 48), (328, 68), (472, 68)])
        pygame.draw.polygon(s, (50, 52, 60), [(400, 48), (328, 68), (472, 68)], 1)
        # Rosetón vitral con la RUNA DELTA brillante
        pygame.draw.circle(s, (40, 30, 55), (400, 58), 8)
        pygame.draw.circle(s, (245, 215, 80), (400, 55), 3)
        pygame.draw.polygon(s, (160, 120, 240), [(400, 58), (396, 63), (404, 63)])

        # Gárgolas / pebeteros de piedra a los lados con fuego carmesí de advertencia
        for ux in [318, 474]:
            pygame.draw.rect(s, (70, 72, 80), (ux, 116, 10, 14), border_radius=1)
            pygame.draw.circle(s, (235, 65, 95), (ux + 5, 112), 4)
            pygame.draw.circle(s, (255, 215, 120), (ux + 5, 112), 2)

        # Portal de entrada a la parte más profunda del cementerio (Abismo del Cementerio)
        self.depths_gate_rect = pygame.Rect(378, 134, 44, 24)

        # Cartel junto a la escalinata del Mausoleo avisando del Abismo y el Jefe
        self.world_objects.append(SignObject(
            x=342, y=156,
            message="* CARTEL DEL PANTEÓN: 'Gran Mausoleo Ancestral. Custodiado por Morvath, el Sepulturero Eterno.'"
        ))

        # 1. Árboles góticos antiguos con y sin faroles
        self.world_objects.append(TwistedTreeProp(48, 190, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(280, 220, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(90, 480, has_lantern=False))
        self.world_objects.append(TwistedTreeProp(490, 220, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(710, 260, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(670, 480, has_lantern=False))

        # 2. Fuegos fatuos / Ánimas danzantes flotantes
        self.world_objects.append(WillOWisp(120, 190, color=(130, 235, 255)))
        self.world_objects.append(WillOWisp(230, 360, color=(195, 160, 255)))
        self.world_objects.append(WillOWisp(380, 210, color=(140, 255, 210)))
        self.world_objects.append(WillOWisp(580, 220, color=(160, 210, 255)))
        self.world_objects.append(WillOWisp(700, 360, color=(255, 170, 220)))
        self.world_objects.append(WillOWisp(260, 500, color=(180, 240, 190)))

        # 3. Estatua del Ángel del Silencio (Monumento rezando)
        def draw_angel_statue(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (80, 82, 92), (cx + 4, cy + 34, w - 8, 18), border_radius=2)
            pygame.draw.rect(surf, (60, 62, 70), (cx + 4, cy + 34, w - 8, 18), 1, border_radius=2)
            pygame.draw.polygon(surf, (98, 100, 112), [(cx + w//2, cy + 12), (cx + 8, cy + 34), (cx + w - 8, cy + 34)])
            pygame.draw.circle(surf, (110, 112, 124), (cx + w//2, cy + 10), 6)
            pygame.draw.polygon(surf, (120, 124, 138), [(cx + w//2 - 2, cy + 14), (cx + 2, cy + 6), (cx + 6, cy + 26)])
            pygame.draw.polygon(surf, (120, 124, 138), [(cx + w//2 + 2, cy + 14), (cx + w - 2, cy + 6), (cx + w - 6, cy + 26)])
            # Velas encendidas a los pies
            pygame.draw.rect(surf, (240, 235, 215), (cx + 6, cy + 30, 3, 5))
            pygame.draw.circle(surf, (255, 210, 80), (cx + 7, cy + 28), 2)
            pygame.draw.rect(surf, (240, 235, 215), (cx + w - 9, cy + 30, 3, 5))
            pygame.draw.circle(surf, (255, 210, 80), (cx + w - 8, cy + 28), 2)
        self.world_objects.append(InteriorProp(
            160, 410, 40, 52, 464, draw_angel_statue,
            [
                "* Monumento del Ángel del Silencio.",
                "* 'Para aquellos cuyas voces se apagaron pacíficamente en la noche.'",
                "* Pequeñas velas titilan a sus pies, arrojando sombras danzantes sobre el musgo.",
                "* (Sientes una caricia tibia que calma tu espíritu. +15 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 15

        # 4. Cruz Celta de Piedra Antigua
        def draw_celtic_cross(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (78, 80, 88), (cx + 4, cy + 36, w - 8, 14), border_radius=2)
            pygame.draw.rect(surf, (58, 60, 68), (cx + 4, cy + 36, w - 8, 14), 1, border_radius=2)
            pygame.draw.rect(surf, (92, 94, 104), (cx + w//2 - 3, cy + 4, 6, 34), border_radius=1)
            pygame.draw.rect(surf, (92, 94, 104), (cx + 6, cy + 14, 22, 6), border_radius=1)
            pygame.draw.circle(surf, (110, 114, 126), (cx + w//2, cy + 17), 10, 2)
            pygame.draw.circle(surf, (60, 95, 65), (cx + w//2 - 1, cy + 16), 2)
        self.world_objects.append(InteriorProp(
            80, 320, 34, 50, 372, draw_celtic_cross,
            [
                "* Antigua Cruz Celta de Piedra.",
                "* Los grabados entrelazados representan la eternidad del alma y el ciclo sin fin.",
                "* El viento nocturno silba una melodía melancólica a través del círculo de piedra."
            ]
        ))

        # 5. Entrada a la Antigua Cripta de los Pioneros
        def draw_old_crypt(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (70, 72, 82), (cx, cy + 8, w, h - 8), border_radius=3)
            pygame.draw.rect(surf, (48, 50, 58), (cx, cy + 8, w, h - 8), 2, border_radius=3)
            pygame.draw.polygon(surf, (84, 86, 96), [(cx + w//2, cy), (cx - 2, cy + 8), (cx + w + 2, cy + 8)])
            # Entrada enrejada y escalones descendentes en sombra
            pygame.draw.rect(surf, (14, 14, 18), (cx + 12, cy + 18, w - 24, h - 18), border_radius=2)
            for gx in range(cx + 16, cx + w - 16, 6):
                pygame.draw.line(surf, (65, 68, 78), (gx, cy + 18), (gx, cy + h - 1), 1)
            pygame.draw.line(surf, (65, 68, 78), (cx + 12, cy + 32), (cx + w - 13, cy + 32), 1)
        self.world_objects.append(InteriorProp(
            70, 96, 60, 52, 150, draw_old_crypt,
            [
                "* Entrada a la Antigua Cripta Familiar.",
                "* 'Aquí yacen los pioneros que fundaron el valle.'",
                "* El aire que sube desde los escalones de piedra es gélido como la escarcha."
            ]
        ))

        # 6. Lápida de Gerson Boom
        def draw_gerson_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (94, 96, 106), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (68, 70, 80), (cx, cy, w, h), 1, border_radius=4)
            # Martillo de herrero tallado en relieve
            pygame.draw.rect(surf, (155, 120, 75), (cx + w//2 - 2, cy + 8, 4, 16))
            pygame.draw.rect(surf, (170, 140, 95), (cx + w//2 - 8, cy + 8, 16, 6))
            # Conchas marinas y flores a los pies
            pygame.draw.circle(surf, (230, 220, 200), (cx + 6, cy + h - 5), 3)
            pygame.draw.circle(surf, (245, 215, 60), (cx + w - 8, cy + h - 5), 3)
        self.world_objects.append(InteriorProp(
            160, 160, 44, 48, 210, draw_gerson_tomb,
            [
                "* Lápida de GERSON BOOM, el Martillo de la Justicia.",
                "* 'Aquí descansa el viejo historiador que lo vio todo.'",
                "* Una profunda corriente de serenidad y determinación emana de esta piedra.",
                "* (Tu corazón se llena de paz inmutable. +20 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 20

        # 7. Lápida de Crystal
        def draw_crystal_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (96, 102, 118), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (72, 78, 94), (cx, cy, w, h), 1, border_radius=4)
            # Alas de ángel grabadas
            pygame.draw.arc(surf, (180, 210, 245), (cx + 4, cy + 4, 16, 18), 0, math.pi, 2)
            pygame.draw.arc(surf, (180, 210, 245), (cx + w - 20, cy + 4, 16, 18), 0, math.pi, 2)
            # Ramo de flores no-me-olvides azules
            for fi, (fx, fy) in enumerate([(cx + 8, cy + 34), (cx + 20, cy + 31), (cx + 32, cy + 35)]):
                pygame.draw.circle(surf, (80, 150, 250), (fx, fy), 4)
                pygame.draw.circle(surf, (215, 235, 255), (fx, fy), 2)
        self.world_objects.append(InteriorProp(
            250, 160, 42, 48, 210, draw_crystal_tomb,
            [
                "* Lápida de CRYSTAL.",
                "* Flores celestes frescas adornan su base. Alguien las puso hace pocas horas.",
                "* (El aroma floral disipa tu terror y refresca tu mente. +20 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 20

        # 8. Cripta de la Antigua Guardia Real
        def draw_guard_crypt(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (76, 78, 88), (cx, cy + 8, w, h - 8), border_radius=3)
            pygame.draw.rect(surf, (52, 54, 62), (cx, cy + 8, w, h - 8), 2, border_radius=3)
            pygame.draw.polygon(surf, (90, 92, 104), [(cx + w//2, cy), (cx - 2, cy + 8), (cx + w + 2, cy + 8)])
            # Escudo y espadas cruzadas esculpidas
            pygame.draw.rect(surf, (180, 185, 200), (cx + w//2 - 6, cy + 18, 12, 14), border_radius=1)
            pygame.draw.line(surf, (210, 215, 230), (cx + 14, cy + 14), (cx + w - 14, cy + 36), 2)
            pygame.draw.line(surf, (210, 215, 230), (cx + w - 14, cy + 14), (cx + 14, cy + 36), 2)
        self.world_objects.append(InteriorProp(
            670, 96, 60, 52, 150, draw_guard_crypt,
            [
                "* Cripta de la Antigua Guardia Real.",
                "* 'Su honor fue su escudo; su deber, su vida.'",
                "* Dos espadas de piedra descansan cruzadas sobre el frontón esculpido."
            ]
        ))

        # 9. Fuente de la Memoria (Fountain of Memory)
        def draw_fountain(surf, cx, cy, w, h):
            # Base octogonal de la fuente
            pygame.draw.polygon(surf, (74, 78, 88), [
                (cx + 10, cy + h), (cx + w - 10, cy + h),
                (cx + w, cy + h - 14), (cx + w, cy + 16),
                (cx + w - 10, cy), (cx + 10, cy),
                (cx, cy + 16), (cx, cy + h - 14)
            ])
            pygame.draw.polygon(surf, (50, 54, 62), [
                (cx + 10, cy + h), (cx + w - 10, cy + h),
                (cx + w, cy + h - 14), (cx + w, cy + 16),
                (cx + w - 10, cy), (cx + 10, cy),
                (cx, cy + 16), (cx, cy + h - 14)
            ], 2)
            # Agua cristalina ondulante
            pygame.draw.ellipse(surf, (30, 60, 95), (cx + 6, cy + 8, w - 12, h - 16))
            pygame.draw.ellipse(surf, (60, 110, 160), (cx + 10, cy + 12, w - 20, h - 24), 1)
            # Reflejos estelares en el agua
            pygame.draw.circle(surf, (200, 230, 255), (cx + w//2 - 6, cy + h//2 - 2), 2)
            pygame.draw.circle(surf, (200, 230, 255), (cx + w//2 + 8, cy + h//2 + 3), 1)
            # Columna central y gárgola surtidora
            pygame.draw.rect(surf, (90, 95, 105), (cx + w//2 - 4, cy + 12, 8, 16), border_radius=1)
            pygame.draw.circle(surf, (110, 115, 128), (cx + w//2, cy + 10), 4)
        self.world_objects.append(InteriorProp(
            560, 155, 54, 50, 208, draw_fountain,
            [
                "* La Fuente de la Memoria.",
                "* El agua cristalina refleja el brillo de las estrellas y la luna llena.",
                "* Te enjuagas la cara con el agua helada. Te sientes renovado. (+15 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 15

        # 10. Lápida de Mutt
        def draw_mutt_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (94, 92, 102), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (72, 70, 80), (cx, cy, w, h), 1, border_radius=4)
            # Hueso tallado
            pygame.draw.rect(surf, (230, 225, 210), (cx + w//2 - 8, cy + 12, 16, 5))
            pygame.draw.circle(surf, (230, 225, 210), (cx + w//2 - 8, cy + 14), 4)
            pygame.draw.circle(surf, (230, 225, 210), (cx + w//2 + 8, cy + 14), 4)
            # Pelotita roja
            pygame.draw.circle(surf, (220, 50, 50), (cx + 8, cy + h - 5), 4)
        self.world_objects.append(InteriorProp(
            680, 170, 40, 48, 220, draw_mutt_tomb,
            [
                "* Lápida de MUTT.",
                "* 'El perro más fiel. Siempre un buen chico.'",
                "* Hay un hueso tallado en la piedra y una pequeña pelota roja descansando a sus pies."
            ]
        ))

        # 11. Lápida del Poeta Olvidado
        def draw_poet_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (86, 88, 98), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (64, 66, 76), (cx, cy, w, h), 1, border_radius=4)
            # Libro abierto y pluma tallada
            pygame.draw.rect(surf, (215, 210, 195), (cx + w//2 - 8, cy + 10, 7, 10))
            pygame.draw.rect(surf, (215, 210, 195), (cx + w//2 + 1, cy + 10, 7, 10))
            pygame.draw.line(surf, (150, 140, 120), (cx + w//2, cy + 10), (cx + w//2, cy + 20), 1)
            pygame.draw.line(surf, (190, 175, 120), (cx + w - 10, cy + 8), (cx + w - 4, cy + 22), 1)
        self.world_objects.append(InteriorProp(
            520, 420, 38, 46, 468, draw_poet_tomb,
            [
                "* Lápida con un libro abierto grabado en la piedra.",
                "* 'No llores ante mi lápida, viajero. No estoy allí... yo nunca duermo.'",
                "* Un suave suspiro parece acariciar las hojas marchitas a tu alrededor."
            ]
        ))

        # 12. Tumba Abierta (La de Paniel con consciencia de muertes)
        def draw_open_grave(surf, cx, cy, w, h):
            # Fosa profunda y oscura
            pygame.draw.rect(surf, (12, 8, 7), (cx + 4, cy + 20, w - 8, h - 20), border_radius=2)
            # Tablones de apuntalamiento
            pygame.draw.line(surf, (85, 60, 40), (cx + 6, cy + 22), (cx + w - 6, cy + 22), 2)
            pygame.draw.line(surf, (85, 60, 40), (cx + 6, cy + 34), (cx + w - 6, cy + 34), 2)
            # Montículo de tierra removida
            pygame.draw.polygon(surf, (58, 44, 34), [(cx, cy + 24), (cx + w//2, cy + 14), (cx + w, cy + 24)])
            # Lápida inclinada
            pygame.draw.rect(surf, (84, 86, 96), (cx + w//2 - 12, cy, 24, 28), border_radius=3)
            pygame.draw.rect(surf, (60, 62, 72), (cx + w//2 - 12, cy, 24, 28), 1, border_radius=3)
            # Pala oxidada clavada
            pygame.draw.line(surf, (115, 90, 60), (cx + w - 6, cy + 5), (cx + w + 2, cy + 32), 2)
            pygame.draw.rect(surf, (95, 75, 50), (cx + w - 8, cy + 2, 10, 6))
            # Velón encendido junto a la fosa
            pygame.draw.circle(surf, (255, 200, 70), (cx + 2, cy + 24), 2)
        self.world_objects.append(InteriorProp(
            640, 390, 54, 46, 438, draw_open_grave,
            None,
            is_solid=False
        ))
        self._open_grave_obj = self.world_objects[-1]
        self._open_grave_obj.interactable = True
        self._open_grave_obj._is_open_grave = True

        # 13. Punto de Guardado (Estrella de Determinación en el Cruce de Caminos)
        self.world_objects.append(SavePointObject(x=390, y=336))

        # ==========================================================
        # COLISIONES SÓLIDAS
        # ==========================================================
        self.solid_rects.append(pygame.Rect(0, 76, 800, 24))         # Muro superior
        self.solid_rects.append(pygame.Rect(0, 76, 24, 524))         # Muro izquierdo
        self.solid_rects.append(pygame.Rect(776, 76, 24, 524))       # Muro derecho
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))        # Muro inferior izq
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))      # Muro inferior der
        # Laterales del Mausoleo dejando libre el vano central (x=378..422) para entrar al Abismo
        self.solid_rects.append(pygame.Rect(328, 64, 50, 86))
        self.solid_rects.append(pygame.Rect(422, 64, 50, 86))
        self.solid_rects.append(pygame.Rect(378, 64, 44, 70))

    # ==========================================================
    # 3. PARTE MÁS PROFUNDA DEL CEMENTERIO: ABISMO DEL CEMENTERIO (ZONA DEL JEFE)
    # ==========================================================
    def _build_cemetery_depths(self):
        s = self.surface
        # Suelo abismal de obsidiana y ceniza oscura
        s.fill((12, 10, 18))

        # 1. CIELO DEL ABISMO CON ECLIPSE CARMESÍ Y FUENTE OSCURA
        for y in range(84):
            t = y / 84.0
            r = int(28 - 14 * t)
            g = int(6 + 6 * t)
            b = int(32 + 12 * t)
            pygame.draw.line(s, (r, g, b), (0, y), (800, y))

        # Columna de la Fuente Oscura surgiendo tras el Altar Norte (x=370..430)
        for layer_w, col in [(68, (32, 14, 48)), (44, (65, 20, 72)), (24, (135, 35, 90)), (10, (235, 80, 120))]:
            pygame.draw.rect(s, col, (400 - layer_w // 2, 0, layer_w, 84))

        # Luna de Eclipse Carmesí a la izquierda del horizonte
        ec_x, ec_y = 180, 38
        for rad, alpha in [(42, 22), (28, 55), (20, 110)]:
            halo = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo, (235, 50, 80, alpha), (rad, rad), rad)
            s.blit(halo, (ec_x - rad, ec_y - rad))
        pygame.draw.circle(s, (255, 95, 115), (ec_x, ec_y), 15, 2)
        pygame.draw.circle(s, (10, 6, 16), (ec_x, ec_y), 13)

        # Estrellas carmesí y violetas en la bóveda
        random.seed(77)
        for _ in range(85):
            sx = random.randint(0, 799)
            sy = random.randint(4, 78)
            c = random.choice([(255, 140, 160), (200, 160, 255), (255, 220, 190)])
            s.set_at((sx, sy), c)

        # 2. MUROS PERIMETRALES DE OBSIDIANA Y REJAS DEL ABISMO
        for bx in range(0, 800, 24):
            sh = random.randint(46, 58)
            pygame.draw.rect(s, (sh, sh - 6, sh + 10), (bx, 80, 24, 24))
            pygame.draw.rect(s, (24, 18, 32), (bx, 80, 24, 24), 1)
            pygame.draw.line(s, (165, 45, 75), (bx + 12, 66), (bx + 12, 80), 2)

        for by in range(80, 600, 20):
            sh = random.randint(46, 58)
            pygame.draw.rect(s, (sh, sh - 6, sh + 10), (0, by, 24, 20))
            pygame.draw.rect(s, (24, 18, 32), (0, by, 24, 20), 1)
            pygame.draw.rect(s, (sh, sh - 6, sh + 10), (776, by, 24, 20))
            pygame.draw.rect(s, (24, 18, 32), (776, by, 24, 20), 1)

        # Muro inferior con portal de regreso al Cementerio (x=370..430)
        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            sh = random.randint(46, 58)
            pygame.draw.rect(s, (sh, sh - 6, sh + 10), (bx, 576, 24, 24))
            pygame.draw.rect(s, (24, 18, 32), (bx, 576, 24, 24), 1)

        # Pilares del portal sur
        pygame.draw.rect(s, (120, 40, 65), (364, 566, 8, 34), border_radius=2)
        pygame.draw.rect(s, (120, 40, 65), (428, 566, 8, 34), border_radius=2)

        # 3. GRAN PUENTE REAL DE OBSIDIANA Y PLAZA CIRCULAR DEL JEFE
        # Plaza Circular del Osario (centro en 400, 240, radio 148)
        pygame.draw.circle(s, (26, 20, 36), (400, 240), 152)
        pygame.draw.circle(s, (150, 42, 72), (400, 240), 152, 3)
        pygame.draw.circle(s, (34, 26, 46), (400, 240), 124)
        pygame.draw.circle(s, (95, 40, 85), (400, 240), 124, 2)

        # Emblema Delta Rune carmesí grabado en el centro de la arena del Jefe
        pygame.draw.circle(s, (185, 50, 85), (400, 240), 46, 2)
        for dx, dy in [(-24, 18), (24, 18), (0, -22)]:
            tri = [(400 + dx, 240 + dy - 10), (400 + dx - 10, 240 + dy + 8), (400 + dx + 10, 240 + dy + 8)]
            pygame.draw.polygon(s, (165, 45, 78), tri, 2)

        # Calzada procesional desde la entrada sur (y=380..580) hasta la plaza del Jefe
        for gy in range(375, 580, 14):
            for gx in range(368, 432, 16):
                sh = random.randint(44, 56)
                pygame.draw.rect(s, (sh, sh - 6, sh + 12), (gx, gy, 15, 13), border_radius=2)
                pygame.draw.rect(s, (24, 18, 34), (gx, gy, 15, 13), 1, border_radius=2)
            # Alfombra/runa carmesí central
            pygame.draw.rect(s, (125, 28, 52), (392, gy, 16, 13))

        # Grietas luminosas de energía del Dark World en el suelo
        for cx1, cy1, cx2, cy2 in [
            (120, 180, 175, 210), (680, 185, 625, 215),
            (140, 420, 210, 450), (660, 420, 590, 455),
        ]:
            pygame.draw.line(s, (195, 45, 85), (cx1, cy1), (cx2, cy2), 2)
            pygame.draw.line(s, (255, 160, 190), (cx1, cy1), ((cx1 + cx2) // 2, (cy1 + cy2) // 2), 1)

        # 4. PORTAL DE CRISTAL QUEBRADO EN EL ALTAR NORTE (Hacia el Santuario del Cristal Quebrado)
        pygame.draw.rect(s, (48, 38, 62), (344, 118, 112, 18), border_radius=2)
        pygame.draw.rect(s, (62, 48, 78), (354, 108, 92, 12), border_radius=2)
        portal_arch = [(368, 118), (364, 62), (384, 72), (400, 48), (416, 72), (436, 62), (432, 118)]
        pygame.draw.polygon(s, (18, 8, 28), portal_arch)
        pygame.draw.polygon(s, (235, 45, 95), portal_arch, 2)
        pygame.draw.polygon(s, (0, 0, 0), portal_arch, 1)
        # Vórtice de cristal quebrado y fuego oscuro en el umbral norte (x=378..422, y=72..118)
        pygame.draw.rect(s, (8, 2, 16), (378, 74, 44, 44), border_radius=4)
        pygame.draw.rect(s, (235, 40, 90), (378, 74, 44, 44), 2, border_radius=4)
        pygame.draw.line(s, (255, 220, 245), (382, 78), (416, 112), 2)
        pygame.draw.line(s, (255, 220, 245), (416, 80), (384, 110), 1)

        # Rectángulo de transición hacia la nueva zona más difícil (Santuario del Cristal Quebrado)
        self.sanctuary_gate_rect = pygame.Rect(376, 82, 48, 44)

        # ==========================================================
        # OBJETOS INTERACTIVOS Y AMBIENTALES DEL ABISMO
        # ==========================================================
        # Punto de Guardado y Cofre antes del combate contra el Jefe
        self.world_objects.append(SavePointObject(x=326, y=448))
        self.world_objects.append(ChestObject(x=452, y=448))

        # Cartel de advertencia antes de la Plaza del Jefe y el Portal Norte
        self.world_objects.append(SignObject(
            x=342, y=388,
            message="* INSCRIPCIÓN CARMESÍ: 'Al norte del altar se abre la Grieta de Cristal hacia el Santuario del Rey Vaelkor.'"
        ))

        # Pilares góticos rodeando el anillo del Jefe
        for px, py in [(225, 160), (555, 160), (215, 290), (565, 290), (310, 495), (470, 495)]:
            self.world_objects.append(RuinPillar(px, py))

        # Árboles retorcidos con faroles en las esquinas del abismo
        for tx, ty in [(64, 150), (680, 150), (64, 440), (680, 440)]:
            self.world_objects.append(TwistedTreeProp(tx, ty, has_lantern=True))

        # Ánimas carmesí y violetas flotando alrededor de la plaza
        for wx, wy, wcol in [
            (265, 195, (255, 95, 125)),
            (535, 195, (255, 95, 125)),
            (265, 295, (195, 125, 255)),
            (535, 295, (195, 125, 255)),
            (345, 520, (130, 235, 255)),
            (455, 520, (130, 235, 255)),
        ]:
            self.world_objects.append(WillOWisp(wx, wy, color=wcol))

        # Colisiones perimetrales del Abismo (dejando abierto el portal norte x=374..426 hacia el Santuario)
        self.solid_rects.append(pygame.Rect(0, 80, 374, 24))
        self.solid_rects.append(pygame.Rect(426, 80, 374, 24))
        self.solid_rects.append(pygame.Rect(374, 56, 52, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))

    # ==========================================================
    # 4. NUEVA ZONA EXTREMA: SANTUARIO DEL CRISTAL QUEBRADO (JEFE SUPREMO VAELKOR)
    # ==========================================================
    def _build_eclipse_sanctuary(self):
        s = self.surface
        s.fill((7, 4, 14))

        # 1. BÓVEDA CÓSMICA CON CRISTAL ROTO Y COLUMNAS DE FUEGO OSCURO
        for y in range(86):
            t = y / 86.0
            pygame.draw.line(s, (int(18 - 10 * t), int(3 + 4 * t), int(26 + 10 * t)), (0, y), (800, y))

        # Columnas gemelas de Fuego Oscuro con borde negro al fondo
        for fx in (230, 400, 570):
            pygame.draw.rect(s, (0, 0, 0), (fx - 26, 0, 52, 86))
            pygame.draw.rect(s, (38, 6, 54), (fx - 22, 0, 44, 86))
            pygame.draw.rect(s, (215, 28, 82), (fx - 12, 0, 24, 86))
            pygame.draw.rect(s, (15, 2, 24), (fx - 5, 0, 10, 86))

        # Grietas de cristal quebrado en el cielo del Santuario
        sky_cracks = [
            [(90, 12), (145, 36), (125, 62), (185, 74)],
            [(620, 14), (665, 40), (640, 64), (710, 76)],
            [(310, 10), (355, 32), (340, 58)],
            [(490, 12), (445, 34), (465, 60)],
        ]
        for pts in sky_cracks:
            pygame.draw.lines(s, (0, 0, 0), False, pts, 5)
            pygame.draw.lines(s, (235, 35, 90), False, pts, 3)
            pygame.draw.lines(s, (255, 230, 245), False, pts, 1)

        # Muros perimetrales de cristal negro con púas carmesí
        for bx in range(0, 800, 24):
            pygame.draw.rect(s, (24, 14, 36), (bx, 80, 24, 24))
            pygame.draw.rect(s, (0, 0, 0), (bx, 80, 24, 24), 2)
            pygame.draw.polygon(s, (220, 35, 85), [(bx + 6, 80), (bx + 12, 64), (bx + 18, 80)])
            pygame.draw.polygon(s, (0, 0, 0), [(bx + 6, 80), (bx + 12, 64), (bx + 18, 80)], 1)

        for by in range(80, 600, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (24, 14, 36), (mx, by, 24, 20))
                pygame.draw.rect(s, (0, 0, 0), (mx, by, 24, 20), 2)

        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (24, 14, 36), (bx, 576, 24, 24))
            pygame.draw.rect(s, (0, 0, 0), (bx, 576, 24, 24), 2)

        # 2. PLAZA OCTOGONAL DEL CRISTAL QUEBRADO (ARENA DEL JEFE SUPREMO VAELKOR)
        cx, cy = 400, 235
        oct_outer = [(cx + int(math.cos(a) * 165), cy + int(math.sin(a) * 145)) for a in [i * math.pi / 4 for i in range(8)]]
        oct_inner = [(cx + int(math.cos(a) * 125), cy + int(math.sin(a) * 110)) for a in [i * math.pi / 4 for i in range(8)]]
        pygame.draw.polygon(s, (20, 10, 32), oct_outer)
        pygame.draw.polygon(s, (0, 0, 0), oct_outer, 4)
        pygame.draw.polygon(s, (235, 35, 90), oct_outer, 2)
        pygame.draw.polygon(s, (28, 14, 44), oct_inner)
        pygame.draw.polygon(s, (185, 35, 85), oct_inner, 2)

        # Estrella de Cristal Quebrado grabada en el centro (con borde negro y núcleo carmesí)
        for i in range(8):
            ang = i * (math.pi / 4.0)
            ex = cx + int(math.cos(ang) * 95)
            ey = cy + int(math.sin(ang) * 82)
            pygame.draw.line(s, (0, 0, 0), (cx, cy), (ex, ey), 5)
            pygame.draw.line(s, (235, 35, 90), (cx, cy), (ex, ey), 2)
            pygame.draw.line(s, (255, 225, 245), (cx, cy), ((cx + ex) // 2, (cy + ey) // 2), 1)

        # Calzada de cristal oscuro desde la entrada sur (y=375..580)
        for gy in range(375, 580, 14):
            pygame.draw.rect(s, (26, 14, 40), (366, gy, 68, 13))
            pygame.draw.rect(s, (0, 0, 0), (366, gy, 68, 13), 1)
            pygame.draw.rect(s, (215, 30, 80), (392, gy, 16, 13))

        # Monolito del Cristal Negro al norte (x=360..440, y=72..126)
        throne_crystal = [(368, 120), (356, 76), (382, 86), (400, 52), (418, 86), (444, 76), (432, 120)]
        pygame.draw.polygon(s, (16, 6, 26), throne_crystal)
        pygame.draw.polygon(s, (0, 0, 0), throne_crystal, 4)
        pygame.draw.polygon(s, (245, 40, 95), throne_crystal, 2)

        self.world_objects.append(InteriorProp(
            364, 72, 72, 52, 126,
            lambda surf, x, y, w, h: None,
            [
                "* El Monolito del Cristal Quebrado, trono de Vaelkor.",
                "* Las llamas oscuras con borde negro parecen cortar el espacio mismo.",
            ],
            is_solid=True,
        ))

        # Punto de Guardado, Cofre y Cartel antes del Jefe Supremo
        self.world_objects.append(SavePointObject(x=326, y=452))
        self.world_objects.append(ChestObject(x=452, y=452))
        self.world_objects.append(SignObject(
            x=342, y=392,
            message="* SANTUARIO DEL CRISTAL QUEBRADO: 'Aquí aguarda Vaelkor, Rey del Cristal Negro. ¡Usa tu habilidad BlackFlash (50% TP) para romper su guardia!'",
        ))

        for px, py in [(205, 155), (575, 155), (195, 295), (585, 295), (305, 495), (475, 495)]:
            self.world_objects.append(RuinPillar(px, py))

        for wx, wy, wcol in [
            (250, 185, (255, 45, 100)),
            (550, 185, (255, 45, 100)),
            (250, 295, (195, 80, 255)),
            (550, 295, (195, 80, 255)),
            (345, 520, (255, 70, 120)),
            (455, 520, (255, 70, 120)),
        ]:
            self.world_objects.append(WillOWisp(wx, wy, color=wcol))

        self.solid_rects.append(pygame.Rect(0, 80, 800, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))


