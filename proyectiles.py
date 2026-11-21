import math
import random
import pygame

# 3. BALAS Y PATRONES DE ATAQUE ESTILO BULLET HELL DELTARUNE
class Bullet:
    def __init__(self, x, y, radius=3.5):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.alive = True
        self.grazed = False

    def update(self, dt, arena_rect, soul_pos=None):
        pass

    def draw(self, surface):
        pass

    def collides_with_soul(self, soul_center, soul_radius=3.0):
        dist_sq = (self.x - soul_center[0]) ** 2 + (self.y - soul_center[1]) ** 2
        return dist_sq < (self.radius + soul_radius) ** 2

    def check_graze(self, soul_center, graze_radius=15.0):
        if self.grazed:
            return False
        dist_sq = (self.x - soul_center[0]) ** 2 + (self.y - soul_center[1]) ** 2
        if dist_sq < (self.radius + graze_radius) ** 2:
            self.grazed = True
            return True
        return False


class ShadowRainBullet(Bullet):
    def __init__(self, x, y, phase=0.0):
        super().__init__(x, y, radius=4.0)
        self.base_x = x
        self.phase = phase
        self.time = 0.0
        self.vy = 64.0
        self.erratic_freq = random.uniform(8.5, 14.5)
        self.erratic_amp = random.uniform(16.0, 26.0)
        self.juke_dir = random.choice([-1.0, 1.0])

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        # Caída errática con acelerones y zig-zag impredecible para exigir buen timing de Parry
        speed_surge = 1.0 + 0.55 * math.sin(self.time * 11.0 + self.phase)
        self.y += self.vy * speed_surge * dt
        zig = math.sin(self.time * self.erratic_freq + self.phase) * self.erratic_amp
        zag = math.cos(self.time * (self.erratic_freq * 1.7)) * 7.0 * self.juke_dir
        self.x = self.base_x + zig + zag
        if self.y > arena_rect.bottom + 10:
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (140, 70, 220), (ix, iy), int(self.radius + 1))
        pygame.draw.circle(surface, (230, 190, 255), (ix, iy), int(self.radius - 1))


class ShadowSpiralBullet(Bullet):
    def __init__(self, cx, cy, angle, speed=54.0):
        x = cx + math.cos(angle) * 75.0
        y = cy + math.sin(angle) * 75.0
        super().__init__(x, y, radius=3.8)
        self.angle = angle
        self.speed = speed
        self.target_cx = cx
        self.target_cy = cy
        self.time = 0.0
        self.wobble_phase = random.uniform(0, math.pi * 2)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        # Giro errático con cambios bruscos de velocidad angular y radial
        ang_vel = 1.15 + math.sin(self.time * 12.0 + self.wobble_phase) * 1.45
        self.angle += dt * ang_vel
        spd_burst = self.speed * (1.0 + 0.45 * math.cos(self.time * 10.0 + self.wobble_phase))
        self.x -= math.cos(self.angle) * spd_burst * dt
        self.y -= math.sin(self.angle) * spd_burst * dt
        if not arena_rect.inflate(30, 30).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (80, 40, 150), (ix, iy), 5)
        pygame.draw.circle(surface, (255, 230, 80), (ix, iy), 2)


class DiamondSwordBullet(Bullet):
    def __init__(self, target_x, start_y, ceiling_y):
        super().__init__(target_x, start_y, radius=4.5)
        self.ceiling_y = ceiling_y
        self.warn_timer = 0.55
        self.falling = False
        self.vy = 165.0
        self.time = 0.0
        self.swerve_phase = random.uniform(0, math.pi * 2)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        if self.warn_timer > 0:
            self.warn_timer -= dt
            if self.warn_timer <= 0:
                self.falling = True
        else:
            self.y += self.vy * dt
            # Oscilación lateral errática mientras cae
            self.x += math.sin(self.time * 19.0 + self.swerve_phase) * 72.0 * dt
            if self.y > arena_rect.bottom + 12:
                self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        if not self.falling:
            # Rayo de advertencia vertical muy claro y parpadeante con flechas hacia abajo
            flash = (int(self.time * 24) % 2 == 0)
            col_line = (120, 255, 180) if flash else (50, 180, 110)
            pygame.draw.line(surface, col_line, (ix, self.ceiling_y), (ix, self.ceiling_y + 160), 1)
            # Flechas indicadoras descendentes
            for arrow_y in range(int(self.ceiling_y) + 12, int(self.ceiling_y) + 140, 28):
                pygame.draw.line(surface, (255, 240, 100), (ix - 3, arrow_y - 3), (ix, arrow_y), 1)
                pygame.draw.line(surface, (255, 240, 100), (ix + 3, arrow_y - 3), (ix, arrow_y), 1)
            # Runa en el techo
            pygame.draw.circle(surface, (255, 220, 90), (ix, int(self.ceiling_y) + 3), 4, 1)
        else:
            pts = [(ix, iy - 8), (ix + 4, iy), (ix, iy + 8), (ix - 4, iy)]
            pygame.draw.polygon(surface, (140, 255, 200), pts)
            pygame.draw.polygon(surface, (40, 160, 110), pts, 1)
            pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 2)



class CrossfireDiamondBullet(Bullet):
    def __init__(self, x, y, vx):
        super().__init__(x, y, radius=4.0)
        self.vx = vx
        self.time = 0.0
        self.phase = random.uniform(0, math.pi * 2)
        self.freq = random.uniform(11.0, 16.0)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        surge = 1.0 + 0.4 * math.sin(self.time * 12.0 + self.phase)
        self.x += self.vx * surge * dt
        self.y += math.cos(self.time * self.freq + self.phase) * 78.0 * dt
        if not arena_rect.inflate(25, 25).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pts = [(ix - 6, iy), (ix, iy - 3), (ix + 6, iy), (ix, iy + 3)]
        pygame.draw.polygon(surface, (80, 240, 160), pts)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 2)


class BouncingNoteBullet(Bullet):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, radius=4.5)
        self.vx = vx
        self.vy = vy
        self.time = 0.0
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        # Zig-zag rítmico errático en pleno vuelo y desvíos de ángulo al rebotar
        swerve_x = math.sin(self.time * 14.0 + self.phase) * 38.0
        swerve_y = math.cos(self.time * 11.0 + self.phase) * 38.0
        self.x += (self.vx + swerve_x) * dt
        self.y += (self.vy + swerve_y) * dt
        # Rebote errático en las paredes de la caja de batalla
        if self.x - self.radius < arena_rect.left:
            self.x = arena_rect.left + self.radius
            self.vx = abs(self.vx) * random.uniform(0.9, 1.15)
            self.vy += random.uniform(-25, 25)
        elif self.x + self.radius > arena_rect.right:
            self.x = arena_rect.right - self.radius
            self.vx = -abs(self.vx) * random.uniform(0.9, 1.15)
            self.vy += random.uniform(-25, 25)

        if self.y - self.radius < arena_rect.top:
            self.y = arena_rect.top + self.radius
            self.vy = abs(self.vy) * random.uniform(0.9, 1.15)
            self.vx += random.uniform(-25, 25)
        elif self.y + self.radius > arena_rect.bottom:
            self.y = arena_rect.bottom - self.radius
            self.vy = -abs(self.vy) * random.uniform(0.9, 1.15)
            self.vx += random.uniform(-25, 25)

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (255, 100, 150), (ix - 2, iy + 2), 3)
        pygame.draw.line(surface, (255, 240, 255), (ix, iy + 2), (ix, iy - 6), 2)
        pygame.draw.line(surface, (255, 240, 255), (ix, iy - 6), (ix + 3, iy - 4), 2)


class SoundArcBullet(Bullet):
    def __init__(self, cx, cy, angle, speed=58.0):
        super().__init__(cx, cy, radius=3.5)
        self.angle = angle
        self.speed = speed
        self.time = 0.0
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        wobble_a = self.angle + math.sin(self.time * 13.0 + self.phase) * 0.48
        spd = self.speed * (1.0 + 0.45 * math.cos(self.time * 10.0 + self.phase))
        self.x += math.cos(wobble_a) * spd * dt
        self.y += math.sin(wobble_a) * spd * dt
        if not arena_rect.inflate(20, 20).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (100, 220, 255), (ix, iy), 3)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 1)


# ==========================================================
# PROYECTILES EXCLUSIVOS DEL JEFE (MORVATH, EL SEPULTURERO)
# ==========================================================
class ScytheWaveBullet(Bullet):
    """Guadaña espectral giratoria que avanza en curva por la arena."""
    def __init__(self, x, y, vx, vy_amp=36.0, phase=0.0):
        super().__init__(x, y, radius=5.5)
        self.vx = vx
        self.base_y = float(y)
        self.vy_amp = vy_amp
        self.phase = phase
        self.time = 0.0
        self.spin = 0.0

    def update(self, dt, arena_rect):
        self.time += dt
        self.spin += dt * 11.0
        self.x += self.vx * dt
        self.y = self.base_y + math.sin(self.time * 4.5 + self.phase) * self.vy_amp
        if not arena_rect.inflate(36, 36).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        # Media luna de guadaña giratoria carmesí/dorada
        pts = []
        for i in range(6):
            ang = self.spin + (i - 2.5) * 0.45
            r = 7 if i in (2, 3) else 4
            pts.append((ix + int(math.cos(ang) * r), iy + int(math.sin(ang) * r)))
        pygame.draw.polygon(surface, (235, 55, 80), pts)
        pygame.draw.circle(surface, (255, 230, 120), (ix, iy), 3)


class LanternFlameBullet(Bullet):
    """Llama de ánima lanzada desde el Farol del Sepulturero hacia el alma."""
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, radius=4.2)
        self.vx = vx
        self.vy = vy
        self.time = 0.0

    def update(self, dt, arena_rect):
        self.time += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if not arena_rect.inflate(30, 30).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        flicker = int(math.sin(self.time * 16.0) * 2)
        pygame.draw.circle(surface, (90, 225, 255), (ix, iy), 5)
        pygame.draw.polygon(surface, (190, 250, 255), [(ix - 3, iy), (ix, iy - 7 - flicker), (ix + 3, iy)])
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 2)


class GravePillarBullet(Bullet):
    """Lápida espectral que emerge desde el suelo de la arena tras una advertencia vertical evidente."""
    def __init__(self, x, arena_bottom, warn_timer=0.68):
        super().__init__(x, arena_bottom - 4, radius=6.0)
        self.arena_bottom = arena_bottom
        self.warn_timer = float(warn_timer)
        self.active_timer = 0.65
        self.erupted = False
        self.current_h = 0.0
        self.target_h = 54.0
        self.time = 0.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.arena_bottom = arena_rect.bottom
        if self.warn_timer > 0:
            self.warn_timer -= dt
            if self.warn_timer <= 0:
                self.erupted = True
        else:
            self.current_h = min(self.target_h, self.current_h + 320.0 * dt)
            self.y = self.arena_bottom - self.current_h * 0.5
            self.active_timer -= dt
            if self.active_timer <= 0:
                self.alive = False

    def collides_with_soul(self, soul_center, soul_radius=3.0):
        if not self.erupted:
            return False
        rect = pygame.Rect(int(self.x - 7), int(self.arena_bottom - self.current_h), 14, int(self.current_h))
        soul_rect = pygame.Rect(int(soul_center[0] - soul_radius), int(soul_center[1] - soul_radius), int(soul_radius * 2), int(soul_radius * 2))
        return rect.colliderect(soul_rect)

    def check_graze(self, soul_center, graze_radius=15.0):
        if not self.erupted or self.grazed:
            return False
        rect = pygame.Rect(int(self.x - 7 - graze_radius), int(self.arena_bottom - self.current_h - graze_radius), int(14 + graze_radius * 2), int(self.current_h + graze_radius))
        if rect.collidepoint(soul_center[0], soul_center[1]):
            self.grazed = True
            return True
        return False

    def draw(self, surface):
        ix = int(self.x)
        by = int(self.arena_bottom)
        if not self.erupted:
            # Columna de advertencia vertical completa (evita apariciones por sorpresa bajo el jugador)
            flash = (int(self.time * 26) % 2 == 0)
            col_bar = (255, 60, 85) if flash else (180, 40, 60)
            # Líneas límite de la columna donde emergerá la lápida (ancho 14)
            pygame.draw.line(surface, col_bar, (ix - 7, by), (ix - 7, by - int(self.target_h)), 1)
            pygame.draw.line(surface, col_bar, (ix + 7, by), (ix + 7, by - int(self.target_h)), 1)
            # Flechas indicadoras ascendentes ▲ ▲ ▲
            offset_y = int(self.time * 48.0) % 18
            for ay in range(by - 8 - offset_y, by - int(self.target_h), -18):
                pygame.draw.line(surface, (255, 235, 110), (ix - 4, ay + 3), (ix, ay), 1)
                pygame.draw.line(surface, (255, 235, 110), (ix + 4, ay + 3), (ix, ay), 1)
            # Runa de advertencia en el piso de la arena
            pygame.draw.rect(surface, (255, 55, 80), (ix - 8, by - 5, 16, 5))
            pygame.draw.rect(surface, (255, 230, 110), (ix - 8, by - 5, 16, 5), 1)
            if flash:
                pygame.draw.line(surface, (255, 255, 255), (ix, by - 16), (ix, by - 7), 2)
        else:
            h = int(self.current_h)
            if h > 2:
                r = pygame.Rect(ix - 7, by - h, 14, h)
                pygame.draw.rect(surface, (95, 85, 125), r, border_top_left_radius=5, border_top_right_radius=5)
                pygame.draw.rect(surface, (210, 190, 255), r, 1, border_top_left_radius=5, border_top_right_radius=5)
                if h > 20:
                    pygame.draw.line(surface, (255, 80, 100), (ix, by - h + 6), (ix, by - h + 16), 2)
                    pygame.draw.line(surface, (255, 80, 100), (ix - 4, by - h + 10), (ix + 4, by - h + 10), 2)


# ==========================================================
# PROYECTILES DEL ACÓLITO ENCAPUCHADO DE LA SECTA ("sectario")
# ==========================================================
class CultDaggerBullet(Bullet):
    """Daga ritual carmesí que apunta hacia el Alma de Paniel antes de lanzarse a gran velocidad."""
    def __init__(self, x, y, target_x, target_y, speed=145.0):
        super().__init__(x, y, radius=4.0)
        self.angle = math.atan2(target_y - y, target_x - x)
        self.speed = speed
        self.aim_timer = 0.52
        self.launched = False
        self.time = 0.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        if self.aim_timer > 0:
            self.aim_timer -= dt
            if self.aim_timer <= 0:
                self.launched = True
        else:
            self.x += math.cos(self.angle) * self.speed * dt
            self.y += math.sin(self.angle) * self.speed * dt
            if not arena_rect.inflate(32, 32).collidepoint(self.x, self.y):
                self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        ca = math.cos(self.angle)
        sa = math.sin(self.angle)
        if not self.launched:
            # Sello circular ritual y puntero láser nítido con cruceta de advertencia
            flash = (int(self.time * 24) % 2 == 0)
            col_laser = (255, 75, 110) if flash else (175, 35, 65)
            pygame.draw.circle(surface, (245, 65, 95), (ix, iy), 6, 1)
            # Puntero láser hacia la posición apuntada
            laser_len = 160
            lx = int(ix + ca * laser_len)
            ly = int(iy + sa * laser_len)
            pygame.draw.line(surface, col_laser, (ix, iy), (lx, ly), 1)
            # Cruceta en el extremo
            pygame.draw.circle(surface, (255, 235, 100), (lx, ly), 3, 1)
        # Hoja de la daga orientada hacia su dirección de vuelo
        tip = (int(ix + ca * 8), int(iy + sa * 8))
        left_w = (int(ix - ca * 4 - sa * 3), int(iy - sa * 4 + ca * 3))
        right_w = (int(ix - ca * 4 + sa * 3), int(iy - sa * 4 - ca * 3))
        pommel = (int(ix - ca * 7), int(iy - sa * 7))
        pygame.draw.polygon(surface, (245, 65, 95), [tip, left_w, right_w])
        pygame.draw.polygon(surface, (255, 220, 230), [tip, left_w, right_w], 1)
        pygame.draw.line(surface, (255, 215, 90), pommel, (ix, iy), 2)


class RitualSigilBullet(Bullet):
    """Orbe rúnico giratorio de la secta que avanza describiendo un pulso sinusoidal."""
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, radius=4.5)
        self.vx = vx
        self.vy = vy
        self.time = 0.0

    def update(self, dt, arena_rect):
        self.time += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if not arena_rect.inflate(28, 28).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (185, 35, 80), (ix, iy), 5)
        pygame.draw.circle(surface, (255, 220, 90), (ix, iy), 5, 1)
        # Ojo/runa interna
        pygame.draw.circle(surface, (255, 245, 210), (ix, iy), 2)


# ==========================================================
# PROYECTILES DEL JEFE SUPREMO: VAELKOR, ARCONTE DEL ECLIPSE ("arconte")
# ==========================================================
class DarkFlameBullet(Bullet):
    """Destello de Fuego Oscuro con borde negro nítido que ondula con furia abismal."""
    def __init__(self, x, y, vx, vy, phase=0.0):
        super().__init__(x, y, radius=5.0)
        self.vx = vx
        self.vy = vy
        self.phase = phase
        self.time = 0.0

    def update(self, dt, arena_rect):
        self.time += dt
        perp_x = -self.vy
        perp_y = self.vx
        mag = max(1.0, math.hypot(perp_x, perp_y))
        sway = math.cos(self.time * 9.0 + self.phase) * 26.0
        self.x += (self.vx + (perp_x / mag) * sway) * dt
        self.y += (self.vy + (perp_y / mag) * sway) * dt
        if not arena_rect.inflate(32, 32).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        flicker = int(math.sin(self.time * 22.0 + self.phase) * 2)
        flame_pts = [
            (ix, iy - 8 + flicker),
            (ix + 6, iy - 1),
            (ix + 4, iy + 6),
            (ix, iy + 4),
            (ix - 4, iy + 6),
            (ix - 6, iy - 1),
        ]
        # Relleno de fuego oscuro (violeta abismal / carmesí) con borde negro grueso
        pygame.draw.polygon(surface, (35, 8, 52), flame_pts)
        pygame.draw.polygon(surface, (0, 0, 0), flame_pts, 2)
        inner_pts = [
            (ix, iy - 5 + flicker),
            (ix + 3, iy),
            (ix, iy + 3),
            (ix - 3, iy),
        ]
        pygame.draw.polygon(surface, (235, 35, 85), inner_pts)
        pygame.draw.circle(surface, (15, 0, 22), (ix, iy + 1), 2)


class ShatterCrystalBullet(Bullet):
    """Esquirla de cristal oscuro quebrado con borde negro y núcleo incandescente."""
    def __init__(self, x, y, vx, vy, spin_speed=7.0):
        super().__init__(x, y, radius=4.5)
        self.vx = vx
        self.vy = vy
        self.angle = random.uniform(0, math.pi * 2)
        self.spin_speed = spin_speed

    def update(self, dt, arena_rect):
        self.angle += self.spin_speed * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if not arena_rect.inflate(30, 30).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pts = []
        for i, r in enumerate([8, 4, 7, 4]):
            a = self.angle + i * (math.pi / 2.0)
            pts.append((int(ix + math.cos(a) * r), int(iy + math.sin(a) * r)))
        # Esquirla de cristal oscuro con borde negro como cristal roto
        pygame.draw.polygon(surface, (195, 30, 80), pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 2)
        pygame.draw.line(surface, (255, 225, 245), pts[0], pts[2], 1)


class VoidCleaveBullet(Bullet):
    """Grieta dimensional de cristal que advierte con una franja evidente y estalla en Fuego Oscuro con borde negro."""
    def __init__(self, arena_rect, y_pos, warn_time=0.68, duration=1.15):
        super().__init__(arena_rect.centerx, y_pos, radius=5.0)
        self.left_x = arena_rect.left + 4
        self.right_x = arena_rect.right - 4
        self.y_pos = y_pos
        self.timer = 0.0
        self.warn_time = float(warn_time)
        self.duration = float(duration)

    def collides_with_soul(self, soul_rect_or_pos, soul_radius=3.5):
        if not self.alive or self.timer < self.warn_time or self.timer > self.duration - 0.12:
            return False
        sx, sy = soul_rect_or_pos
        return abs(sy - self.y_pos) <= (5.5 + soul_radius) and (self.left_x <= sx <= self.right_x)

    def check_graze(self, soul_pos, graze_radius=16.0):
        if not self.alive or self.grazed or self.timer < self.warn_time:
            return False
        sx, sy = soul_pos
        if abs(sy - self.y_pos) <= graze_radius:
            self.grazed = True
            return True
        return False

    def update(self, dt, arena_rect, soul_pos=None):
        self.timer += dt
        if self.timer >= self.duration:
            self.alive = False

    def draw(self, surface):
        iy = int(self.y_pos)
        if self.timer < self.warn_time:
            # Franja completa de advertencia con líneas guía y marcadores de peligro
            flash = (int(self.timer * 28) % 2 == 0)
            c_edge = (255, 60, 100) if flash else (140, 30, 60)
            pygame.draw.line(surface, c_edge, (self.left_x, iy - 6), (self.right_x, iy - 6), 1)
            pygame.draw.line(surface, c_edge, (self.left_x, iy + 6), (self.right_x, iy + 6), 1)
            # Línea central parpadeante de fractura
            pygame.draw.line(surface, (255, 230, 110) if flash else (200, 45, 90), (self.left_x, iy), (self.right_x, iy), 1)
            # Triángulos de advertencia horizontales
            for mx in range(int(self.left_x) + 16, int(self.right_x) - 10, 32):
                pygame.draw.line(surface, (255, 255, 255), (mx - 3, iy - 3), (mx, iy), 1)
                pygame.draw.line(surface, (255, 255, 255), (mx + 3, iy - 3), (mx, iy), 1)
        else:
            # Estallido horizontal de Fuego Oscuro con borde negro y grietas de cristal
            pygame.draw.rect(surface, (0, 0, 0), (self.left_x, iy - 6, self.right_x - self.left_x, 12))
            pygame.draw.rect(surface, (45, 5, 65), (self.left_x, iy - 4, self.right_x - self.left_x, 8))
            pygame.draw.rect(surface, (235, 35, 85), (self.left_x, iy - 2, self.right_x - self.left_x, 4))
            pygame.draw.line(surface, (255, 230, 245), (self.left_x, iy), (self.right_x, iy), 1)


# ==========================================================
# PROYECTILES ERRÁTICOS Y CREATIVOS PARA JEFES (ALTA DIFICULTAD)
# ==========================================================

class BoomerangScytheBullet(Bullet):
    """Guadaña espectral que se lanza veloz, frena en seco y regresa con un látigo errático de alta velocidad."""
    def __init__(self, x, y, vx, vy, decel=160.0):
        super().__init__(x, y, radius=6.0)
        self.vx = float(vx)
        self.vy = float(vy)
        self.decel = float(decel)
        self.state = "FORWARD"  # FORWARD, PAUSE, RETURN
        self.pause_timer = 0.16
        self.spin = random.uniform(0, math.pi * 2)
        self.time = 0.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.spin += dt * 17.0
        if self.state == "FORWARD":
            spd = math.hypot(self.vx, self.vy)
            if spd > 12.0:
                self.vx -= (self.vx / spd) * self.decel * dt
                self.vy -= (self.vy / spd) * self.decel * dt
                self.x += self.vx * dt
                self.y += self.vy * dt
            else:
                self.state = "PAUSE"
        elif self.state == "PAUSE":
            self.pause_timer -= dt
            if self.pause_timer <= 0:
                self.state = "RETURN"
                # Snap backward con empuje errático hacia donde esté el alma o en reversa amplificada
                if soul_pos:
                    ang = math.atan2(soul_pos[1] - self.y, soul_pos[0] - self.x) + random.uniform(-0.35, 0.35)
                    self.vx = math.cos(ang) * 115.0
                    self.vy = math.sin(ang) * 115.0
                else:
                    self.vx = -self.vx * 2.4 if abs(self.vx) > 5 else random.choice([-90.0, 90.0])
                    self.vy = -self.vy * 2.4 if abs(self.vy) > 5 else random.choice([-90.0, 90.0])
        elif self.state == "RETURN":
            # Trayectoria serpenteante errática
            sway = math.sin(self.time * 14.0) * 38.0
            spd = max(1.0, math.hypot(self.vx, self.vy))
            self.x += (self.vx - (self.vy / spd) * sway) * dt
            self.y += (self.vy + (self.vx / spd) * sway) * dt
            if not arena_rect.inflate(60, 60).collidepoint(self.x, self.y):
                self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        glow_col = (255, 60, 90) if self.state != "PAUSE" else (255, 240, 110)
        pts = []
        for i in range(6):
            ang = self.spin + (i - 2.5) * 0.48
            r = 9 if i in (2, 3) else 4
            pts.append((ix + int(math.cos(ang) * r), iy + int(math.sin(ang) * r)))
        pygame.draw.polygon(surface, glow_col, pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 1)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 2)


class ErraticWispBullet(Bullet):
    """Fuego fatuo errático que cambia bruscamente de ángulo y da acelerones impredecibles."""
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, radius=4.5)
        self.vx = float(vx)
        self.vy = float(vy)
        self.jitter_timer = random.uniform(0.22, 0.36)
        self.time = random.uniform(0, 6.28)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.jitter_timer -= dt
        if self.jitter_timer <= 0:
            self.jitter_timer = random.uniform(0.20, 0.34)
            # Giro brusco en ángulo cerrado de 45° a 90° con impulso
            curr_spd = max(45.0, math.hypot(self.vx, self.vy))
            new_ang = math.atan2(self.vy, self.vx) + random.choice([-1, 1]) * random.uniform(0.75, 1.45)
            burst_spd = min(110.0, curr_spd * random.uniform(1.15, 1.35))
            self.vx = math.cos(new_ang) * burst_spd
            self.vy = math.sin(new_ang) * burst_spd

        self.x += self.vx * dt
        self.y += self.vy * dt
        if not arena_rect.inflate(36, 36).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        flicker = int(math.sin(self.time * 26.0) * 2)
        pygame.draw.circle(surface, (120, 245, 255), (ix, iy), 5 + flicker)
        pygame.draw.circle(surface, (25, 40, 75), (ix, iy), 3)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 1)


class FuneralBellShockwave(Bullet):
    """Onda sónica espectral expansiva con una brecha giratoria y campanada previa de advertencia."""
    def __init__(self, cx, cy, expand_speed=76.0, gap_angle=0.0, gap_size=1.05, start_delay=0.45):
        super().__init__(cx, cy, radius=8.0)
        self.cx = float(cx)
        self.cy = float(cy)
        self.current_r = 8.0
        self.max_r = 150.0
        self.expand_speed = float(expand_speed)
        self.gap_angle = float(gap_angle)
        self.gap_size = float(gap_size)
        self.ring_thickness = 5.5
        self.time = 0.0
        self.start_delay = float(start_delay)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        if self.time >= self.start_delay:
            self.current_r += self.expand_speed * dt
            self.gap_angle = (self.gap_angle + dt * 0.35) % (math.pi * 2)
            if self.current_r > self.max_r:
                self.alive = False

    def collides_with_soul(self, soul_center, soul_radius=3.0):
        if self.time < self.start_delay or not self.alive:
            return False
        dx = soul_center[0] - self.cx
        dy = soul_center[1] - self.cy
        dist = math.hypot(dx, dy)
        if abs(dist - self.current_r) <= (self.ring_thickness * 0.5 + soul_radius):
            angle = math.atan2(dy, dx) % (math.pi * 2)
            gap_min = (self.gap_angle - self.gap_size * 0.5) % (math.pi * 2)
            gap_max = (self.gap_angle + self.gap_size * 0.5) % (math.pi * 2)
            if gap_min < gap_max:
                in_gap = (gap_min <= angle <= gap_max)
            else:
                in_gap = (angle >= gap_min or angle <= gap_max)
            return not in_gap
        return False

    def check_graze(self, soul_center, graze_radius=15.0):
        if self.time < self.start_delay or self.grazed or not self.alive:
            return False
        dx = soul_center[0] - self.cx
        dy = soul_center[1] - self.cy
        dist = math.hypot(dx, dy)
        if abs(dist - self.current_r) <= (self.ring_thickness * 0.5 + graze_radius):
            self.grazed = True
            return True
        return False

    def draw(self, surface):
        icx, icy = int(self.cx), int(self.cy)
        if self.time < self.start_delay:
            # Campana espectral repicando como advertencia visual nítida
            pulse = math.sin(self.time * 28.0) * 3.0
            pygame.draw.circle(surface, (120, 240, 255), (icx, icy), int(8 + pulse), 1)
            # Dibujar silueta de campana fúnebre
            bell_pts = [(icx, icy - 7), (icx + 5, icy + 2), (icx + 7, icy + 6), (icx - 7, icy + 6), (icx - 5, icy + 2)]
            pygame.draw.polygon(surface, (170, 235, 255), bell_pts)
            pygame.draw.circle(surface, (255, 255, 255), (icx, icy + 7), 2)
            return

        ir = int(self.current_r)
        if ir < 4:
            return
        rect = pygame.Rect(icx - ir, icy - ir, ir * 2, ir * 2)
        start_a = (self.gap_angle + self.gap_size * 0.5)
        end_a = (self.gap_angle + math.pi * 2 - self.gap_size * 0.5)
        pygame.draw.arc(surface, (140, 235, 255), rect, start_a, end_a, 3)
        pygame.draw.arc(surface, (255, 255, 255), rect, start_a, end_a, 1)


class ChaosBouncingScythe(Bullet):
    """Guadaña rápida que rebota en los bordes de la arena a ángulos impredecibles."""
    def __init__(self, x, y, vx, vy, max_bounces=4):
        super().__init__(x, y, radius=5.5)
        self.vx = float(vx)
        self.vy = float(vy)
        self.bounces_left = max_bounces
        self.spin = 0.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.spin += dt * 19.0
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Rebotes caóticos en bordes
        bounced = False
        if self.x <= arena_rect.left + 5 and self.vx < 0:
            self.vx = abs(self.vx) + random.uniform(-10, 10)
            self.vy += random.uniform(-25, 25)
            bounced = True
        elif self.x >= arena_rect.right - 5 and self.vx > 0:
            self.vx = -abs(self.vx) + random.uniform(-10, 10)
            self.vy += random.uniform(-25, 25)
            bounced = True

        if self.y <= arena_rect.top + 5 and self.vy < 0:
            self.vy = abs(self.vy) + random.uniform(-10, 10)
            self.vx += random.uniform(-25, 25)
            bounced = True
        elif self.y >= arena_rect.bottom - 5 and self.vy > 0:
            self.vy = -abs(self.vy) + random.uniform(-10, 10)
            self.vx += random.uniform(-25, 25)
            bounced = True

        if bounced:
            self.bounces_left -= 1
            if self.bounces_left <= 0:
                self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pts = []
        for i in range(4):
            ang = self.spin + i * (math.pi / 2.0)
            r = 7 if i % 2 == 0 else 3
            pts.append((ix + int(math.cos(ang) * r), iy + int(math.sin(ang) * r)))
        pygame.draw.polygon(surface, (255, 185, 40), pts)
        pygame.draw.polygon(surface, (235, 45, 75), pts, 1)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 2)


class HomingSoulOrb(Bullet):
    """Ánima perspicaz que rastrea la posición del alma con inercia y curvas suaves."""
    def __init__(self, x, y, speed=86.0, turn_rate=3.6, lifespan=3.2):
        super().__init__(x, y, radius=4.2)
        self.speed = float(speed)
        self.turn_rate = float(turn_rate)
        self.lifespan = float(lifespan)
        self.angle = random.uniform(0, math.pi * 2)
        self.time = 0.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.alive = False
            return

        if soul_pos:
            target_ang = math.atan2(soul_pos[1] - self.y, soul_pos[0] - self.x)
            diff = (target_ang - self.angle + math.pi) % (math.pi * 2) - math.pi
            self.angle += max(-self.turn_rate * dt, min(self.turn_rate * dt, diff))

        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt

        if not arena_rect.inflate(40, 40).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (175, 120, 255), (ix, iy), 5)
        pygame.draw.circle(surface, (245, 220, 255), (ix, iy), 3)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 1)


class DarkGravityVortexBullet(Bullet):
    """Núcleo gravitacional abismal que atrae al alma hacia el vórtice tras una fase de formación advertida."""
    def __init__(self, cx, cy, duration=4.8, forming_timer=0.70):
        super().__init__(cx, cy, radius=9.0)
        self.duration = float(duration)
        self.forming_timer = float(forming_timer)
        self.time = 0.0

    def is_active(self):
        return self.alive and self.time >= self.forming_timer

    def collides_with_soul(self, soul_pos, soul_radius=3.0):
        if not self.is_active():
            return False
        return super().collides_with_soul(soul_pos, soul_radius)

    def check_graze(self, soul_pos, graze_radius=12.0):
        if not self.is_active():
            return False
        return super().check_graze(soul_pos, graze_radius)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        if self.time >= self.duration:
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        if not self.is_active():
            # Fase de invocación: anillos de runa púrpura que se concentran hacia el centro sin dañar
            form_progress = self.time / max(0.01, self.forming_timer)
            spin = self.time * 6.0
            r_form = max(4, int(26.0 * (1.0 - form_progress * 0.45)))
            flash = (int(self.time * 26) % 2 == 0)
            pygame.draw.circle(surface, (235, 35, 85) if flash else (135, 20, 60), (ix, iy), r_form, 1)
            for i in range(4):
                a = spin + i * (math.pi / 2.0)
                spk_x = int(ix + math.cos(a) * r_form)
                spk_y = int(iy + math.sin(a) * r_form)
                pygame.draw.line(surface, (255, 220, 110), (ix, iy), (spk_x, spk_y), 1)
            pygame.draw.circle(surface, (255, 255, 255), (ix, iy), 2)
            return

        pulse = int(math.sin(self.time * 9.0) * 2)
        # Núcleo oscuro activo con horizonte de sucesos
        pygame.draw.circle(surface, (0, 0, 0), (ix, iy), 11 + pulse)
        pygame.draw.circle(surface, (235, 35, 85), (ix, iy), 11 + pulse, 2)
        pygame.draw.circle(surface, (45, 8, 65), (ix, iy), 7)
        # Anillos de acreción giratorios
        for i in range(3):
            ang = self.time * 4.5 + i * 2.1
            rx = int(ix + math.cos(ang) * 16)
            ry = int(iy + math.sin(ang) * 16)
            pygame.draw.circle(surface, (255, 215, 120), (rx, ry), 2)


class LaserCrossGridBullet(Bullet):
    """Láser dimensional con carril de advertencia claro (0.70s) que barre columnas o filas completas."""
    def __init__(self, arena_rect, pos, is_vertical=False, warn_time=0.70, duration=1.15):
        super().__init__(pos if is_vertical else arena_rect.centerx, arena_rect.centery if is_vertical else pos, radius=5.0)
        self.is_vertical = is_vertical
        self.pos = float(pos)
        self.warn_time = float(warn_time)
        self.duration = float(duration)
        self.timer = 0.0
        self.arena_rect = arena_rect

    def update(self, dt, arena_rect, soul_pos=None):
        self.arena_rect = arena_rect
        self.timer += dt
        if self.timer >= self.duration:
            self.alive = False

    def collides_with_soul(self, soul_pos, soul_radius=3.0):
        if self.timer < self.warn_time or not self.alive:
            return False
        if self.is_vertical:
            return abs(soul_pos[0] - self.pos) <= (5.0 + soul_radius) and (self.arena_rect.top <= soul_pos[1] <= self.arena_rect.bottom)
        else:
            return abs(soul_pos[1] - self.pos) <= (5.0 + soul_radius) and (self.arena_rect.left <= soul_pos[0] <= self.arena_rect.right)

    def check_graze(self, soul_pos, graze_radius=15.0):
        if self.grazed or self.timer < self.warn_time or not self.alive:
            return False
        if self.is_vertical:
            if abs(soul_pos[0] - self.pos) <= graze_radius:
                self.grazed = True
                return True
        else:
            if abs(soul_pos[1] - self.pos) <= graze_radius:
                self.grazed = True
                return True
        return False

    def draw(self, surface):
        ar = self.arena_rect
        ip = int(self.pos)
        if self.timer < self.warn_time:
            # Carril de advertencia completo de 12px de ancho con líneas guía y flechas
            flash = (int(self.timer * 28) % 2 == 0)
            col_edge = (255, 60, 85) if flash else (160, 35, 60)
            col_core = (255, 235, 120) if flash else (220, 60, 100)
            if self.is_vertical:
                pygame.draw.line(surface, col_edge, (ip - 6, ar.top), (ip - 6, ar.bottom), 1)
                pygame.draw.line(surface, col_edge, (ip + 6, ar.top), (ip + 6, ar.bottom), 1)
                pygame.draw.line(surface, col_core, (ip, ar.top), (ip, ar.bottom), 1)
                # Flechas de advertencia verticales
                for vy in range(ar.top + 16, ar.bottom - 10, 26):
                    pygame.draw.line(surface, (255, 255, 255), (ip - 3, vy - 2), (ip, vy + 2), 1)
                    pygame.draw.line(surface, (255, 255, 255), (ip + 3, vy - 2), (ip, vy + 2), 1)
            else:
                pygame.draw.line(surface, col_edge, (ar.left, ip - 6), (ar.right, ip - 6), 1)
                pygame.draw.line(surface, col_edge, (ar.left, ip + 6), (ar.right, ip + 6), 1)
                pygame.draw.line(surface, col_core, (ar.left, ip), (ar.right, ip), 1)
                # Flechas de advertencia horizontales
                for vx in range(ar.left + 16, ar.right - 10, 26):
                    pygame.draw.line(surface, (255, 255, 255), (vx - 2, ip - 3), (vx + 2, ip), 1)
                    pygame.draw.line(surface, (255, 255, 255), (vx - 2, ip + 3), (vx + 2, ip), 1)
        else:
            # Haz masivo de láser carmesí y negro
            if self.is_vertical:
                pygame.draw.rect(surface, (0, 0, 0), (ip - 6, ar.top, 12, ar.height))
                pygame.draw.rect(surface, (235, 35, 85), (ip - 4, ar.top, 8, ar.height))
                pygame.draw.line(surface, (255, 255, 255), (ip, ar.top), (ip, ar.bottom), 2)
            else:
                pygame.draw.rect(surface, (0, 0, 0), (ar.left, ip - 6, ar.width, 12))
                pygame.draw.rect(surface, (235, 35, 85), (ar.left, ip - 4, ar.width, 8))
                pygame.draw.line(surface, (255, 255, 255), (ar.left, ip), (ar.right, ip), 2)


class FracturedMirrorShards(Bullet):
    """Cluster de cristal que se detiene en seco, vibra con advertencia y estalla en 6 esquirlas a velocidades variables."""
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, radius=6.0)
        self.vx = float(vx)
        self.vy = float(vy)
        self.state = "FLY"  # FLY, CHARGE, EXPLODED
        self.charge_timer = 0.48
        self.shards = []
        self.time = 0.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        if self.state == "FLY":
            self.vx *= 0.94
            self.vy *= 0.94
            self.x += self.vx * dt
            self.y += self.vy * dt
            if math.hypot(self.vx, self.vy) < 14.0:
                self.state = "CHARGE"
        elif self.state == "CHARGE":
            self.charge_timer -= dt
            if self.charge_timer <= 0:
                self.state = "EXPLODED"
                # Estallido en 6 esquirlas erráticas
                for i in range(6):
                    ang = (i / 6.0) * math.pi * 2 + random.uniform(-0.25, 0.25)
                    spd = random.uniform(70.0, 115.0)
                    self.shards.append({
                        "x": self.x, "y": self.y,
                        "vx": math.cos(ang) * spd,
                        "vy": math.sin(ang) * spd,
                        "alive": True,
                        "grazed": False
                    })
        elif self.state == "EXPLODED":
            all_dead = True
            for sh in self.shards:
                if sh["alive"]:
                    sh["x"] += sh["vx"] * dt
                    sh["y"] += sh["vy"] * dt
                    if not arena_rect.inflate(30, 30).collidepoint(sh["x"], sh["y"]):
                        sh["alive"] = False
                    else:
                        all_dead = False
            if all_dead:
                self.alive = False

    def collides_with_soul(self, soul_pos, soul_radius=3.0):
        if self.state != "EXPLODED":
            return super().collides_with_soul(soul_pos, soul_radius)
        for sh in self.shards:
            if sh["alive"] and math.hypot(sh["x"] - soul_pos[0], sh["y"] - soul_pos[1]) <= (3.8 + soul_radius):
                return True
        return False

    def check_graze(self, soul_pos, graze_radius=15.0):
        if self.state != "EXPLODED":
            return super().check_graze(soul_pos, graze_radius)
        any_graze = False
        for sh in self.shards:
            if sh["alive"] and not sh["grazed"] and math.hypot(sh["x"] - soul_pos[0], sh["y"] - soul_pos[1]) <= (3.8 + graze_radius):
                sh["grazed"] = True
                any_graze = True
        return any_graze

    def draw(self, surface):
        if self.state in ("FLY", "CHARGE"):
            ix, iy = int(self.x), int(self.y)
            shake = random.randint(-2, 2) if self.state == "CHARGE" else 0
            if self.state == "CHARGE":
                # Rayos radiales de peligro avisando de la inminente fragmentación
                flash = (int(self.time * 26) % 2 == 0)
                col_spk = (255, 235, 110) if flash else (255, 60, 95)
                for i in range(6):
                    ang = (i / 6.0) * math.pi * 2
                    pygame.draw.line(surface, col_spk, (ix, iy), (int(ix + math.cos(ang) * 12), int(iy + math.sin(ang) * 12)), 1)
            pts = [(ix + shake, iy - 7), (ix + 6 + shake, iy), (ix + shake, iy + 7), (ix - 6 + shake, iy)]
            pygame.draw.polygon(surface, (245, 50, 100), pts)
            pygame.draw.polygon(surface, (0, 0, 0), pts, 2)
            pygame.draw.circle(surface, (255, 255, 255), (ix + shake, iy), 2)
        else:
            for sh in self.shards:
                if sh["alive"]:
                    sx, sy = int(sh["x"]), int(sh["y"])
                    pygame.draw.circle(surface, (255, 60, 110), (sx, sy), 4)
                    pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 2)


# ==========================================================
# PROYECTILES ERRÁTICOS DEL DARK WORLD (BUFÓN DEL CAOS Y CENTINELA NEÓN)
# ==========================================================
class ErraticChaosCardBullet(Bullet):
    """Carta del Caos del Dark World que zigzaguea bruscamente y hace fintas erráticas para retar el Parry."""
    def __init__(self, x, y, vx, vy, suit="DIAMOND"):
        super().__init__(x, y, radius=4.5)
        self.vx = float(vx)
        self.vy = float(vy)
        self.suit = suit
        self.time = 0.0
        self.phase = random.uniform(0, math.pi * 2)
        self.juke_timer = random.uniform(0.18, 0.34)
        self.spin = random.uniform(0, math.pi * 2)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.spin += dt * 14.0
        self.juke_timer -= dt
        if self.juke_timer <= 0:
            self.juke_timer = random.uniform(0.18, 0.34)
            # Cambio brusco de ángulo (finta errática)
            ang = math.atan2(self.vy, self.vx) + random.uniform(-0.85, 0.85)
            if soul_pos is not None and random.random() < 0.55:
                to_soul = math.atan2(soul_pos[1] - self.y, soul_pos[0] - self.x)
                ang = to_soul + random.uniform(-0.48, 0.48)
            spd = max(65.0, min(145.0, math.hypot(self.vx, self.vy) * random.uniform(0.88, 1.22)))
            self.vx = math.cos(ang) * spd
            self.vy = math.sin(ang) * spd

        perp_x = -self.vy
        perp_y = self.vx
        mag = max(1.0, math.hypot(perp_x, perp_y))
        zig = math.sin(self.time * 18.0 + self.phase) * 52.0
        self.x += (self.vx + (perp_x / mag) * zig) * dt
        self.y += (self.vy + (perp_y / mag) * zig) * dt
        if not arena_rect.inflate(34, 34).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        col = (255, 70, 195) if self.suit == "DIAMOND" else (95, 240, 255)
        pts = [
            (ix + int(math.cos(self.spin) * 7), iy + int(math.sin(self.spin) * 7)),
            (ix + int(math.cos(self.spin + 1.57) * 4), iy + int(math.sin(self.spin + 1.57) * 4)),
            (ix + int(math.cos(self.spin + 3.14) * 7), iy + int(math.sin(self.spin + 3.14) * 7)),
            (ix + int(math.cos(self.spin + 4.71) * 4), iy + int(math.sin(self.spin + 4.71) * 4)),
        ]
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 2)
        pygame.draw.circle(surface, (255, 245, 120), (ix, iy), 2)


class CyberNeonGlitchBullet(Bullet):
    """Proyectil cibernético del Dark World que da saltos laterales ('glitch') y acelerones súbitos."""
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, radius=4.5)
        self.vx = float(vx)
        self.vy = float(vy)
        self.time = 0.0
        self.glitch_timer = random.uniform(0.16, 0.28)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.glitch_timer -= dt
        if self.glitch_timer <= 0:
            self.glitch_timer = random.uniform(0.16, 0.28)
            # Desplazamiento lateral de glitch dentro de la arena
            perp_x = -self.vy
            perp_y = self.vx
            mag = max(1.0, math.hypot(perp_x, perp_y))
            jump = random.choice([-11.0, 11.0])
            nx = self.x + (perp_x / mag) * jump
            ny = self.y + (perp_y / mag) * jump
            if arena_rect.inflate(-8, -8).collidepoint(nx, ny):
                self.x, self.y = nx, ny

        burst = 1.0 + 0.65 * math.sin(self.time * 15.0 + self.phase)
        self.x += self.vx * burst * dt
        self.y += self.vy * burst * dt
        if not arena_rect.inflate(32, 32).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        jit = random.choice([-1, 0, 1])
        pygame.draw.rect(surface, (0, 0, 0), (ix - 6 + jit, iy - 6, 12, 12), border_radius=2)
        pygame.draw.rect(surface, (65, 245, 255), (ix - 4 + jit, iy - 4, 8, 8), border_radius=1)
        pygame.draw.rect(surface, (255, 80, 215), (ix - 2, iy - 2, 4, 4))


# ==========================================================
# PROYECTILES DE ENTRENAMIENTO DEL TUTORIAL (ESQUIVA, PARRY [Z], DASH [X])
# ==========================================================
class TutorialDodgeWaveBullet(Bullet):
    """Barrera de esferas cian con un HUECO SEGURO iluminado que obliga al jugador a mover el corazón para ESQUIVAR.
    Solo cuenta como esquiva válida cuando la barrera cruza la posición X del corazón a través del hueco SIN golpearlo."""
    def __init__(self, arena_rect, gap_y, from_right=True, speed=78.0):
        start_x = float(arena_rect.right - 4) if from_right else float(arena_rect.left + 4)
        super().__init__(start_x, gap_y, radius=5.0)
        self.arena_rect = arena_rect
        self.gap_y = float(gap_y)
        self.gap_half_h = 22.0
        self.vx = -abs(speed) if from_right else abs(speed)
        self.warn_timer = 0.26
        self.time = 0.0
        self.hit_player = False
        self.dodge_verified = False

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.arena_rect = arena_rect
        if self.warn_timer > 0:
            self.warn_timer -= dt
            return
        self.x += self.vx * dt
        if self.x < arena_rect.left - 12 or self.x > arena_rect.right + 12:
            self.alive = False

    def collides_with_soul(self, soul_center, soul_radius=3.0):
        if self.warn_timer > 0:
            return False
        if abs(self.x - soul_center[0]) <= (4.5 + soul_radius):
            # Si el corazón NO está dentro del hueco seguro, recibe impacto y anula esta repetición
            if abs(soul_center[1] - self.gap_y) > (self.gap_half_h - soul_radius):
                self.hit_player = True
                return True
        return False

    def check_clean_dodge(self, soul_center):
        """Retorna True una sola vez cuando la barrera ya pasó por el corazón habiendo cruzado limpiamente por el hueco sin golpear."""
        if self.warn_timer > 0 or self.hit_player or self.dodge_verified:
            return False
        passed_x = (self.vx < 0 and self.x < soul_center[0] - 5.0) or (self.vx > 0 and self.x > soul_center[0] + 5.0)
        if passed_x and abs(soul_center[1] - self.gap_y) <= (self.gap_half_h + 6.0):
            self.dodge_verified = True
            return True
        return False

    def check_graze(self, soul_center, graze_radius=18.0):
        if self.warn_timer > 0 or self.grazed or self.hit_player:
            return False
        if abs(self.x - soul_center[0]) <= 12.0 and abs(soul_center[1] - self.gap_y) <= (self.gap_half_h + 4.0):
            self.grazed = True
            return True
        return False

    def draw(self, surface):
        ar = self.arena_rect
        ix = int(self.x)
        gy_top = int(self.gap_y - self.gap_half_h)
        gy_bot = int(self.gap_y + self.gap_half_h)

        # Marco verde brillante del HUECO SEGURO donde el jugador debe moverse para esquivar
        pulse_g = 180 + int(abs(math.sin(self.time * 12.0)) * 75)
        pygame.draw.rect(surface, (40, pulse_g, 110), (ix - 6, gy_top + 2, 12, max(6, gy_bot - gy_top - 4)), 2, border_radius=3)

        # Esferas de la barrera por encima y por debajo del hueco
        for by in range(ar.top + 6, gy_top - 2, 11):
            pygame.draw.circle(surface, (0, 0, 0), (ix, by), 5)
            pygame.draw.circle(surface, (85, 225, 255), (ix, by), 4)
            pygame.draw.circle(surface, (255, 255, 255), (ix, by), 2)
        for by in range(gy_bot + 4, ar.bottom - 4, 11):
            pygame.draw.circle(surface, (0, 0, 0), (ix, by), 5)
            pygame.draw.circle(surface, (85, 225, 255), (ix, by), 4)
            pygame.draw.circle(surface, (255, 255, 255), (ix, by), 2)


class TutorialParryOrbBullet(Bullet):
    """Esfera esmeralda guiada hacia el corazón con un anillo de sincronización que indica cuándo pulsar [Z] para hacer PARRY."""
    def __init__(self, x, y, target_x, target_y, speed=64.0):
        super().__init__(x, y, radius=6.4)
        ang = math.atan2(target_y - y, target_x - x)
        self.vx = math.cos(ang) * speed
        self.vy = math.sin(ang) * speed
        self.speed = speed
        self.time = 0.0
        self.dist_to_soul = 999.0

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        if soul_pos is not None:
            self.dist_to_soul = math.hypot(soul_pos[0] - self.x, soul_pos[1] - self.y)
            desired = math.atan2(soul_pos[1] - self.y, soul_pos[0] - self.x)
            curr = math.atan2(self.vy, self.vx)
            diff = (desired - curr + math.pi) % (math.pi * 2) - math.pi
            new_ang = curr + max(-2.6 * dt, min(2.6 * dt, diff))
            self.vx = math.cos(new_ang) * self.speed
            self.vy = math.sin(new_ang) * self.speed
        self.x += self.vx * dt
        self.y += self.vy * dt
        if not arena_rect.inflate(28, 28).collidepoint(self.x, self.y):
            self.alive = False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        in_parry_zone = (self.dist_to_soul <= 28.0)
        ring_col = (255, 245, 90) if in_parry_zone else (45, 255, 130)
        pulse_r = (8 if in_parry_zone else 11) + int(abs(math.sin(self.time * 12.0)) * 4)
        pygame.draw.circle(surface, ring_col, (ix, iy), pulse_r, 2 if in_parry_zone else 1)
        pygame.draw.circle(surface, (0, 0, 0), (ix, iy), 7)
        pygame.draw.circle(surface, (55, 245, 125), (ix, iy), 5)
        pygame.draw.circle(surface, (235, 255, 240), (ix, iy), 2)


class TutorialDashWallBullet(Bullet):
    """Muro de energía dorada de ancho/alto COMPLETO sin huecos: obliga a usar DASH con [X] para atravesarlo sin daño.
    Solo cuenta como repetición válida cuando el corazón cruza de un lado al otro del muro usando el impulso del DASH [X]."""
    def __init__(self, arena_rect, horizontal_sweep=True, from_end=True, speed=104.0):
        self.arena_rect = arena_rect
        self.horizontal_sweep = horizontal_sweep
        if horizontal_sweep:
            sx = float(arena_rect.right - 4) if from_end else float(arena_rect.left + 4)
            sy = float(arena_rect.centery)
            self.vel = -abs(speed) if from_end else abs(speed)
        else:
            sx = float(arena_rect.centerx)
            sy = float(arena_rect.bottom - 4) if from_end else float(arena_rect.top + 4)
            self.vel = -abs(speed) if from_end else abs(speed)
        super().__init__(sx, sy, radius=5.0)
        self.warn_timer = 0.38
        self.time = 0.0
        self.hit_player = False
        self.dash_verified = False

    def update(self, dt, arena_rect, soul_pos=None):
        self.time += dt
        self.arena_rect = arena_rect
        if self.warn_timer > 0:
            self.warn_timer -= dt
            return
        if self.horizontal_sweep:
            self.x += self.vel * dt
            if self.x < arena_rect.left - 10 or self.x > arena_rect.right + 10:
                self.alive = False
        else:
            self.y += self.vel * dt
            if self.y < arena_rect.top - 10 or self.y > arena_rect.bottom + 10:
                self.alive = False

    def collides_with_soul(self, soul_center, soul_radius=3.0):
        if self.warn_timer > 0:
            return False
        if self.horizontal_sweep:
            return abs(self.x - soul_center[0]) <= (4.0 + soul_radius)
        else:
            return abs(self.y - soul_center[1]) <= (4.0 + soul_radius)

    def check_clean_dash_cross(self, soul_center, is_dashing_or_iframes):
        """Retorna True una sola vez cuando el jugador atraviesa el muro activamente con DASH [X] sin haber recibido daño."""
        if self.warn_timer > 0 or self.hit_player or self.dash_verified:
            return False
        dist = abs(self.x - soul_center[0]) if self.horizontal_sweep else abs(self.y - soul_center[1])
        if is_dashing_or_iframes and dist <= 18.0:
            self.dash_verified = True
            return True
        return False

    def check_graze(self, soul_center, graze_radius=16.0):
        if self.warn_timer > 0 or self.grazed:
            return False
        dist = abs(self.x - soul_center[0]) if self.horizontal_sweep else abs(self.y - soul_center[1])
        if dist <= 12.0:
            self.grazed = True
            return True
        return False

    def draw(self, surface):
        ar = self.arena_rect
        flash = (int(self.time * 24) % 2 == 0)
        if self.horizontal_sweep:
            ix = int(self.x)
            if self.warn_timer > 0:
                col = (255, 230, 85) if flash else (180, 130, 40)
                pygame.draw.line(surface, col, (ix, ar.top + 2), (ix, ar.bottom - 2), 2)
            else:
                pygame.draw.rect(surface, (0, 0, 0), (ix - 5, ar.top + 2, 10, ar.height - 4))
                pygame.draw.rect(surface, (255, 210, 65), (ix - 3, ar.top + 2, 6, ar.height - 4))
                pygame.draw.line(surface, (255, 255, 255), (ix, ar.top + 2), (ix, ar.bottom - 2), 2)
        else:
            iy = int(self.y)
            if self.warn_timer > 0:
                col = (255, 230, 85) if flash else (180, 130, 40)
                pygame.draw.line(surface, col, (ar.left + 2, iy), (ar.right - 2, iy), 2)
            else:
                pygame.draw.rect(surface, (0, 0, 0), (ar.left + 2, iy - 5, ar.width - 4, 10))
                pygame.draw.rect(surface, (255, 210, 65), (ar.left + 2, iy - 3, ar.width - 4, 6))
                pygame.draw.line(surface, (255, 255, 255), (ar.left + 2, iy), (ar.right - 2, iy), 2)







