import os
import math
import pygame
from objetos_mundo import WorldObject
from particulas import DustParticle

# ==========================================================
# SPRITES 4 DIRECCIONES (Down, Up, Left, Right)
# ==========================================================
class CharacterSpriteManager:
    """Gestiona los sprites de Paniel en 4 direcciones y según su estado emocional
    (FELIZ, TRISTE, TRAUMADO, LOCO), además de sus retratos de Estadisticas.png."""

    STATE_FOLDERS = {
        "FELIZ": "Paniel_Feliz",
        "TRISTE": "paniel_triste",
        "TRAUMADO": "Paniel_traumado",
        "LOCO": "Paniel_loco",
        "DARK_WORLD": "Paniel_Dark-World",
    }

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.frames = {"DOWN": [], "UP": [], "LEFT": [], "RIGHT": []}
        self.state_frames = {
            "FELIZ": {"DOWN": [], "UP": [], "LEFT": [], "RIGHT": []},
            "TRISTE": {"DOWN": [], "UP": [], "LEFT": [], "RIGHT": []},
            "TRAUMADO": {"DOWN": [], "UP": [], "LEFT": [], "RIGHT": []},
            "LOCO": {"DOWN": [], "UP": [], "LEFT": [], "RIGHT": []},
            "DARK_WORLD": {"DOWN": [], "UP": [], "LEFT": [], "RIGHT": []},
        }
        self.stat_portraits = {}
        self.load_or_generate_sprites()

    def _slice_paniel_sheet(self, sheet, target_w=25, target_h=45):
        """Segmenta automáticamente los 4 frames de Paniel preservando 100% el pixel art original sin bajar calidad."""
        w, h = sheet.get_size()
        col_has = [any(sheet.get_at((x, y))[3] > 0 for y in range(h)) for x in range(w)]
        islands = []
        in_island = False
        start = 0
        for x in range(w):
            if col_has[x] and not in_island:
                in_island = True
                start = x
            elif not col_has[x] and in_island:
                in_island = False
                islands.append((start, x - 1))
        if in_island:
            islands.append((start, w - 1))

        frames = []
        for sx, ex in islands:
            ys = [y for x in range(sx, ex + 1) for y in range(h) if sheet.get_at((x, y))[3] > 0]
            if not ys:
                continue
            min_y, max_y = min(ys), max(ys)
            fw = ex - sx + 1
            fh = max_y - min_y + 1
            sub = sheet.subsurface(pygame.Rect(sx, min_y, fw, fh))

            # Mantener cada pixel 1:1 original sin reescalar ni deformar
            frame_w = max(target_w, fw)
            frame_h = max(target_h, fh)
            frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)

            dest_x = (frame_w - fw) // 2
            dest_y = frame_h - fh  # Pies firmes en la base
            frame_surf.blit(sub, (dest_x, dest_y))
            frames.append(frame_surf)

        return frames

    def _load_stat_portrait(self, folder):
        """Carga y recorta el retrato en proporción 1:1 original del diseño auténtico (sin reescalar ni deformar)."""
        if not os.path.exists(folder):
            return None
        candidates = [
            f for f in os.listdir(folder)
            if "estadistica" in f.lower() and f.lower().endswith(".png")
        ]
        if not candidates:
            # Soporte para Dark World: extraer la cabeza auténtica del sprite original (Panie_dow1)
            dow_candidates = [
                f for f in os.listdir(folder)
                if any(k in f.lower() for k in ("dow1", "adelante1", "adl1", "-ad1")) and f.lower().endswith(".png")
            ]
            if not dow_candidates:
                dow_candidates = [f for f in os.listdir(folder) if "dow" in f.lower() and f.lower().endswith(".png")]
            if dow_candidates:
                path = os.path.join(folder, sorted(dow_candidates)[0])
                try:
                    sheet = pygame.image.load(path)
                    if pygame.display.get_surface():
                        sheet = sheet.convert_alpha()
                    w, h = sheet.get_size()
                    head_sub = sheet.subsurface(pygame.Rect(0, 0, w, min(h, 20))).copy()
                    xs = [x for x in range(w) for y in range(head_sub.get_height()) if head_sub.get_at((x, y))[3] > 0]
                    ys = [y for x in range(w) for y in range(head_sub.get_height()) if head_sub.get_at((x, y))[3] > 0]
                    if xs and ys:
                        min_x, max_x = min(xs), max(xs)
                        min_y, max_y = min(ys), max(ys)
                        fw = max_x - min_x + 1
                        fh = max_y - min_y + 1
                        sub = head_sub.subsurface(pygame.Rect(min_x, min_y, fw, fh)).copy()
                        box_w = max(25, fw + 2)
                        box_h = max(22, fh + 2)
                        portrait_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                        portrait_surf.blit(sub, ((box_w - fw) // 2, box_h - fh))
                        return portrait_surf
                except Exception:
                    pass
            return None

        path = os.path.join(folder, candidates[0])
        try:
            sheet = pygame.image.load(path)
            if pygame.display.get_surface():
                sheet = sheet.convert_alpha()
            w, h = sheet.get_size()
            xs = [x for x in range(w) for y in range(h) if sheet.get_at((x, y))[3] > 0]
            ys = [y for x in range(w) for y in range(h) if sheet.get_at((x, y))[3] > 0]
            if not xs or not ys:
                return None
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            fw = max_x - min_x + 1
            fh = max_y - min_y + 1
            sub = sheet.subsurface(pygame.Rect(min_x, min_y, fw, fh)).copy()

            # Mantener resolución 1:1 original intacta del diseño de Paniel
            box_w = max(25, fw + 2)
            box_h = max(22, fh + 2)
            portrait_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            dest_x = (box_w - fw) // 2
            dest_y = box_h - fh
            portrait_surf.blit(sub, (dest_x, dest_y))
            return portrait_surf
        except Exception as e:
            print(f"Aviso al cargar retrato {path}: {e}")
            return None

    def load_or_generate_sprites(self):
        # 1. Cargar sprites por estado emocional desde Paniel_Estado-masmovimientos
        estados_root = os.path.join(self.base_dir, "Paniel_Estado-masmovimientos")
        loaded_states = {}

        if os.path.exists(estados_root):
            for state_key, subfolder_name in self.STATE_FOLDERS.items():
                state_dir = os.path.join(estados_root, subfolder_name)
                if not os.path.exists(state_dir):
                    # Búsqueda insensible a mayúsculas/minúsculas por si cambia el nombre de carpeta
                    matches = [
                        d for d in os.listdir(estados_root)
                        if d.lower() == subfolder_name.lower()
                    ]
                    if matches:
                        state_dir = os.path.join(estados_root, matches[0])

                if os.path.exists(state_dir):
                    frames_dict = self._load_paniel_sprites_dict(state_dir)
                    if frames_dict:
                        loaded_states[state_key] = frames_dict
                    portrait = self._load_stat_portrait(state_dir)
                    if portrait is not None:
                        self.stat_portraits[state_key] = portrait

        # 2. Si no se encontró Paniel_Estado-masmovimientos, intentar Paniel_movimientos clásico
        if not loaded_states:
            paniel_dir = os.path.join(self.base_dir, "Paniel_movimientos")
            if not os.path.exists(paniel_dir):
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                if os.path.exists(downloads_dir):
                    paniel_dir = downloads_dir

            if os.path.exists(paniel_dir):
                base_dict = self._load_paniel_sprites_dict(paniel_dir)
                if base_dict:
                    for state_key in self.STATE_FOLDERS:
                        loaded_states[state_key] = base_dict

        if loaded_states:
            # Preservar al 100% el diseño original auténtico de los sprites y retratos de Paniel
            default_frames = loaded_states.get("FELIZ") or next(iter(loaded_states.values()))
            self.frames = default_frames
            for state_key in ("FELIZ", "TRISTE", "TRAUMADO", "LOCO", "DARK_WORLD"):
                self.state_frames[state_key] = loaded_states.get(state_key, default_frames)
            return

        # 3. Respaldo: Personajes/New Piskel.png o procedural
        if not self._load_piskel_fallback():
            self._create_undertale_hero_sprites()
        for state_key in ("FELIZ", "TRISTE", "TRAUMADO", "LOCO", "DARK_WORLD"):
            self.state_frames[state_key] = self.frames

    def get_state_sprites(self, state_key):
        return self.state_frames.get(state_key, self.frames)

    def get_sprites_for_state(self, state_key):
        return self.state_frames.get(state_key, self.frames)

    def _trim_single_frame(self, img, target_w=25, target_h=45):
        """Recorta un frame individual preservando 100% el pixel-art 1:1 original con los pies en la base."""
        w, h = img.get_size()
        xs = [x for x in range(w) for y in range(h) if img.get_at((x, y))[3] > 0]
        ys = [y for x in range(w) for y in range(h) if img.get_at((x, y))[3] > 0]
        if not xs or not ys:
            return img
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        fw = max_x - min_x + 1
        fh = max_y - min_y + 1
        sub = img.subsurface(pygame.Rect(min_x, min_y, fw, fh))
        frame_w = max(target_w, fw)
        frame_h = max(target_h, fh)
        frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame_surf.blit(sub, ((frame_w - fw) // 2, frame_h - fh))
        return frame_surf

    def _load_paniel_sprites_dict(self, folder):
        all_files = sorted([
            f for f in os.listdir(folder)
            if f.lower().endswith(".png") and "estadistica" not in f.lower()
        ])

        # Soporte para carpetas con frames individuales numerados (como Paniel_Dark-World: Panie_dow1..4, Panie_up1..4, Paniel_Drc1..4, Paniel_Izq1..4)
        multi_frame_groups = {
            "DOWN": [f for f in all_files if any(k in f.lower() for k in ("dow", "adelante", "_adl", "-ad", "_ad"))],
            "UP": [f for f in all_files if any(k in f.lower() for k in ("up", "atras"))],
            "RIGHT": [f for f in all_files if any(k in f.lower() for k in ("drc", "-dr", "_dr", "der"))],
            "LEFT": [f for f in all_files if "izq" in f.lower()],
        }
        if any(len(files) >= 2 for files in multi_frame_groups.values()):
            loaded_multi = {}
            for direction, flist in multi_frame_groups.items():
                if len(flist) >= 2:
                    dir_frames = []
                    for fname in sorted(flist)[:4]:
                        fpath = os.path.join(folder, fname)
                        try:
                            img = pygame.image.load(fpath)
                            if pygame.display.get_surface():
                                img = img.convert_alpha()
                            dir_frames.append(self._trim_single_frame(img))
                        except Exception as e:
                            print(f"Aviso al cargar frame individual {fpath}: {e}")
                    if dir_frames:
                        loaded_multi[direction] = dir_frames
            if loaded_multi:
                if "LEFT" in loaded_multi and "RIGHT" not in loaded_multi:
                    loaded_multi["RIGHT"] = [pygame.transform.flip(f, True, False) for f in loaded_multi["LEFT"]]
                elif "RIGHT" in loaded_multi and "LEFT" not in loaded_multi:
                    loaded_multi["LEFT"] = [pygame.transform.flip(f, True, False) for f in loaded_multi["RIGHT"]]
                result = {}
                for d in ["DOWN", "UP", "LEFT", "RIGHT"]:
                    result[d] = loaded_multi.get(d) or loaded_multi.get("DOWN") or next(iter(loaded_multi.values()))
                return result

        file_map = {
            "DOWN": "Paniel camina para adelante.png",
            "UP": "Paniel camina para atras.png",
            "RIGHT": "Paniel camina para la Drc.png",
            "LEFT": "Paniel camina para la Izq.png",
        }
        loaded = {}
        for direction, filename in file_map.items():
            path = os.path.join(folder, filename)
            if not os.path.exists(path):
                # Búsqueda flexible para todos los estados (adelante/adl/-ad, atras, drc/-dr/der, izq)
                candidates = []
                for f in all_files:
                    fl = f.lower()
                    if direction == "DOWN" and any(k in fl for k in ("adelante", "_adl", "-ad", "_ad")):
                        candidates.append(f)
                    elif direction == "UP" and "atras" in fl:
                        candidates.append(f)
                    elif direction == "RIGHT" and any(k in fl for k in ("drc", "-dr", "_dr", "der")):
                        candidates.append(f)
                    elif direction == "LEFT" and "izq" in fl:
                        candidates.append(f)
                if candidates:
                    path = os.path.join(folder, candidates[0])

            if os.path.exists(path):
                try:
                    sheet = pygame.image.load(path)
                    if pygame.display.get_surface():
                        sheet = sheet.convert_alpha()
                    frames = self._slice_paniel_sheet(sheet)
                    if len(frames) >= 4:
                        loaded[direction] = frames[:4]
                    elif len(frames) > 0:
                        loaded[direction] = frames
                except Exception as e:
                    print(f"Aviso al cargar {path}: {e}")

        if loaded:
            if "LEFT" in loaded and "RIGHT" not in loaded:
                loaded["RIGHT"] = [pygame.transform.flip(f, True, False) for f in loaded["LEFT"]]
            elif "RIGHT" in loaded and "LEFT" not in loaded:
                loaded["LEFT"] = [pygame.transform.flip(f, True, False) for f in loaded["RIGHT"]]

            result = {}
            for d in ["DOWN", "UP", "LEFT", "RIGHT"]:
                if d in loaded:
                    result[d] = loaded[d]
                elif "DOWN" in loaded:
                    result[d] = loaded["DOWN"]
            return result
        return None

    def _load_piskel_fallback(self):
        png_path = os.path.join(self.base_dir, "Personajes", "New Piskel.png")
        if not os.path.exists(png_path):
            return False
        try:
            sheet = pygame.image.load(png_path)
            if pygame.display.get_surface():
                sheet = sheet.convert_alpha()
            crop_box = pygame.Rect(29, 14, 25, 45)
            f0_raw = sheet.subsurface(pygame.Rect(0, 0, 64, 64)).subsurface(crop_box).copy()
            f1_raw = sheet.subsurface(pygame.Rect(64, 0, 64, 64)).subsurface(crop_box).copy()
            f2_raw = sheet.subsurface(pygame.Rect(0, 64, 64, 64)).subsurface(crop_box).copy()
            f0 = pygame.transform.scale(f0_raw, (16, 28))
            f1 = pygame.transform.scale(f1_raw, (16, 28))
            f2 = pygame.transform.scale(f2_raw, (16, 28))
            self.frames["DOWN"] = [f0, f1, f0, f2]
            self.frames["UP"] = [
                self._generate_back_frame(f0),
                self._generate_back_frame(f1),
                self._generate_back_frame(f0),
                self._generate_back_frame(f2),
            ]
            s0 = self._generate_side_frame(step=0)
            s1 = self._generate_side_frame(step=1)
            s2 = self._generate_side_frame(step=2)
            self.frames["LEFT"] = [s0, s1, s0, s2]
            self.frames["RIGHT"] = [pygame.transform.flip(f, True, False) for f in self.frames["LEFT"]]
            return True
        except Exception:
            return False

    def _generate_back_frame(self, front_surf):
        """Convierte una pose frontal en vista trasera respetando el cabello y ropa."""
        surf = front_surf.copy()
        skin = (243, 169, 139)
        hair = (42, 42, 42)
        w, h = surf.get_size()
        for y in range(h):
            for x in range(w):
                c = surf.get_at((x, y))
                # Si está en el área de la cabeza y es piel u ojos, se reemplaza por cabello
                if y < 14 and c[3] > 0 and (c[:3] == skin or c[:3] == (0, 0, 0)):
                    surf.set_at((x, y), hair)
        return surf

    def _generate_side_frame(self, step=0):
        """Crea el perfil lateral estilo Deltarune caminando a 16x28."""
        surf = pygame.Surface((16, 28), pygame.SRCALPHA)
        hair = (42, 42, 42)
        skin = (243, 169, 139)
        coat = (226, 226, 226)
        pants = (42, 42, 42)
        shoes = (15, 15, 15)

        # Cabeza y cabello
        pygame.draw.rect(surf, hair, (4, 1, 9, 9), border_radius=2)
        pygame.draw.rect(surf, skin, (3, 4, 4, 5))
        surf.set_at((4, 5), (0, 0, 0))
        pygame.draw.rect(surf, hair, (2, 2, 5, 3))

        # Torso / Abrigo
        pygame.draw.rect(surf, coat, (4, 10, 8, 10), border_radius=1)
        arm_x = 6 + (1 if step == 1 else -1 if step == 2 else 0)
        pygame.draw.rect(surf, coat, (arm_x, 11, 3, 7), border_radius=1)

        # Piernas con ciclo de caminata
        if step == 0:
            pygame.draw.rect(surf, pants, (5, 20, 3, 5))
            pygame.draw.rect(surf, pants, (8, 20, 3, 5))
            pygame.draw.rect(surf, shoes, (4, 25, 4, 3))
            pygame.draw.rect(surf, shoes, (8, 25, 4, 3))
        elif step == 1:
            pygame.draw.rect(surf, pants, (3, 20, 3, 5))
            pygame.draw.rect(surf, pants, (9, 20, 3, 5))
            pygame.draw.rect(surf, shoes, (2, 25, 4, 3))
            pygame.draw.rect(surf, shoes, (9, 24, 4, 3))
        elif step == 2:
            pygame.draw.rect(surf, pants, (8, 20, 3, 5))
            pygame.draw.rect(surf, pants, (4, 20, 3, 5))
            pygame.draw.rect(surf, shoes, (8, 25, 4, 3))
            pygame.draw.rect(surf, shoes, (3, 24, 4, 3))

        return surf

    def _create_undertale_hero_sprites(self):
        """Generador alternativo de personaje estilo Frisk / Kris a 16x28."""
        colors = {
            "hair": (70, 45, 30),
            "skin": (255, 220, 160),
            "shirt": (40, 120, 220),
            "stripe": (230, 80, 160),
            "pants": (30, 40, 90),
            "shoes": (40, 30, 20),
        }
        for d in ["DOWN", "UP", "LEFT", "RIGHT"]:
            frames = []
            for s in range(4):
                surf = pygame.Surface((16, 28), pygame.SRCALPHA)
                # Cabeza
                pygame.draw.rect(surf, colors["skin"], (4, 3, 8, 8), border_radius=2)
                pygame.draw.rect(surf, colors["hair"], (3, 1, 10, 5), border_radius=2)
                if d == "DOWN":
                    surf.set_at((5, 7), (0, 0, 0))
                    surf.set_at((10, 7), (0, 0, 0))
                elif d == "UP":
                    pygame.draw.rect(surf, colors["hair"], (4, 3, 8, 7))
                # Torso
                pygame.draw.rect(surf, colors["shirt"], (3, 11, 10, 9), border_radius=2)
                pygame.draw.rect(surf, colors["stripe"], (3, 14, 10, 2))
                # Piernas
                leg_off = 1 if s == 1 else (-1 if s == 3 else 0)
                pygame.draw.rect(surf, colors["pants"], (4 + leg_off, 20, 3, 5))
                pygame.draw.rect(surf, colors["pants"], (9 - leg_off, 20, 3, 5))
                pygame.draw.rect(surf, colors["shoes"], (3 + leg_off, 25, 4, 3))
                pygame.draw.rect(surf, colors["shoes"], (9 - leg_off, 25, 4, 3))
                frames.append(surf)
            self.frames[d] = frames



# ==========================================================
# JUGADOR (Con movimiento 4 direcciones y sprint Deltarune)
# ==========================================================
class Player(WorldObject):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, depth_y=y + 44)
        self.sprite_manager = sprite_manager
        self._default_sprites = sprite_manager.frames
        self.state_sprites = getattr(sprite_manager, "state_frames", {})
        self.stat_portraits = getattr(sprite_manager, "stat_portraits", {})
        self.w = 25
        self.h = 45

        # Velocidades (Virtual pixels / seg) originales y fluidas
        self.walk_speed = 95.0
        self.run_speed = 165.0   # Mecánica de correr de Deltarune [X / LSHIFT]

        self.facing = "DOWN"
        self.is_moving = False
        self.is_running = False

        self.anim_timer = 0.0
        self.frame_idx = 0

        # Hitbox centrada en los pies (14x8) para permitir perspectiva 2.5D y cruzar el vano de la puerta
        self.hitbox_w = 14
        self.hitbox_h = 8
        self.particles = []
        self.step_timer = 0.0

        # Estadísticas de combate y nivel (máximo nivel 18)
        self.lv = 1
        self.max_lv = 18
        self.exp = 0
        self.max_hp = 20
        self.hp = 20
        self.attack = 10
        self.defense = 2
        self.gold = 0
        self.weapon = "Vara de Roble"
        self.armor = "Capa Gris"

        # Sistema de Equipamiento estilo Deltarune (Ranura de Arma + 2 Ranuras de Armadura/Reliquia)
        self.equipped_weapon = {
            "name": "Vara de Roble",
            "slot": "WEAPON",
            "atk_bonus": 0,
            "def_bonus": 0,
            "desc": "Bastón de roble equilibrado. Arma inicial de Paniel (+0 ATK).",
        }
        self.equipped_armor_1 = {
            "name": "Capa Gris",
            "slot": "ARMOR",
            "atk_bonus": 0,
            "def_bonus": 0,
            "desc": "Capa ligera contra el viento nocturno del cementerio (+0 DEF).",
        }
        self.equipped_armor_2 = {
            "name": "Cinta Ánima",
            "slot": "ARMOR",
            "atk_bonus": 0,
            "def_bonus": 0,
            "desc": "Cinta protectora tejida con hilos de determinación (+0 DEF).",
        }
        self.equipment_bag = [
            dict(self.equipped_weapon),
            {
                "name": "Hoja de Ánima",
                "slot": "WEAPON",
                "atk_bonus": 3,
                "def_bonus": 1,
                "desc": "Espada corta espiritual que vibra con TP. Incrementa +3 ATK y +1 DEF.",
            },
            dict(self.equipped_armor_1),
            dict(self.equipped_armor_2),
            {
                "name": "Coraza Rúnica",
                "slot": "ARMOR",
                "atk_bonus": 0,
                "def_bonus": 3,
                "desc": "Peto grabado con la Runa Delta. Incrementa +3 de Defensa.",
            },
            {
                "name": "Anillo Carmesí",
                "slot": "ARMOR",
                "atk_bonus": 2,
                "def_bonus": 2,
                "desc": "Reliquia del cementerio antiguo. Incrementa +2 de Ataque y +2 de Defensa.",
            },
        ]

        self.inventory = [
            {"name": "Caramelo Oscuro", "heal": 10, "sanity_heal": 5, "desc": "Restaura 10 HP y 5% cordura con sabor a mora."},
            {"name": "Tarta de Caramelo", "heal": 20, "sanity_heal": 15, "desc": "Restaura todo el HP con amor maternal."},
            {"name": "Tónico de Menta", "heal": 8, "sanity_heal": 35, "desc": "Infusión fría. Restaura 8 HP y calma la mente (+35% cordura)."},
        ]
        self.on_step_callback = None

        # Sistema de Cordura / Locura y Consciencia de Muertes
        self.sanity = 100.0   # 0.0 (Locura total) a 100.0 (Plena cordura / Feliz)
        self.death_count = 0  # Contador de muertes del que Paniel es plenamente consciente
        self.last_death_acknowledged = 0
        self.in_dark_world = False

    @property
    def mental_state(self):
        """Retorna el estado psicológico de Paniel según su nivel de cordura."""
        if self.sanity >= 75.0:
            return "FELIZ"
        elif self.sanity >= 45.0:
            return "TRISTE"
        elif self.sanity >= 20.0:
            return "TRAUMADO"
        else:
            return "LOCO"

    @property
    def sprites(self):
        """Retorna automáticamente los diseños de Paniel_Dark-World al estar en el Dark World, o los de su estado mental."""
        if getattr(self, "in_dark_world", False) and "DARK_WORLD" in self.state_sprites and self.state_sprites["DARK_WORLD"].get("DOWN"):
            return self.state_sprites["DARK_WORLD"]
        state = self.mental_state
        if state in self.state_sprites and self.state_sprites[state].get("DOWN"):
            return self.state_sprites[state]
        return self._default_sprites

    def get_stat_portrait(self):
        """Retorna el retrato de Estadisticas.png correspondiente al estado mental actual (o Dark World)."""
        if getattr(self, "in_dark_world", False) and "DARK_WORLD" in self.stat_portraits:
            return self.stat_portraits["DARK_WORLD"]
        return self.stat_portraits.get(self.mental_state)

    @property
    def effective_attack(self):
        """Ataque modificado por el estado emocional de Paniel."""
        state = self.mental_state
        base = self.attack
        if state == "FELIZ":
            return base
        elif state == "TRISTE":
            return max(1, base - 3)
        elif state == "TRAUMADO":
            return max(1, base - 2)
        elif state == "LOCO":
            return base + 8

    @property
    def effective_defense(self):
        """Defensa modificada por el estado emocional de Paniel."""
        state = self.mental_state
        base = self.defense
        if state == "FELIZ":
            return base
        elif state == "TRISTE":
            return base + 2
        elif state == "TRAUMADO":
            return max(0, base - 3)
        elif state == "LOCO":
            return max(0, base - 4)

    @property
    def effective_walk_speed(self):
        state = self.mental_state
        if state == "TRISTE":
            return max(50.0, self.walk_speed - 14.0)
        elif state == "LOCO":
            return self.walk_speed + 20.0
        return self.walk_speed

    @property
    def effective_run_speed(self):
        state = self.mental_state
        if state == "TRISTE":
            return max(80.0, self.run_speed - 18.0)
        elif state == "LOCO":
            return self.run_speed + 28.0
        return self.run_speed

    def sync_equipment_bag(self):
        """Sincroniza cualquier arma/armadura del inventario general hacia la bolsa de equipamiento."""
        known_names = {g["name"] for g in self.equipment_bag}
        for it in self.inventory:
            if (it.get("atk_bonus") or it.get("def_bonus") or it.get("slot")) and it["name"] not in known_names:
                slot = it.get("slot", "BOTH" if it["name"] == "Sturdy Arm" else ("WEAPON" if it.get("atk_bonus", 0) >= it.get("def_bonus", 0) else "ARMOR"))
                self.equipment_bag.append({
                    "name": it["name"],
                    "slot": slot,
                    "atk_bonus": it.get("atk_bonus", 0),
                    "def_bonus": it.get("def_bonus", 0),
                    "desc": it.get("desc", ""),
                })
                known_names.add(it["name"])
        if getattr(self, "sturdy_arm_equipped", False) and "Sturdy Arm" not in known_names:
            sturdy = {
                "name": "Sturdy Arm",
                "slot": "BOTH",
                "atk_bonus": 5,
                "def_bonus": 10,
                "desc": "¿Refuerzo robótico o mágico? de brazo. Incrementa +5 de Ataque y +10 de Defensa.",
            }
            self.equipment_bag.append(sturdy)

    def add_equipment(self, gear_item):
        """Añade una pieza de equipo a la bolsa sin equiparla automáticamente ni duplicarla."""
        self.sync_equipment_bag()
        if all(g["name"] != gear_item["name"] for g in self.equipment_bag):
            self.equipment_bag.append(dict(gear_item))
            return True
        return False

    def get_slot_gear(self, slot_idx):
        if slot_idx == 0:
            return self.equipped_weapon
        elif slot_idx == 1:
            return self.equipped_armor_1
        return self.equipped_armor_2

    def get_candidates_for_slot(self, slot_idx):
        """Retorna las armas (slot_idx=0) o armaduras/reliquias (slot_idx=1,2) disponibles para equipar.
        Impide equipar el mismo objeto (incluido Sturdy Arm) en más de una ranura a la vez."""
        self.sync_equipment_bag()
        want = "WEAPON" if slot_idx == 0 else "ARMOR"
        other_equipped_names = {
            self.get_slot_gear(i)["name"]
            for i in range(3)
            if i != slot_idx and self.get_slot_gear(i)
        }
        candidates = []
        for g in self.equipment_bag:
            if g.get("slot") in (want, "BOTH"):
                if g["name"] in other_equipped_names:
                    continue
                candidates.append(g)
        return candidates

    def equip_in_slot(self, slot_idx, gear_item):
        """Equipa un arma o armadura en la ranura indicada (0: Arma, 1: Armadura 1, 2: Armadura 2) y actualiza ATK y DEF.
        Retorna False si el objeto ya está equipado en otra ranura para evitar duplicados."""
        self.sync_equipment_bag()
        if all(g["name"] != gear_item["name"] for g in self.equipment_bag):
            self.equipment_bag.append(dict(gear_item))

        # Bloquear cualquier intento de equipar la misma pieza en más de una ranura a la vez
        for i in range(3):
            if i != slot_idx:
                other = self.get_slot_gear(i)
                if other and other.get("name") == gear_item["name"]:
                    return False

        old_gear = self.get_slot_gear(slot_idx)
        if old_gear and old_gear.get("name") == gear_item["name"]:
            return True

        old_atk = old_gear.get("atk_bonus", 0) if old_gear else 0
        old_def = old_gear.get("def_bonus", 0) if old_gear else 0

        new_atk = gear_item.get("atk_bonus", 0)
        new_def = gear_item.get("def_bonus", 0)

        self.attack = max(1, self.attack - old_atk + new_atk)
        self.defense = max(0, self.defense - old_def + new_def)

        if slot_idx == 0:
            self.equipped_weapon = dict(gear_item)
        elif slot_idx == 1:
            self.equipped_armor_1 = dict(gear_item)
        else:
            self.equipped_armor_2 = dict(gear_item)

        self.sturdy_arm_equipped = any(
            s and s.get("name") == "Sturdy Arm"
            for s in (self.equipped_weapon, self.equipped_armor_1, self.equipped_armor_2)
        )

        self.weapon = self.equipped_weapon["name"] if self.equipped_weapon else "Ninguna"
        a1 = self.equipped_armor_1["name"] if self.equipped_armor_1 else "Ninguna"
        a2 = self.equipped_armor_2["name"] if self.equipped_armor_2 else ""
        self.armor = f"{a1} / {a2}" if a2 else a1
        return True

    def modify_sanity(self, delta):
        """Aumenta o reduce la cordura asegurando límites entre 0 y 100."""
        self.sanity = max(0.0, min(100.0, self.sanity + delta))

    def exp_for_next_level(self):
        """Retorna la experiencia total requerida para el siguiente nivel hasta LV 18."""
        if self.lv >= self.max_lv:
            return 999999
        return self.lv * 20 + (self.lv ** 2) * 5

    def add_exp(self, amount):
        """Añade experiencia y procesa la subida de nivel hasta el máximo de 18."""
        if self.lv >= self.max_lv:
            return False, 0
        self.exp += amount
        leveled_up = False
        levels_gained = 0
        while self.lv < self.max_lv and self.exp >= self.exp_for_next_level():
            self.lv += 1
            levels_gained += 1
            leveled_up = True
            self.max_hp += 4
            self.attack += 2
            if self.lv % 2 == 0:
                self.defense += 1
            self.hp = self.max_hp

        return leveled_up, levels_gained

    @property
    def hitbox(self):
        """Rectángulo de colisión exacto en la base de los pies."""
        return pygame.Rect(
            int(self.x + (self.w - self.hitbox_w) / 2),
            int(self.y + self.h - self.hitbox_h - 1),
            self.hitbox_w,
            self.hitbox_h,
        )

    def handle_input_and_move(self, dt, solid_rects, is_void_func=None, disabled=False):
        if disabled:
            self.is_moving = False
            self.frame_idx = 0
            return

        keys = pygame.key.get_pressed()
        dx = 0.0
        dy = 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1.0

        self.is_running = (keys[pygame.K_x] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        current_speed = self.effective_run_speed if self.is_running else self.effective_walk_speed

        self.is_moving = (dx != 0.0 or dy != 0.0)

        if self.is_moving:
            if abs(dy) >= abs(dx):
                self.facing = "UP" if dy < 0 else "DOWN"
            else:
                self.facing = "LEFT" if dx < 0 else "RIGHT"

            dist = math.hypot(dx, dy)
            dx = (dx / dist) * current_speed * dt
            dy = (dy / dist) * current_speed * dt

            # Movimiento en eje X
            self.x += dx
            r_x = self.hitbox
            for solid in solid_rects:
                if r_x.colliderect(solid):
                    if dx > 0:
                        self.x = solid.left - self.hitbox_w - (self.w - self.hitbox_w) / 2
                    elif dx < 0:
                        self.x = solid.right - (self.w - self.hitbox_w) / 2
                    break

            # Movimiento en eje Y
            self.y += dy
            r_y = self.hitbox
            for solid in solid_rects:
                if r_y.colliderect(solid):
                    if dy > 0:
                        self.y = solid.top - self.h + 1
                    elif dy < 0:
                        self.y = solid.bottom - (self.h - self.hitbox_h - 1)
                    break

            self.depth_y = self.y + self.h - 1

            # Animación de fotogramas
            anim_rate = 0.11 if self.is_running else 0.17
            self.anim_timer += dt
            if self.anim_timer >= anim_rate:
                self.anim_timer = 0.0
                self.frame_idx = (self.frame_idx + 1) % len(self.sprites[self.facing])
                if self.frame_idx in [1, 3] and self.on_step_callback:
                    self.on_step_callback()

            # Partículas de pisadas
            dust_interval = 0.09 if self.is_running else 0.22
            self.step_timer += dt
            if self.step_timer >= dust_interval:
                self.step_timer = 0.0
                foot_x = self.x + self.w / 2
                foot_y = self.y + self.h - 1
                self.particles.append(DustParticle(foot_x, foot_y))
        else:
            self.frame_idx = 0
            self.anim_timer = 0.0

        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)

        cx, cy = camera.apply((self.x, self.y))

        # Sombra suave bajo los pies (estilo Undertale/Deltarune)
        shadow_w = 18
        shadow_h = 6
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 95), (0, 0, shadow_w, shadow_h))
        surface.blit(shadow_surf, (cx + (self.w - shadow_w) // 2, cy + self.h - 4))

        # Sprite animado a resolución 1:1 original nítida según el estado emocional actual
        dir_frames = self.sprites[self.facing]
        current_frame = dir_frames[self.frame_idx % len(dir_frames)]
        surface.blit(current_frame, (cx, cy))

