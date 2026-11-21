import os
import math
import random
import pygame
from configuracion import VIRTUAL_WIDTH, VIRTUAL_HEIGHT
from objetos_mundo import SavePointObject, SignObject, ChestObject, RuinPillar, WillOWisp, TwistedTreeProp, InteriorProp, DarkWorldVendorNPC

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
        elif self.scene_id == "cemetery_church_section":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(0, 314, 28, 64)
            self._build_cemetery_church_section()
        elif self.scene_id == "church":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_church()
        elif self.scene_id == "church_basement":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_church_basement()
        elif self.scene_id == "dark_world":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_dark_world()
        elif self.scene_id == "tutorial_grounds":
            self.pixel_w = 800
            self.pixel_h = 900
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self._build_tutorial_grounds()

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

        # MARCO DE LA PUERTA DEL CEMENTERIO (x=234..266, y=368..402)
        self.cemetery_gate_rect = pygame.Rect(234, 368, 32, 34)

        # Pedestales simétricos de piedra en la acera para el Cartel (izquierda) y el Punto de Guardado (derecha)
        s = self.surface
        for ped_x in (156, 316):
            pygame.draw.rect(s, (58, 62, 72), (ped_x, 402, 32, 26), border_radius=4)
            pygame.draw.rect(s, (98, 106, 122), (ped_x, 402, 32, 26), 1, border_radius=4)

        # Punto de guardado en el pedestal derecho de la acera
        self.world_objects.append(SavePointObject(x=322, y=406))

        # Cartel del cementerio en el pedestal izquierdo de la acera
        self.world_objects.append(SignObject(
            x=164, y=406,
            message="* CARTEL DE HIERRO: 'CEMENTERIO DE HOMETOWN. Al este dentro del cementerio: Nueva Sección de la Iglesia.'"
        ))

        # Faroles espectrales simétricos flanqueando la puerta principal
        self.world_objects.append(WillOWisp(214, 386, color=(135, 225, 255)))
        self.world_objects.append(WillOWisp(286, 386, color=(135, 225, 255)))

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

        # 4. CAMINOS DE ADOQUINES ORGANIZADOS CON BORDILLOS Y 4 SECTORES SIMÉTRICOS
        def draw_paved_avenue(rx, ry, rw, rh):
            pygame.draw.rect(s, (46, 48, 56), (rx - 3, ry - 3, rw + 6, rh + 6), border_radius=4)
            pygame.draw.rect(s, (104, 108, 122), (rx - 3, ry - 3, rw + 6, rh + 6), 2, border_radius=4)
            for gy in range(ry, ry + rh, 14):
                for gx in range(rx, rx + rw, 16):
                    cw = min(15, rx + rw - gx)
                    ch = min(13, ry + rh - gy)
                    if cw > 2 and ch > 2:
                        shade = random.randint(64, 78)
                        pygame.draw.rect(s, (shade, shade - 3, shade + 3), (gx, gy, cw, ch), border_radius=2)
                        pygame.draw.rect(s, (38, 38, 44), (gx, gy, cw, ch), 1, border_radius=2)

        def draw_monument_plot(px, py, pw, ph):
            """Dibuja una parcela de piedra delimitada con bordillo gótico para organizar cada tumba o monumento."""
            pygame.draw.rect(s, (28, 34, 32), (px, py, pw, ph), border_radius=4)
            pygame.draw.rect(s, (88, 92, 106), (px, py, pw, ph), 2, border_radius=4)
            pygame.draw.rect(s, (42, 44, 52), (px + 2, py + 2, pw - 4, ph - 4), 1, border_radius=3)

        # Avenidas Principales y Senderos Simétricos de los 4 Claustros:
        # 1) Gran Avenida Transversal Este-Oeste (y=326..366)
        draw_paved_avenue(28, 326, 744, 40)
        # 2) Sendero Norte Este-Oeste (Sector de los Héroes y la Memoria, y=212..236)
        draw_paved_avenue(84, 212, 632, 24)
        # 3) Sendero Sur Este-Oeste (Claustros del Silencio y de los Olvidados, y=462..486)
        draw_paved_avenue(84, 462, 632, 24)
        # 4) Gran Avenida Central Norte-Sur (x=372..428, y=148..576)
        draw_paved_avenue(372, 148, 56, 428)

        # Plaza Octogonal Central en el Cruce de Caminos (alrededor del Punto de Guardado)
        pygame.draw.circle(s, (54, 56, 66), (400, 346), 42)
        pygame.draw.circle(s, (120, 126, 142), (400, 346), 42, 2)
        pygame.draw.circle(s, (72, 74, 86), (400, 346), 32)
        pygame.draw.circle(s, (175, 165, 110), (400, 346), 32, 1)

        # Parcelas simétricas de piedra para cada cripta, tumba y monumento:
        # Sector Noroeste (Cripta Pioneros, Gerson, Crystal)
        draw_monument_plot(64, 98, 72, 60)
        draw_monument_plot(162, 152, 56, 58)
        draw_monument_plot(250, 152, 54, 58)
        # Sector Noreste (Fuente de la Memoria, Mutt, Cripta Guardia Real)
        draw_monument_plot(494, 148, 66, 62)
        draw_monument_plot(584, 152, 52, 58)
        draw_monument_plot(664, 98, 72, 60)
        # Sector Suroeste (Cruz Celta, Ángel del Silencio)
        draw_monument_plot(102, 396, 50, 64)
        draw_monument_plot(214, 396, 56, 64)
        # Sector Sureste (Poeta Olvidado, Tumba Abierta)
        draw_monument_plot(516, 398, 54, 62)
        draw_monument_plot(624, 398, 66, 62)

        # Charcos de agua simétricos con reflejos nocturnos en los adoquines
        puddles = [
            (388, 492, 24, 10),
            (388, 268, 22, 9),
            (220, 340, 26, 10),
            (554, 340, 26, 10),
        ]
        for px, py, pw, ph in puddles:
            pygame.draw.ellipse(s, (28, 42, 60), (px, py, pw, ph))
            pygame.draw.ellipse(s, (45, 65, 90), (px + 2, py + 1, pw - 4, ph - 2), 1)
            pygame.draw.line(s, (180, 210, 255), (px + 4, py + 2), (px + pw - 6, py + 2), 1)

        # Flores doradas y celestes ordenadas junto a los bordillos de las parcelas
        for fx, fy in [(152, 204), (242, 204), (362, 520), (438, 520)]:
            pygame.draw.circle(s, (245, 215, 60), (fx, fy), 3)
            pygame.draw.circle(s, (255, 245, 140), (fx, fy), 1)
            pygame.draw.line(s, (45, 110, 50), (fx, fy + 1), (fx, fy + 4), 1)

        for fx, fy in [(312, 204), (484, 204), (572, 204), (646, 204)]:
            pygame.draw.circle(s, (90, 160, 245), (fx, fy), 3)
            pygame.draw.circle(s, (210, 235, 255), (fx, fy), 1)

        # Hongos bioluminiscentes en las 4 esquinas del jardín
        for hx, hy in [(50, 280), (746, 280), (50, 540), (746, 540)]:
            pygame.draw.circle(s, (80, 240, 210), (hx, hy), 2)
            pygame.draw.circle(s, (180, 110, 255), (hx + 4, hy + 3), 2)

        # Niebla baja mágica con capas onduladas
        for fy in [310, 430, 530]:
            fog = pygame.Surface((800, 22), pygame.SRCALPHA)
            fog.fill((160, 190, 215, 18))
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
            x=336, y=156,
            message="* CARTEL DEL PANTEÓN: 'Gran Mausoleo Ancestral. Custodiado por Morvath, el Sepulturero Eterno.'"
        ))

        # 1. Árboles góticos antiguos organizados simétricamente en los 4 cuadrantes
        self.world_objects.append(TwistedTreeProp(40, 236, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(306, 236, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(442, 236, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(708, 236, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(40, 488, has_lantern=False))
        self.world_objects.append(TwistedTreeProp(708, 488, has_lantern=False))

        # 2. Fuegos fatuos / Ánimas danzantes alineadas simétricamente en los cruces
        self.world_objects.append(WillOWisp(346, 200, color=(140, 255, 210)))
        self.world_objects.append(WillOWisp(454, 200, color=(140, 255, 210)))
        self.world_objects.append(WillOWisp(346, 346, color=(130, 235, 255)))
        self.world_objects.append(WillOWisp(454, 346, color=(130, 235, 255)))
        self.world_objects.append(WillOWisp(346, 474, color=(195, 160, 255)))
        self.world_objects.append(WillOWisp(454, 474, color=(195, 160, 255)))

        # 3. Estatua del Ángel del Silencio (Sector Suroeste - Parcela derecha)
        def draw_angel_statue(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (80, 82, 92), (cx + 4, cy + 34, w - 8, 18), border_radius=2)
            pygame.draw.rect(surf, (60, 62, 70), (cx + 4, cy + 34, w - 8, 18), 1, border_radius=2)
            pygame.draw.polygon(surf, (98, 100, 112), [(cx + w//2, cy + 12), (cx + 8, cy + 34), (cx + w - 8, cy + 34)])
            pygame.draw.circle(surf, (110, 112, 124), (cx + w//2, cy + 10), 6)
            pygame.draw.polygon(surf, (120, 124, 138), [(cx + w//2 - 2, cy + 14), (cx + 2, cy + 6), (cx + 6, cy + 26)])
            pygame.draw.polygon(surf, (120, 124, 138), [(cx + w//2 + 2, cy + 14), (cx + w - 2, cy + 6), (cx + w - 6, cy + 26)])
            pygame.draw.rect(surf, (240, 235, 215), (cx + 6, cy + 30, 3, 5))
            pygame.draw.circle(surf, (255, 210, 80), (cx + 7, cy + 28), 2)
            pygame.draw.rect(surf, (240, 235, 215), (cx + w - 9, cy + 30, 3, 5))
            pygame.draw.circle(surf, (255, 210, 80), (cx + w - 8, cy + 28), 2)
        self.world_objects.append(InteriorProp(
            222, 402, 40, 52, 456, draw_angel_statue,
            [
                "* Monumento del Ángel del Silencio.",
                "* 'Para aquellos cuyas voces se apagaron pacíficamente en la noche.'",
                "* Pequeñas velas titilan a sus pies, arrojando sombras danzantes sobre el musgo.",
                "* (Sientes una caricia tibia que calma tu espíritu. +15 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 15

        # 4. Cruz Celta de Piedra Antigua (Sector Suroeste - Parcela izquierda)
        def draw_celtic_cross(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (78, 80, 88), (cx + 4, cy + 36, w - 8, 14), border_radius=2)
            pygame.draw.rect(surf, (58, 60, 68), (cx + 4, cy + 36, w - 8, 14), 1, border_radius=2)
            pygame.draw.rect(surf, (92, 94, 104), (cx + w//2 - 3, cy + 4, 6, 34), border_radius=1)
            pygame.draw.rect(surf, (92, 94, 104), (cx + 6, cy + 14, 22, 6), border_radius=1)
            pygame.draw.circle(surf, (110, 114, 126), (cx + w//2, cy + 17), 10, 2)
            pygame.draw.circle(surf, (60, 95, 65), (cx + w//2 - 1, cy + 16), 2)
        self.world_objects.append(InteriorProp(
            110, 404, 34, 50, 456, draw_celtic_cross,
            [
                "* Antigua Cruz Celta de Piedra.",
                "* Los grabados entrelazados representan la eternidad del alma y el ciclo sin fin.",
                "* El viento nocturno silba una melodía melancólica a través del círculo de piedra."
            ]
        ))

        # 5. Entrada a la Antigua Cripta de los Pioneros (Sector Noroeste)
        def draw_old_crypt(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (70, 72, 82), (cx, cy + 8, w, h - 8), border_radius=3)
            pygame.draw.rect(surf, (48, 50, 58), (cx, cy + 8, w, h - 8), 2, border_radius=3)
            pygame.draw.polygon(surf, (84, 86, 96), [(cx + w//2, cy), (cx - 2, cy + 8), (cx + w + 2, cy + 8)])
            pygame.draw.rect(surf, (14, 14, 18), (cx + 12, cy + 18, w - 24, h - 18), border_radius=2)
            for gx in range(cx + 16, cx + w - 16, 6):
                pygame.draw.line(surf, (65, 68, 78), (gx, cy + 18), (gx, cy + h - 1), 1)
            pygame.draw.line(surf, (65, 68, 78), (cx + 12, cy + 32), (cx + w - 13, cy + 32), 1)
        self.world_objects.append(InteriorProp(
            70, 102, 60, 52, 156, draw_old_crypt,
            [
                "* Entrada a la Antigua Cripta Familiar.",
                "* 'Aquí yacen los pioneros que fundaron el valle.'",
                "* El aire que sube desde los escalones de piedra es gélido como la escarcha."
            ]
        ))

        # 6. Lápida de Gerson Boom (Sector Noroeste - Parcela central)
        def draw_gerson_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (94, 96, 106), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (68, 70, 80), (cx, cy, w, h), 1, border_radius=4)
            pygame.draw.rect(surf, (155, 120, 75), (cx + w//2 - 2, cy + 8, 4, 16))
            pygame.draw.rect(surf, (170, 140, 95), (cx + w//2 - 8, cy + 8, 16, 6))
            pygame.draw.circle(surf, (230, 220, 200), (cx + 6, cy + h - 5), 3)
            pygame.draw.circle(surf, (245, 215, 60), (cx + w - 8, cy + h - 5), 3)
        self.world_objects.append(InteriorProp(
            168, 156, 44, 48, 206, draw_gerson_tomb,
            [
                "* Lápida de GERSON BOOM, el Martillo de la Justicia.",
                "* 'Aquí descansa el viejo historiador que lo vio todo.'",
                "* Una profunda corriente de serenidad y determinación emana de esta piedra.",
                "* (Tu corazón se llena de paz inmutable. +20 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 20

        # 7. Lápida de Crystal (Sector Noroeste - Parcela derecha)
        def draw_crystal_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (96, 102, 118), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (72, 78, 94), (cx, cy, w, h), 1, border_radius=4)
            pygame.draw.arc(surf, (180, 210, 245), (cx + 4, cy + 4, 16, 18), 0, math.pi, 2)
            pygame.draw.arc(surf, (180, 210, 245), (cx + w - 20, cy + 4, 16, 18), 0, math.pi, 2)
            for fi, (fx, fy) in enumerate([(cx + 8, cy + 34), (cx + 20, cy + 31), (cx + 32, cy + 35)]):
                pygame.draw.circle(surf, (80, 150, 250), (fx, fy), 4)
                pygame.draw.circle(surf, (215, 235, 255), (fx, fy), 2)
        self.world_objects.append(InteriorProp(
            256, 156, 42, 48, 206, draw_crystal_tomb,
            [
                "* Lápida de CRYSTAL.",
                "* Flores celestes frescas adornan su base. Alguien las puso hace pocas horas.",
                "* (El aroma floral disipa tu terror y refresca tu mente. +20 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 20

        # 8. Cripta de la Antigua Guardia Real (Sector Noreste - Simétrica a la Cripta de los Pioneros)
        def draw_guard_crypt(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (76, 78, 88), (cx, cy + 8, w, h - 8), border_radius=3)
            pygame.draw.rect(surf, (52, 54, 62), (cx, cy + 8, w, h - 8), 2, border_radius=3)
            pygame.draw.polygon(surf, (90, 92, 104), [(cx + w//2, cy), (cx - 2, cy + 8), (cx + w + 2, cy + 8)])
            pygame.draw.rect(surf, (180, 185, 200), (cx + w//2 - 6, cy + 18, 12, 14), border_radius=1)
            pygame.draw.line(surf, (210, 215, 230), (cx + 14, cy + 14), (cx + w - 14, cy + 36), 2)
            pygame.draw.line(surf, (210, 215, 230), (cx + w - 14, cy + 14), (cx + 14, cy + 36), 2)
        self.world_objects.append(InteriorProp(
            670, 102, 60, 52, 156, draw_guard_crypt,
            [
                "* Cripta de la Antigua Guardia Real.",
                "* 'Su honor fue su escudo; su deber, su vida.'",
                "* Dos espadas de piedra descansan cruzadas sobre el frontón esculpido."
            ]
        ))

        # 9. Fuente de la Memoria (Sector Noreste - Parcela izquierda)
        def draw_fountain(surf, cx, cy, w, h):
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
            pygame.draw.ellipse(surf, (30, 60, 95), (cx + 6, cy + 8, w - 12, h - 16))
            pygame.draw.ellipse(surf, (60, 110, 160), (cx + 10, cy + 12, w - 20, h - 24), 1)
            pygame.draw.circle(surf, (200, 230, 255), (cx + w//2 - 6, cy + h//2 - 2), 2)
            pygame.draw.circle(surf, (200, 230, 255), (cx + w//2 + 8, cy + h//2 + 3), 1)
            pygame.draw.rect(surf, (90, 95, 105), (cx + w//2 - 4, cy + 12, 8, 16), border_radius=1)
            pygame.draw.circle(surf, (110, 115, 128), (cx + w//2, cy + 10), 4)
        self.world_objects.append(InteriorProp(
            500, 154, 54, 50, 206, draw_fountain,
            [
                "* La Fuente de la Memoria.",
                "* El agua cristalina refleja el brillo de las estrellas y la luna llena.",
                "* Te enjuagas la cara con el agua helada. Te sientes renovado. (+15 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 15

        # 10. Lápida de Mutt (Sector Noreste - Parcela central)
        def draw_mutt_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (94, 92, 102), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (72, 70, 80), (cx, cy, w, h), 1, border_radius=4)
            pygame.draw.rect(surf, (230, 225, 210), (cx + w//2 - 8, cy + 12, 16, 5))
            pygame.draw.circle(surf, (230, 225, 210), (cx + w//2 - 8, cy + 14), 4)
            pygame.draw.circle(surf, (230, 225, 210), (cx + w//2 + 8, cy + 14), 4)
            pygame.draw.circle(surf, (220, 50, 50), (cx + 8, cy + h - 5), 4)
        self.world_objects.append(InteriorProp(
            590, 156, 40, 48, 206, draw_mutt_tomb,
            [
                "* Lápida de MUTT.",
                "* 'El perro más fiel. Siempre un buen chico.'",
                "* Hay un hueso tallado en la piedra y una pequeña pelota roja descansando a sus pies."
            ]
        ))

        # 11. Lápida del Poeta Olvidado (Sector Sureste - Parcela izquierda)
        def draw_poet_tomb(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (86, 88, 98), (cx, cy, w, h), border_radius=4)
            pygame.draw.rect(surf, (64, 66, 76), (cx, cy, w, h), 1, border_radius=4)
            pygame.draw.rect(surf, (215, 210, 195), (cx + w//2 - 8, cy + 10, 7, 10))
            pygame.draw.rect(surf, (215, 210, 195), (cx + w//2 + 1, cy + 10, 7, 10))
            pygame.draw.line(surf, (150, 140, 120), (cx + w//2, cy + 10), (cx + w//2, cy + 20), 1)
            pygame.draw.line(surf, (190, 175, 120), (cx + w - 10, cy + 8), (cx + w - 4, cy + 22), 1)
        self.world_objects.append(InteriorProp(
            524, 406, 38, 46, 456, draw_poet_tomb,
            [
                "* Lápida con un libro abierto grabado en la piedra.",
                "* 'No llores ante mi lápida, viajero. No estoy allí... yo nunca duermo.'",
                "* Un suave suspiro parece acariciar las hojas marchitas a tu alrededor."
            ]
        ))

        # 12. Tumba Abierta (Sector Sureste - Parcela derecha)
        def draw_open_grave(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (12, 8, 7), (cx + 4, cy + 20, w - 8, h - 20), border_radius=2)
            pygame.draw.line(surf, (85, 60, 40), (cx + 6, cy + 22), (cx + w - 6, cy + 22), 2)
            pygame.draw.line(surf, (85, 60, 40), (cx + 6, cy + 34), (cx + w - 6, cy + 34), 2)
            pygame.draw.polygon(surf, (58, 44, 34), [(cx, cy + 24), (cx + w//2, cy + 14), (cx + w, cy + 24)])
            pygame.draw.rect(surf, (84, 86, 96), (cx + w//2 - 12, cy, 24, 28), border_radius=3)
            pygame.draw.rect(surf, (60, 62, 72), (cx + w//2 - 12, cy, 24, 28), 1, border_radius=3)
            pygame.draw.line(surf, (115, 90, 60), (cx + w - 6, cy + 5), (cx + w + 2, cy + 32), 2)
            pygame.draw.rect(surf, (95, 75, 50), (cx + w - 8, cy + 2, 10, 6))
            pygame.draw.circle(surf, (255, 200, 70), (cx + 2, cy + 24), 2)
        self.world_objects.append(InteriorProp(
            630, 406, 54, 46, 456, draw_open_grave,
            None,
            is_solid=False
        ))
        self._open_grave_obj = self.world_objects[-1]
        self._open_grave_obj.interactable = True
        self._open_grave_obj._is_open_grave = True

        # 13. Punto de Guardado (Estrella de Determinación en el medallón central del Cruce de Caminos)
        self.world_objects.append(SavePointObject(x=390, y=336))

        # 14. Paso abierto al Este (final de la Avenida Este, x=764..800, y=316..372) hacia la Nueva Sección de la Iglesia del Cementerio
        for gx in range(748, 800, 16):
            for gy in range(326, 366, 14):
                pygame.draw.rect(s, (72, 70, 78), (gx, gy, 15, 13), border_radius=2)
                pygame.draw.rect(s, (40, 40, 46), (gx, gy, 15, 13), 1, border_radius=2)
        # Pilares del arco de paso hacia la Sección de la Iglesia
        pygame.draw.rect(s, (60, 60, 72), (768, 298, 12, 24), border_radius=2)
        pygame.draw.circle(s, (255, 225, 90), (774, 296), 4)
        pygame.draw.rect(s, (60, 60, 72), (768, 368, 12, 24), border_radius=2)
        pygame.draw.circle(s, (255, 225, 90), (774, 366), 4)

        self.church_section_gate_rect = pygame.Rect(768, 318, 32, 52)
        self.world_objects.append(SignObject(
            x=712, y=300,
            message="* ARCO DEL ESTE -> 'Atrio de la Iglesia del Cementerio (Continúa hacia la derecha para ir a la Iglesia).'"
        ))

        # ==========================================================
        # COLISIONES SÓLIDAS
        # ==========================================================
        self.solid_rects.append(pygame.Rect(0, 76, 800, 24))         # Muro superior
        self.solid_rects.append(pygame.Rect(0, 76, 24, 524))         # Muro izquierdo
        # Muro derecho con abertura en y=318..370 para pasar a la Sección de la Iglesia
        self.solid_rects.append(pygame.Rect(776, 76, 24, 242))
        self.solid_rects.append(pygame.Rect(776, 370, 24, 230))
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

        # Calzada procesional con bordillos y Vestíbulo Simétrico Sur (y=375..580)
        pygame.draw.rect(s, (30, 22, 42), (288, 434, 224, 62), border_radius=6)
        pygame.draw.rect(s, (150, 42, 72), (288, 434, 224, 62), 2, border_radius=6)
        for ped_cx in (328, 472):
            pygame.draw.circle(s, (20, 14, 28), (ped_cx, 465), 20)
            pygame.draw.circle(s, (195, 55, 95), (ped_cx, 465), 20, 2)

        for gy in range(375, 580, 14):
            for gx in range(368, 432, 16):
                sh = random.randint(44, 56)
                pygame.draw.rect(s, (sh, sh - 6, sh + 12), (gx, gy, 15, 13), border_radius=2)
                pygame.draw.rect(s, (24, 18, 34), (gx, gy, 15, 13), 1, border_radius=2)
            pygame.draw.rect(s, (125, 28, 52), (392, gy, 16, 13))
        pygame.draw.line(s, (150, 42, 72), (366, 378), (366, 576), 2)
        pygame.draw.line(s, (150, 42, 72), (434, 378), (434, 576), 2)

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

        # Calzada de cristal oscuro con Vestíbulo Simétrico Sur (y=375..580)
        pygame.draw.rect(s, (22, 12, 34), (288, 438, 224, 62), border_radius=6)
        pygame.draw.rect(s, (0, 0, 0), (288, 438, 224, 62), 4, border_radius=6)
        pygame.draw.rect(s, (235, 35, 90), (288, 438, 224, 62), 2, border_radius=6)
        for ped_cx in (328, 472):
            pygame.draw.circle(s, (16, 8, 26), (ped_cx, 469), 20)
            pygame.draw.circle(s, (235, 35, 90), (ped_cx, 469), 20, 2)

        for gy in range(375, 580, 14):
            pygame.draw.rect(s, (26, 14, 40), (366, gy, 68, 13))
            pygame.draw.rect(s, (0, 0, 0), (366, gy, 68, 13), 1)
            pygame.draw.rect(s, (215, 30, 80), (392, gy, 16, 13))
        pygame.draw.line(s, (235, 35, 90), (366, 376), (366, 576), 2)
        pygame.draw.line(s, (235, 35, 90), (434, 376), (434, 576), 2)

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

    # ==========================================================
    # 4.5 NUEVA SECCIÓN DEL CEMENTERIO: ATRIO DE LA IGLESIA DEL CEMENTERIO
    # ==========================================================
    def _build_cemetery_church_section(self):
        s = self.surface
        # Hierba nocturna del cementerio
        s.fill((20, 24, 22))

        # 1. Cielo nocturno del cementerio con luna y estrellas
        for y in range(76):
            t = y / 76.0
            pygame.draw.line(s, (int(8 + 18 * t), int(8 + 10 * t), int(22 + 20 * t)), (0, y), (800, y))

        random.seed(99)
        for _ in range(85):
            sx = random.randint(0, 799)
            sy = random.randint(2, 70)
            b_val = random.randint(180, 255)
            s.set_at((sx, sy), (b_val, b_val, b_val - 20))

        # Muros perimetrales góticos del cementerio (dejando abierta la entrada Oeste en y=318..370)
        for bx in range(0, 800, 24):
            sh = random.randint(80, 96)
            pygame.draw.rect(s, (sh, sh - 2, sh + 2), (bx, 76, 24, 24))
            pygame.draw.rect(s, (45, 45, 52), (bx, 76, 24, 24), 1)
            pygame.draw.line(s, (42, 42, 48), (bx + 12, 62), (bx + 12, 76), 2)
            pygame.draw.rect(s, (sh, sh - 2, sh + 2), (bx, 576, 24, 24))
            pygame.draw.rect(s, (45, 45, 52), (bx, 576, 24, 24), 1)

        for by in range(76, 600, 20):
            sh = random.randint(80, 96)
            if not (316 <= by <= 368):
                pygame.draw.rect(s, (sh, sh - 2, sh + 2), (0, by, 24, 20))
                pygame.draw.rect(s, (45, 45, 52), (0, by, 24, 20), 1)
            pygame.draw.rect(s, (sh, sh - 2, sh + 2), (776, by, 24, 20))
            pygame.draw.rect(s, (45, 45, 52), (776, by, 24, 20), 1)

        # Plaza Central del Atrio de la Iglesia y Avenidas Empedradas Simétricas
        def draw_atrium_paving(rx, ry, rw, rh):
            pygame.draw.rect(s, (46, 48, 56), (rx - 3, ry - 3, rw + 6, rh + 6), border_radius=4)
            pygame.draw.rect(s, (108, 112, 128), (rx - 3, ry - 3, rw + 6, rh + 6), 2, border_radius=4)
            for gy in range(ry, ry + rh, 14):
                for gx in range(rx, rx + rw, 16):
                    cw = min(15, rx + rw - gx)
                    ch = min(13, ry + rh - gy)
                    if cw > 2 and ch > 2:
                        sh = random.randint(64, 78)
                        pygame.draw.rect(s, (sh, sh - 3, sh + 3), (gx, gy, cw, ch), border_radius=2)
                        pygame.draw.rect(s, (40, 40, 46), (gx, gy, cw, ch), 1, border_radius=2)

        # 1) Avenida Oeste-Este que atraviesa todo el Atrio (x=0..772, y=326..366)
        draw_atrium_paving(4, 326, 768, 40)
        # 2) Gran Plaza del Atrio frente a la Iglesia (x=264..536, y=268..424)
        draw_atrium_paving(264, 268, 272, 156)
        # 3) Calzada Norte hacia la escalinata de la Iglesia y paseo Sur (x=372..428, y=244..536)
        draw_atrium_paving(372, 244, 56, 292)

        # Rosetón de piedra grabado en el centro de la Plaza del Atrio
        pygame.draw.circle(s, (56, 58, 70), (400, 346), 44)
        pygame.draw.circle(s, (215, 185, 95), (400, 346), 44, 2)
        pygame.draw.circle(s, (74, 76, 90), (400, 346), 31)
        pygame.draw.circle(s, (110, 215, 255), (400, 346), 31, 1)
        for ang_i in range(8):
            a = ang_i * (math.pi / 4.0)
            pygame.draw.line(s, (185, 160, 90), (400, 346), (400 + int(math.cos(a) * 30), 346 + int(math.sin(a) * 30)), 1)
        pygame.draw.circle(s, (235, 205, 110), (400, 346), 8)

        # Jardineras góticas de piedra con flores doradas y celestes en las 4 esquinas del Atrio
        for fx_bed, fy_bed in [(274, 276), (482, 276), (274, 386), (482, 386)]:
            pygame.draw.rect(s, (34, 44, 38), (fx_bed, fy_bed, 44, 28), border_radius=4)
            pygame.draw.rect(s, (110, 115, 132), (fx_bed, fy_bed, 44, 28), 2, border_radius=4)
            for fl_i in range(4):
                fl_x = fx_bed + 8 + fl_i * 9
                fl_y = fy_bed + 10 + (fl_i % 2) * 7
                f_col = (255, 220, 75) if fl_i % 2 == 0 else (95, 195, 255)
                pygame.draw.circle(s, f_col, (fl_x, fl_y), 3)
                pygame.draw.circle(s, (255, 255, 240), (fl_x, fl_y), 1)

        # 2. GRAN CATEDRAL / IGLESIA GÓTICA DEL CEMENTERIO (x=256..544, y=4..260)
        # Sombra proyectada por la fachada y las dos torres sobre el atrio
        pygame.draw.rect(s, (14, 16, 20), (258, 244, 284, 16), border_radius=4)

        # A) Torres Gemelas Laterales (Torre Oeste x=264..316, Torre Este x=484..536, y=86..252)
        for tx in (264, 484):
            pygame.draw.rect(s, (68, 64, 84), (tx, 86, 52, 166), border_radius=2)
            # Ladrillos de sillería labrada en las torres
            for by in range(90, 248, 12):
                for bx in range(tx + 2, tx + 48, 16):
                    off = 6 if (by // 12) % 2 == 1 else 0
                    bw = min(14, tx + 50 - (bx + off))
                    if bw > 3:
                        pygame.draw.rect(s, (78, 74, 96), (bx + off, by, bw, 10), 1)
            pygame.draw.rect(s, (34, 30, 48), (tx, 86, 52, 166), 2, border_radius=2)
            # Cornisas molduradas de las torres
            pygame.draw.rect(s, (108, 104, 128), (tx - 3, 124, 58, 5), border_radius=1)
            pygame.draw.rect(s, (108, 104, 128), (tx - 3, 184, 58, 5), border_radius=1)
            # Ventanal del campanario lateral con campana de bronce dorada
            pygame.draw.rect(s, (20, 14, 32), (tx + 14, 94, 24, 26), border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.polygon(s, (235, 195, 75), [(tx + 26, 99), (tx + 19, 113), (tx + 33, 113)])
            pygame.draw.circle(s, (255, 240, 150), (tx + 26, 114), 3)
            pygame.draw.rect(s, (215, 185, 90), (tx + 14, 94, 24, 26), 2, border_top_left_radius=12, border_top_right_radius=12)
            # Vitral ojival iluminado en el cuerpo de cada torre
            pygame.draw.rect(s, (22, 16, 36), (tx + 14, 138, 24, 40), border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.rect(s, (95, 220, 255), (tx + 17, 142, 8, 32), border_top_left_radius=8)
            pygame.draw.rect(s, (255, 110, 205), (tx + 27, 142, 8, 32), border_top_right_radius=8)
            pygame.draw.rect(s, (230, 195, 95), (tx + 14, 138, 24, 40), 2, border_top_left_radius=12, border_top_right_radius=12)
            # Chapitel gótico puntiagudo de cada torre lateral (y=36..86) con pináculo dorado
            spire_pts = [(tx - 4, 86), (tx + 26, 36), (tx + 56, 86)]
            pygame.draw.polygon(s, (48, 34, 66), spire_pts)
            for sy_line in range(48, 84, 8):
                t_w = int((sy_line - 36) * 0.55)
                pygame.draw.line(s, (68, 52, 90), (tx + 26 - t_w, sy_line), (tx + 26 + t_w, sy_line), 1)
            pygame.draw.polygon(s, (24, 16, 36), spire_pts, 2)
            pygame.draw.line(s, (255, 225, 85), (tx + 26, 22), (tx + 26, 36), 2)
            pygame.draw.line(s, (255, 225, 85), (tx + 21, 27), (tx + 31, 27), 2)

        # B) Nave Central de Piedra Labrada (x=312..488, y=104..252)
        pygame.draw.rect(s, (78, 74, 96), (312, 104, 176, 148), border_radius=2)
        for by in range(108, 248, 12):
            for bx in range(316, 480, 18):
                off = 9 if (by // 12) % 2 == 1 else 0
                bw = min(16, 484 - (bx + off))
                if bw > 3:
                    pygame.draw.rect(s, (88, 84, 108), (bx + off, by, bw, 10), 1)
        pygame.draw.rect(s, (38, 34, 52), (312, 104, 176, 148), 3, border_radius=2)

        # Contrafuertes góticos escalonados con pináculos
        for bx in (310, 354, 436, 480):
            pygame.draw.rect(s, (62, 58, 78), (bx, 102, 10, 150))
            pygame.draw.rect(s, (96, 92, 116), (bx + 1, 102, 3, 148))
            pygame.draw.rect(s, (30, 26, 42), (bx, 102, 10, 150), 1)
            pygame.draw.polygon(s, (110, 106, 130), [(bx - 1, 102), (bx + 5, 88), (bx + 11, 102)])
            pygame.draw.circle(s, (245, 215, 90), (bx + 5, 87), 2)

        # Frontón Gótico Central y Gran Aguja del Campanario Mayor (y=4..106)
        gable_pts = [(304, 106), (400, 44), (496, 106)]
        pygame.draw.polygon(s, (52, 36, 68), gable_pts)
        for gy_l in range(54, 104, 7):
            hw = int((gy_l - 44) * 1.45)
            pygame.draw.line(s, (74, 54, 96), (400 - hw, gy_l), (400 + hw, gy_l), 1)
        pygame.draw.polygon(s, (22, 14, 34), gable_pts, 3)
        # Moldura dorada en el borde del frontón
        pygame.draw.lines(s, (225, 195, 95), False, [(308, 105), (400, 47), (492, 105)], 2)

        # Aguja Central Mayor y Cruz Dorada Radiante
        pygame.draw.polygon(s, (64, 46, 86), [(374, 62), (400, 14), (426, 62)])
        pygame.draw.polygon(s, (24, 16, 36), [(374, 62), (400, 14), (426, 62)], 2)
        cross_glow = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(cross_glow, (255, 235, 110, 75), (14, 14), 13)
        s.blit(cross_glow, (386, -2))
        pygame.draw.line(s, (255, 235, 95), (400, 2), (400, 18), 3)
        pygame.draw.line(s, (255, 235, 95), (392, 8), (408, 8), 3)

        # Reloj / Rosetón Superior de la Runa Delta en el frontón (cx=400, cy=78)
        pygame.draw.circle(s, (24, 16, 38), (400, 78), 12)
        pygame.draw.circle(s, (235, 200, 90), (400, 78), 12, 2)
        pygame.draw.polygon(s, (120, 225, 255), [(400, 71), (393, 83), (407, 83)])

        # C) Gran Rosetón Central de Vitral Gótico (cx=400, cy=142, r=24) con tracería radial
        rose_halo = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(rose_halo, (140, 210, 255, 38), (32, 32), 30)
        s.blit(rose_halo, (368, 110))
        pygame.draw.circle(s, (20, 12, 34), (400, 142), 24)
        petal_cols = [(95, 225, 255), (255, 105, 205), (255, 225, 85), (130, 250, 170)]
        for i in range(8):
            ang = i * (math.pi / 4.0)
            px = 400 + int(math.cos(ang) * 14)
            py = 142 + int(math.sin(ang) * 14)
            pygame.draw.circle(s, petal_cols[i % 4], (px, py), 6)
            pygame.draw.line(s, (30, 20, 44), (400, 142), (400 + int(math.cos(ang) * 23), 142 + int(math.sin(ang) * 23)), 2)
        pygame.draw.circle(s, (255, 240, 120), (400, 142), 7)
        pygame.draw.circle(s, (255, 255, 255), (400, 142), 3)
        pygame.draw.circle(s, (235, 200, 95), (400, 142), 24, 3)
        pygame.draw.circle(s, (180, 150, 75), (400, 142), 16, 1)

        # Vitrales ojivales gemelos a los lados del Rosetón (wx=334 y wx=466)
        for wx in (334, 466):
            pygame.draw.rect(s, (20, 14, 34), (wx - 11, 134, 22, 64), border_top_left_radius=11, border_top_right_radius=11)
            pygame.draw.rect(s, (105, 220, 255), (wx - 8, 138, 7, 56), border_top_left_radius=7)
            pygame.draw.rect(s, (255, 115, 205), (wx + 1, 138, 7, 56), border_top_right_radius=7)
            pygame.draw.circle(s, (255, 235, 95), (wx, 148), 5)
            pygame.draw.rect(s, (230, 195, 90), (wx - 11, 134, 22, 64), 2, border_top_left_radius=11, border_top_right_radius=11)
            # Reflejo multicolor del vitral sobre el césped/piedra
            w_beam = pygame.Surface((32, 28), pygame.SRCALPHA)
            pygame.draw.polygon(w_beam, (140, 215, 255, 32), [(4, 0), (28, 0), (32, 28), (0, 28)])
            s.blit(w_beam, (wx - 16, 248))

        # D) Gran Pórtico Gótico Arquivolta y Puerta Doble de Roble (x=368..432, y=182..252)
        # Escalinata de mármol de 3 peldaños
        pygame.draw.rect(s, (92, 94, 112), (354, 252, 92, 10), border_radius=2)
        pygame.draw.rect(s, (112, 114, 132), (360, 247, 80, 8), border_radius=2)
        pygame.draw.rect(s, (132, 134, 152), (366, 242, 68, 7), border_radius=2)
        # Arquivoltas concéntricas de piedra y oro
        pygame.draw.rect(s, (54, 48, 70), (368, 180, 64, 66), border_top_left_radius=28, border_top_right_radius=28)
        pygame.draw.rect(s, (235, 195, 90), (368, 180, 64, 66), 2, border_top_left_radius=28, border_top_right_radius=28)
        pygame.draw.rect(s, (36, 30, 50), (373, 185, 54, 61), border_top_left_radius=24, border_top_right_radius=24)
        pygame.draw.rect(s, (195, 160, 75), (373, 185, 54, 61), 1, border_top_left_radius=24, border_top_right_radius=24)
        # Puertas dobles de madera noble entreabiertas con luz cálida interior y herrajes
        pygame.draw.rect(s, (18, 10, 26), (377, 190, 46, 56), border_top_left_radius=20, border_top_right_radius=20)
        pygame.draw.rect(s, (74, 42, 28), (378, 194, 16, 52), border_top_left_radius=14)
        pygame.draw.rect(s, (74, 42, 28), (406, 194, 16, 52), border_top_right_radius=14)
        # Haz cálido que sale del interior de la iglesia
        pygame.draw.rect(s, (255, 210, 115), (394, 196, 12, 50))
        pygame.draw.rect(s, (255, 245, 190), (397, 198, 6, 48))
        # Herrajes dorados en las hojas de la puerta
        for hy in (210, 228):
            pygame.draw.line(s, (225, 190, 85), (379, hy), (391, hy), 2)
            pygame.draw.line(s, (225, 190, 85), (409, hy), (421, hy), 2)

        # Faroles de hierro forjado encendidos a ambos lados del pórtico
        for lx in (358, 442):
            pygame.draw.rect(s, (42, 38, 52), (lx - 3, 206, 6, 10), border_radius=1)
            pygame.draw.circle(s, (255, 225, 100), (lx, 211), 3)
            lglow = pygame.Surface((26, 26), pygame.SRCALPHA)
            pygame.draw.circle(lglow, (255, 200, 80, 65), (13, 13), 12)
            s.blit(lglow, (lx - 13, 198))

        # Rectángulo de entrada a la Iglesia (apenas subes los escalones hacia el arco)
        self.church_gate_rect = pygame.Rect(376, 214, 48, 44)

        # Colisiones del edificio de la Iglesia dejando libre el vano de la puerta (x=376..424)
        self.solid_rects.append(pygame.Rect(264, 92, 112, 158))
        self.solid_rects.append(pygame.Rect(424, 92, 112, 158))
        self.solid_rects.append(pygame.Rect(376, 92, 48, 120))

        # Bancas de Piedra del Atrio y Relicarios Góticos interactivos
        def draw_stone_bench(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (52, 54, 66), (cx + 4, cy + 12, 8, 10))
            pygame.draw.rect(surf, (52, 54, 66), (cx + w - 12, cy + 12, 8, 10))
            pygame.draw.rect(surf, (96, 100, 116), (cx, cy + 6, w, 10), border_radius=2)
            pygame.draw.rect(surf, (120, 124, 142), (cx + 2, cy, w - 4, 7), border_radius=2)
            pygame.draw.rect(surf, (40, 42, 52), (cx, cy + 6, w, 10), 1, border_radius=2)

        for bx_bench in (312, 440):
            self.world_objects.append(InteriorProp(
                bx_bench, 442, 48, 22, 462, draw_stone_bench,
                [
                    "* Un banco de piedra labrada frente a la Catedral del Cementerio.",
                    "* Desde aquí puedes contemplar el gran rosetón iluminado y las agujas góticas.",
                ],
                is_solid=True,
            ))

        # Carteles, Punto de Guardado, árboles góticos y pilares alineados simétricamente alrededor de la Plaza del Atrio
        self.world_objects.append(SignObject(
            x=296, y=282,
            message="* CATEDRAL DEL CEMENTERIO: 'Entra por el pórtico norte. Más allá del altar mayor se oculta la puerta hacia el antiguo Sótano...'"
        ))
        self.world_objects.append(SavePointObject(x=484, y=282))
        self.world_objects.append(SignObject(
            x=48, y=296,
            message="* <- OESTE: Regresar a la plaza principal del Cementerio."
        ))

        for tx, ty in [(64, 156), (684, 156), (64, 464), (684, 464)]:
            self.world_objects.append(TwistedTreeProp(tx, ty, has_lantern=True))

        for px, py in [(232, 232), (548, 232), (232, 404), (548, 404)]:
            self.world_objects.append(RuinPillar(px, py))

        for wx, wy, wcol in [
            (278, 346, (130, 235, 255)),
            (522, 346, (130, 235, 255)),
            (346, 484, (195, 130, 255)),
            (454, 484, (195, 130, 255)),
        ]:
            self.world_objects.append(WillOWisp(wx, wy, color=wcol))

        # Colisiones perimetrales de la Sección de la Iglesia (con salida Oeste en y=318..370)
        self.solid_rects.append(pygame.Rect(0, 76, 800, 24))
        self.solid_rects.append(pygame.Rect(0, 76, 24, 242))
        self.solid_rects.append(pygame.Rect(0, 370, 24, 230))
        self.solid_rects.append(pygame.Rect(776, 76, 24, 524))
        self.solid_rects.append(pygame.Rect(0, 576, 800, 24))

    # ==========================================================
    # 5. INTERIOR DE LA IGLESIA DE HOMETOWN (ULTRA DETALLADO CON ÓRGANO, VITRALES, CONFESIONARIO Y PUERTA AL SÓTANO)
    # ==========================================================
    def _build_church(self):
        s = self.surface
        # Base de madera de caoba oscura y piedra catedralicia
        s.fill((34, 24, 30))

        # 1. MURO NORTE CATEDRALICIO CON SILLERÍA, PILASTRAS Y 6 VITRALES GÓTICOS (y=0..96)
        pygame.draw.rect(s, (52, 42, 66), (0, 0, 800, 96))
        for wy_b in range(0, 92, 16):
            for wx_b in range(0, 800, 32):
                off = 16 if (wy_b // 16) % 2 == 1 else 0
                pygame.draw.rect(s, (60, 48, 76), ((wx_b + off) % 800, wy_b, 30, 14), 1)

        # Friso y zócalo dorado a lo largo del muro norte
        pygame.draw.rect(s, (38, 28, 48), (0, 82, 800, 14))
        pygame.draw.line(s, (225, 195, 95), (0, 82), (800, 82), 2)
        pygame.draw.line(s, (240, 210, 110), (0, 96), (800, 96), 3)

        # Pilastras estriadas con capiteles dorados en el muro norte
        for pil_x in (36, 134, 236, 338, 462, 564, 666, 764):
            pygame.draw.rect(s, (74, 64, 92), (pil_x - 6, 6, 12, 88))
            pygame.draw.line(s, (96, 84, 116), (pil_x - 2, 8), (pil_x - 2, 92), 1)
            pygame.draw.line(s, (96, 84, 116), (pil_x + 2, 8), (pil_x + 2, 92), 1)
            pygame.draw.rect(s, (230, 195, 90), (pil_x - 8, 4, 16, 5), border_radius=1)
            pygame.draw.rect(s, (230, 195, 90), (pil_x - 8, 90, 16, 5), border_radius=1)

        # 2. SUELO DETALLADO: NAVE DE ROBLE, PASILLOS LATERALES DE MÁRMOL Y PRESBITERIO ELEVADO
        # Pasillos laterales de baldosas de mármol ajedrezadas (x=24..108 y x=692..776)
        for side_x in (24, 692):
            pygame.draw.rect(s, (44, 38, 54), (side_x, 98, 84, 478))
            for ty in range(98, 574, 24):
                for tx in range(side_x, side_x + 84, 28):
                    is_light = ((tx // 28) + (ty // 24)) % 2 == 0
                    t_col = (58, 52, 70) if is_light else (38, 32, 48)
                    pygame.draw.rect(s, t_col, (tx, ty, 28, 24))
                    pygame.draw.rect(s, (28, 22, 36), (tx, ty, 28, 24), 1)
            pygame.draw.line(s, (195, 168, 85), (side_x + (84 if side_x == 24 else 0), 98), (side_x + (84 if side_x == 24 else 0), 576), 2)

        # Tablones de madera noble con vetas y juntas en el cuerpo central de la nave (x=110..690, y=192..576)
        for fy in range(192, 576, 16):
            plank_tone = 36 if (fy // 16) % 2 == 0 else 32
            pygame.draw.rect(s, (plank_tone + 6, plank_tone - 4, plank_tone), (110, fy, 580, 16))
            pygame.draw.line(s, (24, 16, 22), (110, fy), (690, fy), 1)
            for jx in range(130 + ((fy // 16) % 3) * 28, 680, 76):
                pygame.draw.line(s, (26, 18, 24), (jx, fy), (jx, fy + 15), 1)

        # Presbiterio / Santuario Elevado al norte (x=104..696, y=100..190) con mosaico de mármol y 3 escalones dorados
        pygame.draw.rect(s, (56, 44, 64), (104, 100, 592, 88), border_radius=4)
        for my in range(104, 184, 20):
            for mx in range(108, 688, 24):
                m_col = (66, 52, 76) if ((mx // 24) + (my // 20)) % 2 == 0 else (50, 38, 58)
                pygame.draw.rect(s, m_col, (mx, my, 24, 20))
                pygame.draw.rect(s, (40, 30, 48), (mx, my, 24, 20), 1)
        pygame.draw.rect(s, (230, 195, 95), (104, 100, 592, 88), 2, border_radius=4)
        # Escalones del presbiterio con borde dorado
        for step_i, sy_step in enumerate((184, 188, 192)):
            pygame.draw.line(s, (195 - step_i * 20, 165 - step_i * 15, 95), (108, sy_step), (692, sy_step), 2)

        # Vestíbulo / Nártex de entrada al sur (x=250..550, y=496..568)
        pygame.draw.rect(s, (52, 40, 58), (250, 496, 300, 70), border_radius=4)
        pygame.draw.rect(s, (225, 190, 90), (250, 496, 300, 70), 2, border_radius=4)
        pygame.draw.rect(s, (125, 95, 65), (262, 504, 276, 54), 1, border_radius=3)

        # 3. VITRALES GÓTICOS ILUMINADOS CON HACES DE LUZ VOLUMÉTRICOS Y PARTÍCULAS DE POLVO DORADO
        for wx in (86, 185, 286, 514, 615, 714):
            pygame.draw.rect(s, (20, 14, 34), (wx - 20, 12, 40, 66), border_top_left_radius=18, border_top_right_radius=18)
            pygame.draw.rect(s, (100, 215, 255), (wx - 16, 18, 14, 56), border_top_left_radius=12)
            pygame.draw.rect(s, (255, 120, 205), (wx + 2, 18, 14, 56), border_top_right_radius=12)
            # Tracería interior y rosetón dorado del vitral
            pygame.draw.line(s, (30, 20, 46), (wx - 16, 46), (wx + 16, 46), 2)
            pygame.draw.circle(s, (255, 235, 95), (wx, 30), 8)
            pygame.draw.polygon(s, (255, 255, 240), [(wx, 24), (wx - 5, 33), (wx + 5, 33)])
            pygame.draw.rect(s, (230, 195, 95), (wx - 20, 12, 40, 66), 2, border_top_left_radius=18, border_top_right_radius=18)
            # Haz de luz translúcido proyectado sobre el suelo con motas de luz
            beam = pygame.Surface((96, 165), pygame.SRCALPHA)
            pygame.draw.polygon(beam, (255, 235, 165, 24), [(26, 0), (70, 0), (96, 165), (0, 165)])
            pygame.draw.polygon(beam, (135, 225, 255, 16), [(32, 0), (50, 0), (64, 165), (12, 165)])
            for dm_i in range(6):
                dmx = 24 + (dm_i * 11) % 52
                dmy = 22 + dm_i * 24
                pygame.draw.circle(beam, (255, 245, 190, 95), (dmx, dmy), 2)
            s.blit(beam, (wx - 48, 98))

        # 4. GRAN ALFOMBRA REAL CARMESÍ Y DORADA CON MEDALLÓN DE LA RUNA DELTA (x=358..442, y=106..576)
        pygame.draw.rect(s, (110, 18, 38), (358, 106, 84, 470))
        pygame.draw.rect(s, (152, 28, 54), (364, 106, 72, 470))
        pygame.draw.rect(s, (240, 200, 90), (358, 106, 84, 470), 2)
        pygame.draw.rect(s, (210, 165, 70), (364, 106, 72, 470), 1)
        # Rombos bordados en oro a lo largo de la alfombra real
        for ry_pat in range(126, 566, 32):
            pts_d = [(400, ry_pat - 7), (410, ry_pat), (400, ry_pat + 7), (390, ry_pat)]
            pygame.draw.polygon(s, (215, 170, 75), pts_d, 1)
            pygame.draw.circle(s, (245, 215, 105), (361, ry_pat), 1)
            pygame.draw.circle(s, (245, 215, 105), (439, ry_pat), 1)

        # Gran Medallón Tejido de la Runa Delta en el centro de la nave (cx=400, cy=344)
        pygame.draw.circle(s, (125, 22, 46), (400, 344), 34)
        pygame.draw.circle(s, (245, 205, 95), (400, 344), 34, 2)
        pygame.draw.circle(s, (215, 175, 80), (400, 344), 26, 1)
        pygame.draw.circle(s, (255, 230, 115), (400, 336), 6)
        pygame.draw.polygon(s, (240, 200, 90), [(374, 336), (392, 332), (384, 344)])
        pygame.draw.polygon(s, (240, 200, 90), [(426, 336), (408, 332), (416, 344)])
        for dx_t in (-11, 0, 11):
            dy_t = 352 if dx_t != 0 else 356
            pygame.draw.polygon(s, (255, 225, 110), [(400 + dx_t, dy_t - 5), (395 + dx_t, dy_t + 4), (405 + dx_t, dy_t + 4)])

        # 5. PUERTA ARQUEADA AL SÓTANO DE LA IGLESIA EN EL CENTRO DEL MURO NORTE (x=364..436, y=54..118)
        pygame.draw.rect(s, (24, 18, 38), (362, 56, 76, 62), border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.rect(s, (0, 0, 0), (372, 66, 56, 52), border_top_left_radius=12, border_top_right_radius=12)
        for step_i in range(5):
            sy = 74 + step_i * 8
            sh_c = max(25, 95 - step_i * 15)
            pygame.draw.line(s, (sh_c, sh_c - 10, sh_c + 30), (376, sy), (424, sy), 3)
        # Neblina mística violeta/cian emanando del sótano hacia el presbiterio
        mist = pygame.Surface((64, 36), pygame.SRCALPHA)
        pygame.draw.ellipse(mist, (165, 95, 255, 48), (4, 8, 56, 24))
        pygame.draw.ellipse(mist, (85, 235, 255, 36), (12, 12, 40, 16))
        s.blit(mist, (368, 96))
        pygame.draw.rect(s, (235, 195, 90), (362, 56, 76, 62), 2, border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.rect(s, (185, 110, 255), (370, 64, 60, 54), 1, border_top_left_radius=12, border_top_right_radius=12)
        # Antorchas de pared flanqueando la entrada del sótano
        for tx_s in (352, 448):
            pygame.draw.rect(s, (90, 75, 55), (tx_s - 2, 74, 4, 12))
            pygame.draw.circle(s, (185, 110, 255), (tx_s, 71), 4)
            pygame.draw.circle(s, (110, 240, 255), (tx_s, 71), 2)
        self.basement_gate_rect = pygame.Rect(374, 80, 52, 42)

        # 6. MOBILIARIO MONUMENTAL INTERACTIVO DEL PRESBITERIO Y LA NAVE
        # A) Gran Órgano de Tubos Dorados Catedralicio (Noroeste del Presbiterio: x=116, y=94, w=114, h=64)
        def draw_pipe_organ(surf, cx, cy, w, h):
            # Mueble de caoba tallada del órgano
            pygame.draw.rect(surf, (72, 40, 28), (cx, cy + 22, w, h - 22), border_radius=3)
            pygame.draw.rect(surf, (42, 22, 14), (cx, cy + 22, w, h - 22), 2, border_radius=3)
            pygame.draw.rect(surf, (230, 195, 85), (cx + 4, cy + 25, w - 8, h - 28), 1, border_radius=2)
            # 13 Tubos de latón y plata graduados en forma de corona gótica
            pipe_heights = [20, 26, 32, 38, 44, 50, 54, 50, 44, 38, 32, 26, 20]
            for pi, ph in enumerate(pipe_heights):
                px = cx + 8 + pi * 8
                py = cy + 36 - ph
                p_col = (235, 200, 90) if pi % 2 == 0 else (205, 215, 230)
                pygame.draw.rect(surf, p_col, (px, py, 6, ph), border_top_left_radius=2, border_top_right_radius=2)
                pygame.draw.rect(surf, (95, 70, 30), (px, py, 6, ph), 1, border_top_left_radius=2, border_top_right_radius=2)
                pygame.draw.line(surf, (255, 245, 180), (px + 1, py + 2), (px + 1, py + ph - 3), 1)
            # Doble teclado de marfil en la consola central
            pygame.draw.rect(surf, (245, 242, 230), (cx + 28, cy + 44, w - 56, 6))
            pygame.draw.rect(surf, (230, 225, 210), (cx + 28, cy + 51, w - 56, 5))
            for kx_l in range(cx + 30, cx + w - 30, 4):
                pygame.draw.line(surf, (30, 25, 30), (kx_l, cy + 44), (kx_l, cy + 47), 1)

        self.world_objects.append(InteriorProp(
            116, 94, 114, 64, 158, draw_pipe_organ,
            [
                "* El Gran Órgano de Tubos Dorados de la Iglesia de Hometown.",
                "* Sus trece tubos de bronce y plata aún vibran suavemente con el eco de un himno olvidado.",
                "* (Tocas una nota solemne; su resonancia serena tu espíritu. +15 de cordura)",
            ],
            is_solid=True,
        ))
        self.world_objects[-1]._sanity_boost = 15

        # B) Altar Mayor del Ángel y la Runa Delta (Izquierda del pasillo en el Presbiterio: x=244, y=122, w=104, h=42)
        def draw_high_altar(surf, cx, cy, w, h):
            # Mesa de mármol y madera dorada
            pygame.draw.rect(surf, (86, 54, 40), (cx, cy + 10, w, h - 10), border_radius=3)
            pygame.draw.rect(surf, (240, 200, 90), (cx, cy + 10, w, h - 10), 2, border_radius=3)
            # Mantel frontal de terciopelo carmesí con flecos de oro y Runa Delta
            pygame.draw.rect(surf, (165, 28, 58), (cx + 14, cy + 10, w - 28, h - 12))
            pygame.draw.rect(surf, (245, 210, 95), (cx + 14, cy + 10, w - 28, h - 12), 1)
            pygame.draw.circle(surf, (255, 235, 100), (cx + w // 2, cy + 23), 6, 1)
            pygame.draw.polygon(surf, (255, 235, 100), [(cx + w // 2, cy + 28), (cx + w // 2 - 5, cy + 34), (cx + w // 2 + 5, cy + 34)])
            # Cáliz de oro, libro sagrado abierto y candelabros sobre el altar
            pygame.draw.rect(surf, (245, 240, 225), (cx + w // 2 - 10, cy + 4, 9, 7))
            pygame.draw.rect(surf, (245, 240, 225), (cx + w // 2 + 1, cy + 4, 9, 7))
            pygame.draw.line(surf, (180, 40, 60), (cx + w // 2, cy + 4), (cx + w // 2, cy + 11), 1)
            # Cáliz y velas laterales
            pygame.draw.polygon(surf, (255, 220, 85), [(cx + 22, cy + 3), (cx + 28, cy + 3), (cx + 25, cy + 10)])
            for vx in (cx + 10, cx + w - 10):
                pygame.draw.rect(surf, (245, 240, 220), (vx - 2, cy + 1, 4, 9))
                pygame.draw.circle(surf, (255, 215, 80), (vx, cy - 1), 3)

        self.world_objects.append(InteriorProp(
            244, 122, 104, 42, 162, draw_high_altar,
            [
                "* El Altar Mayor del Ángel y la Runa Delta.",
                "* Un cáliz dorado y un códice antiguo descansan sobre el terciopelo carmesí.",
                "* Justo a la derecha del altar, la puerta del muro norte desciende hacia el SÓTANO...",
            ],
            is_solid=True,
        ))

        # C) Púlpito Dorado del Coro y Candelabro de 7 Brazos (Derecha del pasillo en el Presbiterio: x=452, y=122, w=104, h=42)
        def draw_choir_lectern(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (86, 54, 40), (cx, cy + 10, w, h - 10), border_radius=3)
            pygame.draw.rect(surf, (240, 200, 90), (cx, cy + 10, w, h - 10), 2, border_radius=3)
            pygame.draw.rect(surf, (45, 90, 145), (cx + 14, cy + 10, w - 28, h - 12))
            pygame.draw.rect(surf, (245, 210, 95), (cx + 14, cy + 10, w - 28, h - 12), 1)
            # Candelabro dorado de 7 velas encendidas
            pygame.draw.line(surf, (245, 205, 85), (cx + 20, cy + 6), (cx + w - 20, cy + 6), 2)
            for vi in range(7):
                vx = cx + 20 + vi * 10
                pygame.draw.rect(surf, (245, 240, 220), (vx - 1, cy, 3, 7))
                pygame.draw.circle(surf, (255, 220, 85), (vx, cy - 2), 2)

        self.world_objects.append(InteriorProp(
            452, 122, 104, 42, 162, draw_choir_lectern,
            [
                "* El Púlpito del Coro y el Gran Candelabro de Siete Brazos.",
                "* Sus siete llamas doradas arden sin consumirse, iluminando los escalones hacia el Sótano.",
            ],
            is_solid=True,
        ))

        # D) Confesionario Gótico de Roble y Terciopelo (Noreste del Presbiterio: x=570, y=94, w=114, h=64)
        def draw_confessional(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (68, 38, 26), (cx, cy + 8, w, h - 8), border_radius=3)
            pygame.draw.rect(surf, (38, 20, 14), (cx, cy + 8, w, h - 8), 2, border_radius=3)
            # Frontón central con cruz dorada
            pygame.draw.polygon(surf, (88, 50, 34), [(cx + 28, cy + 8), (cx + w // 2, cy - 2), (cx + w - 28, cy + 8)])
            pygame.draw.line(surf, (245, 210, 90), (cx + w // 2, cy - 8), (cx + w // 2, cy), 2)
            pygame.draw.line(surf, (245, 210, 90), (cx + w // 2 - 3, cy - 5), (cx + w // 2 + 3, cy - 5), 2)
            # Tres compartimentos: cortinas púrpura a los lados y celosía dorada en el centro
            for side_off in (8, w - 34):
                pygame.draw.rect(surf, (115, 28, 72), (cx + side_off, cy + 16, 26, h - 20), border_top_left_radius=8, border_top_right_radius=8)
                pygame.draw.line(surf, (155, 45, 98), (cx + side_off + 8, cy + 18), (cx + side_off + 8, cy + h - 6), 1)
                pygame.draw.line(surf, (155, 45, 98), (cx + side_off + 18, cy + 18), (cx + side_off + 18, cy + h - 6), 1)
                pygame.draw.rect(surf, (225, 190, 85), (cx + side_off, cy + 16, 26, h - 20), 1, border_top_left_radius=8, border_top_right_radius=8)
            # Celosía central de madera dorada
            pygame.draw.rect(surf, (28, 16, 22), (cx + 42, cy + 16, 30, 26), border_radius=2)
            for gx in range(cx + 46, cx + 70, 5):
                pygame.draw.line(surf, (215, 180, 80), (gx, cy + 16), (gx, cy + 42), 1)
            for gy in range(cy + 20, cy + 42, 5):
                pygame.draw.line(surf, (215, 180, 80), (cx + 42, gy), (cx + 72, gy), 1)
            pygame.draw.rect(surf, (230, 195, 90), (cx + 42, cy + 16, 30, 26), 1, border_radius=2)

        self.world_objects.append(InteriorProp(
            570, 94, 114, 64, 158, draw_confessional,
            [
                "* Un antiguo Confesionario de roble tallado con cortinas de terciopelo púrpura.",
                "* A través de la celosía dorada solo se escucha el eco lejano de la Fuente Oscura bajo el suelo.",
            ],
            is_solid=True,
        ))

        # E) 8 Bancas de Madera Tallada con Himnarios y Velas Laterales (4 filas a izquierda y derecha)
        for row_idx, py in enumerate(range(212, 476, 66)):
            for is_right, px in enumerate((132, 488)):
                def draw_pew(surf, cx, cy, w, h, r_i=row_idx, side_r=is_right):
                    # Sombra bajo la banca
                    pygame.draw.rect(surf, (20, 14, 18), (cx + 2, cy + h - 2, w - 4, 5), border_radius=2)
                    # Cuerpo y respaldo de caoba pulida
                    pygame.draw.rect(surf, (94, 56, 36), (cx, cy, w, h), border_radius=3)
                    pygame.draw.rect(surf, (136, 84, 54), (cx + 2, cy + 2, w - 4, 8), border_radius=2)
                    pygame.draw.rect(surf, (74, 42, 26), (cx + 4, cy + 11, w - 8, 12))
                    # Costados góticos tallados con remate dorado
                    pygame.draw.rect(surf, (62, 34, 20), (cx, cy - 2, 8, h + 2), border_radius=2)
                    pygame.draw.rect(surf, (62, 34, 20), (cx + w - 8, cy - 2, 8, h + 2), border_radius=2)
                    pygame.draw.circle(surf, (235, 195, 85), (cx + 4, cy - 2), 2)
                    pygame.draw.circle(surf, (235, 195, 85), (cx + w - 4, cy - 2), 2)
                    pygame.draw.rect(surf, (44, 24, 14), (cx, cy, w, h), 2, border_radius=3)
                    # Himnarios de portada azul/carmesí reposando sobre la banca
                    hx1 = cx + 34 + (r_i * 19) % 40
                    hx2 = cx + 112 + (r_i * 13) % 36
                    pygame.draw.rect(surf, (185, 40, 65), (hx1, cy + 13, 10, 8), border_radius=1)
                    pygame.draw.rect(surf, (245, 215, 95), (hx1 + 2, cy + 15, 6, 4), 1)
                    pygame.draw.rect(surf, (55, 115, 195), (hx2, cy + 13, 10, 8), border_radius=1)
                    # Candelero encendido en el extremo que da al pasillo central de la alfombra
                    candle_x = (cx + w - 4) if side_r == 0 else (cx + 4)
                    pygame.draw.circle(surf, (255, 215, 85), (candle_x, cy - 4), 2)

                self.world_objects.append(InteriorProp(
                    px, py, 180, 28, py + 26, draw_pew,
                    [
                        "* Una banca de caoba pulida con grabados góticos y candeleros en los extremos.",
                        "* Sobre el asiento descansan antiguos libros de cánticos con el emblema de la Runa Delta.",
                    ],
                    is_solid=True,
                ))

        # F) Columnas Catedralicias con Candelabros en las Naves Laterales (x=54 y x=722)
        def draw_cathedral_column(surf, cx, cy, w, h):
            pygame.draw.ellipse(surf, (18, 12, 22), (cx - 2, cy + h - 8, w + 4, 10))
            pygame.draw.rect(surf, (68, 60, 84), (cx + 2, cy + h - 12, w - 4, 10), border_radius=2)
            pygame.draw.rect(surf, (88, 78, 108), (cx + 5, cy + 6, w - 10, h - 16))
            pygame.draw.line(surf, (112, 102, 134), (cx + 8, cy + 8), (cx + 8, cy + h - 12), 1)
            pygame.draw.line(surf, (112, 102, 134), (cx + w - 9, cy + 8), (cx + w - 9, cy + h - 12), 1)
            pygame.draw.rect(surf, (230, 195, 90), (cx + 2, cy + 2, w - 4, 6), border_radius=1)
            pygame.draw.rect(surf, (230, 195, 90), (cx + 2, cy + h - 13, w - 4, 4), border_radius=1)
            # Vela encendida en aplique de bronce
            pygame.draw.circle(surf, (255, 220, 85), (cx + w // 2, cy + 22), 3)

        for col_y in (204, 326, 448):
            for col_x in (54, 718):
                self.world_objects.append(InteriorProp(
                    col_x, col_y, 28, 48, col_y + 46, draw_cathedral_column,
                    ["* Una columna estriada de mármol con capitel dorado y un candelabro encendido."],
                    is_solid=True,
                ))

        # G) Pilas de Agua Bendita yAltares de Velas Votivas en el Nártex Sur (x=142, y=506 y x=594, y=506)
        def draw_votive_stand(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (70, 42, 32), (cx, cy + 12, w, h - 12), border_radius=3)
            pygame.draw.rect(surf, (230, 195, 85), (cx, cy + 12, w, h - 12), 2, border_radius=3)
            for row_v in range(2):
                for col_v in range(6):
                    vx = cx + 8 + col_v * 9
                    vy = cy + 8 + row_v * 10
                    pygame.draw.rect(surf, (215, 45, 65), (vx - 2, vy + 2, 4, 5), border_radius=1)
                    pygame.draw.circle(surf, (255, 225, 95), (vx, vy), 2)

        for vx_stand in (142, 594):
            self.world_objects.append(InteriorProp(
                vx_stand, 508, 64, 34, 540, draw_votive_stand,
                [
                    "* Un altar de velas votivas. Decenas de pequeñas llamas titilan en frascos de cristal rubí.",
                    "* Enciendes una vela en silencio. Su luz cálida reconforta tu alma. (+15 de cordura)",
                ],
                is_solid=True,
            ))
            self.world_objects[-1]._sanity_boost = 15

        self.world_objects.append(SignObject(
            x=444, y=104,
            message="* PUERTA DEL SÓTANO: 'Prohibido el paso. Se escuchan ecos extraños provenientes del fondo...'"
        ))
        self.world_objects.append(SavePointObject(x=304, y=520))
        self.world_objects.append(SignObject(
            x=476, y=520,
            message="* CATEDRAL DE HOMETOWN: 'Avanza por la alfombra real hacia el norte para cruzar la puerta del Sótano.'"
        ))

        # Muros perimetrales dejando abierta la puerta norte al sótano (x=374..426) y la salida sur (x=370..430)
        self.solid_rects.append(pygame.Rect(0, 80, 374, 24))
        self.solid_rects.append(pygame.Rect(426, 80, 374, 24))
        self.solid_rects.append(pygame.Rect(374, 56, 52, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))

    # ==========================================================
    # 6. SÓTANO DE LA IGLESIA (UMBRAL HACIA EL DARK WORLD DE DELTARUNE)
    # ==========================================================
    def _build_church_basement(self):
        s = self.surface
        s.fill((14, 10, 22))

        # Ladrillos húmedos y muros perimetrales del sótano subterráneo
        for by in range(0, 96, 16):
            for bx in range(0, 800, 32):
                off = 16 if (by // 16) % 2 == 1 else 0
                pygame.draw.rect(s, (28, 22, 42), ((bx + off) % 800, by, 30, 14))
        for by in range(80, 600, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (26, 20, 40), (mx, by, 24, 20))
                pygame.draw.rect(s, (75, 55, 115), (mx, by, 24, 20), 1)
        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (26, 20, 40), (bx, 576, 24, 24))
            pygame.draw.rect(s, (75, 55, 115), (bx, 576, 24, 24), 1)

        # Galería Subterránea Simétrica (Cámara Central, Antecámara Sur y Altar Norte)
        pygame.draw.rect(s, (20, 16, 32), (230, 210, 340, 210), border_radius=6)
        pygame.draw.rect(s, (90, 65, 140), (230, 210, 340, 210), 2, border_radius=6)
        pygame.draw.rect(s, (22, 18, 36), (280, 444, 240, 64), border_radius=6)
        pygame.draw.rect(s, (90, 65, 140), (280, 444, 240, 64), 2, border_radius=6)

        # Camino central de baldosas desde la escalera sur (y=580) hasta la Grieta del Dark World al norte
        for gy in range(130, 580, 16):
            pygame.draw.rect(s, (28, 22, 44), (360, gy, 80, 14), border_radius=2)
            pygame.draw.rect(s, (85, 65, 125), (360, gy, 80, 14), 1, border_radius=2)

        # GRAN PORTAL / FUENTE OSCURA AL NORTE DEL SÓTANO (x=356..444, y=45..135)
        for rad, col in [(62, (35, 15, 70)), (48, (75, 25, 135)), (34, (50, 185, 235)), (20, (255, 255, 255))]:
            pygame.draw.circle(s, col, (400, 96), rad)
        pygame.draw.rect(s, (0, 0, 0), (368, 66, 64, 58), border_radius=8)
        pygame.draw.rect(s, (85, 245, 255), (368, 66, 64, 58), 3, border_radius=8)
        pygame.draw.rect(s, (255, 75, 215), (374, 72, 52, 46), 2, border_radius=6)

        # Rectángulo de transición que absorbe a Paniel hacia el Dark World
        self.dark_world_gate_rect = pygame.Rect(370, 78, 60, 48)

        self.world_objects.append(SignObject(
            x=312, y=464,
            message="* SÓTANO DE LA IGLESIA: '¡La oscuridad del fondo rebosa como una Fuente Oscura! Cruza el portal norte para entrar al DARK WORLD.'"
        ))
        self.world_objects.append(SavePointObject(x=464, y=464))

        for px, py in [(252, 224), (528, 224), (252, 356), (528, 356)]:
            self.world_objects.append(RuinPillar(px, py))

        for wx, wy, col in [(310, 250, (80, 245, 255)), (490, 250, (255, 80, 215)), (310, 375, (180, 110, 255)), (490, 375, (80, 245, 255))]:
            self.world_objects.append(WillOWisp(wx, wy, color=col))

        self.solid_rects.append(pygame.Rect(0, 80, 368, 24))
        self.solid_rects.append(pygame.Rect(432, 80, 368, 24))
        self.solid_rects.append(pygame.Rect(368, 52, 64, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))

    # ==========================================================
    # 7. DARK WORLD DE DELTARUNE (CON NUEVOS ENEMIGOS Y VENDEDOR DE "STURDY ARM")
    # ==========================================================
    def _build_dark_world(self):
        s = self.surface
        # Fondo abismal azul/índigo profundo estilo Field of Hopes and Dreams / Cyber World de Deltarune
        s.fill((10, 6, 24))

        # 1. Horizonte del Dark World con la Fuente Oscura (Dark Fountain) multicolor
        for y in range(88):
            t = y / 88.0
            pygame.draw.line(s, (int(18 + 25 * t), int(8 + 18 * t), int(48 + 42 * t)), (0, y), (800, y))

        for w_bar, col in [(90, (28, 20, 72)), (62, (55, 35, 130)), (38, (65, 185, 245)), (18, (255, 255, 255))]:
            pygame.draw.rect(s, col, (400 - w_bar // 2, 0, w_bar, 88))

        # Cuadrícula neón cian y magenta característica del Dark World de Deltarune
        for gx in range(24, 776, 40):
            pygame.draw.line(s, (38, 22, 68), (gx, 88), (gx, 576), 1)
        for gy in range(88, 576, 40):
            pygame.draw.line(s, (38, 22, 68), (24, gy), (776, gy), 1)

        # Arquitectura Organizada del Dark World:
        # 1) Ala Oeste: Terraza del Bazar del Dark World (x=124..256, y=212..348)
        pygame.draw.rect(s, (34, 14, 58), (124, 212, 136, 136), border_radius=8)
        pygame.draw.rect(s, (0, 0, 0), (124, 212, 136, 136), 4, border_radius=8)
        pygame.draw.rect(s, (255, 220, 85), (124, 212, 136, 136), 2, border_radius=8)
        # 2) Ala Este Simétrica: Mirador de Cristal Neón (x=540..676, y=212..348)
        pygame.draw.rect(s, (34, 14, 58), (540, 212, 136, 136), border_radius=8)
        pygame.draw.rect(s, (0, 0, 0), (540, 212, 136, 136), 4, border_radius=8)
        pygame.draw.rect(s, (255, 75, 215), (540, 212, 136, 136), 2, border_radius=8)
        # 3) Gran Plaza Central de la Runa Delta (x=250..550, y=160..400)
        pygame.draw.rect(s, (28, 14, 52), (250, 160, 300, 240), border_radius=8)
        pygame.draw.rect(s, (0, 0, 0), (250, 160, 300, 240), 4, border_radius=8)
        pygame.draw.rect(s, (75, 245, 255), (250, 160, 300, 240), 2, border_radius=8)
        # 4) Vestíbulo Sur de Guardado y Cofre (x=280..520, y=446..514)
        pygame.draw.rect(s, (28, 14, 52), (280, 446, 240, 68), border_radius=8)
        pygame.draw.rect(s, (0, 0, 0), (280, 446, 240, 68), 4, border_radius=8)
        pygame.draw.rect(s, (75, 245, 255), (280, 446, 240, 68), 2, border_radius=8)
        # 5) Avenida Central Norte-Sur (x=356..444, y=120..576)
        pygame.draw.rect(s, (34, 16, 62), (356, 120, 88, 456))
        pygame.draw.line(s, (255, 75, 215), (356, 120), (356, 576), 2)
        pygame.draw.line(s, (75, 245, 255), (444, 120), (444, 576), 2)

        # Emblema Delta Rune neón en el centro de la plaza del Dark World
        pygame.draw.circle(s, (255, 75, 215), (400, 280), 44, 2)
        pygame.draw.circle(s, (75, 245, 255), (400, 280), 38, 1)

        # Árboles Escarlata del Dark World (follaje carmesí/magenta y tronco negro como en Deltarune Cap. 1)
        for tx, ty in [(64, 132), (684, 132), (64, 436), (684, 436)]:
            def draw_dark_candy_tree(surf, cx, cy, w, h):
                pygame.draw.ellipse(surf, (5, 2, 14), (cx + 8, cy + 44, 36, 10))
                pygame.draw.rect(surf, (15, 10, 24), (cx + 21, cy + 28, 10, 22), border_radius=2)
                pygame.draw.circle(surf, (175, 25, 90), (cx + 26, cy + 22), 20)
                pygame.draw.circle(surf, (235, 45, 125), (cx + 24, cy + 19), 15)
                pygame.draw.circle(surf, (255, 110, 185), (cx + 21, cy + 15), 8)
            self.world_objects.append(InteriorProp(
                tx, ty, 52, 54, ty + 50, draw_dark_candy_tree,
                ["* Un Árbol Escarlata del Dark World. Sus hojas brillan con energía mágica."],
                is_solid=True,
            ))

        # VENDEDOR DEL DARK WORLD en su Terraza del Bazar (Ala Oeste)
        self.world_objects.append(DarkWorldVendorNPC(x=162, y=246))

        # Cartel junto a la entrada del Bazar y Punto de Guardado + Cofre en el Vestíbulo Sur
        self.world_objects.append(SignObject(
            x=232, y=262,
            message="* BAZAR DEL DARK WORLD: '¡Habla con el Vendedor a la izquierda con [Z] para conseguir el [Sturdy Arm] (+5 ATK, +10 DEF)!'"
        ))
        self.world_objects.append(SavePointObject(x=312, y=468))
        self.world_objects.append(ChestObject(x=464, y=468))

        for wx, wy, col in [
            (266, 176, (75, 245, 255)),
            (534, 176, (255, 75, 215)),
            (266, 384, (255, 235, 85)),
            (534, 384, (75, 245, 255)),
        ]:
            self.world_objects.append(WillOWisp(wx, wy, color=col))

        # Muros perimetrales neón del Dark World
        for bx in range(0, 800, 24):
            pygame.draw.rect(s, (22, 12, 44), (bx, 80, 24, 24))
            pygame.draw.rect(s, (75, 245, 255), (bx, 80, 24, 24), 1)
        for by in range(80, 600, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (22, 12, 44), (mx, by, 24, 20))
                pygame.draw.rect(s, (255, 75, 215), (mx, by, 24, 20), 1)
        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (22, 12, 44), (bx, 576, 24, 24))
            pygame.draw.rect(s, (75, 245, 255), (bx, 576, 24, 24), 1)

        self.solid_rects.append(pygame.Rect(0, 80, 800, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))

    # ==========================================================
    # 8. ZONA DE TUTORIAL PREVIA AL CEMENTERIO (GRAN SANTUARIO DEL TUTORIAL 800x900 DE 5 SALAS PASO A PASO)
    # ==========================================================
    def _build_tutorial_grounds(self):
        s = self.surface
        s.fill((16, 18, 30))

        # Cielo estrellado del Santuario del Tutorial
        for y in range(80):
            t = y / 80.0
            pygame.draw.line(s, (int(12 + 16 * t), int(14 + 18 * t), int(34 + 32 * t)), (0, y), (800, y))

        random.seed(123)
        for _ in range(95):
            s.set_at((random.randint(0, 799), random.randint(4, 74)), (235, 240, 255))

        # Cuadrícula arquitectónica sutil del Gran Santuario del Tutorial (800x900)
        for gx in range(24, 776, 32):
            pygame.draw.line(s, (22, 26, 44), (gx, 104), (gx, 876), 1)
        for gy in range(104, 876, 32):
            pygame.draw.line(s, (22, 26, 44), (24, gy), (776, gy), 1)

        # 1. Gran Calzada Central de Base (dibujada PRIMERO para que las 5 Salas queden limpias encima sin líneas que las corten)
        pygame.draw.rect(s, (32, 38, 62), (356, 110, 88, 766), border_radius=4)
        for gy_r in range(114, 872, 16):
            pygame.draw.line(s, (26, 30, 50), (358, gy_r), (442, gy_r), 1)
        pygame.draw.line(s, (95, 165, 245), (356, 110), (356, 876), 2)
        pygame.draw.line(s, (95, 165, 245), (444, 110), (444, 876), 2)

        # 2. Las 5 Salas Progresivas de Aprendizaje (dibujadas SOBRE la calzada con mosaico interior y pedestales simétricos):
        # Sala 1 (Sur, y=750..826): Movimiento, Correr [X/Shift] y El Guardado
        # Sala 2 (Media-Sur, y=620..696): Menú [C], Equipamiento [EQUIP], Inventario [ITEM] y Cordura [MENTE]
        # Sala 3 (Centro-Sur, y=490..566): Los 5 Botones de Combate (FIGHT, ACT/BlackFlash, ITEM, SPARE, DEFEND)
        # Sala 4 (Gran Coliseo Central, y=276..436): Los 3 Instructores Inmortales en 3 Bahías Simétricas
        # Sala 5 (Norte, y=140..216): La Tienda Dinámica del Dark World (Sturdy Arm), los Jefes y el Portal Dorado
        terrace_specs = [
            (220, 750, 360, 76, (255, 220, 85)),
            (204, 620, 392, 76, (110, 235, 255)),
            (204, 490, 392, 76, (185, 140, 255)),
            (88, 276, 624, 160, (85, 245, 165)),
            (204, 140, 392, 76, (255, 195, 95)),
        ]
        for rx, ry, rw, rh, bcol in terrace_specs:
            pygame.draw.rect(s, (26, 30, 52), (rx, ry, rw, rh), border_radius=6)
            # Mosaico interior sutil de cada sala
            for ty in range(ry + 16, ry + rh - 8, 16):
                pygame.draw.line(s, (32, 36, 62), (rx + 6, ty), (rx + rw - 6, ty), 1)
            for tx in range(rx + 24, rx + rw - 12, 24):
                pygame.draw.line(s, (32, 36, 62), (tx, ry + 6), (tx, ry + rh - 6), 1)
            # Alfombra central de paso dentro de la sala
            pygame.draw.rect(s, (38, 44, 74), (364, ry + 4, 72, rh - 8))
            pygame.draw.line(s, (70, 115, 185), (364, ry + 4), (364, ry + rh - 4), 1)
            pygame.draw.line(s, (70, 115, 185), (436, ry + 4), (436, ry + rh - 4), 1)
            pygame.draw.rect(s, (10, 12, 24), (rx, ry, rw, rh), 4, border_radius=6)
            pygame.draw.rect(s, bcol, (rx, ry, rw, rh), 2, border_radius=6)

        # Pedestales de piedra enmarcados para los carteles y punto de guardado de las Salas 1, 2, 3 y 5
        for ped_x, ped_y, ped_col in [
            (254, 768, (255, 220, 85)), (510, 768, (255, 220, 85)),
            (242, 638, (110, 235, 255)), (522, 638, (110, 235, 255)),
            (242, 508, (185, 140, 255)), (522, 508, (185, 140, 255)),
            (242, 158, (255, 195, 95)), (522, 158, (255, 195, 95)),
        ]:
            pygame.draw.rect(s, (18, 22, 38), (ped_x, ped_y, 36, 36), border_radius=4)
            pygame.draw.rect(s, ped_col, (ped_x, ped_y, 36, 36), 1, border_radius=4)

        # 3. Tres Bahías de Entrenamiento Simétricas en la Sala 4 (Gran Coliseo Central):
        # Cada bahía tiene su pedestal de cartel a la izquierda y su círculo de combate a la derecha,
        # dejando 2 corredores amplios y toda la galería inferior despejados para caminar.
        bay_specs = [
            (120, 320, 196, 332, (95, 225, 255)),   # Bahía 1 (Izquierda): Esquiva
            (324, 320, 400, 332, (65, 250, 130)),   # Bahía 2 (Centro): Parry [Z]
            (528, 320, 604, 332, (255, 210, 80)),   # Bahía 3 (Derecha): Dash [X]
        ]
        for ped_x, ped_y, cx, cy, col in bay_specs:
            # Pedestal del cartel del instructor
            pygame.draw.rect(s, (18, 22, 38), (ped_x, ped_y - 4, 32, 32), border_radius=4)
            pygame.draw.rect(s, col, (ped_x, ped_y - 4, 32, 32), 1, border_radius=4)
            # Línea conectora entre el cartel y el círculo del instructor
            pygame.draw.line(s, col, (ped_x + 32, cy), (cx - 34, cy), 1)
            # Círculo de entrenamiento del instructor
            pygame.draw.circle(s, (18, 20, 36), (cx, cy), 34)
            pygame.draw.circle(s, col, (cx, cy), 34, 2)
            pygame.draw.circle(s, col, (cx, cy), 24, 1)

        # PORTAL DORADO AL NORTE (Sellado hasta completar las 3 pruebas 4/4 de los Instructores)
        pygame.draw.rect(s, (28, 22, 48), (362, 58, 76, 62), border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.rect(s, (10, 14, 28), (370, 66, 60, 54), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.rect(s, (255, 230, 85), (362, 58, 76, 62), 3, border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.circle(s, (110, 235, 255), (400, 92), 16, 2)
        self.tutorial_exit_gate_rect = pygame.Rect(370, 74, 60, 46)

        # ----------------------------------------------------------
        # SALA 1 (SUR, y=774): MOVIMIENTO, CORRER Y EL GUARDADO
        # ----------------------------------------------------------
        self.world_objects.append(SavePointObject(x=262, y=774))
        self.world_objects.append(SignObject(
            x=520, y=774,
            message=(
                "* [SALA 1/5 - MOVIMIENTO Y EL GUARDADO]:\n"
                "* • MOVERSE Y CORRER: Usa [Flechas / WASD] para caminar y mantén [X] o [SHIFT] para correr.\n"
                "* • ¿DÓNDE SE GUARDA?: En las Estrellas Amarillas como la que tienes a la izquierda (están en la entrada del cementerio, cruces, la iglesia y antes de cada Jefe).\n"
                "* • ¿QUÉ HACE EL GUARDADO?: Guarda tu partida, cura tu HP al 100% y restaura +25% de Cordura."
            ),
        ))

        # ----------------------------------------------------------
        # SALA 2 (MEDIA-SUR, y=644): MENÚ [C], EQUIPAR ARMAS/ARMADURAS Y CORDURA
        # ----------------------------------------------------------
        self.world_objects.append(SignObject(
            x=252, y=644,
            message=(
                "* [SALA 2/5 - MENÚ [C] Y EQUIPAMIENTO (EQUIP)]:\n"
                "* • Pulsa [C] fuera de combate para abrir tu Menú de Exploración.\n"
                "* • En la pestaña [EQUIP] puedes equipar ARMAS y hasta 2 ARMADURAS/RELIQUIAS viendo cómo suben tu ATK y DEF en tiempo real.\n"
                "* • En la pestaña [ITEM] puedes usar consumibles para curar HP y Cordura."
            ),
        ))
        self.world_objects.append(SignObject(
            x=532, y=644,
            message=(
                "* [SALA 2/5 - CORDURA Y ESTADOS EMOCIONALES]:\n"
                "* • En la esquina inferior derecha ves el rostro de Paniel y su CORDURA (100% a 0%).\n"
                "* • FELIZ: Equilibrado | TRISTE: -3 ATK, +2 DEF | TRAUMADO: -2 ATK, -3 DEF | LOCO: ¡+8 ATK, -4 DEF!\n"
                "* • Morir en combate o ver horrores reduce tu cordura; guardar o rezar en la iglesia la recupera."
            ),
        ))

        # ----------------------------------------------------------
        # SALA 3 (CENTRO-SUR, y=514): LOS 5 BOTONES DE COMBATE (FIGHT, ACT, ITEM, SPARE, DEFEND)
        # ----------------------------------------------------------
        self.world_objects.append(SignObject(
            x=252, y=514,
            message=(
                "* [SALA 3/5 - FIGHT, ACT (HABILIDADES MÁGICAS) E ITEM]:\n"
                "* • FIGHT (Pelear): Pulsa [Z] justo cuando la barra blanca cruce la mira azul para un golpe crítico.\n"
                "* • ACT (Actuar y Magia TP): Habla con enemigos para subir su MERCY, o gasta TP en Habilidades Mágicas como ★ BlackFlash (50%TP, pulsa [Z] cuando el anillo se cierre en la diana estilo Clover para un doble impacto), Tajo Ánima, Calma Mental y Pacificar.\n"
                "* • ITEM (Objetos): Usa comida o pociones en tu turno."
            ),
        ))
        self.world_objects.append(SignObject(
            x=532, y=514,
            message=(
                "* [SALA 3/5 - SPARE (PERDONAR) Y DEFEND (DEFENDER)]:\n"
                "* • SPARE (Perdonar): Cuando la barra amarilla de MERCY del enemigo llega al 100% (★), puedes elegir SPARE para ganar el combate pacíficamente recibiendo EXP y D$.\n"
                "* • DEFEND (Defender): Alza un escudo azul que reduce el daño recibido ese turno y carga +25% de TP de inmediato."
            ),
        ))

        # ----------------------------------------------------------
        # SALA 4 (GRAN COLISEO CENTRAL, y=320): LOS 3 INSTRUCTORES CON PRUEBA OBLIGATORIA 4/4
        # ----------------------------------------------------------
        self.world_objects.append(SignObject(
            x=128, y=320,
            message=(
                "* [INSTRUCTOR 1 - PRUEBA DE ESQUIVA (4/4)]:\n"
                "* • Lanza barreras azules con un HUECO VERDE.\n"
                "* • Debes mover tu corazón hacia el HUECO VERDE y cruzar 4 barreras sin recibir daño (4/4) para que su MERCY suba a 100% y puedas usar SPARE."
            ),
        ))
        self.world_objects.append(SignObject(
            x=332, y=320,
            message=(
                "* [INSTRUCTOR 2 - PRUEBA DE PARRY [Z] (4/4)]:\n"
                "* • Lanza esferas verdes que persiguen tu corazón.\n"
                "* • Cuando la esfera esté cerca (su anillo brilla en amarillo), pulsa [Z] para activar tu Escudo Verde. ¡Bloquea 4 esferas (4/4) para poder usar SPARE!"
            ),
        ))
        self.world_objects.append(SignObject(
            x=536, y=320,
            message=(
                "* [INSTRUCTOR 3 - PRUEBA DE DASH [X] (4/4)]:\n"
                "* • Lanza muros dorados que cubren TODA la arena sin huecos.\n"
                "* • Camina hacia el muro dorado y pulsa [X] para ATRAVESARLO con la invulnerabilidad del Dash. ¡Cruza 4 muros (4/4) para poder usar SPARE!"
            ),
        ))

        # ----------------------------------------------------------
        # SALA 5 (NORTE, y=164): LA TIENDA DEL DARK WORLD, LOS JEFES Y EL PORTAL DORADO
        # ----------------------------------------------------------
        self.world_objects.append(SignObject(
            x=252, y=164,
            message=(
                "* [SALA 5/5 - LA IGLESIA Y LA TIENDA DEL DARK WORLD]:\n"
                "* • Dentro del Cementerio, ve hacia el ESTE para entrar a la CATEDRAL y baja a su SÓTANO para entrar al DARK WORLD.\n"
                "* • En el Bazar del Dark World habla con el Vendedor para abrir su menú de tienda estilo Deltarune y comprar el [Sturdy Arm] (+5 ATK y +10 DEF)."
            ),
        ))
        self.world_objects.append(SignObject(
            x=532, y=164,
            message=(
                "* [SALA 5/5 - LOS JEFES Y EL PORTAL DE GRADUACIÓN]:\n"
                "* • En el Cementerio y el Santuario del Cristal Quebrado aguardan JEFES (Morvath y Vaelkor) con ataques muy erráticos que exigen combinar Esquiva, Parry [Z], Dash [X] y ★ BlackFlash.\n"
                "* • ¡IMPORTANTE!: El PORTAL DORADO DEL NORTE solo se abrirá cuando hayas completado las 3 pruebas (4/4) de los 3 Instructores."
            ),
        ))

        # Pilares y faroles espectrales simétricos a lo largo de las 5 salas del santuario
        for px, py in [(116, 266), (664, 266), (116, 412), (664, 412), (196, 610), (584, 610), (196, 740), (584, 740)]:
            self.world_objects.append(RuinPillar(px, py))
        for wx, wy, col in [
            (225, 178, (95, 225, 255)), (575, 178, (255, 210, 80)),
            (225, 528, (185, 140, 255)), (575, 528, (185, 140, 255)),
            (225, 788, (95, 225, 255)), (575, 788, (65, 250, 130)),
        ]:
            self.world_objects.append(WillOWisp(wx, wy, color=col))

        # Muros perimetrales (800x900) dejando abierto el Portal Norte (x=370..430)
        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (42, 48, 76), (bx, 80, 24, 24))
            pygame.draw.rect(s, (95, 165, 245), (bx, 80, 24, 24), 1)
        for bx in range(0, 800, 24):
            pygame.draw.rect(s, (42, 48, 76), (bx, 876, 24, 24))
            pygame.draw.rect(s, (95, 165, 245), (bx, 876, 24, 24), 1)
        for by in range(80, 900, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (42, 48, 76), (mx, by, 24, 20))
                pygame.draw.rect(s, (95, 165, 245), (mx, by, 24, 20), 1)

        self.solid_rects.append(pygame.Rect(0, 80, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 80, 370, 24))
        self.solid_rects.append(pygame.Rect(370, 52, 60, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 820))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 820))
        self.solid_rects.append(pygame.Rect(0, 876, 800, 24))


