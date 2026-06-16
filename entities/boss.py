import math
import random

import pygame

from constants import GRAVITY, TERMINAL_VELOCITY
from sounds import sfx_stomp, sfx_die, sfx_hazard


class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.life = 200
        self.anim = 0.0
        self.rect = pygame.Rect(0, 0, 22, 22)
        self.rect.center = (int(x), int(y))

    def update(self, tiles=None):
        self.vy += 0.18
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
        outer = (255, 120, 20) if flick == 0 else (255, 80, 10)
        pygame.draw.circle(surface, (120, 30, 0), (dx, dy), 12)
        pygame.draw.circle(surface, outer,        (dx, dy), 10)
        pygame.draw.circle(surface, (255, 220, 90), (dx, dy), 5)


class Boss(pygame.sprite.Sprite):
    WIDTH, HEIGHT = 92, 96

    def __init__(self, x, y, sprites, hp=4, speed=1.6):
        super().__init__()
        self.sprites = sprites
        self.x = float(x)
        self.y = float(y)
        self.vx = -abs(speed)
        self.base_speed = abs(speed)
        self.vy = 0.0

        self.hp = hp
        self.max_hp = hp
        self.is_dead = False
        self.dead_timer = 0
        self.invincible = 0
        self.facing_right = False
        self.on_ground = False

        self.anim_frame = 0.0
        self.shoot_timer = 150
        self.jump_timer = random.randint(160, 260)

        self.left_bound = 80
        self.right_bound = 720

        self.image = sprites.boss['walk1']
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

        self.x += self.vx
        self.rect.centerx = int(self.x)
        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.x = self.rect.centerx
            self.vx = abs(self.vx)
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.x = self.rect.centerx
            self.vx = -abs(self.vx)
        self.facing_right = self.vx > 0

        self.vy = min(self.vy + GRAVITY, TERMINAL_VELOCITY)
        self.y += self.vy
        self.rect.midbottom = (int(self.x), int(self.y))
        self.on_ground = False
        for t in tiles:
            if self.rect.colliderect(t.rect) and self.vy > 0:
                self.rect.bottom = t.rect.top
                self.y = self.rect.bottom
                self.vy = 0
                self.on_ground = True

        self.jump_timer -= 1
        if self.jump_timer <= 0 and self.on_ground:
            self.vy = -11
            self.jump_timer = random.randint(180, 300)

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(110, 180)
            direction = -1 if player.x < self.x else 1
            fb = Fireball(self.rect.centerx + direction * 30,
                          self.rect.top + 30,
                          direction * 3.6, -3.0)
            projectiles.add(fb)
            sfx_hazard()

        self.anim_frame += 0.12

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

    def draw(self, surface, camera_x):
        frame = int(self.anim_frame) % 2
        img = self.sprites.boss['walk1'] if frame == 0 else self.sprites.boss['walk2']
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
