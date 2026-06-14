"""
Global game settings (volumes, toggles).

A single shared `settings` instance is imported wherever it's needed so that
adjusting a slider in the pause/settings menu instantly affects every sound.
"""


class Settings:
    def __init__(self):
        # Volumes are 0.0 .. 1.0 multipliers applied on top of each sound's
        # own baseline volume.
        self.music_volume = 0.5
        self.sfx_volume   = 0.7
        self.music_enabled = True

    def clamp(self):
        self.music_volume = max(0.0, min(1.0, self.music_volume))
        self.sfx_volume   = max(0.0, min(1.0, self.sfx_volume))


# Shared singleton
settings = Settings()
