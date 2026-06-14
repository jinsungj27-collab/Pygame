"""
Procedural, difficulty-scaling level builder.

build_level(level_num, sprites) returns a LevelData object holding fully
populated sprite groups plus level metadata. Difficulty rises with level_num:
more (and faster) enemies, more gaps, and spike hazards from level 2 onward.

Geometry bounds (level width, flag, castle) are kept consistent across levels
so the flag-slide / victory-walk logic in Game stays simple and robust, while
the *interior* obstacles change and intensify each level.
"""
import random

from constants import TILE_SIZE, SCREEN_WIDTH
from entities import Enemy, Tile, Boss

# Themes cycle as the player advances. Each theme drives the background palette
# and the background-music track index.
THEMES = [
    {   # 0 Overworld (day)
        'name': 'Overworld',
        'sky_top': (107, 140, 255), 'sky_bottom': (175, 205, 255),
        'hill': (80, 190, 110), 'hill_shadow': (60, 160, 90),
        'cloud': (255, 255, 255), 'mountain': (120, 140, 200),
        'sun': (255, 245, 200), 'night': False,
    },
    {   # 1 Sunset
        'name': 'Sunset',
        'sky_top': (255, 140, 90), 'sky_bottom': (255, 210, 150),
        'hill': (150, 120, 90), 'hill_shadow': (120, 90, 70),
        'cloud': (255, 220, 200), 'mountain': (170, 110, 120),
        'sun': (255, 230, 120), 'night': False,
    },
    {   # 2 Night
        'name': 'Night',
        'sky_top': (15, 18, 55), 'sky_bottom': (50, 45, 100),
        'hill': (40, 70, 60), 'hill_shadow': (25, 50, 45),
        'cloud': (120, 130, 170), 'mountain': (45, 50, 90),
        'sun': (235, 235, 220), 'night': True,
    },
    {   # 3 Cave / dusk
        'name': 'Cavern',
        'sky_top': (35, 25, 45), 'sky_bottom': (70, 55, 80),
        'hill': (70, 55, 80), 'hill_shadow': (50, 40, 60),
        'cloud': (110, 95, 120), 'mountain': (55, 45, 70),
        'sun': (200, 180, 210), 'night': True,
    },
]


class LevelData:
    def __init__(self):
        self.tile_group   = None
        self.hazard_group = None
        self.enemy_group  = None
        self.level_width  = 3800
        self.flagpole_x   = 3400
        self.flagpole_y   = TILE_SIZE * 3
        self.castle_x     = 3550
        self.theme_index  = 0
        self.world_name   = "1-1"
        self.start_timer  = 400
        self.is_boss      = False
        self.boss         = None


def _create_pipe(col, row, layout):
    layout[(col,     row)] = 'pipe_tl'
    layout[(col + 1, row)] = 'pipe_tr'
    for r in range(row + 1, 13):
        layout[(col,     r)] = 'pipe_l'
        layout[(col + 1, r)] = 'pipe_r'


def _create_staircase(start_col, floor_row, size, ascends_right, layout):
    for step in range(size):
        height = (step + 1) if ascends_right else (size - step)
        col    = start_col + step
        for h in range(height):
            layout[(col, floor_row - h)] = 'S'


def build_level(level_num, sprites):
    """Construct and return a fully-populated LevelData for the given level."""
    import pygame

    rng = random.Random(level_num * 7919 + 13)
    data = LevelData()
    data.theme_index = (level_num - 1) % len(THEMES)
    data.world_name  = f"{((level_num - 1) // 4) + 1}-{((level_num - 1) % 4) + 1}"

    # Difficulty knobs ------------------------------------------------------
    diff = level_num - 1
    enemy_speed_mult = 1.0 + 0.12 * diff
    num_enemies      = min(6 + 2 * diff, 22)
    num_gaps         = min(diff, 5)            # gaps start at level 2
    gap_width        = 2 if level_num < 3 else 3
    num_spike_sets   = min(max(diff - 1, 0), 5)  # spikes start at level 3
    data.start_timer = max(250, 400 - 20 * diff)

    tile_group   = pygame.sprite.Group()
    hazard_group = pygame.sprite.Group()
    enemy_group  = pygame.sprite.Group()

    COLS = 95   # 95 * 40 = 3800
    SAFE_START = 11      # columns of guaranteed ground after spawn
    SAFE_END   = 86      # ground guaranteed up to flag foundation

    # ── Decide gap positions (each gap = contiguous missing-ground columns) ──
    gap_cols = set()
    forbidden = set(range(0, SAFE_START)) | set(range(SAFE_END, COLS))
    attempts = 0
    placed_gaps = []
    while len(placed_gaps) < num_gaps and attempts < 60:
        attempts += 1
        start = rng.randint(SAFE_START + 2, SAFE_END - gap_width - 4)
        span = set(range(start - 1, start + gap_width + 1))  # buffer around gap
        if span & forbidden or span & gap_cols:
            continue
        for c in range(start, start + gap_width):
            gap_cols.add(c)
        # keep a margin so gaps don't touch each other
        forbidden |= set(range(start - 3, start + gap_width + 3))
        placed_gaps.append((start, gap_width))

    layout = {}

    # ── Ground rows (skip gap columns) ──────────────────────────────────────
    for col in range(COLS):
        if col in gap_cols:
            continue
        layout[(col, 13)] = 'G'
        layout[(col, 14)] = 'G'

    # ── Flag approach: keep cols 84..94 flat ground so the victory walk into
    #    the castle is never blocked. (No raised foundation wall here.)
    # (ground already laid above; nothing extra needed)

    # ── Floating block clusters (coins / power-ups) ─────────────────────────
    block_rows = [
        (8, 9, 'B'), (9, 9, 'Q'), (10, 9, 'B'),
        (11, 9, 'M'), (12, 9, 'B'), (10, 5, 'Q'),
        (20, 9, 'Q'),
        (39, 9, 'B'), (40, 9, 'Q'), (41, 9, 'B'), (42, 9, 'B'),
        (60, 9, 'B'), (61, 9, 'Q'), (62, 9, 'Q'), (63, 9, 'B'),
    ]
    for col, row, kind in block_rows:
        if col in gap_cols:
            continue
        layout[(col, row)] = kind

    for col in range(67, 72):
        if col not in gap_cols:
            layout[(col, 5)] = 'B'

    # ── Pipes (count scales a little with level) ────────────────────────────
    pipe_candidates = [(18, 11), (25, 10), (34, 11), (48, 11), (70, 10)]
    num_pipes = min(3 + diff, len(pipe_candidates))
    for (pc, pr) in pipe_candidates[:num_pipes]:
        if pc in gap_cols or (pc + 1) in gap_cols:
            continue
        _create_pipe(pc, pr, layout)

    # ── Staircases (kept clear of the flag at col ~85) ──────────────────────
    _create_staircase(46, 12, size=4, ascends_right=True, layout=layout)
    _create_staircase(78, 12, size=min(4 + diff, 6), ascends_right=True, layout=layout)

    # ── Spike hazards on safe ground ────────────────────────────────────────
    spike_cols = set()
    sp_attempts = 0
    while len(spike_cols) < num_spike_sets and sp_attempts < 50:
        sp_attempts += 1
        c = rng.randint(SAFE_START + 4, SAFE_END - 4)
        # spikes must sit on solid ground (col 13 present) and clear of blocks
        if c in gap_cols or (c, 13) not in layout or (c, 12) in layout:
            continue
        if any(abs(c - s) < 4 for s in spike_cols):
            continue
        spike_cols.add(c)

    # ── Instantiate solid tiles ─────────────────────────────────────────────
    tile_map = {
        'G': ('ground',   None),
        'B': ('brick',    None),
        'S': ('solid',    None),
        'Q': ('question', 'coin'),
        'M': ('question', 'mushroom'),
    }
    for (col, row), kind in layout.items():
        x, y = col * TILE_SIZE, row * TILE_SIZE
        if kind in tile_map:
            tile_type, item = tile_map[kind]
            tile_group.add(Tile(x, y, tile_type, sprites, contains_item=item))
        elif kind.startswith('pipe_'):
            tile_group.add(Tile(x, y, kind, sprites))

    # ── Instantiate spike hazards (sit on row 12, atop ground row 13) ───────
    for c in spike_cols:
        hazard_group.add(Tile(c * TILE_SIZE, 12 * TILE_SIZE, 'spike', sprites))

    # ── Enemies ─────────────────────────────────────────────────────────────
    walkable = [c for c in range(SAFE_START + 3, SAFE_END - 2)
                if c not in gap_cols and c not in spike_cols]
    rng.shuffle(walkable)
    koopa_chance = min(0.25 + 0.06 * diff, 0.6)
    used = []
    for c in walkable:
        if len(used) >= num_enemies:
            break
        if any(abs(c - u) < 2 for u in used):
            continue
        used.append(c)
        etype = 'koopa' if rng.random() < koopa_chance else 'goomba'
        sx = c * TILE_SIZE
        sy = 480 if etype == 'goomba' else 440
        e = Enemy(sx, sy, etype, sprites)
        # scale base patrol speed by difficulty (preserve direction)
        e.vx = -1.2 * enemy_speed_mult
        e.shell_speed = 8.0 * enemy_speed_mult
        enemy_group.add(e)

    data.tile_group   = tile_group
    data.hazard_group = hazard_group
    data.enemy_group  = enemy_group
    return data


def is_boss_level(level_num):
    """Every 4th level (4, 8, 12, ...) is a boss battle."""
    return level_num % 4 == 0


def build_boss_level(level_num, sprites):
    """Build an enclosed single-screen arena with a boss to defeat."""
    import pygame

    data = LevelData()
    data.is_boss = True
    data.theme_index = (level_num - 1) % len(THEMES)
    data.world_name = f"{((level_num - 1) // 4) + 1}-BOSS"
    data.level_width = SCREEN_WIDTH          # 800 -> no horizontal scroll
    data.flagpole_x = 10 ** 9                # flag disabled; clear by defeating boss
    data.castle_x = 10 ** 9
    boss_round = level_num // 4              # 1, 2, 3, ...
    data.start_timer = max(180, 320 - 20 * boss_round)

    tile_group   = pygame.sprite.Group()
    hazard_group = pygame.sprite.Group()
    enemy_group  = pygame.sprite.Group()

    COLS = 20   # 20 * 40 = 800

    # Floor
    for col in range(COLS):
        tile_group.add(Tile(col * TILE_SIZE, 13 * TILE_SIZE, 'ground', sprites))
        tile_group.add(Tile(col * TILE_SIZE, 14 * TILE_SIZE, 'ground', sprites))

    # Side walls so nobody leaves the arena
    for r in range(6, 13):
        tile_group.add(Tile(0,             r * TILE_SIZE, 'solid', sprites))
        tile_group.add(Tile(19 * TILE_SIZE, r * TILE_SIZE, 'solid', sprites))

    # Two side platforms for tactical jumps
    for col in (4, 5):
        tile_group.add(Tile(col * TILE_SIZE, 9 * TILE_SIZE, 'solid', sprites))
    for col in (14, 15):
        tile_group.add(Tile(col * TILE_SIZE, 9 * TILE_SIZE, 'solid', sprites))

    # Boss — HP and speed scale each boss round
    hp    = 4 + (boss_round - 1)
    speed = 1.6 + 0.25 * (boss_round - 1)
    boss = Boss(560, 13 * TILE_SIZE, sprites, hp=hp, speed=speed)
    boss.set_bounds(TILE_SIZE + 20, 19 * TILE_SIZE - 20)
    data.boss = boss

    data.tile_group   = tile_group
    data.hazard_group = hazard_group
    data.enemy_group  = enemy_group
    return data
