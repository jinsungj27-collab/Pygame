import random

import pygame


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, sprites):
        super().__init__()
        self.sprites = sprites
        self.anim_frame = random.random() * 2.0
        self.image = sprites.items['coin1']

        self.rect = pygame.Rect(0, 0, 34, 42)
        self.rect.center = (int(x), int(y))

    def update(self, *args):
        self.anim_frame += 0.15
        frame = int(self.anim_frame) % 2
        self.image = self.sprites.items['coin1'] if frame == 0 else self.sprites.items['coin2']

    def draw(self, surface, camera_x):
        img = self.image
        draw_x = self.rect.centerx - img.get_width() // 2 - camera_x
        draw_y = self.rect.centery - img.get_height() // 2
        surface.blit(img, (draw_x, draw_y))
