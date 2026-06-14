"""
SpriteSheet: builds and caches every pygame Surface used by the game.
"""
import pygame
from sprites import make_sprite
from sprites import (
    SMALL_MARIO_IDLE, SMALL_MARIO_WALK1, SMALL_MARIO_WALK2,
    SMALL_MARIO_JUMP, SMALL_MARIO_DUCK,
    BIG_MARIO_IDLE, BIG_MARIO_WALK1, BIG_MARIO_WALK2,
    BIG_MARIO_JUMP, BIG_MARIO_DUCK,
    GOOMBA_WALK1, GOOMBA_WALK2, GOOMBA_SQUISHED,
    KOOPA_WALK1, KOOPA_WALK2, KOOPA_SHELL,
    BLOCK_GROUND, BLOCK_BRICK, BLOCK_QUESTION_F1,
    BLOCK_QUESTION_F2, BLOCK_SOLID, BLOCK_SPIKE,
    ITEM_MUSHROOM, ITEM_COIN_F1, ITEM_COIN_F2,
    FLAG,
)

_SCALE = 2.5


def _make(data, flip_x=False):
    return make_sprite(data, scale=_SCALE, flip_x=flip_x)


def _make_boss(frame):
    """Draw a chunky Bowser-style boss (facing LEFT) with pygame primitives."""
    W, H = 122, 112
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    green  = (44, 165, 64);  dgreen = (26, 112, 42)
    orange = (240, 150, 44); dor    = (198, 108, 22)
    yellow = (250, 220, 64); lyellow= (255, 240, 150)
    white  = (255, 255, 255); black = (16, 16, 16); red = (212, 44, 44)

    # ── Shell (back, right side) ──
    pygame.draw.ellipse(s, dgreen, (46, 22, 72, 78))
    pygame.draw.ellipse(s, green,  (54, 30, 56, 62))
    for sx, sy in [(62, 26), (88, 22), (104, 36), (98, 64), (72, 56)]:
        pygame.draw.polygon(s, yellow,  [(sx, sy), (sx - 9, sy + 15), (sx + 9, sy + 15)])
        pygame.draw.polygon(s, lyellow, [(sx, sy + 3), (sx - 4, sy + 13), (sx + 4, sy + 13)])

    # ── Body + belly ──
    pygame.draw.ellipse(s, green,  (20, 44, 72, 58))
    pygame.draw.ellipse(s, orange, (28, 60, 46, 40))
    pygame.draw.ellipse(s, dor,    (28, 60, 46, 40), 3)

    # ── Legs (alternate by frame) ──
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

    # ── Arm + claw ──
    pygame.draw.ellipse(s, green, (16, 60, 22, 26))
    for c in range(3):
        pygame.draw.polygon(s, white,
            [(14, 78 + c * 6), (20, 80 + c * 6), (12, 84 + c * 6)])

    # ── Head (upper-left) ──
    pygame.draw.ellipse(s, green, (6, 16, 54, 48))
    pygame.draw.ellipse(s, green, (0, 38, 36, 26))            # snout
    pygame.draw.rect(s, black, (5, 52, 30, 8))                # mouth
    for tx in range(8, 34, 8):
        pygame.draw.polygon(s, white, [(tx, 52), (tx + 6, 52), (tx + 3, 59)])
    pygame.draw.circle(s, white, (32, 34), 9)                 # eye
    pygame.draw.circle(s, black, (28, 34), 4)
    pygame.draw.line(s, red, (20, 22), (42, 30), 5)           # angry brow
    pygame.draw.polygon(s, white, [(14, 16), (7, 0), (24, 14)])   # horn
    pygame.draw.polygon(s, white, [(42, 16), (49, 0), (32, 14)])  # horn
    return s


def _make_bird(frame):
    """Draw a small flying bird (facing LEFT) with pygame primitives."""
    W, H = 46, 32
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    body  = (150, 90, 220); wing = (108, 58, 178)
    belly = (240, 240, 255); beak = (245, 160, 40); eye = (18, 18, 18)

    pygame.draw.polygon(s, wing, [(32, 15), (46, 7), (45, 22)])     # tail (right)
    pygame.draw.ellipse(s, body, (8, 11, 30, 16))                  # body
    pygame.draw.circle(s, body, (15, 15), 9)                       # head
    pygame.draw.ellipse(s, belly, (15, 17, 18, 9))                 # belly
    pygame.draw.polygon(s, beak, [(1, 15), (11, 11), (11, 19)])    # beak (left)
    pygame.draw.circle(s, eye, (13, 13), 2)                        # eye
    if frame == 0:
        pygame.draw.polygon(s, wing, [(18, 13), (27, 0), (35, 13)])   # wing up
        pygame.draw.polygon(s, body, [(20, 13), (27, 4), (32, 13)])
    else:
        pygame.draw.polygon(s, wing, [(18, 17), (27, 31), (35, 17)])  # wing down
        pygame.draw.polygon(s, body, [(20, 17), (27, 27), (32, 17)])
    return s


class SpriteSheet:
    def __init__(self):
        # ── Player ────────────────────────────────────────────────────────────
        self.player_small = {
            'idle':  _make(SMALL_MARIO_IDLE),
            'walk1': _make(SMALL_MARIO_WALK1),
            'walk2': _make(SMALL_MARIO_WALK2),
            'jump':  _make(SMALL_MARIO_JUMP),
            'duck':  _make(SMALL_MARIO_DUCK),
        }
        self.player_small_left = {
            'idle':  _make(SMALL_MARIO_IDLE,  flip_x=True),
            'walk1': _make(SMALL_MARIO_WALK1, flip_x=True),
            'walk2': _make(SMALL_MARIO_WALK2, flip_x=True),
            'jump':  _make(SMALL_MARIO_JUMP,  flip_x=True),
            'duck':  _make(SMALL_MARIO_DUCK,  flip_x=True),
        }
        self.player_big = {
            'idle':  _make(BIG_MARIO_IDLE),
            'walk1': _make(BIG_MARIO_WALK1),
            'walk2': _make(BIG_MARIO_WALK2),
            'jump':  _make(BIG_MARIO_JUMP),
            'duck':  _make(BIG_MARIO_DUCK),
        }
        self.player_big_left = {
            'idle':  _make(BIG_MARIO_IDLE,  flip_x=True),
            'walk1': _make(BIG_MARIO_WALK1, flip_x=True),
            'walk2': _make(BIG_MARIO_WALK2, flip_x=True),
            'jump':  _make(BIG_MARIO_JUMP,  flip_x=True),
            'duck':  _make(BIG_MARIO_DUCK,  flip_x=True),
        }

        # ── Blocks ────────────────────────────────────────────────────────────
        self.blocks = {
            'ground':    _make(BLOCK_GROUND),
            'brick':     _make(BLOCK_BRICK),
            'question1': _make(BLOCK_QUESTION_F1),
            'question2': _make(BLOCK_QUESTION_F2),
            'solid':     _make(BLOCK_SOLID),
            'spent':     _make(BLOCK_SOLID),   # spent block reuses solid art
            'spike':     _make(BLOCK_SPIKE),
        }

        # ── Items ─────────────────────────────────────────────────────────────
        self.items = {
            'mushroom': _make(ITEM_MUSHROOM),
            'coin1':    _make(ITEM_COIN_F1),
            'coin2':    _make(ITEM_COIN_F2),
        }

        # ── Enemies ───────────────────────────────────────────────────────────
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

        # ── Misc ──────────────────────────────────────────────────────────────
        self.flag = _make(FLAG)

        # ── Boss (procedurally drawn, faces left) ───────────────────────────────
        self.boss = {
            'walk1': _make_boss(0),
            'walk2': _make_boss(1),
        }

        # ── Bird enemy (procedurally drawn, faces left) ─────────────────────────
        self.bird = {
            'fly1':   _make_bird(0),
            'fly2':   _make_bird(1),
            'fly1_r': pygame.transform.flip(_make_bird(0), True, False),
            'fly2_r': pygame.transform.flip(_make_bird(1), True, False),
        }
