import math
import random
import pygame

# ==========================================================
# OBJETOS DEL MUNDO CON PROFUNDIDAD Y-SORTING
# ==========================================================
class WorldObject:
    """Clase base para todos los objetos con perspectiva y profundidad 2.5D."""
    def __init__(self, x, y, depth_y):
        self.x = x
        self.y = y
        self.depth_y = depth_y  # Posición Y para ordenar quién se dibuja delante/detrás
        self.solid_rect = None
        self.interactable = False
        self.prompt_text = ""

    def update(self, dt):
        pass

    def draw(self, surface, camera):
        pass

    def interact(self, dialogue_box, sound_fx, player=None):
        pass


class TreeObject(WorldObject):
    """Árbol con tronco sólido y copa con profundidad Y-Sorting."""
    def __init__(self, x, y):
        # Base del tronco está en y + 54
        super().__init__(x, y, depth_y=y + 54)
        # Sólido únicamente en el tronco (los pies colisionan, pero la copa permite estar detrás o delante)
        self.solid_rect = pygame.Rect(x + 16, y + 42, 20, 14)
        self.surf = self._create_tree_surface()

    def _create_tree_surface(self):
        w, h = 52, 60
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Sombra en el suelo
        pygame.draw.ellipse(surf, (15, 30, 20, 110), (10, 48, 32, 12))
        # Tronco
        pygame.draw.rect(surf, (85, 50, 30), (20, 36, 12, 18), border_radius=2)
        pygame.draw.rect(surf, (65, 38, 22), (28, 36, 4, 18), border_radius=1)
        # Copa de hojas (Estilo Undertale / Earthbound)
        pygame.draw.circle(surf, (28, 78, 38), (26, 26), 22)
        pygame.draw.circle(surf, (38, 105, 50), (26, 22), 20)
        pygame.draw.circle(surf, (55, 140, 68), (23, 18), 15)
        pygame.draw.circle(surf, (72, 175, 85), (20, 14), 8)
        return surf

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        surface.blit(self.surf, (cx, cy))


class SavePointObject(WorldObject):
    """El icónico punto de guardado de Undertale/Deltarune (Estrella amarilla giratoria)."""
    def __init__(self, x, y):
        super().__init__(x, y, depth_y=y + 20)
        self.solid_rect = pygame.Rect(x + 4, y + 10, 16, 12)
        self.interactable = True
        self.angle = 0.0
        self.sparkle_timer = 0.0
        self.sparkles = []

    def update(self, dt):
        self.angle = (self.angle + dt * 140) % 360
        self.sparkle_timer += dt
        if self.sparkle_timer >= 0.25:
            self.sparkle_timer = 0.0
            self.sparkles.append({
                "x": self.x + 12 + random.uniform(-10, 10),
                "y": self.y + 8 + random.uniform(-8, 8),
                "life": 0.4,
                "max": 0.4
            })
        for s in self.sparkles:
            s["y"] -= dt * 10
            s["life"] -= dt
        self.sparkles = [s for s in self.sparkles if s["life"] > 0]

    def draw(self, surface, camera):
        # Sombra sutil en el suelo
        cx, cy = camera.apply((self.x, self.y))
        pygame.draw.ellipse(surface, (20, 25, 10, 100), (cx + 3, cy + 18, 18, 6))

        # Estrella giratoria de 4 puntas
        star_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Dibujar estrella con rotación
        center = 12
        rad = math.radians(self.angle)
        scale = 0.85 + 0.15 * math.sin(rad * 2)
        pts = []
        for i in range(8):
            r = (9 if i % 2 == 0 else 3.5) * scale
            a = rad + i * (math.pi / 4)
            pts.append((center + math.cos(a) * r, center + math.sin(a) * r))
        pygame.draw.polygon(star_surf, (255, 245, 80), pts)
        pygame.draw.polygon(star_surf, (255, 255, 200), [(p[0] * 0.6 + center * 0.4, p[1] * 0.6 + center * 0.4) for p in pts])

        surface.blit(star_surf, (cx, cy))

        # Destellos
        for sp in self.sparkles:
            scx, scy = camera.apply((sp["x"], sp["y"]))
            alpha = int(255 * (sp["life"] / sp["max"]))
            ps = pygame.Surface((3, 3), pygame.SRCALPHA)
            ps.fill((255, 255, 150, alpha))
            surface.blit(ps, (scx, scy))

    def interact(self, dialogue_box, sound_fx, player=None):
        sound_fx.play_save()
        if player:
            player.hp = player.max_hp
            player.modify_sanity(25.0)  # La estrella reconforta el alma y recupera cordura

        if player and player.death_count > 0:
            lines = [
                f"* Recuerdas las {player.death_count} veces que tu corazón se partió ante la muerte...",
                "* Pero saber que tu alma se niega a perecer te llena de una sombría DETERMINACIÓN.",
                "* (Punto de guardado registrado. HP restaurado al máximo y tu mente se sosiega).",
            ]
        else:
            lines = [
                "* El suave aroma a pino y la vista del claro te llenan de DETERMINACIÓN.",
                "* (Punto de guardado registrado. HP restaurado al máximo).",
            ]
        dialogue_box.start_dialogue(lines)


class SignObject(WorldObject):
    """Cartel de madera estilo Undertale."""
    def __init__(self, x, y, message):
        super().__init__(x, y, depth_y=y + 24)
        self.solid_rect = pygame.Rect(x + 4, y + 14, 16, 12)
        self.interactable = True
        self.message = message

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Poste
        pygame.draw.rect(surface, (90, 60, 40), (cx + 10, cy + 12, 4, 12))
        # Tablón
        pygame.draw.rect(surface, (160, 115, 75), (cx + 2, cy + 2, 20, 13), border_radius=2)
        pygame.draw.rect(surface, (115, 75, 45), (cx + 2, cy + 2, 20, 13), 1, border_radius=2)
        pygame.draw.line(surface, (115, 75, 45), (cx + 5, cy + 6), (cx + 19, cy + 6), 1)
        pygame.draw.line(surface, (115, 75, 45), (cx + 5, cy + 10), (cx + 17, cy + 10), 1)

    def interact(self, dialogue_box, sound_fx, player=None):
        sound_fx.play_select()
        if isinstance(self.message, list):
            dialogue_box.start_dialogue(self.message)
        else:
            pages = [ln.strip() for ln in str(self.message).split("\n") if ln.strip()]
            dialogue_box.start_dialogue(pages if pages else [str(self.message)])


class ChestObject(WorldObject):
    """Cofre del tesoro que se puede abrir."""
    def __init__(self, x, y):
        super().__init__(x, y, depth_y=y + 22)
        self.solid_rect = pygame.Rect(x + 2, y + 8, 20, 14)
        self.interactable = True
        self.is_open = False

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Base del cofre
        pygame.draw.rect(surface, (135, 75, 35), (cx + 2, cy + 8, 20, 12), border_radius=2)
        pygame.draw.rect(surface, (215, 175, 55), (cx + 10, cy + 10, 4, 5))
        # Tapa
        if not self.is_open:
            pygame.draw.rect(surface, (170, 95, 45), (cx + 1, cy + 3, 22, 7), border_radius=2)
            pygame.draw.rect(surface, (230, 195, 70), (cx + 10, cy + 6, 4, 3))
        else:
            pygame.draw.rect(surface, (100, 50, 25), (cx + 2, cy + 1, 20, 7), border_radius=2)
            pygame.draw.circle(surface, (255, 230, 100), (cx + 12, cy + 6), 3)

    def interact(self, dialogue_box, sound_fx, player=None):
        if not self.is_open:
            self.is_open = True
            sound_fx.play_chest()
            if player is not None and hasattr(player, "inventory"):
                player.inventory.append({
                    "name": "Chocolate Oscuro",
                    "heal": 14,
                    "sanity_heal": 15,
                    "desc": "Chocolate antiguo. Restaura 14 HP y +15% de cordura."
                })
            dialogue_box.start_dialogue([
                "* ¡Abriste el cofre antiguo!",
                "* Encontraste un [Chocolate Oscuro].",
                "* (Fue añadido al inventario de Paniel).",
            ])
        else:
            sound_fx.play_select()
            dialogue_box.start_dialogue(["* El cofre ya está vacío."])


class RuinPillar(WorldObject):
    """Pilar gótico tallado de piedra antigua con musgo, grietas, hiedra y vela opcional."""
    def __init__(self, x, y, style="gothic", has_candle=True):
        super().__init__(x, y, depth_y=y + 38)
        self.solid_rect = pygame.Rect(x + 4, y + 26, 16, 14)
        self.style = style
        self.has_candle = has_candle
        self.flicker = random.uniform(0, 10)

    def update(self, dt):
        self.flicker += dt * 7.0

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Sombra suave en el suelo
        sh = pygame.Surface((26, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (6, 8, 14, 130), (0, 0, 26, 10))
        surface.blit(sh, (cx - 1, cy + 33))

        if self.style == "abyss":
            stone_dark = (36, 26, 52)
            stone_mid = (58, 42, 80)
            stone_hi = (98, 68, 128)
            moss_col = (140, 35, 95)
            flame_outer = (235, 55, 115)
        else:
            stone_dark = (54, 58, 70)
            stone_mid = (92, 98, 114)
            stone_hi = (138, 146, 168)
            moss_col = (54, 108, 66)
            flame_outer = (255, 195, 75)

        # Base escalonada
        pygame.draw.rect(surface, stone_dark, (cx + 1, cy + 33, 22, 6), border_radius=2)
        pygame.draw.rect(surface, stone_mid, (cx + 2, cy + 31, 20, 4), border_radius=1)
        pygame.draw.line(surface, stone_hi, (cx + 3, cy + 31), (cx + 20, cy + 31), 1)

        # Fuste estriado con volumen 3D (luz lunar desde la izquierda/arriba)
        pygame.draw.rect(surface, stone_mid, (cx + 4, cy + 7, 16, 25), border_radius=1)
        pygame.draw.rect(surface, stone_hi, (cx + 5, cy + 8, 3, 23))
        pygame.draw.rect(surface, stone_dark, (cx + 16, cy + 8, 4, 23))
        # Estrías verticales
        pygame.draw.line(surface, stone_dark, (cx + 9, cy + 9), (cx + 9, cy + 30), 1)
        pygame.draw.line(surface, stone_dark, (cx + 13, cy + 9), (cx + 13, cy + 30), 1)
        pygame.draw.rect(surface, (24, 24, 34), (cx + 4, cy + 7, 16, 25), 1)

        # Capitel gótico moldurado
        pygame.draw.rect(surface, stone_mid, (cx + 1, cy + 3, 22, 5), border_radius=1)
        pygame.draw.line(surface, stone_hi, (cx + 2, cy + 3), (cx + 21, cy + 3), 1)
        pygame.draw.rect(surface, (24, 24, 34), (cx + 1, cy + 3, 22, 5), 1, border_radius=1)

        # Grieta diagonal y musgo/hiedra trepadora
        pygame.draw.line(surface, (30, 30, 40), (cx + 15, cy + 10), (cx + 11, cy + 19), 1)
        pygame.draw.line(surface, (30, 30, 40), (cx + 11, cy + 19), (cx + 13, cy + 24), 1)
        pygame.draw.ellipse(surface, moss_col, (cx + 4, cy + 16, 6, 9))
        pygame.draw.ellipse(surface, (min(255, moss_col[0] + 24), min(255, moss_col[1] + 28), min(255, moss_col[2] + 20)), (cx + 5, cy + 17, 3, 5))
        pygame.draw.circle(surface, moss_col, (cx + 15, cy + 28), 3)

        # Pequeña vela votiva titilante sobre el capitel
        if self.has_candle:
            pygame.draw.rect(surface, (235, 228, 205), (cx + 10, cy - 2, 4, 5))
            f_bob = int(math.sin(self.flicker) * 1)
            glow = pygame.Surface((24, 24), pygame.SRCALPHA)
            a_pulse = int(42 + math.sin(self.flicker * 1.4) * 14)
            pygame.draw.circle(glow, (*flame_outer, a_pulse), (12, 12), 11)
            pygame.draw.circle(glow, (255, 240, 170, a_pulse + 30), (12, 12), 5)
            surface.blit(glow, (cx, cy - 15))
            pygame.draw.circle(surface, flame_outer, (cx + 12, cy - 4 + f_bob), 2)
            pygame.draw.circle(surface, (255, 250, 225), (cx + 12, cy - 4 + f_bob), 1)


# ==========================================================
# OBJETOS AMBIENTALES DEL CEMENTERIO (Árboles góticos, Faroles, Pebeteros y Ánimas)
# ==========================================================
class WillOWisp(WorldObject):
    """Fuego fatuo / ánima etérea que flota suavemente por el cementerio con estela luminosa."""
    def __init__(self, x, y, color=(130, 235, 255)):
        super().__init__(x, y, depth_y=y + 12)
        self.base_x = x
        self.base_y = y
        self.color = color
        self.time = random.uniform(0, 10)
        self.drift_speed = random.uniform(0.7, 1.25)
        self.orbit_rx = random.uniform(14, 28)
        self.orbit_ry = random.uniform(7, 14)
        self.particles = []

    def update(self, dt):
        self.time += dt * self.drift_speed
        self.x = self.base_x + math.sin(self.time) * self.orbit_rx
        self.y = self.base_y + math.cos(self.time * 1.35) * self.orbit_ry
        self.depth_y = self.y + 12

        if random.random() < 0.36:
            self.particles.append({
                "x": self.x + random.uniform(-2, 2),
                "y": self.y + random.uniform(-2, 2),
                "life": 0.65,
                "max_life": 0.65,
                "radius": random.uniform(1.0, 2.4)
            })

        for p in self.particles:
            p["life"] -= dt
            p["y"] -= dt * 5.0
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        for p in self.particles:
            px, py = camera.apply((p["x"], p["y"]))
            ratio = max(0.0, min(1.0, p["life"] / p["max_life"]))
            alpha = int(175 * ratio)
            r = max(1, int(p["radius"] * ratio + 0.5))
            ps = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*self.color, alpha), (r + 1, r + 1), r)
            surface.blit(ps, (px - r - 1, py - r - 1))

        pulse = 1.0 + 0.14 * math.sin(self.time * 4.5)
        rad = int(14 * pulse)
        aura = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        c = rad + 1
        pygame.draw.circle(aura, (*self.color, 26), (c, c), rad)
        pygame.draw.circle(aura, (*self.color, 65), (c, c), max(2, int(rad * 0.62)))
        pygame.draw.circle(aura, (*self.color, 130), (c, c), max(2, int(rad * 0.35)))
        pygame.draw.circle(aura, (255, 255, 255, 240), (c, c), 2)
        surface.blit(aura, (cx - c, cy - c))


class TwistedTreeProp(WorldObject):
    """Árbol gótico monumental (sauce llorón / roble ancestral) con follaje nocturno, raíces, musgo y farol."""
    def __init__(self, x, y, has_lantern=True, foliage_tint="moonlit"):
        super().__init__(x, y, depth_y=y + 62)
        self.w = 64
        self.h = 74
        self.solid_rect = pygame.Rect(x + 20, y + 48, 22, 14)
        self.has_lantern = has_lantern
        self.foliage_tint = foliage_tint
        self.flicker = random.uniform(0, 10)
        self.tree_surf = self._bake_tree_surface()

    def _bake_tree_surface(self):
        trunk = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        if self.foliage_tint == "abyss":
            bark_dark = (22, 14, 28)
            bark_mid = (40, 26, 50)
            bark_hi = (72, 46, 86)
            leaf_dark = (28, 12, 42, 235)
            leaf_mid = (56, 20, 74, 225)
            leaf_hi = (108, 38, 118, 200)
            moss_col = (145, 55, 125, 175)
        else:
            bark_dark = (24, 22, 28)
            bark_mid = (44, 38, 46)
            bark_hi = (76, 70, 84)
            leaf_dark = (18, 30, 38, 238)
            leaf_mid = (28, 50, 58, 228)
            leaf_hi = (52, 88, 96, 200)
            moss_col = (64, 104, 84, 185)

        # Sombra orgánica amplia en la base
        pygame.draw.ellipse(trunk, (6, 8, 12, 130), (8, 54, 48, 16))

        # Raíces retorcidas agarrando la tierra
        pygame.draw.polygon(trunk, bark_dark, [(12, 64), (22, 48), (42, 48), (52, 64), (44, 65), (36, 56), (28, 56), (20, 65)])
        pygame.draw.polygon(trunk, bark_mid, [(16, 62), (24, 46), (39, 46), (48, 62), (41, 61), (35, 53), (27, 53), (22, 61)])
        # Tronco principal nudoso con corteza iluminada por la luna
        pygame.draw.polygon(trunk, bark_dark, [(23, 54), (25, 28), (38, 28), (41, 54)])
        pygame.draw.polygon(trunk, bark_mid, [(25, 52), (27, 29), (36, 29), (38, 52)])
        pygame.draw.line(trunk, bark_hi, (27, 50), (28, 30), 2)
        pygame.draw.line(trunk, bark_dark, (33, 48), (32, 34), 1)
        # Nudo hueco en el tronco
        pygame.draw.ellipse(trunk, (12, 10, 16), (30, 40, 4, 6))

        # Ramas principales góticas
        branches = [
            ((28, 32), (10, 18), 4), ((10, 18), (3, 12), 2), ((10, 18), (15, 7), 2),
            ((35, 31), (52, 19), 4), ((52, 19), (60, 13), 2), ((52, 19), (46, 8), 2),
            ((31, 30), (31, 10), 3), ((31, 10), (23, 4), 2), ((31, 10), (39, 4), 2),
        ]
        for p1, p2, w_b in branches:
            pygame.draw.line(trunk, bark_dark, p1, p2, w_b + 2)
            pygame.draw.line(trunk, bark_mid, p1, p2, w_b)

        # Copa de sauce llorón / follaje nocturno en capas suaves con brillo lunar
        canopy_back = [(14, 18, 12), (28, 12, 14), (42, 14, 13), (50, 20, 11), (22, 24, 11), (38, 23, 11)]
        for lx, ly, lr in canopy_back:
            pygame.draw.circle(trunk, leaf_dark, (lx, ly), lr)
        canopy_mid = [(16, 15, 9), (28, 10, 11), (41, 12, 10), (49, 18, 8), (32, 18, 9)]
        for lx, ly, lr in canopy_mid:
            pygame.draw.circle(trunk, leaf_mid, (lx, ly), lr)
        # Borde superior tocado por la luz de la luna
        canopy_hi = [(20, 10, 5), (30, 7, 6), (41, 9, 5), (48, 14, 4)]
        for lx, ly, lr in canopy_hi:
            pygame.draw.circle(trunk, leaf_hi, (lx, ly), lr)

        # Cortinas de hojas/musgo colgante estilo sauce llorón
        for mx, my, mlen in [(8, 22, 12), (13, 24, 15), (19, 25, 11), (42, 24, 14), (48, 23, 12), (55, 21, 10)]:
            pygame.draw.line(trunk, moss_col, (mx, my), (mx, my + mlen), 2)
            pygame.draw.line(trunk, leaf_hi, (mx, my), (mx, my + mlen // 2), 1)

        return trunk

    def update(self, dt):
        self.flicker += dt * 5.2

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        surface.blit(self.tree_surf, (cx, cy))

        # Farol de hierro forjado colgante que se balancea suavemente
        if self.has_lantern:
            sway = int(math.sin(self.flicker * 0.45) * 1.4)
            lx = cx + 50 + sway
            ly = cy + 25
            # Cadena de hierro
            pygame.draw.line(surface, (62, 60, 72), (cx + 52, cy + 19), (lx + 3, ly), 1)
            # Tejadillo y estructura del farol
            pygame.draw.polygon(surface, (34, 30, 42), [(lx - 1, ly + 1), (lx + 3, ly - 3), (lx + 8, ly + 1)])
            pygame.draw.rect(surface, (36, 32, 46), (lx, ly + 1, 7, 9), border_radius=1)
            flicker_a = int(185 + math.sin(self.flicker * 1.8) * 42)
            if self.foliage_tint == "abyss":
                f_col = (235, 85, 165)
                g_col = (210, 50, 140)
            else:
                f_col = (255, 210, 95)
                g_col = (255, 185, 65)
            pygame.draw.rect(surface, f_col, (lx + 1, ly + 3, 5, 5))
            pygame.draw.rect(surface, (255, 250, 220), (lx + 2, ly + 4, 3, 3))
            # Halo cálido volumétrico
            glow = pygame.Surface((42, 42), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*g_col, max(0, min(255, flicker_a // 6))), (21, 21), 20)
            pygame.draw.circle(glow, (*f_col, max(0, min(255, flicker_a // 3))), (21, 21), 11)
            pygame.draw.circle(glow, (255, 245, 195, max(0, min(255, flicker_a // 2))), (21, 21), 5)
            surface.blit(glow, (lx - 18, ly - 15))


class GothicLampPost(WorldObject):
    """Farol gótico victoriano de hierro forjado para iluminar las avenidas del cementerio."""
    def __init__(self, x, y, flame_color=(255, 205, 95), facing="RIGHT"):
        super().__init__(x, y, depth_y=y + 42)
        self.solid_rect = pygame.Rect(x + 4, y + 34, 8, 8)
        self.flame_color = flame_color
        self.facing = facing
        self.flicker = random.uniform(0, 10)

    def update(self, dt):
        self.flicker += dt * 6.0

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Sombra y halo en el suelo bajo el farol
        g_pool = pygame.Surface((44, 20), pygame.SRCALPHA)
        pulse = int(34 + math.sin(self.flicker) * 9)
        pygame.draw.ellipse(g_pool, (*self.flame_color, pulse), (0, 0, 44, 20))
        surface.blit(g_pool, (cx - 14, cy + 32))

        # Pedestal de piedra y fuste de hierro forjado
        pygame.draw.rect(surface, (52, 54, 66), (cx + 3, cy + 35, 10, 7), border_radius=1)
        pygame.draw.rect(surface, (86, 90, 108), (cx + 4, cy + 35, 3, 6))
        pygame.draw.rect(surface, (28, 28, 36), (cx + 3, cy + 35, 10, 7), 1, border_radius=1)

        pygame.draw.rect(surface, (34, 34, 44), (cx + 6, cy + 8, 4, 28))
        pygame.draw.line(surface, (76, 78, 96), (cx + 7, cy + 9), (cx + 7, cy + 34), 1)
        # Voluta gótica decorativa
        arm_dir = 1 if self.facing == "RIGHT" else -1
        arm_end_x = cx + 8 + arm_dir * 8
        pygame.draw.line(surface, (42, 42, 54), (cx + 8, cy + 10), (arm_end_x, cy + 7), 2)
        pygame.draw.line(surface, (62, 64, 80), (cx + 8, cy + 14), (cx + 8 + arm_dir * 5, cy + 10), 1)
        # Remate puntiagudo superior
        pygame.draw.polygon(surface, (56, 58, 74), [(cx + 6, cy + 8), (cx + 8, cy + 2), (cx + 10, cy + 8)])

        # Farol colgante
        lx = arm_end_x - 3
        ly = cy + 9
        pygame.draw.polygon(surface, (34, 34, 44), [(lx - 1, ly + 1), (lx + 3, ly - 2), (lx + 7, ly + 1)])
        pygame.draw.rect(surface, (30, 30, 40), (lx, ly + 1, 7, 9), border_radius=1)
        pygame.draw.rect(surface, self.flame_color, (lx + 1, ly + 3, 5, 5))
        pygame.draw.rect(surface, (255, 252, 230), (lx + 2, ly + 4, 3, 3))

        # Resplandor luminoso
        halo = pygame.Surface((46, 46), pygame.SRCALPHA)
        ha = int(55 + math.sin(self.flicker * 1.4) * 14)
        pygame.draw.circle(halo, (*self.flame_color, ha // 2), (23, 23), 22)
        pygame.draw.circle(halo, (*self.flame_color, ha), (23, 23), 12)
        pygame.draw.circle(halo, (255, 250, 220, ha + 35), (23, 23), 5)
        surface.blit(halo, (lx - 19, ly - 17))


class GothicBrazier(WorldObject):
    """Pebetero gótico de piedra con fuego animado (carmesí, violeta miasma o dorado) y brasas ascendentes."""
    def __init__(self, x, y, flame_color=(225, 55, 110), core_color=(255, 220, 145)):
        super().__init__(x, y, depth_y=y + 24)
        self.solid_rect = pygame.Rect(x + 2, y + 12, 16, 12)
        self.flame_color = flame_color
        self.core_color = core_color
        self.time = random.uniform(0, 10)
        self.embers = []

    def update(self, dt):
        self.time += dt * 8.0
        if random.random() < 0.35:
            self.embers.append({
                "x": self.x + 10 + random.uniform(-4, 4),
                "y": self.y + 4,
                "vx": random.uniform(-6, 6),
                "vy": random.uniform(-16, -28),
                "life": random.uniform(0.4, 0.8),
                "max_life": 0.8,
            })
        for e in self.embers:
            e["x"] += e["vx"] * dt
            e["y"] += e["vy"] * dt
            e["life"] -= dt
        self.embers = [e for e in self.embers if e["life"] > 0]

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Resplandor en el suelo
        glow = pygame.Surface((46, 36), pygame.SRCALPHA)
        ga = int(46 + math.sin(self.time) * 14)
        pygame.draw.ellipse(glow, (*self.flame_color, ga), (2, 10, 42, 24))
        pygame.draw.circle(glow, (*self.flame_color, ga + 18), (23, 14), 14)
        surface.blit(glow, (cx - 13, cy - 6))

        # Pedestal de piedra tallada
        pygame.draw.polygon(surface, (44, 42, 56), [(cx + 2, cy + 24), (cx + 18, cy + 24), (cx + 15, cy + 13), (cx + 5, cy + 13)])
        pygame.draw.polygon(surface, (76, 74, 92), [(cx + 1, cy + 8), (cx + 19, cy + 8), (cx + 16, cy + 14), (cx + 4, cy + 14)])
        pygame.draw.polygon(surface, (22, 20, 30), [(cx + 1, cy + 8), (cx + 19, cy + 8), (cx + 16, cy + 14), (cx + 4, cy + 14)], 1)
        pygame.draw.line(surface, (115, 112, 134), (cx + 3, cy + 9), (cx + 16, cy + 9), 1)

        # Lenguas de fuego animadas
        sway = int(math.sin(self.time * 1.1) * 2)
        h_fl = int(11 + math.sin(self.time * 1.7) * 3)
        outer = [(cx + 4, cy + 8), (cx + 10 + sway, cy + 8 - h_fl), (cx + 16, cy + 8)]
        inner = [(cx + 7, cy + 8), (cx + 10 + sway // 2, cy + 8 - int(h_fl * 0.62)), (cx + 13, cy + 8)]
        pygame.draw.polygon(surface, self.flame_color, outer)
        pygame.draw.polygon(surface, self.core_color, inner)

        # Brasas ascendentes
        for e in self.embers:
            ex, ey = camera.apply((e["x"], e["y"]))
            a = int(220 * max(0.0, min(1.0, e["life"] / e["max_life"])))
            es = pygame.Surface((3, 3), pygame.SRCALPHA)
            es.fill((*self.core_color, a))
            surface.blit(es, (ex - 1, ey - 1))


class CemeteryCandleProp(WorldObject):
    """Pequeño conjunto de velas votivas titilantes sobre el suelo o junto a lápidas."""
    def __init__(self, x, y, flame_color=(255, 215, 95)):
        super().__init__(x, y, depth_y=y + 10)
        self.flame_color = flame_color
        self.time = random.uniform(0, 10)

    def update(self, dt):
        self.time += dt * 7.5

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        glow = pygame.Surface((26, 22), pygame.SRCALPHA)
        ga = int(42 + math.sin(self.time) * 12)
        pygame.draw.ellipse(glow, (*self.flame_color, ga), (0, 2, 26, 18))
        surface.blit(glow, (cx - 8, cy - 8))
        for ox, oy, ch in [(0, 2, 6), (4, 0, 8), (8, 3, 5)]:
            pygame.draw.rect(surface, (238, 232, 214), (cx + ox, cy + oy, 3, ch))
            pygame.draw.rect(surface, (190, 182, 162), (cx + ox + 2, cy + oy, 1, ch))
            fb = int(math.sin(self.time + ox) * 0.8)
            pygame.draw.circle(surface, self.flame_color, (cx + ox + 1, cy + oy - 2 + fb), 2)
            pygame.draw.circle(surface, (255, 252, 230), (cx + ox + 1, cy + oy - 2 + fb), 1)


# OBJETOS INTERIORES INTERACTIVOS (Muebles, NPCs, Lore)
# ==========================================================
class InteriorProp(WorldObject):
    def __init__(self, x, y, w, h, depth_y, draw_func, dialogue_lines, is_solid=True):
        super().__init__(x, y, depth_y=depth_y)
        self.w = w
        self.h = h
        self.draw_func = draw_func
        self.dialogue_lines = dialogue_lines
        self.interactable = bool(dialogue_lines)
        if is_solid:
            self.solid_rect = pygame.Rect(x, y, w, h)
        else:
            self.solid_rect = None

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        self.draw_func(surface, cx, cy, self.w, self.h)

    def interact(self, dialogue_box, sound_fx, player=None):
        if hasattr(self, '_is_open_grave') and self._is_open_grave and player is not None:
            # Tumba abierta con el nombre de Paniel
            if player.death_count > 0:
                lines = [
                    f"* Una lapida sin terminar. En ella se lee: 'PANIEL'.",
                    f"* Debajo, tallado toscamente: 'Ha muerto {player.death_count} vez/veces.'",
                    "* (El suelo helado parece recordarte algo)",
                    "* Tu cordura se resiente ante esta vision. (-15 cordura)"
                ]
                player.modify_sanity(-15.0)
            else:
                lines = [
                    "* Una tumba abierta sin nombre.",
                    "* La tierra removida huele a humedad y silencio.",
                    "* El hoyo es... exactamente de tu tamano.",
                    "* (Una corriente fria te eriza la piel)"
                ]
            sound_fx.play_select()
            dialogue_box.start_dialogue(lines)
        elif self.dialogue_lines:
            if player is not None and hasattr(self, '_sanity_boost') and self._sanity_boost:
                player.modify_sanity(float(self._sanity_boost))
            sound_fx.play_select()
            dialogue_box.start_dialogue(self.dialogue_lines)


class DarkWorldVendorNPC(WorldObject):
    """Vendedor misterioso del Dark World que ofrece el objeto 'Sturdy Arm' (+5 ATK y +10 DEF)."""
    def __init__(self, x, y):
        super().__init__(x, y, depth_y=y + 42)
        self.w = 56
        self.h = 46
        self.solid_rect = pygame.Rect(x + 4, y + 18, 48, 26)
        self.interactable = True
        self.sold_sturdy_arm = False
        self.anim_time = 0.0

    def update(self, dt):
        self.anim_time += dt

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        bob = int(math.sin(self.anim_time * 3.8) * 2)

        # Sombra neón bajo el puesto del vendedor
        pygame.draw.ellipse(surface, (10, 6, 22), (cx + 2, cy + 36, 52, 12))

        # Vendedor del Dark World (estilo Rouxls / Swatch / Spamton con gafas neón y túnica cian/magenta)
        vx = cx + 28
        vy = cy + 12 + bob
        pygame.draw.polygon(surface, (28, 16, 48), [(vx - 11, vy + 2), (vx + 11, vy + 2), (vx + 15, vy + 22), (vx - 15, vy + 22)])
        pygame.draw.polygon(surface, (80, 235, 255), [(vx - 11, vy + 2), (vx + 11, vy + 2), (vx + 15, vy + 22), (vx - 15, vy + 22)], 1)
        pygame.draw.circle(surface, (18, 12, 32), (vx, vy - 3), 8)
        # Sombrero / capucha de mercader del Dark World
        pygame.draw.polygon(surface, (45, 20, 72), [(vx - 11, vy - 5), (vx, vy - 15), (vx + 11, vy - 5)])
        pygame.draw.polygon(surface, (255, 85, 210), [(vx - 11, vy - 5), (vx, vy - 15), (vx + 11, vy - 5)], 1)
        # Gafas asimétricas neón (rosa y amarillo estilo Deltarune)
        pygame.draw.rect(surface, (255, 95, 210), (vx - 6, vy - 5, 5, 4))
        pygame.draw.rect(surface, (255, 240, 80), (vx + 1, vy - 5, 5, 4))

        # Mostrador de cristal oscuro del Dark World
        pygame.draw.rect(surface, (22, 14, 38), (cx + 4, cy + 24, 48, 18), border_radius=3)
        pygame.draw.rect(surface, (0, 0, 0), (cx + 4, cy + 24, 48, 18), 3, border_radius=3)
        pygame.draw.rect(surface, (85, 240, 255), (cx + 4, cy + 24, 48, 18), 1, border_radius=3)
        # Letrero SHOP en el frontal
        pygame.draw.line(surface, (255, 90, 210), (cx + 10, cy + 33), (cx + 46, cy + 33), 2)

        # Objeto "Sturdy Arm" expuesto sobre un cojín flotante si aún no se ha vendido
        if not self.sold_sturdy_arm:
            ax = cx + 14
            ay = cy + 19 - abs(bob)
            pygame.draw.circle(surface, (90, 245, 255), (ax, ay), 6, 1)
            # Brazo robótico/mágico plateado y cian
            pygame.draw.rect(surface, (180, 205, 235), (ax - 5, ay - 2, 10, 4), border_radius=1)
            pygame.draw.rect(surface, (0, 0, 0), (ax - 5, ay - 2, 10, 4), 1, border_radius=1)
            pygame.draw.circle(surface, (255, 230, 80), (ax + 3, ay), 2)

    def interact(self, dialogue_box, sound_fx, player=None, shop_menu=None):
        if player is None:
            return
        if shop_menu is not None:
            shop_menu.open(vendor_npc=self, player=player)
            return
        if not self.sold_sturdy_arm:
            self.sold_sturdy_arm = True
            sound_fx.play_chest()
            cost = min(player.gold, 25)
            player.gold -= cost
            sturdy_gear = {
                "name": "Sturdy Arm",
                "slot": "BOTH",
                "atk_bonus": 5,
                "def_bonus": 10,
                "desc": "¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.",
            }
            if hasattr(player, "add_equipment"):
                player.add_equipment(sturdy_gear)
            elif hasattr(player, "equipment_bag"):
                if all(g["name"] != sturdy_gear["name"] for g in player.equipment_bag):
                    player.equipment_bag.append(sturdy_gear)
            dialogue_box.start_dialogue([
                "* VENDEDOR DEL DARK WORLD: '¡Bienvenido a mi bazar abismal, viajero de la Luz!'",
                "* 'Tengo una reliquia única para ti: [Sturdy Arm].'",
                "* Descripción: '¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.'",
                "* ¡Obtuviste [Sturdy Arm]! Puedes equiparlo desde [C] -> EQUIP en la ranura que prefieras.",
            ])
        else:
            sound_fx.play_select()
            dialogue_box.start_dialogue([
                "* VENDEDOR DEL DARK WORLD: 'Ese [Sturdy Arm] es una reliquia única.'",
                "* '¿Es tecnología cibernética o hechicería oscura? ¡Nadie en el Dark World lo sabe!'",
                "* (Puedes equiparlo o revisar su descripción en [C] -> EQUIP).",
            ])


