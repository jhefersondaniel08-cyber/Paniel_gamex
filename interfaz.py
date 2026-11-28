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
        if isinstance(lines, str):
            raw_list = [lines]
        else:
            raw_list = list(lines or [])

        # Dividir saltos de línea y paginar automáticamente en bloques de máximo 3 líneas envueltas
        # para que ningún cartel largo quede escribiendo fuera de la caja ni bloquee el diálogo
        paginated = []
        max_w = self.box_rect.width - 68
        for entry in raw_list:
            for subline in str(entry).split("\n"):
                subline = subline.strip()
                if not subline:
                    continue
                wrapped = self.wrap_text(subline, max_width=max_w)
                if len(wrapped) <= 3:
                    paginated.append(subline)
                else:
                    for i in range(0, len(wrapped), 3):
                        chunk = " ".join(wrapped[i:i + 3])
                        paginated.append(chunk)

        if not paginated:
            paginated = ["* ..."]

        self.lines = paginated
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

        # Fondo negro de la caja con doble marco más grueso estilo Deltarune
        pygame.draw.rect(surface, COLOR_BLACK, self.box_rect)
        pygame.draw.rect(surface, (110, 65, 210), self.box_rect.inflate(4, 4), 2)
        pygame.draw.rect(surface, COLOR_WHITE, self.box_rect, 4)
        inner = self.box_rect.inflate(-6, -6)
        pygame.draw.rect(surface, (55, 45, 90), inner, 2)

        prev_clip = surface.get_clip()
        surface.set_clip(inner)

        # Si hay retrato de Paniel disponible, mostrarlo 1:1 sin deformar y apoyado en la base de su marco
        portrait = player.get_stat_portrait() if (player is not None and hasattr(player, "get_stat_portrait")) else None
        if portrait is not None:
            pw, ph = portrait.get_size()
            p_box = pygame.Rect(self.box_rect.x + 10, self.box_rect.y + 12, pw + 2, ph + 2)
            pygame.draw.rect(surface, (18, 20, 32), p_box, border_radius=2)
            surface.blit(portrait, (p_box.x + 1, p_box.y + 1))
            pygame.draw.rect(surface, (120, 100, 190), p_box, 1, border_radius=2)
            text_x = p_box.right + 10
            max_width = self.box_rect.width - (p_box.width + 24)
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
        """Genera el rostro pixel art 32x32 de Paniel reproduciendo fielmente su diseño original auténtico."""
        anim_step = int(t * 7) % 6
        key = (state, anim_step)
        if key in self._cache:
            return self._cache[key]

        surf = pygame.Surface((32, 32), pygame.SRCALPHA)

        # Color base de piel del diseño de Paniel
        skin_color = {
            "FELIZ":      (255, 196, 155),
            "TRISTE":     (215, 200, 220),
            "TRAUMADO":   (190, 180, 210),
            "LOCO":       (255, 185, 155),
            "DARK_WORLD": (215, 200, 240),
        }.get(state, (255, 196, 155))

        if state == "DARK_WORLD":
            hair_gray = (70, 130, 200)
            hair_white = (170, 225, 255)
            eye_col = (10, 15, 30)
        elif state == "LOCO":
            hair_gray = (175, 175, 185)
            hair_white = (255, 250, 250)
            eye_col = (235, 30, 30)
        else:
            hair_gray = (196, 196, 196)
            hair_white = (255, 255, 255)
            eye_col = (0, 0, 0)

        # Cabeza rectangular con bordes suaves según el pixel art original
        pygame.draw.rect(surf, skin_color, (7, 10, 18, 11), border_radius=3)

        # Mechones puntiagudos de cabello del diseño original
        # Lado izquierdo (tono plateado/gris)
        pygame.draw.rect(surf, hair_gray, (4, 7, 11, 7))
        pygame.draw.polygon(surf, hair_gray, [(5, 7), (8, 2), (10, 7)])
        # Lado derecho (brillos blancos característicos)
        pygame.draw.rect(surf, hair_white, (15, 7, 13, 7))
        pygame.draw.polygon(surf, hair_white, [(21, 7), (24, 2), (26, 7)])

        # Flequillo superior a dos tonos
        pygame.draw.rect(surf, hair_gray, (5, 9, 10, 3))
        pygame.draw.rect(surf, hair_white, (15, 9, 12, 3))

        # Mechón blanco central característico que cae entre los ojos
        pygame.draw.rect(surf, hair_white, (13, 11, 2, 4))

        # Contorno oscuro exterior
        pygame.draw.rect(surf, (0, 0, 0), (6, 5, 20, 17), 1, border_radius=3)

        # Ojos del diseño original: ranuras verticales características
        shake = int(math.sin(t * 26.0) * 1.5) if state == "LOCO" else 0

        if state == "FELIZ":
            # Ojos auténticos de Paniel: ranuras verticales
            pygame.draw.rect(surf, eye_col, (10, 13, 1, 4))
            pygame.draw.rect(surf, eye_col, (15, 13, 1, 4))
            # Amplia sonrisa auténtica del diseño de Paniel
            pygame.draw.rect(surf, (0, 0, 0), (10, 18, 7, 1))
            pygame.draw.rect(surf, (0, 0, 0), (11, 19, 5, 1))

        elif state == "TRISTE":
            # Ojos melancólicos con leve inclinación y lágrima
            pygame.draw.line(surf, (30, 30, 60), (9, 14), (11, 16), 1)
            pygame.draw.line(surf, (30, 30, 60), (16, 16), (18, 14), 1)
            pygame.draw.circle(surf, (110, 175, 255), (10, 18), 1)
            pygame.draw.rect(surf, (60, 50, 70), (11, 19, 5, 1))

        elif state == "TRAUMADO":
            # Ojos abiertos con pupilas en hendidura temblorosa
            pygame.draw.rect(surf, (255, 255, 255), (9, 13, 3, 4))
            pygame.draw.rect(surf, (255, 255, 255), (15, 13, 3, 4))
            pygame.draw.rect(surf, (0, 0, 0), (10, 14, 1, 2))
            pygame.draw.rect(surf, (0, 0, 0), (16, 14, 1, 2))
            pygame.draw.rect(surf, (0, 0, 0), (11, 19, 5, 1))

        elif state == "LOCO":
            # Ojos inyectados en sangre vibrando al unísono
            pygame.draw.rect(surf, (235, 30, 30), (10 + shake, 13, 1, 4))
            pygame.draw.rect(surf, (235, 30, 30), (15 + shake, 13, 1, 4))
            pygame.draw.rect(surf, (255, 220, 60), (10 + shake, 14, 1, 1))
            pygame.draw.rect(surf, (255, 220, 60), (15 + shake, 14, 1, 1))
            # Sonrisa desquiciada de oreja a oreja con dientes
            pygame.draw.rect(surf, (180, 20, 20), (9 + shake, 18, 9, 2))
            for di in range(4):
                pygame.draw.rect(surf, (255, 255, 255), (10 + di * 2 + shake, 18, 1, 1))

        elif state == "DARK_WORLD":
            # Diseño auténtico del Dark World
            pygame.draw.rect(surf, (10, 20, 45), (10, 13, 1, 4))
            pygame.draw.rect(surf, (10, 20, 45), (15, 13, 1, 4))
            pygame.draw.rect(surf, (10, 20, 45), (10, 18, 7, 1))
            pygame.draw.rect(surf, (10, 20, 45), (11, 19, 5, 1))

        self._cache[key] = surf
        return surf

        self._cache[key] = surf
        return surf

    def get_face(self, state, t, player=None):
        """Obtiene el retrato 1:1 desde Estadisticas.png del estado mental actual (o respaldo procedural)."""
        if player is not None:
            portrait = None
            if hasattr(player, "get_stat_portrait"):
                portrait = player.get_stat_portrait()
            elif hasattr(player, "stat_portraits") and state in player.stat_portraits:
                portrait = player.stat_portraits[state]

            if portrait is not None:
                if state == "LOCO":
                    shake_x = int(math.sin(t * 26.0) * 1.0)
                    pw, ph = portrait.get_size()
                    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
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

        # 1. Rostro de Paniel 1:1 original (sin deformar) en un marco ajustado a su tamaño exacto y apoyado en la base
        face = self.get_face(state, self.anim_time, player=player)
        fw, fh = face.get_size()
        face_frame = pygame.Rect(box_x + 7, box_y + 9, fw + 2, fh + 2)
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

        # Lugar actual alineado a la derecha dentro de la caja (sin desbordar ni pisar textos)
        loc_txt = self.font_prompt.render(area_name, False, (205, 225, 255))
        loc_x = max(bar_rect.x + 210, bar_rect.right - loc_txt.get_width() - 8)
        if is_running:
            run_lbl = self.font_prompt.render("»RUN«", False, (140, 240, 255))
            if bar_rect.x + 206 + run_lbl.get_width() + 6 <= loc_x:
                surface.blit(run_lbl, (bar_rect.x + 206, bar_rect.y + 5))

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

        self.main_options = ["ITEM", "EQUIP", "STAT", "MENTE"]
        self.main_idx = 0
        self.state = "MAIN"  # MAIN, SUBMENU_ITEM, SUBMENU_ITEM_ACTION, ITEM_MESSAGE, SUBMENU_EQUIP_SLOT, SUBMENU_EQUIP_LIST, SUBMENU_STAT, SUBMENU_MENTE

        self.item_idx = 0
        self.action_idx = 0  # 0: USAR, 1: INFO, 2: TIRAR
        self.action_options = ["USAR", "INFO", "TIRAR"]
        self.equip_slot_idx = 0  # 0: ARMA, 1: ARMADURA 1, 2: ARMADURA 2
        self.equip_list_idx = 0
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

        # 1. Menú Principal Izquierdo [ITEM, EQUIP, STAT, MENTE]
        if self.state == "MAIN":
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.main_idx = (self.main_idx - 1) % len(self.main_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.main_idx = (self.main_idx + 1) % len(self.main_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self.sound_fx.play_select()
                opt_name = self.main_options[self.main_idx]
                if opt_name == "ITEM":
                    self.state = "SUBMENU_ITEM"
                    self.item_idx = 0
                elif opt_name == "EQUIP":
                    if hasattr(player, "sync_equipment_bag"):
                        player.sync_equipment_bag()
                    self.state = "SUBMENU_EQUIP_SLOT"
                    self.equip_slot_idx = 0
                    self.equip_list_idx = 0
                elif opt_name == "STAT":
                    self.state = "SUBMENU_STAT"
                elif opt_name == "MENTE":
                    self.state = "SUBMENU_MENTE"
            elif event.key in [pygame.K_x, pygame.K_c, pygame.K_ESCAPE]:
                self.close()

        # 1.5 Submenú EQUIPAMIENTO estilo Deltarune (Selección de Ranura: ARMA, ARMADURA 1, ARMADURA 2)
        elif self.state == "SUBMENU_EQUIP_SLOT":
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.equip_slot_idx = (self.equip_slot_idx - 1) % 3
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.equip_slot_idx = (self.equip_slot_idx + 1) % 3
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                candidates = player.get_candidates_for_slot(self.equip_slot_idx) if hasattr(player, "get_candidates_for_slot") else []
                if candidates:
                    self.state = "SUBMENU_EQUIP_LIST"
                    curr_g = player.get_slot_gear(self.equip_slot_idx)
                    self.equip_list_idx = 0
                    for ci, cg in enumerate(candidates):
                        if curr_g and cg["name"] == curr_g.get("name"):
                            self.equip_list_idx = ci
                            break
                    self.sound_fx.play_select()
            elif event.key in [pygame.K_x, pygame.K_c, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self.sound_fx.play_select()

        # 1.6 Submenú EQUIPAMIENTO estilo Deltarune (Lista de Armas o Armaduras para la ranura elegida)
        elif self.state == "SUBMENU_EQUIP_LIST":
            candidates = player.get_candidates_for_slot(self.equip_slot_idx) if hasattr(player, "get_candidates_for_slot") else []
            if not candidates:
                self.state = "SUBMENU_EQUIP_SLOT"
                return
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.equip_list_idx = (self.equip_list_idx - 1) % len(candidates)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.equip_list_idx = (self.equip_list_idx + 1) % len(candidates)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                chosen = candidates[self.equip_list_idx]
                if player.equip_in_slot(self.equip_slot_idx, chosen):
                    self.sound_fx.play_heal()
                else:
                    self.sound_fx.play_hurt()
                self.state = "SUBMENU_EQUIP_SLOT"
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "SUBMENU_EQUIP_SLOT"
                self.sound_fx.play_select()

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

                if self.action_idx == 0:  # USAR / EQUIPAR
                    if item.get("atk_bonus") or item.get("def_bonus"):
                        equipped_ok = True
                        if hasattr(player, "equip_in_slot"):
                            slot_t = 0 if item.get("atk_bonus", 0) >= item.get("def_bonus", 0) or item["name"] == "Sturdy Arm" else 1
                            equipped_ok = player.equip_in_slot(slot_t, {
                                "name": item["name"],
                                "slot": "BOTH" if item["name"] == "Sturdy Arm" else ("WEAPON" if slot_t == 0 else "ARMOR"),
                                "atk_bonus": item.get("atk_bonus", 0),
                                "def_bonus": item.get("def_bonus", 0),
                                "desc": item.get("desc", ""),
                            })
                        elif not getattr(player, "sturdy_arm_equipped", False):
                            player.sturdy_arm_equipped = True
                            player.attack += item.get("atk_bonus", 0)
                            player.defense += item.get("def_bonus", 0)
                            player.weapon = item["name"]
                            player.armor = f"{item['name']} (+10 DEF)"
                        if equipped_ok:
                            self.sound_fx.play_heal()
                            self.msg_lines = [
                                f"* ¡Equipaste {item['name']}!",
                                f"* \"{item.get('desc', '')}\"",
                                f"* (Estadísticas actuales: ATK {player.effective_attack} | DEF {player.effective_defense})",
                            ]
                        else:
                            self.sound_fx.play_hurt()
                            self.msg_lines = [
                                f"* Ya tienes equipado {item['name']} en otra ranura.",
                                "* Cámbialo desde el menú [EQUIP] si deseas moverlo.",
                            ]
                        self.state = "ITEM_MESSAGE"
                    else:
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

        # 1. Caja de Opciones Izquierda (ITEM, EQUIP, STAT, MENTE)
        box_menu = pygame.Rect(22, 34, 80, 102)
        pygame.draw.rect(surface, (0, 0, 0), box_menu)
        pygame.draw.rect(surface, (255, 255, 255), box_menu, 3)

        for i, opt in enumerate(self.main_options):
            is_sel = (i == self.main_idx)
            col = (255, 240, 90) if (is_sel and self.state != "MAIN") else (255, 255, 255)
            txt = self.font_hud.render(opt, False, col)
            surface.blit(txt, (box_menu.x + 22, box_menu.y + 10 + i * 21))

        # Alma indicadora en el menú principal
        if self.state == "MAIN":
            self._draw_soul(surface, box_menu.x + 7, box_menu.y + 11 + self.main_idx * 21)

        # 2. Caja Mini-Status Izquierda (debajo del menú)
        box_mini = pygame.Rect(22, 142, 80, 78)
        pygame.draw.rect(surface, (0, 0, 0), box_mini)
        pygame.draw.rect(surface, (255, 255, 255), box_mini, 3)

        name_s = self.font_hud.render("PANIEL", False, (255, 255, 255))
        lv_s = self.font_small.render(f"LV  {player.lv}", False, (255, 220, 80))
        hp_s = self.font_small.render(f"HP  {player.hp}/{player.max_hp}", False, (255, 255, 255))
        g_s = self.font_small.render(f"D$  {player.gold}", False, (255, 230, 90))

        surface.blit(name_s, (box_mini.x + 8, box_mini.y + 8))
        surface.blit(lv_s, (box_mini.x + 8, box_mini.y + 24))
        surface.blit(hp_s, (box_mini.x + 8, box_mini.y + 40))
        surface.blit(g_s, (box_mini.x + 8, box_mini.y + 56))

        # 3. Ventana Derecha de Submenú (se abre al elegir EQUIP, STAT, ITEM o MENTE)
        if self.state != "MAIN":
            box_sub = pygame.Rect(106, 26, 282, 246)
            pygame.draw.rect(surface, (0, 0, 0), box_sub)
            pygame.draw.rect(surface, (255, 255, 255), box_sub, 3)

            # A-0) SUBMENÚ DE EQUIPAMIENTO ESTILO DELTARUNE (EQUIP: Armas y Armaduras)
            if self.state in ("SUBMENU_EQUIP_SLOT", "SUBMENU_EQUIP_LIST"):
                pygame.draw.rect(surface, (75, 110, 185), box_sub.inflate(-6, -6), 1)
                hdr = self.font_hud.render("★ EQUIPAMIENTO DE PANIEL ★", False, (100, 235, 255))
                surface.blit(hdr, (box_sub.x + 10, box_sub.y + 7))

                # 1) BLOQUE SUPERIOR ORGANIZADO: Caja de 3 Ranuras (Izquierda) + Marco de Retrato 1:1 (Derecha)
                slots_pane = pygame.Rect(box_sub.x + 8, box_sub.y + 23, 218, 60)
                port_pane = pygame.Rect(box_sub.x + 230, box_sub.y + 23, 44, 60)
                pygame.draw.rect(surface, (14, 16, 30), slots_pane, border_radius=3)
                pygame.draw.rect(surface, (95, 225, 255) if self.state == "SUBMENU_EQUIP_SLOT" else (65, 95, 160), slots_pane, 1, border_radius=3)
                pygame.draw.rect(surface, (14, 16, 30), port_pane, border_radius=3)
                pygame.draw.rect(surface, (65, 95, 160), port_pane, 1, border_radius=3)

                state = player.mental_state
                state_col = mental_hud.STATE_COLORS.get(state, (255, 255, 255))
                eq_face = mental_hud.get_face(state, self.anim_time, player=player)
                efw, efh = eq_face.get_size()
                eq_frame = pygame.Rect(port_pane.centerx - (efw + 2) // 2, port_pane.y + 8, efw + 2, efh + 2)
                pygame.draw.rect(surface, (35, 40, 58), eq_frame, border_radius=2)
                surface.blit(eq_face, (eq_frame.x + 1, eq_frame.y + 1))
                pygame.draw.rect(surface, state_col, eq_frame, 1, border_radius=2)
                lv_tag_s = self.font_small.render(f"LV {player.lv}", False, (255, 225, 85))
                surface.blit(lv_tag_s, (port_pane.centerx - lv_tag_s.get_width() // 2, port_pane.bottom - 16))

                slot_labels = ["ARMA   :", "ARMAD.1:", "ARMAD.2:"]
                slot_colors = [(255, 145, 90), (110, 225, 255), (165, 250, 155)]
                for si in range(3):
                    sy = slots_pane.y + 5 + si * 18
                    is_slot_sel = (si == self.equip_slot_idx)
                    g_obj = player.get_slot_gear(si) if hasattr(player, "get_slot_gear") else None
                    g_name = g_obj["name"] if g_obj else "(Vacío)"
                    lbl_col = (255, 240, 85) if is_slot_sel else slot_colors[si]
                    val_col = (255, 245, 110) if is_slot_sel else (240, 245, 255)

                    ix, iy = slots_pane.x + 18, sy + 2
                    if si == 0:
                        pygame.draw.line(surface, lbl_col, (ix, iy + 8), (ix + 8, iy), 2)
                        pygame.draw.line(surface, (255, 255, 255), (ix + 1, iy + 5), (ix + 5, iy + 9), 1)
                    else:
                        pygame.draw.polygon(surface, lbl_col, [(ix + 4, iy), (ix + 8, iy + 2), (ix + 7, iy + 7), (ix + 4, iy + 9), (ix + 1, iy + 7), (ix, iy + 2)], 1)

                    ls = self.font_small.render(slot_labels[si], False, lbl_col)
                    vs = self.font_small.render(g_name, False, val_col)
                    surface.blit(ls, (slots_pane.x + 30, sy + 1))
                    surface.blit(vs, (slots_pane.x + 86, sy + 1))

                    if is_slot_sel and self.state == "SUBMENU_EQUIP_SLOT":
                        self._draw_soul(surface, slots_pane.x + 5, sy + 1)

                # 2) BLOQUE CENTRAL DIVIDIDO: Estadísticas en Vivo (Izquierda) y Bolsa de Equipo (Derecha)
                stat_pane = pygame.Rect(box_sub.x + 8, box_sub.y + 87, 116, 102)
                list_pane = pygame.Rect(box_sub.x + 128, box_sub.y + 87, 146, 102)
                pygame.draw.rect(surface, (14, 16, 30), stat_pane, border_radius=3)
                pygame.draw.rect(surface, (65, 95, 160), stat_pane, 1, border_radius=3)
                pygame.draw.rect(surface, (14, 16, 30), list_pane, border_radius=3)
                pygame.draw.rect(surface, (95, 225, 255) if self.state == "SUBMENU_EQUIP_LIST" else (65, 95, 160), list_pane, 1, border_radius=3)
                pygame.draw.line(surface, (45, 65, 115), (stat_pane.x + 6, stat_pane.y + 20), (stat_pane.right - 6, stat_pane.y + 20), 1)
                pygame.draw.line(surface, (45, 65, 115), (list_pane.x + 6, list_pane.y + 20), (list_pane.right - 6, list_pane.y + 20), 1)

                candidates = player.get_candidates_for_slot(self.equip_slot_idx) if hasattr(player, "get_candidates_for_slot") else []
                curr_gear = player.get_slot_gear(self.equip_slot_idx) if hasattr(player, "get_slot_gear") else None
                preview_gear = candidates[self.equip_list_idx] if (self.state == "SUBMENU_EQUIP_LIST" and candidates and self.equip_list_idx < len(candidates)) else curr_gear

                cur_atk = player.effective_attack
                cur_def = player.effective_defense
                old_a = curr_gear.get("atk_bonus", 0) if curr_gear else 0
                old_d = curr_gear.get("def_bonus", 0) if curr_gear else 0
                new_a = preview_gear.get("atk_bonus", 0) if preview_gear else old_a
                new_d = preview_gear.get("def_bonus", 0) if preview_gear else old_d
                prv_atk = max(1, cur_atk - old_a + new_a)
                prv_def = max(0, cur_def - old_d + new_d)

                shdr = self.font_small.render("ESTADÍSTICAS", False, (255, 225, 95))
                surface.blit(shdr, (stat_pane.x + 8, stat_pane.y + 5))

                a_col = (100, 255, 140) if prv_atk > cur_atk else ((255, 95, 95) if prv_atk < cur_atk else (235, 240, 255))
                a_str = f"ATK : {cur_atk} -> {prv_atk}" if self.state == "SUBMENU_EQUIP_LIST" else f"ATK : {cur_atk}"
                surface.blit(self.font_small.render(a_str, False, a_col), (stat_pane.x + 8, stat_pane.y + 26))

                d_col = (95, 235, 255) if prv_def > cur_def else ((255, 95, 95) if prv_def < cur_def else (235, 240, 255))
                d_str = f"DEF : {cur_def} -> {prv_def}" if self.state == "SUBMENU_EQUIP_LIST" else f"DEF : {cur_def}"
                surface.blit(self.font_small.render(d_str, False, d_col), (stat_pane.x + 8, stat_pane.y + 44))

                surface.blit(self.font_small.render(f"HP  : {player.hp}/{player.max_hp}", False, (235, 240, 255)), (stat_pane.x + 8, stat_pane.y + 62))
                surface.blit(self.font_small.render(f"EST : {state}", False, state_col), (stat_pane.x + 8, stat_pane.y + 80))

                lhdr_txt = "ARMAS DISP." if self.equip_slot_idx == 0 else "ARMADURAS DISP."
                surface.blit(self.font_small.render(lhdr_txt, False, (120, 230, 255)), (list_pane.x + 8, list_pane.y + 5))

                start_ci = max(0, min(self.equip_list_idx - 1, max(0, len(candidates) - 4)))
                for row_i, ci in enumerate(range(start_ci, min(len(candidates), start_ci + 4))):
                    cg = candidates[ci]
                    cy_it = list_pane.y + 25 + row_i * 18
                    is_c_sel = (ci == self.equip_list_idx and self.state == "SUBMENU_EQUIP_LIST")
                    is_equipped = (curr_gear and cg["name"] == curr_gear.get("name"))
                    c_col = (255, 240, 85) if is_c_sel else ((110, 255, 160) if is_equipped else (215, 225, 245))
                    c_surf = self.font_small.render(cg["name"], False, c_col)
                    surface.blit(c_surf, (list_pane.x + 20, cy_it))
                    if is_equipped:
                        eq_badge = self.font_small.render("[E]", False, (110, 255, 160))
                        surface.blit(eq_badge, (list_pane.right - eq_badge.get_width() - 6, cy_it))
                    if is_c_sel:
                        self._draw_soul(surface, list_pane.x + 6, cy_it)

                # 3) BLOQUE INFERIOR DE DESCRIPCIÓN Y CONTROLES
                desc_box = pygame.Rect(box_sub.x + 8, box_sub.y + 193, 266, 45)
                pygame.draw.rect(surface, (10, 12, 24), desc_box, border_radius=3)
                pygame.draw.rect(surface, (70, 95, 155), desc_box, 1, border_radius=3)
                active_gear = preview_gear if preview_gear else curr_gear
                desc_str = active_gear.get("desc", "Selecciona una pieza de equipo.") if active_gear else "Ranura vacía."
                dy_eq = desc_box.y + 5
                for dl in self.wrap_text(desc_str, self.font_small, desc_box.width - 14)[:2]:
                    surface.blit(self.font_small.render(dl, False, (205, 230, 255)), (desc_box.x + 7, dy_eq))
                    dy_eq += 12
                hint_eq = "[Z] Equipar  [X] Ranuras" if self.state == "SUBMENU_EQUIP_LIST" else "[Z] Cambiar Equipo  [X] Volver"
                surface.blit(self.font_small.render(hint_eq, False, (255, 230, 90)), (desc_box.x + 7, desc_box.bottom - 13))

            # A) SUBMENÚ DE ESTADÍSTICAS (STAT)
            if self.state == "SUBMENU_STAT":
                title_s = self.font_hud.render('"PANIEL"', False, (255, 255, 255))
                surface.blit(title_s, (box_sub.x + 14, box_sub.y + 10))

                # Retrato 1:1 de Estadisticas.png en la esquina superior derecha del panel STAT
                state = player.mental_state
                state_col = mental_hud.STATE_COLORS.get(state, (255, 255, 255))
                stat_face = mental_hud.get_face(state, self.anim_time, player=player)
                sfw, sfh = stat_face.get_size()
                stat_frame = pygame.Rect(box_sub.right - sfw - 14, box_sub.y + 10, sfw + 2, sfh + 2)
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

                # Rostro 1:1 de Paniel desde Estadisticas.png en su marco exacto y apoyado en la base
                face = mental_hud.get_face(state, self.anim_time, player=player)
                mfw, mfh = face.get_size()
                mente_frame = pygame.Rect(box_sub.x + 16, box_sub.y + 32, mfw + 2, mfh + 2)
                pygame.draw.rect(surface, (40, 45, 60), mente_frame, border_radius=2)
                surface.blit(face, (mente_frame.x + 1, mente_frame.y + 1))
                pygame.draw.rect(surface, state_col, mente_frame, 1, border_radius=2)

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
    Pantalla de título estilo DELTARUNE:
    - Pantalla de título con Fuente Oscura (Dark Fountain) ascendente en el fondo,
      emblema Delta Rune alado, título U N D E R B R E A D y menú interactivo con el Alma Roja.
    """
    def __init__(self, sound_fx, sprite_mgr=None):
        self.sound_fx = sound_fx
        self.sprite_mgr = sprite_mgr

        self.font_title = pygame.font.SysFont("Lucida Console", 26, bold=True) or pygame.font.SysFont("Courier New", 26, bold=True)
        self.font_sub = pygame.font.SysFont("Lucida Console", 11, bold=True)
        self.font_menu = pygame.font.SysFont("Lucida Console", 12, bold=True)
        self.font_small = pygame.font.SysFont("Lucida Console", 9, bold=True)

        self.state = "TITLE"  # "TITLE", "CONTROLS"
        self.timer = 0.0
        self.fade_alpha = 255.0

        # Opciones del menú de título
        self.menu_options = ["INICIAR JUEGO", "TUTORIAL", "CONTROLES", "SALIR"]
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

    def handle_input(self, event):
        """
        Procesa entradas de teclado.
        Retorna:
          - "START_GAME" cuando el jugador elige INICIAR JUEGO
          - "START_TUTORIAL" cuando el jugador elige TUTORIAL
          - "QUIT" cuando elige SALIR
          - None en cualquier otro caso
        """
        if event.type != pygame.KEYDOWN:
            return None

        if self.state == "CONTROLS":
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
                elif choice == "TUTORIAL":
                    return "START_TUTORIAL"
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

        # Título principal "U N D E R B R E A D" con resplandor estilo Deltarune
        title_text = "U N D E R B R E A D"
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
        pygame.draw.line(surface, (110, 175, 255), (cx - 115, 100), (cx + 115, 100), 1)
        sub_s = self.font_sub.render("— SOMBRAS Y DARK WORLD —", False, (185, 215, 255))
        surface.blit(sub_s, ((VIRTUAL_WIDTH - sub_s.get_width()) // 2, 106))

        # Sprite de Paniel mirando hacia la Fuente Oscura
        if self.sprite_mgr:
            spr = self.sprite_mgr.state_frames.get("FELIZ", self.sprite_mgr.frames)["DOWN"][0]
            surface.blit(spr, (cx - spr.get_width() // 2, 123))

        # Caja de menú estilo Deltarune (4 opciones)
        menu_box = pygame.Rect(cx - 92, 166, 184, 92)
        pygame.draw.rect(surface, (8, 10, 22), menu_box)
        pygame.draw.rect(surface, (255, 255, 255), menu_box, 2)
        pygame.draw.rect(surface, (60, 95, 160), menu_box.inflate(-6, -6), 1)

        for i, opt in enumerate(self.menu_options):
            selected = (i == self.menu_idx)
            oy = menu_box.y + 8 + i * 20
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
        self._draw_title(surface)

        if self.fade_alpha > 0:
            fade_s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_s.fill((0, 0, 0, int(self.fade_alpha)))
            surface.blit(fade_s, (0, 0))


# ==========================================================
# MENÚ DE TIENDA DINÁMICO ESTILO DELTARUNE (BAZAR DEL DARK WORLD)
# ==========================================================
class DeltaruneShopMenu:
    """Interfaz de tienda interactiva y animada al estilo Deltarune (Seam / Rouxls / Swatch / Spamton):
    - Escenario superior (400x158) con fondo neón animado, estanterías de reliquias y retrato grande
      del Vendedor del Dark World con expresiones faciales, gafas neón animadas y movimiento de boca al hablar.
    - Paneles inferiores divididos con bordes gruesos estilo Deltarune:
      * Menú principal: COMPRAR, VENDER, HABLAR, SALIR + diálogo vivo del vendedor.
      * Submenú COMPRAR: Catálogo con 'Sturdy Arm' (+5 ATK, +10 DEF) y consumibles del Dark World,
        más panel lateral dinámico con comparación de estadísticas de Paniel en tiempo real.
      * Submenú VENDER: Venta de objetos del inventario por D$.
      * Submenú HABLAR: Temas de conversación con animaciones y reacciones del vendedor.
    """
    def __init__(self, font_hud, font_small, font_dialogue, sound_fx):
        self.font_hud = font_hud
        self.font_small = font_small
        self.font_dialogue = font_dialogue
        self.sound_fx = sound_fx

        self.active = False
        self.vendor_npc = None
        self.state = "MAIN"  # MAIN, BUY, SELL, TALK, TALK_DIALOGUE
        self.main_options = ["COMPRAR", "VENDER", "HABLAR", "SALIR"]
        self.main_idx = 0
        self.sub_idx = 0

        self.anim_time = 0.0
        self.expression = "WELCOME"  # WELCOME, SMUG, EXCITED, TALK, SOLD
        self.keeper_text = ""
        self.keeper_char_idx = 0.0
        self.talk_pages = []
        self.talk_page_idx = 0

        # Partículas flotantes de fondo del bazar del Dark World
        self.bg_sparkles = [
            {
                "x": random.uniform(10, VIRTUAL_WIDTH - 10),
                "y": random.uniform(10, 148),
                "spd": random.uniform(10, 26),
                "phase": random.uniform(0, math.pi * 2),
                "col": random.choice([(80, 245, 255), (255, 85, 210), (255, 235, 90)]),
            }
            for _ in range(20)
        ]

        # Catálogo del Vendedor del Dark World
        self.catalog = [
            {
                "id": "sturdy_arm",
                "name": "Sturdy Arm",
                "price": 25,
                "heal": 0,
                "sanity_heal": 0,
                "atk_bonus": 5,
                "def_bonus": 10,
                "unique": True,
                "desc": "¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.",
            },
            {
                "id": "darkburger",
                "name": "Darkburger",
                "price": 15,
                "heal": 18,
                "sanity_heal": 15,
                "atk_bonus": 0,
                "def_bonus": 0,
                "unique": False,
                "desc": "Hamburguesa misteriosa del Dark World. Restaura +18 HP y +15% Cordura.",
            },
            {
                "id": "pan_estelar",
                "name": "Pan Estelar",
                "price": 12,
                "heal": 14,
                "sanity_heal": 25,
                "atk_bonus": 0,
                "def_bonus": 0,
                "unique": False,
                "desc": "Pan horneado con polvo de estrellas de UnderBread. +14 HP y +25% Cordura.",
            },
            {
                "id": "elixir_neon",
                "name": "Elixir Neón",
                "price": 20,
                "heal": 25,
                "sanity_heal": 30,
                "atk_bonus": 0,
                "def_bonus": 0,
                "unique": False,
                "desc": "Destilado cibernético brillante. Restaura +25 HP y +30% Cordura.",
            },
        ]

        self.talk_topics = [
            (
                "Sobre Sturdy Arm",
                "EXCITED",
                [
                    "* '¡Ah, el [Sturdy Arm]! Mi obra maestra más intrigante.'",
                    "* '¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.'",
                    "* 'Al comprarlo se guarda en tu bolsa de equipo ([C] -> EQUIP) para que elijas en qué ranura usarlo.'",
                ],
            ),
            (
                "El Dark World",
                "SMUG",
                [
                    "* 'La oscuridad bajo el sótano de la Iglesia cobró forma propia.'",
                    "* '¿Notaste cómo cambió tu atuendo al cruzar la Fuente Oscura?'",
                    "* 'Aquí los enemigos atacan con trayectorias erráticas: ¡mantén listo tu Parry [Z] y tu Dash [X]!'",
                ],
            ),
            (
                "Sobre los Jefes",
                "TALK",
                [
                    "* 'En la superficie aguarda Morvath el Sepulturero, y más allá reina Vaelkor, Rey del Cristal Negro.'",
                    "* 'Con mi [Sturdy Arm] (+5 ATK, +10 DEF) y un ★ BlackFlash preciso en la diana, ¡ningún jefe podrá detenerte!'",
                ],
            ),
        ]

    def _set_keeper_text(self, text, expression="WELCOME"):
        self.keeper_text = text
        self.keeper_char_idx = 0.0
        self.expression = expression

    def open(self, vendor_npc=None, player=None):
        self.active = True
        self.vendor_npc = vendor_npc
        self.state = "MAIN"
        self.main_idx = 0
        self.sub_idx = 0
        self._set_keeper_text(
            "* ¡Bienvenido a mi Bazar del Dark World, viajero!\n* ¿Buscas poder robótico... o tal vez mágico?",
            expression="WELCOME",
        )
        self.sound_fx.play_select()

    def close(self):
        self.active = False
        self.sound_fx.play_select()

    def _is_sturdy_arm_sold(self, player):
        if self.vendor_npc and getattr(self.vendor_npc, "sold_sturdy_arm", False):
            return True
        if player and getattr(player, "sturdy_arm_equipped", False):
            return True
        if player and any(g.get("name") == "Sturdy Arm" for g in getattr(player, "equipment_bag", [])):
            return True
        if player and any(it.get("name") == "Sturdy Arm" for it in player.inventory):
            return True
        return False

    def wrap_text(self, text, font, max_width):
        lines = []
        for paragraph in str(text).split("\n"):
            words = paragraph.split(" ")
            curr = ""
            for w in words:
                test = (curr + " " + w).strip()
                if font.size(test)[0] <= max_width:
                    curr = test
                else:
                    if curr:
                        lines.append(curr)
                    curr = w
            if curr:
                lines.append(curr)
        return lines

    def update(self, dt):
        if not self.active:
            return
        self.anim_time += dt
        if self.keeper_char_idx < len(self.keeper_text):
            prev_i = int(self.keeper_char_idx)
            self.keeper_char_idx = min(float(len(self.keeper_text)), self.keeper_char_idx + dt * 42.0)
            if int(self.keeper_char_idx) > prev_i and int(self.keeper_char_idx) % 3 == 0:
                self.sound_fx.play_blip()

        for sp in self.bg_sparkles:
            sp["y"] -= sp["spd"] * dt
            if sp["y"] < 6:
                sp["y"] = 150.0
                sp["x"] = random.uniform(12, VIRTUAL_WIDTH - 12)

    def handle_input(self, event, player):
        if not self.active or event.type != pygame.KEYDOWN:
            return

        if self.state == "MAIN":
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.main_idx = (self.main_idx - 1) % len(self.main_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.main_idx = (self.main_idx + 1) % len(self.main_options)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                opt = self.main_options[self.main_idx]
                if opt == "COMPRAR":
                    self.state = "BUY"
                    self.sub_idx = 0
                    self._set_keeper_text("* ¡Elige lo que te llame la atención! El [Sturdy Arm] es único.", "EXCITED")
                    self.sound_fx.play_select()
                elif opt == "VENDER":
                    self.state = "SELL"
                    self.sub_idx = 0
                    self._set_keeper_text("* ¿Qué tesoros de la superficie traes en tus bolsillos?", "SMUG")
                    self.sound_fx.play_select()
                elif opt == "HABLAR":
                    self.state = "TALK"
                    self.sub_idx = 0
                    self._set_keeper_text("* ¡Jejeje! Siempre tengo tiempo para charlar en la oscuridad.", "TALK")
                    self.sound_fx.play_select()
                elif opt == "SALIR":
                    self.close()
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.close()

        elif self.state == "BUY":
            total_opts = len(self.catalog) + 1  # +1 para "Volver"
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.sub_idx = (self.sub_idx - 1) % total_opts
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.sub_idx = (self.sub_idx + 1) % total_opts
                self.sound_fx.play_select()
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self._set_keeper_text("* ¿Algo más que desees hacer en mi bazar?", "WELCOME")
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                if self.sub_idx == len(self.catalog):
                    self.state = "MAIN"
                    self._set_keeper_text("* ¿Algo más que desees hacer en mi bazar?", "WELCOME")
                    self.sound_fx.play_select()
                    return

                item = self.catalog[self.sub_idx]
                if item["unique"] and self._is_sturdy_arm_sold(player):
                    self.sound_fx.play_hurt()
                    self._set_keeper_text("* ¡Ya compraste el [Sturdy Arm]! Equípalo desde [C] -> EQUIP.", "SMUG")
                    return

                if (not item["unique"]) and len(player.inventory) >= 8:
                    self.sound_fx.play_hurt()
                    self._set_keeper_text("* ¡Tus bolsillos están llenos (8/8)! Usa o vende algún objeto primero.", "TALK")
                    return

                # Si es el Sturdy Arm y al jugador le falta un poco de D$, el vendedor le hace oferta especial para que nunca se quede sin él
                eff_price = min(player.gold, item["price"]) if item["unique"] else item["price"]
                if player.gold < eff_price:
                    self.sound_fx.play_hurt()
                    self._set_keeper_text(f"* ¡Te faltan D$! Necesitas {eff_price} D$ para comprar {item['name']}.", "SMUG")
                    return

                player.gold -= eff_price
                if item["unique"]:
                    if self.vendor_npc is not None:
                        self.vendor_npc.sold_sturdy_arm = True
                    sturdy_gear = {
                        "name": item["name"],
                        "slot": "BOTH",
                        "atk_bonus": item["atk_bonus"],
                        "def_bonus": item["def_bonus"],
                        "desc": item["desc"],
                    }
                    if hasattr(player, "add_equipment"):
                        player.add_equipment(sturdy_gear)
                    elif hasattr(player, "equipment_bag"):
                        if all(g["name"] != sturdy_gear["name"] for g in player.equipment_bag):
                            player.equipment_bag.append(sturdy_gear)
                    self.sound_fx.play_chest()
                    self._set_keeper_text(
                        "* ¡Compraste [Sturdy Arm]! Se guardó en tu bolsa de equipo ([C] -> EQUIP).",
                        "SOLD",
                    )
                else:
                    new_item = {
                        "name": item["name"],
                        "heal": item["heal"],
                        "sanity_heal": item["sanity_heal"],
                        "atk_bonus": item["atk_bonus"],
                        "def_bonus": item["def_bonus"],
                        "desc": item["desc"],
                    }
                    player.inventory.append(new_item)
                    self.sound_fx.play_heal()
                    self._set_keeper_text(f"* ¡Gracias por tu compra! Guardaste [{item['name']}] en tu inventario.", "SOLD")

        elif self.state == "SELL":
            inv = player.inventory
            total_opts = len(inv) + 1
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.sub_idx = (self.sub_idx - 1) % total_opts
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.sub_idx = (self.sub_idx + 1) % total_opts
                self.sound_fx.play_select()
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self._set_keeper_text("* ¿Algo más que desees en mi Bazar del Dark World?", "WELCOME")
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                if self.sub_idx >= len(inv):
                    self.state = "MAIN"
                    self._set_keeper_text("* ¿Algo más que desees en mi Bazar del Dark World?", "WELCOME")
                    self.sound_fx.play_select()
                    return
                target_it = inv[self.sub_idx]
                if target_it.get("name") == "Sturdy Arm" or target_it.get("atk_bonus"):
                    self.sound_fx.play_hurt()
                    self._set_keeper_text("* ¡Ohoho! ¡El [Sturdy Arm] es una reliquia irremplazable, quédatelo!", "SMUG")
                    return
                sold_it = inv.pop(self.sub_idx)
                sell_val = max(6, int((sold_it.get("heal", 10) + sold_it.get("sanity_heal", 10)) * 0.4))
                player.gold += sell_val
                self.sub_idx = min(self.sub_idx, len(inv))
                self.sound_fx.play_heal()
                self._set_keeper_text(f"* ¡Trato hecho! Te doy +{sell_val} D$ por tu [{sold_it['name']}].", "SOLD")

        elif self.state == "TALK":
            total_opts = len(self.talk_topics) + 1
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.sub_idx = (self.sub_idx - 1) % total_opts
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.sub_idx = (self.sub_idx + 1) % total_opts
                self.sound_fx.play_select()
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "MAIN"
                self._set_keeper_text("* ¿En qué más puedo ayudarte, viajero?", "WELCOME")
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                if self.sub_idx >= len(self.talk_topics):
                    self.state = "MAIN"
                    self._set_keeper_text("* ¿En qué más puedo ayudarte, viajero?", "WELCOME")
                    self.sound_fx.play_select()
                    return
                _, expr, pages = self.talk_topics[self.sub_idx]
                self.talk_pages = list(pages)
                self.talk_page_idx = 0
                self.state = "TALK_DIALOGUE"
                self._set_keeper_text(self.talk_pages[0], expr)
                self.sound_fx.play_select()

        elif self.state == "TALK_DIALOGUE":
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                if self.keeper_char_idx < len(self.keeper_text):
                    self.keeper_char_idx = float(len(self.keeper_text))
                else:
                    self.talk_page_idx += 1
                    if self.talk_page_idx < len(self.talk_pages):
                        _, expr, _ = self.talk_topics[self.sub_idx]
                        self._set_keeper_text(self.talk_pages[self.talk_page_idx], expr)
                        self.sound_fx.play_select()
                    else:
                        self.state = "TALK"
                        self._set_keeper_text("* ¿Quieres preguntarme sobre algún otro secreto?", "TALK")
                        self.sound_fx.play_select()
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "TALK"
                self._set_keeper_text("* ¿Quieres preguntarme sobre algún otro secreto?", "TALK")
                self.sound_fx.play_select()

    def _draw_soul_cursor(self, surface, x, y):
        heart_rows = [
            " 11 11 ",
            "1111111",
            "1111111",
            " 11111 ",
            "  111  ",
            "   1   ",
        ]
        for r_idx, row in enumerate(heart_rows):
            for c_idx, ch in enumerate(row):
                if ch == "1":
                    surface.set_at((int(x + c_idx), int(y + r_idx)), COLOR_SOUL_RED)

    def _draw_shopkeeper_stage(self, surface, player):
        """Dibuja la mitad superior (400x158) estilo tienda de Deltarune con el Vendedor animado."""
        # 1. Fondo degradado neón del Bazar del Dark World
        for y in range(158):
            t = y / 158.0
            r = int(14 + 18 * t)
            g = int(6 + 10 * t)
            b = int(34 + 34 * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (VIRTUAL_WIDTH, y))

        # Cuadrícula en perspectiva y cortinas/estanterías del Bazar
        scroll = int(self.anim_time * 18.0) % 32
        for gx in range(-scroll, VIRTUAL_WIDTH, 32):
            pygame.draw.line(surface, (42, 22, 76), (gx, 0), (gx, 158), 1)
        for gy in range(18, 158, 28):
            pygame.draw.line(surface, (42, 22, 76), (0, gy), (VIRTUAL_WIDTH, gy), 1)

        # Partículas mágicas flotantes
        for sp in self.bg_sparkles:
            pulse = 1 + int(abs(math.sin(self.anim_time * 4.0 + sp["phase"])) * 2)
            pygame.draw.circle(surface, sp["col"], (int(sp["x"]), int(sp["y"])), pulse)

        # 2. Estanterías del fondo (Izquierda y Derecha) con frascos neón y cristales
        for shelf_x in (16, 286):
            pygame.draw.rect(surface, (22, 12, 42), (shelf_x, 18, 98, 108), border_radius=4)
            pygame.draw.rect(surface, (0, 0, 0), (shelf_x, 18, 98, 108), 3, border_radius=4)
            pygame.draw.rect(surface, (75, 235, 255), (shelf_x, 18, 98, 108), 1, border_radius=4)
            for sy in (52, 88):
                pygame.draw.line(surface, (180, 75, 215), (shelf_x + 4, sy), (shelf_x + 94, sy), 2)
            # Frascos y reliquias brillantes en los estantes
            pygame.draw.rect(surface, (90, 245, 255), (shelf_x + 16, 32, 12, 18), border_radius=3)
            pygame.draw.circle(surface, (255, 95, 210), (shelf_x + 48, 40), 8)
            pygame.draw.polygon(surface, (255, 230, 85), [(shelf_x + 76, 28), (shelf_x + 84, 48), (shelf_x + 68, 48)])
            pygame.draw.rect(surface, (255, 130, 215), (shelf_x + 22, 68, 14, 18), border_radius=2)
            pygame.draw.circle(surface, (110, 250, 170), (shelf_x + 66, 76), 9)

        # 3. Retrato Grande Animado del Vendedor del Dark World en el Centro (x=135..265)
        bob = int(math.sin(self.anim_time * 3.6) * 3)
        is_talking = self.keeper_char_idx < len(self.keeper_text) and (int(self.anim_time * 15.0) % 2 == 0)
        kx, ky = 200, 78 + bob

        # Halo detrás del vendedor
        pygame.draw.circle(surface, (46, 22, 82), (kx, ky - 4), 48)
        pygame.draw.circle(surface, (85, 240, 255), (kx, ky - 4), 48, 1)

        # Túnica / Capa de Mercader del Dark World con hombreras elegantes
        cloak_pts = [(kx - 44, ky + 54), (kx - 32, ky + 6), (kx + 32, ky + 6), (kx + 44, ky + 54)]
        pygame.draw.polygon(surface, (30, 16, 56), cloak_pts)
        pygame.draw.polygon(surface, (0, 0, 0), cloak_pts, 3)
        pygame.draw.polygon(surface, (80, 240, 255), cloak_pts, 1)
        # Cuello alto y solapas magenta
        pygame.draw.polygon(surface, (52, 22, 86), [(kx - 24, ky + 8), (kx, ky + 34), (kx + 24, ky + 8)])
        pygame.draw.lines(surface, (255, 85, 215), False, [(kx - 24, ky + 8), (kx, ky + 34), (kx + 24, ky + 8)], 2)

        # Cabeza y Sombrero / Capucha puntiaguda
        pygame.draw.circle(surface, (18, 12, 34), (kx, ky - 10), 22)
        pygame.draw.circle(surface, (85, 240, 255), (kx, ky - 10), 22, 1)
        hat_pts = [(kx - 30, ky - 22), (kx, ky - 56), (kx + 30, ky - 22)]
        pygame.draw.polygon(surface, (46, 18, 78), hat_pts)
        pygame.draw.polygon(surface, (0, 0, 0), hat_pts, 3)
        pygame.draw.polygon(surface, (255, 85, 215), hat_pts, 1)

        # Gafas Neón Asimétricas (Rosa y Amarillo al estilo Deltarune)
        glint = int(math.sin(self.anim_time * 5.0) * 3)
        left_lens = pygame.Rect(kx - 19, ky - 18, 16, 11)
        right_lens = pygame.Rect(kx + 3, ky - 18, 16, 11)
        pygame.draw.rect(surface, (255, 85, 210), left_lens, border_radius=2)
        pygame.draw.rect(surface, (255, 240, 85), right_lens, border_radius=2)
        pygame.draw.rect(surface, (255, 255, 255), left_lens, 1, border_radius=2)
        pygame.draw.rect(surface, (255, 255, 255), right_lens, 1, border_radius=2)
        pygame.draw.line(surface, (255, 255, 255), (kx - 3, ky - 13), (kx + 3, ky - 13), 2)
        # Brillo animado en los cristales
        pygame.draw.line(surface, (255, 255, 255), (left_lens.x + 3 + glint, left_lens.y + 2), (left_lens.x + 7 + glint, left_lens.bottom - 3), 2)
        pygame.draw.line(surface, (255, 255, 255), (right_lens.x + 3 + glint, right_lens.y + 2), (right_lens.x + 7 + glint, right_lens.bottom - 3), 2)

        # Sonrisa / Boca animada según expresión y tipeo de voz
        if is_talking:
            pygame.draw.rect(surface, (95, 245, 255), (kx - 8, ky - 2, 16, 6), border_radius=2)
            pygame.draw.line(surface, (18, 12, 34), (kx - 4, ky - 2), (kx - 4, ky + 4), 1)
            pygame.draw.line(surface, (18, 12, 34), (kx + 4, ky - 2), (kx + 4, ky + 4), 1)
        elif self.expression in ("EXCITED", "SOLD"):
            pygame.draw.arc(surface, (255, 240, 90), (kx - 10, ky - 6, 20, 10), math.pi, math.pi * 2, 2)
        elif self.expression == "SMUG":
            pygame.draw.line(surface, (255, 95, 215), (kx - 8, ky + 1), (kx + 9, ky - 2), 2)
        else:
            pygame.draw.arc(surface, (95, 245, 255), (kx - 9, ky - 5, 18, 8), math.pi, math.pi * 2, 2)

        # 4. Mostrador del Bazar en primer plano (y=128..158)
        pygame.draw.rect(surface, (24, 14, 44), (0, 128, VIRTUAL_WIDTH, 30))
        pygame.draw.line(surface, (0, 0, 0), (0, 128), (VIRTUAL_WIDTH, 128), 4)
        pygame.draw.line(surface, (85, 245, 255), (0, 130), (VIRTUAL_WIDTH, 130), 2)

        # Si el Sturdy Arm aún no se ha comprado, se exhibe flotando sobre un cojín de energía en el mostrador
        if not self._is_sturdy_arm_sold(player):
            ax, ay = 92, 116 - abs(bob)
            pygame.draw.ellipse(surface, (55, 22, 95), (ax - 18, 124, 36, 8))
            pygame.draw.ellipse(surface, (255, 85, 215), (ax - 18, 124, 36, 8), 1)
            pygame.draw.circle(surface, (85, 245, 255), (ax, ay), 13, 1)
            pygame.draw.rect(surface, (190, 215, 245), (ax - 10, ay - 4, 20, 8), border_radius=2)
            pygame.draw.rect(surface, (0, 0, 0), (ax - 10, ay - 4, 20, 8), 1, border_radius=2)
            pygame.draw.circle(surface, (255, 235, 85), (ax + 5, ay), 3)

    def _draw_deltarune_box(self, surface, rect, border_col=(255, 255, 255), inner_col=(75, 105, 175)):
        pygame.draw.rect(surface, (0, 0, 0), rect)
        pygame.draw.rect(surface, border_col, rect, 3)
        pygame.draw.rect(surface, inner_col, rect.inflate(-6, -6), 1)

    def draw(self, surface, player):
        if not self.active:
            return

        # 1. Escenario superior animado del Vendedor (y=0..158)
        self._draw_shopkeeper_stage(surface, player)

        # 2. Paneles inferiores estilo Deltarune (y=158..300)
        if self.state == "MAIN":
            left_box = pygame.Rect(6, 160, 254, 134)
            right_box = pygame.Rect(264, 160, 130, 134)
            self._draw_deltarune_box(surface, left_box)
            self._draw_deltarune_box(surface, right_box)

            # Texto tipeado del vendedor a la izquierda
            shown = self.keeper_text[: int(self.keeper_char_idx)]
            ty = left_box.y + 12
            for line in self.wrap_text(shown, self.font_dialogue, left_box.width - 24)[:4]:
                ts = self.font_dialogue.render(line, False, (255, 255, 255))
                surface.blit(ts, (left_box.x + 12, ty))
                ty += 18

            # Barra inferior de Oro (D$) y Espacio
            pygame.draw.line(surface, (60, 75, 120), (left_box.x + 10, left_box.bottom - 26), (left_box.right - 10, left_box.bottom - 26), 1)
            gold_s = self.font_hud.render(f"D$ {player.gold}", False, (255, 235, 85))
            spc_s = self.font_small.render(f"INV: {len(player.inventory)}/8", False, (160, 225, 255))
            surface.blit(gold_s, (left_box.x + 14, left_box.bottom - 20))
            surface.blit(spc_s, (left_box.right - 74, left_box.bottom - 19))

            # Opciones a la derecha: COMPRAR, VENDER, HABLAR, SALIR
            for i, opt in enumerate(self.main_options):
                oy = right_box.y + 16 + i * 26
                is_sel = (i == self.main_idx)
                col = (255, 240, 85) if is_sel else (255, 255, 255)
                os = self.font_hud.render(opt, False, col)
                surface.blit(os, (right_box.x + 28, oy))
                if is_sel:
                    self._draw_soul_cursor(surface, right_box.x + 12, oy + 3)

        elif self.state == "BUY":
            left_box = pygame.Rect(6, 160, 232, 134)
            right_box = pygame.Rect(242, 160, 152, 134)
            self._draw_deltarune_box(surface, left_box)
            self._draw_deltarune_box(surface, right_box, border_col=(85, 245, 255))

            # Lista de artículos a la izquierda
            for i, item in enumerate(self.catalog):
                iy = left_box.y + 10 + i * 22
                is_sel = (i == self.sub_idx)
                sold = item["unique"] and self._is_sturdy_arm_sold(player)
                if sold:
                    col = (120, 125, 145)
                    price_str = "AGOTADO"
                else:
                    col = (255, 240, 85) if is_sel else (255, 255, 255)
                    price_str = f"{item['price']} D$"
                ns = self.font_dialogue.render(item["name"], False, col)
                ps = self.font_small.render(price_str, False, (255, 215, 90) if not sold else col)
                surface.blit(ns, (left_box.x + 24, iy))
                surface.blit(ps, (left_box.right - ps.get_width() - 12, iy + 2))
                if is_sel:
                    self._draw_soul_cursor(surface, left_box.x + 10, iy + 3)

            # Opción Volver
            back_y = left_box.y + 10 + len(self.catalog) * 22
            is_back = (self.sub_idx == len(self.catalog))
            bs = self.font_dialogue.render("Volver", False, (255, 240, 85) if is_back else (190, 200, 220))
            surface.blit(bs, (left_box.x + 24, back_y))
            if is_back:
                self._draw_soul_cursor(surface, left_box.x + 10, back_y + 3)

            # Panel derecho dinámico: Descripción y vista previa de estadísticas de Paniel
            gold_hdr = self.font_hud.render(f"TU ORO: {player.gold} D$", False, (255, 235, 85))
            surface.blit(gold_hdr, (right_box.x + 10, right_box.y + 8))
            pygame.draw.line(surface, (60, 95, 150), (right_box.x + 8, right_box.y + 24), (right_box.right - 8, right_box.y + 24), 1)

            if self.sub_idx < len(self.catalog):
                sel_item = self.catalog[self.sub_idx]
                dy = right_box.y + 28
                for dl in self.wrap_text(sel_item["desc"], self.font_small, right_box.width - 18)[:4]:
                    ds = self.font_small.render(dl, False, (215, 235, 255))
                    surface.blit(ds, (right_box.x + 9, dy))
                    dy += 12

                # Comparación de estadísticas en vivo estilo Deltarune
                pygame.draw.line(surface, (60, 95, 150), (right_box.x + 8, right_box.bottom - 42), (right_box.right - 8, right_box.bottom - 42), 1)
                if sel_item["atk_bonus"] or sel_item["def_bonus"]:
                    already = self._is_sturdy_arm_sold(player)
                    equipped = getattr(player, "sturdy_arm_equipped", False)
                    cur_a = player.effective_attack
                    cur_d = player.effective_defense
                    new_a = cur_a if already else cur_a + sel_item["atk_bonus"]
                    new_d = cur_d if already else cur_d + sel_item["def_bonus"]
                    tag = "(EQUIPADO)" if equipped else "(EN BOLSA)"
                    a_txt = f"ATK: {cur_a} -> {new_a} (+{sel_item['atk_bonus']})" if not already else f"ATK: {cur_a} {tag}"
                    d_txt = f"DEF: {cur_d} -> {new_d} (+{sel_item['def_bonus']})" if not already else f"DEF: {cur_d} {tag}"
                    asurf = self.font_small.render(a_txt, False, (100, 255, 140))
                    dsurf = self.font_small.render(d_txt, False, (95, 235, 255))
                    surface.blit(asurf, (right_box.x + 10, right_box.bottom - 36))
                    surface.blit(dsurf, (right_box.x + 10, right_box.bottom - 21))
                else:
                    h_txt = f"CURA: +{sel_item['heal']} HP | +{sel_item['sanity_heal']}% MENTE"
                    hs = self.font_small.render(h_txt, False, (120, 255, 165))
                    inv_s = self.font_small.render(f"PANIEL HP: {player.hp}/{player.max_hp}", False, (255, 230, 120))
                    surface.blit(hs, (right_box.x + 10, right_box.bottom - 36))
                    surface.blit(inv_s, (right_box.x + 10, right_box.bottom - 21))
            else:
                 shown = self.keeper_text[: int(self.keeper_char_idx)]
                 dy = right_box.y + 32
                 for dl in self.wrap_text(shown, self.font_small, right_box.width - 18)[:5]:
                     ds = self.font_small.render(dl, False, (235, 235, 245))
                     surface.blit(ds, (right_box.x + 9, dy))
                     dy += 13

        elif self.state == "SELL":
            left_box = pygame.Rect(6, 160, 232, 134)
            right_box = pygame.Rect(242, 160, 152, 134)
            self._draw_deltarune_box(surface, left_box)
            self._draw_deltarune_box(surface, right_box)

            inv = player.inventory
            for i, it in enumerate(inv[:4]):
                iy = left_box.y + 10 + i * 22
                is_sel = (i == self.sub_idx)
                is_relic = (it.get("name") == "Sturdy Arm" or it.get("atk_bonus"))
                val_str = "RELIQUIA" if is_relic else f"+{max(6, int((it.get('heal', 10) + it.get('sanity_heal', 10)) * 0.4))} D$"
                col = (255, 240, 85) if is_sel else (255, 255, 255)
                ns = self.font_dialogue.render(it["name"], False, col)
                vs = self.font_small.render(val_str, False, (255, 215, 90))
                surface.blit(ns, (left_box.x + 24, iy))
                surface.blit(vs, (left_box.right - vs.get_width() - 12, iy + 2))
                if is_sel:
                    self._draw_soul_cursor(surface, left_box.x + 10, iy + 3)

            back_y = left_box.y + 10 + min(4, len(inv)) * 22
            is_back = (self.sub_idx >= len(inv))
            bs = self.font_dialogue.render("Volver", False, (255, 240, 85) if is_back else (190, 200, 220))
            surface.blit(bs, (left_box.x + 24, back_y))
            if is_back:
                self._draw_soul_cursor(surface, left_box.x + 10, back_y + 3)

            shown = self.keeper_text[: int(self.keeper_char_idx)]
            dy = right_box.y + 14
            for dl in self.wrap_text(shown, self.font_small, right_box.width - 18)[:6]:
                ds = self.font_small.render(dl, False, (235, 235, 245))
                surface.blit(ds, (right_box.x + 9, dy))
                dy += 14

        elif self.state == "TALK":
            left_box = pygame.Rect(6, 160, 232, 134)
            right_box = pygame.Rect(242, 160, 152, 134)
            self._draw_deltarune_box(surface, left_box)
            self._draw_deltarune_box(surface, right_box)

            for i, (title, _, _) in enumerate(self.talk_topics):
                iy = left_box.y + 14 + i * 24
                is_sel = (i == self.sub_idx)
                col = (255, 240, 85) if is_sel else (255, 255, 255)
                ts = self.font_dialogue.render(title, False, col)
                surface.blit(ts, (left_box.x + 24, iy))
                if is_sel:
                    self._draw_soul_cursor(surface, left_box.x + 10, iy + 3)

            back_y = left_box.y + 14 + len(self.talk_topics) * 24
            is_back = (self.sub_idx >= len(self.talk_topics))
            bs = self.font_dialogue.render("Volver", False, (255, 240, 85) if is_back else (190, 200, 220))
            surface.blit(bs, (left_box.x + 24, back_y))
            if is_back:
                self._draw_soul_cursor(surface, left_box.x + 10, back_y + 3)

            shown = self.keeper_text[: int(self.keeper_char_idx)]
            dy = right_box.y + 14
            for dl in self.wrap_text(shown, self.font_small, right_box.width - 18)[:6]:
                ds = self.font_small.render(dl, False, (215, 235, 255))
                surface.blit(ds, (right_box.x + 9, dy))
                dy += 14

        elif self.state == "TALK_DIALOGUE":
            full_box = pygame.Rect(6, 160, 388, 134)
            self._draw_deltarune_box(surface, full_box)
            shown = self.keeper_text[: int(self.keeper_char_idx)]
            dy = full_box.y + 14
            for dl in self.wrap_text(shown, self.font_dialogue, full_box.width - 28)[:4]:
                ds = self.font_dialogue.render(dl, False, (255, 255, 255))
                surface.blit(ds, (full_box.x + 14, dy))
                dy += 20
            hint_s = self.font_small.render("★ [Z / ENTER] Continuar ★", False, (255, 235, 85))
            surface.blit(hint_s, (full_box.right - hint_s.get_width() - 14, full_box.bottom - 20))



