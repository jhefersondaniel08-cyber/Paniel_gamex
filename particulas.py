import math
import random
import pygame
from configuracion import VIRTUAL_WIDTH, VIRTUAL_HEIGHT

# ==========================================================
# PARTÍCULAS (Polvo al correr y polvo mágico ambiental)
# ==========================================================
class DustParticle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-3, 3)
        self.y = y + random.uniform(-1, 2)
        self.radius = random.uniform(1.8, 3.2)
        self.alpha = 200
        self.fade = random.uniform(10, 18)

    def update(self):
        self.radius = max(0.5, self.radius - 0.08)
        self.alpha -= self.fade
        return self.alpha > 0

    def draw(self, surface, camera):
        if self.alpha > 0:
            cx, cy = camera.apply((self.x, self.y))
            s = pygame.Surface((int(self.radius * 2 + 2), int(self.radius * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 200, 170, int(self.alpha)), (int(self.radius + 1), int(self.radius + 1)), int(self.radius))
            surface.blit(s, (cx - self.radius, cy - self.radius))


class AmbientSparkle:
    def __init__(self, map_w, map_h):
        self.map_w = map_w
        self.map_h = map_h
        self.x = random.uniform(0, map_w)
        self.y = random.uniform(0, map_h)
        self.vx = random.uniform(-0.15, 0.15)
        self.vy = random.uniform(-0.35, -0.1)
        self.life = random.uniform(2.0, 5.0)
        self.max_life = self.life
        self.size = random.choice([1, 1, 2])
        self.color = random.choice([(255, 255, 200), (180, 240, 255), (200, 255, 200)])

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt
        if self.life <= 0:
            self.x = random.uniform(0, self.map_w)
            self.y = random.uniform(0, self.map_h)
            self.life = self.max_life

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        if -10 <= cx <= VIRTUAL_WIDTH + 10 and -10 <= cy <= VIRTUAL_HEIGHT + 10:
            alpha = int(255 * (math.sin(self.life / self.max_life * math.pi)))
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            s.fill((*self.color, max(0, min(255, alpha))))
            surface.blit(s, (cx, cy))

