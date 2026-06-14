import pygame
from constants import COLOR_MAP, TILE_SIZE
from sounds import sfx_block_bump


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type, sprites, contains_item=None):
        super().__init__()
        self.tile_type     = tile_type
        self.sprites       = sprites
        self.contains_item = contains_item

        self.original_y  = y
        self.y           = y
        self.bump_offset = 0
        self.bump_speed  = 0
        self.is_bumped   = False

        self.anim_frame = 0.0
        self.update_image()

        self.rect   = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update_image(self):
        t = self.tile_type
        b = self.sprites.blocks

        if t == 'ground':
            self.image = b['ground']
        elif t == 'brick':
            self.image = b['brick']
        elif t == 'solid':
            self.image = b['solid']
        elif t == 'spent':
            self.image = b['spent']
        elif t == 'spike':
            self.image = b['spike']
        elif t == 'question':
            self.anim_frame += 0.05
            frame      = int(self.anim_frame) % 2
            self.image = b['question1'] if frame == 0 else b['question2']
        elif t.startswith('pipe_'):
            self._draw_pipe_segment(t)

    def _draw_pipe_segment(self, t):
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        gl = COLOR_MAP['g']
        gd = COLOR_MAP['G']

        if t == 'pipe_tl':
            self.image.fill(gl)
            pygame.draw.rect(self.image, gd, (0, 0, 8, TILE_SIZE))
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        elif t == 'pipe_tr':
            self.image.fill(gl)
            pygame.draw.rect(self.image, gd, (TILE_SIZE - 8, 0, 8, TILE_SIZE))
            pygame.draw.rect(self.image, gd, (0, 0, TILE_SIZE, 8))
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        elif t == 'pipe_l':
            self.image.fill(gl)
            pygame.draw.rect(self.image, gd, (0, 0, 8, TILE_SIZE))
            pygame.draw.line(self.image, (0, 0, 0), (0, 0), (0, TILE_SIZE), 2)
            pygame.draw.line(self.image, (0, 0, 0), (TILE_SIZE - 1, 0), (TILE_SIZE - 1, TILE_SIZE), 1)
        elif t == 'pipe_r':
            self.image.fill(gl)
            pygame.draw.rect(self.image, gd, (TILE_SIZE - 8, 0, 8, TILE_SIZE))
            pygame.draw.line(self.image, (0, 0, 0), (TILE_SIZE - 1, 0), (TILE_SIZE - 1, TILE_SIZE), 2)
            pygame.draw.line(self.image, (0, 0, 0), (0, 0), (0, TILE_SIZE), 1)

    def bump(self):
        if not self.is_bumped and self.tile_type in ('brick', 'question'):
            self.is_bumped  = True
            self.bump_speed = -5
            sfx_block_bump()

    def update(self):
        self.update_image()
        if self.is_bumped:
            self.bump_offset += self.bump_speed
            self.bump_speed  += 1.0
            if self.bump_offset >= 0:
                self.bump_offset = 0
                self.is_bumped   = False
                self.bump_speed  = 0
            self.rect.y = self.original_y + self.bump_offset
        else:
            self.rect.y = self.original_y

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
