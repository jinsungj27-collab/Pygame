import math
import random

import pygame

from constants import GRAVITY, TERMINAL_VELOCITY
from sounds import sfx_stomp, sfx_die, sfx_hazard


class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, kind='classic', grav=0.18):
        super().__init__()
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.grav = grav
        self.life = 200
        self.anim = 0.0
        self.rect = pygame.Rect(0, 0, 22, 22)
        self.rect.center = (int(x), int(y))

    def update(self, tiles=None):
        self.vy += self.grav
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        self.anim += 0.4

        if tiles is not None:
            for t in tiles:
                if self.rect.colliderect(t.rect) and self.vy > 0:
                    self.rect.bottom = t.rect.top
                    self.y = self.rect.centery
                    self.vy = -abs(self.vy) * 0.55
                    break

        self.life -= 1
        if self.life <= 0 or self.y > 700:
            self.kill()

    def draw(self, surface, camera_x):
        dx = int(self.x - camera_x)
        dy = int(self.y)
        flick = int(self.anim) % 2
        if self.kind == 'city':
            # Electric energy bolt.
            outer = (90, 200, 255) if flick == 0 else (60, 170, 255)
            pygame.draw.circle(surface, (20, 60, 130), (dx, dy), 12)
            pygame.draw.circle(surface, outer,         (dx, dy), 10)
            pygame.draw.circle(surface, (220, 245, 255), (dx, dy), 5)
        else:
            outer = (255, 120, 20) if flick == 0 else (255, 80, 10)
            pygame.draw.circle(surface, (120, 30, 0), (dx, dy), 12)
            pygame.draw.circle(surface, outer,        (dx, dy), 10)
            pygame.draw.circle(surface, (255, 220, 90), (dx, dy), 5)


class Laser(pygame.sprite.Sprite):
    """Fast straight-flying energy beam used by the city mech boss."""
    def __init__(self, x, y, vx):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = 0.0
        self.life = 150
        self.anim = 0.0
        self.rect = pygame.Rect(0, 0, 34, 12)
        self.rect.center = (int(x), int(y))

    def update(self, tiles=None):
        self.x += self.vx
        self.rect.center = (int(self.x), int(self.y))
        self.anim += 0.6
        # Beams are absorbed by walls/platforms.
        if tiles is not None:
            for t in tiles:
                if self.rect.colliderect(t.rect):
                    self.kill()
                    return
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def draw(self, surface, camera_x):
        dx = int(self.x - camera_x)
        dy = int(self.y)
        flick = int(self.anim) % 2
        core = (235, 250, 255) if flick == 0 else (205, 240, 255)
        beam = pygame.Rect(dx - 17, dy - 5, 34, 10)
        pygame.draw.rect(surface, (20, 60, 130), beam.inflate(4, 4), border_radius=5)
        pygame.draw.rect(surface, (80, 185, 255), beam, border_radius=5)
        pygame.draw.rect(surface, core, beam.inflate(-10, -4), border_radius=4)


class Shockwave(pygame.sprite.Sprite):
    """A wave of energy that races along the ground, used by slam-style
    bosses. It hugs a fixed Y (the arena floor) and is stopped by walls."""
    def __init__(self, x, y, vx):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = 0.0
        self.life = 120
        self.anim = 0.0
        self.rect = pygame.Rect(0, 0, 26, 30)
        self.rect.midbottom = (int(x), int(y))

    def update(self, tiles=None):
        self.x += self.vx
        self.rect.midbottom = (int(self.x), int(self.y))
        self.anim += 0.5
        if tiles is not None:
            for t in tiles:
                # Walls (solid pillars) block the wave; it rides over the floor.
                if getattr(t, 'tile_type', None) == 'solid' and self.rect.colliderect(t.rect):
                    self.kill()
                    return
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def draw(self, surface, camera_x):
        dx = int(self.x - camera_x)
        dy = int(self.y)
        flick = int(self.anim) % 2
        h = 26 if flick == 0 else 32
        col = (255, 170, 40) if flick == 0 else (255, 120, 20)
        pts = [(dx - 13, dy), (dx, dy - h), (dx + 13, dy)]
        pygame.draw.polygon(surface, (120, 50, 0), pts)
        pygame.draw.polygon(surface, col, pts, 4)
        pygame.draw.line(surface, (255, 235, 150), (dx, dy - h + 4), (dx, dy - 4), 3)


class Boss(pygame.sprite.Sprite):
    WIDTH, HEIGHT = 92, 96

    def __init__(self, x, y, sprites, hp=4, speed=1.6, kind='classic',
                 ai=1, style=None, name=None, tint=None):
        super().__init__()
        self.sprites = sprites
        self.kind = kind
        self.sprite_set = sprites.boss_city if kind == 'city' else sprites.boss
        # Per-boss color identity. tint=None keeps the original sprite look
        # (used by Endless mode and the first two PvP bosses); a tint recolors
        # the boss and gives it a matching glowing aura.
        self.tint = tint
        if tint:
            self.frames = {k: self._mul_tint(v, tint)
                           for k, v in self.sprite_set.items()}
        else:
            self.frames = self.sprite_set
        self.x = float(x)
        self.y = float(y)
        self.vx = -abs(speed)
        self.base_speed = abs(speed)
        self.vy = 0.0

        # Intelligence level (1 = dumb patrol, 10 = relentless hunter) and the
        # attack pattern this boss uses. Higher ai = chases, dodges, predicts
        # the player's movement, dashes and fires faster.
        self.ai = max(1, int(ai))
        self.style = style or ('laser' if kind == 'city' else 'fire')
        self.name = name or ('MEGA MECH' if kind == 'city' else 'GORTHRAX')

        self.hp = hp
        self.max_hp = hp
        self.is_dead = False
        self.dead_timer = 0
        self.invincible = 0
        self.facing_right = False
        self.on_ground = False
        self._air_frames = 0

        self.anim_frame = 0.0
        self.shoot_timer = max(40, 150 - self.ai * 8)
        self.jump_timer = random.randint(160, 260)
        self.move_timer = 0
        self.target_dir = -1
        self.dash_timer = random.randint(180, 320)
        self.dashing = 0
        self.burst = 0
        self.burst_dir = -1
        self.combo = 0  # cycles attack types for 'cross' / 'chaos' bosses

        self.left_bound = 80
        self.right_bound = 720

        self.image = self.sprite_set['walk1']
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.midbottom = (int(x), int(y))

    def set_bounds(self, left, right):
        self.left_bound = left
        self.right_bound = right

    def update(self, tiles, projectiles, player):
        if self.is_dead:
            self.vy = min(self.vy + GRAVITY, TERMINAL_VELOCITY)
            self.y += self.vy
            self.rect.midbottom = (int(self.x), int(self.y))
            self.dead_timer -= 1
            return

        if self.invincible > 0:
            self.invincible -= 1

        self._move(player)

        # Gravity + floor collision.
        self.vy = min(self.vy + GRAVITY, TERMINAL_VELOCITY)
        prev_bottom = self.rect.bottom
        self.y += self.vy
        self.rect.midbottom = (int(self.x), int(self.y))
        self.on_ground = False
        for t in tiles:
            # Land on a surface only when descending onto it from above. This
            # lets the boss jump up onto platforms (obstacles) without snagging
            # on / climbing platforms it merely walks past at body height.
            if self.rect.colliderect(t.rect) and self.vy > 0 and prev_bottom <= t.rect.top + 6:
                self.rect.bottom = t.rect.top
                self.y = self.rect.bottom
                self.vy = 0
                self.on_ground = True

        # Landing detection (for slam shockwaves). Only a real jump counts:
        # require several airborne frames so the 1px resting jitter on the
        # floor doesn't register as a landing every other frame.
        if self.on_ground:
            if self._air_frames > 8:
                self._on_land(projectiles)
            self._air_frames = 0
        else:
            self._air_frames += 1

        self._jump(player)
        self._shoot(projectiles, player)

        self.anim_frame += 0.12 + 0.015 * self.ai

    def _move(self, player):
        """Horizontal movement. Dumb bosses patrol wall-to-wall; smarter ones
        hunt the player and dash, with growing unpredictability."""
        if self.dashing > 0:
            self.dashing -= 1
        elif self.ai >= 2:
            self.move_timer -= 1
            if self.move_timer <= 0:
                self.move_timer = random.randint(
                    max(20, 70 - self.ai * 4), max(45, 140 - self.ai * 6))
                toward = 1 if player.x > self.x else -1
                # The wiser the boss, the more it commits to chasing the player
                # rather than wandering randomly.
                if random.random() < 0.35 + 0.06 * self.ai:
                    self.target_dir = toward
                else:
                    self.target_dir = random.choice([-1, 1])
            self.vx = self.target_dir * self.base_speed

            # Dash bursts toward the player (ai 5+).
            self.dash_timer -= 1
            if self.ai >= 5 and self.dash_timer <= 0 and self.on_ground:
                self.dash_timer = random.randint(
                    max(80, 260 - self.ai * 12), max(160, 420 - self.ai * 14))
                self.target_dir = 1 if player.x > self.x else -1
                self.vx = self.target_dir * self.base_speed * 2.6
                self.dashing = 26
        # ai == 1 keeps its current vx and just bounces off the walls below.

        self.x += self.vx
        self.rect.centerx = int(self.x)
        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.x = self.rect.centerx
            self.vx = abs(self.vx)
            self.target_dir = 1
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.x = self.rect.centerx
            self.vx = -abs(self.vx)
            self.target_dir = -1
        self.facing_right = self.vx > 0

    def _jump(self, player):
        self.jump_timer -= 1
        if self.jump_timer <= 0 and self.on_ground:
            power = 11 + min(self.ai, 8) * 0.4
            # Smart bosses leap when the player is above them or to close
            # distance; dumb ones just hop on a timer.
            if self.ai >= 3 and player.rect.centery < self.rect.centery - 30:
                power += 2.5
            self.vy = -power
            self.jump_timer = random.randint(
                max(60, 200 - self.ai * 14), max(110, 320 - self.ai * 18))

    def _on_land(self, projectiles):
        if self.style in ('slam', 'chaos') and self.ai >= 6:
            y = self.rect.bottom
            projectiles.add(Shockwave(self.rect.centerx - 30, y, -5.5))
            projectiles.add(Shockwave(self.rect.centerx + 30, y, 5.5))
            sfx_hazard()

    def _shoot(self, projectiles, player):
        # Mid-burst rapid fire (volley / chaos).
        if self.burst > 0:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.burst -= 1
                self.shoot_timer = 9
                self._fire_laser(projectiles, self.burst_dir)
                if self.burst == 0:
                    self.shoot_timer = random.randint(
                        max(60, 150 - self.ai * 9), max(110, 240 - self.ai * 11))
            return

        self.shoot_timer -= 1
        if self.shoot_timer > 0:
            return
        self.shoot_timer = random.randint(
            max(40, 140 - self.ai * 9), max(80, 220 - self.ai * 11))

        direction = -1 if player.x < self.x else 1
        style = self.style
        if style == 'cross':
            style = ['fire', 'laser', 'spread'][self.combo % 3]
            self.combo += 1
        elif style == 'chaos':
            style = ['spread', 'volley', 'aimed', 'rain'][self.combo % 4]
            self.combo += 1

        self._do_attack(style, projectiles, player, direction)
        sfx_hazard()

    def _do_attack(self, style, projectiles, player, direction):
        if style == 'laser':
            self._fire_laser(projectiles, direction)
        elif style == 'volley':
            self.burst = 3
            self.burst_dir = direction
            self.shoot_timer = 1
        elif style == 'spread':
            cx = self.rect.centerx + direction * 30
            cy = self.rect.top + 30
            for vy in (-4.5, -2.5, -0.5):
                projectiles.add(Fireball(cx, cy, direction * 3.4, vy, kind=self.kind))
        elif style == 'rain':
            cx = self.rect.centerx + direction * 20
            cy = self.rect.top + 10
            for vx in (direction * 1.6, direction * 3.2):
                projectiles.add(Fireball(cx, cy, vx, -8.5, kind=self.kind, grav=0.32))
        elif style == 'aimed':
            self._fire_aimed(projectiles, player)
        else:  # 'fire'
            projectiles.add(Fireball(self.rect.centerx + direction * 30,
                                     self.rect.top + 30,
                                     direction * 3.6, -3.0, kind=self.kind))

    def _fire_laser(self, projectiles, direction):
        projectiles.add(Laser(self.rect.centerx + direction * 44,
                              self.rect.bottom - 30,
                              direction * (8.0 + 0.2 * self.ai)))

    def _fire_aimed(self, projectiles, player):
        """A predicted shot: aims where the player is heading, not just where
        they are. Used by high-intelligence snipers."""
        sx = self.rect.centerx
        sy = self.rect.top + 30
        lead = 8 + self.ai  # frames of lead prediction
        tx = player.rect.centerx + getattr(player, 'vx', 0) * lead
        ty = player.rect.centery
        dx = tx - sx
        dy = ty - sy
        dist = max(1.0, math.hypot(dx, dy))
        speed = 6.0 + 0.2 * self.ai
        projectiles.add(Fireball(sx, sy, dx / dist * speed, dy / dist * speed,
                                 kind=self.kind, grav=0.04))

    def stomp(self):
        if self.invincible > 0 or self.is_dead:
            return False
        self.hp -= 1
        self.invincible = 70
        sfx_stomp()
        if self.hp <= 0:
            self.die()
            return True
        return False

    def die(self):
        self.is_dead = True
        self.dead_timer = 100
        self.vx = 0
        self.vy = -6
        sfx_die()

    @staticmethod
    def _mul_tint(img, tint):
        out = img.copy()
        out.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return out

    def _draw_aura(self, surface, camera_x):
        """A soft pulsing colored glow behind the boss so each one reads as a
        distinct threat at a glance."""
        if not self.tint or self.is_dead:
            return
        pulse = 0.5 + 0.5 * math.sin(self.anim_frame * 1.4)
        rw = int(self.WIDTH * 1.25)
        rh = int(self.HEIGHT * 1.2)
        aura = pygame.Surface((rw, rh), pygame.SRCALPHA)
        for i, scale in enumerate((1.0, 0.7, 0.45)):
            alpha = int((40 + 50 * pulse) * (1.0 - i * 0.25))
            rect = pygame.Rect(0, 0, int(rw * scale), int(rh * scale))
            rect.center = (rw // 2, rh // 2)
            pygame.draw.ellipse(aura, (*self.tint, alpha), rect)
        cx = self.rect.centerx - camera_x
        cy = self.rect.centery
        surface.blit(aura, (cx - rw // 2, cy - rh // 2))

    def draw(self, surface, camera_x):
        self._draw_aura(surface, camera_x)
        frame = int(self.anim_frame) % 2
        img = self.frames['walk1'] if frame == 0 else self.frames['walk2']
        if self.facing_right:
            img = pygame.transform.flip(img, True, False)

        if self.is_dead:
            ang = (100 - self.dead_timer) * 8
            img = pygame.transform.rotate(img, ang)
        elif self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            img = img.copy()
            img.fill((255, 120, 120, 0), special_flags=pygame.BLEND_RGB_ADD)

        draw_x = self.rect.centerx - img.get_width() // 2 - camera_x
        draw_y = self.rect.bottom - img.get_height()
        surface.blit(img, (draw_x, draw_y))
