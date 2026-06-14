# ── Screen / physics constants ────────────────────────────────────────────────
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS           = 60

TILE_SIZE         = 40   # 40x40 pixel grid
GRAVITY           = 0.6
TERMINAL_VELOCITY = 12

# ── Colour palette (shared by pixel-art renderer and tile drawing) ─────────────
COLOR_MAP = {
    '.': (0,   0,   0,   0),    # Transparent
    'r': (220, 30,  30),        # Red   (Cap & Shirt)
    'b': (30,  80,  200),       # Blue  (Overalls)
    's': (255, 200, 150),       # Skin / Peach
    'k': (100, 60,  20),        # Brown (Hair, Shoes, Goomba cap)
    'y': (255, 225, 0),         # Yellow (Buttons, Coins)
    'w': (255, 255, 255),       # White  (Gloves, eyes, clouds)
    'g': (30,  180, 50),        # Green  (Koopa, Pipes, bushes)
    'o': (240, 130, 30),        # Orange (Brick highlight)
    'e': (0,   0,   0),         # Black  (Outline, eyes)
    'm': (140, 20,  20),        # Maroon (Big Mario shadows)
    'c': (100, 200, 255),       # Cyan   (Sky detail)
    'G': (10,  100, 20),        # Dark Green (Pipe shadow)
    'd': (80,  80,  80),        # Dark Gray  (Solid block)
    'l': (160, 160, 160),       # Light Gray (Solid block highlight)
    'p': (200, 80,  60),        # Terracotta (Brick main)
}

SKY_BLUE      = (107, 140, 255)
DARK_SKY_BLUE = (92,  126, 255)
