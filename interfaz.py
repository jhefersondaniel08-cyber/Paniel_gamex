import math
import random
import pygame
from configuracion import (
    VIRTUAL_WIDTH,
    VIRTUAL_HEIGHT,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_SOUL_RED,
    COLOR_TEXT,
)


class DialogueBox:
    def __init__(self, font, sound_fx):
        self.font = font
        self.sound_fx = sound_fx
        self.active = False
        self.lines = []
        self.current_line_idx = 0
        self.displayed_text = ""
        self.char_idx = 0
        self.char_timer = 0.0
        self.char_delay = 0.022  # Velocidad de tipeo
        self.anim_time = 0.0
        self.box_rect = pygame.Rect(14, VIRTUAL_HEIGHT - 86, VIRTUAL_WIDTH - 28, 76)

    def start_dialogue(self, lines):
        self.lines = lines
        self.current_line_idx = 0
        self.displayed_text = ""
        self.char_idx = 0
        self.char_timer = 0.0
        self.active = True

    def wrap_text(self, text, max_width):
        """Envuelve texto respetando saltos de línea para que ninguna palabra salga de la caja."""
        wrapped = []
        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            curr_line = ""
            for word in words:
                test_line = (curr_line + " " + word).strip()
                if self.font.size(test_line)[0] <= max_width:
                    curr_line = test_line
                else:
                    if curr_line:
                        wrapped.append(curr_line)
                    curr_line = word
            if curr_line:
                wrapped.append(curr_line)
        return wrapped

    def update(self, dt):
        self.anim_time += dt
        if not self.active:
            return

        target_line = self.lines[self.current_line_idx]
        if self.char_idx < len(target_line):
            self.char_timer += dt
            if self.char_timer >= self.char_delay:
                self.char_timer = 0.0
                next_char = target_line[self.char_idx]
                self.displayed_text += next_char
                self.char_idx += 1
                if next_char not in [" ", "\n", "*"]:
                    self.sound_fx.play_blip()

    def handle_input(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE, pygame.K_x]:
                target_line = self.lines[self.current_line_idx]
                # Si aún está escribiendo, autocompletar la línea inmediatamente
                if self.char_idx < len(target_line):
                    self.displayed_text = target_line
                    self.char_idx = len(target_line)
                    return True
                else:
                    # Pasar a la siguiente línea de diálogo
                    self.current_line_idx += 1
                    if self.current_line_idx < len(self.lines):
                        self.displayed_text = ""
                        self.char_idx = 0
                        self.char_timer = 0.0
                    else:
                        # Diálogo concluido
                        self.active = False
                    return True
        return False

    def draw(self, surface, player=None):
        if not self.active:
            return

        # Fondo negro de la caja con doble marco estilo Deltarune
        pygame.draw.rect(surface, COLOR_BLACK, self.box_rect)
        pygame.draw.rect(surface, (110, 65, 210), self.box_rect.inflate(2, 2), 1)
        pygame.draw.rect(surface, COLOR_WHITE, self.box_rect, 2)
        inner = self.box_rect.inflate(-6, -6)
        pygame.draw.rect(surface, (55, 45, 90), inner, 1)

        prev_clip = surface.get_clip()
        surface.set_clip(inner)

        # Si hay retrato de Paniel disponible, mostrarlo ajustado y apoyado en la base del marco
        portrait = player.get_stat_portrait() if (player is not None and hasattr(player, "get_stat_portrait")) else None
        if portrait is not None:
            p_box = pygame.Rect(self.box_rect.x + 10, self.box_rect.y + 10, 34, 34)
            pygame.draw.rect(surface, (18, 20, 32), p_box, border_radius=2)
            surface.blit(portrait, (p_box.x + 1, p_box.y + 1))
            pygame.draw.rect(surface, (120, 100, 190), p_box, 1, border_radius=2)
            text_x = self.box_rect.x + 52
            max_width = self.box_rect.width - 66
        else:
            self._draw_soul(surface, self.box_rect.x + 12, self.box_rect.y + 12)
            text_x = self.box_rect.x + 28
            max_width = self.box_rect.width - 42

        lines = self.wrap_text(self.displayed_text, max_width=max_width)
        ty = self.box_rect.y + 10
        for line in lines[:4]:
            txt_s = self.font.render(line, False, COLOR_TEXT)
            surface.blit(txt_s, (text_x, ty))
            ty += 14

        # Indicador parpadeante [Z] ▼ cuando termina de escribirse la línea
        target_line = self.lines[self.current_line_idx] if self.lines else ""
        if self.char_idx >= len(target_line) and int(self.anim_time * 4) % 2 == 0:
            prompt_s = self.font.render("[Z] ▼", False, (255, 235, 80))
            surface.blit(prompt_s, (self.box_rect.right - prompt_s.get_width() - 10, self.box_rect.bottom - 16))

        surface.set_clip(prev_clip)

    def _draw_soul(self, surface, x, y):
        """Dibuja el corazón pixelado de Undertale/Deltarune (11x10, proporción clásica no alargada)."""
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 1, y, 3, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 7, y, 3, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x, y + 1, 5, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 6, y + 1, 5, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x, y + 2, 11, 3))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 1, y + 5, 9, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 2, y + 6, 7, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 3, y + 7, 5, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 4, y + 8, 3, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 5, y + 9, 1, 1))



# ==========================================================
# HUD DE SALUD MENTAL DE PANIEL (Medidor de Locura)
# ==========================================================
class PanielMentalHUD:
    """Renderiza el rostro de Paniel con expresiones dinámicas según su estado mental
    (FELIZ, TRISTE, TRAUMADO, LOCO), su medidor de cordura, contador de muertes y estadísticas."""

    STATE_COLORS = {
        "FELIZ":    (110, 240, 140),
        "TRISTE":   (95, 160, 245),
        "TRAUMADO": (195, 105, 230),
        "LOCO":     (255, 60, 60),
    }

    STATE_TITLES = {
        "FELIZ":    "FELIZ",
        "TRISTE":   "TRISTE",
        "TRAUMADO": "TRAUMADO",
        "LOCO":     "¡¡LOCO!!",
    }

    STAT_BADGES = {
        "FELIZ":    "ATK 10  DEF 2",
        "TRISTE":   "ATK -3  DEF +2",
        "TRAUMADO": "ATK -2  DEF -3",
        "LOCO":     "ATK +8  DEF -4",
    }

    def __init__(self, font, font_small=None):
        self.font = font
        self.font_small = font_small or font
        self.anim_time = 0.0
        self._cache = {}

    def update(self, dt):
        self.anim_time += dt

    def _generate_face(self, state, t):
        """Genera el rostro pixel art 32x32 de Paniel mostrando su nivel progresivo de locura."""
        # Frame de animación para ojos y gestos
        anim_step = int(t * 7) % 6
        key = (state, anim_step)
        if key in self._cache:
            return self._cache[key]

        surf = pygame.Surface((32, 32), pygame.SRCALPHA)

        # Color base de piel que se vuelve más pálida / demacrada con la locura
        skin_color = {
            "FELIZ":    (255, 218, 175),
            "TRISTE":   (210, 205, 225),
            "TRAUMADO": (185, 180, 210),
            "LOCO":     (255, 190, 160),
        }.get(state, (255, 218, 175))

        # Cabeza redonda
        pygame.draw.circle(surf, skin_color, (16, 16), 13)

        # Cabello castaño oscuro característico
        hair_color = (75, 48, 35) if state != "LOCO" else (95, 40, 30)
        pygame.draw.arc(surf, hair_color, (3, 3, 26, 18), 0, math.pi, 5)
        pygame.draw.rect(surf, hair_color, (4, 7, 24, 7), border_radius=2)
        # Mechones
        pygame.draw.line(surf, hair_color, (8, 12), (10, 16), 2)
        pygame.draw.line(surf, hair_color, (22, 12), (24, 16), 2)

        if state == "FELIZ":
            # Ojos amigables y tranquilos
            pygame.draw.circle(surf, (40, 40, 60), (11, 14), 2)
            pygame.draw.circle(surf, (40, 40, 60), (21, 14), 2)
            pygame.draw.rect(surf, (255, 255, 255), (11, 13, 1, 1))
            pygame.draw.rect(surf, (255, 255, 255), (21, 13, 1, 1))
            # Sonrisa cálida
            pygame.draw.arc(surf, (160, 75, 60), (10, 16, 12, 7), math.pi, 2 * math.pi, 2)
            # Mejillas sonrosadas
            pygame.draw.circle(surf, (255, 150, 150), (9, 18), 2)
            pygame.draw.circle(surf, (255, 150, 150), (23, 18), 2)

        elif state == "TRISTE":
            # Ojos caídos con mirada baja
            pygame.draw.line(surf, (50, 50, 80), (9, 15), (13, 16), 2)
            pygame.draw.line(surf, (50, 50, 80), (19, 16), (23, 15), 2)
            # Cejas caídas
            pygame.draw.line(surf, (70, 60, 80), (8, 12), (13, 14), 1)
            pygame.draw.line(surf, (70, 60, 80), (19, 14), (24, 12), 1)
            # Boca curvada hacia abajo
            pygame.draw.arc(surf, (110, 75, 75), (10, 20, 12, 6), 0, math.pi, 2)
            # Lágrima rodando por la mejilla
            tear_y = 17 + (anim_step % 5)
            pygame.draw.circle(surf, (110, 170, 255), (10, tear_y), 2)

        elif state == "TRAUMADO":
            # Ojos desmesuradamente abiertos de espanto
            pygame.draw.circle(surf, (245, 245, 255), (11, 14), 4)
            pygame.draw.circle(surf, (245, 245, 255), (21, 14), 4)
            # Pupilas minúsculas temblando de horror
            pupil_jitter = (anim_step % 2)
            pygame.draw.circle(surf, (25, 20, 35), (11 + pupil_jitter, 14), 1)
            pygame.draw.circle(surf, (25, 20, 35), (21 - pupil_jitter, 14), 1)
            # Ojeras violáceas
            pygame.draw.arc(surf, (110, 80, 150), (7, 16, 8, 4), math.pi, 2 * math.pi, 1)
            pygame.draw.arc(surf, (110, 80, 150), (17, 16, 8, 4), math.pi, 2 * math.pi, 1)
            # Boca temblorosa en zigzag
            pygame.draw.line(surf, (120, 70, 70), (11, 22), (13, 20), 1)
            pygame.draw.line(surf, (120, 70, 70), (13, 20), (16, 22), 1)
            pygame.draw.line(surf, (120, 70, 70), (16, 22), (19, 20), 1)
            pygame.draw.line(surf, (120, 70, 70), (19, 20), (21, 22), 1)
            # Gota de sudor frío cayendo
            pygame.draw.ellipse(surf, (140, 200, 255), (23, 8 + (anim_step % 4), 3, 4))

        elif state == "LOCO":
            # Sacudida espasmódica de la cabeza
            shake_x = int(math.sin(t * 26.0) * 1.5)
            # Ojos inyectados en sangre
            pygame.draw.circle(surf, (255, 240, 240), (11 + shake_x, 13), 5)
            pygame.draw.circle(surf, (255, 240, 240), (21 - shake_x, 13), 5)
            # Venitas rojas
            pygame.draw.line(surf, (255, 50, 50), (8 + shake_x, 11), (11 + shake_x, 13), 1)
            pygame.draw.line(surf, (255, 50, 50), (24 - shake_x, 11), (21 - shake_x, 13), 1)
            # Iris rojos luminosos y desorbitados
            pygame.draw.circle(surf, (230, 20, 20), (11 + shake_x, 13), 3)
            pygame.draw.circle(surf, (230, 20, 20), (21 - shake_x, 13), 3)
            pygame.draw.circle(surf, (255, 240, 60), (11 + shake_x, 13), 1)
            pygame.draw.circle(surf, (255, 240, 60), (21 - shake_x, 13), 1)
            # Enorme y desquiciada sonrisa de oreja a oreja
            pygame.draw.arc(surf, (160, 30, 30), (7, 14, 18, 12), math.pi, 2 * math.pi, 3)
            # Dientes afilados y desordenados
            for di in range(5):
                pygame.draw.rect(surf, (255, 255, 240), (9 + di * 3, 19, 2, 4))
            # Vórtices / destellos de locura alrededor de la cabeza
            for vi in range(4):
                ang = t * 6.0 + vi * (math.pi / 2)
                vx = int(16 + math.cos(ang) * 15)
                vy = int(16 + math.sin(ang) * 15)
                if 0 <= vx < 32 and 0 <= vy < 32:
                    surf.set_at((vx, vy), (255, 60, 60, 200))

        self._cache[key] = surf
        return surf

    def get_face(self, state, t, player=None):
        """Obtiene el retrato desde Estadisticas.png del estado mental actual (o respaldo procedural)."""
        if player is not None and hasattr(player, "stat_portraits") and state in player.stat_portraits:
            portrait = player.stat_portraits[state]
            if portrait is not None:
                if state == "LOCO":
                    shake_x = int(math.sin(t * 26.0) * 1.5)
                    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                    surf.blit(portrait, (shake_x, 0))
                    return surf
                return portrait
        return self._generate_face(state, t)

    def draw(self, surface, player):
        """Renderiza el HUD de estado mental compacto en la esquina superior izquierda."""
        state = player.mental_state
        state_color = self.STATE_COLORS.get(state, (255, 255, 255))

        # Caja compacta en la esquina superior izquierda (ensanchada para evitar solapamientos)
        box_x = 10
        box_y = 10
        box_w = 158
        box_h = 58

        # Fondo translúcido oscuro estilizado
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((12, 14, 22, 225))
        surface.blit(bg, (box_x, box_y))

        # Marco con el color del estado mental
        border_width = 2 if state == "LOCO" else 1
        pygame.draw.rect(surface, state_color, (box_x, box_y, box_w, box_h), border_width, border_radius=3)

        # 1. Rostro de Paniel (32x32 ajustado al marco 34x34 y apoyado en la base sin flotar)
        face = self.get_face(state, self.anim_time, player=player)
        face_frame = pygame.Rect(box_x + 4, box_y + 4, 34, 34)
        pygame.draw.rect(surface, (40, 45, 60), face_frame, border_radius=2)
        surface.blit(face, (face_frame.x + 1, face_frame.y + 1))
        pygame.draw.rect(surface, state_color, face_frame, 1, border_radius=2)

        # 2. Etiqueta del estado (FELIZ, TRISTE, TRAUMADO, ¡¡LOCO!!)
        title_txt = self.STATE_TITLES.get(state, state)
        lbl_s = self.font.render(title_txt, False, state_color)
        surface.blit(lbl_s, (box_x + 44, box_y + 4))

        # 3. Barra de Cordura / Sanity
        bar_x = box_x + 44
        bar_y = box_y + 17
        bar_w = 56
        bar_h = 6
        ratio = max(0.0, min(1.0, player.sanity / 100.0))
        # Fondo barra
        pygame.draw.rect(surface, (35, 30, 42), (bar_x, bar_y, bar_w, bar_h), border_radius=1)
        if ratio > 0:
            fill_w = max(1, int(bar_w * ratio))
            pygame.draw.rect(surface, state_color, (bar_x, bar_y, fill_w, bar_h), border_radius=1)
        pygame.draw.rect(surface, (120, 120, 140), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=1)

        # Porcentaje de cordura
        pct_s = self.font_small.render(f"{int(player.sanity)}%", False, (220, 225, 235))
        surface.blit(pct_s, (bar_x + bar_w + 4, bar_y - 2))

        # 4. Estadísticas de ATK y DEF modificadas en tiempo real (con separación amplia)
        atk_col = (255, 230, 90) if state == "LOCO" else ((160, 210, 255) if state == "TRISTE" else (240, 240, 250))
        def_col = (120, 230, 160) if state == "TRISTE" else ((255, 120, 120) if state in ("LOCO", "TRAUMADO") else (240, 240, 250))

        atk_s = self.font.render(f"ATK {player.effective_attack}", False, atk_col)
        def_s = self.font.render(f"DEF {player.effective_defense}", False, def_col)
        surface.blit(atk_s, (box_x + 44, box_y + 27))
        surface.blit(def_s, (box_x + 100, box_y + 27))

        # 5. Fila inferior: Contador de Muertes y Efecto Anímico
        skull_color = (255, 80, 80) if player.death_count > 0 else (160, 160, 175)
        death_txt = f"Muertes: {player.death_count}"
        death_s = self.font_small.render(death_txt, False, skull_color)
        surface.blit(death_s, (box_x + 6, box_y + 42))

        stat_desc = {
            "FELIZ":    "Equilibrado",
            "TRISTE":   "-ATK/+DEF",
            "TRAUMADO": "En panico!",
            "LOCO":     "¡FURIA! (+8)",
        }.get(state, "")
        desc_s = self.font_small.render(stat_desc, False, state_color)
        surface.blit(desc_s, (box_x + 74, box_y + 42))


# ==========================================================
# HUD RETRO DINÁMICO (Con indicador de puertas y lugares)
# ==========================================================
class RetroHUD:
    def __init__(self, font, font_prompt):
        self.font = font
        self.font_prompt = font_prompt

    def draw(self, surface, player, is_running, area_name, door_prompt=None):
        bar_rect = pygame.Rect(10, VIRTUAL_HEIGHT - 24, VIRTUAL_WIDTH - 20, 20)

        # Fondo con marco elegante Undertale / Deltarune
        bg = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        bg.fill((10, 12, 18, 225))
        surface.blit(bg, bar_rect.topleft)
        pygame.draw.rect(surface, (85, 70, 145), bar_rect, 1, border_radius=3)

        prev_clip = surface.get_clip()
        surface.set_clip(bar_rect.inflate(-4, -2))

        # Nombre, Nivel LV y HP bien compactos a la izquierda para dejar espacio al nombre del lugar
        name_txt = self.font.render("PANIEL", False, (255, 255, 255))
        lv_txt = self.font.render(f"LV {player.lv}", False, (255, 220, 80))
        hp_label = self.font.render("HP", False, (255, 180, 0))
        hp_num = self.font.render(f"{player.hp}/{player.max_hp}", False, (255, 255, 255))

        surface.blit(name_txt, (bar_rect.x + 6, bar_rect.y + 4))
        surface.blit(lv_txt, (bar_rect.x + 56, bar_rect.y + 4))
        surface.blit(hp_label, (bar_rect.x + 96, bar_rect.y + 4))

        # Barra de HP (42px)
        max_bar_w = 42
        ratio = max(0.0, min(1.0, player.hp / max(1, player.max_hp)))
        curr_bar_w = int(max_bar_w * ratio)
        pygame.draw.rect(surface, (160, 20, 20), (bar_rect.x + 114, bar_rect.y + 5, max_bar_w, 9))
        if curr_bar_w > 0:
            pygame.draw.rect(surface, (100, 240, 95), (bar_rect.x + 114, bar_rect.y + 5, curr_bar_w, 9))
        pygame.draw.rect(surface, (220, 220, 235), (bar_rect.x + 114, bar_rect.y + 5, max_bar_w, 9), 1)
        surface.blit(hp_num, (bar_rect.x + 160, bar_rect.y + 4))

        # Lugar actual alineado a la derecha dentro de la caja (sin desbordar jamás)
        if is_running:
            run_lbl = self.font_prompt.render("»SPRINT«", False, (140, 240, 255))
            surface.blit(run_lbl, (bar_rect.x + 206, bar_rect.y + 5))

        loc_txt = self.font_prompt.render(area_name, False, (205, 225, 255))
        loc_x = max(bar_rect.x + 210, bar_rect.right - loc_txt.get_width() - 8)
        surface.blit(loc_txt, (loc_x, bar_rect.y + 5))

        surface.set_clip(prev_clip)

        # Cartel emergente interactivo cuando estás cerca de una puerta
        if door_prompt:
            p_txt = self.font_prompt.render(f"★ [Z / Enter / Caminar] Entrar a: {door_prompt}", False, (255, 255, 255))
            pw, ph = p_txt.get_width() + 16, p_txt.get_height() + 8
            px = VIRTUAL_WIDTH // 2 - pw // 2
            py = VIRTUAL_HEIGHT - 52
            p_bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
            p_bg.fill((20, 20, 30, 220))
            pygame.draw.rect(p_bg, (255, 230, 80), (0, 0, pw, ph), 1, border_radius=3)
            surface.blit(p_bg, (px, py))
            surface.blit(p_txt, (px + 8, py + 4))


# ==========================================================
# MENÚ OVERWORLD ESTILO UNDERTALE (Tecla [C])
# ==========================================================
class UndertaleMenu:
    """Menú pausado de exploración estilo Undertale.
    Permite ver Estadísticas completas, Inventario de Objetos,
    Estado Mental y Consciencia de Muertes."""

    def __init__(self, font_hud, font_small, font_dialogue, sound_fx):
        self.font_hud = font_hud
        self.font_small = font_small
        self.font_dialogue = font_dialogue
        self.sound_fx = sound_fx
        self.active = False

        self.main_options = ["ITEM", "STAT", "MENTE"]
        self.main_idx = 0
        self.state = "MAIN"  # MAIN, SUBMENU_ITEM, SUBMENU_ITEM_ACTION, ITEM_MESSAGE, SUBMENU_STAT, SUBMENU_MENTE

        self.item_idx = 0
        self.action_idx = 0  # 0: USAR, 1: INFO, 2: TIRAR
        self.action_options = ["USAR", "INFO", "TIRAR"]
        self.msg_lines = []
        self.anim_time = 0.0

    def open(self):
        self.active = True
        self.state = "MAIN"
        self.main_idx = 0
        self.item_idx = 0
        self.action_idx = 0
        self.msg_lines = []
        self.sound_fx.play_select()

    def close(self):
        self.active = False
        self.state = "MAIN"
        self.sound_fx.play_select()

    def update(self, dt):
        self.anim_time += dt

    def _draw_soul(self, surface, x, y):
        """Dibuja el corazón pixelado de Undertale/Deltarune (11x10, proporción clásica)."""
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 1, y, 3, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 7, y, 3, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x, y + 1, 5, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 6, y + 1, 5, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x, y + 2, 11, 3))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 1, y + 5, 9, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 2, y + 6, 7, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 3, y + 7, 5, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 4, y + 8, 3, 1))
        pygame.draw.rect(surface, COLOR_SOUL_RED, (x + 5, y + 9, 1, 1))

    def wrap_text(self, text, font, max_width):
        """Envuelve texto para garantizar que ninguna línea sobrepase los bordes del cuadro."""
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split(' ')
            curr = ''
            for w in words:
                test = (curr + ' ' + w).strip()
                if font.size(test)[0] <= max_width:
                    curr = test
                else:
                    if curr:
                        lines.append(curr)
                    curr = w
            if curr:
                lines.append(curr)
        return lines

    def handle_input(self, event, player, dialogue_box):
        if not self.active or event.type != pygame.KEYDOWN:
            return

        # 1. Menú Principal Izquierdo [ITEM, STAT, MENTE]
        if self.state == "MAIN":
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.main_idx = (self.main_idx - 1) % len(self.main_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.main_idx = (self.main_idx + 1) % len(self.main_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self.sound_fx.play_select()
                if self.main_idx == 0:
                    self.state = "SUBMENU_ITEM"
                    self.item_idx = 0
                elif self.main_idx == 1:
                    self.state = "SUBMENU_STAT"
                elif self.main_idx == 2:
                    self.state = "SUBMENU_MENTE"
            elif event.key in [pygame.K_x, pygame.K_c, pygame.K_ESCAPE]:
                self.close()

        # 2. Submenú STATS
        elif self.state == "SUBMENU_STAT":
            if event.key in [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self.sound_fx.play_select()

        # 3. Submenú OBJETOS (Lista)
        elif self.state == "SUBMENU_ITEM":
            if not player.inventory:
                if event.key in [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    self.state = "MAIN"
                    self.sound_fx.play_select()
                return

            if event.key in [pygame.K_UP, pygame.K_w]:
                self.item_idx = (self.item_idx - 1) % len(player.inventory)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.item_idx = (self.item_idx + 1) % len(player.inventory)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self.state = "SUBMENU_ITEM_ACTION"
                self.action_idx = 0
                self.sound_fx.play_select()
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self.sound_fx.play_select()

        # 4. Acción sobre el objeto [USAR, INFO, TIRAR]
        elif self.state == "SUBMENU_ITEM_ACTION":
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.action_idx = (self.action_idx - 1) % len(self.action_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.action_idx = (self.action_idx + 1) % len(self.action_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                if not player.inventory:
                    self.state = "SUBMENU_ITEM"
                    return

                item = player.inventory[self.item_idx]

                if self.action_idx == 0:  # USAR
                    player.inventory.pop(self.item_idx)
                    heal = item.get("heal", 0)
                    san_heal = item.get("sanity_heal", 0)
                    player.hp = min(player.max_hp, player.hp + heal)
                    if san_heal > 0:
                        player.modify_sanity(san_heal)
                    self.sound_fx.play_heal()
                    lines = [f"* Usaste {item['name']}."]
                    if heal > 0:
                        lines.append(f"* ¡Recuperaste {heal} HP! ({player.hp}/{player.max_hp})")
                    if san_heal > 0:
                        lines.append(f"* ¡Tu mente se siente más tranquila (+{san_heal}% cordura)!")
                    self.msg_lines = lines
                    self.state = "ITEM_MESSAGE"

                elif self.action_idx == 1:  # INFO
                    self.sound_fx.play_select()
                    desc = item.get("desc", "Sin descripción.")
                    self.msg_lines = [f"* {item['name']}:", f"* \"{desc}\""]
                    self.state = "ITEM_MESSAGE"

                elif self.action_idx == 2:  # TIRAR
                    dropped = player.inventory.pop(self.item_idx)
                    self.sound_fx.play_select()
                    self.msg_lines = [
                        f"* Dejaste caer {dropped['name']}.",
                        "* Se perdió silenciosamente entre la niebla del cementerio."
                    ]
                    self.state = "ITEM_MESSAGE"

            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "SUBMENU_ITEM"
                self.sound_fx.play_select()

        # 5. Mensaje emergente de objeto
        elif self.state == "ITEM_MESSAGE":
            if event.key in [pygame.K_z, pygame.K_x, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                if player.inventory:
                    self.item_idx = min(self.item_idx, len(player.inventory) - 1)
                else:
                    self.item_idx = 0
                self.state = "SUBMENU_ITEM"
                self.sound_fx.play_select()

        # 6. Submenú MENTE
        elif self.state == "SUBMENU_MENTE":
            if event.key in [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self.sound_fx.play_select()

    def draw(self, surface, player, mental_hud):
        if not self.active:
            return

        # Capa translúcida sutil para enfocar la vista en el menú
        dark_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 110))
        surface.blit(dark_overlay, (0, 0))

        # 1. Caja de Opciones Izquierda (ITEM, STAT, MENTE)
        box_menu = pygame.Rect(24, 45, 76, 82)
        pygame.draw.rect(surface, (0, 0, 0), box_menu)
        pygame.draw.rect(surface, (255, 255, 255), box_menu, 2)

        for i, opt in enumerate(self.main_options):
            txt = self.font_hud.render(opt, False, (255, 255, 255))
            surface.blit(txt, (box_menu.x + 24, box_menu.y + 12 + i * 22))

        # Alma indicadora en el menú principal
        if self.state == "MAIN":
            self._draw_soul(surface, box_menu.x + 8, box_menu.y + 13 + self.main_idx * 22)

        # 2. Caja Mini-Status Izquierda (debajo del menú)
        box_mini = pygame.Rect(24, 135, 76, 78)
        pygame.draw.rect(surface, (0, 0, 0), box_mini)
        pygame.draw.rect(surface, (255, 255, 255), box_mini, 2)

        name_s = self.font_hud.render("PANIEL", False, (255, 255, 255))
        lv_s = self.font_small.render(f"LV  {player.lv}", False, (255, 220, 80))
        hp_s = self.font_small.render(f"HP  {player.hp}/{player.max_hp}", False, (255, 255, 255))
        g_s = self.font_small.render(f"G   {player.gold}", False, (255, 230, 90))

        surface.blit(name_s, (box_mini.x + 8, box_mini.y + 8))
        surface.blit(lv_s, (box_mini.x + 8, box_mini.y + 24))
        surface.blit(hp_s, (box_mini.x + 8, box_mini.y + 40))
        surface.blit(g_s, (box_mini.x + 8, box_mini.y + 56))

        # 3. Ventana Derecha de Submenú (se abre al elegir STAT, ITEM o MENTE)
        if self.state != "MAIN":
            box_sub = pygame.Rect(106, 34, 280, 232)
            pygame.draw.rect(surface, (0, 0, 0), box_sub)
            pygame.draw.rect(surface, (255, 255, 255), box_sub, 2)

            # A) SUBMENÚ DE ESTADÍSTICAS (STAT)
            if self.state == "SUBMENU_STAT":
                title_s = self.font_hud.render('"PANIEL"', False, (255, 255, 255))
                surface.blit(title_s, (box_sub.x + 14, box_sub.y + 10))

                # Retrato de Estadisticas.png en la esquina superior derecha del panel STAT
                state = player.mental_state
                state_col = mental_hud.STATE_COLORS.get(state, (255, 255, 255))
                stat_face = mental_hud.get_face(state, self.anim_time, player=player)
                stat_frame = pygame.Rect(box_sub.right - 44, box_sub.y + 8, 34, 34)
                pygame.draw.rect(surface, (40, 45, 60), stat_frame, border_radius=2)
                surface.blit(stat_face, (stat_frame.x + 1, stat_frame.y + 1))
                pygame.draw.rect(surface, state_col, stat_frame, 1, border_radius=2)

                lv_txt = self.font_hud.render(f"LV  {player.lv}", False, (255, 220, 80))
                hp_txt = self.font_hud.render(f"HP  {player.hp} / {player.max_hp}", False, (255, 255, 255))
                surface.blit(lv_txt, (box_sub.x + 14, box_sub.y + 26))
                surface.blit(hp_txt, (box_sub.x + 75, box_sub.y + 26))

                # ATK y DEF con base y modificador emocional
                atk_base = player.attack
                atk_eff = player.effective_attack
                atk_diff = atk_eff - atk_base
                atk_str = f"ATK {atk_eff} ({atk_base})" if atk_diff == 0 else f"ATK {atk_eff} ({atk_base}{atk_diff:+d})"

                def_base = player.defense
                def_eff = player.effective_defense
                def_diff = def_eff - def_base
                def_str = f"DEF {def_eff} ({def_base})" if def_diff == 0 else f"DEF {def_eff} ({def_base}{def_diff:+d})"

                next_exp = player.exp_for_next_level() - player.exp if player.lv < player.max_lv else 0
                next_str = str(next_exp) if player.lv < player.max_lv else "MAX"

                atk_s = self.font_dialogue.render(atk_str, False, (240, 240, 250))
                exp_s = self.font_dialogue.render(f"EXP:  {player.exp}", False, (240, 240, 250))
                def_s = self.font_dialogue.render(def_str, False, (240, 240, 250))
                next_s = self.font_dialogue.render(f"NEXT: {next_str}", False, (240, 240, 250))

                surface.blit(atk_s, (box_sub.x + 14, box_sub.y + 42))
                surface.blit(exp_s, (box_sub.x + 155, box_sub.y + 42))
                surface.blit(def_s, (box_sub.x + 14, box_sub.y + 57))
                surface.blit(next_s, (box_sub.x + 155, box_sub.y + 57))

                # Equipamiento
                wep_s = self.font_dialogue.render(f"ARMA:   {player.weapon}", False, (200, 225, 255))
                arm_s = self.font_dialogue.render(f"ARMADURA:{player.armor}", False, (200, 225, 255))
                gold_s = self.font_dialogue.render(f"ORO:    {player.gold}", False, (255, 235, 120))
                surface.blit(wep_s, (box_sub.x + 14, box_sub.y + 73))
                surface.blit(arm_s, (box_sub.x + 14, box_sub.y + 88))
                surface.blit(gold_s, (box_sub.x + 14, box_sub.y + 103))

                # Línea divisoria
                pygame.draw.line(surface, (80, 85, 105), (box_sub.x + 10, box_sub.y + 118), (box_sub.right - 10, box_sub.y + 118), 1)

                # SECCIÓN ESTADO MENTAL Y LOCURA
                state = player.mental_state
                state_col = mental_hud.STATE_COLORS.get(state, (255, 255, 255))
                m_hdr = self.font_hud.render("[ESTADO MENTAL Y CORDURA]", False, state_col)
                surface.blit(m_hdr, (box_sub.x + 14, box_sub.y + 122))

                st_s = self.font_small.render(f"Estado: {state} ({int(player.sanity)}%)", False, state_col)
                surface.blit(st_s, (box_sub.x + 14, box_sub.y + 136))

                # Mini barra de cordura
                bar_x = box_sub.x + 160
                bar_y = box_sub.y + 138
                bar_w = 85
                bar_h = 6
                ratio = max(0.0, min(1.0, player.sanity / 100.0))
                pygame.draw.rect(surface, (35, 30, 42), (bar_x, bar_y, bar_w, bar_h))
                if ratio > 0:
                    pygame.draw.rect(surface, state_col, (bar_x, bar_y, int(bar_w * ratio), bar_h))
                pygame.draw.rect(surface, (120, 125, 140), (bar_x, bar_y, bar_w, bar_h), 1)

                stat_desc = {
                    "FELIZ":    "Equilibrado (Sin penalizadores ni bonos)",
                    "TRISTE":   "Desanimado (ATK -3, DEF +2, Vel. reducida)",
                    "TRAUMADO": "En panico (ATK -2, DEF -3)",
                    "LOCO":     "¡¡FURIA TOTAL!! (ATK +8, DEF -4)",
                }.get(state, "")
                desc_s = self.font_small.render(stat_desc, False, (215, 220, 235))
                surface.blit(desc_s, (box_sub.x + 14, box_sub.y + 150))

                # SECCIÓN CONSCIENCIA DE MUERTES
                dc = player.death_count
                d_color = (255, 70, 70) if dc > 0 else (160, 165, 180)
                d_hdr = self.font_hud.render(f"[MUERTES RECORDADAS: {dc}]", False, d_color)
                surface.blit(d_hdr, (box_sub.x + 14, box_sub.y + 166))

                if dc == 0:
                    quote = "* Paniel aun no ha sentido el frio del mas alla."
                elif dc == 1:
                    quote = "* Paniel recuerda con escalofrios su primera caida."
                elif dc <= 5:
                    quote = f"* {dc} muertes. Las cicatrices temporales queman su alma."
                elif dc <= 10:
                    quote = f"* {dc} resurrecciones... La linea entre vivo y muerto se borra."
                else:
                    quote = f"* ¡¡{dc} MUERTES!! La muerte ya ni le asusta... ¡le fascina!"

                qy = box_sub.y + 180
                for ql in self.wrap_text(quote, self.font_small, max_width=245):
                    q_s = self.font_small.render(ql, False, (255, 235, 140))
                    surface.blit(q_s, (box_sub.x + 14, qy))
                    qy += 12

                bk_s = self.font_small.render("[Z / X / C] Volver", False, (140, 145, 160))
                surface.blit(bk_s, (box_sub.right - 95, box_sub.bottom - 15))

            # B) SUBMENÚ DE OBJETOS (ITEM)
            elif self.state in ("SUBMENU_ITEM", "SUBMENU_ITEM_ACTION", "ITEM_MESSAGE"):
                hdr = self.font_hud.render("* OBJETOS *", False, (255, 255, 255))
                surface.blit(hdr, (box_sub.x + 14, box_sub.y + 10))

                if not player.inventory:
                    none_s = self.font_dialogue.render("* (No llevas ningun objeto encima)", False, (160, 165, 180))
                    surface.blit(none_s, (box_sub.x + 20, box_sub.y + 40))
                    bk_s = self.font_small.render("[X] Volver", False, (140, 145, 160))
                    surface.blit(bk_s, (box_sub.right - 70, box_sub.bottom - 15))
                    return

                # Mensaje de acción (Usar/Info/Tirar)
                if self.state == "ITEM_MESSAGE":
                    my = box_sub.y + 40
                    for line in self.msg_lines:
                        for wl in self.wrap_text(line, self.font_dialogue, max_width=240):
                            txt_s = self.font_dialogue.render(wl, False, (255, 255, 255))
                            surface.blit(txt_s, (box_sub.x + 20, my))
                            my += 18

                    p_s = self.font_small.render("★ [Z / Enter] Continuar ★", False, (255, 230, 90))
                    surface.blit(p_s, (box_sub.x + 20, box_sub.bottom - 20))
                    return

                # Lista de objetos
                for i, it in enumerate(player.inventory[:6]):
                    iy = box_sub.y + 32 + i * 20
                    is_curr = (i == self.item_idx)
                    col = (255, 255, 255) if is_curr else (180, 185, 200)
                    it_s = self.font_dialogue.render(f"* {it['name']}", False, col)
                    surface.blit(it_s, (box_sub.x + 26, iy))

                    if is_curr and self.state == "SUBMENU_ITEM":
                        self._draw_soul(surface, box_sub.x + 12, iy + 2)

                # Acciones sobre el objeto seleccionado
                curr_item = player.inventory[self.item_idx]
                act_y = box_sub.y + 152
                pygame.draw.line(surface, (60, 65, 80), (box_sub.x + 10, act_y - 8), (box_sub.right - 10, act_y - 8), 1)

                btn_xs = [box_sub.x + 28, box_sub.x + 108, box_sub.x + 188]
                for bi, bname in enumerate(self.action_options):
                    is_sel = (bi == self.action_idx and self.state == "SUBMENU_ITEM_ACTION")
                    b_col = (255, 240, 90) if is_sel else (160, 165, 180)
                    b_s = self.font_hud.render(bname, False, b_col)
                    surface.blit(b_s, (btn_xs[bi] + 14, act_y))

                    if is_sel:
                        self._draw_soul(surface, btn_xs[bi], act_y + 2)

                # Descripción del objeto abajo con ajuste de texto para no salirse del cuadro
                desc_text = f"\"{curr_item.get('desc', '')}\""
                dy = box_sub.y + 172
                for dl in self.wrap_text(desc_text, self.font_small, max_width=245):
                    desc_s = self.font_small.render(dl, False, (190, 215, 240))
                    surface.blit(desc_s, (box_sub.x + 14, dy))
                    dy += 12

                hint = "[X] Cancelar" if self.state == "SUBMENU_ITEM_ACTION" else "[Z] Opciones  [X] Volver"
                h_s = self.font_small.render(hint, False, (140, 145, 160))
                surface.blit(h_s, (box_sub.right - 145, box_sub.bottom - 15))

            # C) SUBMENÚ DE MONÓLOGO INTERIOR Y MENTE
            elif self.state == "SUBMENU_MENTE":
                hdr = self.font_hud.render("* MONOLOGO INTERIOR *", False, (255, 255, 255))
                surface.blit(hdr, (box_sub.x + 14, box_sub.y + 10))

                state = player.mental_state
                state_col = mental_hud.STATE_COLORS.get(state, (255, 255, 255))

                # Rostro de Paniel desde Estadisticas.png ajustado a su marco (34x34) y apoyado en la base
                face = mental_hud.get_face(state, self.anim_time, player=player)
                mente_frame = pygame.Rect(box_sub.x + 16, box_sub.y + 28, 34, 34)
                pygame.draw.rect(surface, (40, 45, 60), mente_frame, border_radius=3)
                surface.blit(face, (mente_frame.x + 1, mente_frame.y + 1))
                pygame.draw.rect(surface, state_col, mente_frame, 1, border_radius=3)

                # Etiqueta de estado y cordura
                lbl_state = self.font_hud.render(f"Estado: {state}", False, state_col)
                lbl_san = self.font_small.render(f"Cordura: {int(player.sanity)}%  |  Muertes: {player.death_count}", False, (220, 225, 235))
                surface.blit(lbl_state, (box_sub.x + 60, box_sub.y + 30))
                surface.blit(lbl_san, (box_sub.x + 60, box_sub.y + 48))

                pygame.draw.line(surface, (70, 75, 95), (box_sub.x + 10, box_sub.y + 70), (box_sub.right - 10, box_sub.y + 70), 1)

                # Pensamientos internos de Paniel con texto ajustado dentro del cuadro
                dc = player.death_count
                if state == "FELIZ":
                    lines = [
                        "* (Paniel respira hondo el aire otoñal).",
                        "* 'Me siento sereno. Las sombras son tranquilas.'",
                        "* 'Mientras conserve mi cordura, saldre de aqui.'",
                        "* (Efecto: Estadisticas en perfecto equilibrio)"
                    ]
                elif state == "TRISTE":
                    lines = [
                        "* (Paniel mira hacia el suelo con desanimo).",
                        f"* 'Siento un gran peso... Ya van {dc} muertes.'",
                        "* 'Mis pasos pesan y me cuesta levantar la guardia.'",
                        "* (Efecto: ATK -3, DEF +2, Velocidad reducida)"
                    ]
                elif state == "TRAUMADO":
                    lines = [
                        "* (Las manos de Paniel tiemblan de panico).",
                        "* '¡Estan ahi! ¡Siento ojos en la oscuridad...!'",
                        f"* '{dc} muertes... Mi alma se quiebra de dolor.'",
                        "* (Efecto: ATK -2, DEF -3, Defensa destrozada)"
                    ]
                elif state == "LOCO":
                    lines = [
                        "* (Paniel suelta una carcajada histerica).",
                        f"* '¡¡{dc} MUERTES!! ¿¡LO VES!? ¡EL DOLOR ES NADA!'",
                        "* '¡¡DEFENSA EN CERO PERO ATAQUE POR LAS NUBES!!'",
                        "* (Efecto: ATK +8, DEF -4, Furia homicida activa)"
                    ]

                ty = box_sub.y + 78
                for line in lines:
                    for wl in self.wrap_text(line, self.font_dialogue, max_width=245):
                        txt_s = self.font_dialogue.render(wl, False, (255, 245, 120) if "(Efecto:" in wl else (240, 240, 250))
                        surface.blit(txt_s, (box_sub.x + 14, ty))
                        ty += 15

                bk_s = self.font_small.render("[Z / X / C] Volver", False, (140, 145, 160))
                surface.blit(bk_s, (box_sub.right - 95, box_sub.bottom - 15))


# ==========================================================
# 4.5 PANTALLA DE TÍTULO E INTRO ESTILO DELTARUNE
# ==========================================================
class DeltaruneTitleScreen:
    """
    Pantalla de introducción y título estilo DELTARUNE:
    - Fase 1 ("LEGEND"): Prólogo cinematográfico con paneles ilustrados,
      efecto máquina de escribir y opción de saltar con [X] o avanzar con [Z].
    - Fase 2 ("TITLE"): Pantalla de título con Fuente Oscura (Dark Fountain)
      ascendente en el fondo, emblema Delta Rune alado, título P A N I E L
      y menú interactivo con el Alma Roja.
    """
    def __init__(self, sound_fx, sprite_mgr=None):
        self.sound_fx = sound_fx
        self.sprite_mgr = sprite_mgr

        self.font_title = pygame.font.SysFont("Lucida Console", 26, bold=True) or pygame.font.SysFont("Courier New", 26, bold=True)
        self.font_sub = pygame.font.SysFont("Lucida Console", 11, bold=True)
        self.font_menu = pygame.font.SysFont("Lucida Console", 12, bold=True)
        self.font_lore = pygame.font.SysFont("Lucida Console", 11)
        self.font_small = pygame.font.SysFont("Lucida Console", 9, bold=True)

        self.state = "LEGEND"  # "LEGEND", "TITLE", "CONTROLS"
        self.timer = 0.0
        self.fade_alpha = 255.0

        # Prólogo estilo "The Legend" de Deltarune
        self.legend_slides = [
            {
                "panel": 0,
                "lines": [
                    "Hace mucho tiempo, una leyenda se",
                    "susurraba entre la niebla otoñal...",
                    "Una leyenda de SOMBRAS y de CORDURA."
                ]
            },
            {
                "panel": 1,
                "lines": [
                    "En el límite entre la vigilia y el",
                    "olvido yace EL CEMENTERIO ETERNO,",
                    "donde las almas rotas nunca descansan."
                ]
            },
            {
                "panel": 2,
                "lines": [
                    "Solo un alma atrapada en el ciclo de",
                    "la muerte puede desafiar la oscuridad",
                    "antes de que su mente se quiebre..."
                ]
            }
        ]
        self.slide_idx = 0
        self.char_idx = 0.0
        self.type_speed = 34.0
        self.last_beep_char = 0

        # Opciones del menú de título
        self.menu_options = ["INICIAR JUEGO", "CONTROLES", "SALIR"]
        self.menu_idx = 0

        # Partículas ascendentes de la Fuente Oscura (Dark Fountain)
        self.fountain_particles = []
        for _ in range(45):
            self.fountain_particles.append({
                "x": random.uniform(0, VIRTUAL_WIDTH),
                "y": random.uniform(0, VIRTUAL_HEIGHT),
                "vy": random.uniform(14.0, 42.0),
                "size": random.choice([1, 2, 2, 3]),
                "phase": random.uniform(0, math.pi * 2),
                "col_idx": random.choice([0, 1, 2])
            })

    def _current_slide_total_chars(self):
        slide = self.legend_slides[self.slide_idx]
        return sum(len(line) for line in slide["lines"])

    def handle_input(self, event):
        """
        Procesa entradas de teclado.
        Retorna:
          - "START_GAME" cuando el jugador elige INICIAR JUEGO
          - "QUIT" cuando elige SALIR
          - None en cualquier otro caso
        """
        if event.type != pygame.KEYDOWN:
            return None

        if self.state == "LEGEND":
            # [X] o [C] salta directamente al título
            if event.key in [pygame.K_x, pygame.K_c, pygame.K_ESCAPE]:
                self.sound_fx.play_select()
                self.state = "TITLE"
                self.fade_alpha = 180.0
                return None

            # [Z], [ENTER] o [ESPACIO] avanza texto o pasa a la siguiente diapositiva
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                total = self._current_slide_total_chars()
                if self.char_idx < total:
                    self.char_idx = float(total)
                else:
                    self.sound_fx.play_select()
                    self.slide_idx += 1
                    if self.slide_idx >= len(self.legend_slides):
                        self.state = "TITLE"
                        self.fade_alpha = 200.0
                    else:
                        self.char_idx = 0.0
                        self.last_beep_char = 0
                return None

        elif self.state == "CONTROLS":
            if event.key in [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                self.sound_fx.play_select()
                self.state = "TITLE"
            return None

        elif self.state == "TITLE":
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.menu_idx = (self.menu_idx - 1) % len(self.menu_options)
                self.sound_fx.play_move()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.menu_idx = (self.menu_idx + 1) % len(self.menu_options)
                self.sound_fx.play_move()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self.sound_fx.play_select()
                choice = self.menu_options[self.menu_idx]
                if choice == "INICIAR JUEGO":
                    return "START_GAME"
                elif choice == "CONTROLES":
                    self.state = "CONTROLS"
                elif choice == "SALIR":
                    return "QUIT"
            elif event.key == pygame.K_ESCAPE:
                return "QUIT"

        return None

    def update(self, dt):
        self.timer += dt
        if self.fade_alpha > 0:
            self.fade_alpha = max(0.0, self.fade_alpha - 260.0 * dt)

        if self.state == "LEGEND":
            total = self._current_slide_total_chars()
            if self.char_idx < total:
                self.char_idx = min(float(total), self.char_idx + self.type_speed * dt)
                if int(self.char_idx) - self.last_beep_char >= 3:
                    self.last_beep_char = int(self.char_idx)
                    self.sound_fx.play_blip()

        # Actualizar partículas de la Fuente Oscura
        for p in self.fountain_particles:
            p["y"] -= p["vy"] * dt
            p["x"] += math.sin(self.timer * 2.0 + p["phase"]) * 8.0 * dt
            if p["y"] < -6:
                p["y"] = VIRTUAL_HEIGHT + 6
                p["x"] = random.uniform(0, VIRTUAL_WIDTH)

    def _draw_delta_emblem(self, surface, cx, cy, scale=1.0, color=(190, 215, 255)):
        """Dibuja el emblema alado estilo Delta Rune."""
        r_orb = max(3, int(6 * scale))
        pygame.draw.circle(surface, color, (cx, cy - int(6 * scale)), r_orb, 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy - int(6 * scale)), max(1, r_orb - 3))

        # Alas laterales
        left_wing = [
            (cx - int(8 * scale), cy - int(6 * scale)),
            (cx - int(32 * scale), cy - int(15 * scale)),
            (cx - int(25 * scale), cy - int(3 * scale)),
            (cx - int(36 * scale), cy + int(2 * scale)),
            (cx - int(12 * scale), cy + int(2 * scale)),
        ]
        right_wing = [
            (cx + int(8 * scale), cy - int(6 * scale)),
            (cx + int(32 * scale), cy - int(15 * scale)),
            (cx + int(25 * scale), cy - int(3 * scale)),
            (cx + int(36 * scale), cy + int(2 * scale)),
            (cx + int(12 * scale), cy + int(2 * scale)),
        ]
        pygame.draw.polygon(surface, color, left_wing, 1)
        pygame.draw.polygon(surface, color, right_wing, 1)

        # Tres triángulos inferiores (Delta)
        for dx, dy, sz in [(-int(10 * scale), int(6 * scale), int(5 * scale)),
                           (int(10 * scale), int(6 * scale), int(5 * scale)),
                           (0, int(8 * scale), int(6 * scale))]:
            tri = [
                (cx + dx, cy + dy + sz),
                (cx + dx - sz, cy + dy - sz // 2),
                (cx + dx + sz, cy + dy - sz // 2),
            ]
            pygame.draw.polygon(surface, color, tri, 1)

    def _draw_soul_heart(self, surface, cx, cy, color=(255, 45, 65)):
        """Dibuja el corazón pixel-art del Alma estilo Deltarune."""
        pts = [
            (cx, cy + 5),
            (cx - 6, cy - 1),
            (cx - 6, cy - 4),
            (cx - 3, cy - 6),
            (cx, cy - 3),
            (cx + 3, cy - 6),
            (cx + 6, cy - 4),
            (cx + 6, cy - 1),
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, (255, 190, 200), pts, 1)

    def _draw_legend(self, surface):
        surface.fill((6, 6, 12))

        # Marco ilustrado superior estilo "The Legend" de Deltarune (sepia/cian oscuro)
        art_rect = pygame.Rect(68, 22, 264, 134)
        pygame.draw.rect(surface, (16, 18, 32), art_rect)

        panel_id = self.legend_slides[self.slide_idx]["panel"]
        sepia_main = (195, 155, 95)
        sepia_bright = (240, 205, 135)
        sepia_dark = (75, 55, 40)

        # Ilustración según la diapositiva
        if panel_id == 0:
            # Panel 1: Colina bajo la luna y fuente de sombra surgiendo
            pygame.draw.circle(surface, sepia_bright, (art_rect.centerx, art_rect.y + 38), 20)
            pygame.draw.circle(surface, (16, 18, 32), (art_rect.centerx + 7, art_rect.y + 34), 17)
            for i in range(6):
                w_bar = 18 - i * 2
                pygame.draw.rect(surface, (90, 120, 195), (art_rect.centerx - w_bar // 2, art_rect.y + 20 + i * 16, w_bar, 14))
            pygame.draw.ellipse(surface, sepia_dark, (art_rect.x + 20, art_rect.bottom - 38, 224, 50))
            self._draw_delta_emblem(surface, art_rect.centerx, art_rect.y + 68, scale=1.1, color=sepia_bright)

        elif panel_id == 1:
            # Panel 2: Siluetas de verjas góticas, cruces y niebla del cementerio
            pygame.draw.rect(surface, (26, 22, 38), (art_rect.x, art_rect.bottom - 34, art_rect.width, 34))
            # Cruces y lápidas
            for gx in [96, 135, 265, 300]:
                pygame.draw.rect(surface, sepia_main, (gx - 6, art_rect.bottom - 52, 12, 22), border_radius=3)
                pygame.draw.line(surface, sepia_bright, (gx, art_rect.bottom - 64), (gx, art_rect.bottom - 48), 2)
                pygame.draw.line(surface, sepia_bright, (gx - 5, art_rect.bottom - 58), (gx + 5, art_rect.bottom - 58), 2)
            # Arco gótico central
            arch_rect = pygame.Rect(art_rect.centerx - 28, art_rect.y + 34, 56, 72)
            pygame.draw.rect(surface, sepia_bright, arch_rect, 2, border_top_left_radius=24, border_top_right_radius=24)
            for bx in range(arch_rect.x + 8, arch_rect.right - 4, 9):
                pygame.draw.line(surface, sepia_main, (bx, arch_rect.y + 10), (bx, arch_rect.bottom), 1)

        else:
            # Panel 3: Paniel frente al Alma Roja flotante y ojos en la oscuridad
            for ex, ey in [(105, 52), (295, 56), (125, 86), (275, 84)]:
                pygame.draw.circle(surface, (225, 50, 70), (ex - 5, ey), 2)
                pygame.draw.circle(surface, (225, 50, 70), (ex + 5, ey), 2)
            bob = int(math.sin(self.timer * 4.0) * 3)
            self._draw_soul_heart(surface, art_rect.centerx, art_rect.y + 52 + bob, color=(255, 50, 75))
            pygame.draw.circle(surface, (255, 90, 110), (art_rect.centerx, art_rect.y + 52 + bob), 16, 1)
            if self.sprite_mgr:
                spr = self.sprite_mgr.state_frames.get("FELIZ", self.sprite_mgr.frames)["UP"][0]
                surface.blit(spr, (art_rect.centerx - spr.get_width() // 2, art_rect.bottom - spr.get_height() - 12))

        # Doble borde estilo Deltarune en el panel ilustrado
        pygame.draw.rect(surface, sepia_bright, art_rect, 2)
        pygame.draw.rect(surface, sepia_dark, art_rect.inflate(-6, -6), 1)

        # Texto narrativo centrado debajo con efecto máquina de escribir
        slide = self.legend_slides[self.slide_idx]
        rem = int(self.char_idx)
        ty = 176
        for line in slide["lines"]:
            if rem <= 0:
                break
            vis = line[:rem]
            rem -= len(line)
            shd = self.font_lore.render(vis, False, (35, 30, 55))
            txt = self.font_lore.render(vis, False, (235, 225, 195))
            tx = (VIRTUAL_WIDTH - self.font_lore.size(line)[0]) // 2
            surface.blit(shd, (tx + 1, ty + 1))
            surface.blit(txt, (tx, ty))
            ty += 18

        # Indicadores inferiores
        dots_str = "  ".join("◆" if i == self.slide_idx else "◇" for i in range(len(self.legend_slides)))
        dots_s = self.font_small.render(dots_str, False, (140, 150, 185))
        surface.blit(dots_s, ((VIRTUAL_WIDTH - dots_s.get_width()) // 2, 248))

        hint_s = self.font_small.render("[Z / ENTER] Continuar    [X] Saltar Intro", False, (125, 135, 170))
        surface.blit(hint_s, ((VIRTUAL_WIDTH - hint_s.get_width()) // 2, 274))

    def _draw_title(self, surface):
        # Fondo abismal azul/violeta oscuro estilo Deltarune
        surface.fill((6, 8, 18))

        # Columna de luz de la Fuente Oscura (Dark Fountain) en el centro
        cx = VIRTUAL_WIDTH // 2
        beam_pulse = int(math.sin(self.timer * 2.6) * 8)
        for layer, (w_half, col) in enumerate([
            (54 + beam_pulse, (14, 24, 52)),
            (36 + beam_pulse // 2, (22, 42, 86)),
            (20 + beam_pulse // 3, (36, 72, 135)),
            (9, (65, 125, 205)),
        ]):
            pygame.draw.rect(surface, col, (cx - w_half, 0, w_half * 2, VIRTUAL_HEIGHT))

        # Ondas sinusoidales ascendentes dentro de la fuente
        for y in range(0, VIRTUAL_HEIGHT, 6):
            wave = int(math.sin(y * 0.045 - self.timer * 3.5) * 14)
            pygame.draw.line(surface, (85, 155, 235), (cx + wave - 6, y), (cx + wave + 6, y), 1)

        # Partículas luminosas ascendentes
        p_cols = [(110, 195, 255), (170, 140, 255), (220, 245, 255)]
        for p in self.fountain_particles:
            c = p_cols[p["col_idx"]]
            pygame.draw.rect(surface, c, (int(p["x"]), int(p["y"]), p["size"], p["size"]))

        # Silueta de colina y verjas del cementerio en la base
        pygame.draw.rect(surface, (4, 5, 12), (0, 266, VIRTUAL_WIDTH, 34))
        for gx in range(16, VIRTUAL_WIDTH, 22):
            pygame.draw.line(surface, (18, 24, 44), (gx, 252), (gx, 266), 2)
        pygame.draw.line(surface, (28, 38, 68), (0, 266), (VIRTUAL_WIDTH, 266), 2)

        # Emblema Delta Rune superior
        self._draw_delta_emblem(surface, cx, 42, scale=1.25, color=(190, 225, 255))

        # Título principal "P A N I E L" con resplandor estilo Deltarune
        title_text = "P A N I E L"
        glow_offset = int(math.sin(self.timer * 3.0) * 1.5)
        t_shadow = self.font_title.render(title_text, False, (25, 50, 110))
        t_glow = self.font_title.render(title_text, False, (100, 180, 255))
        t_main = self.font_title.render(title_text, False, (255, 255, 255))
        tx = (VIRTUAL_WIDTH - t_main.get_width()) // 2
        ty = 66
        surface.blit(t_shadow, (tx + 2, ty + 3))
        surface.blit(t_glow, (tx, ty + glow_offset))
        surface.blit(t_main, (tx, ty))

        # Línea divisoria y subtítulo
        pygame.draw.line(surface, (110, 175, 255), (cx - 95, 100), (cx + 95, 100), 1)
        sub_s = self.font_sub.render("— EL CEMENTERIO —", False, (185, 215, 255))
        surface.blit(sub_s, ((VIRTUAL_WIDTH - sub_s.get_width()) // 2, 106))

        # Sprite de Paniel mirando hacia la Fuente Oscura
        if self.sprite_mgr:
            spr = self.sprite_mgr.state_frames.get("FELIZ", self.sprite_mgr.frames)["DOWN"][0]
            surface.blit(spr, (cx - spr.get_width() // 2, 128))

        # Caja de menú estilo Deltarune
        menu_box = pygame.Rect(cx - 92, 168, 184, 78)
        pygame.draw.rect(surface, (8, 10, 22), menu_box)
        pygame.draw.rect(surface, (255, 255, 255), menu_box, 2)
        pygame.draw.rect(surface, (60, 95, 160), menu_box.inflate(-6, -6), 1)

        for i, opt in enumerate(self.menu_options):
            selected = (i == self.menu_idx)
            oy = menu_box.y + 12 + i * 21
            col = (255, 245, 90) if selected else (215, 225, 245)
            opt_s = self.font_menu.render(opt, False, col)
            ox = cx - opt_s.get_width() // 2 + (8 if selected else 0)
            surface.blit(opt_s, (ox, oy))
            if selected:
                self._draw_soul_heart(surface, ox - 14, oy + 6)

        # Pie de pantalla
        foot_s = self.font_small.render("[Z / ENTER] Seleccionar   [C] Menú en juego", False, (130, 145, 180))
        surface.blit(foot_s, ((VIRTUAL_WIDTH - foot_s.get_width()) // 2, 276))

        # Ventana superpuesta de Controles si está activa
        if self.state == "CONTROLS":
            ctrl_box = pygame.Rect(44, 54, 312, 192)
            pygame.draw.rect(surface, (6, 8, 18), ctrl_box)
            pygame.draw.rect(surface, (255, 255, 255), ctrl_box, 2)
            pygame.draw.rect(surface, (80, 130, 210), ctrl_box.inflate(-6, -6), 1)

            hdr = self.font_menu.render("* CONTROLES DEL JUEGO *", False, (255, 245, 90))
            surface.blit(hdr, (cx - hdr.get_width() // 2, ctrl_box.y + 14))

            controls_list = [
                ("Flechas / WASD", "Mover a Paniel / Alma"),
                ("Z / ENTER", "Interactuar / Confirmar"),
                ("X / SHIFT", "Correr / Cancelar / Saltar"),
                ("C", "Abrir Menú (Obj / Mente)"),
                ("1, 2, 3, 4", "Probar Estados de Cordura"),
                ("ESC", "Salir del juego"),
            ]
            cy_line = ctrl_box.y + 42
            for k_txt, d_txt in controls_list:
                ks = self.font_small.render(k_txt, False, (130, 210, 255))
                ds = self.font_small.render(d_txt, False, (235, 235, 245))
                surface.blit(ks, (ctrl_box.x + 18, cy_line))
                surface.blit(ds, (ctrl_box.x + 128, cy_line))
                cy_line += 20

            back_s = self.font_small.render("Presiona [Z / X] para volver", False, (255, 245, 90))
            surface.blit(back_s, (cx - back_s.get_width() // 2, ctrl_box.bottom - 22))

    def draw(self, surface):
        if self.state == "LEGEND":
            self._draw_legend(surface)
        else:
            self._draw_title(surface)

        if self.fade_alpha > 0:
            fade_s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_s.fill((0, 0, 0, int(self.fade_alpha)))
            surface.blit(fade_s, (0, 0))


