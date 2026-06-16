import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")


class Settings:
    def __init__(self):
        self.master_volume = 1.0
        self.music_volume = 0.5
        self.sfx_volume   = 0.7
        self.music_enabled = True
        # Index into Game.display_modes (0 = Fullscreen by default).
        self.display_mode = 0
        # How many lives a new game starts with. -1 means infinite.
        self.starting_lives = 3
        self.load()

    def clamp(self):
        self.master_volume = max(0.0, min(1.0, self.master_volume))
        self.music_volume = max(0.0, min(1.0, self.music_volume))
        self.sfx_volume   = max(0.0, min(1.0, self.sfx_volume))

    # The actual loudness used by the mixer combines the per-channel volume
    # with the master volume.
    def effective_music(self):
        return self.music_volume * self.master_volume

    def effective_sfx(self):
        return self.sfx_volume * self.master_volume

    def to_dict(self):
        return {
            "master_volume": self.master_volume,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "music_enabled": self.music_enabled,
            "display_mode": self.display_mode,
            "starting_lives": self.starting_lives,
        }

    def load(self):
        try:
            with open(_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                self.master_volume = float(d.get("master_volume", self.master_volume))
                self.music_volume = float(d.get("music_volume", self.music_volume))
                self.sfx_volume = float(d.get("sfx_volume", self.sfx_volume))
                self.music_enabled = bool(d.get("music_enabled", self.music_enabled))
                self.display_mode = int(d.get("display_mode", self.display_mode))
                self.starting_lives = int(d.get("starting_lives", self.starting_lives))
                self.clamp()
        except Exception:
            pass

    def save(self):
        try:
            with open(_PATH, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f)
        except Exception:
            pass


settings = Settings()
