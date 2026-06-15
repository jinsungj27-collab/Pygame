import math

import pygame
from constants import GRAVITY, TERMINAL_VELOCITY
from sounds import sfx_stomp


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, sprites):
        super().__init__()
        self.enemy_type = enemy_type
        self.sprites    = sprites

        self.vx = -1.2
        self.vy = 0.0
        self.x  = float(x)
        self.y  = float(y)

        self.is_dead   = False
        self.dead_timer = 0
        self.in_shell  = False
        self.shell_speed = 8.0
        self.on_ground = False

        self.anim_frame = 0.0
        self.anim_speed = 0.1

        self.is_bird = (enemy_type == 'bird')
        if self.is_bird:
            self.vx = -2.0
            self.fly_y = float(y)
            self.bob_t = float(x) * 0.01
            self.patrol_min = x - 200
            self.patrol_max = x + 200
            self.anim_speed = 0.25
            self.image = self.sprites.bird['fly1']
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.rect.height = 30
            return

        self.image = (
            self.sprites.goomba['walk1']
            if self.enemy_type == 'goomba'
            else self.sprites.koopa['walk1']
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        if self.enemy_type == 'koopa':
            self.rect.height = 50

    def update(self, tiles):
        if self.is_bird:
            self._update_bird()
            return

        if self.is_dead and self.enemy_type == 'goomba':
            self.dead_timer -= 1
            if self.dead_timer <= 0:
                self.kill()
            return

        self.vy = min(self.vy + GRAVITY, TERMINAL_VELOCITY)

        self.x      += self.vx
        self.rect.x  = self.x
        self._collide_tiles(tiles, horizontal=True)

        self.y      += self.vy
        self.rect.y  = self.y
        self.on_ground = False
        self._collide_tiles(tiles, horizontal=False)

        # Walking enemies turn around at the edge of a platform instead of
        # walking off into a gap. Shell-sliding koopas are allowed to slide off.
        if self.on_ground and not self.in_shell and not self._ground_ahead(tiles):
            self.vx = -self.vx

        self.anim_frame += self.anim_speed
        self.update_image()

    def _update_bird(self):
        if self.is_dead:
            self.vy += GRAVITY
            self.y += self.vy
            self.rect.y = int(self.y)
            self.dead_timer -= 1
            if self.dead_timer <= 0 or self.y > 700:
                self.kill()
            return

        self.x += self.vx
        if self.x <= self.patrol_min:
            self.x = self.patrol_min
            self.vx = abs(self.vx)
        elif self.x >= self.patrol_max:
            self.x = self.patrol_max
            self.vx = -abs(self.vx)
        self.rect.x = int(self.x)

        self.bob_t += 0.12
        self.rect.y = int(self.fly_y + math.sin(self.bob_t) * 5)

        self.anim_frame += self.anim_speed
        self.update_image()

    def _collide_tiles(self, tiles, horizontal):
        for tile in tiles:
            if not self.rect.colliderect(tile.rect):
                continue
            if horizontal:
                if self.vx > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
                self.vx = -self.vx
                self.x  = self.rect.x
            else:
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.y  = self.rect.y
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vy = 0
                    self.y  = self.rect.y

    def _ground_ahead(self, tiles):
        """True if there is a tile just below the leading edge (so the enemy is
        about to stay on a platform rather than step off into a gap)."""
        foot_y = self.rect.bottom + 2
        probe_x = self.rect.right + 1 if self.vx >= 0 else self.rect.left - 1
        probe = pygame.Rect(int(probe_x), int(foot_y), 1, 2)
        for tile in tiles:
            if tile.rect.colliderect(probe):
                return True
        return False

    def update_image(self):
        frame = int(self.anim_frame) % 2
        if self.is_bird:
            if self.vx > 0:
                base = self.sprites.bird['fly1_r'] if frame == 0 else self.sprites.bird['fly2_r']
            else:
                base = self.sprites.bird['fly1'] if frame == 0 else self.sprites.bird['fly2']
            self.image = base
            return
        if self.enemy_type == 'goomba':
            if self.is_dead:
                self.image = self.sprites.goomba['squished']
            else:
                self.image = (
                    self.sprites.goomba['walk1']
                    if frame == 0
                    else self.sprites.goomba['walk2']
                )
        elif self.enemy_type == 'koopa':
            if self.in_shell:
                self.image = self.sprites.koopa['shell']
            else:
                base = (
                    self.sprites.koopa['walk1']
                    if frame == 0
                    else self.sprites.koopa['walk2']
                )
                self.image = pygame.transform.flip(base, self.vx > 0, False)

    def squish(self):
        sfx_stomp()
        if self.is_bird:
            self.is_dead    = True
            self.vx         = 0
            self.vy         = 2
            self.dead_timer = 60
            return
        if self.enemy_type == 'goomba':
            self.is_dead    = True
            self.vx         = 0
            self.vy         = 0
            self.dead_timer = 30
            self.image      = self.sprites.goomba['squished']
        elif self.enemy_type == 'koopa':
            if not self.in_shell:
                self.in_shell    = True
                self.vx          = 0
                self.rect.height = 36
                self.y           = self.rect.bottom - 36
                self.rect.y      = self.y
            else:
                self.vx = self.shell_speed

    def kick(self, direction):
        sfx_stomp()
        self.in_shell = True
        self.vx       = direction * self.shell_speed

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
