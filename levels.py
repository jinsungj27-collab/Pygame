import random

from constants import TILE_SIZE, SCREEN_WIDTH
from entities import Enemy, Tile, Boss, Coin

THEMES = [
    {
        'name': 'Overworld',
        'sky_top': (107, 140, 255), 'sky_bottom': (175, 205, 255),
        'hill': (80, 190, 110), 'hill_shadow': (60, 160, 90),
        'cloud': (255, 255, 255), 'mountain': (120, 140, 200),
        'sun': (255, 245, 200), 'night': False,
    },
    {
        'name': 'Sunset',
        'sky_top': (255, 140, 90), 'sky_bottom': (255, 210, 150),
        'hill': (150, 120, 90), 'hill_shadow': (120, 90, 70),
        'cloud': (255, 220, 200), 'mountain': (170, 110, 120),
        'sun': (255, 230, 120), 'night': False,
    },
    {
        'name': 'Night',
        'sky_top': (15, 18, 55), 'sky_bottom': (50, 45, 100),
        'hill': (40, 70, 60), 'hill_shadow': (25, 50, 45),
        'cloud': (120, 130, 170), 'mountain': (45, 50, 90),
        'sun': (235, 235, 220), 'night': True,
    },
    {
        'name': 'Cavern',
        'sky_top': (35, 25, 45), 'sky_bottom': (70, 55, 80),
        'hill': (70, 55, 80), 'hill_shadow': (50, 40, 60),
        'cloud': (110, 95, 120), 'mountain': (55, 45, 70),
        'sun': (200, 180, 210), 'night': True,
    },
    {
        'name': 'City',
        'sky_top': (34, 40, 92), 'sky_bottom': (168, 122, 138),
        'hill': (70, 80, 120), 'hill_shadow': (50, 58, 95),
        'cloud': (188, 176, 198), 'mountain': (60, 70, 110),
        'sun': (255, 198, 128), 'night': False,
        'city': True,
    },
]

# Index of the City theme in THEMES (used for all levels after the first boss).
CITY_THEME_INDEX = len(THEMES) - 1


class LevelData:
    def __init__(self):
        self.tile_group   = None
        self.hazard_group = None
        self.enemy_group  = None
        self.coin_group   = None
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


def _add_coin(coins, col, row):
    coins.append((col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2))


def _place_feature(feat, col, end, layout, gap_cols, spike_cols,
                   coins, enemy_spawns, bird_spawns, rng, diff, is_city=False):
    koopa_chance = min(0.20 + 0.06 * diff, 0.5)

    def ground_enemy():
        # In the city phase, the new Robot enemy patrols the streets.
        if is_city and rng.random() < 0.7:
            return 'robot'
        return 'koopa' if rng.random() < koopa_chance else 'goomba'

    if feat == 'flat':
        length = rng.randint(4, 7)
        if rng.random() < 0.6:
            enemy_spawns.append(((col + length // 2) * TILE_SIZE, ground_enemy()))
        return col + length + 1

    if feat == 'coin_line':
        n = rng.randint(3, 5)
        for i in range(n):
            if col + i < end:
                _add_coin(coins, col + i, 12)
        return col + n + 1

    if feat == 'pipe':
        pr = rng.choice([10, 11])
        _create_pipe(col, pr, layout)
        _add_coin(coins, col, pr - 2)
        _add_coin(coins, col + 1, pr - 2)
        if rng.random() < 0.5:
            enemy_spawns.append(((col + 3) * TILE_SIZE,
                                 'robot' if is_city else 'goomba'))
        return col + 4

    if feat == 'gap':
        gw = 2 if diff < 2 else rng.choice([2, 3])
        for i in range(gw):
            gap_cols.add(col + i)
        for i in range(gw):
            _add_coin(coins, col + i, 9)
        if diff >= 3 and rng.random() < 0.5:
            bird_spawns.append({
                'x': (col + gw // 2) * TILE_SIZE,
                'y': 7 * TILE_SIZE,
                'pmin': (col - 3) * TILE_SIZE,
                'pmax': (col + gw + 3) * TILE_SIZE,
            })
        return col + gw + 2

    if feat == 'parkour':
        n = rng.randint(2, 4)
        base_row = 10
        top_row = max(6, base_row - (n - 1))
        for i in range(n):
            prow = max(6, base_row - i)
            pcol = col + i * 2
            layout[(pcol,     prow)] = 'S'
            layout[(pcol + 1, prow)] = 'S'
            _add_coin(coins, pcol, prow - 1)
        if rng.random() < 0.75:
            bird_spawns.append({
                'x': (col + n) * TILE_SIZE,
                'y': (top_row - 1) * TILE_SIZE,
                'pmin': col * TILE_SIZE,
                'pmax': (col + n * 2 + 1) * TILE_SIZE,
            })
        return col + n * 2 + 2

    if feat == 'spikes':
        w = rng.choice([1, 1, 2, 2, 3]) if diff >= 2 else rng.choice([1, 2])
        for i in range(w):
            spike_cols.add(col + i)
        return col + w + rng.randint(2, 4)

    return col + 4


def build_level(level_num, sprites, seed=0):
    import pygame

    rng = random.Random(seed * 1000003 + level_num * 7919 + 13)
    data = LevelData()
    # First boss is level 4. After it (level 5+), the world becomes a City.
    if level_num <= 4:
        data.theme_index = (level_num - 1) % 4
    else:
        data.theme_index = CITY_THEME_INDEX
    data.world_name  = f"{((level_num - 1) // 4) + 1}-{((level_num - 1) % 4) + 1}"

    diff = level_num - 1
    enemy_speed_mult = 1.0 + 0.12 * diff

    COLS = min(190 + 14 * diff, 300)
    data.level_width = COLS * TILE_SIZE

    flag_col = COLS - 9
    data.flagpole_x = flag_col * TILE_SIZE
    data.flagpole_y = TILE_SIZE * 3
    data.castle_x   = (flag_col + 4) * TILE_SIZE
    data.start_timer = 300

    SAFE_START = 11
    SAFE_END   = flag_col - 2

    tile_group   = pygame.sprite.Group()
    hazard_group = pygame.sprite.Group()
    enemy_group  = pygame.sprite.Group()
    coin_group   = pygame.sprite.Group()

    layout = {}
    gap_cols = set()
    spike_cols = set()
    coins = []
    enemy_spawns = []
    bird_spawns = []

    # Three SEPARATE ? blocks spread across the level (one per third), each at
    # its own random column and height. One of them holds the mushroom.
    span_start = SAFE_START + 4
    span_end   = SAFE_END - 8
    zone = max(6, (span_end - span_start) // 3)
    block_slots = []
    for z in range(3):
        z0 = span_start + z * zone
        bc = z0 + rng.randint(0, max(1, zone - 4))
        br = rng.choice([8, 9, 10])
        block_slots.append((bc, br))
    mush_idx = rng.randint(0, 2)

    col = SAFE_START + 4
    end = SAFE_END - 6
    while col < end:
        choices = ['flat', 'flat', 'coin_line', 'pipe', 'parkour', 'gap', 'parkour']
        if diff >= 2:
            choices += ['spikes', 'gap', 'parkour']
        if diff >= 4:
            choices += ['gap', 'spikes', 'parkour']
        feat = rng.choice(choices)
        col = _place_feature(feat, col, end, layout, gap_cols, spike_cols,
                             coins, enemy_spawns, bird_spawns, rng, diff,
                             is_city=(level_num > 4))

    # Place the power-up blocks after features so they sit on top, and never
    # over a pit column.
    for i, (bc, br) in enumerate(block_slots):
        if bc in gap_cols:
            bc += 1
        layout[(bc, br)] = 'M' if i == mush_idx else 'Q'

    _create_staircase(flag_col - 7, 12, size=min(4 + diff, 6),
                      ascends_right=True, layout=layout)

    for c in range(COLS):
        if c in gap_cols:
            continue
        layout[(c, 13)] = 'G'
        layout[(c, 14)] = 'G'

    tile_map = {
        'G': ('ground',   None),
        'B': ('brick',    None),
        'S': ('solid',    None),
        'Q': ('question', 'coin'),
        'M': ('question', 'mushroom'),
    }
    for (c, r), kind in layout.items():
        x, y = c * TILE_SIZE, r * TILE_SIZE
        if kind in tile_map:
            tile_type, item = tile_map[kind]
            tile_group.add(Tile(x, y, tile_type, sprites, contains_item=item))
        elif kind.startswith('pipe_'):
            tile_group.add(Tile(x, y, kind, sprites))

    for c in spike_cols:
        if c in gap_cols or (c, 12) in layout:
            continue
        hazard_group.add(Tile(c * TILE_SIZE, 12 * TILE_SIZE, 'spike', sprites))

    for (cx, cy) in coins:
        coin_group.add(Coin(cx, cy, sprites))

    for (sx, etype) in enemy_spawns:
        sy = 440 if etype == 'koopa' else 480
        e = Enemy(sx, sy, etype, sprites)
        base_speed = 1.8 if etype == 'robot' else 1.2
        e.vx = -base_speed * enemy_speed_mult
        e.shell_speed = 8.0 * enemy_speed_mult
        enemy_group.add(e)

    for sp in bird_spawns:
        e = Enemy(sp['x'], sp['y'], 'bird', sprites)
        e.vx = -2.0 * enemy_speed_mult
        e.fly_y = float(sp['y'])
        e.patrol_min = sp['pmin']
        e.patrol_max = sp['pmax']
        enemy_group.add(e)

    data.tile_group   = tile_group
    data.hazard_group = hazard_group
    data.enemy_group  = enemy_group
    data.coin_group   = coin_group
    return data


def is_boss_level(level_num):
    return level_num % 4 == 0


def build_boss_level(level_num, sprites, seed=0):
    import pygame

    data = LevelData()
    data.is_boss = True
    if level_num <= 4:
        data.theme_index = (level_num - 1) % 4
    else:
        data.theme_index = CITY_THEME_INDEX
    data.world_name = f"{((level_num - 1) // 4) + 1}-BOSS"
    data.level_width = SCREEN_WIDTH
    data.flagpole_x = 10 ** 9
    data.castle_x = 10 ** 9
    boss_round = level_num // 4
    data.start_timer = 300

    tile_group   = pygame.sprite.Group()
    hazard_group = pygame.sprite.Group()
    enemy_group  = pygame.sprite.Group()
    coin_group   = pygame.sprite.Group()

    kind = 'city' if level_num > 4 else 'classic'

    if kind == 'city':
        # Bigger, more vertical arena for the city mech boss so the player has
        # room to run and platforms to dodge lasers / reach the boss.
        COLS = 30
        platforms = {
            11: [(3, 5), (24, 26)],   # low side ledges
            9:  [(13, 16)],           # central platform
            8:  [(8, 10), (19, 21)],  # high side platforms
        }
        coin_spots = [(4, 10), (14, 8), (15, 8), (9, 7), (20, 7), (25, 10)]
        hp     = 6 + (boss_round - 2)   # mech boss starts at 6 HP
        speed  = 1.5 + 0.2 * (boss_round - 2)
        boss_x = (COLS // 2) * TILE_SIZE
    else:
        COLS = 20
        platforms = {9: [(4, 5), (14, 15)]}
        coin_spots = [(4, 8), (15, 8)]
        hp     = 4 + (boss_round - 1)   # classic boss has 4 HP
        speed  = 1.4 + 0.2 * (boss_round - 1)
        boss_x = 560

    data.level_width = max(SCREEN_WIDTH, COLS * TILE_SIZE)

    # Ground.
    for col in range(COLS):
        tile_group.add(Tile(col * TILE_SIZE, 13 * TILE_SIZE, 'ground', sprites))
        tile_group.add(Tile(col * TILE_SIZE, 14 * TILE_SIZE, 'ground', sprites))

    # Side walls.
    for r in range(6, 13):
        tile_group.add(Tile(0, r * TILE_SIZE, 'solid', sprites))
        tile_group.add(Tile((COLS - 1) * TILE_SIZE, r * TILE_SIZE, 'solid', sprites))

    # Platforms.
    for row, spans in platforms.items():
        for (c0, c1) in spans:
            for c in range(c0, c1 + 1):
                tile_group.add(Tile(c * TILE_SIZE, row * TILE_SIZE, 'solid', sprites))

    # Coins.
    for (c, r) in coin_spots:
        coin_group.add(Coin(c * TILE_SIZE + TILE_SIZE // 2,
                            r * TILE_SIZE + TILE_SIZE // 2, sprites))

    boss = Boss(boss_x, 13 * TILE_SIZE, sprites, hp=hp, speed=speed, kind=kind)
    boss.set_bounds(TILE_SIZE + 20, (COLS - 1) * TILE_SIZE - 20)
    data.boss = boss

    data.tile_group   = tile_group
    data.hazard_group = hazard_group
    data.enemy_group  = enemy_group
    data.coin_group   = coin_group
    return data
