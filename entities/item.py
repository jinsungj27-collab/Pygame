import pygame
from constants import GRAVITY, TERMINAL_VELOCITY, TILE_SIZE
from sounds import sfx_coin


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, sprites):
        super().__init__()
        self.item_type = item_type
        self.sprites   = sprites

        self.x     = float(x)
        self.y     = float(y)
        self.vx    = 1.8
        self.vy    = 0.0
        self.state = "spawning"
        self.spawn_y_target = y - TILE_SIZE

        self.image = (
            self.sprites.items['mushroom']
            if self.item_type == 'mushroom'
            else self.sprites.items['coin1']
        )
        self.rect   = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.anim_frame = 0.0

        if self.item_type == 'coin':
            sfx_coin()
            self.vy = -7.0

    def update(self, tiles):
        if self.state == "spawning":
            if self.item_type == 'mushroom':
                self.y     -= 1.0
                self.rect.y = self.y
                if self.y <= self.spawn_y_target:
                    self.state  = "active"
                    self.rect.y = self.y

            elif self.item_type == 'coin':
                self.vy        += 0.4
                self.y         += self.vy
                self.rect.y     = self.y
                self.anim_frame += 0.2
                frame = int(self.anim_frame) % 2
                self.image = (
                    self.sprites.items['coin1']
                    if frame == 0
                    else self.sprites.items['coin2']
                )
                if self.vy > 0 and self.y >= self.spawn_y_target + 10:
                    self.kill()
            return

        if self.state == "active" and self.item_type == 'mushroom':
            self.vy = min(self.vy + GRAVITY, TERMINAL_VELOCITY)

            self.x      += self.vx
            self.rect.x  = self.x
            self._collide_tiles(tiles, horizontal=True)

            self.y      += self.vy
            self.rect.y  = self.y
            self._collide_tiles(tiles, horizontal=False)

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

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
