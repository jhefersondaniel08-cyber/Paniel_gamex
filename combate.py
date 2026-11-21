import math
import random
import pygame
from configuracion import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_SOUL_RED, COLOR_SOUL_GREEN
from enemigos import ENEMY_TEMPLATES, DeltaruneEnemyRenderer
from proyectiles import (
    ShadowRainBullet,
    ShadowSpiralBullet,
    DiamondSwordBullet,
    CrossfireDiamondBullet,
    BouncingNoteBullet,
    SoundArcBullet,
    ScytheWaveBullet,
    LanternFlameBullet,
    GravePillarBullet,
    CultDaggerBullet,
    RitualSigilBullet,
    DarkFlameBullet,
    ShatterCrystalBullet,
    VoidCleaveBullet,
    BoomerangScytheBullet,
    ErraticWispBullet,
    FuneralBellShockwave,
    ChaosBouncingScythe,
    HomingSoulOrb,
    DarkGravityVortexBullet,
    LaserCrossGridBullet,
    FracturedMirrorShards,
)

# ==========================================================
# SISTEMA INTEGRAL DE COMBATE ESTILO DELTARUNE
# ==========================================================
class DeltaruneBattle:
    """Gestiona el combate estilo Deltarune:
    - Paniel en el lado izquierdo del campo de batalla (con su sprite según estado emocional)
    - Enemigo en el lado derecho con barras de HP y MERCY (%)
    - Arena de esquiva (Bullet Box) situada ENTRE Paniel y el enemigo, POR ENCIMA de la barra de vida
    - Cuadrícula neón animada estilo Dark World
    - Barra de TP (Tension Points) con habilidades especiales de TP y halo de Graze en el alma
    - Barra de precisión de ataque estilo Deltarune y números flotantes de daño / piedad
    """
    def __init__(self, player, template_id, sound_fx, font_hud, font_dialogue, on_finish_callback):
        self.player = player
        self.template_id = template_id
        self.template = ENEMY_TEMPLATES[template_id]

        # Escalado dinámico de dificultad según el Nivel (LV) actual de Paniel
        self.lv_bonus = max(0, self.player.lv - 1)
        is_boss = self.template.get("is_boss", False)
        hp_scale = 1.0 + self.lv_bonus * (0.22 if is_boss else 0.20)
        scaled_hp = int(round(self.template["max_hp"] * hp_scale)) + self.lv_bonus * (8 if is_boss else 4)
        scaled_atk = self.template["attack"] + int(round(self.lv_bonus * 1.8))
        scaled_def = self.template["defense"] + int(round(self.lv_bonus * 0.8))
        scaled_exp = int(round(self.template.get("exp", 25) * (1.0 + self.lv_bonus * 0.14)))

        # Multiplicadores de cadencia y velocidad de proyectiles según el LV de Paniel
        self.diff_mult = 1.0 + min(1.25, self.lv_bonus * 0.10)
        self.spd_mult = 1.0 + min(0.65, self.lv_bonus * 0.05)

        # Clonar ACTs y actualizar Examinar con las estadísticas reales escaladas
        scaled_acts = []
        for a in self.template["acts"]:
            act_copy = dict(a)
            if act_copy["name"] == "Examinar" and self.lv_bonus > 0:
                act_copy["text"] = (
                    f"* {self.template['name'].upper()} [NV+{self.lv_bonus}] - ATK {scaled_atk} DEF {scaled_def}\n"
                    f"* Su poder aumentó con tu nivel (HP {scaled_hp})."
                )
            scaled_acts.append(act_copy)

        self.enemy = {
            "id": self.template["id"],
            "name": self.template["name"],
            "hp": scaled_hp,
            "max_hp": scaled_hp,
            "attack": scaled_atk,
            "defense": scaled_def,
            "exp": scaled_exp,
            "mercy": 0,
            "acts": scaled_acts,
            "quotes": self.template["quotes"],
            "patterns": self.template["patterns"],
        }
        self.sound_fx = sound_fx
        self.font_hud = font_hud
        self.font_dialogue = font_dialogue
        self.on_finish_callback = on_finish_callback

        # Estados: INTRO, MENU, SUBMENU_ACT, SUBMENU_ITEM, ATTACK_METER, SLASH_ANIM, ACTION_TEXT, ENEMY_TURN, VICTORY, SPARE_VICTORY, GAME_OVER
        self.state = "INTRO"
        self.intro_timer = 0.45

        # Barra TP (Tension Points) Deltarune [0 - 100%] (Inicia en 0% TP; se gana rozando balas / Graze y con Defensa)
        self.tp = 0.0
        self.display_tp = 0.0

        # Estado y efectos visuales de la habilidad mágica BlackFlash (50% TP, 15% prob, +20% daño, 2 golpes)
        self.black_flash_chance = 0.15
        self.black_flash_casts = 0
        self.black_flash_state = None
        self.black_flash_flames = []
        self.black_flash_bolts = []
        self.crystal_cracks = []
        self.crystal_shards = []

        # Botones de acción principales de Deltarune
        self.btn_names = ["FIGHT", "ACT", "ITEM", "SPARE", "DEFEND"]
        self.btn_colors = [
            (255, 110, 65),   # FIGHT (Naranja/Rojo espada)
            (70, 220, 255),   # ACT / MAGIC (Cian)
            (95, 240, 115),   # ITEM (Verde)
            (255, 230, 65),   # SPARE (Amarillo)
            (110, 165, 255),  # DEFEND (Azul escudo)
        ]
        self.selected_btn = 0
        self.submenu_idx = 0

        # Posiciones base del escenario:
        # En modo MENÚ: barra de vida en y=148, caja de texto en y=174, botones en y=250.
        # En modo PELEA (ENEMY_TURN): la barra de vida y los botones bajan hasta el borde inferior
        # (card_y=240, btn_y=268) dejando una arena de pelea mucho más grande (176x168) en el centro.
        self.ui_slide = 0.0  # 0.0 = Posición de menú, 1.0 = Barra de acciones abajo para ver mejor la pelea

        self.hero_base_x = 46.0
        self.hero_base_y = 62.0
        self.hero_lunge_x = 0.0
        self.hero_hurt_flash = 0.0
        self.rude_buster_beam = None  # Efecto de proyectil mágico TP

        self.enemy_base_x = 340
        self.enemy_base_y = 76

        # Caja inferior de diálogo/submenús (en modo menú) y Arena central ampliada (en modo pelea)
        self.default_box = pygame.Rect(20, 174, 360, 72)
        self.bullet_box = pygame.Rect(102, 52, 176, 168)
        self.cur_box = [
            float(self.bullet_box.centerx - 16),
            float(self.bullet_box.centery - 16),
            32.0,
            32.0,
        ]

        # Alma roja del jugador en la fase de esquiva
        self.soul_x = float(self.bullet_box.centerx)
        self.soul_y = float(self.bullet_box.centery)
        self.soul_speed_normal = 112.0
        self.soul_speed_focus = 56.0  # Mantener [Shift] o [X] para modo precisión
        self.invulnerable_timer = 0.0
        self.graze_flash_timer = 0.0
        self.graze_sparks = []
        self.graze_echoes = []
        self._init_soul_silhouette_surfaces()

        # Sistema de Parry (Alma Verde con [Z], duración 0.32s, cooldown 5 segundos)
        self.parry_active_timer = 0.0
        self.parry_cooldown = 0.0
        self.parry_sparks = []
        self.parry_floating_txt = None
        self.parry_floating_pos = [0.0, 0.0]
        self.parry_floating_life = 0.0

        # Barra de Ataque interactiva estilo Deltarune (dentro de default_box)
        self.meter_rect = pygame.Rect(36, 186, 328, 48)
        self.target_x = self.meter_rect.left + 44
        self.cursor_x = float(self.meter_rect.right - 10)
        self.cursor_speed = 290.0 + min(110.0, self.lv_bonus * 8.0)
        self.attack_hit = False
        self.attack_rating = ""
        self.afterimages = []

        # Animación de golpe y números flotantes (Daño y +Mercy%)
        self.slash_timer = 0.0
        self.floating_dmg = None
        self.floating_dmg_color = (255, 255, 255)
        self.floating_dmg_pos = [0.0, 0.0]
        self.floating_dmg_vy = 0.0
        self.enemy_hit_flash = 0.0

        # Texto informativo
        self.action_message = self.template["intro_text"]
        self.speech_bubble_text = ""
        self.speech_bubble_timer = 0.0

        # Temporizador y balas del turno enemigo (más largo e intenso al subir de nivel)
        self.turn_timer = 0.0
        self.turn_duration = 5.4 + min(2.2, self.lv_bonus * 0.18)
        self.bullets = []
        self.bullet_spawn_timer = 0.0
        self.turn_prep_timer = 0.0
        self.current_pattern = None

        self.defending = False
        self.screen_shake = 0.0
        self.anim_time = 0.0
        self.grid_scroll = 0.0

        # Partículas ambientales de fondo estilo Dark World
        self.bg_squares = [
            {
                "x": random.uniform(0, VIRTUAL_WIDTH),
                "y": random.uniform(0, 142),
                "speed": random.uniform(12, 32),
                "size": random.choice([3, 5, 7]),
                "phase": random.uniform(0, math.pi * 2),
            }
            for _ in range(22)
        ]

        # Secuencia Game Over
        self.game_over_timer = 0.0
        self.soul_shards = []

    def wrap_text(self, text, font, max_width):
        """Envuelve texto respetando saltos de línea para que jamás desborde la caja de batalla."""
        lines = []
        for paragraph in text.split("\n"):
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

    def _get_act_options(self):
        """Combina las opciones ACT del enemigo con las habilidades mágicas de TP (incluyendo BlackFlash)."""
        base_acts = list(self.enemy["acts"])
        tp_skills = [
            {
                "name": "★ BlackFlash (50%TP)",
                "tp_cost": 50,
                "type": "TP_BLACK_FLASH",
                "hit_chance": 0.15,
                "damage_mult": 1.20,
                "hits": 2,
                "mercy": 0,
                "text": "",
            },
            {
                "name": "★ Tajo Ánima (35%TP)",
                "tp_cost": 35,
                "type": "TP_ATTACK",
                "mercy": 0,
                "text": "",
            },
            {
                "name": "★ Calma Mental(25%TP)",
                "tp_cost": 25,
                "type": "TP_HEAL",
                "mercy": 0,
                "text": "",
            },
            {
                "name": "★ Pacificar (40%TP)",
                "tp_cost": 40,
                "type": "TP_PACIFY",
                "mercy": 65,
                "text": "",
            },
        ]
        return base_acts + tp_skills

    def _spawn_black_flash_vfx(self, ex, ey, shatter_burst=False):
        """Genera los destellos de Fuego Oscuro con borde negro y el efecto de romper un cristal."""
        # 1. Llamas de Fuego Oscuro con borde negro alrededor del punto de impacto
        for _ in range(18 if shatter_burst else 14):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(35, 135 if shatter_burst else 95)
            self.black_flash_flames.append({
                "x": float(ex + random.uniform(-10, 10)),
                "y": float(ey + random.uniform(-14, 14)),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - random.uniform(15, 45),
                "size": random.uniform(8.0, 15.0),
                "life": random.uniform(0.45, 0.85),
                "max_life": 0.85,
                "phase": random.uniform(0, math.pi * 2),
            })

        # 2. Relámpagos quebrados de Fuego Oscuro con borde negro
        self.black_flash_bolts.clear()
        for i in range(8):
            base_ang = i * (math.pi / 4.0) + random.uniform(-0.22, 0.22)
            pts = [(ex, ey)]
            cx, cy = float(ex), float(ey)
            for step in range(1, 5):
                r = step * random.uniform(14, 24)
                jitter = random.uniform(-0.35, 0.35)
                cx = ex + math.cos(base_ang + jitter) * r
                cy = ey + math.sin(base_ang + jitter) * r
                pts.append((int(cx), int(cy)))
            self.black_flash_bolts.append(pts)

        # 3. Grietas radiales como rompiendo un cristal
        if not shatter_burst:
            self.crystal_cracks.clear()
            for i in range(10):
                ang = i * (math.pi / 5.0) + random.uniform(-0.18, 0.18)
                crack_pts = [(ex, ey)]
                for seg in range(1, 5):
                    dist = seg * random.uniform(16, 28)
                    a_off = ang + random.uniform(-0.25, 0.25)
                    crack_pts.append((int(ex + math.cos(a_off) * dist), int(ey + math.sin(a_off) * dist)))
                self.crystal_cracks.append(crack_pts)

        # 4. Esquirlas poligonales de cristal roto con borde negro saliendo disparadas
        for _ in range(24 if shatter_burst else 12):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(55, 175 if shatter_burst else 110)
            self.crystal_shards.append({
                "x": float(ex + random.uniform(-12, 12)),
                "y": float(ey + random.uniform(-12, 12)),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 20.0,
                "angle": random.uniform(0, math.pi * 2),
                "v_ang": random.uniform(-12.0, 12.0),
                "radius": random.uniform(5.0, 11.0),
                "life": random.uniform(0.55, 0.95),
            })

    def _trigger_black_flash(self, from_crit=False):
        """Ejecuta la habilidad mágica BlackFlash:
        - Cuesta 50 TP
        - 15% de probabilidad de acertar (garantizado en el primer uso de la batalla para demostración inmediata)
        - Cada golpe es 20% más fuerte que un ataque normal (x1.20)
        - Impacta DOS VECES (2 golpes consecutivos) rompiendo un cristal con Fuego Oscuro de borde negro.
        """
        ex, ey = int(self.enemy_base_x), int(self.enemy_base_y)
        self.black_flash_flames.clear()
        self.crystal_shards.clear()
        self._spawn_black_flash_vfx(ex, ey, shatter_burst=False)

        # Probabilidad del 15% (0.15) en acertar la habilidad (1er intento de la batalla acierta para poder verla de inmediato)
        landed = from_crit or (self.black_flash_casts == 0) or (random.random() < self.black_flash_chance)
        self.black_flash_casts += 1

        # Daño base de un ataque normal completo (mult 1.55) aumentado en un +20% (x1.20)
        normal_atk_dmg = max(6, (self.player.effective_attack * 1.55) - self.enemy["defense"])
        hit_dmg_1 = max(8, int(round(normal_atk_dmg * 1.20 + random.uniform(0.0, 1.5))))
        hit_dmg_2 = max(8, int(round(normal_atk_dmg * 1.20 + random.uniform(0.5, 2.5))))

        self.hero_lunge_x = 32.0
        self.rude_buster_beam = None

        if landed:
            self.sound_fx.play_crit()
            self.sound_fx.play_slash()
            # Primer impacto inmediato
            self.enemy["hp"] = max(0, self.enemy["hp"] - hit_dmg_1)
            self.enemy_hit_flash = 0.95
            self.screen_shake = 8.5
            self.slash_timer = 1.15
            self.black_flash_state = {
                "landed": True,
                "hit1_dmg": hit_dmg_1,
                "hit2_dmg": hit_dmg_2,
                "hit2_done": False,
            }
            self.attack_rating = f"¡¡BLACK FLASH x2!! ({hit_dmg_1}+{hit_dmg_2})"
            self.floating_dmg = f"¡IMPACTO 1! {hit_dmg_1}"
            self.floating_dmg_color = (255, 45, 95)
            self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 28)]
            self.floating_dmg_vy = -78.0
        else:
            # Si falla el 15%, aún muestra los destellos de fuego oscuro y cristal agrietado
            self.sound_fx.play_shatter()
            self.screen_shake = 5.0
            self.slash_timer = 0.75
            self.black_flash_state = {
                "landed": False,
                "hit1_dmg": 0,
                "hit2_dmg": 0,
                "hit2_done": True,
            }
            self.attack_rating = "BLACK FLASH FALLÓ (15% PROB.)"
            self.floating_dmg = "FALLO (15%)"
            self.floating_dmg_color = (195, 140, 220)
            self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 26)]
            self.floating_dmg_vy = -65.0

        self.state = "SLASH_ANIM"

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "MENU":
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.selected_btn = (self.selected_btn - 1) % 5
                self.sound_fx.play_select()
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.selected_btn = (self.selected_btn + 1) % 5
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self._choose_menu_action()

        elif self.state == "SUBMENU_ACT":
            acts = self._get_act_options()
            if event.key in [pygame.K_UP, pygame.K_w]:
                if self.submenu_idx >= 2:
                    self.submenu_idx -= 2
                    self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                if self.submenu_idx + 2 < len(acts):
                    self.submenu_idx += 2
                    self.sound_fx.play_select()
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                if self.submenu_idx % 2 == 1:
                    self.submenu_idx -= 1
                    self.sound_fx.play_select()
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                if self.submenu_idx % 2 == 0 and self.submenu_idx + 1 < len(acts):
                    self.submenu_idx += 1
                    self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                act = acts[self.submenu_idx]
                tp_cost = act.get("tp_cost", 0)
                if tp_cost > 0 and self.tp < tp_cost:
                    self.sound_fx.play_blip()
                    return

                if tp_cost > 0:
                    self.tp = max(0.0, self.tp - tp_cost)

                act_type = act.get("type", "NORMAL")
                if act_type == "TP_BLACK_FLASH":
                    self._trigger_black_flash(from_crit=False)
                    return

                elif act_type == "TP_ATTACK":
                    self.black_flash_state = None
                    self.sound_fx.play_crit()
                    self.sound_fx.play_slash()
                    dmg = max(12, int(self.player.effective_attack * 2.2 - self.enemy["defense"]))
                    self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
                    self.enemy_hit_flash = 0.55
                    self.slash_timer = 0.65
                    self.hero_lunge_x = 26.0
                    self.rude_buster_beam = {"progress": 0.0}
                    self.attack_rating = "¡¡TAJO ÁNIMA!!"
                    self.floating_dmg = f"{dmg}"
                    self.floating_dmg_color = (255, 110, 240)
                    self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 25)]
                    self.floating_dmg_vy = -70.0
                    self.state = "SLASH_ANIM"
                    return

                elif act_type == "TP_HEAL":
                    self.sound_fx.play_heal()
                    self.player.hp = min(self.player.max_hp, self.player.hp + 12)
                    self.player.modify_sanity(25.0)
                    self.action_message = (
                        "* ¡Paniel canalizó su TP en una Calma Mental!\n"
                        f"* ¡Recuperó +12 HP ({self.player.hp}/{self.player.max_hp}) y +25% de Cordura!"
                    )
                    self.state = "ACTION_TEXT"
                    return

                elif act_type == "TP_PACIFY":
                    self.sound_fx.play_spare()
                    self.enemy["mercy"] = min(100, self.enemy["mercy"] + act["mercy"])
                    self.floating_dmg = f"+{act['mercy']}% MERCY"
                    self.floating_dmg_color = (255, 235, 70)
                    self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 25)]
                    self.floating_dmg_vy = -55.0
                    self.action_message = (
                        f"* ¡Paniel lanzó el hechizo PACIFICAR sobre {self.enemy['name']}!\n"
                        f"* ¡El espíritu del enemigo se serenó (+{act['mercy']}% Piedad)!"
                    )
                    self.state = "ACTION_TEXT"
                    return

                if act["mercy"] > 0:
                    self.enemy["mercy"] = min(100, self.enemy["mercy"] + act["mercy"])
                    self.sound_fx.play_spare()
                    self.floating_dmg = f"+{act['mercy']}% MERCY"
                    self.floating_dmg_color = (255, 235, 70)
                    self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 25)]
                    self.floating_dmg_vy = -55.0
                else:
                    self.sound_fx.play_select()
                self.action_message = act["text"]
                self.state = "ACTION_TEXT"
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "MENU"

        elif self.state == "SUBMENU_ITEM":
            items = self.player.inventory
            if not items:
                self.state = "MENU"
                return
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.submenu_idx = (self.submenu_idx - 1) % len(items)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.submenu_idx = (self.submenu_idx + 1) % len(items)
                self.sound_fx.play_select()
            elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                item = items.pop(self.submenu_idx)
                heal = item.get("heal", 0)
                san_heal = item.get("sanity_heal", 0)
                self.player.hp = min(self.player.max_hp, self.player.hp + heal)
                if san_heal > 0:
                    self.player.modify_sanity(san_heal)
                self.sound_fx.play_heal()
                msg = f"* ¡Paniel usó {item['name']}!\n* ¡Recuperaste {heal} HP!"
                if san_heal > 0:
                    msg += f" (+{san_heal}% cordura)"
                msg += f" (HP actual: {self.player.hp}/{self.player.max_hp})"
                self.action_message = msg
                self.state = "ACTION_TEXT"
            elif event.key in [pygame.K_x, pygame.K_ESCAPE]:
                self.state = "MENU"

        elif self.state == "ATTACK_METER":
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE] and not self.attack_hit:
                self._resolve_player_attack()

        elif self.state == "ACTION_TEXT":
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                if self.enemy["hp"] <= 0:
                    self._trigger_victory(spared=False)
                elif self.enemy["mercy"] >= 100 and self.selected_btn == 3:
                    self._trigger_victory(spared=True)
                else:
                    self._start_enemy_turn()

        elif self.state in ["VICTORY", "SPARE_VICTORY"]:
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self.on_finish_callback(victory=True)

        elif self.state == "ENEMY_TURN":
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                self._trigger_parry()

        elif self.state == "GAME_OVER":
            if event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE] and self.game_over_timer > 1.2:
                self.player.hp = self.player.max_hp
                self.on_finish_callback(victory=False, revived=True)

    def _trigger_parry(self):
        """Activa el bloqueo / Parry con el Alma Verde durante el turno enemigo.
        Dura 0.32 segundos. Requiere que el cooldown de 5 segundos haya finalizado."""
        if self.parry_cooldown > 0 or self.parry_active_timer > 0:
            return
        self.parry_active_timer = 0.32
        self.parry_cooldown = 5.0
        self.sound_fx.play_parry_ready()

    def _execute_parry(self, bullet):
        """Ejecuta con éxito un Parry al desviar un proyectil enemigo durante la ventana activa:
        - Destruye/anula el proyectil
        - Emite sonido metálico triunfal de parry (snd_parry)
        - Crea estallido de chispas verdes/esmeralda
        - Otorga +16% TP
        - Muestra texto flotante '+PARRY! (+16% TP)'
        - Otorga 0.30s de invulnerabilidad para seguridad
        - Añade sacudida de pantalla épica
        """
        bullet.alive = False
        self.sound_fx.play_parry()
        self.screen_shake = max(self.screen_shake, 4.5)
        self.invulnerable_timer = max(self.invulnerable_timer, 0.30)
        self.tp = min(100.0, self.tp + 16.0)

        self.parry_floating_txt = "+PARRY! (+16% TP)"
        self.parry_floating_pos = [float(self.soul_x), float(self.soul_y - 14)]
        self.parry_floating_life = 0.85

        for _ in range(16):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(60, 160)
            self.parry_sparks.append({
                "x": float(self.soul_x),
                "y": float(self.soul_y),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "color": random.choice([(40, 255, 120), (160, 255, 200), (255, 255, 255), (80, 230, 255)]),
                "size": random.choice([2, 3, 4]),
                "life": random.uniform(0.28, 0.45),
                "max_life": 0.45,
            })

    def _trigger_victory(self, spared=False):
        """Procesa la victoria estilo Deltarune, entrega de experiencia, D$ y subida de nivel."""
        self.player.gold += (18 + self.lv_bonus * 3) if not spared else (22 + self.lv_bonus * 4)
        base_exp = self.enemy.get("exp", self.template.get("exp", 25))
        if spared:
            self.state = "SPARE_VICTORY"
            exp_gain = int(base_exp * 0.8)
            leveled_up, levels = self.player.add_exp(exp_gain)
            self.sound_fx.play_spare()
            if leveled_up:
                self.sound_fx.play_save()
                max_txt = " (MÁX)" if self.player.lv >= self.player.max_lv else ""
                self.action_message = (
                    f"* ¡¡GANASTE!! Perdonaste a {self.enemy['name']}.\n"
                    f"* Recibiste {exp_gain} EXP y 22 D$.\n"
                    f"* ¡¡TU NIVEL SUBIÓ A LV {self.player.lv}{max_txt}!!"
                )
            else:
                self.action_message = (
                    f"* ¡¡GANASTE!! Perdonaste a {self.enemy['name']}.\n"
                    f"* Recibiste {exp_gain} EXP y 22 D$."
                )
        else:
            self.state = "VICTORY"
            exp_gain = base_exp
            leveled_up, levels = self.player.add_exp(exp_gain)
            self.sound_fx.play_crit()
            if leveled_up:
                self.sound_fx.play_save()
                max_txt = " (MÁX)" if self.player.lv >= self.player.max_lv else ""
                self.action_message = (
                    f"* ¡¡GANASTE!! {self.enemy['name']} fue derrotado.\n"
                    f"* Recibiste {exp_gain} EXP y 18 D$.\n"
                    f"* ¡¡TU NIVEL SUBIÓ A LV {self.player.lv}{max_txt}!!"
                )
            else:
                self.action_message = (
                    f"* ¡¡GANASTE!! {self.enemy['name']} fue derrotado.\n"
                    f"* Recibiste {exp_gain} EXP y 18 D$."
                )

    def _choose_menu_action(self):
        btn = self.btn_names[self.selected_btn]
        if btn == "FIGHT":
            self.state = "ATTACK_METER"
            self.cursor_x = float(self.meter_rect.right - 12)
            self.attack_hit = False
            self.attack_rating = ""
            self.afterimages.clear()
            self.sound_fx.play_select()

        elif btn == "ACT":
            self.state = "SUBMENU_ACT"
            self.submenu_idx = 0
            self.sound_fx.play_select()

        elif btn == "ITEM":
            if self.player.inventory:
                self.state = "SUBMENU_ITEM"
                self.submenu_idx = 0
                self.sound_fx.play_select()
            else:
                self.action_message = "* Tu inventario de objetos está vacío."
                self.state = "ACTION_TEXT"

        elif btn == "SPARE":
            if self.enemy["mercy"] >= 100:
                self._trigger_victory(spared=True)
            else:
                self.sound_fx.play_select()
                self.enemy["mercy"] = min(100, self.enemy["mercy"] + 10)
                self.floating_dmg = "+10% MERCY"
                self.floating_dmg_color = (255, 235, 70)
                self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 25)]
                self.floating_dmg_vy = -50.0
                self.action_message = (
                    f"* Intentaste perdonar a {self.enemy['name']}...\n"
                    "* Pero su nombre aún no es amarillo (+10% Piedad)."
                )
                self.state = "ACTION_TEXT"

        elif btn == "DEFEND":
            self.defending = True
            self.tp = min(100.0, self.tp + 25.0)
            self.sound_fx.play_select()
            self.action_message = (
                "* ¡Paniel alzó su guardia defensiva!\n"
                "* (Daño reducido en este turno y +25% TP ganado)"
            )
            self.state = "ACTION_TEXT"

    def _resolve_player_attack(self):
        self.attack_hit = True
        self.black_flash_state = None
        dist = abs(self.cursor_x - self.target_x)

        if dist <= 7:
            # 15% de probabilidad de despertar un BlackFlash espontáneo al acertar un crítico perfecto
            if random.random() < self.black_flash_chance:
                self.tp = min(100.0, self.tp + 15.0)
                self._trigger_black_flash(from_crit=True)
                return
            mult = 1.55
            self.attack_rating = "¡¡150 CRÍTICO!!"
            self.tp = min(100.0, self.tp + 15.0)
            self.sound_fx.play_crit()
        elif dist <= 22:
            mult = 1.15
            self.attack_rating = "¡120 GOLPE!"
            self.tp = min(100.0, self.tp + 10.0)
            self.sound_fx.play_enemy_hit()
        elif dist <= 52:
            mult = 0.75
            self.attack_rating = "70 DÉBIL"
            self.tp = min(100.0, self.tp + 5.0)
            self.sound_fx.play_enemy_hit()
        else:
            mult = 0.0
            self.attack_rating = "FALLO"

        dmg = 0
        if mult > 0:
            base_dmg = (self.player.effective_attack * mult) - self.enemy["defense"]
            dmg = max(1, int(round(base_dmg + random.uniform(0.5, 2.5))))
            self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
            self.sound_fx.play_slash()

        self.hero_lunge_x = 24.0
        self.rude_buster_beam = None
        self.enemy_hit_flash = 0.45
        self.slash_timer = 0.55
        self.floating_dmg = str(dmg) if mult > 0 else "FALLO"
        self.floating_dmg_color = (255, 230, 75) if dist <= 7 else (255, 255, 255)
        self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 25)]
        self.floating_dmg_vy = -68.0
        self.state = "SLASH_ANIM"

    def _start_enemy_turn(self):
        self.state = "ENEMY_TURN"
        self.turn_timer = self.turn_duration
        self.bullets.clear()
        self.bullet_spawn_timer = -0.75  # Pausa previa de advertencia de 0.75s antes de que aparezca cualquier proyectil
        self.turn_prep_timer = 0.75  # Indicador visual de alerta mientras la arena se expande
        self.current_pattern = random.choice(self.enemy["patterns"])

        # Iniciar la animación de expansión de la arena justo en el centro entre Paniel y el enemigo
        self.cur_box = [
            float(self.bullet_box.centerx - 16),
            float(self.bullet_box.centery - 16),
            32.0,
            32.0,
        ]

        self.soul_x = float(self.bullet_box.centerx)
        self.soul_y = float(self.bullet_box.centery)
        self.invulnerable_timer = 0.85  # Escudo de gracia al iniciar el turno para evitar daño instantáneo
        self.parry_active_timer = 0.0

        self.speech_bubble_text = random.choice(self.enemy["quotes"])
        self.speech_bubble_timer = 1.45
        self.sound_fx.play_warning()


    def update(self, dt):
        self.anim_time += dt
        self.grid_scroll = (self.grid_scroll + dt * 24.0) % 32.0

        # Suavizado de la barra de TP
        self.display_tp += (self.tp - self.display_tp) * min(1.0, dt * 12.0)

        # Deslizamiento suave de la barra de acciones hacia abajo durante la pelea (ENEMY_TURN)
        target_slide = 1.0 if self.state == "ENEMY_TURN" else 0.0
        self.ui_slide += (target_slide - self.ui_slide) * min(1.0, dt * 12.0)

        # Expansión suave de la arena verde grande entre Paniel y el enemigo
        if self.state == "ENEMY_TURN":
            lerp_spd = min(1.0, dt * 16.0)
            self.cur_box[0] += (self.bullet_box.x - self.cur_box[0]) * lerp_spd
            self.cur_box[1] += (self.bullet_box.y - self.cur_box[1]) * lerp_spd
            self.cur_box[2] += (self.bullet_box.width - self.cur_box[2]) * lerp_spd
            self.cur_box[3] += (self.bullet_box.height - self.cur_box[3]) * lerp_spd

        if self.hero_lunge_x > 0:
            self.hero_lunge_x = max(0.0, self.hero_lunge_x - dt * 65.0)
        if self.hero_hurt_flash > 0:
            self.hero_hurt_flash = max(0.0, self.hero_hurt_flash - dt)
        if self.graze_flash_timer > 0:
            self.graze_flash_timer = max(0.0, self.graze_flash_timer - dt)

        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 18.0)
        if self.enemy_hit_flash > 0:
            self.enemy_hit_flash = max(0.0, self.enemy_hit_flash - dt)

        if self.floating_dmg:
            self.floating_dmg_pos[1] += self.floating_dmg_vy * dt
            self.floating_dmg_vy += 180.0 * dt
            if self.floating_dmg_pos[1] > self.enemy_base_y - 12:
                self.floating_dmg_pos[1] = float(self.enemy_base_y - 12)
                self.floating_dmg_vy *= -0.35

        for sq in self.bg_squares:
            sq["x"] -= sq["speed"] * dt
            if sq["x"] < -12:
                sq["x"] = VIRTUAL_WIDTH + 12
                sq["y"] = random.uniform(0, 142)

        for sp in self.graze_sparks:
            sp["x"] += sp["vx"] * dt
            sp["y"] += sp["vy"] * dt
            sp["life"] -= dt
        self.graze_sparks = [sp for sp in self.graze_sparks if sp["life"] > 0]

        for echo in self.graze_echoes:
            echo["life"] -= dt
        self.graze_echoes = [e for e in self.graze_echoes if e["life"] > 0]

        # Actualizar llamas de Fuego Oscuro con borde negro y esquirlas de cristal roto (BlackFlash)
        for fl in self.black_flash_flames:
            fl["x"] += fl["vx"] * dt
            fl["y"] += fl["vy"] * dt
            fl["vy"] -= 35.0 * dt
            fl["life"] -= dt
        self.black_flash_flames = [fl for fl in self.black_flash_flames if fl["life"] > 0]

        for sh in self.crystal_shards:
            sh["x"] += sh["vx"] * dt
            sh["y"] += sh["vy"] * dt
            sh["vy"] += 160.0 * dt
            sh["angle"] += sh["v_ang"] * dt
            sh["life"] -= dt
        self.crystal_shards = [sh for sh in self.crystal_shards if sh["life"] > 0]

        # Actualización del Parry (Alma Verde [Z])
        if self.parry_active_timer > 0:
            self.parry_active_timer = max(0.0, self.parry_active_timer - dt)

        if self.parry_cooldown > 0:
            prev_cd = self.parry_cooldown
            self.parry_cooldown = max(0.0, self.parry_cooldown - dt)
            if prev_cd > 0 and self.parry_cooldown <= 0:
                self.sound_fx.play_parry_ready()

        for psp in self.parry_sparks:
            psp["x"] += psp["vx"] * dt
            psp["y"] += psp["vy"] * dt
            psp["life"] -= dt
        self.parry_sparks = [psp for psp in self.parry_sparks if psp["life"] > 0]

        if self.parry_floating_life > 0:
            self.parry_floating_life = max(0.0, self.parry_floating_life - dt)
            self.parry_floating_pos[1] -= 22.0 * dt
            if self.parry_floating_life <= 0:
                self.parry_floating_txt = None

        if self.state == "INTRO":
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.state = "MENU"

        elif self.state == "ATTACK_METER":
            if not self.attack_hit:
                self.afterimages.append({"x": self.cursor_x, "alpha": 160})
                self.afterimages = [a for a in self.afterimages if a["alpha"] > 20]
                for a in self.afterimages:
                    a["alpha"] -= dt * 500
                self.cursor_x -= self.cursor_speed * dt
                if self.cursor_x <= self.meter_rect.left + 8:
                    self._resolve_player_attack()

        elif self.state == "SLASH_ANIM":
            self.slash_timer -= dt
            if self.rude_buster_beam is not None:
                self.rude_buster_beam["progress"] = min(1.0, self.rude_buster_beam["progress"] + dt * 3.2)

            # Segundo impacto de BlackFlash (impacta DOS VECES rompiendo el cristal)
            if self.black_flash_state and self.black_flash_state["landed"] and not self.black_flash_state["hit2_done"]:
                if self.slash_timer <= 0.60:
                    self.black_flash_state["hit2_done"] = True
                    d1 = self.black_flash_state["hit1_dmg"]
                    d2 = self.black_flash_state["hit2_dmg"]
                    self.enemy["hp"] = max(0, self.enemy["hp"] - d2)
                    self.sound_fx.play_shatter()
                    self.sound_fx.play_crit()
                    self.screen_shake = 12.0
                    self.enemy_hit_flash = 0.65
                    self.hero_lunge_x = 28.0
                    self._spawn_black_flash_vfx(int(self.enemy_base_x), int(self.enemy_base_y), shatter_burst=True)
                    self.floating_dmg = f"¡¡DOBLE IMPACTO!! {d1}+{d2}"
                    self.floating_dmg_color = (255, 235, 85)
                    self.floating_dmg_pos = [float(self.enemy_base_x), float(self.enemy_base_y - 30)]
                    self.floating_dmg_vy = -82.0

            if self.slash_timer <= 0:
                self.rude_buster_beam = None
                bf = self.black_flash_state
                self.black_flash_state = None
                if self.enemy["hp"] <= 0:
                    self._trigger_victory(spared=False)
                else:
                    self.state = "ACTION_TEXT"
                    if bf is not None:
                        if bf["landed"]:
                            tot = bf["hit1_dmg"] + bf["hit2_dmg"]
                            self.action_message = (
                                f"* ¡¡BLACK FLASH ACERTADO (15%)!! ¡El espacio se rompió como un cristal!\n"
                                f"* ¡Doble impacto (+20% fuerza): {bf['hit1_dmg']} + {bf['hit2_dmg']} = {tot} de daño!"
                            )
                        else:
                            self.action_message = (
                                "* ¡Paniel desató BlackFlash (50% TP), pero falló el 15% de probabilidad!\n"
                                "* (Destellos de Fuego Oscuro y cristal quebrado resonaron en el aire)"
                            )
                    else:
                        self.action_message = f"* ¡Paniel atacó a {self.enemy['name']} ({self.attack_rating})!"

        elif self.state == "ENEMY_TURN":
            self.turn_timer -= dt
            if self.turn_prep_timer > 0:
                self.turn_prep_timer = max(0.0, self.turn_prep_timer - dt)
            if self.speech_bubble_timer > 0:
                self.speech_bubble_timer -= dt
            if self.invulnerable_timer > 0:
                self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

            keys = pygame.key.get_pressed()
            sdx, sdy = 0.0, 0.0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                sdx -= 1.0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                sdx += 1.0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                sdy -= 1.0
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                sdy += 1.0

            is_focus = (keys[pygame.K_x] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            soul_spd = self.soul_speed_focus if is_focus else self.soul_speed_normal

            if sdx != 0 or sdy != 0:
                mag = math.hypot(sdx, sdy)
                self.soul_x += (sdx / mag) * soul_spd * dt
                self.soul_y += (sdy / mag) * soul_spd * dt

            # Confinar estrictamente al alma dentro de la arena entre Paniel y el enemigo
            pad = 6
            self.soul_x = max(float(self.bullet_box.left + pad), min(float(self.bullet_box.right - pad), self.soul_x))
            self.soul_y = max(float(self.bullet_box.top + pad), min(float(self.bullet_box.bottom - pad), self.soul_y))

            self._update_bullet_pattern(dt)

            soul_pt = (self.soul_x, self.soul_y)
            for b in self.bullets:
                try:
                    b.update(dt, self.bullet_box, soul_pos=soul_pt)
                except TypeError:
                    b.update(dt, self.bullet_box)

                # Efecto gravitacional si hay un vórtice del eclipse activo (solo cuando ya se formó)
                if isinstance(b, DarkGravityVortexBullet) and b.alive:
                    if hasattr(b, 'is_active') and not b.is_active():
                        pass
                    else:
                        vdx = b.x - self.soul_x
                        vdy = b.y - self.soul_y
                        vdist = max(18.0, math.hypot(vdx, vdy))
                        vpull = min(42.0, 1400.0 / vdist) * dt
                        self.soul_x += (vdx / vdist) * vpull
                        self.soul_y += (vdy / vdist) * vpull

                if b.check_graze(soul_pt, graze_radius=15.0):
                    self.sound_fx.play_graze()
                    self.tp = min(100.0, self.tp + 3.0)
                    self.graze_flash_timer = 0.20
                    self.graze_echoes.append({
                        "x": self.soul_x,
                        "y": self.soul_y,
                        "life": 0.26,
                        "max_life": 0.26,
                    })
                    for _ in range(5):
                        ang = random.uniform(0, 2 * math.pi)
                        self.graze_sparks.append({
                            "x": self.soul_x, "y": self.soul_y,
                            "vx": math.cos(ang) * random.uniform(40, 95),
                            "vy": math.sin(ang) * random.uniform(40, 95),
                            "life": 0.24,
                        })

                # Comprobación de Parry activo (Alma Verde con [Z]):
                if self.parry_active_timer > 0:
                    if b.collides_with_soul(soul_pt, soul_radius=5.5):
                        self._execute_parry(b)
                        continue

                if b.collides_with_soul(soul_pt, soul_radius=3.0):
                    if self.invulnerable_timer <= 0:
                        defense_bonus = 4 if self.defending else 0
                        raw_dmg = self.enemy["attack"] - (self.player.effective_defense + defense_bonus)
                        dmg = max(1, int(round(raw_dmg + random.uniform(-0.5, 1.2))))
                        self.player.hp = max(0, self.player.hp - dmg)
                        self.player.modify_sanity(-2.5)
                        self.invulnerable_timer = 0.85
                        self.hero_hurt_flash = 0.45
                        self.screen_shake = 5.0
                        self.sound_fx.play_hurt()
                        b.alive = False

                        if self.player.hp <= 0:
                            self._trigger_game_over()
                            return

            self.bullets = [b for b in self.bullets if b.alive]

            if self.turn_timer <= 0:
                self.bullets.clear()
                self.defending = False
                self.floating_dmg = None
                self.parry_active_timer = 0.0
                self.state = "MENU"
                self.action_message = random.choice([
                    f"* {self.enemy['name']} acecha entre la niebla oscura.",
                    "* El poder del Dark World resuena alrededor de Paniel.",
                    "* El alma de Paniel brilla con determinación.",
                ])

        elif self.state == "GAME_OVER":
            self.game_over_timer += dt
            for sh in self.soul_shards:
                sh["x"] += sh["vx"] * dt
                sh["y"] += sh["vy"] * dt
                sh["vy"] += 140.0 * dt

    def _trigger_game_over(self):
        self.state = "GAME_OVER"
        self.game_over_timer = 0.0
        self.sound_fx.play_shatter()
        self.bullets.clear()
        self.player.death_count += 1
        self.player.modify_sanity(-32.0)
        for _ in range(7):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(45, 110)
            self.soul_shards.append({
                "x": self.soul_x,
                "y": self.soul_y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 30,
            })

    def _safe_spawn_pos(self, bb, min_dist=52.0, preferred_side=None):
        """Encuentra una posición de spawn que garantice al menos min_dist de distancia del alma de Paniel."""
        for _ in range(30):
            if preferred_side == "TOP":
                sx = random.uniform(bb.left + 14, bb.right - 14)
                sy = bb.top + 6
            elif preferred_side == "BOTTOM":
                sx = random.uniform(bb.left + 14, bb.right - 14)
                sy = bb.bottom - 6
            elif preferred_side == "LEFT":
                sx = bb.left + 6
                sy = random.uniform(bb.top + 14, bb.bottom - 14)
            elif preferred_side == "RIGHT":
                sx = bb.right - 6
                sy = random.uniform(bb.top + 14, bb.bottom - 14)
            else:
                sx = random.uniform(bb.left + 14, bb.right - 14)
                sy = random.uniform(bb.top + 14, bb.bottom - 14)
            if math.hypot(sx - self.soul_x, sy - self.soul_y) >= min_dist:
                return sx, sy
        # Fallback seguro en la esquina opuesta al alma
        fx = bb.left + 14 if self.soul_x > bb.centerx else bb.right - 14
        fy = bb.top + 14 if self.soul_y > bb.centery else bb.bottom - 14
        return fx, fy

    def _update_bullet_pattern(self, dt):
        self.bullet_spawn_timer += dt
        bb = self.bullet_box

        # Multiplicadores de dificultad y velocidad según el estado del enemigo y fase de jefe
        is_boss = self.enemy.get("is_boss", False)
        is_enraged = is_boss and (self.enemy["hp"] < self.enemy["max_hp"] * 0.5)

        boss_dm = 1.30 if is_boss else 1.0
        boss_sm = 1.25 if is_boss else 1.0
        if is_enraged:
            boss_dm *= 1.32
            boss_sm *= 1.18

        dm = self.diff_mult * boss_dm
        sm = self.spd_mult * boss_sm

        if self.current_pattern == "shadow_rain":
            if self.bullet_spawn_timer >= 0.32 / dm:
                self.bullet_spawn_timer = 0.0
                rx = random.uniform(bb.left + 12, bb.right - 12)
                phase = random.uniform(0, math.pi * 2)
                b = ShadowRainBullet(rx, bb.top + 2, phase=phase)
                b.vy *= sm
                self.bullets.append(b)

        elif self.current_pattern == "shadow_spiral":
            if self.bullet_spawn_timer >= 0.65 / dm:
                self.bullet_spawn_timer = 0.0
                base_a = self.anim_time * 2.0
                count = 4 if self.lv_bonus >= 3 else 3
                for i in range(count):
                    self.bullets.append(
                        ShadowSpiralBullet(bb.centerx, bb.centery, base_a + i * (math.pi * 2 / count), speed=48.0 * sm)
                    )

        elif self.current_pattern == "diamond_swords":
            if self.bullet_spawn_timer >= 0.72 / dm:
                self.bullet_spawn_timer = 0.0
                tx = self.soul_x + random.uniform(-18, 18)
                tx = max(bb.left + 8, min(bb.right - 8, tx))
                b = DiamondSwordBullet(tx, bb.top - 8, bb.top)
                b.vy *= sm
                self.bullets.append(b)
                self.sound_fx.play_warning()

        elif self.current_pattern == "crossfire_diamonds":
            if self.bullet_spawn_timer >= 0.44 / dm:
                self.bullet_spawn_timer = 0.0
                side = "RIGHT" if self.soul_x < bb.centerx else "LEFT"
                ry = random.uniform(bb.top + 10, bb.bottom - 10)
                if abs(ry - self.soul_y) < 22:
                    ry = max(bb.top + 12, min(bb.bottom - 12, self.soul_y + random.choice([-32, 32])))
                if side == "LEFT":
                    self.bullets.append(CrossfireDiamondBullet(bb.left - 5, ry, vx=82.0 * sm))
                else:
                    self.bullets.append(CrossfireDiamondBullet(bb.right + 5, ry, vx=-82.0 * sm))

        elif self.current_pattern == "bouncing_notes":
            max_notes = 4 if self.lv_bonus >= 2 else 3
            if len(self.bullets) < max_notes and self.bullet_spawn_timer >= 0.5 / dm:
                self.bullet_spawn_timer = 0.0
                ang = random.uniform(0.3, 1.2) + random.choice([0, math.pi / 2, math.pi, math.pi * 1.5])
                spd = 65.0 * sm
                sx, sy = self._safe_spawn_pos(bb, min_dist=50.0, preferred_side="TOP")
                self.bullets.append(BouncingNoteBullet(sx, sy, math.cos(ang) * spd, math.sin(ang) * spd))

        elif self.current_pattern == "sound_arcs":
            if self.bullet_spawn_timer >= 1.05 / dm:
                self.bullet_spawn_timer = 0.0
                gap_angle = random.uniform(0.4, math.pi - 0.4)
                for i in range(12):
                    ang = (i / 12.0) * math.pi
                    if abs(ang - gap_angle) > 0.35:
                        self.bullets.append(SoundArcBullet(bb.centerx, bb.top + 4, ang, speed=52.0 * sm))

        # --- PATRONES DEL ACÓLITO ENCAPUCHADO DE LA SECTA ("sectario") ---
        elif self.current_pattern == "cult_daggers":
            if self.bullet_spawn_timer >= 0.52 / dm:
                self.bullet_spawn_timer = 0.0
                side = "TOP" if random.random() < 0.5 else ("RIGHT" if self.soul_x < bb.centerx else "LEFT")
                sx, sy = self._safe_spawn_pos(bb, min_dist=48.0, preferred_side=side)
                self.bullets.append(CultDaggerBullet(sx, sy, self.soul_x, self.soul_y, speed=145.0 * sm))
                self.sound_fx.play_warning()

        elif self.current_pattern == "blood_sigil":
            if self.bullet_spawn_timer >= 0.78 / dm:
                self.bullet_spawn_timer = 0.0
                ox, oy = self._safe_spawn_pos(bb, min_dist=45.0, preferred_side="TOP")
                n_orbs = 6 if self.lv_bonus >= 2 else 5
                base_ang = self.anim_time * 1.8
                spd = 62.0 * sm
                for i in range(n_orbs):
                    ang = base_ang + i * (2 * math.pi / n_orbs)
                    self.bullets.append(RitualSigilBullet(ox, oy, math.cos(ang) * spd, math.sin(ang) * spd))

        # ==========================================================
        # PATRONES DEL JEFE: MORVATH EL SEPULTURERO (ALTA DIFICULTAD Y ERRÁTICOS)
        # ==========================================================
        elif self.current_pattern == "scythe_sweep":
            # Barrido de guadañas ondulantes con velocidades alternadas desde los bordes de la arena
            if self.bullet_spawn_timer >= 0.75 / dm:
                self.bullet_spawn_timer = 0.0
                from_right = (self.soul_x < bb.centerx)
                sy = random.uniform(bb.top + 16, bb.bottom - 16)
                if abs(sy - self.soul_y) < 22:
                    sy = max(bb.top + 14, min(bb.bottom - 14, self.soul_y + random.choice([-28, 28])))
                sx = bb.right + 10 if from_right else bb.left - 10
                vx = (-92.0 if from_right else 92.0) * sm
                self.bullets.append(ScytheWaveBullet(sx, sy, vx=vx, vy_amp=30.0, phase=random.uniform(0, math.pi * 2)))
                if is_enraged or random.random() < 0.40:
                    sy2 = max(bb.top + 14, min(bb.bottom - 14, sy + random.choice([-32, 32])))
                    vx2 = (105.0 if from_right else -105.0) * sm
                    self.bullets.append(ScytheWaveBullet(bb.left - 8 if from_right else bb.right + 8, sy2, vx=vx2, vy_amp=24.0, phase=random.uniform(0, math.pi)))

        elif self.current_pattern == "soul_lantern_ring":
            # Anillo de llamas espectrales con apertura angular y chispas secundarias
            if self.bullet_spawn_timer >= 1.05 / dm:
                self.bullet_spawn_timer = 0.0
                origin_x = random.uniform(bb.left + 22, bb.right - 22)
                origin_y = bb.top + 8
                aim_ang = math.atan2(self.soul_y - origin_y, self.soul_x - origin_x)
                n_flames = 5 if not is_enraged else 6
                for i in range(n_flames):
                    ang = aim_ang + (i - n_flames / 2.0) * 0.32
                    spd = random.uniform(68.0, 88.0) * sm
                    self.bullets.append(LanternFlameBullet(origin_x, origin_y, math.cos(ang) * spd, math.sin(ang) * spd))
                self.bullets.append(ErraticWispBullet(origin_x, origin_y, math.cos(aim_ang) * 78.0 * sm, math.sin(aim_ang) * 78.0 * sm))

        elif self.current_pattern == "grave_pillars":
            # Columnas de lápida con clara advertencia vertical luminosa previa (0.75s)
            active_pillars = len([b for b in self.bullets if isinstance(b, GravePillarBullet)])
            max_p = 2 if is_enraged else 1
            if active_pillars < max_p and self.bullet_spawn_timer >= 1.15 / dm:
                self.bullet_spawn_timer = 0.0
                tx1 = max(bb.left + 20, min(bb.right - 20, self.soul_x + random.uniform(-16, 16)))
                self.bullets.append(GravePillarBullet(tx1, bb.bottom, warn_timer=0.75))
                self.sound_fx.play_warning()
                rx = random.uniform(bb.left + 12, bb.right - 12)
                b_rain = ShadowRainBullet(rx, bb.top + 2, phase=random.uniform(0, math.pi * 2))
                b_rain.vy = (65.0 + random.uniform(0, 20)) * sm
                self.bullets.append(b_rain)

        elif self.current_pattern == "death_scythe_boomerang":
            # Guadañas bumerán que cruzan la arena desde el borde exterior
            active_boomerangs = len([b for b in self.bullets if isinstance(b, BoomerangScytheBullet)])
            max_b = 2 if is_enraged else 1
            if active_boomerangs < max_b and self.bullet_spawn_timer >= 1.20 / dm:
                self.bullet_spawn_timer = 0.0
                side = "RIGHT" if self.soul_x < bb.centerx else "LEFT"
                if side == "LEFT":
                    sx, sy = bb.left - 8, random.uniform(bb.top + 16, bb.bottom - 16)
                else:
                    sx, sy = bb.right + 8, random.uniform(bb.top + 16, bb.bottom - 16)
                ang = math.atan2(self.soul_y - sy, self.soul_x - sx)
                spd = 120.0 * sm
                self.bullets.append(BoomerangScytheBullet(sx, sy, math.cos(ang) * spd, math.sin(ang) * spd, decel=145.0))
                if is_enraged and active_boomerangs == 0:
                    ang2 = ang + random.choice([-0.40, 0.40])
                    self.bullets.append(BoomerangScytheBullet(sx, sy, math.cos(ang2) * spd * 0.9, math.sin(ang2) * spd * 0.9, decel=135.0))

        elif self.current_pattern == "funeral_bell_toll":
            # Ondas sónicas expansivas de campana fúnebre con apertura angular dodgeable
            active_shockwaves = len([b for b in self.bullets if isinstance(b, FuneralBellShockwave)])
            if active_shockwaves < 1 and self.bullet_spawn_timer >= 1.35 / dm:
                self.bullet_spawn_timer = 0.0
                cx = bb.centerx
                cy = bb.top + 8
                gap_a = math.atan2(self.soul_y - cy, self.soul_x - cx)
                self.bullets.append(FuneralBellShockwave(cx, cy, expand_speed=72.0 * sm, gap_angle=gap_a, gap_size=1.20, start_delay=0.45))
                self.sound_fx.play_warning()
                corner_x = bb.left + 6 if self.soul_x > bb.centerx else bb.right - 6
                corner_y = bb.top + 8
                ang_c = math.atan2(self.soul_y - corner_y, self.soul_x - corner_x)
                self.bullets.append(ErraticWispBullet(corner_x, corner_y, math.cos(ang_c) * 75.0 * sm, math.sin(ang_c) * 75.0 * sm))

        elif self.current_pattern == "graveyard_cataclysm":
            # Cataclismo de guadañas rebotantes en esquinas lejanas + columnas del sepulcro
            max_bouncers = 2 if is_enraged else 1
            bouncers_alive = len([b for b in self.bullets if isinstance(b, ChaosBouncingScythe)])
            active_pillars = len([b for b in self.bullets if isinstance(b, GravePillarBullet)])
            if bouncers_alive < max_bouncers and self.bullet_spawn_timer >= 1.25 / dm:
                self.bullet_spawn_timer = 0.0
                ang = random.uniform(0.35, 1.15) + random.choice([0, math.pi / 2, math.pi, math.pi * 1.5])
                spd = 105.0 * sm
                spawn_x = bb.left + 14 if self.soul_x > bb.centerx else bb.right - 14
                spawn_y = bb.top + 14
                self.bullets.append(ChaosBouncingScythe(spawn_x, spawn_y, math.cos(ang) * spd, math.sin(ang) * spd, max_bounces=3))
                if active_pillars < 1:
                    pill_x = bb.left + 24 if self.soul_x > bb.centerx else bb.right - 24
                    self.bullets.append(GravePillarBullet(pill_x, bb.bottom, warn_timer=0.75))
                    self.sound_fx.play_warning()

        elif self.current_pattern == "frenzy_soul_hunt":
            # Ánimas teledirigidas que rastrean al alma desde el borde opuesto
            active_homing = len([b for b in self.bullets if isinstance(b, HomingSoulOrb)])
            if active_homing < 1 and self.bullet_spawn_timer >= 1.15 / dm:
                self.bullet_spawn_timer = 0.0
                ox = bb.right - 8 if self.soul_x < bb.centerx else bb.left + 8
                oy = random.uniform(bb.top + 16, bb.bottom - 16)
                self.bullets.append(HomingSoulOrb(ox, oy, speed=85.0 * sm, turn_rate=3.2, lifespan=3.0))
                aim = math.atan2(self.soul_y - oy, self.soul_x - ox)
                self.bullets.append(LanternFlameBullet(ox, oy, math.cos(aim) * 88.0 * sm, math.sin(aim) * 88.0 * sm))

        # ==========================================================
        # PATRONES DEL JEFE SUPREMO: VAELKOR, REY DEL CRISTAL NEGRO (MÁXIMA DIFICULTAD)
        # ==========================================================
        elif self.current_pattern == "black_flame_barrage":
            # Ráfaga implacable de Fuego Oscuro desde los bordes alejados del alma
            if self.bullet_spawn_timer >= 0.55 / dm:
                self.bullet_spawn_timer = 0.0
                side = "TOP" if random.random() < 0.4 else ("RIGHT" if self.soul_x < bb.centerx else "LEFT")
                sx, sy = self._safe_spawn_pos(bb, min_dist=50.0, preferred_side=side)
                ang = math.atan2(self.soul_y - sy, self.soul_x - sx) + random.uniform(-0.18, 0.18)
                spd = (90.0 + random.uniform(0, 22.0)) * sm
                self.bullets.append(DarkFlameBullet(sx, sy, math.cos(ang) * spd, math.sin(ang) * spd, phase=random.uniform(0, 6.28)))

        elif self.current_pattern == "crystal_shatter_storm":
            # Tormenta de esquirlas de cristal oscuro en espirales dobles alternas
            if self.bullet_spawn_timer >= 1.05 / dm:
                self.bullet_spawn_timer = 0.0
                ox, oy = self._safe_spawn_pos(bb, min_dist=50.0, preferred_side="TOP")
                n_shards = 7 if not is_enraged else 8
                base_a = self.anim_time * 2.5
                spd = 82.0 * sm
                for i in range(n_shards):
                    a = base_a + i * (2 * math.pi / n_shards)
                    self.bullets.append(ShatterCrystalBullet(ox, oy, math.cos(a) * spd, math.sin(a) * spd, spin_speed=random.uniform(6.0, 10.0)))

        elif self.current_pattern == "void_cleave_laser":
            # Grietas dimensionales con advertencia clara de 0.70s y estallido horizontal
            active_cleaves = len([b for b in self.bullets if isinstance(b, VoidCleaveBullet)])
            if active_cleaves < 1 and self.bullet_spawn_timer >= 1.30 / dm:
                self.bullet_spawn_timer = 0.0
                ty = max(bb.top + 16, min(bb.bottom - 16, self.soul_y))
                self.bullets.append(VoidCleaveBullet(bb, ty, warn_time=0.70, duration=1.05))
                self.sound_fx.play_warning()
                rx = random.uniform(bb.left + 14, bb.right - 14)
                self.bullets.append(ShatterCrystalBullet(rx, bb.top + 4, random.uniform(-20, 20), 82.0 * sm))

        elif self.current_pattern == "eclipse_gravity_vortex":
            # Vórtice abismal que se forma en la parte superior central (lejos del centro)
            if self.bullet_spawn_timer >= 0:
                vortices = [b for b in self.bullets if isinstance(b, DarkGravityVortexBullet)]
                vortex_y = bb.top + 28
                if not vortices:
                    self.bullets.append(DarkGravityVortexBullet(bb.centerx, vortex_y, duration=4.5, forming_timer=0.70))
                    self.sound_fx.play_warning()
                if self.bullet_spawn_timer >= 0.75 / dm:
                    self.bullet_spawn_timer = 0.0
                    vx, vy = bb.centerx, vortex_y
                    n_sparks = 3
                    base_ang = self.anim_time * 2.8
                    for i in range(n_sparks):
                        a = base_ang + i * (math.pi * 2 / n_sparks)
                        spd = random.uniform(70.0, 92.0) * sm
                        self.bullets.append(DarkFlameBullet(vx, vy, math.cos(a) * spd, math.sin(a) * spd))

        elif self.current_pattern == "fractured_mirror_barrage":
            # Racimos de cristal que vuelan, frenan y estallan en 6 esquirlas tras advertencia
            active_clusters = len([b for b in self.bullets if isinstance(b, FracturedMirrorShards)])
            if active_clusters < 1 and self.bullet_spawn_timer >= 1.25 / dm:
                self.bullet_spawn_timer = 0.0
                side = "TOP" if random.random() < 0.4 else ("RIGHT" if self.soul_x < bb.centerx else "LEFT")
                sx, sy = self._safe_spawn_pos(bb, min_dist=50.0, preferred_side=side)
                ang = math.atan2(self.soul_y - sy, self.soul_x - sx)
                spd = 115.0 * sm
                self.bullets.append(FracturedMirrorShards(sx, sy, math.cos(ang) * spd, math.sin(ang) * spd))

        elif self.current_pattern == "abyssal_cross_lasers":
            # Rejilla de láseres dimensionales cruzados con carril de advertencia de 0.75s
            active_lasers = len([b for b in self.bullets if isinstance(b, LaserCrossGridBullet)])
            if active_lasers == 0 and self.bullet_spawn_timer >= 1.40 / dm:
                self.bullet_spawn_timer = 0.0
                target_y = max(bb.top + 16, min(bb.bottom - 16, self.soul_y))
                target_x = max(bb.left + 16, min(bb.right - 16, self.soul_x))
                self.bullets.append(LaserCrossGridBullet(bb, target_y, is_vertical=False, warn_time=0.75, duration=1.10))
                self.bullets.append(LaserCrossGridBullet(bb, target_x, is_vertical=True, warn_time=0.75, duration=1.10))
                self.sound_fx.play_warning()

        elif self.current_pattern == "apocalypse_crystal_rain":
            # Lluvia apocalíptica de esquirlas oscuras y fuego errático cayendo desde el techo
            if self.bullet_spawn_timer >= 0.42 / dm:
                self.bullet_spawn_timer = 0.0
                rx = random.uniform(bb.left + 12, bb.right - 12)
                if random.random() < 0.60:
                    self.bullets.append(DarkFlameBullet(rx, bb.top + 4, random.uniform(-20, 20), (88.0 + random.uniform(0, 24)) * sm))
                else:
                    self.bullets.append(ShatterCrystalBullet(rx, bb.top + 4, random.uniform(-28, 28), (84.0 + random.uniform(0, 22)) * sm))
                if random.random() < 0.20:
                    self.bullets.append(ErraticWispBullet(rx, bb.top + 4, random.uniform(-35, 35), 88.0 * sm))

    # ==========================================================
    # RENDERIZADO DEL ESCENARIO Y UI DE COMBATE DELTARUNE
    # ==========================================================
    def _get_current_enemy_pos(self, ox=0.0, oy=0.0):
        """Retorna la posición (x, y) actual del enemigo interpolada según si la barra de acciones bajó."""
        ex = int(self.enemy_base_x + ox)
        ey = int(self.enemy_base_y + 56.0 * self.ui_slide + oy)
        return ex, ey

    def _get_current_hero_pos(self, ox=0.0, oy=0.0):
        """Retorna la posición (x, y) actual de Paniel interpolada según si la barra de acciones bajó."""
        bob = int(math.sin(self.anim_time * 4.2) * 1.5)
        recoil = -6 if self.hero_hurt_flash > 0 and (int(self.anim_time * 24) % 2 == 0) else 0
        hx = int(self.hero_base_x + self.hero_lunge_x + recoil + ox)
        hy = int(self.hero_base_y + 46.0 * self.ui_slide + bob + oy)
        return hx, hy

    def draw(self, surface):
        ox = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        oy = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        # 1. Fondo Dark World con cuadrícula neón animada que se expande al bajar la barra de acciones
        self._draw_dark_world_background(surface, ox, oy)

        # 2. Barra vertical de TP (Tension Points) Deltarune a la izquierda
        self._draw_tp_bar(surface)

        if self.state != "GAME_OVER":
            # 3. Dibujar a PANIEL en el lado izquierdo del campo de batalla (con su sprite actual)
            self._draw_battle_hero(surface, ox, oy)

            # 4. Dibujar al ENEMIGO en el lado derecho del campo de batalla
            ex, ey = self._get_current_enemy_pos(ox, oy)
            DeltaruneEnemyRenderer.draw_enemy(
                surface, self.enemy["id"], ex, ey,
                self.anim_time, hit_flash=self.enemy_hit_flash, mercy=self.enemy["mercy"]
            )
            # En modo pelea (cuando puede salir el diálogo sobre su cabeza), las barras de HP/Mercy
            # del enemigo se colocan debajo de sus pies para dejar libre el espacio sobre su cabeza
            if self.ui_slide > 0.35:
                self._draw_enemy_hud(surface, ex, ey + 52)
            else:
                self._draw_enemy_hud(surface, ex, int(18 + oy))

            # Efecto de corte / Rude Buster / BlackFlash sobre el enemigo
            if self.state == "SLASH_ANIM" or self.black_flash_flames or self.crystal_shards:
                self._draw_slash_effects(surface, ox, oy)

        # 5. Caja inferior de diálogo / submenús / barra de ataque (se oculta al bajar la barra de acciones en ENEMY_TURN)
        if self.state != "ENEMY_TURN":
            if self.state in ["ATTACK_METER", "SLASH_ANIM"]:
                self._draw_dialogue_and_submenus(surface, empty_box=True)
                self._draw_attack_meter(surface)
            else:
                self._draw_dialogue_and_submenus(surface, empty_box=False)

        # 6. Tarjeta de personaje (barra de vida) y botones de acción (bajan durante ENEMY_TURN)
        self._draw_deltarune_party_bar(surface)

        # 7. Arena de esquiva Bullet Hell ampliada ENTRE Paniel y el enemigo (POR ENCIMA de la barra de vida)
        if self.state == "ENEMY_TURN":
            self._draw_bullet_arena(surface, ox, oy)
            if self.speech_bubble_timer > 0:
                ex, ey = self._get_current_enemy_pos(ox, oy)
                self._draw_speech_bubble(surface, ex, ey, self.speech_bubble_text)

        # 8. Número de daño o +MERCY% flotante con rebote
        if self.floating_dmg and self.state in ["SLASH_ANIM", "ACTION_TEXT"]:
            self._draw_floating_damage(surface)

        # 9. Pantalla de Game Over
        if self.state == "GAME_OVER":
            self._draw_game_over(surface)

    def _draw_dark_world_background(self, surface, ox, oy):
        """Dibuja la característica cuadrícula neón púrpura/verde de combate de Deltarune."""
        surface.fill((6, 4, 14))

        grid_h = int(146 + 92 * self.ui_slide)
        grid_surf = pygame.Surface((VIRTUAL_WIDTH, grid_h), pygame.SRCALPHA)
        scroll = int(self.grid_scroll)
        grid_col = (52, 24, 92, 115)
        accent_col = (30, 110, 95, 70)

        for gx in range(-32 + scroll, VIRTUAL_WIDTH + 32, 32):
            pygame.draw.line(grid_surf, grid_col, (gx, 0), (gx, grid_h), 1)
        for gy in range(12, grid_h, 24):
            pygame.draw.line(grid_surf, grid_col, (0, gy), (VIRTUAL_WIDTH, gy), 1)

        pygame.draw.line(grid_surf, (130, 55, 200, 190), (0, grid_h - 3), (VIRTUAL_WIDTH, grid_h - 3), 2)
        pygame.draw.line(grid_surf, accent_col, (0, grid_h - 1), (VIRTUAL_WIDTH, grid_h - 1), 1)
        surface.blit(grid_surf, (int(ox * 0.4), int(oy * 0.4)))

        for sq in self.bg_squares:
            pulse = 0.5 + 0.5 * math.sin(self.anim_time * 3.0 + sq["phase"])
            alpha = int(45 + 75 * pulse)
            s = sq["size"]
            sq_surf = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.rect(sq_surf, (150, 80, 235, alpha), (0, 0, s, s), 1)
            surface.blit(sq_surf, (int(sq["x"] + ox * 0.5), int(sq["y"] + oy * 0.5)))

    def _draw_battle_hero(self, surface, ox, oy):
        """Dibuja a Paniel en el lado izquierdo del escenario mirando al enemigo."""
        hx, hy = self._get_current_hero_pos(ox, oy)
        base_plat_y = int(self.hero_base_y + 46.0 * self.ui_slide + 39 + oy)

        # Plataforma / sombra circular bajo los pies de Paniel
        plat = pygame.Surface((42, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(plat, (90, 40, 160, 120), (0, 0, 42, 12))
        pygame.draw.ellipse(plat, (170, 90, 255, 180), (0, 0, 42, 12), 1)
        surface.blit(plat, (hx - 9, base_plat_y))

        # Obtener el sprite de perfil derecho de Paniel según su estado emocional actual (FELIZ, TRISTE, TRAUMADO, LOCO)
        right_frames = self.player.sprites.get("RIGHT", self.player.sprites.get("DOWN", []))
        if right_frames:
            frame_idx = 1 if self.hero_lunge_x > 4 else (int(self.anim_time * 3.5) % len(right_frames) if self.state == "ATTACK_METER" else 0)
            hero_surf = right_frames[frame_idx % len(right_frames)]
            surface.blit(hero_surf, (hx, hy))

            if self.hero_lunge_x > 2:
                arc_s = pygame.Surface((26, 44), pygame.SRCALPHA)
                pygame.draw.arc(arc_s, (255, 240, 120, 230), (0, 2, 24, 40), -1.1, 1.1, 3)
                pygame.draw.arc(arc_s, (255, 255, 255, 255), (2, 4, 20, 36), -0.9, 0.9, 1)
                surface.blit(arc_s, (hx + 18, hy + 2))

        if self.defending:
            sh_surf = pygame.Surface((44, 54), pygame.SRCALPHA)
            pulse_a = int(130 + 50 * math.sin(self.anim_time * 8.0))
            pts = [(22, 2), (40, 14), (40, 38), (22, 50), (4, 38), (4, 14)]
            pygame.draw.polygon(sh_surf, (70, 190, 255, 45), pts)
            pygame.draw.polygon(sh_surf, (110, 230, 255, pulse_a), pts, 2)
            surface.blit(sh_surf, (hx - 9, hy - 4))

    def _draw_slash_effects(self, surface, ox, oy):
        """Dibuja el corte diagonal, el rayo mágico TP o los destellos de Fuego Oscuro y cristal roto de BlackFlash."""
        ex = int(self.enemy_base_x + ox)
        ey = int(self.enemy_base_y + oy)

        # Si hay efectos activos de BlackFlash (Fuego Oscuro con borde negro + Cristal rompiéndose)
        if self.black_flash_state is not None or self.black_flash_flames or self.crystal_shards:
            # 1. Grietas como rompiendo un cristal sobre el espacio del enemigo
            if self.black_flash_state is not None:
                for crack in self.crystal_cracks:
                    if len(crack) >= 2:
                        pygame.draw.lines(surface, (0, 0, 0), False, crack, 5)
                        pygame.draw.lines(surface, (235, 30, 85), False, crack, 3)
                        pygame.draw.lines(surface, (255, 235, 250), False, crack, 1)

                # Relámpagos de Fuego Oscuro con borde negro grueso
                for bolt in self.black_flash_bolts:
                    if len(bolt) >= 2:
                        pygame.draw.lines(surface, (0, 0, 0), False, bolt, 6)
                        pygame.draw.lines(surface, (240, 25, 80), False, bolt, 3)
                        pygame.draw.lines(surface, (18, 0, 28), False, bolt, 1)

                # Anillo de distorsión espacial negro con borde carmesí
                rad = int(16 + 26 * abs(math.sin(self.anim_time * 16.0)))
                pygame.draw.circle(surface, (0, 0, 0), (ex, ey), rad + 2, 4)
                pygame.draw.circle(surface, (245, 35, 90), (ex, ey), rad, 2)

            # 2. Llamas de Fuego Oscuro con borde negro
            for fl in self.black_flash_flames:
                fx, fy = int(fl["x"] + ox), int(fl["y"] + oy)
                sz = max(3, int(fl["size"] * (fl["life"] / fl["max_life"])))
                flick = int(math.sin(self.anim_time * 24.0 + fl["phase"]) * 3)
                flame_poly = [
                    (fx, fy - sz - 4 + flick),
                    (fx + sz, fy),
                    (fx + sz // 2, fy + sz),
                    (fx - sz // 2, fy + sz),
                    (fx - sz, fy),
                ]
                # Relleno oscuro abismal + núcleo carmesí + borde negro nítido
                pygame.draw.polygon(surface, (28, 4, 42), flame_poly)
                pygame.draw.polygon(surface, (0, 0, 0), flame_poly, 2)
                inner_poly = [
                    (fx, fy - sz // 2 - 2 + flick),
                    (fx + max(2, sz // 2), fy),
                    (fx, fy + max(2, sz // 2)),
                    (fx - max(2, sz // 2), fy),
                ]
                pygame.draw.polygon(surface, (240, 30, 85), inner_poly)

            # 3. Esquirlas de cristal roto con borde negro volando por los aires
            for sh in self.crystal_shards:
                sx, sy = int(sh["x"] + ox), int(sh["y"] + oy)
                r = sh["radius"]
                a = sh["angle"]
                shard_pts = [
                    (int(sx + math.cos(a) * r), int(sy + math.sin(a) * r)),
                    (int(sx + math.cos(a + 2.1) * (r * 0.75)), int(sy + math.sin(a + 2.1) * (r * 0.75))),
                    (int(sx + math.cos(a + 4.2) * (r * 0.9)), int(sy + math.sin(a + 4.2) * (r * 0.9))),
                ]
                pygame.draw.polygon(surface, (225, 45, 95), shard_pts)
                pygame.draw.polygon(surface, (0, 0, 0), shard_pts, 2)
                pygame.draw.line(surface, (255, 235, 250), shard_pts[0], shard_pts[1], 1)
            return

        if self.rude_buster_beam is not None:
            p = self.rude_buster_beam["progress"]
            sx = int(self.hero_base_x + 28)
            sy = int(self.hero_base_y + 18)
            cx = int(sx + (ex - sx) * p)
            cy = int(sy + (ey - sy) * p)
            pygame.draw.line(surface, (255, 90, 220), (sx, sy), (cx, cy), 5)
            pygame.draw.line(surface, (255, 240, 255), (sx, sy), (cx, cy), 2)
            rad = int(10 + 22 * math.sin(p * math.pi))
            pygame.draw.circle(surface, (255, 110, 240), (ex, ey), rad, 3)
            pygame.draw.circle(surface, (255, 255, 255), (ex, ey), max(2, rad // 2), 2)
        else:
            prog = 1.0 - (self.slash_timer / 0.55)
            x1 = int(ex - 26 + prog * 12)
            y1 = int(ey - 28 + prog * 12)
            x2 = int(ex + 26 - prog * 6)
            y2 = int(ey + 28 - prog * 6)
            pygame.draw.line(surface, (255, 240, 90), (x1, y1), (x2, y2), 5)
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 2)

    def _draw_tp_bar(self, surface):
        """Dibuja la barra vertical de TP (Tension Points) de Deltarune en el borde izquierdo."""
        tx, ty, tw, th = 10, 26, 13, 102
        t_lbl = self.font_hud.render("T", False, (255, 165, 50))
        p_lbl = self.font_hud.render("P", False, (255, 165, 50))
        surface.blit(t_lbl, (tx + 2, ty - 22))
        surface.blit(p_lbl, (tx + 2, ty - 11))

        pygame.draw.rect(surface, (22, 12, 28), (tx, ty, tw, th), border_radius=2)

        tp_h = int((self.display_tp / 100.0) * (th - 4))
        if tp_h > 0:
            fill_c = (255, 145, 35) if self.tp < 100.0 else (255, 235, 75)
            fill_y = ty + th - 2 - tp_h
            pygame.draw.rect(surface, fill_c, (tx + 2, fill_y, tw - 4, tp_h), border_radius=1)
            pygame.draw.line(surface, (255, 255, 255), (tx + 2, fill_y), (tx + tw - 3, fill_y), 2)

        pygame.draw.rect(surface, (255, 255, 255), (tx, ty, tw, th), 2, border_radius=2)

        pct_txt = "MAX" if self.tp >= 100.0 else f"{int(self.tp)}%"
        pct_col = (255, 240, 80) if self.tp >= 100.0 else (255, 255, 255)
        pct_lbl = self.font_hud.render(pct_txt, False, pct_col)
        surface.blit(pct_lbl, (tx - 3, ty + th + 3))

    def _draw_enemy_hud(self, surface, cx, cy):
        """Dibuja el nombre del enemigo y las dos barras paralelas de Deltarune: HP y MERCY."""
        is_spared = (self.enemy["mercy"] >= 100)
        name_color = (255, 240, 70) if is_spared else (255, 255, 255)
        prefix = "★ " if is_spared else ""
        lv_tag = f" [NV+{self.lv_bonus}]" if getattr(self, "lv_bonus", 0) > 0 else ""
        txt_name = self.font_hud.render(f"{prefix}{self.enemy['name']}{lv_tag}", False, name_color)
        surface.blit(txt_name, (cx - txt_name.get_width() // 2, cy - 8))

        bw, bh = 58, 5
        bx = cx - bw // 2
        hp_y = cy + 6
        mercy_y = cy + 14

        hp_ratio = max(0.0, min(1.0, self.enemy["hp"] / max(1, self.enemy["max_hp"])))
        pygame.draw.rect(surface, (130, 20, 30), (bx, hp_y, bw, bh))
        if hp_ratio > 0:
            pygame.draw.rect(surface, (85, 235, 95), (bx, hp_y, int(bw * hp_ratio), bh))
        pygame.draw.rect(surface, (255, 255, 255), (bx, hp_y, bw, bh), 1)

        mercy_ratio = max(0.0, min(1.0, self.enemy["mercy"] / 100.0))
        pygame.draw.rect(surface, (110, 45, 25), (bx, mercy_y, bw, bh))
        if mercy_ratio > 0:
            pygame.draw.rect(surface, (255, 230, 60), (bx, mercy_y, int(bw * mercy_ratio), bh))
        pygame.draw.rect(surface, (255, 200, 90), (bx, mercy_y, bw, bh), 1)

        m_lbl = self.font_hud.render(f"MERCY {self.enemy['mercy']}%", False, (255, 230, 75) if is_spared else (210, 185, 150))
        surface.blit(m_lbl, (cx - m_lbl.get_width() // 2, mercy_y + 7))

    def _draw_speech_bubble(self, surface, enemy_x, enemy_y, text):
        """Dibuja el bocadillo de diálogo del enemigo POR ENCIMA de su cabeza sin taparlo jamás."""
        clean_txt = text.lstrip("* ").strip()
        wrapped = self.wrap_text(clean_txt, self.font_dialogue, max_width=112)[:3]
        if not wrapped:
            return
        max_lw = max(self.font_dialogue.size(line)[0] for line in wrapped)
        bw = max_lw + 12
        bh = len(wrapped) * 13 + 8
        # Ubicar estrictamente por encima de la cabeza/sombrero del enemigo (enemy_y - 44)
        # y a la derecha de la arena de combate (self.bullet_box.right + 4)
        bx = min(VIRTUAL_WIDTH - bw - 4, max(self.bullet_box.right + 4, int(enemy_x - bw // 2)))
        by = max(4, int(enemy_y - 44 - bh))
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, bw, bh), border_radius=4)
        pygame.draw.rect(surface, (40, 40, 60), (bx, by, bw, bh), 1, border_radius=4)
        tail_x = min(bx + bw - 8, max(bx + 8, int(enemy_x)))
        pygame.draw.polygon(
            surface,
            (255, 255, 255),
            [(tail_x - 4, by + bh - 1), (tail_x + 4, by + bh - 1), (tail_x, by + bh + 5)],
        )
        for i, line in enumerate(wrapped):
            txt_s = self.font_dialogue.render(line, False, (10, 10, 20))
            surface.blit(txt_s, (bx + 6, by + 4 + i * 13))

    def _draw_bullet_arena(self, surface, ox, oy):
        """Dibuja la arena de esquiva ENTRE Paniel y el enemigo, POR ENCIMA de la barra de vida (y < 148)."""
        box = pygame.Rect(
            int(self.cur_box[0] + ox),
            int(self.cur_box[1] + oy),
            int(self.cur_box[2]),
            int(self.cur_box[3]),
        )
        is_prepping = (self.turn_prep_timer > 0)
        flash_prep = is_prepping and (int(self.anim_time * 16) % 2 == 0)

        # Sombra exterior y borde: ámbar parpadeante durante advertencia previa, verde neón normal
        border_col = (255, 235, 90) if flash_prep else (65, 235, 115)
        shadow_col = (200, 140, 40) if is_prepping else (35, 185, 95)
        pygame.draw.rect(surface, shadow_col, box.inflate(4, 4), 1)
        pygame.draw.rect(surface, (0, 0, 0), box)
        pygame.draw.rect(surface, border_col, box, 2)

        # Letrero de aviso en la parte superior de la arena durante el tiempo de preparación
        if is_prepping and box.height > 60:
            warn_lbl = self.font_hud.render("! ALERTA !", False, (255, 235, 90) if flash_prep else (255, 120, 120))
            surface.blit(warn_lbl, (box.centerx - warn_lbl.get_width() // 2, max(36, box.top - 12)))

        # Recortar estrictamente las balas dentro de la arena para que jamás salgan ni tapen la barra de vida
        prev_clip = surface.get_clip()
        surface.set_clip(box.inflate(-2, -2))

        for sp in self.graze_sparks:
            alpha = int(255 * (sp["life"] / 0.24))
            ps = pygame.Surface((3, 3), pygame.SRCALPHA)
            ps.fill((180, 245, 255, alpha))
            surface.blit(ps, (int(sp["x"] + ox - 1), int(sp["y"] + oy - 1)))

        for psp in self.parry_sparks:
            alpha = int(255 * (psp["life"] / psp["max_life"]))
            ps = pygame.Surface((psp["size"], psp["size"]), pygame.SRCALPHA)
            col = psp["color"]
            ps.fill((col[0], col[1], col[2], alpha))
            surface.blit(ps, (int(psp["x"] + ox - psp["size"] // 2), int(psp["y"] + oy - psp["size"] // 2)))

        for b in self.bullets:
            b.draw(surface)

        sx = int(self.soul_x + ox - 5)
        sy = int(self.soul_y + oy - 5)

        # Aura de protección de spawn mientras el alma es invulnerable
        if self.invulnerable_timer > 0:
            shld_col = (100, 240, 255) if (int(self.anim_time * 16) % 2 == 0) else (255, 235, 120)
            pygame.draw.circle(surface, shld_col, (sx + 5, sy + 5), 10, 1)

        # Ecos expansivos en forma de silueta de corazón (onda de choque estilo Deltarune)
        for echo in self.graze_echoes:
            t = 1.0 - (echo["life"] / echo["max_life"])
            scale = 1.0 + t * 1.35
            alpha = int(240 * (1.0 - t))
            col = (
                int(255 - t * 140),
                int(255 - t * 20),
                255
            )
            ex = int(echo["x"] + ox)
            ey = int(echo["y"] + oy)
            self._draw_heart_silhouette(surface, ex, ey, scale=scale, color=col, alpha=int(alpha * 0.35), is_outline=False)
            self._draw_heart_silhouette(surface, ex, ey, scale=scale, color=col, alpha=alpha, is_outline=True)

        # Silueta inmediata del corazón envolviendo el alma al rozar y cargar TP
        if self.graze_flash_timer > 0:
            pulse_alpha = int(255 * (self.graze_flash_timer / 0.20))
            self._draw_heart_silhouette(surface, sx + 5, sy + 5, scale=1.05, color=(120, 240, 255), alpha=int(pulse_alpha * 0.65), is_outline=False)
            self._draw_heart_silhouette(surface, sx + 5, sy + 5, scale=1.12, color=(255, 255, 255), alpha=pulse_alpha, is_outline=True)

        if self.invulnerable_timer <= 0 or (int(self.anim_time * 20) % 2 == 0):
            self._draw_soul(surface, sx, sy)

        # Texto flotante de Parry exitoso dentro de la arena
        if self.parry_floating_txt and self.parry_floating_life > 0:
            txt_s = self.font_hud.render(self.parry_floating_txt, False, (70, 255, 150))
            sh_s = self.font_hud.render(self.parry_floating_txt, False, (0, 0, 0))
            fx = int(self.parry_floating_pos[0] + ox - txt_s.get_width() // 2)
            fy = int(self.parry_floating_pos[1] + oy)
            surface.blit(sh_s, (fx + 1, fy + 1))
            surface.blit(txt_s, (fx, fy))

        surface.set_clip(prev_clip)

        # Indicador de estado del Parry [Z] debajo de la arena durante el combate
        if box.height > 60:
            if self.parry_active_timer > 0:
                p_text = "[Z] ¡PARRY ACTIVO!"
                p_col = (120, 255, 170) if (int(self.anim_time * 16) % 2 == 0) else (255, 255, 255)
            elif self.parry_cooldown > 0:
                p_text = f"[Z] PARRY: {self.parry_cooldown:.1f}s"
                p_col = (185, 190, 210)
            else:
                p_text = "[Z] PARRY: LISTO"
                p_col = (65, 245, 120)
            parry_lbl = self.font_hud.render(p_text, False, p_col)
            sh_lbl = self.font_hud.render(p_text, False, (0, 0, 0))
            px = box.centerx - parry_lbl.get_width() // 2
            py = min(226, box.bottom + 3)
            surface.blit(sh_lbl, (px + 1, py + 1))
            surface.blit(parry_lbl, (px, py))

    def _draw_deltarune_party_bar(self, surface):
        """Dibuja la barra horizontal de vida y los botones de acción, que bajan durante la pelea."""
        state = self.player.mental_state
        state_col = {
            "FELIZ": (95, 235, 130),
            "TRISTE": (95, 165, 255),
            "TRAUMADO": (200, 105, 245),
            "LOCO": (255, 65, 65),
        }.get(state, (255, 255, 255))

        # Desliza suavemente de y=148 (modo menú) a y=242 (modo pelea) cuando bajan las acciones
        card_y = int(148 + 94 * self.ui_slide)
        card_rect = pygame.Rect(20, card_y, 360, 24)
        pygame.draw.rect(surface, (10, 12, 22), card_rect)
        pygame.draw.line(surface, state_col, (card_rect.left, card_rect.top), (card_rect.right, card_rect.top), 2)
        pygame.draw.line(surface, (55, 60, 85), (card_rect.left, card_rect.bottom - 1), (card_rect.right, card_rect.bottom - 1), 1)

        portrait = self.player.get_stat_portrait() if hasattr(self.player, "get_stat_portrait") else None
        if portrait is not None:
            shake_x = int(math.sin(self.anim_time * 26.0) * 1.5) if state == "LOCO" else 0
            py = card_rect.bottom - 1 - portrait.get_height()
            surface.blit(portrait, (21 + shake_x, py))

        name_s = self.font_hud.render("PANIEL", False, (255, 255, 255))
        state_s = self.font_hud.render(f"[{state}]", False, state_col)
        surface.blit(name_s, (56, card_y + 3))
        surface.blit(state_s, (104, card_y + 3))

        stats_s = self.font_hud.render(f"AT {self.player.effective_attack}  DF {self.player.effective_defense}", False, (200, 210, 235))
        surface.blit(stats_s, (56, card_y + 13))

        hp_lbl = self.font_hud.render("HP", False, (255, 190, 50))
        hp_val = self.font_hud.render(f"{self.player.hp}/{self.player.max_hp}", False, (255, 255, 255))
        surface.blit(hp_lbl, (232, card_y + 3))
        surface.blit(hp_val, (320, card_y + 3))

        bw = 64
        ratio = max(0.0, min(1.0, self.player.hp / max(1, self.player.max_hp)))
        pygame.draw.rect(surface, (135, 20, 30), (252, card_y + 13, bw, 7))
        if ratio > 0:
            pygame.draw.rect(surface, (100, 240, 95), (252, card_y + 13, int(bw * ratio), 7))
        pygame.draw.rect(surface, (255, 255, 255), (252, card_y + 13, bw, 7), 1)

        self._draw_action_buttons(surface)

    def _draw_button_icon(self, surface, idx, x, y, color):
        """Dibuja los iconos pixel-art de Deltarune (Espada, Magia/Act, Bolsa, Destello, Escudo)."""
        if idx == 0:
            pygame.draw.line(surface, color, (x + 2, y + 10), (x + 10, y + 2), 2)
            pygame.draw.line(surface, color, (x + 2, y + 6), (x + 6, y + 10), 2)
        elif idx == 1:
            pygame.draw.circle(surface, color, (x + 6, y + 6), 5, 1)
            pygame.draw.line(surface, color, (x + 6, y + 3), (x + 6, y + 9), 1)
            pygame.draw.line(surface, color, (x + 3, y + 6), (x + 9, y + 6), 1)
        elif idx == 2:
            pygame.draw.rect(surface, color, (x + 3, y + 4, 7, 7), 1)
            pygame.draw.line(surface, color, (x + 4, y + 2), (x + 8, y + 2), 2)
        elif idx == 3:
            pygame.draw.line(surface, color, (x + 6, y + 1), (x + 6, y + 11), 2)
            pygame.draw.line(surface, color, (x + 1, y + 6), (x + 11, y + 6), 2)
        elif idx == 4:
            pts = [(x + 6, y + 1), (x + 11, y + 3), (x + 9, y + 10), (x + 6, y + 12), (x + 3, y + 10), (x + 1, y + 3)]
            pygame.draw.polygon(surface, color, pts, 1)

    def _draw_action_buttons(self, surface):
        btn_w = 68
        btn_h = 24
        start_x = 20
        # Desliza de y=250 (modo menú) a y=270 (modo pelea en el borde inferior)
        by = int(250 + 20 * self.ui_slide)
        gap = 5

        for i, name in enumerate(self.btn_names):
            bx = start_x + i * (btn_w + gap)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            is_sel = (i == self.selected_btn and self.state == "MENU")
            color = self.btn_colors[i] if is_sel else (150, 110, 65)
            bg_col = (32, 20, 42) if is_sel else (12, 10, 20)

            pygame.draw.rect(surface, bg_col, rect, border_radius=3)
            pygame.draw.rect(surface, color, rect, 2 if is_sel else 1, border_radius=3)

            self._draw_button_icon(surface, i, bx + 5, by + 6, color)
            txt = self.font_hud.render(name, False, (255, 245, 160) if is_sel else color)
            surface.blit(txt, (bx + 20, by + 6))

    def _draw_dialogue_and_submenus(self, surface, empty_box=False):
        box = self.default_box
        pygame.draw.rect(surface, (0, 0, 0), box)
        pygame.draw.rect(surface, (110, 65, 210), box.inflate(2, 2), 1)
        pygame.draw.rect(surface, (255, 255, 255), box, 2)
        inner = box.inflate(-6, -6)
        pygame.draw.rect(surface, (45, 35, 75), inner, 1)

        if empty_box:
            return

        prev_clip = surface.get_clip()
        surface.set_clip(box.inflate(-6, -6))

        if self.state == "ENEMY_TURN":
            hint1 = self.font_dialogue.render("* ¡Esquiva los proyectiles en la arena!", False, (190, 235, 205))
            hint2 = self.font_dialogue.render("* [Z] Parry (Alma Verde, CD 5s, +16% TP). [X/Shift] Precisión.", False, (95, 245, 130))
            hint3 = self.font_dialogue.render("* Rozar proyectiles (Graze) también carga tu barra de TP.", False, (255, 210, 120))
            surface.blit(hint1, (box.x + 12, box.y + 10))
            surface.blit(hint2, (box.x + 12, box.y + 28))
            surface.blit(hint3, (box.x + 12, box.y + 46))
            surface.set_clip(prev_clip)
            return

        if self.state in ["INTRO", "MENU", "ACTION_TEXT", "VICTORY", "SPARE_VICTORY"]:
            wrapped_lines = self.wrap_text(self.action_message, self.font_dialogue, max_width=box.width - 24)
            ty = box.y + 8
            for line in wrapped_lines[:4]:
                t = self.font_dialogue.render(line, False, (255, 255, 255))
                surface.blit(t, (box.x + 12, ty))
                ty += 14

            if self.state in ["ACTION_TEXT", "VICTORY", "SPARE_VICTORY"]:
                if int(self.anim_time * 4) % 2 == 0:
                    nxt = self.font_hud.render("[Z] ▼", False, (255, 235, 80))
                    surface.blit(nxt, (box.right - nxt.get_width() - 8, box.bottom - 15))

        elif self.state == "SUBMENU_ACT":
            acts = self._get_act_options()
            for i, act in enumerate(acts[:8]):
                col = i % 2
                row = i // 2
                ax = box.x + 10 + col * 176
                ay = box.y + 6 + row * 15
                is_sel = (i == self.submenu_idx)
                tp_cost = act.get("tp_cost", 0)
                is_bf = (act.get("type") == "TP_BLACK_FLASH")

                if is_sel:
                    self._draw_soul(surface, ax, ay + 1)

                if tp_cost > 0:
                    can_cast = (self.tp >= tp_cost)
                    if is_bf and can_cast:
                        c = (255, 235, 90) if is_sel else (255, 70, 120)
                    else:
                        c = (255, 235, 80) if (is_sel and can_cast) else ((255, 165, 65) if can_cast else (110, 105, 120))
                else:
                    c = (255, 240, 90) if is_sel else (230, 235, 245)

                lbl = self.font_dialogue.render(act["name"], False, c)
                surface.blit(lbl, (ax + 14, ay))

        elif self.state == "SUBMENU_ITEM":
            items = self.player.inventory
            for i, it in enumerate(items[:3]):
                iy = box.y + 10 + i * 19
                if i == self.submenu_idx:
                    self._draw_soul(surface, box.x + 12, iy + 1)
                san_txt = f", +{it.get('sanity_heal', 0)}% Cord." if it.get("sanity_heal", 0) > 0 else ""
                lbl = self.font_dialogue.render(
                    f"{it['name']} (+{it['heal']} HP{san_txt})",
                    False,
                    (255, 240, 100) if i == self.submenu_idx else (225, 230, 240),
                )
                surface.blit(lbl, (box.x + 26, iy))

        surface.set_clip(prev_clip)

    def _draw_attack_meter(self, surface):
        """Dibuja la barra de ataque de Deltarune dentro del panel inferior."""
        m = self.meter_rect
        portrait = self.player.get_stat_portrait() if hasattr(self.player, "get_stat_portrait") else None
        if portrait is not None:
            p_frame = pygame.Rect(m.left - 11, m.centery - 17, 34, 34)
            pygame.draw.rect(surface, (18, 12, 32), p_frame, border_radius=2)
            surface.blit(portrait, (p_frame.x + 1, p_frame.y + 1))
            pygame.draw.rect(surface, (110, 70, 200), p_frame, 1, border_radius=2)

        track_rect = pygame.Rect(m.left + 24, m.top + 8, m.width - 32, m.height - 16)
        pygame.draw.rect(surface, (18, 12, 32), track_rect)
        pygame.draw.rect(surface, (110, 70, 200), track_rect, 2)

        t_box = pygame.Rect(self.target_x - 8, track_rect.top + 2, 16, track_rect.height - 4)
        pygame.draw.rect(surface, (40, 90, 180), t_box)
        pygame.draw.rect(surface, (100, 225, 255), t_box, 2)
        pygame.draw.line(surface, (255, 255, 255), (self.target_x, t_box.top + 2), (self.target_x, t_box.bottom - 2), 2)

        for a in self.afterimages:
            ax = int(a["x"])
            s = pygame.Surface((6, track_rect.height - 4), pygame.SRCALPHA)
            s.fill((140, 200, 255, int(max(0, min(255, a["alpha"])))))
            surface.blit(s, (ax - 3, track_rect.top + 2))

        cx = int(self.cursor_x)
        bar_col = (255, 235, 70) if self.attack_hit else (255, 255, 255)
        pygame.draw.rect(surface, bar_col, (cx - 3, track_rect.top, 6, track_rect.height))

        if self.attack_rating:
            r_col = (255, 235, 75) if "150" in self.attack_rating else (120, 230, 255)
            r_s = self.font_hud.render(self.attack_rating, False, r_col)
            surface.blit(r_s, (track_rect.centerx - r_s.get_width() // 2, track_rect.top - 13))
        else:
            hint_s = self.font_hud.render("¡Pulsa [Z] en la mira azul!", False, (190, 205, 240))
            surface.blit(hint_s, (track_rect.centerx - hint_s.get_width() // 2, track_rect.top - 13))

    def _draw_floating_damage(self, surface):
        fx, fy = int(self.floating_dmg_pos[0]), int(self.floating_dmg_pos[1])
        txt_str = str(self.floating_dmg)
        sh_txt = self.font_hud.render(txt_str, False, (0, 0, 0))
        txt = self.font_hud.render(txt_str, False, self.floating_dmg_color)
        surface.blit(sh_txt, (fx - txt.get_width() // 2 + 1, fy + 1))
        surface.blit(txt, (fx - txt.get_width() // 2, fy))

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        for sh in self.soul_shards:
            pygame.draw.rect(surface, (255, 40, 40), (int(sh["x"]), int(sh["y"]), 3, 3))

        if self.game_over_timer > 0.8:
            title = self.font_hud.render("FIN DEL JUEGO", False, (220, 220, 220))
            surface.blit(title, (VIRTUAL_WIDTH // 2 - title.get_width() // 2, 80))

            dc = self.player.death_count
            if dc == 1:
                meta_line = "* ...Ah. Es la primera vez que la muerte me alcanza."
                meta_sub = "* (Paniel mira sus manos sintiendo el frío del más allá)"
            elif dc == 2:
                meta_line = f"* ...Ya van {dc} muertes. Puedo recordar cada instante."
                meta_sub = "* (Sus pupilas tiemblan... la cordura se resquebraja)"
            elif dc <= 5:
                meta_line = f"* {dc} muertes. {dc} veces destrozado y de vuelta al umbral."
                meta_sub = "* (Una risa ahogada y temblorosa se escapa de su pecho)"
            elif dc <= 10:
                meta_line = f"* Muerte número {dc}... ¿El cementerio es mi verdadero hogar?"
                meta_sub = "* (La locura empieza a devorar la noción del dolor)"
            else:
                meta_line = f"* ¡¡{dc} VECES MUERTO!! ¡¡JAJAJAJA YA NI PUEDO MORIR BIEN!!"
                meta_sub = "* (Sus ojos inyectados en sangre brillan con delirio puro)"

            q1 = self.font_dialogue.render(meta_line, False, (255, 245, 100))
            q_sub = self.font_dialogue.render(meta_sub, False, (210, 200, 225))
            q2 = self.font_hud.render(f"★ [Z] Rehusar el fin (Muertes: {dc}) ★", False, (255, 255, 255))
            surface.blit(q1, (VIRTUAL_WIDTH // 2 - q1.get_width() // 2, 118))
            surface.blit(q_sub, (VIRTUAL_WIDTH // 2 - q_sub.get_width() // 2, 138))
            surface.blit(q2, (VIRTUAL_WIDTH // 2 - q2.get_width() // 2, 175))

    def _draw_soul(self, surface, x, y, color=None):
        """Dibuja el corazón pixelado de Undertale/Deltarune (11x10, proporción clásica no alargada).
        Si el Parry con [Z] está activo, se vuelve de color verde (COLOR_SOUL_GREEN) con un escudo vibrante."""
        c = color if color is not None else (COLOR_SOUL_GREEN if self.parry_active_timer > 0 else COLOR_SOUL_RED)
        pygame.draw.rect(surface, c, (x + 1, y, 3, 1))
        pygame.draw.rect(surface, c, (x + 7, y, 3, 1))
        pygame.draw.rect(surface, c, (x, y + 1, 5, 1))
        pygame.draw.rect(surface, c, (x + 6, y + 1, 5, 1))
        pygame.draw.rect(surface, c, (x, y + 2, 11, 3))
        pygame.draw.rect(surface, c, (x + 1, y + 5, 9, 1))
        pygame.draw.rect(surface, c, (x + 2, y + 6, 7, 1))
        pygame.draw.rect(surface, c, (x + 3, y + 7, 5, 1))
        pygame.draw.rect(surface, c, (x + 4, y + 8, 3, 1))
        pygame.draw.rect(surface, c, (x + 5, y + 9, 1, 1))

        if self.parry_active_timer > 0 and color is None:
            pulse = (math.sin(self.anim_time * 28.0) + 1.0) * 0.5
            rad = int(8 + pulse * 4)
            pygame.draw.circle(surface, (140, 255, 180), (x + 5, y + 5), rad, 1)
            pygame.draw.circle(surface, (255, 255, 255), (x + 5, y + 5), max(4, rad - 3), 1)

    def _init_soul_silhouette_surfaces(self):
        """Genera las superficies base del corazón y su silueta de contorno para el efecto Graze de Deltarune."""
        self.base_heart_surf = pygame.Surface((11, 10), pygame.SRCALPHA)
        heart_rects = [
            (1, 0, 3, 1), (7, 0, 3, 1),
            (0, 1, 5, 1), (6, 1, 5, 1),
            (0, 2, 11, 3),
            (1, 5, 9, 1),
            (2, 6, 7, 1),
            (3, 7, 5, 1),
            (4, 8, 3, 1),
            (5, 9, 1, 1),
        ]
        for r in heart_rects:
            pygame.draw.rect(self.base_heart_surf, (255, 255, 255, 255), r)

        self.outline_heart_surf = pygame.Surface((13, 12), pygame.SRCALPHA)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    self.outline_heart_surf.blit(self.base_heart_surf, (1 + dx, 1 + dy))
        for x in range(11):
            for y in range(10):
                if self.base_heart_surf.get_at((x, y))[3] > 0:
                    self.outline_heart_surf.set_at((1 + x, 1 + y), (0, 0, 0, 0))

    def _draw_heart_silhouette(self, surface, cx, cy, scale=1.0, color=(255, 255, 255), alpha=255, is_outline=True):
        """Dibuja la silueta o contorno del corazón del alma escalada y teñida."""
        if alpha <= 0:
            return
        src = self.outline_heart_surf if is_outline else self.base_heart_surf
        ow, oh = src.get_size()
        nw = max(1, int(round(ow * scale)))
        nh = max(1, int(round(oh * scale)))
        scaled = pygame.transform.scale(src, (nw, nh))
        tint = pygame.Surface((nw, nh), pygame.SRCALPHA)
        tint.fill((*color[:3], int(max(0, min(255, alpha)))))
        scaled.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(scaled, (int(round(cx - nw / 2.0)), int(round(cy - nh / 2.0))))

