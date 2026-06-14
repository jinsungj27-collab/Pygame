import pygame
from constants import COLOR_MAP
from sounds import sfx_block_break


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, particle_type, color=None):
        super().__init__()
        self.x             = float(x)
        self.y             = float(y)
        self.vx            = vx
        self.vy            = vy
        self.particle_type = particle_type
        self.color         = color or (255, 255, 255)

        self.life  = 40
        self.max_life = 40
        self.angle = 0

        self.text = ""
        self.font = None

    @classmethod
    def create_debris(cls, x, y, sprites=None):
        brick_color = COLOR_MAP['p']
        particles = [
            cls(x,      y,      -3, -8, 'debris', brick_color),
            cls(x + 10, y,       3, -8, 'debris', brick_color),
            cls(x,      y + 10, -2, -5, 'debris', brick_color),
            cls(x + 10, y + 10,  2, -5, 'debris', brick_color),
        ]
        sfx_block_break()
        return particles

    @classmethod
    def create_score(cls, x, y, text, font):
        p       = cls(x, y, 0, -2.5, 'score_text')
        p.text  = text
        p.font  = font
        p.life  = 45
        return p

    @classmethod
    def create_spark(cls, x, y, vx, vy, color, life=45):
        p = cls(x, y, vx, vy, 'spark', color)
        p.life = life
        p.max_life = life
        return p

    @classmethod
    def create_firework(cls, x, y, color=None):
        import math as _m
        import random as _r
        col = color or _r.choice([
            (255, 90, 90), (255, 220, 90), (120, 220, 255),
            (160, 255, 140), (255, 150, 230), (255, 255, 255),
        ])
        sparks = []
        count = 18
        for i in range(count):
            ang = (2 * _m.pi * i / count) + _r.uniform(-0.1, 0.1)
            spd = _r.uniform(2.5, 5.5)
            sparks.append(cls.create_spark(
                x, y, _m.cos(ang) * spd, _m.sin(ang) * spd, col, life=40
            ))
        return sparks

    def update(self):
        self.life -= 1
        if self.particle_type == 'debris':
            self.vy    += 0.5
            self.x     += self.vx
            self.y     += self.vy
            self.angle += 10
        elif self.particle_type == 'score_text':
            self.y += self.vy
        elif self.particle_type == 'spark':
            self.vy += 0.12
            self.x  += self.vx
            self.y  += self.vy
        if self.life <= 0:
            self.kill()

    def draw(self, surface, camera_x):
        draw_x = self.x - camera_x
        draw_y = self.y

        if self.particle_type == 'debris':
            size    = 8
            surf    = pygame.Surface((size, size))
            surf.fill(self.color)
            rotated = pygame.transform.rotate(surf, self.angle)
            surface.blit(rotated, (draw_x, draw_y))
        elif self.particle_type == 'score_text' and self.font:
            rendered = self.font.render(self.text, True, (255, 255, 255))
            surface.blit(rendered, (draw_x, draw_y))
        elif self.particle_type == 'spark':
            fade = max(0.0, self.life / max(1, self.max_life))
            r = max(1, int(4 * fade))
            col = (
                int(self.color[0] * fade + 255 * (1 - fade) * 0.3),
                int(self.color[1] * fade),
                int(self.color[2] * fade),
            )
            pygame.draw.circle(surface, col, (int(draw_x), int(draw_y)), r)
