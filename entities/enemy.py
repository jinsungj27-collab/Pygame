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

        self.anim_frame = 0.0
        self.anim_speed = 0.1

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

    # ── Physics update ────────────────────────────────────────────────────────
    def update(self, tiles):
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
        self._collide_tiles(tiles, horizontal=False)

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
                elif self.vy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vy = 0
                    self.y  = self.rect.y

    # ── Animation ─────────────────────────────────────────────────────────────
    def update_image(self):
        frame = int(self.anim_frame) % 2
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

    # ── Combat ────────────────────────────────────────────────────────────────
    def squish(self):
        sfx_stomp()
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

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
