import math
import random
import pygame
from configuracion import VIRTUAL_WIDTH, VIRTUAL_HEIGHT

# ==========================================================
# CÁMARA DINÁMICA (Enfoque y seguimiento estilo Deltarune)
# ==========================================================
class Camera:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = 0.0
        self.y = 0.0

    def snap(self, target_x, target_y, map_w, map_h):
        if map_w <= self.screen_w:
            self.x = (map_w - self.screen_w) / 2.0
        else:
            self.x = max(0.0, min(float(map_w - self.screen_w), target_x - self.screen_w / 2.0))

        if map_h <= self.screen_h:
            self.y = (map_h - self.screen_h) / 2.0
        else:
            self.y = max(0.0, min(float(map_h - self.screen_h), target_y - self.screen_h / 2.0))

    def update(self, target_x, target_y, map_w, map_h):
        # Si el mapa es menor o igual a la pantalla (interiores), centrar
        if map_w <= self.screen_w:
            self.x = (map_w - self.screen_w) / 2.0
        else:
            desired_x = target_x - self.screen_w / 2.0
            self.x += (desired_x - self.x) * 0.12
            max_x = max(0, map_w - self.screen_w)
            self.x = max(0.0, min(float(max_x), self.x))

        if map_h <= self.screen_h:
            self.y = (map_h - self.screen_h) / 2.0
        else:
            desired_y = target_y - self.screen_h / 2.0
            self.y += (desired_y - self.y) * 0.12
            max_y = max(0, map_h - self.screen_h)
            self.y = max(0.0, min(float(max_y), self.y))

    def apply(self, rect_or_pos):
        if isinstance(rect_or_pos, (pygame.Rect,)):
            return pygame.Rect(
                int(rect_or_pos.x - self.x),
                int(rect_or_pos.y - self.y),
                rect_or_pos.width,
                rect_or_pos.height,
            )
        return int(rect_or_pos[0] - self.x), int(rect_or_pos[1] - self.y)



# ==========================================================
class SceneTransition:
    def __init__(self):
        self.state = "IDLE"  # IDLE, FADING_OUT, FADING_IN, DW_DIVE
        self.timer = 0.0
        self.duration = 0.22  # 220ms para transiciones normales
        self.dw_duration = 3.30  # 3.30s para la cinemática estilo Kris al caer al Dark World
        self.target_scene_id = None
        self.target_spawn = None
        self.banner_text = ""
        self.banner_timer = 0.0
        self.dw_switched = False
        self.dw_Phase_sfx = set()
        self.dw_streaks = []
        self.dw_sparks = []
        self.dw_afterimages = []

    def start(self, target_scene_id, target_spawn, banner_text=""):
        self.timer = 0.0
        self.target_scene_id = target_scene_id
        self.target_spawn = target_spawn
        self.banner_text = banner_text
        self.banner_timer = 2.4

        # Si el destino es el Dark World, activar la animación cinemática de caída y transformación estilo Kris (Deltarune)
        if target_scene_id == "dark_world":
            self.state = "DW_DIVE"
            self.dw_switched = False
            self.dw_Phase_sfx.clear()
            self.dw_afterimages.clear()
            self.dw_sparks.clear()
            self.dw_streaks = [
                {
                    "x": random.uniform(16, VIRTUAL_WIDTH - 16),
                    "y": random.uniform(0, VIRTUAL_HEIGHT),
                    "len": random.uniform(22, 64),
                    "spd": random.uniform(320, 620),
                    "w": random.choice([1, 2, 2, 3]),
                    "col": random.choice([
                        (75, 245, 255),
                        (255, 75, 215),
                        (135, 110, 255),
                        (255, 255, 255),
                    ]),
                }
                for _ in range(42)
            ]
        else:
            self.state = "FADING_OUT"

    def update(self, dt, on_switch_callback, sound_fx=None):
        if self.state == "IDLE":
            if self.banner_timer > 0:
                self.banner_timer -= dt
            return

        self.timer += dt

        if self.state == "DW_DIVE":
            # Avanzar líneas de velocidad vertical de la caída al Dark World
            for st in self.dw_streaks:
                st["y"] -= st["spd"] * dt
                if st["y"] + st["len"] < 0:
                    st["y"] = float(VIRTUAL_HEIGHT + random.uniform(4, 36))
                    st["x"] = random.uniform(16, VIRTUAL_WIDTH - 16)

            for sp in self.dw_sparks:
                sp["x"] += sp["vx"] * dt
                sp["y"] += sp["vy"] * dt
                sp["life"] -= dt
            self.dw_sparks = [sp for sp in self.dw_sparks if sp["life"] > 0]

            # Efectos de sonido sincronizados con las 4 fases de la caída estilo Kris
            if sound_fx is not None:
                if "pull" not in self.dw_Phase_sfx and self.timer >= 0.05:
                    self.dw_Phase_sfx.add("pull")
                    sound_fx.play_warning()
                if "spin1" not in self.dw_Phase_sfx and self.timer >= 0.65:
                    self.dw_Phase_sfx.add("spin1")
                    sound_fx.play_shatter()
                if "transform" not in self.dw_Phase_sfx and self.timer >= 1.95:
                    self.dw_Phase_sfx.add("transform")
                    sound_fx.play_save()
                    # Explosión de chispas prismáticas al transformarse en Paniel Dark World en el aire
                    for _ in range(32):
                        ang = random.uniform(0, math.pi * 2)
                        spd = random.uniform(55, 190)
                        self.dw_sparks.append({
                            "x": float(VIRTUAL_WIDTH // 2),
                            "y": float(VIRTUAL_HEIGHT // 2),
                            "vx": math.cos(ang) * spd,
                            "vy": math.sin(ang) * spd,
                            "life": random.uniform(0.35, 0.75),
                            "max_life": 0.75,
                            "col": random.choice([(80, 245, 255), (255, 85, 215), (255, 240, 95), (255, 255, 255)]),
                        })
                if "land" not in self.dw_Phase_sfx and self.timer >= 2.82:
                    self.dw_Phase_sfx.add("land")
                    sound_fx.play_parry()

            # En el pico del destello de transformación (t = 2.00s), cambiar el mapa al Dark World
            if not self.dw_switched and self.timer >= 2.00:
                self.dw_switched = True
                on_switch_callback(self.target_scene_id, self.target_spawn)

            if self.timer >= self.dw_duration:
                self.state = "IDLE"
                self.timer = 0.0
            return

        if self.state == "FADING_OUT":
            if self.timer >= self.duration:
                self.state = "FADING_IN"
                self.timer = 0.0
                on_switch_callback(self.target_scene_id, self.target_spawn)
        elif self.state == "FADING_IN":
            if self.timer >= self.duration:
                self.state = "IDLE"
                self.timer = 0.0

    def _draw_dark_world_dive(self, surface, font, player=None, camera=None):
        """Renderiza la secuencia cinemática de entrada al Dark World inspirada en Kris (Deltarune):
        1) 0.00s - 0.55s: El suelo desaparece en un abismo negro mientras Paniel salta y empieza a caer.
        2) 0.55s - 1.95s: Caída libre a toda velocidad girando con estelas fantasma cian/magenta y anillos de energía.
        3) 1.95s - 2.55s: Destello estelar en el aire donde el atuendo de Paniel cambia a su forma de Dark World.
        4) 2.55s - 3.30s: Descenso meteórico al suelo del Dark World con onda de choque neón al aterrizar.
        """
        t = self.timer
        cx, cy = VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2

        # Obtener sprites de Paniel (Normal vs Dark World)
        light_dirs = None
        dw_dirs = None
        if player is not None:
            st = getattr(player, "mental_state", "FELIZ")
            light_dirs = player.state_sprites.get(st, getattr(player, "_default_sprites", {}))
            dw_dirs = player.state_sprites.get("DARK_WORLD", light_dirs)

        dirs_order = ["DOWN", "LEFT", "UP", "RIGHT"]

        # FASE 1 y 2 y 3 (0.0s .. 2.55s): Vórtice de caída libre en la Fuente Oscura
        if t < 2.55:
            # Fondo de abismo oscuro
            bg_alpha = 255 if t >= 0.35 else int(255 * (t / 0.35))
            abyss = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            abyss.fill((6, 3, 18, bg_alpha))
            surface.blit(abyss, (0, 0))

            # Columna central de la Fuente Oscura y líneas de velocidad ascendentes
            if t >= 0.25:
                fountain_w = int(64 + 28 * math.sin(t * 7.0))
                f_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(f_surf, (38, 18, 86, 95), (cx - fountain_w, 0, fountain_w * 2, VIRTUAL_HEIGHT))
                pygame.draw.rect(f_surf, (65, 195, 255, 65), (cx - fountain_w // 2, 0, fountain_w, VIRTUAL_HEIGHT))
                for st_line in self.dw_streaks:
                    pygame.draw.line(
                        f_surf,
                        st_line["col"],
                        (int(st_line["x"]), int(st_line["y"])),
                        (int(st_line["x"]), int(st_line["y"] + st_line["len"])),
                        st_line["w"],
                    )
                surface.blit(f_surf, (0, 0))

            # Posición y rotación de Paniel cayendo
            if t < 0.55:
                # Salto inicial hacia el abismo
                p_prog = t / 0.55
                py_draw = int(cy - math.sin(p_prog * math.pi) * 26)
                dir_key = "UP" if p_prog < 0.5 else "DOWN"
                use_dw = False
            elif t < 1.95:
                # Giro rápido durante la caída libre con oscilación
                spin_idx = int((t - 0.55) * 12.0) % 4
                dir_key = dirs_order[spin_idx]
                py_draw = cy + int(math.sin(t * 14.0) * 6)
                use_dw = False
            else:
                # Pose heroica frontal tras el destello de transformación en Paniel Dark World
                dir_key = "DOWN"
                py_draw = cy - int(math.sin((t - 1.95) * 8.0) * 8)
                use_dw = True

            px_draw = cx + int(math.sin(t * 10.0) * (4 if t < 1.95 else 1))

            # Anillos mágicos convergiendo hacia Paniel antes de la transformación
            if 0.65 <= t < 2.15:
                for ring_i in range(3):
                    r_prog = ((t * 2.2 + ring_i * 0.33) % 1.0)
                    rad = int(78 * (1.0 - r_prog)) + 8
                    r_col = (80, 245, 255) if ring_i % 2 == 0 else (255, 80, 215)
                    pygame.draw.circle(surface, r_col, (px_draw, py_draw), rad, 1)

            # Dibujar estelas fantasma (afterimages estilo Deltarune) y el sprite de Paniel
            active_dict = dw_dirs if use_dw else light_dirs
            if active_dict and active_dict.get(dir_key):
                spr = active_dict[dir_key][0]
                sw, sh = spr.get_size()

                # Estelas cian y magenta que quedan arriba mientras Paniel cae
                for ghost_i in range(3, 0, -1):
                    gy_off = ghost_i * 14
                    gx_off = int(math.sin(t * 12.0 - ghost_i) * 5)
                    ghost = spr.copy()
                    tint = (75, 245, 255, 110) if ghost_i % 2 == 1 else (255, 75, 215, 110)
                    ghost.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)
                    surface.blit(ghost, (px_draw - sw // 2 + gx_off, py_draw - sh // 2 - gy_off))

                # Aura brillante alrededor de Paniel al transformarse en su diseño Dark World
                if use_dw:
                    aura = pygame.Surface((56, 68), pygame.SRCALPHA)
                    pygame.draw.ellipse(aura, (80, 245, 255, 110), (4, 4, 48, 60))
                    pygame.draw.ellipse(aura, (255, 85, 215, 180), (4, 4, 48, 60), 2)
                    surface.blit(aura, (px_draw - 28, py_draw - 34))

                surface.blit(spr, (px_draw - sw // 2, py_draw - sh // 2))

            # Chispas de transformación
            for sp in self.dw_sparks:
                pygame.draw.circle(surface, sp["col"], (int(sp["x"]), int(sp["y"])), 3)

            # Destello blanco/cian en el momento exacto del cambio de traje (1.90s .. 2.25s)
            if 1.88 <= t <= 2.28:
                flash_p = 1.0 - min(1.0, abs(t - 2.02) / 0.22)
                f_alpha = int(245 * flash_p)
                flash_s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
                flash_s.fill((220, 250, 255, f_alpha))
                surface.blit(flash_s, (0, 0))

        # FASE 4 (2.55s .. 3.30s): Aterrizaje meteórico en el suelo del Dark World con onda de choque
        else:
            land_p = (t - 2.55) / (self.dw_duration - 2.55)
            if player is not None and camera is not None:
                scx, scy = camera.apply((player.x + player.w / 2, player.y + player.h - 6))
            else:
                scx, scy = cx, cy + 40

            # Rayo de caída vertical desde el cielo hasta el punto de aterrizaje de Paniel
            if land_p < 0.45:
                beam_p = land_p / 0.45
                beam_w = max(2, int(26 * (1.0 - beam_p * 0.5)))
                beam_s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(beam_s, (80, 245, 255, 175), (scx - beam_w // 2, 0, beam_w, scy))
                pygame.draw.rect(beam_s, (255, 255, 255, 230), (scx - max(1, beam_w // 4), 0, max(2, beam_w // 2), scy))
                surface.blit(beam_s, (0, 0))
            else:
                # Onda de choque expansiva neón al tocar el suelo del Dark World
                ring_p = (land_p - 0.45) / 0.55
                rx = int(12 + ring_p * 75)
                ry = int(5 + ring_p * 32)
                r_alpha = int(240 * (1.0 - ring_p))
                ring_s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
                pygame.draw.ellipse(ring_s, (80, 245, 255, r_alpha), (scx - rx, scy - ry, rx * 2, ry * 2), 3)
                pygame.draw.ellipse(ring_s, (255, 80, 215, r_alpha), (scx - int(rx * 0.7), scy - int(ry * 0.7), int(rx * 1.4), int(ry * 1.4)), 2)
                surface.blit(ring_s, (0, 0))

    def draw(self, surface, font, player=None, camera=None):
        if self.state == "DW_DIVE":
            self._draw_dark_world_dive(surface, font, player=player, camera=camera)
            return

        # Fundido a negro normal
        if self.state != "IDLE":
            if self.state == "FADING_OUT":
                alpha = int(255 * min(1.0, self.timer / self.duration))
            else:
                alpha = int(255 * max(0.0, 1.0 - (self.timer / self.duration)))
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            surface.blit(overlay, (0, 0))

        # Cartel de título superior flotante
        if self.banner_timer > 0 and self.banner_text and self.state != "FADING_OUT":
            b_alpha = min(255, int(255 * (self.banner_timer / 0.4))) if self.banner_timer < 0.4 else 255
            txt = font.render(f"✦ {self.banner_text} ✦", False, (255, 240, 100))
            tw = txt.get_width()
            th = txt.get_height()
            bx = VIRTUAL_WIDTH // 2 - tw // 2 - 10
            by = 12

            bg = pygame.Surface((tw + 20, th + 8), pygame.SRCALPHA)
            bg.fill((10, 10, 15, int(b_alpha * 0.88)))
            pygame.draw.rect(bg, (255, 240, 100, b_alpha), (0, 0, tw + 20, th + 8), 1, border_radius=3)
            surface.blit(bg, (bx, by))
            surface.blit(txt, (bx + 10, by + 4))

