import os
import math
import random
import pygame
from configuracion import VIRTUAL_WIDTH, VIRTUAL_HEIGHT
from objetos_mundo import (
    SavePointObject,
    SignObject,
    ChestObject,
    RuinPillar,
    WillOWisp,
    TwistedTreeProp,
    GothicLampPost,
    GothicBrazier,
    CemeteryCandleProp,
    InteriorProp,
    DarkWorldVendorNPC,
)

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

        # Capa ambiental animada (niebla en movimiento, luciérnagas, pétalos y miasma de la Bruja)
        self.ambient_time = 0.0
        self.ambient_particles = []
        self._fog_band_surf = None
        self._vignette_surf = None

        self._build_scene()
        self._init_ambient_atmosphere()

    def _init_ambient_atmosphere(self):
        """Prepara niebla animada, luciérnagas, pétalos o miasma según la zona del cementerio."""
        if self.scene_id not in ("cemetery", "cemetery_church_section", "cemetery_depths", "eclipse_sanctuary", "dark_world", "dark_world_throne"):
            return

        rng = random.Random(hash(self.scene_id) & 0xFFFF)
        is_abyss = self.scene_id in ("cemetery_depths", "eclipse_sanctuary")
        is_dw = self.scene_id in ("dark_world", "dark_world_throne")
        count = 56 if is_dw else (48 if not is_abyss else 54)

        for _ in range(count):
            if is_dw:
                kind = rng.choice(["spark", "spark", "miasma", "ember"])
                col = rng.choice([(80, 245, 255), (255, 75, 215), (255, 232, 85), (170, 95, 255)])
            elif is_abyss:
                kind = rng.choice(["miasma", "miasma", "ember", "spark"])
                col = (170, 55, 225) if kind == "miasma" else ((255, 75, 115) if kind == "ember" else (245, 185, 255))
            else:
                kind = rng.choice(["firefly", "firefly", "petal", "mote"])
                col = (245, 230, 125) if kind == "firefly" else ((185, 215, 255) if kind == "petal" else (140, 245, 225))
            self.ambient_particles.append({
                "x": rng.uniform(16, self.pixel_w - 16),
                "y": rng.uniform(86, self.pixel_h - 16),
                "vx": rng.uniform(-10.0, 10.0) if kind != "petal" else rng.uniform(-14.0, -5.0),
                "vy": rng.uniform(-18.0, -6.0) if (is_abyss or is_dw) else (rng.uniform(4.0, 11.0) if kind == "petal" else rng.uniform(-6.0, 6.0)),
                "phase": rng.uniform(0, math.tau),
                "size": rng.uniform(1.4, 3.0) if kind == "miasma" else rng.uniform(1.0, 2.2),
                "kind": kind,
                "color": col,
            })

        # Banda de niebla suave reutilizable (400x48)
        fog = pygame.Surface((VIRTUAL_WIDTH, 48), pygame.SRCALPHA)
        fog_col = (80, 35, 165) if is_dw else ((130, 35, 165) if is_abyss else (155, 185, 225))
        for fy in range(48):
            dist = abs(fy - 24) / 24.0
            a = int((1.0 - dist * dist) * (22 if is_dw else (20 if is_abyss else 16)))
            if a > 0:
                pygame.draw.line(fog, (*fog_col, a), (0, fy), (VIRTUAL_WIDTH, fy))
        self._fog_band_surf = fog

        # Viñeta sutil nocturna en los bordes de la pantalla virtual (400x300)
        vig = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        v_col = (14, 4, 24) if is_abyss else (6, 10, 22)
        for border in range(28):
            alpha = int(((28 - border) / 28.0) ** 2 * (76 if is_abyss else 52))
            pygame.draw.rect(vig, (*v_col, alpha), (border, border, VIRTUAL_WIDTH - border * 2, VIRTUAL_HEIGHT - border * 2), 1)
        self._vignette_surf = vig

    def update_ambient(self, dt):
        """Actualiza las partículas atmosféricas del cementerio."""
        if not self.ambient_particles:
            return
        self.ambient_time += dt
        for p in self.ambient_particles:
            p["phase"] += dt * 2.2
            p["x"] += (p["vx"] + math.sin(p["phase"]) * 6.0) * dt
            p["y"] += (p["vy"] + math.cos(p["phase"] * 0.8) * 3.5) * dt
            if p["x"] < 10:
                p["x"] = self.pixel_w - 14
            elif p["x"] > self.pixel_w - 10:
                p["x"] = 14
            if p["y"] < 80:
                p["y"] = self.pixel_h - 14
            elif p["y"] > self.pixel_h - 10:
                p["y"] = 86

    def draw_overlay(self, surface, camera):
        """Dibuja niebla en movimiento, luciérnagas/miasma y viñeta atmosférica sobre la escena."""
        if not self.ambient_particles and self._fog_band_surf is None:
            return

        # 1. Niebla baja desplazándose suavemente
        if self._fog_band_surf is not None:
            drift1 = int((self.ambient_time * 9.0) % VIRTUAL_WIDTH)
            drift2 = int((self.ambient_time * -6.0) % VIRTUAL_WIDTH)
            for row_i, world_y in enumerate((215, 365, 500)):
                sy = int(world_y - camera.y)
                if -56 < sy < VIRTUAL_HEIGHT + 16:
                    dx = drift1 if row_i % 2 == 0 else drift2
                    surface.blit(self._fog_band_surf, (dx - VIRTUAL_WIDTH, sy))
                    surface.blit(self._fog_band_surf, (dx, sy))

        # 2. Luciérnagas, pétalos nocturnos o volutas de miasma de la Bruja
        for p in self.ambient_particles:
            sx, sy = camera.apply((p["x"], p["y"]))
            if -12 <= sx <= VIRTUAL_WIDTH + 12 and -12 <= sy <= VIRTUAL_HEIGHT + 12:
                pulse = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p["phase"] * 1.8))
                col = p["color"]
                if p["kind"] == "miasma":
                    r = max(2, int(p["size"] * 2.2))
                    ms = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(ms, (15, 4, 24, int(95 * pulse)), (r + 1, r + 1), r)
                    pygame.draw.circle(ms, (*col, int(115 * pulse)), (r + 1, r + 1), max(1, r - 1), 1)
                    surface.blit(ms, (int(sx) - r - 1, int(sy) - r - 1))
                elif p["kind"] == "petal":
                    ps = pygame.Surface((5, 4), pygame.SRCALPHA)
                    pygame.draw.ellipse(ps, (*col, int(185 * pulse)), (0, 0, 4, 3))
                    surface.blit(ps, (int(sx), int(sy)))
                else:
                    r = max(2, int(p["size"] * 2.4))
                    gs = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(gs, (*col, int(55 * pulse)), (r + 1, r + 1), r)
                    pygame.draw.circle(gs, (255, 255, 240, int(215 * pulse)), (r + 1, r + 1), 1)
                    surface.blit(gs, (int(sx) - r - 1, int(sy) - r - 1))

        # 3. Viñeta cinematográfica suave
        if self._vignette_surf is not None:
            surface.blit(self._vignette_surf, (0, 0))

    # ----------------------------------------------------------
    # UTILIDADES ARTÍSTICAS PARA EL CEMENTERIO GÓTICO
    # ----------------------------------------------------------
    def _paint_gothic_sky(self, s, w, sky_h=78, moon_pos=(680, 34), theme="moonlit", seed=42):
        rng = random.Random(seed)
        for y in range(sky_h):
            t = y / float(sky_h)
            if theme == "abyss":
                r = int(16 + (42 - 16) * (t ** 1.3))
                g = int(4 + (10 - 4) * t)
                b = int(26 + (54 - 26) * t)
            else:
                r = int(6 + (28 - 6) * (t ** 1.2))
                g = int(8 + (28 - 8) * (t ** 1.2))
                b = int(22 + (58 - 22) * t)
            pygame.draw.line(s, (r, g, b), (0, y), (w, y))

        # Estrellas con varios niveles de brillo y tintes fríos
        for _ in range(115):
            sx = rng.randint(2, w - 3)
            sy = rng.randint(2, sky_h - 14)
            bv = rng.randint(155, 255)
            if theme == "abyss":
                col = rng.choice([(bv, int(bv * 0.55), int(bv * 0.72)), (int(bv * 0.8), int(bv * 0.55), bv)])
            else:
                col = rng.choice([(bv, bv, bv), (bv - 25, bv - 10, 255), (255, bv, bv - 30)])
            s.set_at((sx, sy), col)

        # Destellos en cruz para estrellas principales
        star_coords = [(62, 18), (154, 12), (246, 26), (344, 14), (455, 22), (558, 13), (748, 22)]
        for csx, csy in star_coords:
            c_st = (255, 190, 215) if theme == "abyss" else (245, 250, 255)
            pygame.draw.line(s, c_st, (csx - 2, csy), (csx + 2, csy), 1)
            pygame.draw.line(s, c_st, (csx, csy - 2), (csx, csy + 2), 1)
            s.set_at((csx, csy), (255, 255, 255))

        # Nubes nocturnas translúcidas desplazándose cerca del horizonte y la luna
        cloud_surf = pygame.Surface((w, sky_h), pygame.SRCALPHA)
        cloud_col = (58, 18, 68, 52) if theme == "abyss" else (48, 58, 96, 48)
        cloud_hi = (175, 65, 125, 36) if theme == "abyss" else (165, 190, 235, 34)
        for cx_c, cy_c, cw_c, ch_c in [
            (40, 26, 120, 18), (195, 36, 145, 20), (370, 22, 130, 16),
            (545, 34, 150, 20), (640, 18, 130, 18), (110, 50, 180, 16), (480, 52, 190, 18),
        ]:
            pygame.draw.ellipse(cloud_surf, cloud_col, (cx_c, cy_c, cw_c, ch_c))
            pygame.draw.ellipse(cloud_surf, cloud_hi, (cx_c + 12, cy_c + 2, cw_c - 24, ch_c // 2))
        s.blit(cloud_surf, (0, 0))

        # Luna llena detallada (o Eclipse Carmesí en el Abismo)
        mx, my = moon_pos
        if theme == "abyss":
            for rad, alpha in [(54, 18), (36, 42), (24, 88)]:
                halo = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (220, 35, 88, alpha), (rad, rad), rad)
                s.blit(halo, (mx - rad, my - rad))
            pygame.draw.circle(s, (255, 105, 140), (mx, my), 16, 2)
            pygame.draw.circle(s, (255, 215, 230), (mx - 6, my - 6), 3)
            pygame.draw.circle(s, (10, 4, 18), (mx, my), 14)
        else:
            for rad, alpha in [(58, 12), (42, 24), (28, 48), (20, 82)]:
                halo = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (185, 215, 255, alpha), (rad, rad), rad)
                s.blit(halo, (mx - rad, my - rad))
            pygame.draw.circle(s, (248, 246, 234), (mx, my), 16)
            pygame.draw.circle(s, (226, 224, 212), (mx - 5, my - 3), 5)
            pygame.draw.circle(s, (218, 216, 204), (mx + 5, my + 4), 4)
            pygame.draw.circle(s, (212, 210, 198), (mx - 2, my + 7), 3)
            pygame.draw.circle(s, (255, 255, 248), (mx - 6, my - 7), 2)

        # Dos planos de siluetas góticas en el horizonte (colinas brumosas, cipreses y agujas lejanas)
        far_col = (20, 14, 34) if theme == "abyss" else (18, 22, 40)
        near_col = (11, 7, 20) if theme == "abyss" else (10, 13, 24)
        # Colinas suaves de fondo
        hill_pts = [(0, sky_h), (0, sky_h - 14), (110, sky_h - 24), (240, sky_h - 15),
                    (380, sky_h - 26), (520, sky_h - 18), (660, sky_h - 24), (800, sky_h - 14), (800, sky_h)]
        pygame.draw.polygon(s, far_col, hill_pts)
        # Cipreses, catedrales y agujas en primer plano
        for bx in range(12, w - 10, 44):
            h_sp = rng.randint(18, 36)
            if (bx // 44) % 4 == 1:
                # Aguja gótica lejana
                pygame.draw.rect(s, near_col, (bx - 5, sky_h - h_sp + 12, 10, h_sp - 12))
                pygame.draw.polygon(s, near_col, [(bx - 6, sky_h - h_sp + 12), (bx, sky_h - h_sp), (bx + 6, sky_h - h_sp + 12)])
                pygame.draw.line(s, near_col, (bx, sky_h - h_sp - 5), (bx, sky_h - h_sp), 1)
            else:
                # Ciprés esbelto
                pygame.draw.polygon(s, near_col, [(bx - 6, sky_h), (bx, sky_h - h_sp), (bx + 6, sky_h)])

    def _paint_textured_cemetery_ground(self, s, w, h, top_y=100, theme="moonlit", seed=42):
        rng = random.Random(seed)
        if theme == "abyss":
            s.fill((12, 8, 20))
            patch_cols = [(18, 11, 28), (24, 14, 36), (15, 10, 24), (30, 14, 42)]
            tuft_cols = [(44, 22, 62), (68, 26, 84), (28, 16, 42)]
        else:
            s.fill((17, 23, 23))
            patch_cols = [(22, 31, 29), (14, 19, 21), (26, 36, 33), (19, 28, 31)]
            tuft_cols = [(32, 50, 42), (44, 68, 54), (25, 38, 36), (56, 82, 66)]

        # Manchas suaves de musgo, humedad y sombras nocturnas en el terreno
        for _ in range(85):
            px = rng.randint(12, w - 12)
            py = rng.randint(top_y + 6, h - 18)
            rx = rng.randint(24, 68)
            ry = rng.randint(14, 36)
            pygame.draw.ellipse(s, rng.choice(patch_cols), (px - rx // 2, py - ry // 2, rx, ry))

        # Briznas de hierba / grietas minerales delicadas
        for _ in range(320):
            gx = rng.randint(26, w - 26)
            gy = rng.randint(top_y + 4, h - 26)
            tc = rng.choice(tuft_cols)
            if theme == "abyss":
                pygame.draw.line(s, tc, (gx, gy), (gx + rng.randint(-4, 4), gy + rng.randint(-2, 3)), 1)
                if rng.random() < 0.14:
                    s.set_at((gx, gy), (145, 45, 120))
            else:
                pygame.draw.line(s, tc, (gx, gy), (gx - 2, gy - 3), 1)
                pygame.draw.line(s, tc, (gx, gy), (gx, gy - 4), 1)
                pygame.draw.line(s, tc, (gx, gy), (gx + 2, gy - 3), 1)

        # Guijarros diminutos y pétalos caídos en el césped
        if theme != "abyss":
            for _ in range(55):
                px = rng.randint(30, w - 30)
                py = rng.randint(top_y + 8, h - 30)
                c_pet = rng.choice([(135, 165, 205), (190, 175, 110), (96, 102, 118)])
                s.set_at((px, py), c_pet)
                if rng.random() < 0.45:
                    s.set_at((px + 1, py), c_pet)

    def _paint_ornate_gothic_walls(self, s, w, h, top_y=76, open_south=True, open_east=False, open_west=False, theme="moonlit", seed=42):
        rng = random.Random(seed + 10)
        if theme == "abyss":
            b_lo, b_hi = 36, 52
            tint = (0, -8, 14)
            outline = (16, 10, 26)
            iron = (135, 36, 78)
            iron_hi = (225, 75, 125)
        else:
            b_lo, b_hi = 68, 86
            tint = (0, 2, 10)
            outline = (30, 32, 42)
            iron = (34, 36, 46)
            iron_hi = (98, 104, 124)

        def draw_stone_block(bx, by, bw, bh):
            sh = rng.randint(b_lo, b_hi)
            col = (max(0, min(255, sh + tint[0])), max(0, min(255, sh + tint[1])), max(0, min(255, sh + tint[2])))
            hi = (min(255, col[0] + 22), min(255, col[1] + 24), min(255, col[2] + 28))
            lo = (max(0, col[0] - 20), max(0, col[1] - 20), max(0, col[2] - 18))
            pygame.draw.rect(s, col, (bx, by, bw, bh))
            pygame.draw.line(s, hi, (bx + 1, by + 1), (bx + bw - 2, by + 1), 1)
            pygame.draw.line(s, lo, (bx + 1, by + bh - 2), (bx + bw - 2, by + bh - 2), 1)
            pygame.draw.rect(s, outline, (bx, by, bw, bh), 1)

        # Muro Norte + Reja de hierro forjado ornamental
        for bx in range(0, w, 24):
            draw_stone_block(bx, top_y, 24, 24)
            # Reja de hierro con dos lanzas por bloque y barra transversal
            for sx in (bx + 6, bx + 18):
                pygame.draw.line(s, iron, (sx, top_y - 16), (sx, top_y), 2)
                pygame.draw.polygon(s, iron_hi, [(sx - 2, top_y - 14), (sx, top_y - 20), (sx + 2, top_y - 14)])
            pygame.draw.line(s, iron, (bx, top_y - 10), (bx + 24, top_y - 10), 1)
            pygame.draw.line(s, iron, (bx, top_y - 4), (bx + 24, top_y - 4), 1)

        # Pilares de piedra con remate gótico cada 96px a lo largo del muro norte
        for px in range(24, w, 96):
            if 320 <= px <= 480:
                continue
            pygame.draw.rect(s, (58, 60, 74) if theme != "abyss" else (42, 24, 56), (px - 6, top_y - 18, 12, 42))
            pygame.draw.rect(s, outline, (px - 6, top_y - 18, 12, 42), 1)
            pygame.draw.polygon(s, iron_hi, [(px - 7, top_y - 18), (px, top_y - 26), (px + 7, top_y - 18)])

        # Muros laterales
        for by in range(top_y, h, 20):
            if not (open_west and 316 <= by <= 368):
                draw_stone_block(0, by, 24, 20)
            if not (open_east and 316 <= by <= 368):
                draw_stone_block(w - 24, by, 24, 20)

        # Muro inferior
        for bx in range(0, w, 24):
            if open_south and 366 <= bx < 430:
                continue
            draw_stone_block(bx, h - 24, 24, 24)

        # Guirnaldas de hiedra y musgo colgando de los muros
        ivy_dark = (32, 58, 40) if theme != "abyss" else (66, 22, 74)
        ivy_hi = (56, 98, 64) if theme != "abyss" else (138, 42, 120)
        for ix, iy in [(48, top_y + 6), (170, top_y + 8), (264, top_y + 5), (536, top_y + 7),
                       (640, top_y + 6), (735, top_y + 8), (22, 210), (22, 445), (778, 205), (778, 455)]:
            for dxi, dyi, ri in [(0, 0, 5), (4, 4, 4), (-3, 5, 4), (2, 10, 3), (-2, 14, 2)]:
                pygame.draw.circle(s, ivy_dark, (ix + dxi, iy + dyi), ri)
            pygame.draw.circle(s, ivy_hi, (ix + 1, iy + 1), 3)
            pygame.draw.circle(s, ivy_hi, (ix - 2, iy + 6), 2)

    def _paint_cobblestone_avenue(self, s, rx, ry, rw, rh, style="moonlit", seed=11):
        rng = random.Random(seed + rx + ry)
        if style == "abyss":
            curb_out = (145, 38, 82)
            curb_in = (34, 20, 48)
            base_sh = (36, 26, 52)
            hi_delta = 18
            mortar = (16, 10, 26)
        else:
            curb_out = (106, 112, 130)
            curb_in = (42, 46, 56)
            base_sh = (60, 63, 74)
            hi_delta = 18
            mortar = (28, 30, 38)

        # Sombra sutil bajo el bordillo
        pygame.draw.rect(s, (10, 12, 16), (rx - 4, ry - 2, rw + 8, rh + 8), border_radius=5)
        pygame.draw.rect(s, curb_in, (rx - 3, ry - 3, rw + 6, rh + 6), border_radius=4)
        pygame.draw.rect(s, curb_out, (rx - 3, ry - 3, rw + 6, rh + 6), 2, border_radius=4)

        row_idx = 0
        for gy in range(ry, ry + rh, 12):
            off = 8 if (row_idx % 2 == 1) else 0
            row_idx += 1
            gx = rx - off
            while gx < rx + rw:
                sx1 = max(rx, gx)
                sx2 = min(rx + rw, gx + 15)
                cw = sx2 - sx1
                ch = min(11, ry + rh - gy)
                if cw > 2 and ch > 2:
                    d = rng.randint(-9, 10)
                    c = (max(0, min(255, base_sh[0] + d)), max(0, min(255, base_sh[1] + d - 1)), max(0, min(255, base_sh[2] + d + 2)))
                    hi = (min(255, c[0] + hi_delta), min(255, c[1] + hi_delta), min(255, c[2] + hi_delta + 4))
                    pygame.draw.rect(s, c, (sx1, gy, cw, ch), border_radius=2)
                    pygame.draw.line(s, hi, (sx1 + 1, gy + 1), (sx1 + cw - 2, gy + 1), 1)
                    pygame.draw.rect(s, mortar, (sx1, gy, cw, ch), 1, border_radius=2)
                    # Pequeño brote de musgo ocasional entre adoquines
                    if style != "abyss" and rng.random() < 0.08:
                        pygame.draw.circle(s, (48, 86, 56), (sx1 + 1, gy + ch - 1), 2)
                gx += 16

    def _paint_flower_patch(self, s, fx, fy, color=(95, 175, 255), core=(230, 248, 255), count=3):
        """Dibuja un delicado ramillete de flores nocturnas con hojas y suave halo luminoso."""
        glow = pygame.Surface((26, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*color, 34), (0, 2, 26, 16))
        s.blit(glow, (fx - 13, fy - 8))
        offsets = [(-5, 1), (0, -2), (5, 2), (-2, 4), (4, -2)][:count]
        for ox, oy in offsets:
            pygame.draw.line(s, (38, 86, 48), (fx + ox, fy + oy + 1), (fx + ox, fy + oy + 5), 1)
            pygame.draw.ellipse(s, (46, 102, 56), (fx + ox - 3, fy + oy + 2, 3, 2))
            pygame.draw.circle(s, color, (fx + ox, fy + oy), 3)
            pygame.draw.circle(s, core, (fx + ox, fy + oy), 1)

    def _paint_decorative_minor_grave(self, s, gx, gy, tilt=0):
        """Dibuja pequeñas lápidas o cruces musgosas de fondo para enriquecer el paisaje sin estorbar."""
        pygame.draw.ellipse(s, (10, 14, 15), (gx - 2, gy + 12, 16, 6))
        if tilt == 0:
            pygame.draw.rect(s, (70, 74, 86), (gx, gy, 12, 15), border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.line(s, (108, 114, 130), (gx + 2, gy + 2), (gx + 2, gy + 13), 1)
            pygame.draw.rect(s, (34, 36, 44), (gx, gy, 12, 15), 1, border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.line(s, (46, 48, 58), (gx + 3, gy + 6), (gx + 9, gy + 6), 1)
            pygame.draw.line(s, (46, 48, 58), (gx + 4, gy + 9), (gx + 8, gy + 9), 1)
            pygame.draw.circle(s, (48, 88, 56), (gx + 2, gy + 13), 2)
        else:
            # Cruz inclinada de piedra antigua
            pygame.draw.line(s, (32, 34, 42), (gx + 6, gy), (gx + 6 + tilt, gy + 15), 4)
            pygame.draw.line(s, (82, 86, 100), (gx + 6, gy), (gx + 6 + tilt, gy + 15), 2)
            pygame.draw.line(s, (32, 34, 42), (gx + 1, gy + 5), (gx + 11, gy + 5 - tilt // 2), 4)
            pygame.draw.line(s, (96, 100, 116), (gx + 1, gy + 5), (gx + 11, gy + 5 - tilt // 2), 2)

    def _build_scene(self):
        if self.scene_id == "cemetery":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = None
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
        elif self.scene_id == "dark_world_throne":
            self.pixel_w = 800
            self.pixel_h = 600
            self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
            self.exit_rect = pygame.Rect(370, 580, 60, 20)
            self._build_dark_world_throne()
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

    # 2. INTERIOR DEL CEMENTERIO (Versión Gótica Monumental, Expandida 800x600 y Hermosa)
    def _build_cemetery(self):
        s = self.surface

        # 1. CÉSPED NOCTURNO TEXTURIZADO CON MUSGO, SOMBRAS Y BRIZNAS DE HIERBA
        self._paint_textured_cemetery_ground(s, 800, 600, top_y=100, theme="moonlit", seed=42)

        # 2. CIELO NOCTURNO CINEMATOGRÁFICO CON NUBES, LUNA LLENA Y SILUETAS GÓTICAS
        self._paint_gothic_sky(s, 800, sky_h=78, moon_pos=(678, 34), theme="moonlit", seed=42)

        # Rayos diagonales de luna bañando el camposanto (volumetric moonlight)
        moon_cx, moon_cy = 678, 34
        rays = pygame.Surface((800, 600), pygame.SRCALPHA)
        pygame.draw.polygon(rays, (195, 220, 255, 13), [(moon_cx, moon_cy), (355, 600), (545, 600)])
        pygame.draw.polygon(rays, (185, 215, 255, 9), [(moon_cx, moon_cy), (125, 600), (295, 600)])
        pygame.draw.polygon(rays, (195, 220, 255, 10), [(moon_cx, moon_cy), (575, 600), (770, 600)])
        s.blit(rays, (0, 0))

        # 3. MUROS PERIMETRALES DE SILLERÍA CON REJA DE HIERRO FORJADO Y HIEDRA
        self._paint_ornate_gothic_walls(s, 800, 600, top_y=76, open_south=True, open_east=True, open_west=False, theme="moonlit", seed=42)

        # 4. CAMINOS DE ADOQUINES DESGASTADOS Y PARCELAS MONUMENTALES
        def draw_monument_plot(px, py, pw, ph):
            """Dibuja una parcela gótica elevada con bordillo biselado, musgo y sombra."""
            pygame.draw.rect(s, (10, 14, 15), (px - 2, py + 2, pw + 4, ph + 2), border_radius=5)
            pygame.draw.rect(s, (26, 33, 33), (px, py, pw, ph), border_radius=4)
            pygame.draw.rect(s, (34, 42, 42), (px + 4, py + 4, pw - 8, ph - 8), border_radius=3)
            pygame.draw.rect(s, (98, 104, 122), (px, py, pw, ph), 2, border_radius=4)
            pygame.draw.line(s, (134, 142, 164), (px + 2, py + 1), (px + pw - 3, py + 1), 1)
            pygame.draw.rect(s, (36, 40, 50), (px + 2, py + 2, pw - 4, ph - 4), 1, border_radius=3)
            # Pequeños remaches/esquineros de piedra en las 4 esquinas de la parcela
            for ex_c, ey_c in [(px + 1, py + 1), (px + pw - 5, py + 1), (px + 1, py + ph - 5), (px + pw - 5, py + ph - 5)]:
                pygame.draw.rect(s, (120, 126, 146), (ex_c, ey_c, 4, 4))

        # Avenidas Principales y Senderos Simétricos de los 4 Claustros:
        self._paint_cobblestone_avenue(s, 28, 326, 744, 40, style="moonlit", seed=101)
        self._paint_cobblestone_avenue(s, 84, 212, 632, 24, style="moonlit", seed=102)
        self._paint_cobblestone_avenue(s, 84, 462, 632, 24, style="moonlit", seed=103)
        self._paint_cobblestone_avenue(s, 372, 148, 56, 402, style="moonlit", seed=104)

        # Pilares monumentales de hierro y piedra del portal sur (x=362 y x=428) + REJA CERRADA CON CANDADO (encima del adoquín y sobre el HUD)
        for px_g in (362, 428):
            pygame.draw.rect(s, (54, 56, 68), (px_g, 542, 10, 44), border_radius=2)
            pygame.draw.line(s, (112, 118, 138), (px_g + 1, 543), (px_g + 1, 584), 1)
            pygame.draw.rect(s, (26, 26, 36), (px_g, 542, 10, 44), 1, border_radius=2)
            pygame.draw.circle(s, (255, 215, 105), (px_g + 5, 539), 4)
            pygame.draw.circle(s, (255, 248, 210), (px_g + 5, 539), 2)

        # Fondo oscuro tras la reja cerrada + barrotes forjados con puntas de lanza
        pygame.draw.rect(s, (12, 14, 22), (372, 550, 56, 34))
        pygame.draw.line(s, (28, 30, 40), (372, 552), (428, 552), 3)
        pygame.draw.line(s, (88, 94, 112), (372, 551), (428, 551), 1)
        pygame.draw.line(s, (28, 30, 40), (372, 572), (428, 572), 3)
        for bx_g in (376, 383, 390, 397, 403, 410, 417, 424):
            pygame.draw.line(s, (24, 26, 34), (bx_g, 546), (bx_g, 584), 3)
            pygame.draw.line(s, (84, 90, 108), (bx_g - 1, 547), (bx_g - 1, 583), 1)
            pygame.draw.polygon(s, (116, 122, 144), [(bx_g - 2, 547), (bx_g, 541), (bx_g + 2, 547)])
        # Cadenas y gran candado de latón cerrando la reja desde afuera
        pygame.draw.line(s, (132, 138, 156), (390, 559), (410, 565), 2)
        pygame.draw.line(s, (132, 138, 156), (390, 565), (410, 559), 2)
        pygame.draw.arc(s, (186, 192, 210), (396, 552, 8, 9), 0, math.pi, 2)
        pygame.draw.rect(s, (195, 152, 52), (395, 558, 10, 11), border_radius=2)
        pygame.draw.rect(s, (250, 222, 120), (396, 559, 4, 3))
        pygame.draw.rect(s, (62, 42, 16), (395, 558, 10, 11), 1, border_radius=2)
        pygame.draw.rect(s, (24, 18, 12), (399, 562, 2, 4))

        # Plaza Octogonal Central con Mosaico de Rosa de los Vientos y Ribete Dorado
        pygame.draw.circle(s, (12, 15, 20), (400, 348), 47)
        pygame.draw.circle(s, (50, 54, 66), (400, 346), 45)
        pygame.draw.circle(s, (132, 140, 162), (400, 346), 45, 2)
        pygame.draw.circle(s, (66, 70, 86), (400, 346), 34)
        pygame.draw.circle(s, (205, 185, 115), (400, 346), 34, 1)
        for ang_i in range(8):
            a = ang_i * (math.pi / 4.0)
            pygame.draw.line(s, (96, 102, 122), (400, 346), (400 + int(math.cos(a) * 43), 346 + int(math.sin(a) * 43)), 1)
            pygame.draw.line(s, (200, 182, 112), (400, 346), (400 + int(math.cos(a) * 30), 346 + int(math.sin(a) * 30)), 1)
        pygame.draw.circle(s, (44, 48, 60), (400, 346), 16)
        pygame.draw.circle(s, (225, 205, 128), (400, 346), 16, 1)

        # Parcelas simétricas de piedra para cada cripta, tumba y monumento:
        draw_monument_plot(64, 98, 72, 60)
        draw_monument_plot(162, 152, 56, 58)
        draw_monument_plot(250, 152, 54, 58)
        draw_monument_plot(494, 148, 66, 62)
        draw_monument_plot(584, 152, 52, 58)
        draw_monument_plot(664, 98, 72, 60)
        draw_monument_plot(102, 396, 50, 64)
        draw_monument_plot(214, 396, 56, 64)
        draw_monument_plot(516, 398, 54, 62)
        draw_monument_plot(624, 398, 66, 62)

        # Pequeñas lápidas y cruces antiguas decorativas en las zonas verdes abiertas (sin obstruir rutas)
        for mgx, mgy, mtilt in [
            (46, 174, 0), (146, 114, 2), (234, 112, 0), (566, 112, -2),
            (168, 412, 0), (288, 414, 2), (484, 414, -2), (594, 412, 0),
            (132, 514, 0), (242, 518, -2), (538, 516, 2), (648, 514, 0),
        ]:
            self._paint_decorative_minor_grave(s, mgx, mgy, tilt=mtilt)

        # Charcos de lluvia nocturna con reflejo estrellado y lunar en los adoquines
        puddles = [
            (386, 444, 28, 11),
            (388, 268, 24, 10),
            (218, 340, 28, 11),
            (552, 340, 28, 11),
        ]
        for px, py, pw, ph in puddles:
            pygame.draw.ellipse(s, (20, 34, 54), (px, py, pw, ph))
            pygame.draw.ellipse(s, (38, 62, 94), (px + 2, py + 1, pw - 4, ph - 2))
            pygame.draw.ellipse(s, (66, 98, 138), (px + 2, py + 1, pw - 4, ph - 2), 1)
            pygame.draw.line(s, (195, 224, 255), (px + 5, py + 3), (px + pw - 7, py + 3), 1)
            s.set_at((px + pw // 2 + 2, py + ph - 3), (235, 245, 255))

        # Ramilletes de flores nocturnas (lirios celestes, flores doradas y rosas pálidas lunares)
        for fx, fy in [(148, 204), (240, 204), (356, 520), (444, 520), (356, 260), (444, 260)]:
            self._paint_flower_patch(s, fx, fy, color=(245, 210, 68), core=(255, 248, 175), count=3)
        for fx, fy in [(312, 204), (484, 204), (572, 204), (646, 204), (168, 452), (602, 452)]:
            self._paint_flower_patch(s, fx, fy, color=(92, 178, 255), core=(228, 246, 255), count=4)
        for fx, fy in [(94, 384), (704, 384), (288, 526), (512, 526)]:
            self._paint_flower_patch(s, fx, fy, color=(198, 145, 255), core=(245, 232, 255), count=3)

        # Hongos bioluminiscentes con halo suave en las 4 esquinas del jardín
        for hx, hy in [(46, 286), (748, 286), (48, 542), (744, 542)]:
            mglow = pygame.Surface((24, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(mglow, (95, 235, 215, 42), (0, 2, 24, 16))
            s.blit(mglow, (hx - 8, hy - 6))
            pygame.draw.rect(s, (185, 215, 205), (hx - 1, hy + 1, 2, 4))
            pygame.draw.circle(s, (75, 245, 215), (hx, hy), 3)
            pygame.draw.rect(s, (195, 180, 225), (hx + 4, hy + 4, 2, 3))
            pygame.draw.circle(s, (190, 115, 255), (hx + 5, hy + 3), 3)

        # 5. GRAN MAUSOLEO CATEDRAL GÓTICO (Panteón de la Runa Delta - x: 324..476, y: 40..152)
        # Escalinata monumental de mármol desgastado con balaustradas laterales
        pygame.draw.rect(s, (12, 14, 18), (320, 142, 160, 14), border_radius=3)
        pygame.draw.rect(s, (62, 66, 78), (324, 138, 152, 14), border_radius=2)
        pygame.draw.line(s, (108, 114, 132), (326, 139), (474, 139), 1)
        pygame.draw.rect(s, (74, 78, 92), (332, 130, 136, 10), border_radius=2)
        pygame.draw.line(s, (120, 126, 144), (334, 131), (466, 131), 1)
        pygame.draw.rect(s, (88, 92, 108), (340, 122, 120, 9), border_radius=2)
        pygame.draw.line(s, (138, 144, 164), (342, 123), (458, 123), 1)
        # Alfombra carmesí desgastada subiendo hacia el portal
        pygame.draw.rect(s, (112, 22, 46), (386, 122, 28, 30))
        pygame.draw.line(s, (205, 168, 86), (386, 122), (386, 151), 1)
        pygame.draw.line(s, (205, 168, 86), (413, 122), (413, 151), 1)

        # Cuerpo principal de sillería tallada
        pygame.draw.rect(s, (68, 70, 84), (334, 66, 132, 58))
        for my_b in range(70, 122, 10):
            pygame.draw.line(s, (52, 54, 66), (336, my_b), (464, my_b), 1)
        pygame.draw.rect(s, (34, 34, 46), (334, 66, 132, 58), 2)

        # Columnas corintias estriadas con capiteles dorados
        for col_x in [340, 358, 434, 452]:
            pygame.draw.rect(s, (88, 92, 108), (col_x, 72, 9, 50), border_radius=1)
            pygame.draw.line(s, (132, 138, 158), (col_x + 2, 74), (col_x + 2, 120), 1)
            pygame.draw.line(s, (56, 58, 70), (col_x + 6, 74), (col_x + 6, 120), 1)
            pygame.draw.rect(s, (148, 144, 124), (col_x - 2, 70, 13, 4), border_radius=1)
            pygame.draw.rect(s, (124, 128, 144), (col_x - 2, 119, 13, 4), border_radius=1)

        # Vitrales estrechos laterales iluminados en carmesí-violeta
        for vx_m in (372, 428):
            pygame.draw.rect(s, (22, 12, 32), (vx_m - 4, 82, 8, 24), border_top_left_radius=4, border_top_right_radius=4)
            pygame.draw.rect(s, (175, 45, 105), (vx_m - 2, 85, 4, 18), border_top_left_radius=2, border_top_right_radius=2)
            pygame.draw.rect(s, (210, 175, 95), (vx_m - 4, 82, 8, 24), 1, border_top_left_radius=4, border_top_right_radius=4)

        # Gran Portal Gótico ojival hacia el Abismo con halo miasmático carmesí/violeta
        portal_glow = pygame.Surface((60, 56), pygame.SRCALPHA)
        pygame.draw.ellipse(portal_glow, (185, 38, 92, 55), (4, 6, 52, 46))
        s.blit(portal_glow, (370, 74))
        pygame.draw.rect(s, (42, 38, 52), (380, 76, 40, 48), border_top_left_radius=18, border_top_right_radius=18)
        pygame.draw.rect(s, (185, 155, 86), (380, 76, 40, 48), 1, border_top_left_radius=18, border_top_right_radius=18)
        pygame.draw.rect(s, (14, 6, 22), (384, 80, 32, 44), border_top_left_radius=14, border_top_right_radius=14)
        pygame.draw.rect(s, (165, 32, 88), (392, 83, 16, 40), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.rect(s, (255, 140, 185), (397, 86, 6, 36), border_top_left_radius=3, border_top_right_radius=3)
        # Hojas de reja de hierro entreabiertas
        for gx_o in (385, 409):
            pygame.draw.rect(s, (34, 30, 42), (gx_o, 84, 6, 39), 1)
            pygame.draw.line(s, (66, 62, 78), (gx_o + 3, 84), (gx_o + 3, 122), 1)
        pygame.draw.line(s, (245, 78, 125), (385, 123), (415, 123), 2)

        # Frontón triangular moldurado con pináculos, gárgolas y gran rosetón Runa Delta
        pygame.draw.polygon(s, (78, 80, 96), [(400, 42), (324, 68), (476, 68)])
        pygame.draw.polygon(s, (38, 40, 52), [(400, 42), (324, 68), (476, 68)], 2)
        pygame.draw.lines(s, (198, 172, 98), False, [(328, 67), (400, 44), (472, 67)], 2)
        # Pináculos y cruz en la cumbre del Mausoleo
        for px_pin in (328, 472):
            pygame.draw.polygon(s, (92, 96, 114), [(px_pin - 4, 68), (px_pin, 52), (px_pin + 4, 68)])
            pygame.draw.circle(s, (235, 198, 92), (px_pin, 51), 2)
        pygame.draw.line(s, (240, 208, 102), (400, 28), (400, 43), 2)
        pygame.draw.line(s, (240, 208, 102), (394, 34), (406, 34), 2)

        # Rosetón vitral luminoso con la RUNA DELTA
        rose_g = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(rose_g, (215, 110, 245, 65), (15, 15), 14)
        s.blit(rose_g, (385, 43))
        pygame.draw.circle(s, (28, 18, 44), (400, 58), 9)
        pygame.draw.circle(s, (225, 192, 95), (400, 58), 9, 1)
        pygame.draw.circle(s, (255, 225, 95), (400, 55), 3)
        pygame.draw.polygon(s, (185, 115, 255), [(400, 58), (395, 64), (405, 64)])

        # Portal de entrada a la parte más profunda del cementerio (Abismo del Cementerio)
        self.depths_gate_rect = pygame.Rect(378, 134, 44, 24)

        # Pebeteros animados con llamas carmesí-violeta flanqueando la escalinata del Mausoleo
        self.world_objects.append(GothicBrazier(314, 126, flame_color=(225, 55, 115), core_color=(255, 225, 145)))
        self.world_objects.append(GothicBrazier(466, 126, flame_color=(225, 55, 115), core_color=(255, 225, 145)))

        # Cartel junto a la escalinata del Mausoleo avisando del Abismo y el Jefe
        self.world_objects.append(SignObject(
            x=336, y=156,
            message="* CARTEL DEL PANTEÓN: 'Gran Mausoleo Ancestral. Custodiado por Morvath, el Sepulturero Eterno.'"
        ))

        # Faroles góticos victorianos alineados a lo largo de la Avenida Central y el Cruce
        self.world_objects.append(GothicLampPost(352, 272, flame_color=(255, 205, 95), facing="RIGHT"))
        self.world_objects.append(GothicLampPost(432, 272, flame_color=(255, 205, 95), facing="LEFT"))
        self.world_objects.append(GothicLampPost(352, 378, flame_color=(255, 205, 95), facing="RIGHT"))
        self.world_objects.append(GothicLampPost(432, 378, flame_color=(255, 205, 95), facing="LEFT"))
        self.world_objects.append(GothicLampPost(352, 502, flame_color=(255, 205, 95), facing="RIGHT"))
        self.world_objects.append(GothicLampPost(432, 502, flame_color=(255, 205, 95), facing="LEFT"))

        # 1. Sauces llorones góticos antiguos organizados simétricamente en los 4 cuadrantes
        self.world_objects.append(TwistedTreeProp(36, 232, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(268, 232, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(468, 232, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(702, 232, has_lantern=True))
        self.world_objects.append(TwistedTreeProp(36, 486, has_lantern=False))
        self.world_objects.append(TwistedTreeProp(702, 486, has_lantern=False))

        # Velas votivas animadas junto a las tumbas principales
        for cx_c, cy_c in [(218, 448), (104, 448), (164, 198), (254, 198), (586, 198), (520, 448)]:
            self.world_objects.append(CemeteryCandleProp(cx_c, cy_c))

        # 2. Fuegos fatuos / Ánimas danzantes alineadas simétricamente en los cruces
        self.world_objects.append(WillOWisp(346, 200, color=(140, 255, 210)))
        self.world_objects.append(WillOWisp(454, 200, color=(140, 255, 210)))
        self.world_objects.append(WillOWisp(346, 346, color=(130, 235, 255)))
        self.world_objects.append(WillOWisp(454, 346, color=(130, 235, 255)))
        self.world_objects.append(WillOWisp(346, 474, color=(195, 160, 255)))
        self.world_objects.append(WillOWisp(454, 474, color=(195, 160, 255)))

        # 3. Estatua del Ángel del Silencio (Esculpida en mármol lunar con alas en capas y velas)
        def draw_angel_statue(surf, cx, cy, w, h):
            # Sombra base
            pygame.draw.ellipse(surf, (10, 14, 18), (cx + 2, cy + 46, w - 4, 8))
            # Pedestal escalonado con placa grabada
            pygame.draw.rect(surf, (66, 70, 82), (cx + 3, cy + 34, w - 6, 18), border_radius=2)
            pygame.draw.rect(surf, (96, 102, 118), (cx + 2, cy + 32, w - 4, 4), border_radius=1)
            pygame.draw.line(surf, (140, 148, 170), (cx + 3, cy + 32), (cx + w - 4, cy + 32), 1)
            pygame.draw.rect(surf, (38, 40, 50), (cx + 3, cy + 34, w - 6, 18), 1, border_radius=2)
            pygame.draw.rect(surf, (50, 54, 66), (cx + 9, cy + 38, w - 18, 8))
            pygame.draw.line(surf, (130, 136, 156), (cx + 11, cy + 41), (cx + w - 12, cy + 41), 1)
            # Alas plumadas con sombra y luz lunar
            pygame.draw.polygon(surf, (84, 88, 104), [(cx + w//2 - 2, cy + 14), (cx, cy + 4), (cx + 4, cy + 28)])
            pygame.draw.polygon(surf, (134, 142, 164), [(cx + w//2 - 2, cy + 14), (cx + 2, cy + 6), (cx + 7, cy + 20)])
            pygame.draw.polygon(surf, (84, 88, 104), [(cx + w//2 + 2, cy + 14), (cx + w, cy + 4), (cx + w - 4, cy + 28)])
            pygame.draw.polygon(surf, (134, 142, 164), [(cx + w//2 + 2, cy + 14), (cx + w - 2, cy + 6), (cx + w - 7, cy + 20)])
            # Túnica esculpida con pliegues y rostro sereno
            pygame.draw.polygon(surf, (108, 114, 130), [(cx + w//2, cy + 11), (cx + 8, cy + 33), (cx + w - 8, cy + 33)])
            pygame.draw.line(surf, (148, 156, 178), (cx + w//2 - 2, cy + 14), (cx + 12, cy + 32), 1)
            pygame.draw.line(surf, (74, 78, 92), (cx + w//2 + 2, cy + 15), (cx + w - 12, cy + 32), 1)
            pygame.draw.circle(surf, (124, 130, 148), (cx + w//2, cy + 9), 6)
            pygame.draw.circle(surf, (160, 168, 190), (cx + w//2 - 2, cy + 7), 2)
            # Halo dorado tenue sobre el ángel
            pygame.draw.ellipse(surf, (230, 200, 110), (cx + w//2 - 6, cy, 12, 4), 1)
            # Velas a sus pies
            for vx_a in (cx + 6, cx + w - 9):
                pygame.draw.rect(surf, (242, 236, 218), (vx_a, cy + 28, 3, 5))
                pygame.draw.circle(surf, (255, 215, 85), (vx_a + 1, cy + 26), 2)
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

        # 4. Cruz Celta de Piedra Antigua (tallada con relieve, musgo y hiedra)
        def draw_celtic_cross(surf, cx, cy, w, h):
            pygame.draw.ellipse(surf, (10, 14, 18), (cx + 2, cy + 44, w - 4, 8))
            pygame.draw.rect(surf, (68, 72, 84), (cx + 3, cy + 36, w - 6, 14), border_radius=2)
            pygame.draw.line(surf, (118, 124, 142), (cx + 4, cy + 37), (cx + w - 5, cy + 37), 1)
            pygame.draw.rect(surf, (36, 38, 48), (cx + 3, cy + 36, w - 6, 14), 1, border_radius=2)
            # Halo celta tallado
            pygame.draw.circle(surf, (44, 48, 58), (cx + w//2, cy + 17), 11, 3)
            pygame.draw.circle(surf, (124, 130, 148), (cx + w//2, cy + 17), 10, 2)
            # Brazos de la cruz con volumen
            pygame.draw.rect(surf, (96, 102, 118), (cx + w//2 - 4, cy + 3, 8, 35), border_radius=1)
            pygame.draw.line(surf, (140, 148, 168), (cx + w//2 - 3, cy + 4), (cx + w//2 - 3, cy + 36), 1)
            pygame.draw.rect(surf, (96, 102, 118), (cx + 5, cy + 13, 24, 7), border_radius=1)
            pygame.draw.line(surf, (140, 148, 168), (cx + 6, cy + 14), (cx + 28, cy + 14), 1)
            pygame.draw.rect(surf, (38, 40, 50), (cx + w//2 - 4, cy + 3, 8, 35), 1, border_radius=1)
            pygame.draw.circle(surf, (205, 185, 110), (cx + w//2, cy + 16), 2)
            # Enredadera de musgo abrazando la base
            for mx_c, my_c in [(cx + 12, cy + 33), (cx + 16, cy + 28), (cx + 20, cy + 35)]:
                pygame.draw.circle(surf, (52, 98, 62), (mx_c, my_c), 3)
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
            pygame.draw.rect(surf, (62, 66, 78), (cx, cy + 9, w, h - 9), border_radius=3)
            for by_c in range(cy + 14, cy + h - 4, 8):
                pygame.draw.line(surf, (44, 46, 56), (cx + 2, by_c), (cx + w - 2, by_c), 1)
            pygame.draw.rect(surf, (34, 36, 46), (cx, cy + 9, w, h - 9), 2, border_radius=3)
            # Pilastras laterales
            for px_c in (cx + 3, cx + w - 9):
                pygame.draw.rect(surf, (88, 92, 108), (px_c, cy + 11, 6, h - 13))
                pygame.draw.line(surf, (130, 136, 156), (px_c + 1, cy + 12), (px_c + 1, cy + h - 4), 1)
            # Frontón con cruz
            pygame.draw.polygon(surf, (84, 88, 104), [(cx + w//2, cy - 2), (cx - 3, cy + 10), (cx + w + 3, cy + 10)])
            pygame.draw.polygon(surf, (34, 36, 46), [(cx + w//2, cy - 2), (cx - 3, cy + 10), (cx + w + 3, cy + 10)], 1)
            pygame.draw.line(surf, (140, 146, 166), (cx + 1, cy + 9), (cx + w//2, cy), 1)
            # Arco de reja oscura con bruma azulada saliendo del interior
            pygame.draw.rect(surf, (12, 14, 22), (cx + 13, cy + 18, w - 26, h - 18), border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.ellipse(surf, (48, 86, 128), (cx + 18, cy + h - 14, w - 36, 10))
            for gx in range(cx + 17, cx + w - 15, 5):
                pygame.draw.line(surf, (78, 82, 98), (gx, cy + 19), (gx, cy + h - 1), 1)
            pygame.draw.line(surf, (78, 82, 98), (cx + 13, cy + 34), (cx + w - 14, cy + 34), 1)
            pygame.draw.rect(surf, (112, 118, 138), (cx + 13, cy + 18, w - 26, h - 18), 1, border_top_left_radius=12, border_top_right_radius=12)
        self.world_objects.append(InteriorProp(
            70, 102, 60, 52, 156, draw_old_crypt,
            [
                "* Entrada a la Antigua Cripta Familiar.",
                "* 'Aquí yacen los pioneros que fundaron el valle.'",
                "* El aire que sube desde los escalones de piedra es gélido como la escarcha."
            ]
        ))

        # 6. Lápida de Gerson Boom (arco gótico con martillo grabado y flores doradas)
        def draw_gerson_tomb(surf, cx, cy, w, h):
            pygame.draw.ellipse(surf, (10, 14, 18), (cx - 2, cy + h - 6, w + 4, 8))
            pygame.draw.rect(surf, (66, 70, 82), (cx - 2, cy + h - 8, w + 4, 8), border_radius=2)
            pygame.draw.rect(surf, (92, 96, 112), (cx + 2, cy + 2, w - 4, h - 8), border_top_left_radius=14, border_top_right_radius=14)
            pygame.draw.line(surf, (136, 144, 166), (cx + 5, cy + 6), (cx + 5, cy + h - 10), 2)
            pygame.draw.rect(surf, (44, 46, 56), (cx + 2, cy + 2, w - 4, h - 8), 2, border_top_left_radius=14, border_top_right_radius=14)
            # Martillo de la Justicia en relieve
            pygame.draw.rect(surf, (150, 114, 68), (cx + w//2 - 2, cy + 12, 4, 18))
            pygame.draw.rect(surf, (195, 165, 105), (cx + w//2 - 9, cy + 10, 18, 7), border_radius=1)
            pygame.draw.rect(surf, (95, 72, 42), (cx + w//2 - 9, cy + 10, 18, 7), 1, border_radius=1)
            # Ramo dorado y musgo
            pygame.draw.circle(surf, (50, 96, 58), (cx + 7, cy + h - 6), 4)
            pygame.draw.circle(surf, (248, 215, 65), (cx + w - 9, cy + h - 7), 3)
            pygame.draw.circle(surf, (255, 245, 155), (cx + w - 9, cy + h - 7), 1)
            pygame.draw.circle(surf, (245, 210, 60), (cx + w - 14, cy + h - 5), 2)
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

        # 7. Lápida de Crystal (mármol azulado con alas talladas y flores celestes luminosas)
        def draw_crystal_tomb(surf, cx, cy, w, h):
            pygame.draw.ellipse(surf, (10, 14, 18), (cx - 2, cy + h - 6, w + 4, 8))
            pygame.draw.rect(surf, (68, 76, 94), (cx - 2, cy + h - 8, w + 4, 8), border_radius=2)
            pygame.draw.rect(surf, (96, 106, 128), (cx + 2, cy + 2, w - 4, h - 8), border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.line(surf, (156, 174, 206), (cx + 5, cy + 6), (cx + 5, cy + h - 10), 2)
            pygame.draw.rect(surf, (48, 54, 70), (cx + 2, cy + 2, w - 4, h - 8), 2, border_top_left_radius=12, border_top_right_radius=12)
            # Cristal celeste tallado en el centro
            pygame.draw.polygon(surf, (145, 205, 255), [(cx + w//2, cy + 8), (cx + w//2 + 6, cy + 16), (cx + w//2, cy + 25), (cx + w//2 - 6, cy + 16)])
            pygame.draw.polygon(surf, (230, 246, 255), [(cx + w//2, cy + 10), (cx + w//2 + 3, cy + 16), (cx + w//2, cy + 21), (cx + w//2 - 3, cy + 16)])
            # Flores celestes frescas
            for fx, fy in [(cx + 8, cy + 36), (cx + 20, cy + 34), (cx + 32, cy + 36)]:
                pygame.draw.circle(surf, (80, 165, 255), (fx, fy), 4)
                pygame.draw.circle(surf, (225, 245, 255), (fx, fy), 2)
        self.world_objects.append(InteriorProp(
            256, 156, 42, 48, 206, draw_crystal_tomb,
            [
                "* Lápida de CRYSTAL.",
                "* Flores celestes frescas adornan su base. Alguien las puso hace pocas horas.",
                "* (El aroma floral disipa tu terror y refresca tu mente. +20 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 20

        # 8. Cripta de la Antigua Guardia Real (Sector Noreste)
        def draw_guard_crypt(surf, cx, cy, w, h):
            pygame.draw.rect(surf, (66, 70, 84), (cx, cy + 9, w, h - 9), border_radius=3)
            for by_c in range(cy + 14, cy + h - 4, 8):
                pygame.draw.line(surf, (46, 48, 60), (cx + 2, by_c), (cx + w - 2, by_c), 1)
            pygame.draw.rect(surf, (36, 38, 48), (cx, cy + 9, w, h - 9), 2, border_radius=3)
            pygame.draw.polygon(surf, (88, 92, 108), [(cx + w//2, cy - 2), (cx - 3, cy + 10), (cx + w + 3, cy + 10)])
            pygame.draw.polygon(surf, (36, 38, 48), [(cx + w//2, cy - 2), (cx - 3, cy + 10), (cx + w + 3, cy + 10)], 1)
            # Espadas cruzadas y escudo real dorado/plata
            pygame.draw.line(surf, (218, 224, 240), (cx + 14, cy + 14), (cx + w - 14, cy + 38), 2)
            pygame.draw.line(surf, (218, 224, 240), (cx + w - 14, cy + 14), (cx + 14, cy + 38), 2)
            sh_pts = [(cx + w//2, cy + 16), (cx + w//2 + 8, cy + 20), (cx + w//2 + 6, cy + 32), (cx + w//2, cy + 36), (cx + w//2 - 6, cy + 32), (cx + w//2 - 8, cy + 20)]
            pygame.draw.polygon(surf, (58, 72, 112), sh_pts)
            pygame.draw.polygon(surf, (225, 195, 95), sh_pts, 2)
            pygame.draw.circle(surf, (245, 220, 115), (cx + w//2, cy + 25), 2)
        self.world_objects.append(InteriorProp(
            670, 102, 60, 52, 156, draw_guard_crypt,
            [
                "* Cripta de la Antigua Guardia Real.",
                "* 'Su honor fue su escudo; su deber, su vida.'",
                "* Dos espadas de piedra descansan cruzadas sobre el frontón esculpido."
            ]
        ))

        # 9. Fuente de la Memoria (Cuenca octogonal de mármol con chorros cristalinos y reflejos)
        def draw_fountain(surf, cx, cy, w, h):
            oct_pts = [
                (cx + 10, cy + h), (cx + w - 10, cy + h),
                (cx + w, cy + h - 14), (cx + w, cy + 16),
                (cx + w - 10, cy), (cx + 10, cy),
                (cx, cy + 16), (cx, cy + h - 14)
            ]
            pygame.draw.polygon(surf, (78, 84, 98), oct_pts)
            pygame.draw.polygon(surf, (132, 140, 162), oct_pts[:6], 1)
            pygame.draw.polygon(surf, (38, 42, 54), oct_pts, 2)
            # Agua cristalina en capas con reflejo lunar
            pygame.draw.ellipse(surf, (22, 52, 92), (cx + 5, cy + 7, w - 10, h - 14))
            pygame.draw.ellipse(surf, (38, 86, 138), (cx + 8, cy + 10, w - 16, h - 20))
            pygame.draw.ellipse(surf, (96, 172, 228), (cx + 11, cy + 13, w - 22, h - 26), 1)
            # Columna central y cáliz con chorros brillantes
            pygame.draw.rect(surf, (98, 104, 122), (cx + w//2 - 4, cy + 13, 8, 16), border_radius=1)
            pygame.draw.ellipse(surf, (124, 132, 152), (cx + w//2 - 8, cy + 11, 16, 6))
            pygame.draw.circle(surf, (165, 225, 255), (cx + w//2, cy + 10), 4)
            pygame.draw.circle(surf, (240, 252, 255), (cx + w//2, cy + 9), 2)
            # Arcos de agua cayendo a la fuente
            pygame.draw.arc(surf, (175, 232, 255), (cx + w//2 - 14, cy + 10, 14, 16), 0, math.pi * 0.8, 1)
            pygame.draw.arc(surf, (175, 232, 255), (cx + w//2, cy + 10, 14, 16), math.pi * 0.2, math.pi, 1)
            pygame.draw.circle(surf, (225, 248, 255), (cx + w//2 - 11, cy + 25), 2)
            pygame.draw.circle(surf, (225, 248, 255), (cx + w//2 + 11, cy + 25), 2)
        self.world_objects.append(InteriorProp(
            500, 154, 54, 50, 206, draw_fountain,
            [
                "* La Fuente de la Memoria.",
                "* El agua cristalina refleja el brillo de las estrellas y la luna llena.",
                "* Te enjuagas la cara con el agua helada. Te sientes renovado. (+15 de cordura)"
            ]
        ))
        self.world_objects[-1]._sanity_boost = 15

        # 10. Lápida de Mutt (con borde tallado, hueso en relieve y pelota brillante)
        def draw_mutt_tomb(surf, cx, cy, w, h):
            pygame.draw.ellipse(surf, (10, 14, 18), (cx - 2, cy + h - 6, w + 4, 8))
            pygame.draw.rect(surf, (68, 68, 80), (cx - 2, cy + h - 8, w + 4, 8), border_radius=2)
            pygame.draw.rect(surf, (94, 94, 108), (cx + 2, cy + 2, w - 4, h - 8), border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.line(surf, (138, 138, 156), (cx + 5, cy + 6), (cx + 5, cy + h - 10), 2)
            pygame.draw.rect(surf, (46, 46, 56), (cx + 2, cy + 2, w - 4, h - 8), 2, border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.rect(surf, (236, 230, 214), (cx + w//2 - 8, cy + 14, 16, 5))
            pygame.draw.circle(surf, (236, 230, 214), (cx + w//2 - 8, cy + 16), 4)
            pygame.draw.circle(surf, (236, 230, 214), (cx + w//2 + 8, cy + 16), 4)
            pygame.draw.circle(surf, (228, 52, 58), (cx + 9, cy + h - 6), 4)
            pygame.draw.circle(surf, (255, 160, 165), (cx + 8, cy + h - 7), 1)
        self.world_objects.append(InteriorProp(
            590, 156, 40, 48, 206, draw_mutt_tomb,
            [
                "* Lápida de MUTT.",
                "* 'El perro más fiel. Siempre un buen chico.'",
                "* Hay un hueso tallado en la piedra y una pequeña pelota roja descansando a sus pies."
            ]
        ))

        # 11. Lápida del Poeta Olvidado (con libro abierto y pluma dorada grabada)
        def draw_poet_tomb(surf, cx, cy, w, h):
            pygame.draw.ellipse(surf, (10, 14, 18), (cx - 2, cy + h - 6, w + 4, 8))
            pygame.draw.rect(surf, (62, 66, 78), (cx - 2, cy + h - 8, w + 4, 8), border_radius=2)
            pygame.draw.rect(surf, (88, 92, 108), (cx + 2, cy + 2, w - 4, h - 8), border_top_left_radius=10, border_top_right_radius=10)
            pygame.draw.line(surf, (132, 138, 158), (cx + 5, cy + 6), (cx + 5, cy + h - 10), 2)
            pygame.draw.rect(surf, (44, 46, 56), (cx + 2, cy + 2, w - 4, h - 8), 2, border_top_left_radius=10, border_top_right_radius=10)
            pygame.draw.rect(surf, (226, 220, 202), (cx + w//2 - 8, cy + 11, 7, 11))
            pygame.draw.rect(surf, (226, 220, 202), (cx + w//2 + 1, cy + 11, 7, 11))
            pygame.draw.line(surf, (140, 128, 108), (cx + w//2, cy + 11), (cx + w//2, cy + 22), 1)
            pygame.draw.line(surf, (225, 195, 110), (cx + w - 10, cy + 9), (cx + w - 4, cy + 24), 2)
        self.world_objects.append(InteriorProp(
            524, 406, 38, 46, 456, draw_poet_tomb,
            [
                "* Lápida con un libro abierto grabado en la piedra.",
                "* 'No llores ante mi lápida, viajero. No estoy allí... yo nunca duermo.'",
                "* Un suave suspiro parece acariciar las hojas marchitas a tu alrededor."
            ]
        ))

        # 12. Tumba Abierta (Sector Sureste - con profundidad, tierra removida, lápida tallada y pala)
        def draw_open_grave(surf, cx, cy, w, h):
            # Fosa profunda con gradiente de sombra y tablones
            pygame.draw.rect(surf, (10, 7, 8), (cx + 4, cy + 20, w - 8, h - 20), border_radius=3)
            pygame.draw.rect(surf, (38, 28, 22), (cx + 4, cy + 20, w - 8, h - 20), 2, border_radius=3)
            pygame.draw.line(surf, (78, 54, 38), (cx + 6, cy + 24), (cx + w - 6, cy + 24), 2)
            pygame.draw.line(surf, (62, 42, 28), (cx + 6, cy + 35), (cx + w - 6, cy + 35), 2)
            # Montículo de tierra fresca
            pygame.draw.polygon(surf, (56, 42, 32), [(cx - 2, cy + 24), (cx + w//2, cy + 13), (cx + w + 2, cy + 24)])
            pygame.draw.polygon(surf, (76, 58, 44), [(cx + 4, cy + 22), (cx + w//2, cy + 15), (cx + w - 4, cy + 22)])
            # Lápida sin terminar detrás
            pygame.draw.rect(surf, (88, 92, 108), (cx + w//2 - 12, cy, 24, 28), border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(surf, (132, 138, 158), (cx + w//2 - 10, cy + 3), (cx + w//2 - 10, cy + 25), 1)
            pygame.draw.rect(surf, (44, 46, 56), (cx + w//2 - 12, cy, 24, 28), 1, border_top_left_radius=8, border_top_right_radius=8)
            # Pala clavada en la tierra y farolillo
            pygame.draw.line(surf, (124, 94, 62), (cx + w - 6, cy + 5), (cx + w + 2, cy + 32), 2)
            pygame.draw.rect(surf, (136, 142, 158), (cx + w - 9, cy + 1, 10, 6), border_radius=1)
            pygame.draw.circle(surf, (255, 205, 80), (cx + 2, cy + 24), 3)
            pygame.draw.circle(surf, (255, 248, 205), (cx + 2, cy + 24), 1)
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

        # 14. Paso abierto al Este (final de la Avenida Este, x=764..800, y=316..372) hacia el Atrio de la Iglesia
        self._paint_cobblestone_avenue(s, 748, 326, 52, 40, style="moonlit", seed=109)
        # Pilares monumentales del arco de paso hacia el Atrio de la Iglesia
        for py_p in (296, 368):
            pygame.draw.rect(s, (58, 60, 74), (766, py_p, 14, 24), border_radius=2)
            pygame.draw.line(s, (118, 124, 144), (768, py_p + 2), (768, py_p + 22), 1)
            pygame.draw.rect(s, (30, 32, 42), (766, py_p, 14, 24), 1, border_radius=2)
            pygame.draw.circle(s, (255, 225, 95), (773, py_p - 2), 4)
            pygame.draw.circle(s, (255, 250, 215), (773, py_p - 2), 2)

        self.church_section_gate_rect = pygame.Rect(768, 318, 32, 52)
        self.world_objects.append(SignObject(
            x=712, y=300,
            message="* ARCO DEL ESTE -> 'Atrio de la Iglesia del Cementerio (Continúa hacia la derecha para ir a la Iglesia).'"
        ))

        # 15. Reja Sur Cerrada con Candado (interactuable: explica que cerraron de noche) y Ramo caído de Paniel
        def draw_locked_gate_glint(surf, cx, cy, w, h):
            # Pequeño destello dorado sobre el candado para indicar que se puede inspeccionar
            pygame.draw.circle(surf, (255, 240, 145), (cx + 28, cy + 16), 2)
        self.world_objects.append(InteriorProp(
            372, 544, 56, 30, 582, draw_locked_gate_glint,
            [
                "* La reja principal del cementerio está cerrada con cadena y candado por fuera.",
                "* El guardia echó el cerrojo a medianoche sin verte dormido adentro.",
                "* Paniel: 'No se abre... Tendré que buscar otra salida por la Iglesia (Este) o el Mausoleo (Norte).'"
            ],
            is_solid=False
        ))

        def draw_dropped_bouquet(surf, cx, cy, w, h):
            # Ramo de flores celestes que Paniel soltó al quedarse dormido
            pygame.draw.ellipse(surf, (12, 16, 24), (cx, cy + 7, 16, 6))
            pygame.draw.line(surf, (58, 126, 72), (cx + 2, cy + 10), (cx + 12, cy + 6), 2)
            pygame.draw.line(surf, (46, 104, 62), (cx + 3, cy + 11), (cx + 14, cy + 9), 2)
            pygame.draw.rect(surf, (215, 192, 130), (cx + 5, cy + 8, 4, 3))
            for fx, fy in [(cx + 11, cy + 4), (cx + 15, cy + 7), (cx + 12, cy + 10)]:
                pygame.draw.circle(surf, (88, 182, 255), (fx, fy), 3)
                pygame.draw.circle(surf, (228, 248, 255), (fx, fy), 1)
        self.world_objects.append(InteriorProp(
            408, 514, 18, 14, 518, draw_dropped_bouquet,
            [
                "* El ramo de flores celestes que trajiste al atardecer.",
                "* Paniel: 'Solo vine a dejarlas... pero llevaba días sin dormir y esta niebla dulce me venció.'",
                "* (Sus pétalos celestes brillan suavemente bajo el farol.)"
            ],
            is_solid=False
        ))

        # ==========================================================
        # COLISIONES SÓLIDAS
        # ==========================================================
        self.solid_rects.append(pygame.Rect(0, 76, 800, 24))         # Muro superior
        self.solid_rects.append(pygame.Rect(0, 76, 24, 524))         # Muro izquierdo
        # Muro derecho con abertura en y=318..370 para pasar a la Sección de la Iglesia
        self.solid_rects.append(pygame.Rect(776, 76, 24, 242))
        self.solid_rects.append(pygame.Rect(776, 370, 24, 230))
        # Muro inferior completo + reja sur cerrada con candado
        self.solid_rects.append(pygame.Rect(0, 576, 800, 24))
        self.solid_rects.append(pygame.Rect(362, 550, 76, 34))
        # Laterales del Mausoleo dejando libre el vano central (x=378..422) para entrar al Abismo
        self.solid_rects.append(pygame.Rect(328, 64, 50, 86))
        self.solid_rects.append(pygame.Rect(422, 64, 50, 86))
        self.solid_rects.append(pygame.Rect(378, 64, 44, 70))

    # ==========================================================
    # 3. PARTE MÁS PROFUNDA DEL CEMENTERIO: ABISMO DEL CEMENTERIO (ZONA DEL JEFE)
    # ==========================================================
    def _build_cemetery_depths(self):
        s = self.surface
        # 1. SUELO ABISMAL DE OBSIDIANA Y BASALTO FRACTURADO CON BRILLO MIASMÁTICO
        self._paint_textured_cemetery_ground(s, 800, 600, top_y=102, theme="abyss", seed=77)

        # 2. CIELO DEL ABISMO CON ECLIPSE CARMESÍ, NUBES OSCURAS Y COLUMNA DE MIASMA
        self._paint_gothic_sky(s, 800, sky_h=82, moon_pos=(182, 38), theme="abyss", seed=77)

        # Columna de la Fuente Oscura / Miasma de la Bruja surgiendo tras el Altar Norte
        for layer_w, col in [(74, (32, 10, 52)), (48, (72, 18, 86)), (26, (152, 34, 108)), (10, (245, 95, 155))]:
            pygame.draw.rect(s, col, (400 - layer_w // 2, 0, layer_w, 82))

        # 3. MUROS PERIMETRALES DE OBSIDIANA CON REJAS CARMESÍ Y ENREDADERAS OSCURAS
        self._paint_ornate_gothic_walls(s, 800, 600, top_y=80, open_south=True, open_east=False, open_west=False, theme="abyss", seed=77)

        # Pilares del portal sur
        for px_g in (362, 428):
            pygame.draw.rect(s, (120, 36, 68), (px_g, 566, 10, 34), border_radius=2)
            pygame.draw.rect(s, (24, 12, 30), (px_g, 566, 10, 34), 1, border_radius=2)
            pygame.draw.circle(s, (235, 75, 130), (px_g + 5, 563), 3)

        # 4. GRAN PLAZA CIRCULAR DEL OSARIO Y SELLO DEL CULTO DE LA BRUJA
        pygame.draw.circle(s, (10, 6, 18), (400, 242), 158)
        pygame.draw.circle(s, (26, 18, 40), (400, 240), 154)
        pygame.draw.circle(s, (165, 42, 92), (400, 240), 154, 3)
        pygame.draw.circle(s, (34, 24, 52), (400, 240), 126)
        pygame.draw.circle(s, (125, 45, 145), (400, 240), 126, 2)

        # Anillo rúnico ritual de la Bruja grabado en el suelo de la arena
        for ri in range(12):
            ang = ri * (math.pi / 6.0)
            rx1 = 400 + int(math.cos(ang) * 126)
            ry1 = 240 + int(math.sin(ang) * 126)
            rx2 = 400 + int(math.cos(ang) * 150)
            ry2 = 240 + int(math.sin(ang) * 150)
            pygame.draw.line(s, (145, 40, 92), (rx1, ry1), (rx2, ry2), 2)
            pygame.draw.circle(s, (215, 75, 155), (400 + int(math.cos(ang + 0.26) * 138), 240 + int(math.sin(ang + 0.26) * 138)), 2)

        # Emblema Delta Rune & Estrella del Eclipse en el centro de la arena
        pygame.draw.circle(s, (195, 48, 102), (400, 240), 50, 2)
        pygame.draw.circle(s, (135, 52, 165), (400, 240), 38, 1)
        for dx, dy in [(-24, 18), (24, 18), (0, -22)]:
            tri = [(400 + dx, 240 + dy - 10), (400 + dx - 10, 240 + dy + 8), (400 + dx + 10, 240 + dy + 8)]
            pygame.draw.polygon(s, (185, 50, 96), tri, 2)

        # Calzada procesional con bordillos de obsidiana, Vestíbulo Sur y alfombra carmesí-púrpura
        pygame.draw.rect(s, (26, 18, 40), (288, 434, 224, 62), border_radius=6)
        pygame.draw.rect(s, (165, 42, 92), (288, 434, 224, 62), 2, border_radius=6)
        for ped_cx in (328, 472):
            pygame.draw.circle(s, (18, 12, 28), (ped_cx, 465), 21)
            pygame.draw.circle(s, (215, 62, 118), (ped_cx, 465), 21, 2)

        self._paint_cobblestone_avenue(s, 368, 376, 64, 200, style="abyss", seed=79)
        for gy in range(378, 574, 14):
            pygame.draw.rect(s, (128, 26, 62), (392, gy, 16, 12))
            pygame.draw.line(s, (210, 168, 86), (392, gy), (392, gy + 12), 1)
            pygame.draw.line(s, (210, 168, 86), (408, gy), (408, gy + 12), 1)

        # Grietas orgánicas quebradas de miasma violeta-carmesí en el suelo
        jagged_cracks = [
            [(104, 174), (126, 186), (140, 182), (162, 198), (180, 212)],
            [(696, 174), (674, 186), (660, 182), (638, 198), (620, 212)],
            [(126, 414), (154, 424), (168, 438), (194, 444), (214, 456)],
            [(674, 414), (646, 424), (632, 438), (606, 444), (586, 456)],
            [(132, 304), (154, 316), (170, 312), (196, 330)],
            [(668, 304), (646, 316), (630, 312), (604, 330)],
        ]
        for pts_c in jagged_cracks:
            pygame.draw.lines(s, (0, 0, 0), False, pts_c, 6)
            pygame.draw.lines(s, (118, 26, 148), False, pts_c, 4)
            pygame.draw.lines(s, (225, 58, 128), False, pts_c, 2)
            pygame.draw.lines(s, (255, 200, 235), False, pts_c[:3], 1)

        # 5. PORTAL DE CRISTAL QUEBRADO EN EL ALTAR NORTE
        pygame.draw.rect(s, (46, 34, 66), (342, 118, 116, 18), border_radius=2)
        pygame.draw.rect(s, (66, 48, 90), (352, 108, 96, 12), border_radius=2)
        portal_arch = [(366, 118), (360, 60), (384, 72), (400, 44), (416, 72), (440, 60), (434, 118)]
        pygame.draw.polygon(s, (18, 8, 30), portal_arch)
        pygame.draw.polygon(s, (235, 45, 105), portal_arch, 2)
        pygame.draw.polygon(s, (0, 0, 0), portal_arch, 1)
        pygame.draw.rect(s, (8, 2, 18), (378, 74, 44, 44), border_radius=6)
        # Vórtice dimensional cristalino en capas
        for vr, vc in [(20, (82, 18, 118)), (15, (185, 36, 112)), (10, (245, 78, 155)), (5, (255, 225, 245))]:
            pts_v = [(400, 96 - vr), (400 + int(vr * 0.85), 96), (400, 96 + vr), (400 - int(vr * 0.85), 96)]
            pygame.draw.polygon(s, vc, pts_v)
        pygame.draw.rect(s, (235, 42, 105), (378, 74, 44, 44), 2, border_radius=6)

        self.sanctuary_gate_rect = pygame.Rect(376, 82, 48, 44)

        # ==========================================================
        # OBJETOS INTERACTIVOS Y AMBIENTALES DEL ABISMO
        # ==========================================================
        self.world_objects.append(SavePointObject(x=326, y=448))
        self.world_objects.append(ChestObject(x=452, y=448))
        self.world_objects.append(SignObject(
            x=342, y=388,
            message="* INSCRIPCIÓN CARMESÍ: 'Al norte del altar se abre la Grieta de Cristal hacia el Santuario del Rey Vaelkor.'"
        ))

        # Pebeteros de Fuego Miasmático flanqueando el Altar Norte y la entrada procesional
        for bx_b, by_b in [(336, 118), (444, 118), (344, 534), (436, 534)]:
            self.world_objects.append(GothicBrazier(bx_b, by_b, flame_color=(195, 45, 225), core_color=(255, 185, 245)))

        # Pilares abismales rodeando el anillo del Jefe
        for px, py in [(225, 160), (555, 160), (215, 290), (565, 290), (310, 495), (470, 495)]:
            self.world_objects.append(RuinPillar(px, py, style="abyss", has_candle=True))

        # Sauces abismales retorcidos con faroles carmesí en las esquinas
        for tx, ty in [(58, 146), (678, 146), (58, 438), (678, 438)]:
            self.world_objects.append(TwistedTreeProp(tx, ty, has_lantern=True, foliage_tint="abyss"))

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
        self._paint_textured_cemetery_ground(s, 800, 600, top_y=102, theme="abyss", seed=131)

        # 1. BÓVEDA CÓSMICA CON CRISTAL ROTO Y COLUMNAS DE FUEGO OSCURO
        self._paint_gothic_sky(s, 800, sky_h=86, moon_pos=(630, 36), theme="abyss", seed=131)

        # Columnas de Fuego Oscuro con borde negro al fondo
        for fx in (230, 400, 570):
            pygame.draw.rect(s, (0, 0, 0), (fx - 26, 0, 52, 86))
            pygame.draw.rect(s, (42, 8, 64), (fx - 22, 0, 44, 86))
            pygame.draw.rect(s, (215, 28, 92), (fx - 12, 0, 24, 86))
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
            pygame.draw.lines(s, (235, 35, 95), False, pts, 3)
            pygame.draw.lines(s, (255, 230, 245), False, pts, 1)

        # Muros perimetrales de cristal negro con púas carmesí
        for bx in range(0, 800, 24):
            pygame.draw.rect(s, (26, 14, 40), (bx, 80, 24, 24))
            pygame.draw.line(s, (68, 36, 98), (bx + 1, 81), (bx + 22, 81), 1)
            pygame.draw.rect(s, (0, 0, 0), (bx, 80, 24, 24), 2)
            pygame.draw.polygon(s, (220, 35, 92), [(bx + 6, 80), (bx + 12, 62), (bx + 18, 80)])
            pygame.draw.polygon(s, (0, 0, 0), [(bx + 6, 80), (bx + 12, 62), (bx + 18, 80)], 1)

        for by in range(80, 600, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (26, 14, 40), (mx, by, 24, 20))
                pygame.draw.rect(s, (0, 0, 0), (mx, by, 24, 20), 2)

        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (26, 14, 40), (bx, 576, 24, 24))
            pygame.draw.rect(s, (0, 0, 0), (bx, 576, 24, 24), 2)

        # Cristales negros brotando en las esquinas exteriores
        for cx_sh, cy_sh in [(88, 178), (712, 178), (94, 438), (706, 438)]:
            for ox, oy, sh_h in [(-10, 6, 22), (0, 0, 32), (10, 8, 20)]:
                pts = [(cx_sh + ox, cy_sh + oy - sh_h), (cx_sh + ox + 6, cy_sh + oy), (cx_sh + ox, cy_sh + oy + 8), (cx_sh + ox - 6, cy_sh + oy)]
                pygame.draw.polygon(s, (34, 12, 54), pts)
                pygame.draw.polygon(s, (235, 42, 102), pts, 1)

        # 2. PLAZA OCTOGONAL DEL CRISTAL QUEBRADO (ARENA DEL JEFE SUPREMO VAELKOR)
        cx, cy = 400, 235
        oct_outer = [(cx + int(math.cos(a) * 165), cy + int(math.sin(a) * 145)) for a in [i * math.pi / 4 for i in range(8)]]
        oct_inner = [(cx + int(math.cos(a) * 125), cy + int(math.sin(a) * 110)) for a in [i * math.pi / 4 for i in range(8)]]
        pygame.draw.polygon(s, (20, 10, 34), oct_outer)
        pygame.draw.polygon(s, (0, 0, 0), oct_outer, 4)
        pygame.draw.polygon(s, (235, 38, 98), oct_outer, 2)
        pygame.draw.polygon(s, (30, 14, 48), oct_inner)
        pygame.draw.polygon(s, (185, 38, 105), oct_inner, 2)

        # Estrella de Cristal Quebrado grabada en el centro
        for i in range(8):
            ang = i * (math.pi / 4.0)
            ex = cx + int(math.cos(ang) * 95)
            ey = cy + int(math.sin(ang) * 82)
            pygame.draw.line(s, (0, 0, 0), (cx, cy), (ex, ey), 5)
            pygame.draw.line(s, (235, 38, 98), (cx, cy), (ex, ey), 2)
            pygame.draw.line(s, (255, 225, 245), (cx, cy), ((cx + ex) // 2, (cy + ey) // 2), 1)

        # Calzada de cristal oscuro con Vestíbulo Simétrico Sur
        pygame.draw.rect(s, (22, 12, 36), (288, 438, 224, 62), border_radius=6)
        pygame.draw.rect(s, (0, 0, 0), (288, 438, 224, 62), 4, border_radius=6)
        pygame.draw.rect(s, (235, 38, 98), (288, 438, 224, 62), 2, border_radius=6)
        for ped_cx in (328, 472):
            pygame.draw.circle(s, (16, 8, 26), (ped_cx, 469), 20)
            pygame.draw.circle(s, (235, 38, 98), (ped_cx, 469), 20, 2)

        self._paint_cobblestone_avenue(s, 366, 376, 68, 200, style="abyss", seed=133)
        for gy in range(378, 576, 14):
            pygame.draw.rect(s, (215, 32, 88), (392, gy, 16, 12))

        # Monolito del Cristal Negro al norte
        throne_crystal = [(368, 120), (356, 76), (382, 86), (400, 50), (418, 86), (444, 76), (432, 120)]
        pygame.draw.polygon(s, (16, 6, 28), throne_crystal)
        pygame.draw.polygon(s, (0, 0, 0), throne_crystal, 4)
        pygame.draw.polygon(s, (245, 42, 102), throne_crystal, 2)

        self.world_objects.append(InteriorProp(
            364, 72, 72, 52, 126,
            lambda surf, x, y, w, h: None,
            [
                "* El Monolito del Cristal Quebrado, trono de Vaelkor.",
                "* Las llamas oscuras con borde negro parecen cortar el espacio mismo.",
            ],
            is_solid=True,
        ))

        self.world_objects.append(SavePointObject(x=326, y=452))
        self.world_objects.append(ChestObject(x=452, y=452))
        self.world_objects.append(SignObject(
            x=342, y=392,
            message="* SANTUARIO DEL CRISTAL QUEBRADO: 'Aquí aguarda Vaelkor, Rey del Cristal Negro. ¡Usa tu habilidad BlackFlash (50% TP) para romper su guardia!'",
        ))

        for bx_b, by_b in [(336, 114), (444, 114), (344, 514), (436, 514)]:
            self.world_objects.append(GothicBrazier(bx_b, by_b, flame_color=(240, 35, 98), core_color=(255, 225, 240)))

        for px, py in [(205, 155), (575, 155), (195, 295), (585, 295), (305, 495), (475, 495)]:
            self.world_objects.append(RuinPillar(px, py, style="abyss", has_candle=True))

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
        # 1. Hierba nocturna texturizada del cementerio y cielo estrellado con luna y cipreses
        self._paint_textured_cemetery_ground(s, 800, 600, top_y=100, theme="moonlit", seed=99)
        self._paint_gothic_sky(s, 800, sky_h=78, moon_pos=(132, 34), theme="moonlit", seed=99)

        # Muros perimetrales góticos con reja ornamental y hiedra (abierta entrada Oeste en y=318..370)
        self._paint_ornate_gothic_walls(s, 800, 600, top_y=76, open_south=False, open_east=False, open_west=True, theme="moonlit", seed=99)

        # Plaza Central del Atrio de la Iglesia y Avenidas Empedradas Desgastadas
        self._paint_cobblestone_avenue(s, 4, 326, 768, 40, style="moonlit", seed=201)
        self._paint_cobblestone_avenue(s, 264, 268, 272, 156, style="moonlit", seed=202)
        self._paint_cobblestone_avenue(s, 372, 244, 56, 292, style="moonlit", seed=203)

        # Pequeñas lápidas decorativas y flores nocturnas en los jardines laterales del Atrio
        for mgx, mgy, mtilt in [(112, 168, 0), (164, 206, 2), (636, 174, 0), (674, 212, -2), (138, 454, 0), (638, 454, 2)]:
            self._paint_decorative_minor_grave(s, mgx, mgy, tilt=mtilt)
        for fx, fy in [(152, 298), (648, 298), (152, 396), (648, 396), (344, 514), (456, 514)]:
            self._paint_flower_patch(s, fx, fy, color=(100, 195, 255), core=(235, 250, 255), count=4)

        # Rosetón de piedra grabado en el centro de la Plaza del Atrio
        pygame.draw.circle(s, (14, 18, 24), (400, 348), 47)
        pygame.draw.circle(s, (54, 58, 72), (400, 346), 45)
        pygame.draw.circle(s, (220, 192, 102), (400, 346), 45, 2)
        pygame.draw.circle(s, (72, 76, 92), (400, 346), 32)
        pygame.draw.circle(s, (115, 218, 255), (400, 346), 32, 1)
        for ang_i in range(8):
            a = ang_i * (math.pi / 4.0)
            pygame.draw.line(s, (195, 170, 98), (400, 346), (400 + int(math.cos(a) * 31), 346 + int(math.sin(a) * 31)), 1)
        pygame.draw.circle(s, (240, 212, 118), (400, 346), 8)
        pygame.draw.circle(s, (255, 250, 225), (400, 346), 3)

        # Jardineras góticas de piedra con flores doradas y celestes en las 4 esquinas del Atrio
        for fx_bed, fy_bed in [(274, 276), (482, 276), (274, 386), (482, 386)]:
            pygame.draw.rect(s, (14, 18, 22), (fx_bed - 2, fy_bed + 2, 48, 28), border_radius=5)
            pygame.draw.rect(s, (30, 44, 38), (fx_bed, fy_bed, 44, 28), border_radius=4)
            pygame.draw.rect(s, (124, 130, 150), (fx_bed, fy_bed, 44, 28), 2, border_radius=4)
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
            x=330, y=276,
            message="* CATEDRAL DEL CEMENTERIO: 'Entra por el pórtico norte. Más allá del altar mayor se oculta la puerta hacia el antiguo Sótano...'"
        ))
        self.world_objects.append(SavePointObject(x=446, y=276))
        self.world_objects.append(SignObject(
            x=48, y=296,
            message="* <- OESTE: Regresar a la plaza principal del Cementerio."
        ))

        for tx, ty in [(64, 156), (684, 156), (64, 464), (684, 464)]:
            self.world_objects.append(TwistedTreeProp(tx, ty, has_lantern=True))

        # Faroles góticos y pebeteros dorados iluminando el Atrio y el pórtico de la Catedral
        self.world_objects.append(GothicBrazier(340, 240, flame_color=(255, 195, 70), core_color=(255, 250, 210)))
        self.world_objects.append(GothicBrazier(440, 240, flame_color=(255, 195, 70), core_color=(255, 250, 210)))
        self.world_objects.append(GothicLampPost(248, 286, flame_color=(255, 215, 105), facing="RIGHT"))
        self.world_objects.append(GothicLampPost(536, 286, flame_color=(255, 215, 105), facing="LEFT"))
        self.world_objects.append(GothicLampPost(248, 368, flame_color=(255, 215, 105), facing="RIGHT"))
        self.world_objects.append(GothicLampPost(536, 368, flame_color=(255, 215, 105), facing="LEFT"))

        for px, py in [(226, 224), (554, 224), (218, 412), (562, 412)]:
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

        # Muros perimetrales neón del Dark World con PORTAL NORTE hacia la zona extra "Trono Oscuro"
        for bx in list(range(0, 368, 24)) + list(range(432, 800, 24)):
            pygame.draw.rect(s, (22, 12, 44), (bx, 80, 24, 24))
            pygame.draw.rect(s, (75, 245, 255), (bx, 80, 24, 24), 1)

        # Gran Arco Portal Neón en el Norte (x=364..436, y=54..114) hacia el Trono Oscuro (Jefe Nyxar)
        pygame.draw.rect(s, (28, 12, 54), (364, 56, 72, 56), border_top_left_radius=24, border_top_right_radius=24)
        pygame.draw.rect(s, (10, 6, 24), (372, 64, 56, 48), border_top_left_radius=18, border_top_right_radius=18)
        pygame.draw.rect(s, (75, 245, 255), (364, 56, 72, 56), 2, border_top_left_radius=24, border_top_right_radius=24)
        pygame.draw.rect(s, (255, 75, 215), (372, 64, 56, 48), 2, border_top_left_radius=18, border_top_right_radius=18)
        for bw_p, col_p in [(28, (95, 35, 165)), (16, (75, 245, 255)), (6, (255, 255, 255))]:
            pygame.draw.rect(s, col_p, (400 - bw_p // 2, 68, bw_p, 42))
        self.throne_gate_rect = pygame.Rect(370, 82, 60, 28)

        # Cartel avisando de la Zona Extra del Dark World (Trono Oscuro - Jefe Nyxar)
        self.world_objects.append(SignObject(
            x=456, y=126,
            message="* PORTAL NORTE -> 'TRONO OSCURO: Dominio de Nyxar, Soberano de la Fuente Oscura. ¡Prepárate antes de cruzar!'"
        ))

        for by in range(80, 600, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (22, 12, 44), (mx, by, 24, 20))
                pygame.draw.rect(s, (255, 75, 215), (mx, by, 24, 20), 1)
        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (22, 12, 44), (bx, 576, 24, 24))
            pygame.draw.rect(s, (75, 245, 255), (bx, 576, 24, 24), 1)

        self.solid_rects.append(pygame.Rect(0, 80, 368, 24))
        self.solid_rects.append(pygame.Rect(432, 80, 368, 24))
        self.solid_rects.append(pygame.Rect(368, 56, 64, 24))
        self.solid_rects.append(pygame.Rect(0, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(776, 80, 24, 520))
        self.solid_rects.append(pygame.Rect(0, 576, 370, 24))
        self.solid_rects.append(pygame.Rect(430, 576, 370, 24))

    # ==========================================================
    # 7.5 ZONA EXTRA DEL DARK WORLD: TRONO OSCURO (JEFE SECRETO NYXAR)
    # ==========================================================
    def _build_dark_world_throne(self):
        s = self.surface
        s.fill((6, 4, 18))

        # 1. Cielo abismal del núcleo del Dark World con la Gran Fuente Oscura rugiendo detrás del Trono
        for y in range(96):
            t = y / 96.0
            pygame.draw.line(s, (int(14 + 34 * t), int(6 + 14 * t), int(44 + 54 * t)), (0, y), (800, y))

        # Rayos diagonales de energía neón emanando de la Fuente Oscura
        rays = pygame.Surface((800, 600), pygame.SRCALPHA)
        pygame.draw.polygon(rays, (75, 245, 255, 22), [(400, 0), (140, 600), (310, 600)])
        pygame.draw.polygon(rays, (255, 75, 215, 22), [(400, 0), (490, 600), (660, 600)])
        pygame.draw.polygon(rays, (255, 232, 85, 14), [(400, 0), (330, 600), (470, 600)])
        s.blit(rays, (0, 0))

        # Columna principal de la Fuente Oscura
        for w_bar, col in [(136, (28, 14, 68)), (96, (68, 26, 142)), (58, (255, 70, 210)), (32, (80, 245, 255)), (14, (255, 255, 255))]:
            pygame.draw.rect(s, col, (400 - w_bar // 2, 0, w_bar, 108))

        # Cuadrícula ciber-gótica en el piso
        for gx in range(24, 776, 36):
            col_g = (52, 24, 88) if (gx // 36) % 2 == 0 else (26, 44, 78)
            pygame.draw.line(s, col_g, (gx, 96), (gx, 576), 1)
        for gy in range(96, 576, 36):
            col_g = (52, 24, 88) if (gy // 36) % 2 == 0 else (26, 44, 78)
            pygame.draw.line(s, col_g, (24, gy), (776, gy), 1)

        # 2. Gran Calzada Real Neón (Sur -> Arena Central -> Estrado del Trono)
        pygame.draw.rect(s, (24, 12, 48), (350, 146, 100, 430))
        pygame.draw.rect(s, (120, 22, 86), (366, 150, 68, 424))
        pygame.draw.line(s, (255, 228, 85), (366, 150), (366, 574), 2)
        pygame.draw.line(s, (255, 228, 85), (434, 150), (434, 574), 2)
        pygame.draw.line(s, (75, 245, 255), (350, 146), (350, 576), 2)
        pygame.draw.line(s, (75, 245, 255), (450, 146), (450, 576), 2)

        # 3. Gran Arena Octogonal de Combate contra Nyxar (x=210..590, y=184..416)
        arena_pts = [
            (254, 184), (546, 184), (590, 228), (590, 372),
            (546, 416), (254, 416), (210, 372), (210, 228)
        ]
        pygame.draw.polygon(s, (20, 10, 42), arena_pts)
        pygame.draw.polygon(s, (75, 245, 255), arena_pts, 3)
        inner_pts = [
            (268, 198), (532, 198), (572, 238), (572, 362),
            (532, 402), (268, 402), (228, 362), (228, 238)
        ]
        pygame.draw.polygon(s, (255, 75, 215), inner_pts, 1)
        # Sello Delta Rune gigante en el centro de la arena
        pygame.draw.circle(s, (255, 75, 215), (400, 300), 62, 2)
        pygame.draw.circle(s, (75, 245, 255), (400, 300), 48, 2)
        pygame.draw.circle(s, (255, 232, 85), (400, 282), 10, 2)
        for tri in [
            [(400, 318), (386, 298), (414, 298)],
            [(374, 314), (364, 298), (384, 298)],
            [(426, 314), (416, 298), (436, 298)],
        ]:
            pygame.draw.polygon(s, (255, 232, 85), tri, 1)

        # 4. Estrado del Trono de la Fuente Oscura (Norte, y=96..178)
        pygame.draw.rect(s, (30, 14, 58), (288, 96, 224, 76), border_radius=6)
        pygame.draw.rect(s, (255, 232, 85), (288, 96, 224, 76), 2, border_radius=6)
        # Escalinata hacia el trono
        for step_i, sw_s in enumerate((148, 126, 104)):
            sy_s = 172 - step_i * 8
            pygame.draw.rect(s, (48, 22, 86), (400 - sw_s // 2, sy_s, sw_s, 8))
            pygame.draw.line(s, (75, 245, 255), (400 - sw_s // 2, sy_s), (400 + sw_s // 2, sy_s), 1)
        # Trono cibernético-gótico de Nyxar
        pygame.draw.polygon(s, (18, 8, 36), [(372, 138), (366, 98), (384, 110), (400, 88), (416, 110), (434, 98), (428, 138)])
        pygame.draw.polygon(s, (255, 75, 215), [(372, 138), (366, 98), (384, 110), (400, 88), (416, 110), (434, 98), (428, 138)], 2)
        pygame.draw.rect(s, (255, 232, 85), (380, 128, 40, 12), 1)

        # 5. Obeliscos de Cristal Neón flanqueando la arena
        for ox, oy in [(142, 186), (626, 186), (142, 356), (626, 356)]:
            def draw_neon_obelisk(surf, cx, cy, w, h):
                pygame.draw.ellipse(surf, (8, 4, 22), (cx + 2, cy + 44, w - 4, 10))
                pts = [(cx + w // 2, cy), (cx + w - 4, cy + 16), (cx + w - 2, cy + 48), (cx + 2, cy + 48), (cx + 4, cy + 16)]
                pygame.draw.polygon(surf, (24, 12, 52), pts)
                pygame.draw.polygon(surf, (75, 245, 255), pts, 2)
                pygame.draw.line(surf, (255, 75, 215), (cx + w // 2, cy + 6), (cx + w // 2, cy + 44), 2)
                pygame.draw.circle(surf, (255, 232, 85), (cx + w // 2, cy + 18), 3)
            self.world_objects.append(InteriorProp(
                ox, oy, 32, 52, oy + 48, draw_neon_obelisk,
                ["* Un Obelisco de Cristal del Trono Oscuro. Vibra con la energía de Nyxar."],
                is_solid=True,
            ))

        # 6. Cofre de Reliquia detrás del jefe (otorga "Filo Eclipse": +8 ATK, +4 DEF)
        class DarkRelicChest(InteriorProp):
            def __init__(self, x, y):
                self.opened = False
                def draw_relic_chest(surf, cx, cy, w, h):
                    pygame.draw.ellipse(surf, (8, 4, 20), (cx, cy + h - 5, w, 7))
                    c_body = (48, 22, 82) if not self.opened else (28, 16, 44)
                    c_trim = (255, 232, 85) if not self.opened else (110, 120, 145)
                    pygame.draw.rect(surf, c_body, (cx + 2, cy + 4, w - 4, h - 6), border_radius=3)
                    pygame.draw.rect(surf, c_trim, (cx + 2, cy + 4, w - 4, h - 6), 2, border_radius=3)
                    pygame.draw.line(surf, (75, 245, 255), (cx + 3, cy + 11), (cx + w - 4, cy + 11), 2)
                    if not self.opened:
                        pygame.draw.rect(surf, (255, 235, 90), (cx + w // 2 - 2, cy + 9, 4, 5))
                super().__init__(x, y, 28, 22, y + 20, draw_relic_chest, ["* Cofre de la Fuente Oscura."], is_solid=True)

            def interact(self, dialogue_box, sound_fx, player=None):
                if not self.opened:
                    self.opened = True
                    sound_fx.play_chest()
                    relic = {
                        "name": "Filo Eclipse",
                        "slot": "WEAPON",
                        "atk_bonus": 8,
                        "def_bonus": 4,
                        "desc": "Hoja forjada en el Trono Oscuro. Incrementa +8 de Ataque y +4 de Defensa.",
                    }
                    if player and hasattr(player, "add_equipment"):
                        player.add_equipment(relic)
                    dialogue_box.start_dialogue([
                        "* ¡Abriste el Cofre Real del Trono Oscuro!",
                        "* Obtuviste la reliquia [Filo Eclipse] (+8 ATK, +4 DEF).",
                        "* (Se guardó en tu bolsa de equipo: pulsa [C] -> EQUIP para equiparla).",
                    ])
                else:
                    sound_fx.play_select()
                    dialogue_box.start_dialogue(["* El Cofre Real ya está vacío."])

        self.world_objects.append(DarkRelicChest(386, 138))

        # 7. Punto de Guardado y Cartel de aviso en la entrada sur antes de enfrentar a Nyxar
        self.world_objects.append(SavePointObject(x=306, y=496))
        self.world_objects.append(SignObject(
            x=470, y=496,
            message="* TRONO OSCURO: 'Aquí aguarda NYXAR. Combina Dash [X] contra sus muros dorados, Parry [Z] y ★ BlackFlash para vencerlo.'"
        ))

        for wx, wy, col in [
            (242, 214, (75, 245, 255)),
            (558, 214, (255, 75, 215)),
            (242, 386, (255, 232, 85)),
            (558, 386, (75, 245, 255)),
            (318, 126, (255, 75, 215)),
            (482, 126, (75, 245, 255)),
        ]:
            self.world_objects.append(WillOWisp(wx, wy, color=col))

        # 8. Muros perimetrales neón (con salida al sur de vuelta al Dark World)
        for bx in range(0, 800, 24):
            pygame.draw.rect(s, (22, 10, 44), (bx, 80, 24, 24))
            pygame.draw.rect(s, (255, 75, 215), (bx, 80, 24, 24), 1)
        for by in range(80, 600, 20):
            for mx in (0, 776):
                pygame.draw.rect(s, (22, 10, 44), (mx, by, 24, 20))
                pygame.draw.rect(s, (75, 245, 255), (mx, by, 24, 20), 1)
        for bx in list(range(0, 370, 24)) + list(range(430, 800, 24)):
            pygame.draw.rect(s, (22, 10, 44), (bx, 576, 24, 24))
            pygame.draw.rect(s, (255, 75, 215), (bx, 576, 24, 24), 1)

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
                "* • ¿DÓNDE SE GUARDA?: En las Estrellas Amarillas como la que tienes a la izquierda (están en el cementerio, cruces, la iglesia y antes de cada Jefe).\n"
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


