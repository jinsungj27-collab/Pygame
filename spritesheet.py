import pygame
from sprites import make_sprite
from sprites import (
    SMALL_MARIO_IDLE, SMALL_MARIO_WALK1, SMALL_MARIO_WALK2, SMALL_MARIO_WALK3,
    SMALL_MARIO_JUMP, SMALL_MARIO_DUCK,
    BIG_MARIO_IDLE, BIG_MARIO_WALK1, BIG_MARIO_WALK2, BIG_MARIO_WALK3,
    BIG_MARIO_JUMP, BIG_MARIO_DUCK,
    GOOMBA_WALK1, GOOMBA_WALK2, GOOMBA_SQUISHED,
    KOOPA_WALK1, KOOPA_WALK2, KOOPA_SHELL,
    BLOCK_GROUND, BLOCK_BRICK, BLOCK_QUESTION_F1,
    BLOCK_QUESTION_F2, BLOCK_SOLID, BLOCK_SPIKE,
    ITEM_MUSHROOM, ITEM_COIN_F1, ITEM_COIN_F2,
    FLAG,
)

_SCALE = 2.5


def _make(data, flip_x=False, palette=None):
    return make_sprite(data, scale=_SCALE, flip_x=flip_x, palette=palette)


def _make_boss(frame):
    W, H = 122, 112
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    green  = (44, 165, 64);  dgreen = (26, 112, 42)
    orange = (240, 150, 44); dor    = (198, 108, 22)
    yellow = (250, 220, 64); lyellow= (255, 240, 150)
    white  = (255, 255, 255); black = (16, 16, 16); red = (212, 44, 44)

    pygame.draw.ellipse(s, dgreen, (46, 22, 72, 78))
    pygame.draw.ellipse(s, green,  (54, 30, 56, 62))
    for sx, sy in [(62, 26), (88, 22), (104, 36), (98, 64), (72, 56)]:
        pygame.draw.polygon(s, yellow,  [(sx, sy), (sx - 9, sy + 15), (sx + 9, sy + 15)])
        pygame.draw.polygon(s, lyellow, [(sx, sy + 3), (sx - 4, sy + 13), (sx + 4, sy + 13)])

    pygame.draw.ellipse(s, green,  (20, 44, 72, 58))
    pygame.draw.ellipse(s, orange, (28, 60, 46, 40))
    pygame.draw.ellipse(s, dor,    (28, 60, 46, 40), 3)

    if frame == 0:
        pygame.draw.rect(s, green,  (28, 92, 20, 18), border_radius=5)
        pygame.draw.rect(s, dgreen, (60, 97, 20, 13), border_radius=5)
    else:
        pygame.draw.rect(s, dgreen, (28, 97, 20, 13), border_radius=5)
        pygame.draw.rect(s, green,  (60, 92, 20, 18), border_radius=5)
    for fx in (30, 62):
        for c in range(3):
            pygame.draw.polygon(s, white,
                [(fx + c * 6, 108), (fx + c * 6 + 5, 108), (fx + c * 6 + 2, 102)])

    pygame.draw.ellipse(s, green, (16, 60, 22, 26))
    for c in range(3):
        pygame.draw.polygon(s, white,
            [(14, 78 + c * 6), (20, 80 + c * 6), (12, 84 + c * 6)])

    pygame.draw.ellipse(s, green, (6, 16, 54, 48))
    pygame.draw.ellipse(s, green, (0, 38, 36, 26))
    pygame.draw.rect(s, black, (5, 52, 30, 8))
    for tx in range(8, 34, 8):
        pygame.draw.polygon(s, white, [(tx, 52), (tx + 6, 52), (tx + 3, 59)])
    pygame.draw.circle(s, white, (32, 34), 9)
    pygame.draw.circle(s, black, (28, 34), 4)
    pygame.draw.line(s, red, (20, 22), (42, 30), 5)
    pygame.draw.polygon(s, white, [(14, 16), (7, 0), (24, 14)])
    pygame.draw.polygon(s, white, [(42, 16), (49, 0), (32, 14)])
    return s


def _make_bird(frame):
    W, H = 46, 32
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    body  = (150, 90, 220); wing = (108, 58, 178)
    belly = (240, 240, 255); beak = (245, 160, 40); eye = (18, 18, 18)

    pygame.draw.polygon(s, wing, [(32, 15), (46, 7), (45, 22)])
    pygame.draw.ellipse(s, body, (8, 11, 30, 16))
    pygame.draw.circle(s, body, (15, 15), 9)
    pygame.draw.ellipse(s, belly, (15, 17, 18, 9))
    pygame.draw.polygon(s, beak, [(1, 15), (11, 11), (11, 19)])
    pygame.draw.circle(s, eye, (13, 13), 2)
    if frame == 0:
        pygame.draw.polygon(s, wing, [(18, 13), (27, 0), (35, 13)])
        pygame.draw.polygon(s, body, [(20, 13), (27, 4), (32, 13)])
    else:
        pygame.draw.polygon(s, wing, [(18, 17), (27, 31), (35, 17)])
        pygame.draw.polygon(s, body, [(20, 17), (27, 27), (32, 17)])
    return s


def _make_robot(frame):
    """City-phase walking enemy: a small bipedal robot."""
    W, H = 38, 42
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    steel = (158, 168, 184); dsteel = (96, 106, 122); dark = (44, 50, 62)
    eye = (90, 215, 255); red = (232, 72, 72)

    # Antenna with a blinking light.
    pygame.draw.line(s, dsteel, (W // 2, 1), (W // 2, 8), 2)
    pygame.draw.circle(s, red, (W // 2, 2), 3)

    # Arms.
    pygame.draw.rect(s, dsteel, (2, 16, 5, 12), border_radius=2)
    pygame.draw.rect(s, dsteel, (31, 16, 5, 12), border_radius=2)

    # Head/body block.
    pygame.draw.rect(s, dark,  (5, 8, 28, 24), border_radius=6)
    pygame.draw.rect(s, steel, (7, 10, 24, 20), border_radius=5)
    pygame.draw.rect(s, dsteel, (7, 10, 24, 6), border_radius=3)

    # Visor eye.
    pygame.draw.rect(s, dark, (10, 15, 18, 8), border_radius=3)
    pygame.draw.rect(s, eye,  (12, 17, 14, 4))
    # Chest light.
    pygame.draw.circle(s, red, (W // 2, 27), 3)

    # Legs (alternate for walking).
    if frame == 0:
        pygame.draw.rect(s, dark,   (9, 31, 8, 11), border_radius=2)
        pygame.draw.rect(s, dsteel, (21, 31, 8, 8), border_radius=2)
    else:
        pygame.draw.rect(s, dsteel, (9, 31, 8, 8), border_radius=2)
        pygame.draw.rect(s, dark,   (21, 31, 8, 11), border_radius=2)
    return s


def _make_robot_squished():
    W, H = 38, 42
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    steel = (158, 168, 184); dark = (44, 50, 62); spark = (255, 220, 90)
    pygame.draw.rect(s, dark,  (4, 30, 30, 10), border_radius=4)
    pygame.draw.rect(s, steel, (6, 32, 26, 6), border_radius=3)
    # Sparks from the broken bot.
    for sx in (10, 19, 28):
        pygame.draw.line(s, spark, (sx, 30), (sx - 2, 25), 2)
        pygame.draw.line(s, spark, (sx, 30), (sx + 3, 26), 2)
    return s


def _make_robot_boss(frame):
    """City-phase boss: a hulking mech."""
    W, H = 124, 116
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    steel = (150, 162, 180); dsteel = (92, 102, 120); dark = (40, 46, 58)
    eye = (255, 70, 60); glow = (255, 170, 60); bolt = (70, 78, 94)

    # Shoulder cannons.
    pygame.draw.rect(s, dark,   (6, 34, 22, 18), border_radius=4)
    pygame.draw.rect(s, dsteel, (2, 38, 10, 10), border_radius=3)
    pygame.draw.rect(s, dark,   (96, 34, 22, 18), border_radius=4)
    pygame.draw.rect(s, dsteel, (112, 38, 10, 10), border_radius=3)

    # Main torso.
    pygame.draw.rect(s, dark,  (28, 30, 68, 56), border_radius=10)
    pygame.draw.rect(s, steel, (32, 34, 60, 48), border_radius=8)
    # Chest core (glowing reactor).
    pygame.draw.circle(s, dark, (W // 2, 58), 14)
    pygame.draw.circle(s, glow, (W // 2, 58), 10)
    pygame.draw.circle(s, (255, 240, 200), (W // 2, 58), 4)
    # Body bolts.
    for bx, by in [(40, 40), (84, 40), (40, 78), (84, 78)]:
        pygame.draw.circle(s, bolt, (bx, by), 3)

    # Head.
    pygame.draw.rect(s, dsteel, (48, 6, 28, 24), border_radius=6)
    pygame.draw.rect(s, dark,   (52, 12, 20, 9), border_radius=3)
    pygame.draw.rect(s, eye,    (55, 14, 14, 4))
    # Antennae.
    pygame.draw.line(s, dsteel, (54, 6), (48, -2), 2)
    pygame.draw.line(s, dsteel, (70, 6), (76, -2), 2)

    # Legs (alternate).
    if frame == 0:
        pygame.draw.rect(s, dark,   (36, 86, 22, 28), border_radius=5)
        pygame.draw.rect(s, dsteel, (66, 86, 22, 22), border_radius=5)
    else:
        pygame.draw.rect(s, dsteel, (36, 86, 22, 22), border_radius=5)
        pygame.draw.rect(s, dark,   (66, 86, 22, 28), border_radius=5)
    # Feet.
    pygame.draw.rect(s, bolt, (32, 110, 30, 6), border_radius=2)
    pygame.draw.rect(s, bolt, (62, 110, 30, 6), border_radius=2)
    return s


class SpriteSheet:
    def __init__(self):
        self.apply_character(None)

        self.blocks = {
            'ground':    _make(BLOCK_GROUND),
            'brick':     _make(BLOCK_BRICK),
            'question1': _make(BLOCK_QUESTION_F1),
            'question2': _make(BLOCK_QUESTION_F2),
            'solid':     _make(BLOCK_SOLID),
            'spent':     _make(BLOCK_SOLID),
            'spike':     _make(BLOCK_SPIKE),
        }

        self.items = {
            'mushroom': _make(ITEM_MUSHROOM),
            'coin1':    _make(ITEM_COIN_F1),
            'coin2':    _make(ITEM_COIN_F2),
        }

        self.goomba = {
            'walk1':    _make(GOOMBA_WALK1),
            'walk2':    _make(GOOMBA_WALK2),
            'squished': _make(GOOMBA_SQUISHED),
        }
        self.koopa = {
            'walk1': _make(KOOPA_WALK1),
            'walk2': _make(KOOPA_WALK2),
            'shell': _make(KOOPA_SHELL),
        }

        self.flag = _make(FLAG)

        self.boss = {
            'walk1': _make_boss(0),
            'walk2': _make_boss(1),
        }
        self.boss_city = {
            'walk1': _make_robot_boss(0),
            'walk2': _make_robot_boss(1),
        }

        self.robot = {
            'walk1':    _make_robot(0),
            'walk2':    _make_robot(1),
            'squished': _make_robot_squished(),
        }

        self.bird = {
            'fly1':   _make_bird(0),
            'fly2':   _make_bird(1),
            'fly1_r': pygame.transform.flip(_make_bird(0), True, False),
            'fly2_r': pygame.transform.flip(_make_bird(1), True, False),
        }

    def apply_character(self, palette):
        """Rebuild the player sprite sets recolored with the given palette.

        palette maps palette chars to RGB colors. Passing None uses the
        original Mario colors. This is called whenever the player equips a
        different character or skin in the Shop.
        """
        self.player_small = {
            'idle':  _make(SMALL_MARIO_IDLE,  palette=palette),
            'walk1': _make(SMALL_MARIO_WALK1, palette=palette),
            'walk2': _make(SMALL_MARIO_WALK2, palette=palette),
            'walk3': _make(SMALL_MARIO_WALK3, palette=palette),
            'jump':  _make(SMALL_MARIO_JUMP,  palette=palette),
            'duck':  _make(SMALL_MARIO_DUCK,  palette=palette),
        }
        self.player_small_left = {
            'idle':  _make(SMALL_MARIO_IDLE,  flip_x=True, palette=palette),
            'walk1': _make(SMALL_MARIO_WALK1, flip_x=True, palette=palette),
            'walk2': _make(SMALL_MARIO_WALK2, flip_x=True, palette=palette),
            'walk3': _make(SMALL_MARIO_WALK3, flip_x=True, palette=palette),
            'jump':  _make(SMALL_MARIO_JUMP,  flip_x=True, palette=palette),
            'duck':  _make(SMALL_MARIO_DUCK,  flip_x=True, palette=palette),
        }
        self.player_big = {
            'idle':  _make(BIG_MARIO_IDLE,  palette=palette),
            'walk1': _make(BIG_MARIO_WALK1, palette=palette),
            'walk2': _make(BIG_MARIO_WALK2, palette=palette),
            'walk3': _make(BIG_MARIO_WALK3, palette=palette),
            'jump':  _make(BIG_MARIO_JUMP,  palette=palette),
            'duck':  _make(BIG_MARIO_DUCK,  palette=palette),
        }
        self.player_big_left = {
            'idle':  _make(BIG_MARIO_IDLE,  flip_x=True, palette=palette),
            'walk1': _make(BIG_MARIO_WALK1, flip_x=True, palette=palette),
            'walk2': _make(BIG_MARIO_WALK2, flip_x=True, palette=palette),
            'walk3': _make(BIG_MARIO_WALK3, flip_x=True, palette=palette),
            'jump':  _make(BIG_MARIO_JUMP,  flip_x=True, palette=palette),
            'duck':  _make(BIG_MARIO_DUCK,  flip_x=True, palette=palette),
        }

    def make_preview(self, palette, scale=3):
        """A single idle sprite recolored with palette, for shop thumbnails."""
        return make_sprite(SMALL_MARIO_IDLE, scale=scale, palette=palette)
