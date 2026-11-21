import pygame
from configuracion import VIRTUAL_WIDTH

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
        self.state = "IDLE"  # IDLE, FADING_OUT, FADING_IN
        self.timer = 0.0
        self.duration = 0.22  # 220ms
        self.target_scene_id = None
        self.target_spawn = None
        self.banner_text = ""
        self.banner_timer = 0.0

    def start(self, target_scene_id, target_spawn, banner_text=""):
        self.state = "FADING_OUT"
        self.timer = 0.0
        self.target_scene_id = target_scene_id
        self.target_spawn = target_spawn
        self.banner_text = banner_text
        self.banner_timer = 2.4

    def update(self, dt, on_switch_callback):
        if self.state == "IDLE":
            if self.banner_timer > 0:
                self.banner_timer -= dt
            return

        self.timer += dt
        if self.state == "FADING_OUT":
            if self.timer >= self.duration:
                self.state = "FADING_IN"
                self.timer = 0.0
                on_switch_callback(self.target_scene_id, self.target_spawn)
        elif self.state == "FADING_IN":
            if self.timer >= self.duration:
                self.state = "IDLE"
                self.timer = 0.0

    def draw(self, surface, font):
        # Fundido a negro
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

