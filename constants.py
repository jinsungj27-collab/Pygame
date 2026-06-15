# The game's layout is designed around a 600px logical height. We keep that
# height but widen the logical resolution to match the player's monitor aspect
# ratio, so the game fills the whole screen (no black bars) when shown with the
# SCALED | FULLSCREEN flags, and the player sees more of the level horizontally.
SCREEN_HEIGHT = 600


def _detect_screen_width():
    """Pick a logical width that matches the desktop's aspect ratio."""
    default_width = 1067  # 16:9 fallback at 600px height
    try:
        import pygame
        pygame.display.init()
        info = pygame.display.Info()
        dw, dh = info.current_w, info.current_h
        if dw > 0 and dh > 0:
            width = round(SCREEN_HEIGHT * dw / dh)
            # Keep it even and never narrower than the original 4:3 layout.
            width = max(800, width - (width % 2))
            return width
    except Exception:
        pass
    return default_width


SCREEN_WIDTH = _detect_screen_width()
FPS           = 60

TILE_SIZE         = 40
GRAVITY           = 0.6
TERMINAL_VELOCITY = 12

COLOR_MAP = {
    '.': (0,   0,   0,   0),
    'r': (220, 30,  30),
    'b': (30,  80,  200),
    's': (255, 200, 150),
    'k': (100, 60,  20),
    'y': (255, 225, 0),
    'w': (255, 255, 255),
    'g': (30,  180, 50),
    'o': (240, 130, 30),
    'e': (0,   0,   0),
    'm': (140, 20,  20),
    'c': (100, 200, 255),
    'G': (10,  100, 20),
    'd': (80,  80,  80),
    'l': (160, 160, 160),
    'p': (200, 80,  60),
    'v': (150, 90,  220),
    'a': (90,  50,  150),
}

SKY_BLUE      = (107, 140, 255)
DARK_SKY_BLUE = (92,  126, 255)
