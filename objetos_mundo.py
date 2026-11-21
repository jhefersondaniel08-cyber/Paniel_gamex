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
    """Pilar de ruinas con musgo."""
    def __init__(self, x, y):
        super().__init__(x, y, depth_y=y + 38)
        self.solid_rect = pygame.Rect(x + 4, y + 26, 16, 14)

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Sombra
        pygame.draw.ellipse(surface, (15, 20, 25, 90), (cx + 2, cy + 34, 20, 8))
        # Base y cuerpo
        pygame.draw.rect(surface, (120, 125, 135), (cx + 4, cy + 6, 16, 32), border_radius=2)
        # Capitel y base
        pygame.draw.rect(surface, (145, 150, 160), (cx + 2, cy + 4, 20, 6), border_radius=1)
        pygame.draw.rect(surface, (145, 150, 160), (cx + 2, cy + 32, 20, 6), border_radius=1)
        # Grietas y musgo
        pygame.draw.rect(surf:=surface, (70, 130, 75), (cx + 6, cy + 16, 5, 8))
        pygame.draw.line(surface, (80, 85, 95), (cx + 14, cy + 10), (cx + 12, cy + 24), 1)



# ==========================================================
# ==========================================================
# OBJETOS AMBIENTALES DEL CEMENTERIO (Árboles góticos y Ánimas)
# ==========================================================
class WillOWisp(WorldObject):
    """Fuego fatuo / ánima etérea que flota suavemente por el cementerio."""
    def __init__(self, x, y, color=(130, 235, 255)):
        super().__init__(x, y, depth_y=y + 12)
        self.base_x = x
        self.base_y = y
        self.color = color
        self.time = random.uniform(0, 10)
        self.drift_speed = random.uniform(0.7, 1.3)
        self.orbit_rx = random.uniform(14, 28)
        self.orbit_ry = random.uniform(7, 14)
        self.particles = []

    def update(self, dt):
        self.time += dt * self.drift_speed
        self.x = self.base_x + math.sin(self.time) * self.orbit_rx
        self.y = self.base_y + math.cos(self.time * 1.3) * self.orbit_ry
        self.depth_y = self.y + 12

        if random.random() < 0.28:
            self.particles.append({
                "x": self.x,
                "y": self.y,
                "life": 0.55,
                "max_life": 0.55,
                "radius": random.uniform(1.0, 2.0)
            })

        for p in self.particles:
            p["life"] -= dt
            p["y"] += dt * 3
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        for p in self.particles:
            px, py = camera.apply((p["x"], p["y"]))
            alpha = int(180 * (p["life"] / p["max_life"]))
            ps = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*self.color, max(0, min(255, alpha))), (2, 2), int(p["radius"]))
            surface.blit(ps, (px - 2, py - 2))

        aura = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(aura, (*self.color, 40), (11, 11), 11)
        pygame.draw.circle(aura, (*self.color, 95), (11, 11), 6)
        pygame.draw.circle(aura, (255, 255, 255, 230), (11, 11), 2)
        surface.blit(aura, (cx - 11, cy - 11))


class TwistedTreeProp(WorldObject):
    """Árbol gótico retorcido con ramas desnudas, musgo colgante y linterna opcional."""
    def __init__(self, x, y, has_lantern=True):
        super().__init__(x, y, depth_y=y + 60)
        self.w = 56
        self.h = 68
        self.solid_rect = pygame.Rect(x + 18, y + 46, 20, 14)
        self.has_lantern = has_lantern
        self.flicker = random.uniform(0, 10)

    def update(self, dt):
        self.flicker += dt * 6

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        # Sombra suave bajo el árbol
        pygame.draw.ellipse(surface, (10, 12, 14, 110), (cx + 8, cy + 50, 40, 14))

        # Tronco retorcido de roble/sauce oscuro
        trunk = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        t_col = (40, 32, 36)
        t_light = (60, 50, 54)
        # Raíces
        pygame.draw.polygon(trunk, t_col, [(14, 58), (22, 42), (32, 42), (42, 58)])
        pygame.draw.polygon(trunk, t_col, [(20, 48), (25, 28), (34, 28), (38, 48)])
        pygame.draw.polygon(trunk, t_light, [(23, 44), (26, 30), (28, 30), (25, 44)])

        # Ramas góticas retorcidas
        pygame.draw.line(trunk, t_col, (26, 30), (10, 14), 4)
        pygame.draw.line(trunk, t_col, (10, 14), (2, 8), 2)
        pygame.draw.line(trunk, t_col, (10, 14), (16, 4), 2)

        pygame.draw.line(trunk, t_col, (30, 30), (46, 16), 4)
        pygame.draw.line(trunk, t_col, (46, 16), (54, 10), 2)
        pygame.draw.line(trunk, t_col, (46, 16), (40, 4), 2)

        pygame.draw.line(trunk, t_col, (28, 28), (27, 8), 3)
        pygame.draw.line(trunk, t_col, (27, 8), (22, 2), 2)
        pygame.draw.line(trunk, t_col, (27, 8), (33, 2), 2)

        # Musgo español colgante
        for mx, my in [(12, 18), (14, 24), (42, 20), (44, 26), (26, 12)]:
            pygame.draw.line(trunk, (45, 68, 48, 180), (mx, my), (mx, my + 6), 1)

        surface.blit(trunk, (cx, cy))

        # Farol de hierro forjado colgante con vela titilante
        if self.has_lantern:
            lx = cx + 46
            ly = cy + 22
            # Cadena de suspensión
            pygame.draw.line(surface, (65, 62, 70), (lx + 3, cy + 16), (lx + 3, ly), 1)
            # Farol
            pygame.draw.rect(surface, (42, 38, 45), (lx, ly, 7, 9), border_radius=1)
            flicker_a = int(180 + math.sin(self.flicker) * 45)
            pygame.draw.rect(surface, (255, 210, 80), (lx + 1, ly + 2, 5, 5))
            # Resplandor cálido
            glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 195, 60, max(0, min(255, flicker_a // 4))), (15, 15), 15)
            pygame.draw.circle(glow, (255, 230, 120, max(0, min(255, flicker_a // 2))), (15, 15), 7)
            surface.blit(glow, (lx - 11, ly - 10))


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
            sturdy_item = {
                "name": "Sturdy Arm",
                "heal": 0,
                "sanity_heal": 0,
                "atk_bonus": 5,
                "def_bonus": 10,
                "desc": "¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.",
            }
            player.inventory.append(sturdy_item)
            if not getattr(player, "sturdy_arm_equipped", False):
                player.sturdy_arm_equipped = True
                player.attack += 5
                player.defense += 10
                player.weapon = "Sturdy Arm"
                player.armor = "Sturdy Arm (+10 DEF)"
            dialogue_box.start_dialogue([
                "* VENDEDOR DEL DARK WORLD: '¡Bienvenido a mi bazar abismal, viajero de la Luz!'",
                "* 'Tengo una reliquia única para ti: [Sturdy Arm].'",
                "* Descripción: '¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.'",
                f"* ¡Obtuviste y equipaste [Sturdy Arm]! (+5 ATK y +10 DEF -> ATK {player.effective_attack}, DEF {player.effective_defense})",
            ])
        else:
            sound_fx.play_select()
            dialogue_box.start_dialogue([
                "* VENDEDOR DEL DARK WORLD: 'Ese [Sturdy Arm] te sienta de maravilla.'",
                "* '¿Es tecnología cibernética o hechicería oscura? ¡Nadie en el Dark World lo sabe!'",
                "* (Puedes ver su descripción en el menú [C] -> ITEM -> Sturdy Arm -> INFO).",
            ])


