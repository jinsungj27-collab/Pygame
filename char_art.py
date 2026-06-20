"""Procedural player-character art.

Every playable character used to be the same Mario pixel grid with swapped
colors. This module instead draws ten visually distinct characters (knight,
robot, diver, flame, ninja, golem, plant, yeti, cobra, astronaut) using vector
primitives, so each one has its own silhouette - not just a recolor.

Each draw function paints one frame onto a 30x40 surface (matching the small
player sprite size the rest of the game expects), with the feet resting on the
bottom edge. Colors come from the equipped character + skin:
    prim  - the character's primary identity color (palette 'r')
    suit  - the secondary / skin-swappable color (palette 'b')
    skin  - face / skin tone (palette 's')
    hair  - dark accent / hair (palette 'k')

build_small_frames() returns the idle / walk / jump / duck frames; the big
form and left-facing variants are derived by the SpriteSheet (scale + flip).
"""

import math
import pygame

SMALL_W, SMALL_H = 30, 40
FOOT = 40
EYE = (22, 20, 30)
WHITE = (255, 255, 255)


def _surf():
    return pygame.Surface((SMALL_W, SMALL_H), pygame.SRCALPHA)


def _biped_legs(s, col, pose, step, footy=FOOT, w=4):
    """Shared leg animation for humanoid characters."""
    if pose == 'jump':
        pygame.draw.rect(s, col, (9, footy - 7, w, 7))
        pygame.draw.rect(s, col, (17, footy - 7, w, 7))
    elif pose == 'walk':
        a, b = (9, 6) if step == 0 else (6, 9)
        pygame.draw.rect(s, col, (8, footy - a, w, a))
        pygame.draw.rect(s, col, (18, footy - b, w, b))
    else:  # idle
        pygame.draw.rect(s, col, (9, footy - 9, w, 9))
        pygame.draw.rect(s, col, (17, footy - 9, w, 9))


def _eyes(s, lx, rx, y, color=EYE, r=1):
    pygame.draw.circle(s, color, (lx, y), r)
    pygame.draw.circle(s, color, (rx, y), r)


# --- 1. Jin : armored KNIGHT -------------------------------------------
def d_knight(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, prim, pose, step)
    pygame.draw.rect(s, suit, (8, 18, 14, 13))          # torso armor
    pygame.draw.rect(s, prim, (14, 18, 2, 13))          # center trim
    pygame.draw.rect(s, prim, (6, 18, 3, 5))            # shoulders
    pygame.draw.rect(s, prim, (21, 18, 3, 5))
    pygame.draw.ellipse(s, prim, (8, 4, 14, 14))        # helmet
    pygame.draw.rect(s, EYE, (9, 10, 12, 4))            # visor slit
    pygame.draw.rect(s, (120, 220, 255), (11, 11, 4, 2))
    pygame.draw.rect(s, (255, 210, 60), (14, 0, 3, 6))  # plume


# --- 2. Luca : boxy ROBOT ----------------------------------------------
def d_robot(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, suit, pose, step)
    pygame.draw.rect(s, prim, (8, 17, 14, 14), border_radius=2)
    pygame.draw.rect(s, suit, (5, 18, 3, 8))            # arms
    pygame.draw.rect(s, suit, (22, 18, 3, 8))
    pygame.draw.circle(s, (255, 90, 90), (15, 24), 2)   # chest light
    pygame.draw.rect(s, prim, (9, 4, 12, 12), border_radius=2)  # head
    pygame.draw.rect(s, (22, 26, 34), (10, 7, 10, 5))   # visor
    pygame.draw.rect(s, (120, 230, 255), (11, 8, 8, 2))
    pygame.draw.line(s, suit, (15, 4), (15, 0), 1)      # antenna
    pygame.draw.circle(s, (255, 90, 90), (15, 0), 1)


# --- 3. Aqua : bubble-helmet DIVER -------------------------------------
def d_diver(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, suit, pose, step)
    pygame.draw.rect(s, prim, (9, 18, 12, 13))          # wetsuit
    pygame.draw.rect(s, suit, (9, 22, 12, 2))           # belt
    pygame.draw.polygon(s, suit, [(6, 21), (9, 19), (9, 27)])   # fins
    pygame.draw.polygon(s, suit, [(24, 21), (21, 19), (21, 27)])
    pygame.draw.circle(s, skin, (15, 11), 5)            # face
    _eyes(s, 13, 17, 11)
    pygame.draw.circle(s, (180, 235, 255), (15, 11), 8, 2)  # glass dome
    pygame.draw.circle(s, WHITE, (12, 8), 1)            # glint


# --- 4. Blaze : FLAME elemental (no legs) ------------------------------
def d_flame(s, pose, step, prim, suit, skin, hair):
    h = 0 if step == 0 else 2
    if pose == 'jump':
        h = 4
    pygame.draw.polygon(s, prim, [(6, 40), (10, 22 - h), (13, 31),
                                  (15, 13 - h), (17, 31), (20, 22 - h), (24, 40)])
    pygame.draw.polygon(s, suit, [(10, 40), (13, 27), (15, 19 - h // 2),
                                  (17, 27), (20, 40)])
    pygame.draw.polygon(s, (255, 240, 150), [(13, 40), (15, 29), (17, 40)])
    _eyes(s, 13, 18, 26, WHITE, r=1)


# --- 5. Shadow : NINJA --------------------------------------------------
def d_ninja(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, hair, pose, step)
    pygame.draw.rect(s, prim, (9, 17, 12, 14))          # body
    pygame.draw.polygon(s, suit, [(9, 19), (2, 22), (4, 27), (9, 24)])  # scarf
    pygame.draw.rect(s, suit, (9, 26, 12, 2))           # belt
    pygame.draw.ellipse(s, prim, (9, 4, 12, 13))        # head wrap
    pygame.draw.rect(s, EYE, (9, 9, 12, 4))             # eye band
    pygame.draw.rect(s, WHITE, (11, 10, 3, 2))
    pygame.draw.rect(s, WHITE, (16, 10, 3, 2))


# --- 6. Goldie : crowned GOLEM -----------------------------------------
def d_golem(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, prim, pose, step)
    pygame.draw.rect(s, prim, (7, 17, 16, 14))          # blocky body
    pygame.draw.rect(s, (60, 45, 20), (7, 17, 16, 14), 1)
    pygame.draw.polygon(s, suit, [(15, 21), (12, 24), (15, 28), (18, 24)])  # gem
    pygame.draw.rect(s, prim, (10, 6, 10, 11))          # head
    _eyes(s, 12, 18, 11, (60, 45, 20))
    pygame.draw.rect(s, (255, 210, 60), (9, 4, 12, 3))  # crown band
    for cx in (9, 13, 17):
        pygame.draw.polygon(s, (255, 210, 60), [(cx, 4), (cx + 2, 0), (cx + 4, 4)])


# --- 7. Rose : flower PLANT --------------------------------------------
def d_plant(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, suit, pose, step)
    pygame.draw.rect(s, suit, (13, 18, 4, 13))          # stem
    pygame.draw.polygon(s, suit, [(13, 22), (6, 19), (8, 26)])   # leaf arms
    pygame.draw.polygon(s, suit, [(17, 22), (24, 19), (22, 26)])
    for ang in range(0, 360, 60):                       # petals
        px = 15 + int(6 * math.cos(math.radians(ang)))
        py = 10 + int(6 * math.sin(math.radians(ang)))
        pygame.draw.circle(s, prim, (px, py), 4)
    pygame.draw.circle(s, (255, 235, 120), (15, 10), 4)  # face center
    _eyes(s, 13, 17, 10)


# --- 8. Frost : horned YETI --------------------------------------------
def d_yeti(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, prim, pose, step)
    pygame.draw.ellipse(s, prim, (5, 14, 20, 18))       # furry body
    pygame.draw.ellipse(s, (240, 248, 255), (11, 19, 8, 10))  # belly
    pygame.draw.ellipse(s, prim, (2, 16, 6, 11))        # arms
    pygame.draw.ellipse(s, prim, (22, 16, 6, 11))
    pygame.draw.ellipse(s, prim, (9, 3, 12, 12))        # head
    pygame.draw.polygon(s, (240, 248, 255), [(9, 6), (5, 1), (11, 5)])  # horns
    pygame.draw.polygon(s, (240, 248, 255), [(21, 6), (25, 1), (19, 5)])
    _eyes(s, 13, 17, 9)


# --- 9. Viper : hooded COBRA -------------------------------------------
def d_cobra(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, suit, pose, step)
    pygame.draw.rect(s, prim, (11, 18, 8, 13))          # body
    pygame.draw.polygon(s, prim, [(15, 6), (3, 14), (8, 19),
                                  (15, 16), (22, 19), (27, 14)])  # hood
    pygame.draw.ellipse(s, suit, (7, 12, 4, 4))         # hood markings
    pygame.draw.ellipse(s, suit, (19, 12, 4, 4))
    pygame.draw.ellipse(s, prim, (11, 7, 8, 9))         # head
    _eyes(s, 13, 17, 11, (255, 220, 60))
    pygame.draw.line(s, WHITE, (14, 15), (14, 17), 1)   # fangs
    pygame.draw.line(s, WHITE, (16, 15), (16, 17), 1)


# --- 10. Nova : ASTRONAUT / alien --------------------------------------
def d_alien(s, pose, step, prim, suit, skin, hair):
    _biped_legs(s, prim, pose, step)
    pygame.draw.rect(s, prim, (9, 18, 12, 13))          # spacesuit
    pygame.draw.rect(s, prim, (6, 19, 3, 7))            # arms / pack
    pygame.draw.rect(s, prim, (21, 19, 3, 7))
    pygame.draw.circle(s, suit, (15, 24), 2)            # chest control
    pygame.draw.circle(s, (60, 70, 92), (15, 10), 7)    # helmet shell
    pygame.draw.circle(s, (120, 220, 200), (15, 10), 6)  # glass
    pygame.draw.circle(s, (140, 220, 150), (15, 11), 3)  # alien head
    _eyes(s, 14, 17, 11)
    pygame.draw.circle(s, WHITE, (12, 7), 2)            # glint
    pygame.draw.line(s, (200, 200, 210), (15, 4), (15, 1), 1)  # antenna
    pygame.draw.circle(s, (255, 225, 80), (15, 0), 1)


CHAR_DRAW = {
    'jin': d_knight,
    'luca': d_robot,
    'aqua': d_diver,
    'blaze': d_flame,
    'shadow': d_ninja,
    'goldie': d_golem,
    'rose': d_plant,
    'frost': d_yeti,
    'viper': d_cobra,
    'nova': d_alien,
}


def build_small_frames(char_id, prim, suit, skin, hair):
    """Return the 6 small (30x40) animation frames for one character."""
    draw = CHAR_DRAW.get(char_id, d_knight)

    def mk(pose, step):
        s = _surf()
        draw(s, pose, step, prim, suit, skin, hair)
        return s

    idle = mk('idle', 0)
    # Ducking: squash the idle pose into the lower part of the frame so the
    # crouch lines up with the shortened collision box.
    duck = _surf()
    duck.blit(pygame.transform.scale(idle, (SMALL_W, 24)), (0, 16))

    return {
        'idle':  idle,
        'walk1': mk('walk', 0),
        'walk2': mk('walk', 1),
        'walk3': mk('walk', 0),
        'jump':  mk('jump', 0),
        'duck':  duck,
    }
