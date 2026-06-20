import pygame
from sprites import make_sprite
from char_art import build_small_frames
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


# ---------------------------------------------------------------------------
# Unique PvP boss appearances (levels 3-10). Each builder returns one 2-frame
# sprite whose silhouette and colors match the boss's name.
# ---------------------------------------------------------------------------

def _make_stalker(frame):
    """IRON STALKER - a lean, hunched steel-blue predator robot."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    steel = (120, 150, 200); dsteel = (70, 92, 140); dark = (34, 44, 66)
    visor = (90, 220, 255); edge = (180, 210, 255)

    # Hunched back / spine plates.
    pygame.draw.polygon(s, dsteel, [(30, 40), (96, 28), (104, 60), (40, 74)])
    for px in range(40, 96, 12):
        pygame.draw.polygon(s, edge, [(px, 30), (px + 8, 24), (px + 10, 34)])
    # Body core.
    pygame.draw.ellipse(s, dark, (44, 40, 52, 46))
    pygame.draw.ellipse(s, steel, (50, 46, 38, 34))
    pygame.draw.circle(s, visor, (69, 62), 7)
    # Long forward head with a slit visor.
    pygame.draw.polygon(s, dark, [(96, 36), (122, 50), (96, 60)])
    pygame.draw.line(s, visor, (100, 47), (118, 50), 3)
    # Clawed raptor legs (alternate stride).
    if frame == 0:
        legs = [(52, 84, 60, 110), (74, 84, 70, 108)]
    else:
        legs = [(52, 84, 56, 108), (74, 84, 80, 110)]
    for hx, hy, fx, fy in legs:
        pygame.draw.line(s, dsteel, (hx, hy), (fx, fy), 7)
        pygame.draw.polygon(s, steel, [(fx - 6, fy), (fx + 8, fy), (fx, fy - 6)])
    # Tail.
    pygame.draw.line(s, dsteel, (44, 60), (14, 78), 6)
    pygame.draw.circle(s, visor, (14, 78), 4)
    return s


def _make_blaze(frame):
    """BLAZE TYRANT - a horned fire demon wreathed in flame."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    body = (180, 40, 30); dbody = (120, 22, 18); flame = (255, 150, 30)
    flame2 = (255, 215, 90); eye = (255, 240, 120)

    # Flame aura behind the body (animated).
    tips = [(20, 64), (40, 40), (61, 24), (82, 40), (102, 64)]
    off = 0 if frame == 0 else 8
    for i, (fx, fy) in enumerate(tips):
        h = 30 + (off if i % 2 == 0 else -off)
        pygame.draw.polygon(s, flame, [(fx - 12, 78), (fx, fy - h), (fx + 12, 78)])
        pygame.draw.polygon(s, flame2, [(fx - 6, 78), (fx, fy - h + 14), (fx + 6, 78)])
    # Demon body.
    pygame.draw.ellipse(s, dbody, (40, 52, 44, 54))
    pygame.draw.ellipse(s, body, (46, 58, 32, 42))
    # Head.
    pygame.draw.circle(s, body, (61, 50), 22)
    pygame.draw.circle(s, dbody, (61, 50), 22, 3)
    # Horns.
    pygame.draw.polygon(s, dbody, [(44, 38), (34, 14), (52, 32)])
    pygame.draw.polygon(s, dbody, [(78, 38), (88, 14), (70, 32)])
    # Burning eyes + grin.
    pygame.draw.circle(s, eye, (53, 48), 4)
    pygame.draw.circle(s, eye, (69, 48), 4)
    pygame.draw.arc(s, eye, (50, 52, 22, 14), 3.3, 6.1, 3)
    # Clawed feet.
    pygame.draw.polygon(s, dbody, [(44, 104), (54, 104), (49, 112)])
    pygame.draw.polygon(s, dbody, [(70, 104), (80, 104), (75, 112)])
    return s


def _make_storm(frame):
    """STORM SENTINEL - a hovering armored eye crackling with lightning."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    armor = (60, 130, 170); darmor = (34, 78, 110); ring = (120, 220, 255)
    bolt = (180, 245, 255); iris = (20, 40, 70)

    # Lightning arcs around the sentinel.
    pts1 = [(16, 30), (34, 44), (24, 56), (40, 70)]
    pts2 = [(106, 30), (88, 44), (98, 56), (82, 70)]
    arcs = pts1 + pts2
    if frame == 1:
        arcs = [(x, y + 4) for (x, y) in arcs]
    pygame.draw.lines(s, bolt, False, pts1, 3)
    pygame.draw.lines(s, bolt, False, pts2, 3)
    # Outer hovering ring.
    pygame.draw.ellipse(s, darmor, (28, 32, 66, 66))
    pygame.draw.ellipse(s, armor, (34, 38, 54, 54))
    pygame.draw.ellipse(s, ring, (34, 38, 54, 54), 3)
    # Central eye.
    pygame.draw.circle(s, (235, 245, 255), (61, 65), 17)
    pygame.draw.circle(s, iris, (61, 65), 9)
    pygame.draw.circle(s, ring, (61, 65), 9, 2)
    pygame.draw.circle(s, (235, 245, 255), (58, 61), 3)
    # Floating armor fins.
    pygame.draw.polygon(s, armor, [(34, 96), (50, 92), (44, 108)])
    pygame.draw.polygon(s, armor, [(88, 96), (72, 92), (78, 108)])
    return s


def _make_meteor(frame):
    """METEOR KING - a craggy rock golem crowned in gold."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    rock = (110, 96, 130); drock = (74, 62, 92); magma = (255, 120, 40)
    gold = (255, 210, 80); eye = (255, 180, 60)

    # Boulder body.
    pygame.draw.polygon(s, drock, [(34, 60), (52, 40), (88, 44), (100, 70),
                                   (84, 104), (44, 104)])
    pygame.draw.polygon(s, rock, [(42, 60), (56, 48), (84, 50), (92, 70),
                                  (80, 98), (50, 98)])
    # Glowing magma cracks.
    pygame.draw.lines(s, magma, False, [(56, 64), (66, 74), (60, 84), (72, 92)], 3)
    pygame.draw.line(s, magma, (74, 60), (82, 70), 3)
    # Eyes.
    pygame.draw.circle(s, eye, (58, 66), 4)
    pygame.draw.circle(s, eye, (78, 66), 4)
    # Gold crown.
    cy = 40 if frame == 0 else 38
    pygame.draw.rect(s, gold, (50, cy, 40, 8))
    for cx in (50, 62, 74, 86):
        pygame.draw.polygon(s, gold, [(cx, cy), (cx + 4, cy - 12), (cx + 8, cy)])
    # Rocky fists (alternate).
    if frame == 0:
        pygame.draw.circle(s, rock, (34, 92), 12); pygame.draw.circle(s, rock, (96, 84), 12)
    else:
        pygame.draw.circle(s, rock, (34, 84), 12); pygame.draw.circle(s, rock, (96, 92), 12)
    return s


def _make_phantom(frame):
    """PHANTOM RAILGUN - a hooded spectral wraith hoisting a railgun."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    ghost = (90, 230, 170); dghost = (40, 150, 120); robe = (24, 70, 60)
    eye = (220, 255, 240); metal = (80, 100, 110); core = (150, 255, 210)

    # Wispy lower body (tattered, animated).
    sway = 0 if frame == 0 else 6
    pygame.draw.polygon(s, robe, [(40, 60), (84, 60), (92, 104),
                                  (72 + sway, 92), (61, 106), (50 - sway, 92), (32, 104)])
    pygame.draw.polygon(s, dghost, [(44, 58), (80, 58), (84, 92), (40, 92)])
    # Hood + head.
    pygame.draw.polygon(s, dghost, [(44, 44), (61, 24), (78, 44), (74, 58), (48, 58)])
    pygame.draw.circle(s, ghost, (61, 46), 12)
    pygame.draw.circle(s, eye, (56, 46), 3)
    pygame.draw.circle(s, eye, (66, 46), 3)
    # Railgun across the body.
    pygame.draw.rect(s, metal, (70, 58, 46, 12), border_radius=3)
    pygame.draw.rect(s, (50, 64, 72), (70, 58, 46, 12), 2, border_radius=3)
    pygame.draw.circle(s, core, (114, 64), 6)
    pygame.draw.rect(s, metal, (60, 62, 16, 18), border_radius=3)
    return s


def _make_titan(frame):
    """TITAN CRUSHER - a colossal stone titan with massive fists."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    stone = (200, 160, 90); dstone = (150, 112, 56); dark = (96, 70, 36)
    glow = (255, 230, 120); eye = (255, 245, 200)

    # Huge torso.
    pygame.draw.rect(s, dark, (38, 40, 46, 56), border_radius=8)
    pygame.draw.rect(s, stone, (42, 44, 38, 46), border_radius=6)
    # Glowing seams.
    pygame.draw.line(s, glow, (61, 46), (61, 88), 2)
    pygame.draw.line(s, glow, (50, 60), (72, 60), 2)
    # Blocky head.
    pygame.draw.rect(s, dstone, (48, 22, 26, 22), border_radius=4)
    pygame.draw.rect(s, eye, (52, 30, 7, 5))
    pygame.draw.rect(s, eye, (63, 30, 7, 5))
    # Massive fists (alternate raise).
    if frame == 0:
        f1, f2 = (18, 64), (104, 50)
    else:
        f1, f2 = (18, 50), (104, 64)
    for fx, fy in (f1, f2):
        pygame.draw.rect(s, dstone, (fx - 12, fy, 24, 26), border_radius=6)
        pygame.draw.rect(s, stone, (fx - 8, fy + 4, 16, 16), border_radius=4)
    # Stubby legs.
    pygame.draw.rect(s, dark, (44, 94, 14, 18), border_radius=3)
    pygame.draw.rect(s, dark, (64, 94, 14, 18), border_radius=3)
    return s


def _make_warden(frame):
    """OMEGA WARDEN - a magenta armored knight with a great shield."""
    W, H = 122, 114
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    armor = (190, 70, 180); darmor = (130, 40, 124); trim = (255, 180, 240)
    metal = (120, 120, 140); glow = (255, 120, 230); eye = (255, 230, 255)

    # Cape behind.
    pygame.draw.polygon(s, darmor, [(40, 44), (82, 44), (90, 104), (32, 104)])
    # Body armor.
    pygame.draw.rect(s, armor, (44, 46, 36, 50), border_radius=8)
    pygame.draw.rect(s, trim, (44, 46, 36, 50), 2, border_radius=8)
    # Omega emblem on chest.
    pygame.draw.arc(s, glow, (52, 56, 20, 22), 0.6, 5.7, 3)
    pygame.draw.line(s, glow, (54, 78), (50, 82), 3)
    pygame.draw.line(s, glow, (70, 78), (74, 82), 3)
    # Helm with plume.
    pygame.draw.rect(s, metal, (48, 22, 28, 24), border_radius=6)
    pygame.draw.rect(s, eye, (52, 32, 20, 5))
    pygame.draw.polygon(s, glow, [(60, 22), (64, 8), (68, 22)])
    # Great shield (raised/lowered by frame).
    sy = 50 if frame == 0 else 56
    pygame.draw.polygon(s, metal, [(86, sy), (110, sy + 4), (108, sy + 34),
                                   (98, sy + 46), (88, sy + 34)])
    pygame.draw.polygon(s, trim, [(86, sy), (110, sy + 4), (108, sy + 34),
                                  (98, sy + 46), (88, sy + 34)], 2)
    return s


def _make_overlord(frame):
    """JIN OVERLORD - the final boss: a dark, caped demon-king."""
    W, H = 124, 116
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    black = (28, 24, 38); dark = (52, 44, 70); red = (220, 40, 50)
    glow = (255, 70, 70); gold = (255, 205, 90); eye = (255, 90, 80)

    # Spread cape / wings (animated flare).
    flare = 0 if frame == 0 else 10
    pygame.draw.polygon(s, dark, [(60, 40), (12 - flare, 28), (6, 70),
                                  (40, 70), (44, 96), (60, 80)])
    pygame.draw.polygon(s, dark, [(64, 40), (112 + flare, 28), (118, 70),
                                  (84, 70), (80, 96), (64, 80)])
    pygame.draw.polygon(s, black, [(60, 40), (24, 32), (40, 66), (62, 78)])
    pygame.draw.polygon(s, black, [(64, 40), (100, 32), (84, 66), (62, 78)])
    # Armored body.
    pygame.draw.polygon(s, black, [(46, 48), (78, 48), (86, 102), (38, 102)])
    pygame.draw.rect(s, red, (56, 60, 12, 30), border_radius=3)
    pygame.draw.circle(s, glow, (62, 66), 6)
    # Head with great horns + crown.
    pygame.draw.circle(s, dark, (62, 40), 18)
    pygame.draw.polygon(s, black, [(46, 34), (28, 8), (52, 28)])
    pygame.draw.polygon(s, black, [(78, 34), (96, 8), (72, 28)])
    for cx in (50, 62, 74):
        pygame.draw.polygon(s, gold, [(cx - 4, 24), (cx, 12), (cx + 4, 24)])
    # Blazing eyes.
    pygame.draw.circle(s, eye, (55, 40), 4)
    pygame.draw.circle(s, eye, (69, 40), 4)
    pygame.draw.line(s, glow, (50, 33), (60, 38), 2)
    pygame.draw.line(s, glow, (74, 33), (64, 38), 2)
    # Feet.
    pygame.draw.polygon(s, black, [(42, 102), (54, 102), (48, 114)])
    pygame.draw.polygon(s, black, [(70, 102), (82, 102), (76, 114)])
    return s


class SpriteSheet:
    def __init__(self):
        self.apply_character('jin', None)

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

        # Unique appearances for PvP bosses 3-10, keyed by a short name that
        # matches each boss's identity.
        self.boss_variants = {
            'stalker':  {'walk1': _make_stalker(0),  'walk2': _make_stalker(1)},
            'blaze':    {'walk1': _make_blaze(0),    'walk2': _make_blaze(1)},
            'storm':    {'walk1': _make_storm(0),    'walk2': _make_storm(1)},
            'meteor':   {'walk1': _make_meteor(0),   'walk2': _make_meteor(1)},
            'phantom':  {'walk1': _make_phantom(0),  'walk2': _make_phantom(1)},
            'titan':    {'walk1': _make_titan(0),    'walk2': _make_titan(1)},
            'warden':   {'walk1': _make_warden(0),   'walk2': _make_warden(1)},
            'overlord': {'walk1': _make_overlord(0), 'walk2': _make_overlord(1)},
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

    def boss_set(self, key):
        """Resolve a boss sprite key to its 2-frame walk dict."""
        if key == 'city':
            return self.boss_city
        if key in self.boss_variants:
            return self.boss_variants[key]
        return self.boss

    def apply_character(self, char_id=None, palette=None):
        """Rebuild the player sprite sets for the equipped character + skin.

        Each character has its own procedurally drawn silhouette (see
        char_art); palette supplies the recolorable identity ('r'), suit
        ('b'), skin ('s') and accent ('k') colors. The big form is the small
        art scaled up, and the left-facing sets are horizontal flips.
        """
        char_id = char_id or 'jin'
        pal = palette or {}
        prim = pal.get('r', (220, 30, 30))
        suit = pal.get('b', (30, 80, 200))
        skin = pal.get('s', (255, 200, 150))
        hair = pal.get('k', (60, 45, 25))

        small = build_small_frames(char_id, prim, suit, skin, hair)
        self.player_small = small
        self.player_small_left = {
            k: pygame.transform.flip(v, True, False) for k, v in small.items()
        }
        big = {k: pygame.transform.scale(v, (40, 80)) for k, v in small.items()}
        self.player_big = big
        self.player_big_left = {
            k: pygame.transform.flip(v, True, False) for k, v in big.items()
        }

    def make_preview(self, char_id, palette, scale=3):
        """A single idle sprite for shop thumbnails, sized to `scale`."""
        pal = palette or {}
        idle = build_small_frames(
            char_id,
            pal.get('r', (220, 30, 30)),
            pal.get('b', (30, 80, 200)),
            pal.get('s', (255, 200, 150)),
            pal.get('k', (60, 45, 25)),
        )['idle']
        factor = scale / 2.5
        return pygame.transform.scale(
            idle, (int(idle.get_width() * factor), int(idle.get_height() * factor)))
