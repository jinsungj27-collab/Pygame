class Settings:
    def __init__(self):
        self.music_volume = 0.5
        self.sfx_volume   = 0.7
        self.music_enabled = True

    def clamp(self):
        self.music_volume = max(0.0, min(1.0, self.music_volume))
        self.sfx_volume   = max(0.0, min(1.0, self.sfx_volume))


settings = Settings()
