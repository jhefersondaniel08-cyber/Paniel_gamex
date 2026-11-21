import math
import random
import pygame
from objetos_mundo import WorldObject

# ==========================================================
# SISTEMA DE COMBATE Y ENEMIGOS ESTILO DELTARUNE
# ==========================================================

# 1. PLANTILLAS DE ENEMIGOS INVENTADOS (Con estadísticas similares o superiores)
ENEMY_TEMPLATES = {
    "sombra": {
        "id": "sombra",
        "name": "Sombra Sombría",
        "hp": 24,
        "max_hp": 24,
        "attack": 11,
        "defense": 2,
        "exp": 25,
        "color": (160, 100, 240),
        "intro_text": "* ¡Sombra Sombría bloquea el camino con una reverencia elegante!",
        "quotes": [
            "* ¿Viste mi sombrero nuevo?",
            "* ¡Las sombras bailan al compás!",
            "* ¡A ver si puedes seguirme el ritmo!",
            "* ¡No pises mi capa oscura!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* SOMBRA SOMBRÍA - ATK 11 DEF 2\n* Un elegante ser de las sombras con un sombrero impecable.\n* Le encantan los espectáculos y el respeto.",
                "mercy": 0,
            },
            {
                "name": "Reverencia",
                "text": "* Haces una reverencia impecable al estilo de la nobleza.\n* ¡Sombra Sombría se quita el sombrero halagado!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Hacer Truco",
                "text": "* Haces un truco de magia haciendo desaparecer una moneda.\n* ¡Sus ojos brillan fascinados por la ilusión!\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["shadow_rain", "shadow_spiral"],
    },
    "rudinn": {
        "id": "rudinn",
        "name": "Rudinnito",
        "hp": 26,
        "max_hp": 26,
        "attack": 12,
        "defense": 3,
        "exp": 32,
        "color": (60, 220, 150),
        "intro_text": "* ¡Rudinnito adopta guardia con su estoque reluciente!",
        "quotes": [
            "* ¡Por la corona y el reino!",
            "* ¡Mi armadura no tiene ni un rasguño!",
            "* ¡En guardia, forastero!",
            "* ¡Cuidado con el filo de cristal!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* RUDINNITO - ATK 12 DEF 3\n* Caballero esmeralda con armadura de gemas.\n* Presume mucho de su deber y disciplina real.",
                "mercy": 0,
            },
            {
                "name": "Elogiar Joya",
                "text": "* Elogias el brillo pulido de su armadura de esmeralda.\n* ¡Rudinnito se ruboriza con orgullo y la limpia!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Ofrecer Tregua",
                "text": "* Le ofreces un apretón de manos cordial y sincero.\n* Rudinnito suspira con alivio y baja su estoque.\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["diamond_swords", "crossfire_diamonds"],
    },
    "fantasmino": {
        "id": "fantasmino",
        "name": "Fantasmino",
        "hp": 22,
        "max_hp": 22,
        "attack": 10,
        "defense": 2,
        "exp": 22,
        "color": (120, 220, 255),
        "intro_text": "* ¡Fantasmino flota escuchando su mixtape a todo volumen!",
        "quotes": [
            "* ♪ El bajo está a punto de caer... ♪",
            "* ¡Sube el volumen del sintetizador!",
            "* ¿Sientes la vibración del ritmo?",
            "* ¡Esta pista es puro fuego retro!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* FANTASMINO - ATK 10 DEF 2\n* Espíritu melómano de Hometown.\n* Quiere que todos bailen al compás de su música.",
                "mercy": 0,
            },
            {
                "name": "Silbar Canción",
                "text": "* Silbas el tema principal del pueblo.\n* ¡Fantasmino empieza a tararear en perfecta armonía!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Aplaudir Ritmo",
                "text": "* Sigues el compás con aplausos enérgicos.\n* ¡Fantasmino baila flotando en círculos!\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["bouncing_notes", "sound_arcs"],
    },
    "sectario": {
        "id": "sectario",
        "name": "Acólito del Eclipse",
        "hp": 30,
        "max_hp": 30,
        "attack": 12,
        "defense": 3,
        "exp": 36,
        "color": (215, 50, 95),
        "intro_text": "* ¡Un Acólito del Eclipse emerge entre las sombras murmurando un cántico prohibido!",
        "quotes": [
            "* ¡El Eclipse Carmesí todo lo ve!",
            "* ¡Únete al coro del Abismo!",
            "* ¡Nuestras dagas sellarán tu destino!",
            "* ¡Bajo esta capucha solo existe el rito!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* ACÓLITO DEL ECLIPSE - ATK 12 DEF 3\n* Miembro encapuchado de la secta secreta del cementerio.\n* Invoca dagas rituales y sellos desde su grimorio oscuro.",
                "mercy": 0,
            },
            {
                "name": "Recitar Runa",
                "text": "* Recitas en voz baja un verso antiguo de la Runa Delta.\n* ¡El Acólito te mira asombrado creyendo que eres un iniciado!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Gesto Ritual",
                "text": "* Cruzas los brazos haciendo el saludo silencioso de la secta.\n* El Acólito inclina su capucha con solemne reverencia.\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["cult_daggers", "blood_sigil"],
    },
    "sepulturero": {
        "id": "sepulturero",
        "name": "Morvath el Sepulturero",
        "is_boss": True,
        "hp": 110,
        "max_hp": 110,
        "attack": 15,
        "defense": 4,
        "exp": 180,
        "color": (235, 65, 90),
        "intro_text": "* ¡¡MORVATH, EL SEPULTURERO ETERNO, blande su guadaña fúnebre ante el Mausoleo!!",
        "quotes": [
            "* ¡Tu tumba lleva siglos esperando!",
            "* ¡Cada muerte tuya alimenta mi farol!",
            "* ¡¡Siente el corte de mi guadaña bumerán!!",
            "* ¡Las campanas fúnebres doblan por tu alma!",
            "* ¡¡Nadie escapa del Juicio del Sepulturero!!",
            "* ¡La tierra remueve los huesos de los caídos!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* MORVATH EL SEPULTURERO - ATK 15 DEF 4 (JEFE DEL CEMENTERIO)\n* Guardián ancestral que custodia las puertas del Mausoleo.\n* Blande guadañas bumerán, ondas de campana fúnebre y lluvia de ánimas.",
                "mercy": 0,
            },
            {
                "name": "Recordar Nombre",
                "text": "* Pronuncias su antiguo nombre con solemne respeto.\n* ¡La llama del farol de Morvath tiembla con nostalgia!\n* (Piedad +25%)",
                "mercy": 25,
            },
            {
                "name": "Ofrecer Paz",
                "text": "* Le dices que su vigilia eterna ya ha cumplido su deber.\n* Morvath baja lentamente su guadaña-pala ancestral.\n* (Piedad +35%)",
                "mercy": 35,
            },
        ],
        "patterns": [
            "scythe_sweep",
            "soul_lantern_ring",
            "grave_pillars",
            "death_scythe_boomerang",
            "funeral_bell_toll",
            "graveyard_cataclysm",
            "frenzy_soul_hunt",
        ],
    },
    "arconte": {
        "id": "arconte",
        "name": "Vaelkor, Rey del Cristal Negro",
        "is_boss": True,
        "hp": 165,
        "max_hp": 165,
        "attack": 19,
        "defense": 5,
        "exp": 350,
        "color": (255, 35, 95),
        "intro_text": "* ¡¡VAELKOR, REY DEL CRISTAL NEGRO, quiebra el espacio con Fuego Oscuro!!",
        "quotes": [
            "* ¡El cristal de esta realidad ya se ha roto!",
            "* ¡¡Arde en el Vórtice del Fuego Oscuro!!",
            "* ¡¡Ni tu BlackFlash podrá salvar tu alma!!",
            "* ¡¡Las esquirlas dimensionales te consumirán!!",
            "* ¡¡Siente la gravedad del Eclipse Supremo!!",
            "* ¡La realidad se fragmenta ante tu mirada!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* VAELKOR, REY DEL CRISTAL NEGRO - ATK 19 DEF 5 (JEFE SUPREMO)\n* Soberano del Santuario del Cristal Quebrado.\n* Domina vórtices gravitacionales, láseres cruzados y fracturas de cristal negro.",
                "mercy": 0,
            },
            {
                "name": "Desafiar Destino",
                "text": "* Mantienes la mirada firme frente a las grietas de cristal oscuro.\n* ¡Vaelkor reconoce tu determinación inquebrantable!\n* (Piedad +20%)",
                "mercy": 20,
            },
            {
                "name": "Sellar Grieta",
                "text": "* Canalizas el brillo de tu Alma para apaciguar el Fuego Oscuro.\n* Las esquirlas de cristal alrededor de Vaelkor dejan de vibrar.\n* (Piedad +30%)",
                "mercy": 30,
            },
        ],
        "patterns": [
            "black_flame_barrage",
            "crystal_shatter_storm",
            "void_cleave_laser",
            "eclipse_gravity_vortex",
            "fractured_mirror_barrage",
            "abyssal_cross_lasers",
            "apocalypse_crystal_rain",
        ],
    },
}


# 2. ENEMIGO SUELTO EN EL MAPA (Overworld) CON PATRULLA, ALERTA Y PERSECUCIÓN
class OverworldEnemy(WorldObject):
    def __init__(self, x, y, template_id):
        super().__init__(x, y, depth_y=y + 26)
        self.template_id = template_id
        self.template = ENEMY_TEMPLATES[template_id]
        self.is_boss = self.template.get("is_boss", False)
        self.w = 34 if self.is_boss else 22
        self.h = 42 if self.is_boss else 28
        self.hitbox_w = 24 if self.is_boss else 16
        self.hitbox_h = 14 if self.is_boss else 10

        self.state = "WANDER"  # WANDER, ALERT, CHASE
        self.speed_wander = 22.0 if self.is_boss else 38.0
        self.speed_chase = 66.0 if self.is_boss else 74.0

        self.move_dir = [0.0, 0.0]
        self.move_timer = random.uniform(0.5, 2.0)
        self.pause_timer = 0.0

        self.alert_timer = 0.0
        self.anim_timer = 0.0
        self.anim_frame = 0

    @property
    def hitbox(self):
        return pygame.Rect(
            int(self.x + (self.w - self.hitbox_w) / 2),
            int(self.y + self.h - self.hitbox_h - 1),
            self.hitbox_w,
            self.hitbox_h,
        )

    def update(self, dt, player_center, solid_rects, is_void_func=None):
        self.depth_y = self.y + self.h
        self.anim_timer += dt
        if self.anim_timer >= 0.16:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

        pcx, pcy = player_center
        my_cx = self.x + self.w / 2
        my_cy = self.y + self.h / 2
        dist_to_player = math.hypot(pcx - my_cx, pcy - my_cy)

        # Transición de estados de IA
        if self.state == "WANDER":
            if dist_to_player < 78:
                self.state = "ALERT"
                self.alert_timer = 0.38
                self.move_dir = [0.0, 0.0]
        elif self.state == "ALERT":
            self.alert_timer -= dt
            if self.alert_timer <= 0:
                self.state = "CHASE"
        elif self.state == "CHASE":
            if dist_to_player > 145:
                self.state = "WANDER"
                self.move_timer = random.uniform(1.0, 2.2)

        # Movimiento
        dx, dy = 0.0, 0.0
        if self.state == "CHASE":
            if dist_to_player > 2:
                dx = (pcx - my_cx) / dist_to_player * self.speed_chase * dt
                dy = (pcy - my_cy) / dist_to_player * self.speed_chase * dt
        elif self.state == "WANDER":
            if self.pause_timer > 0:
                self.pause_timer -= dt
            else:
                self.move_timer -= dt
                if self.move_timer <= 0:
                    if random.random() < 0.35:
                        self.pause_timer = random.uniform(0.6, 1.4)
                        self.move_dir = [0.0, 0.0]
                    else:
                        angle = random.uniform(0, 2 * math.pi)
                        self.move_dir = [math.cos(angle), math.sin(angle)]
                        self.move_timer = random.uniform(1.2, 2.8)
                dx = self.move_dir[0] * self.speed_wander * dt
                dy = self.move_dir[1] * self.speed_wander * dt

        if dx != 0 or dy != 0:
            old_x = self.x
            self.x += dx
            rx = self.hitbox
            col_x = any(rx.colliderect(s) for s in solid_rects)
            if col_x or (is_void_func and is_void_func(self.hitbox.centerx, self.hitbox.bottom - 2)):
                self.x = old_x
                if self.state == "WANDER":
                    self.move_dir[0] *= -1

            old_y = self.y
            self.y += dy
            ry = self.hitbox
            col_y = any(ry.colliderect(s) for s in solid_rects)
            if col_y or (is_void_func and is_void_func(self.hitbox.centerx, self.hitbox.bottom - 2)):
                self.y = old_y
                if self.state == "WANDER":
                    self.move_dir[1] *= -1

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        shadow = pygame.Surface((16, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 95), (0, 0, 16, 6))
        surface.blit(shadow, (cx + (self.w - 16) // 2, cy + self.h - 5))

        bob = int(math.sin(self.anim_frame * math.pi / 2) * 2)
        if self.template_id == "sombra":
            self._draw_sombra_overworld(surface, cx, cy + bob)
        elif self.template_id == "rudinn":
            self._draw_rudinn_overworld(surface, cx, cy + bob)
        elif self.template_id == "fantasmino":
            self._draw_fantasmino_overworld(surface, cx, cy + bob)
        elif self.template_id == "sectario":
            self._draw_sectario_overworld(surface, cx, cy + bob)
        elif self.template_id == "sepulturero":
            self._draw_sepulturero_overworld(surface, cx, cy + bob)
        elif self.template_id == "arconte":
            self._draw_arconte_overworld(surface, cx, cy + bob)

        # Burbuja de exclamación [!] estilo Deltarune
        if self.state == "ALERT" or (self.state == "CHASE" and self.alert_timer > -0.3):
            self._draw_alert_bubble(surface, cx + self.w // 2, cy - 8)

    def _draw_alert_bubble(self, surface, bx, by):
        pygame.draw.circle(surface, (255, 50, 50), (bx, by), 7)
        pygame.draw.circle(surface, (255, 255, 255), (bx, by), 7, 1)
        pygame.draw.line(surface, (255, 255, 255), (bx, by - 4), (bx, by + 1), 2)
        pygame.draw.circle(surface, (255, 255, 255), (bx, by + 3), 1)

    def _draw_sombra_overworld(self, surface, cx, cy):
        body_rect = pygame.Rect(cx + 3, cy + 6, 16, 18)
        pygame.draw.rect(surface, (35, 25, 55), body_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 240, 50), (cx + 6, cy + 10, 3, 3))
        pygame.draw.rect(surface, (255, 240, 50), (cx + 13, cy + 10, 3, 3))
        pygame.draw.rect(surface, (20, 15, 30), (cx + 6, cy + 1, 10, 6), border_radius=1)
        pygame.draw.rect(surface, (220, 50, 60), (cx + 6, cy + 5, 10, 2))
        pygame.draw.line(surface, (20, 15, 30), (cx + 4, cy + 7), (cx + 17, cy + 7), 2)

    def _draw_rudinn_overworld(self, surface, cx, cy):
        pts = [(cx + 11, cy + 2), (cx + 19, cy + 14), (cx + 11, cy + 24), (cx + 3, cy + 14)]
        pygame.draw.polygon(surface, (40, 175, 120), pts)
        pygame.draw.polygon(surface, (120, 240, 180), [(p[0] * 0.7 + (cx + 11) * 0.3, p[1] * 0.7 + (cy + 14) * 0.3) for p in pts])
        pygame.draw.rect(surface, (255, 255, 255), (cx + 9, cy + 10, 4, 3))
        pygame.draw.line(surface, (200, 230, 255), (cx + 17, cy + 10), (cx + 21, cy + 4), 2)
        pygame.draw.circle(surface, (255, 215, 0), (cx + 17, cy + 10), 2)

    def _draw_fantasmino_overworld(self, surface, cx, cy):
        ghost_surf = pygame.Surface((20, 22), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surf, (150, 230, 255, 210), (10, 8), 8)
        pygame.draw.rect(ghost_surf, (150, 230, 255, 210), (2, 8, 16, 10))
        pygame.draw.circle(ghost_surf, (150, 230, 255, 210), (5, 17), 3)
        pygame.draw.circle(ghost_surf, (150, 230, 255, 210), (10, 17), 3)
        pygame.draw.circle(ghost_surf, (150, 230, 255, 210), (15, 17), 3)
        pygame.draw.circle(ghost_surf, (20, 40, 60), (7, 8), 2)
        pygame.draw.circle(ghost_surf, (20, 40, 60), (13, 8), 2)
        pygame.draw.arc(ghost_surf, (230, 50, 70), (2, 1, 16, 12), 0, math.pi, 2)
        pygame.draw.rect(ghost_surf, (230, 50, 70), (1, 6, 3, 6), border_radius=1)
        pygame.draw.rect(ghost_surf, (230, 50, 70), (16, 6, 3, 6), border_radius=1)
        surface.blit(ghost_surf, (cx + 1, cy + 2))

    def _draw_sectario_overworld(self, surface, cx, cy):
        """Dibuja al Acólito Encapuchado de la secta en el mapa."""
        # Túnica larga púrpura/carmesí oscura
        robe_pts = [(cx + 6, cy + 8), (cx + 16, cy + 8), (cx + 20, cy + 25), (cx + 2, cy + 25)]
        pygame.draw.polygon(surface, (42, 16, 48), robe_pts)
        pygame.draw.polygon(surface, (195, 40, 80), robe_pts, 1)
        # Estola ritual vertical en el pecho
        pygame.draw.line(surface, (215, 50, 85), (cx + 11, cy + 10), (cx + 11, cy + 24), 2)
        # Capucha puntiaguda de secta que oculta el rostro en sombra
        hood_pts = [(cx + 11, cy - 1), (cx + 18, cy + 6), (cx + 17, cy + 12), (cx + 5, cy + 12), (cx + 4, cy + 6)]
        pygame.draw.polygon(surface, (30, 10, 36), hood_pts)
        pygame.draw.polygon(surface, (185, 40, 75), hood_pts, 1)
        pygame.draw.circle(surface, (10, 6, 14), (cx + 11, cy + 8), 4)
        # Ojos rojos brillantes bajo la capucha
        pygame.draw.rect(surface, (255, 65, 90), (cx + 8, cy + 7, 2, 2))
        pygame.draw.rect(surface, (255, 65, 90), (cx + 12, cy + 7, 2, 2))

    def _draw_sepulturero_overworld(self, surface, cx, cy):
        """Dibuja al Jefe Morvath el Sepulturero en el mapa del Abismo del Cementerio."""
        # Aura carmesí/violeta en el suelo bajo el jefe
        aura = pygame.Surface((40, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (180, 35, 70, 95), (0, 0, 40, 16))
        pygame.draw.ellipse(aura, (255, 90, 120, 150), (2, 2, 36, 12), 1)
        surface.blit(aura, (cx - 3, cy + 28))

        # Manto real rasgado oscuro
        cloak_pts = [(cx + 8, cy + 10), (cx + 26, cy + 10), (cx + 31, cy + 38), (cx + 17, cy + 40), (cx + 3, cy + 38)]
        pygame.draw.polygon(surface, (28, 18, 38), cloak_pts)
        pygame.draw.polygon(surface, (165, 45, 75), cloak_pts, 1)

        # Hombreras de hierro gótico
        pygame.draw.ellipse(surface, (75, 75, 92), (cx + 3, cy + 10, 11, 7))
        pygame.draw.ellipse(surface, (75, 75, 92), (cx + 20, cy + 10, 11, 7))

        # Capucha y corona de espinas de hierro
        pygame.draw.circle(surface, (20, 14, 28), (cx + 17, cy + 8), 8)
        pygame.draw.polygon(surface, (190, 175, 120), [(cx + 11, cy + 3), (cx + 13, cy - 3), (cx + 17, cy + 1), (cx + 21, cy - 3), (cx + 23, cy + 3)])
        # Ojos llameantes carmesí/amarillo
        pygame.draw.rect(surface, (255, 230, 70), (cx + 13, cy + 7, 3, 3))
        pygame.draw.rect(surface, (255, 230, 70), (cx + 19, cy + 7, 3, 3))

        # Guadaña-Pala en la mano derecha
        pygame.draw.line(surface, (120, 90, 65), (cx + 2, cy + 36), (cx + 6, cy + 2), 2)
        pygame.draw.polygon(surface, (200, 210, 230), [(cx + 6, cy + 2), (cx + 17, cy + 5), (cx + 8, cy + 9)])

        # Farol de Almas brillante en la mano izquierda
        pygame.draw.line(surface, (90, 90, 110), (cx + 29, cy + 14), (cx + 32, cy + 20), 1)
        pygame.draw.rect(surface, (45, 40, 55), (cx + 29, cy + 20, 7, 9), border_radius=1)
        pygame.draw.circle(surface, (100, 235, 255), (cx + 32, cy + 24), 3)

    def _draw_arconte_overworld(self, surface, cx, cy):
        """Dibuja al Jefe Supremo Vaelkor, Rey del Cristal Negro en el mapa con llamas oscuras."""
        # Aura de Fuego Oscuro con borde negro bajo sus pies
        aura = pygame.Surface((46, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (0, 0, 0, 200), (0, 0, 46, 18))
        pygame.draw.ellipse(aura, (220, 25, 80, 160), (2, 2, 42, 14))
        pygame.draw.ellipse(aura, (25, 5, 40, 220), (6, 4, 34, 10))
        surface.blit(aura, (cx - 6, cy + 28))

        # Alas / esquirlas de cristal roto flotando tras su espalda
        for ox, oy in [(-5, 6), (31, 6), (-3, 18), (29, 18)]:
            shard = [(cx + ox + 4, cy + oy - 5), (cx + ox + 8, cy + oy + 2), (cx + ox + 4, cy + oy + 8), (cx + ox, cy + oy + 2)]
            pygame.draw.polygon(surface, (235, 40, 95), shard)
            pygame.draw.polygon(surface, (0, 0, 0), shard, 2)

        # Manto imperial de obsidiana con borde negro y carmesí
        cloak_pts = [(cx + 7, cy + 9), (cx + 27, cy + 9), (cx + 33, cy + 39), (cx + 17, cy + 42), (cx + 1, cy + 39)]
        pygame.draw.polygon(surface, (16, 6, 26), cloak_pts)
        pygame.draw.polygon(surface, (240, 40, 95), cloak_pts, 2)
        pygame.draw.polygon(surface, (0, 0, 0), cloak_pts, 1)

        # Cabeza y Corona de Cristal Quebrado
        pygame.draw.circle(surface, (10, 4, 16), (cx + 17, cy + 7), 8)
        crown = [(cx + 8, cy + 3), (cx + 10, cy - 6), (cx + 14, cy), (cx + 17, cy - 9), (cx + 20, cy), (cx + 24, cy - 6), (cx + 26, cy + 3)]
        pygame.draw.polygon(surface, (240, 35, 90), crown)
        pygame.draw.polygon(surface, (0, 0, 0), crown, 1)

        # 4 ojos carmesí ardientes
        for ex, ey in [(cx + 12, cy + 5), (cx + 20, cy + 5), (cx + 13, cy + 8), (cx + 19, cy + 8)]:
            pygame.draw.rect(surface, (255, 60, 110), (ex, ey, 2, 2))

        # Mandoble de Fuego Oscuro y Cristal
        blade = [(cx + 31, cy - 6), (cx + 36, cy + 8), (cx + 31, cy + 34), (cx + 27, cy + 8)]
        pygame.draw.polygon(surface, (30, 5, 45), blade)
        pygame.draw.polygon(surface, (245, 45, 100), blade, 1)
        pygame.draw.polygon(surface, (0, 0, 0), blade, 2)



# 4. RENDERIZADOR DE SPRITES DE BATALLA RETRO PROCEDURAL
class DeltaruneEnemyRenderer:
    """Genera y anima los sprites de combate de los enemigos en pantalla."""
    @staticmethod
    def draw_enemy(surface, template_id, x, y, anim_time, hit_flash=0.0, mercy=0):
        bob = int(math.sin(anim_time * 3.5) * 3)
        shake_x = int(math.sin(hit_flash * 40.0) * 4) if hit_flash > 0 else 0
        ex = x + shake_x
        ey = y + bob

        if template_id == "sombra":
            DeltaruneEnemyRenderer._draw_sombra(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "rudinn":
            DeltaruneEnemyRenderer._draw_rudinn(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "fantasmino":
            DeltaruneEnemyRenderer._draw_fantasmino(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "sectario":
            DeltaruneEnemyRenderer._draw_sectario(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "sepulturero":
            DeltaruneEnemyRenderer._draw_sepulturero(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "arconte":
            DeltaruneEnemyRenderer._draw_arconte(surface, ex, ey, anim_time, hit_flash, mercy)

    @staticmethod
    def _draw_sombra(surface, x, y, t, flash, mercy):
        is_spared = (mercy >= 100)
        c_body = (255, 255, 255) if flash > 0.05 else (32, 22, 50)
        c_cloak = (255, 255, 255) if flash > 0.05 else (60, 42, 92)

        # Sombra en el suelo
        pygame.draw.ellipse(surface, (15, 10, 25, 120), (x - 22, y + 42, 44, 12))

        # Capa con caída ondulada
        pts_cloak = [
            (x - 16, y - 4), (x + 16, y - 4),
            (x + 22, y + 36 + int(math.sin(t * 4.0) * 2)),
            (x, y + 42),
            (x - 22, y + 36 - int(math.sin(t * 4.0) * 2)),
        ]
        pygame.draw.polygon(surface, c_cloak, pts_cloak)
        pygame.draw.polygon(surface, (140, 80, 200), pts_cloak, 1)

        # Torso
        pygame.draw.rect(surface, c_body, (x - 12, y - 2, 24, 30), border_radius=4)
        # Guantes flotantes
        gw_off = math.sin(t * 2.8) * 3
        pygame.draw.circle(surface, (230, 230, 245), (int(x - 20 - gw_off), int(y + 14)), 5)
        pygame.draw.circle(surface, (230, 230, 245), (int(x + 20 + gw_off), int(y + 14)), 5)

        # Cabeza
        pygame.draw.circle(surface, c_body, (x, y - 12), 14)
        # Ojos que parpadean
        eye_open = (t % 3.2 > 0.22)
        if eye_open:
            pygame.draw.ellipse(surface, (255, 240, 50), (x - 8, y - 16, 6, 8))
            pygame.draw.ellipse(surface, (255, 240, 50), (x + 2, y - 16, 6, 8))
            pygame.draw.rect(surface, (0, 0, 0), (x - 5, y - 14, 2, 4))
            pygame.draw.rect(surface, (0, 0, 0), (x + 5, y - 14, 2, 4))
        else:
            pygame.draw.line(surface, (255, 240, 50), (x - 8, y - 12), (x - 2, y - 12), 2)
            pygame.draw.line(surface, (255, 240, 50), (x + 2, y - 12), (x + 8, y - 12), 2)

        # Sonrisa si está perdonado
        if is_spared:
            pygame.draw.arc(surface, (255, 240, 50), (x - 6, y - 9, 12, 6), math.pi, 2 * math.pi, 2)
            # Rubor
            pygame.draw.circle(surface, (255, 120, 160), (x - 9, y - 7), 2)
            pygame.draw.circle(surface, (255, 120, 160), (x + 9, y - 7), 2)

        # Sombrero de copa inclinado
        hat_tilt = -4 if is_spared else 0
        pygame.draw.rect(surface, (18, 14, 25), (x - 10 + hat_tilt, y - 30, 20, 16), border_radius=2)
        pygame.draw.rect(surface, (220, 45, 60), (x - 10 + hat_tilt, y - 18, 20, 4))
        pygame.draw.ellipse(surface, (18, 14, 25), (x - 14 + hat_tilt, y - 16, 28, 6))

    @staticmethod
    def _draw_rudinn(surface, x, y, t, flash, mercy):
        is_spared = (mercy >= 100)
        c_gem = (255, 255, 255) if flash > 0.05 else (40, 180, 125)
        c_light = (255, 255, 255) if flash > 0.05 else (135, 245, 190)

        pygame.draw.ellipse(surface, (15, 30, 25, 110), (x - 20, y + 40, 40, 10))

        # Cuerpo en forma de diamante esmeralda
        pts_dia = [(x, y - 26), (x + 22, y + 10), (x, y + 42), (x - 22, y + 10)]
        pygame.draw.polygon(surface, c_gem, pts_dia)
        # Faceta brillante interna
        pts_in = [(x, y - 18), (x + 14, y + 8), (x, y + 32), (x - 14, y + 8)]
        pygame.draw.polygon(surface, c_light, pts_in)
        pygame.draw.polygon(surface, (25, 110, 75), pts_dia, 2)

        # Ojo de cristal
        pygame.draw.rect(surface, (255, 255, 255), (x - 4, y + 2, 8, 7), border_radius=2)
        pygame.draw.rect(surface, (30, 60, 50), (x - 2, y + 4, 4, 3))

        # Corona / pluma real en la punta
        pygame.draw.polygon(surface, (255, 220, 60), [(x, y - 26), (x - 6, y - 38), (x, y - 34), (x + 6, y - 38)])

        # Estoque reluciente animado
        sword_ang = math.sin(t * 3.0) * 0.15 + (0.5 if is_spared else 0.0)
        sx = x + 26
        sy = y + 16
        ex = sx + math.cos(sword_ang - 0.7) * 26
        ey = sy + math.sin(sword_ang - 0.7) * 26
        pygame.draw.line(surface, (220, 245, 255), (sx, sy), (ex, ey), 3)
        pygame.draw.circle(surface, (255, 215, 60), (int(sx), int(sy)), 5)

        if is_spared:
            pygame.draw.circle(surface, (255, 130, 180), (x - 8, y + 16), 3)
            pygame.draw.circle(surface, (255, 130, 180), (x + 8, y + 16), 3)

    @staticmethod
    def _draw_fantasmino(surface, x, y, t, flash, mercy):
        is_spared = (mercy >= 100)
        c_ghost = (255, 255, 255, 250) if flash > 0.05 else (160, 230, 255, 215)

        ghost_s = pygame.Surface((60, 70), pygame.SRCALPHA)
        # Sombra
        pygame.draw.ellipse(ghost_s, (30, 60, 80, 80), (12, 58, 36, 10))

        # Cuerpo fantasmagórico
        pygame.draw.circle(ghost_s, c_ghost, (30, 24), 20)
        pygame.draw.rect(ghost_s, c_ghost, (10, 24, 40, 24))
        # Cola ondulada de 4 picos
        for i in range(4):
            peak_y = 48 + int(math.sin(t * 5.0 + i) * 3)
            pygame.draw.circle(ghost_s, c_ghost, (15 + i * 10, peak_y), 6)

        # Ojos con ritmo
        pygame.draw.circle(ghost_s, (20, 45, 70), (23, 22), 4)
        pygame.draw.circle(ghost_s, (20, 45, 70), (37, 22), 4)
        pygame.draw.circle(ghost_s, (255, 255, 255), (24, 21), 1)
        pygame.draw.circle(ghost_s, (255, 255, 255), (38, 21), 1)

        # Sonrisa
        pygame.draw.arc(ghost_s, (20, 45, 70), (25, 26, 10, 8), math.pi, 2 * math.pi, 2)

        # Auriculares retro
        pygame.draw.arc(ghost_s, (230, 50, 75), (8, 6, 44, 30), 0, math.pi, 4)
        # Almohadillas con LEDs de ecualizador
        pygame.draw.rect(ghost_s, (230, 50, 75), (6, 16, 7, 18), border_radius=3)
        pygame.draw.rect(ghost_s, (230, 50, 75), (47, 16, 7, 18), border_radius=3)
        led_c = (80, 255, 120) if (int(t * 8) % 2 == 0) else (255, 220, 60)
        pygame.draw.circle(ghost_s, led_c, (9, 25), 2)
        pygame.draw.circle(ghost_s, led_c, (50, 25), 2)

        # Notas flotantes alrededor
        for ni, (nx, ny) in enumerate([(8, 4), (52, 6)]):
            note_y = ny + int(math.sin(t * 3.5 + ni * 2) * 4)
            pygame.draw.circle(ghost_s, (255, 140, 200), (nx, note_y), 3)
            pygame.draw.line(ghost_s, (255, 140, 200), (nx + 2, note_y), (nx + 2, note_y - 6), 1)

        surface.blit(ghost_s, (x - 30, y - 25))

    @staticmethod
    def _draw_sectario(surface, x, y, t, flash, mercy):
        """Dibuja al Acólito Encapuchado de la Secta en combate con su túnica, capucha y grimorio."""
        is_spared = (mercy >= 100)
        c_robe = (255, 255, 255) if flash > 0.05 else (44, 16, 52)
        c_trim = (255, 235, 85) if is_spared else (215, 45, 85)

        # Sombra y pentagrama/sello suave bajo sus pies
        pygame.draw.ellipse(surface, (25, 10, 32, 120), (x - 22, y + 38, 44, 12))
        pygame.draw.ellipse(surface, c_trim, (x - 20, y + 39, 40, 10), 1)

        # Túnica ceremonial acampanada
        sway = int(math.sin(t * 3.8) * 2)
        robe_pts = [
            (x - 14, y - 6),
            (x + 14, y - 6),
            (x + 22, y + 40 + sway),
            (x, y + 43),
            (x - 22, y + 40 - sway),
        ]
        pygame.draw.polygon(surface, c_robe, robe_pts)
        pygame.draw.polygon(surface, c_trim, robe_pts, 2)

        # Estola ritual con el símbolo del Eclipse en el pecho
        pygame.draw.rect(surface, (24, 10, 30), (x - 6, y - 2, 12, 42))
        pygame.draw.line(surface, c_trim, (x - 6, y - 2), (x - 6, y + 40), 1)
        pygame.draw.line(surface, c_trim, (x + 6, y - 2), (x + 6, y + 40), 1)
        pygame.draw.circle(surface, c_trim, (x, y + 12), 5, 1)
        pygame.draw.circle(surface, (255, 220, 90), (x, y + 12), 2)

        # Mangas anchas de sectario y manos invocando
        hand_bob = int(math.sin(t * 4.5) * 3)
        pygame.draw.polygon(surface, c_robe, [(x - 13, y - 2), (x - 25, y + 10 + hand_bob), (x - 16, y + 18 + hand_bob)])
        pygame.draw.polygon(surface, c_trim, [(x - 13, y - 2), (x - 25, y + 10 + hand_bob), (x - 16, y + 18 + hand_bob)], 1)
        pygame.draw.polygon(surface, c_robe, [(x + 13, y - 2), (x + 25, y + 10 - hand_bob), (x + 16, y + 18 - hand_bob)])
        pygame.draw.polygon(surface, c_trim, [(x + 13, y - 2), (x + 25, y + 10 - hand_bob), (x + 16, y + 18 - hand_bob)], 1)

        # Capucha puntiaguda profunda que oculta el rostro en tinieblas
        hood_pts = [
            (x, y - 34),
            (x + 16, y - 16),
            (x + 14, y - 2),
            (x - 14, y - 2),
            (x - 16, y - 16),
        ]
        pygame.draw.polygon(surface, c_robe, hood_pts)
        pygame.draw.polygon(surface, c_trim, hood_pts, 2)
        # Vacío oscuro bajo la capucha
        pygame.draw.circle(surface, (8, 4, 14), (x, y - 13), 10)

        # Ojos brillantes bajo la capucha
        eye_c = (255, 240, 110) if is_spared else (255, 55, 90)
        pygame.draw.ellipse(surface, eye_c, (x - 7, y - 15, 5, 4))
        pygame.draw.ellipse(surface, eye_c, (x + 2, y - 15, 5, 4))
        pygame.draw.circle(surface, (255, 255, 255), (x - 5, y - 14), 1)
        pygame.draw.circle(surface, (255, 255, 255), (x + 4, y - 14), 1)

        # Grimorio flotante y sello rúnico a su izquierda
        gx = x - 26
        gy = y - 6 + hand_bob
        pygame.draw.polygon(surface, (130, 30, 55), [(gx - 8, gy), (gx, gy + 3), (gx + 8, gy), (gx, gy + 8)])
        pygame.draw.polygon(surface, (245, 235, 200), [(gx - 7, gy - 2), (gx, gy + 1), (gx + 7, gy - 2), (gx, gy + 5)])
        # Orbe ritual flotando sobre el grimorio
        pygame.draw.circle(surface, c_trim, (gx, gy - 9), 5, 1)
        pygame.draw.circle(surface, (255, 220, 100), (gx, gy - 9), 2)

    @staticmethod
    def _draw_sepulturero(surface, x, y, t, flash, mercy):
        """Dibuja el imponente sprite de batalla del Jefe Morvath el Sepulturero."""
        is_spared = (mercy >= 100)
        c_cloak = (255, 255, 255) if flash > 0.05 else (34, 18, 46)
        c_trim = (255, 235, 90) if is_spared else (210, 45, 75)
        c_armor = (255, 255, 255) if flash > 0.05 else (85, 88, 108)

        # Sombra y círculo rúnico bajo sus pies
        aura = pygame.Surface((64, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (190, 35, 70, 110), (0, 0, 64, 18))
        pygame.draw.ellipse(aura, (*c_trim, 190), (2, 2, 60, 14), 1)
        surface.blit(aura, (x - 32, y + 36))

        # Manto del Sepulturero ondulando con la brisa del abismo
        wave = int(math.sin(t * 4.2) * 3)
        cloak_pts = [
            (x - 20, y - 10),
            (x + 20, y - 10),
            (x + 28, y + 38 + wave),
            (x + 10, y + 44),
            (x, y + 39 - wave),
            (x - 12, y + 44),
            (x - 28, y + 38 - wave),
        ]
        pygame.draw.polygon(surface, c_cloak, cloak_pts)
        pygame.draw.polygon(surface, c_trim, cloak_pts, 2)

        # Pechera de costillas de hierro forjado
        pygame.draw.rect(surface, (20, 14, 28), (x - 13, y - 6, 26, 30), border_radius=4)
        for ry in range(y - 2, y + 20, 6):
            pygame.draw.line(surface, c_armor, (x - 10, ry), (x + 10, ry), 2)
        pygame.draw.line(surface, c_trim, (x, y - 4), (x, y + 20), 2)

        # Hombreras góticas con púas
        pygame.draw.ellipse(surface, c_armor, (x - 27, y - 12, 16, 11))
        pygame.draw.ellipse(surface, c_armor, (x + 11, y - 12, 16, 11))
        pygame.draw.polygon(surface, c_trim, [(x - 22, y - 12), (x - 25, y - 20), (x - 17, y - 12)])
        pygame.draw.polygon(surface, c_trim, [(x + 22, y - 12), (x + 25, y - 20), (x + 17, y - 12)])

        # Cabeza encapuchada y corona fúnebre
        pygame.draw.circle(surface, (16, 10, 24), (x, y - 18), 14)
        pygame.draw.arc(surface, c_trim, (x - 15, y - 33, 30, 28), 0, math.pi, 2)
        crown_pts = [
            (x - 11, y - 28),
            (x - 9, y - 37),
            (x - 4, y - 31),
            (x, y - 39),
            (x + 4, y - 31),
            (x + 9, y - 37),
            (x + 11, y - 28),
        ]
        pygame.draw.polygon(surface, (215, 190, 95), crown_pts)

        # Ojos brillantes del Sepulturero
        eye_col = (120, 245, 255) if is_spared else (255, 230, 65)
        pygame.draw.polygon(surface, eye_col, [(x - 9, y - 19), (x - 3, y - 17), (x - 6, y - 14)])
        pygame.draw.polygon(surface, eye_col, [(x + 9, y - 19), (x + 3, y - 17), (x + 6, y - 14)])

        # Guadaña-Pala Ancestral (a la derecha del sprite)
        scythe_bob = int(math.sin(t * 3.0) * 3)
        sx = x + 24
        sy = y + scythe_bob
        pygame.draw.line(surface, (125, 88, 58), (sx, sy - 30), (sx - 4, sy + 38), 3)
        blade_pts = [
            (sx, sy - 28),
            (sx - 22, sy - 34),
            (sx - 30, sy - 24),
            (sx - 12, sy - 20),
        ]
        pygame.draw.polygon(surface, (210, 225, 245), blade_pts)
        pygame.draw.polygon(surface, c_trim, blade_pts, 1)

        # Farol de Almas flotando (a la izquierda del sprite, balanceándose)
        lan_x = x - 28 + int(math.sin(t * 3.6) * 3)
        lan_y = y + 4 + int(math.cos(t * 3.6) * 2)
        pygame.draw.line(surface, c_armor, (x - 18, y - 4), (lan_x, lan_y - 8), 2)
        pygame.draw.rect(surface, (42, 36, 56), (lan_x - 6, lan_y - 6, 12, 15), border_radius=2)
        pygame.draw.rect(surface, (215, 185, 85), (lan_x - 6, lan_y - 6, 12, 15), 1, border_radius=2)
        pygame.draw.circle(surface, (100, 235, 255), (lan_x, lan_y + 1), 4)
        pygame.draw.circle(surface, (255, 255, 255), (lan_x, lan_y + 1), 2)

    @staticmethod
    def _draw_arconte(surface, x, y, t, flash, mercy):
        """Dibuja al Jefe Supremo Vaelkor, Rey del Cristal Negro con Fuego Oscuro y esquirlas de cristal."""
        is_spared = (mercy >= 100)
        c_cloak = (255, 255, 255) if flash > 0.05 else (18, 8, 28)
        c_fire = (255, 235, 90) if is_spared else (235, 35, 85)

        # Sombra de Fuego Oscuro con borde negro bajo el Jefe
        pygame.draw.ellipse(surface, (0, 0, 0), (x - 36, y + 35, 72, 18))
        pygame.draw.ellipse(surface, c_fire, (x - 34, y + 37, 68, 14), 2)
        pygame.draw.ellipse(surface, (35, 6, 48), (x - 28, y + 39, 56, 10))

        # 6 Esquirlas de Cristal Quebrado con borde negro orbitando detrás de Vaelkor
        for i in range(6):
            ang = t * 1.8 + i * (math.pi / 3.0)
            sx = int(x + math.cos(ang) * 32)
            sy = int(y - 4 + math.sin(ang) * 18)
            shard = [(sx, sy - 8), (sx + 5, sy), (sx, sy + 8), (sx - 5, sy)]
            pygame.draw.polygon(surface, c_fire, shard)
            pygame.draw.polygon(surface, (0, 0, 0), shard, 2)
            pygame.draw.line(surface, (255, 225, 245), (sx, sy - 6), (sx, sy + 6), 1)

        # Lenguas de Fuego Oscuro con borde negro emergiendo de sus hombros
        for fx_off in (-22, -12, 12, 22):
            fl_h = int(14 + 6 * math.sin(t * 10.0 + fx_off))
            f_pts = [(x + fx_off - 6, y - 6), (x + fx_off, y - 12 - fl_h), (x + fx_off + 6, y - 6)]
            pygame.draw.polygon(surface, (35, 5, 50), f_pts)
            pygame.draw.polygon(surface, (0, 0, 0), f_pts, 2)
            pygame.draw.line(surface, c_fire, (x + fx_off, y - 8), (x + fx_off, y - 10 - fl_h // 2), 2)

        # Manto del Rey del Cristal Negro
        wave = int(math.sin(t * 4.8) * 3)
        cloak_pts = [
            (x - 22, y - 12),
            (x + 22, y - 12),
            (x + 30, y + 40 + wave),
            (x + 12, y + 45),
            (x, y + 38 - wave),
            (x - 12, y + 45),
            (x - 30, y + 40 - wave),
        ]
        pygame.draw.polygon(surface, c_cloak, cloak_pts)
        pygame.draw.polygon(surface, c_fire, cloak_pts, 2)
        pygame.draw.polygon(surface, (0, 0, 0), cloak_pts, 1)

        # Núcleo de cristal agrietado en el pecho
        core_pts = [(x, y - 6), (x + 10, y + 8), (x, y + 22), (x - 10, y + 8)]
        pygame.draw.polygon(surface, c_fire, core_pts)
        pygame.draw.polygon(surface, (0, 0, 0), core_pts, 2)
        pygame.draw.line(surface, (255, 240, 255), (x - 5, y + 4), (x + 5, y + 12), 2)
        pygame.draw.line(surface, (0, 0, 0), (x + 4, y + 3), (x - 4, y + 14), 1)

        # Cabeza abismal y Corona de Cristal Negro
        pygame.draw.circle(surface, (10, 4, 18), (x, y - 20), 14)
        pygame.draw.circle(surface, (0, 0, 0), (x, y - 20), 14, 2)
        crown_pts = [
            (x - 14, y - 28),
            (x - 12, y - 42),
            (x - 5, y - 32),
            (x, y - 46),
            (x + 5, y - 32),
            (x + 12, y - 42),
            (x + 14, y - 28),
        ]
        pygame.draw.polygon(surface, c_fire, crown_pts)
        pygame.draw.polygon(surface, (0, 0, 0), crown_pts, 2)

        # 4 Ojos incandescentes
        eye_col = (255, 240, 95) if is_spared else (255, 50, 105)
        for ex, ey in [(x - 8, y - 22), (x + 4, y - 22), (x - 6, y - 16), (x + 2, y - 16)]:
            pygame.draw.rect(surface, eye_col, (ex, ey, 4, 3))

        # Gran Mandoble de Fuego Oscuro y Cristal Quebrado
        sw_y = y + int(math.sin(t * 3.8) * 4)
        sword_pts = [
            (x + 28, sw_y - 38),
            (x + 35, sw_y - 10),
            (x + 28, sw_y + 36),
            (x + 21, sw_y - 10),
        ]
        pygame.draw.polygon(surface, (28, 6, 42), sword_pts)
        pygame.draw.polygon(surface, c_fire, sword_pts, 2)
        pygame.draw.polygon(surface, (0, 0, 0), sword_pts, 1)
        pygame.draw.line(surface, (255, 230, 245), (x + 28, sw_y - 32), (x + 28, sw_y + 28), 2)


