import math
import random
import sys

import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE,
)
from spritesheet import SpriteSheet
from settings import settings
from ui import Button, Slider, draw_vertical_gradient
from levels import (
    build_level, build_boss_level, build_pvp_level, is_boss_level,
    pvp_level_count, THEMES,
)
from highscore import load_high_score, save_high_score
from progress import load_progress, save_progress, default_progress
from shop import ShopScreen, character_palette, get_character
import sounds
from sounds import (
    play_coin_second_tone, sfx_powerup, sfx_powerup_spawn, sfx_stomp,
    sfx_clear, sfx_menu_select, sfx_pause, sfx_unpause, sfx_level_start,
    sfx_hazard, sfx_firework, sfx_coin, start_music, start_boss_music,
    stop_music, update_music_volume, set_jump_profile,
)
from entities import Player, Enemy, Item, Tile, Particle
from legal import TOS_TEXT, LEGAL_TEXT
from skills import SkillManager


MENU, INTRO, PLAYING, PAUSED, SETTINGS, CLEAR, GAMEOVER, TOS, LEGAL, SHOP, MODESELECT, CONTROLS = (
    'menu', 'intro', 'playing', 'paused', 'settings', 'clear', 'gameover',
    'tos', 'legal', 'shop', 'modeselect', 'controls'
)

# Game modes selected from the mode-select screen.
MODE_ENDLESS = 'endless'
MODE_PVP = 'pvp'

# Each collected coin is worth this much toward the shop wallet (and the
# per-run coin counter). Characters cost 10,000 and skins 5,000, so the grind
# stays meaningful.
COIN_VALUE = 50


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)
        except Exception:
            pass

        # Build the list of display modes the player can choose from in
        # Settings: fullscreen plus a few windowed sizes that match the
        # game's aspect ratio (so there's never any distortion).
        self.display_modes = self._build_display_modes()
        if settings.display_mode >= len(self.display_modes):
            settings.display_mode = 0

        # The game always renders onto this fixed-size offscreen surface, then
        # it gets scaled to fill the actual window/screen. Every draw call uses
        # self.screen, so the rest of the game is unaware of the real window size.
        self.window = None
        self.render = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = self.render
        self._dst = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._scale = 1.0
        self.render_shake = (0, 0)
        self._apply_display_mode()
        pygame.display.set_caption("Super Jin  v2.5.0")
        self.clock = pygame.time.Clock()

        self.font_hud   = pygame.font.Font(None, 24); self.font_hud.set_bold(True)
        self.font_menu  = pygame.font.Font(None, 34); self.font_menu.set_bold(True)
        self.font_title = pygame.font.Font(None, 46); self.font_title.set_bold(True)
        self.font_big   = pygame.font.Font(None, 88); self.font_big.set_bold(True)
        self.font_small = pygame.font.Font(None, 22)

        self.sprites = SpriteSheet()

        self.score     = 0
        self.coins     = 0
        self.lives     = 3
        self.infinite_lives = False
        self.level_num = 1
        self.high_score = load_high_score()
        self.prev_high  = self.high_score
        self.new_record = False

        # Persistent shop progress: coin wallet + owned/equipped characters.
        self.progress = load_progress()
        self.wallet = self.progress.get('wallet', 0)

        self.state = MENU

        self.clouds = [(random.randint(0, 4000), random.randint(40, 200),
                        random.uniform(0.4, 1.0)) for _ in range(14)]
        self.stars  = [(random.randint(0, SCREEN_WIDTH), random.randint(0, 360),
                        random.uniform(0.3, 1.0)) for _ in range(70)]
        self.menu_scroll = 0.0
        # Where the SETTINGS screen should return to (MENU or PAUSED).
        self.settings_return = MENU

        self.theme = THEMES[0]
        self.level_width = 3800
        self.is_boss = False
        self.boss = None
        self.mode = MODE_ENDLESS
        self.boss_name = None
        self.victory = False
        self.projectile_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.cleared_boss = False

        self.intro_timer = 0
        self.clear_timer = 0
        self.firework_cd = 0

        self.level = None
        self._build_ui()

        # Build the shop UI and apply the equipped character's look + sound.
        self.shop = ShopScreen(self)
        self.apply_selected_character()

        start_music(0)

    def _build_ui(self):
        cx = SCREEN_WIDTH // 2

        self.btn_play = Button(cx, 322, 260, 60, "PLAY", self.font_menu, icon='play',
                               base_color=(30, 120, 60), hover_color=(50, 170, 90))
        self.btn_shop = Button(cx, 390, 260, 60, "SHOP", self.font_menu, icon='shop',
                               base_color=(150, 110, 30), hover_color=(200, 150, 50))
        self.btn_menu_settings = Button(cx, 458, 260, 60, "SETTINGS", self.font_menu,
                                        icon='gear')
        self.btn_exit = Button(cx, 526, 260, 60, "EXIT", self.font_menu, icon='exit',
                               base_color=(120, 40, 40), hover_color=(170, 60, 60))

        # MODE SELECT screen: two big picture buttons (Endless = Mario,
        # PvP/Boss-Rush = Mech) plus a back button.
        self.btn_mode_endless = Button(cx - 165, 350, 280, 240, "",
                                       self.font_menu,
                                       base_color=(28, 92, 140),
                                       hover_color=(46, 130, 196))
        self.btn_mode_pvp = Button(cx + 165, 350, 280, 240, "",
                                   self.font_menu,
                                   base_color=(140, 44, 52),
                                   hover_color=(196, 64, 74))
        self.btn_mode_back = Button(cx, 540, 200, 50, "BACK", self.font_menu,
                                    icon='home', base_color=(110, 70, 30),
                                    hover_color=(160, 110, 50))

        self.btn_resume   = Button(cx, 250, 280, 60, "RESUME", self.font_menu, icon='play',
                                   base_color=(30, 120, 60), hover_color=(50, 170, 90))
        self.btn_settings = Button(cx, 325, 280, 60, "SETTINGS", self.font_menu, icon='gear')
        self.btn_mainmenu = Button(cx, 400, 280, 60, "MAIN MENU", self.font_menu, icon='home',
                                   base_color=(110, 70, 30), hover_color=(160, 110, 50))

        # SETTINGS screen, laid out in two columns: Audio (left) and Game (right).
        left_cx  = cx - 230
        right_cx = cx + 230

        self.slider_master = Slider(left_cx - 150, 156, 300, "Master Volume",
                                    self.font_small, value=settings.master_volume)
        self.slider_music = Slider(left_cx - 150, 218, 300, "Music Volume",
                                   self.font_small, value=settings.music_volume)
        self.slider_sfx   = Slider(left_cx - 150, 280, 300, "Sound Effects",
                                   self.font_small, value=settings.sfx_volume)
        self.btn_music_toggle = Button(left_cx, 330, 280, 44, self._music_label(),
                                       self.font_small)

        self.btn_lives   = Button(right_cx, 156, 280, 46, self._lives_label(),
                                  self.font_small)
        self.btn_display = Button(right_cx, 216, 280, 46, self._display_label(),
                                  self.font_small)
        self.btn_reset   = Button(right_cx, 276, 280, 46, "RESET PROGRESS",
                                  self.font_small, base_color=(120, 50, 50),
                                  hover_color=(170, 70, 70))
        self.btn_god     = Button(right_cx, 336, 280, 46, self._god_label(),
                                  self.font_small, base_color=(40, 95, 65),
                                  hover_color=(60, 150, 95))

        self.btn_tos   = Button(cx - 100, 474, 188, 44, "TERMS OF SERVICE",
                                self.font_small,
                                base_color=(50, 50, 80), hover_color=(80, 80, 130))
        self.btn_legal = Button(cx + 100, 474, 188, 44, "LEGAL", self.font_small,
                                base_color=(50, 50, 80), hover_color=(80, 80, 130))
        self.btn_back = Button(cx, 534, 200, 50, "BACK", self.font_menu)

        # CONTROLS button (opens the dedicated controls/how-to-play screen)
        # plus that screen's own back button.
        self.btn_controls = Button(cx, 424, 300, 44, "HOW TO PLAY",
                                   self.font_small, base_color=(46, 70, 120),
                                   hover_color=(74, 108, 184))
        self.btn_controls_back = Button(cx, 542, 200, 50, "BACK", self.font_menu)

        # Reset-progress confirmation dialog.
        self.reset_confirm = False
        self.btn_reset_yes = Button(cx - 115, 360, 190, 54, "YES, RESET",
                                    self.font_menu, base_color=(120, 40, 40),
                                    hover_color=(170, 60, 60))
        self.btn_reset_no = Button(cx + 115, 360, 190, 54, "CANCEL",
                                   self.font_menu, base_color=(30, 120, 60),
                                   hover_color=(50, 170, 90))

        # Shared BACK button for the TOS / Legal reading screens.
        self.btn_doc_back = Button(cx, 552, 200, 44, "BACK", self.font_menu)
        # Vertical scroll offsets for the document reading screens.
        self.tos_scroll = 0.0
        self.legal_scroll = 0.0
        self._doc_max_scroll = 0.0

        self.btn_retry    = Button(cx, 356, 260, 60, "RETRY", self.font_menu, icon='play',
                                   base_color=(30, 120, 60), hover_color=(50, 170, 90))
        self.btn_go_menu  = Button(cx, 428, 260, 60, "MAIN MENU", self.font_menu, icon='home',
                                   base_color=(110, 70, 30), hover_color=(160, 110, 50))

    def _music_label(self):
        return "Music: ON" if settings.music_enabled else "Music: OFF"

    def _display_label(self):
        return f"Screen: {self.display_modes[settings.display_mode][0]}"

    def _lives_label(self):
        n = settings.starting_lives
        return f"Lives: {'Infinite' if n < 0 else n}"

    def _god_label(self):
        return f"God Mode: {'ON' if settings.god_mode else 'OFF'}"

    def apply_selected_character(self):
        """Recolor the player sprites and set the jump sound for the equipped
        character + skin stored in self.progress."""
        char_id = self.progress['selected_character']
        skin_id = self.progress['selected_skin']
        palette = character_palette(char_id, skin_id)
        self.sprites.apply_character(char_id, palette)
        char = get_character(char_id)
        freqs, wave = char.get('jump', ([160, 680, 820], 'square'))
        set_jump_profile(freqs, wave)

    def persist_progress(self):
        """Sync the wallet into the progress dict and write it to disk."""
        self.progress['wallet'] = self.wallet
        save_progress(self.progress)

    def _save_all(self):
        """Persist coins (wallet) and high score together. Called at safe
        points (pausing, level transitions) so progress is never lost."""
        if self.score > self.high_score:
            self.high_score = self.score
        try:
            save_high_score(self.high_score)
        except Exception:
            pass
        self.persist_progress()

    def start_new_game(self):
        self.score     = 0
        self.coins     = 0
        # Coins/blocks already collected this run stay collected across deaths;
        # they only reappear on a brand-new game. This also makes farming
        # impossible. Keyed by (level_num, x, y).
        self.collected_coins = set()
        self.spent_blocks = set()
        # Fresh random layout seed so obstacles differ every playthrough
        # (but stay stable across retries within this run).
        self.run_seed  = random.randrange(1, 1 << 30)
        self.infinite_lives = settings.starting_lives < 0
        self.lives     = 99 if self.infinite_lives else settings.starting_lives
        self.level_num = 1
        self.prev_high = self.high_score
        self.new_record = False
        self.victory = False
        self.load_level(self.level_num)
        self._enter_intro()

    def load_level(self, level_num):
        seed = getattr(self, 'run_seed', 0)
        self.boss_name = None
        if self.mode == MODE_PVP:
            # Boss-rush: every level is a boss battle.
            self.is_boss = True
            self.level = build_pvp_level(level_num, self.sprites, seed=seed)
            self.boss_name = self.level.boss_name
        else:
            self.is_boss = is_boss_level(level_num)
            if self.is_boss:
                self.level = build_boss_level(level_num, self.sprites, seed=seed)
            else:
                self.level = build_level(level_num, self.sprites, seed=seed)
        self.theme = THEMES[self.level.theme_index]

        self.camera_x = 0
        self.timer = self.level.start_timer
        self.time_tick_counter = 0
        self.stage_clear = False
        self.cleared_boss = False

        self.flagpole_x = self.level.flagpole_x
        self.flagpole_y = self.level.flagpole_y
        self.flag_y     = self.flagpole_y
        self.castle_x   = self.level.castle_x
        self.level_width = self.level.level_width

        self.tile_group     = self.level.tile_group
        self.hazard_group   = self.level.hazard_group
        self.enemy_group    = self.level.enemy_group
        self.item_group     = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.coin_group     = self.level.coin_group
        self.boss = self.level.boss

        # Remove coins already collected this run and mark already-used ? blocks
        # as spent, so they don't reappear when retrying after a death.
        collected = getattr(self, 'collected_coins', set())
        for c in list(self.coin_group):
            if (level_num, c.rect.centerx, c.rect.centery) in collected:
                c.kill()
        spent = getattr(self, 'spent_blocks', set())
        for t in self.tile_group:
            if getattr(t, 'tile_type', None) == 'question' and \
                    (level_num, t.rect.x, t.rect.y) in spent:
                t.tile_type = 'spent'
                t.contains_item = None

        # Spawn standing on the ground (row 13) instead of dropping from the
        # sky. The sprite is anchored at y + 40, so y = ground_top - 40.
        spawn_y = 13 * TILE_SIZE - 40
        self.player = Player(100, spawn_y, self.sprites)
        self.player_group = pygame.sprite.GroupSingle(self.player)

        # Combat skills are only active in boss battles. A fresh manager is
        # created for each boss so both skills start on the short cooldown.
        if self.is_boss and self.boss is not None:
            self.skills = SkillManager(self, self.progress['selected_character'])
        else:
            self.skills = None

    def reset_current_level(self):
        # On a boss level, keep the damage already dealt to the boss so dying
        # doesn't fully heal it - the player resumes the fight where they left.
        preserved_hp = None
        if self.is_boss and self.boss is not None and not self.boss.is_dead:
            preserved_hp = self.boss.hp
        self.load_level(self.level_num)
        if preserved_hp is not None and self.boss is not None:
            self.boss.hp = preserved_hp
        self._start_level_music()

    def theme_index(self):
        return self.level.theme_index if self.level else 0

    def _start_level_music(self):
        """Boss levels get a tense boss theme (per-boss in PvP); normal levels
        use their overworld theme music."""
        if self.is_boss:
            if self.mode == MODE_PVP:
                start_boss_music(self.level_num - 1)
            else:
                start_boss_music(self.level_num // 4)
        else:
            start_music(self.theme_index())

    def next_level(self):
        self.level_num += 1
        self.score += 2000
        if self.mode == MODE_PVP and self.level_num > pvp_level_count():
            self._on_victory()
            return
        self.load_level(self.level_num)
        self._enter_intro()

    def _on_victory(self):
        """All PvP bosses cleared - show the game-over screen as a win."""
        stop_music()
        # Bank the run's coins into the persistent wallet, just like a normal
        # game over, so a winning run isn't penalized by losing its coins.
        self.wallet += self.coins
        self.victory = True
        self.new_record = self.score > self.prev_high
        if self.score > self.high_score:
            self.high_score = self.score
        save_high_score(self.high_score)
        self.persist_progress()
        self.state = GAMEOVER

    def _enter_intro(self):
        self.state = INTRO
        self.intro_timer = int(FPS * 2.4)
        self.intro_timer_max = self.intro_timer
        sfx_level_start()

    def handle_collisions(self):
        if self.player.is_dead:
            return

        self.player.rect.centerx = self.player.x
        if not self.player.victory_walk:
            for tile in pygame.sprite.spritecollide(self.player, self.tile_group, False):
                if self.player.vx > 0:
                    self.player.rect.right = tile.rect.left
                elif self.player.vx < 0:
                    self.player.rect.left = tile.rect.right
                self.player.vx = 0
                self.player.x  = self.player.rect.centerx

        self.player.y     += self.player.vy
        self.player.rect.y = self.player.y
        self.player.on_ground = False

        for tile in pygame.sprite.spritecollide(self.player, self.tile_group, False):
            if self.player.vy > 0:
                self.player.rect.bottom = tile.rect.top
                self.player.vy        = 0
                self.player.on_ground = True
            elif self.player.vy < 0:
                self.player.rect.top = tile.rect.bottom
                self.player.vy = 0
                self._trigger_block_hit(tile)
            self.player.y = self.player.rect.y

        if self.player.x < self.camera_x + 15:
            self.player.x  = self.camera_x + 15
            self.player.vx = 0
            self.player.rect.centerx = self.player.x

        if self.player.y > SCREEN_HEIGHT + 50:
            if settings.god_mode:
                # Don't die in pits - re-enter from the top so testing can
                # continue (air-steer back onto solid ground).
                self.player.y  = -40
                self.player.vy = 0
                self.player.rect.y = int(self.player.y)
            else:
                self.player.die()

        if (self.player.invincible_timer <= 0 and not self.player.is_dead
                and pygame.sprite.spritecollide(self.player, self.hazard_group, False)):
            sfx_hazard()
            self.player.take_damage()

        for coin in pygame.sprite.spritecollide(self.player, self.coin_group, True):
            self.coins += COIN_VALUE
            self.collected_coins.add((self.level_num, coin.rect.centerx, coin.rect.centery))
            self.score += 200
            sfx_coin()
            sx = coin.rect.x - self.camera_x
            self.particle_group.add(
                Particle.create_score(sx, coin.rect.y - 18, "200", self.font_hud,
                                      color=(255, 255, 255))
            )
            self.particle_group.add(
                Particle.create_score(sx, coin.rect.y + 8, f"+{COIN_VALUE}", self.font_hud,
                                      color=(255, 215, 70))
            )

        for item in pygame.sprite.spritecollide(self.player, self.item_group, False):
            if item.state == "active" and item.item_type == 'mushroom':
                sfx_powerup()
                self.player.is_big = True
                self.score += 1000
                self.particle_group.add(
                    Particle.create_score(item.rect.x - self.camera_x, item.rect.y,
                                          "1000", self.font_hud)
                )
                item.kill()

        for enemy in pygame.sprite.spritecollide(self.player, self.enemy_group, False):
            if enemy.is_dead:
                continue
            stomped = (
                self.player.vy > 0
                and self.player.rect.bottom < enemy.rect.centery + 10
            )
            if stomped:
                self.player.vy = -7.5
                enemy.squish()
                self.score += 200
                self.particle_group.add(
                    Particle.create_score(enemy.rect.x - self.camera_x, enemy.rect.y,
                                          "200", self.font_hud)
                )
            else:
                if enemy.in_shell and enemy.vx == 0:
                    direction = 1 if self.player.rect.centerx < enemy.rect.centerx else -1
                    enemy.kick(direction)
                else:
                    self.player.take_damage()

        for enemy in self.enemy_group:
            if enemy.enemy_type != 'koopa' or not enemy.in_shell or abs(enemy.vx) < 0.1:
                continue
            for hit in pygame.sprite.spritecollide(enemy, self.enemy_group, False):
                if hit is enemy or hit.is_dead:
                    continue
                sfx_stomp()
                hit.is_dead = True
                hit.vy      = -6.0
                hit.vx      = 2.0 if enemy.vx > 0 else -2.0
                self.score += 500
                self.particle_group.add(
                    Particle.create_score(hit.rect.x - self.camera_x, hit.rect.y,
                                          "500", self.font_hud)
                )

    def _trigger_block_hit(self, tile):
        tile.bump()

        if tile.tile_type == 'question':
            if tile.contains_item == 'coin':
                self.coins += COIN_VALUE
                self.score += 200
                self.item_group.add(Item(tile.rect.x, tile.rect.y, 'coin', self.sprites))
                sx = tile.rect.x - self.camera_x
                self.particle_group.add(
                    Particle.create_score(sx, tile.rect.y - 28, "200", self.font_hud,
                                          color=(255, 255, 255))
                )
                self.particle_group.add(
                    Particle.create_score(sx, tile.rect.y - 4, f"+{COIN_VALUE}", self.font_hud,
                                          color=(255, 215, 70))
                )
            elif tile.contains_item == 'mushroom':
                sfx_powerup_spawn()
                self.item_group.add(Item(tile.rect.x, tile.rect.y, 'mushroom', self.sprites))
            tile.tile_type     = 'spent'
            tile.contains_item = None
            # Remember this block so it stays spent after a death-retry.
            self.spent_blocks.add((self.level_num, tile.rect.x, tile.rect.y))

        elif tile.tile_type == 'brick' and self.player.is_big:
            tile.kill()
            self.particle_group.add(*Particle.create_debris(tile.rect.x, tile.rect.y))
            self.score += 50

    def check_stage_clear(self):
        if self.stage_clear or self.is_boss:
            return

        if (
            self.player.x >= self.flagpole_x
            and not self.player.flag_sliding
            and not self.player.victory_walk
        ):
            sfx_clear()
            self.player.flag_sliding = True
            self.player.x  = self.flagpole_x
            self.player.vx = 0
            self.player.vy = 2

        if self.player.flag_sliding:
            if self.flag_y < self.flagpole_y + 360:
                self.flag_y += 3.0
            if self.player.y >= TILE_SIZE * 11:
                self.player.flag_sliding = False
                self.player.victory_walk = True
                self.player.y  = TILE_SIZE * 11
                self.player.vx = 2

        if self.player.victory_walk and self.player.x >= self.castle_x:
            self.player.victory_walk = False
            self.player.vx           = 0
            self.stage_clear         = True
            self._enter_clear()

    def _enter_clear(self, boss=False):
        self.state = CLEAR
        self.clear_timer = int(FPS * 4.5)
        self.firework_cd = 0
        self.cleared_boss = boss
        self.score += max(0, self.timer) * 10
        self._save_all()

    def _handle_boss_combat(self):
        boss = self.boss

        if boss.is_dead:
            if boss.dead_timer <= 0 and not self.stage_clear:
                self.stage_clear = True
                self.score += 5000
                self.particle_group.add(
                    Particle.create_score(boss.rect.centerx - self.camera_x, boss.rect.top,
                                          "5000", self.font_hud)
                )
                self._enter_clear(boss=True)
            return

        if self.player.is_dead:
            return

        for fb in pygame.sprite.spritecollide(self.player, self.projectile_group, False):
            if self.player.invincible_timer <= 0:
                self.player.take_damage()
            fb.kill()

        if self.player.rect.colliderect(boss.rect):
            # If the boss was just hit (invincible), contact does nothing - no
            # stomp and no damage. This prevents the player from taking damage
            # in the frames right after a successful stomp while still
            # overlapping the boss (the "jump over its back" bug).
            if boss.invincible > 0:
                pass
            else:
                stomped = (self.player.vy > 0
                           and self.player.rect.bottom < boss.rect.centery + 6)
                if stomped:
                    self.player.vy = -9.5
                    # Brief grace so the upward bounce can't be punished.
                    self.player.invincible_timer = max(
                        self.player.invincible_timer, 40)
                    defeated = boss.stomp()
                    self.score += 300
                    self.particle_group.add(
                        Particle.create_score(boss.rect.centerx - self.camera_x, boss.rect.top,
                                              "300", self.font_hud)
                    )
                    if defeated:
                        self.particle_group.add(*Particle.create_firework(
                            boss.rect.centerx, boss.rect.centery))
                else:
                    self.player.take_damage()

    def _on_game_over(self):
        stop_music()
        # Bank the run's coins into the persistent wallet now that the game has
        # truly ended (this is the only place coins are committed, which stops
        # death-respawn coin farming, especially with infinite lives).
        self.wallet += self.coins
        self.victory = False
        self.new_record = self.score > self.prev_high
        if self.score > self.high_score:
            self.high_score = self.score
        save_high_score(self.high_score)
        self.persist_progress()
        self.state = GAMEOVER

    def update_playing(self):
        if not self.stage_clear and not self.player.is_dead:
            self.time_tick_counter += 1
            if self.time_tick_counter >= FPS:
                self.time_tick_counter = 0
                self.timer -= 1
                if self.timer <= 0:
                    self.player.die()

        self.player_group.update()

        if self.player.x > self.camera_x + SCREEN_WIDTH * 0.45 and not self.stage_clear:
            self.camera_x = min(
                self.player.x - SCREEN_WIDTH * 0.45,
                self.level_width - SCREEN_WIDTH,
            )

        self.tile_group.update()
        self.item_group.update(self.tile_group)
        self.enemy_group.update(self.tile_group)
        self.particle_group.update()
        self.coin_group.update()

        if self.is_boss and self.boss is not None:
            self.boss.update(self.tile_group, self.projectile_group, self.player)
            self.projectile_group.update(self.tile_group)
            self._handle_boss_combat()
            if self.skills is not None:
                self.skills.update()

        self.handle_collisions()
        self.check_stage_clear()

        if self.score > self.high_score:
            self.high_score = self.score

        if self.player.is_dead:
            self.player.death_timer -= 1
            if self.player.death_timer <= 0:
                if self.infinite_lives:
                    self.reset_current_level()
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self._on_game_over()
                    else:
                        self.reset_current_level()

    def update_clear(self):
        self.particle_group.update()
        self.firework_cd -= 1
        if self.firework_cd <= 0:
            self.firework_cd = random.randint(14, 26)
            fx = self.camera_x + random.randint(120, SCREEN_WIDTH - 120)
            fy = random.randint(80, 280)
            self.particle_group.add(*Particle.create_firework(fx, fy))
            sfx_firework()

        self.clear_timer -= 1
        if self.clear_timer <= 0:
            self.next_level()

    def _draw_background(self, cam):
        th = self.theme

        draw_vertical_gradient(self.screen, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                               th['sky_top'], th['sky_bottom'])

        ticks = pygame.time.get_ticks()

        if th['night']:
            for sx, sy, b in self.stars:
                tw = 0.5 + 0.5 * math.sin(ticks * 0.002 + sx)
                v = int(150 + 105 * b * tw)
                self.screen.fill((v, v, min(255, v + 20)), (sx, sy, 2, 2))

        sun_color = th['sun']
        if th['night']:
            pygame.draw.circle(self.screen, sun_color, (SCREEN_WIDTH - 120, 110), 42)
            pygame.draw.circle(self.screen, th['sky_top'], (SCREEN_WIDTH - 105, 100), 36)
        else:
            for rad, alpha in ((70, 40), (54, 90), (42, 255)):
                glow = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*sun_color, alpha), (rad, rad), rad)
                self.screen.blit(glow, (SCREEN_WIDTH - 120 - rad, 110 - rad))

        if th.get('city'):
            self._draw_city_skyline(cam)
        else:
            mcam = cam * 0.2
            mcolor = th['mountain']
            for mx in range(-200, self.level_width + 400, 420):
                hx = mx - mcam
                pygame.draw.polygon(self.screen, mcolor,
                                    [(hx, 470), (hx + 210, 250), (hx + 420, 470)])
                peak = (min(mcolor[0] + 40, 255), min(mcolor[1] + 40, 255), min(mcolor[2] + 40, 255))
                pygame.draw.polygon(self.screen, peak,
                                    [(hx + 170, 290), (hx + 210, 250), (hx + 250, 290),
                                     (hx + 230, 305), (hx + 190, 305)])

            hcam = cam * 0.3
            for hill_x in range(-100, self.level_width + 200, 600):
                hx = hill_x - hcam
                pygame.draw.polygon(self.screen, th['hill_shadow'],
                                    [(hx, 520), (hx + 150, 320), (hx + 300, 520)])
                pygame.draw.polygon(self.screen, th['hill'],
                                    [(hx + 30, 520), (hx + 160, 340), (hx + 290, 520)])

        drift = ticks * 0.012
        for i, (cxp, cyp, scl) in enumerate(self.clouds):
            cxw = (cxp + drift) % (self.level_width + 400)
            cx = cxw - cam * 0.1
            self._draw_cloud(cx, cyp, scl, th['cloud'])

    def _draw_city_skyline(self, cam):
        """Parallax city skyline with randomized building heights/widths and
        lit windows, used by the City theme."""
        base_y = 520  # building bottoms sit on the ground horizon
        lit = (255, 224, 140)
        # (parallax factor, spacing, body color, min height, max height, salt)
        layers = [
            (0.18, 170, (66, 78, 120), 140, 270, 1234),
            (0.32, 130, (44, 54, 92), 90, 230, 8765),
        ]
        for pfac, step, body, hmin, hmax, salt in layers:
            bcam = cam * pfac
            for i, bx in enumerate(range(-step, self.level_width + step, step)):
                x = int(bx - bcam)
                if x < -step or x > SCREEN_WIDTH:
                    continue
                hh = self._hash(i + salt)
                hw = self._hash(i * 3 + salt + 7)
                h = hmin + hh % (hmax - hmin)
                w = step - 22 - hw % 26
                top = base_y - h
                pygame.draw.rect(self.screen, body, (x, top, w, h))
                hl = (min(body[0] + 25, 255), min(body[1] + 25, 255), min(body[2] + 25, 255))
                pygame.draw.rect(self.screen, hl, (x, top, w, 5))
                # Occasional rooftop antenna for taller buildings.
                if h > hmax - 50 and (hh >> 9) % 2 == 0:
                    pygame.draw.rect(self.screen, hl, (x + w // 2 - 1, top - 14, 2, 14))
                cols = max(1, (w - 12) // 18)
                rows = max(1, (h - 16) // 22)
                for r in range(rows):
                    for c in range(cols):
                        if (self._hash(i * 131 + r * 17 + c * 7 + salt)) % 3 != 0:
                            continue
                        pygame.draw.rect(self.screen, lit,
                                         (x + 8 + c * 18, top + 12 + r * 22, 8, 11))

    @staticmethod
    def _hash(n):
        """Small integer hash for stable, well-spread pseudo-random values."""
        n = (n ^ 61) ^ ((n >> 16) & 0xffffffff)
        n = (n + (n << 3)) & 0xffffffff
        n ^= (n >> 4)
        n = (n * 0x27d4eb2d) & 0xffffffff
        n ^= (n >> 15)
        return n & 0xffffffff

    def _draw_city_grass(self):
        """Draw a grassy strip with blades along the top of the city ground."""
        top_y = 13 * TILE_SIZE  # top row of the ground
        dark  = (38, 140, 58)
        green = (74, 196, 92)
        blade = (96, 220, 110)
        for tile in self.tile_group:
            if tile.tile_type != 'ground' or tile.rect.y != top_y:
                continue
            sx = tile.rect.x - self.camera_x
            if sx < -TILE_SIZE or sx > SCREEN_WIDTH:
                continue
            # Grass band sitting on top of the ground block.
            pygame.draw.rect(self.screen, dark,  (sx, top_y - 6, TILE_SIZE, 8))
            pygame.draw.rect(self.screen, green, (sx, top_y - 6, TILE_SIZE, 4))
            # A few blades poking up, positioned deterministically per column.
            col = tile.rect.x // TILE_SIZE
            for b in range(4):
                bh = 5 + self._hash(col * 9 + b) % 5
                bx = sx + 4 + b * (TILE_SIZE // 4) + self._hash(col + b) % 4
                pygame.draw.polygon(self.screen, blade,
                                    [(bx, top_y - 6), (bx + 3, top_y - 6),
                                     (bx + 1, top_y - 6 - bh)])

    def _draw_cloud(self, x, y, scale, color):
        w = int(110 * scale)
        h = int(38 * scale)
        pygame.draw.ellipse(self.screen, color, (x, y, w, h))
        pygame.draw.ellipse(self.screen, color, (x + w * 0.18, y - h * 0.4, w * 0.7, h))
        pygame.draw.ellipse(self.screen, color, (x + w * 0.45, y - h * 0.2, w * 0.6, h))

    def _draw_hud(self):
        # Modern translucent stat cards laid out along the top.
        low_time = max(0, self.timer) <= 50
        if low_time and (pygame.time.get_ticks() // 300) % 2 == 0:
            time_color = (255, 90, 90)
        elif low_time:
            time_color = (255, 150, 120)
        else:
            time_color = (235, 240, 255)

        cards = [
            ('SCORE', f"{self.score:06d}", (255, 255, 255), None),
            ('COINS', f"{self.coins}",     (255, 215, 70),  'coin'),
            ('LEVEL', f"{self.level_num}", (120, 215, 255), None),
            ('TIME',  f"{max(0, self.timer)}", time_color,  None),
        ]

        x, y, h = 18, 14, 52
        for label, value, color, icon in cards:
            w = self._measure_card(label, value, icon)
            self._draw_hud_card(x, y, w, h, label, value, color, icon)
            if label == 'SCORE':
                self._hud_score_x = x
            elif label == 'COINS':
                self._hud_coins_x = x
            x += w + 10

        # Where the Q / Ultimate skill cards sit (just under the HUD cards).
        self._hud_skill_y = y + h + 6

        self._draw_lives_card(y, h)

    def _measure_card(self, label, value, icon):
        lbl_w = self.font_small.size(label)[0]
        val_w = self.font_hud.size(value)[0]
        icon_w = 24 if icon else 0
        return max(lbl_w, val_w + icon_w) + 24

    def _draw_hud_card(self, x, y, w, h, label, value, value_color, icon=None):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        # One uniform navy-blue highlight across the whole card (top included).
        pygame.draw.rect(panel, (30, 52, 122, 225), (0, 0, w, h), border_radius=11)
        pygame.draw.rect(panel, (120, 160, 240, 170), (0, 0, w, h), width=2,
                         border_radius=11)
        self.screen.blit(panel, (x, y))

        lbl = self.font_small.render(label, True, (175, 198, 240))
        self.screen.blit(lbl, (x + 12, y + 6))

        vx = x + 12
        if icon == 'coin':
            frame = (pygame.time.get_ticks() // 250) % 2
            coin = self.sprites.items['coin1'] if frame == 0 else self.sprites.items['coin2']
            self.screen.blit(pygame.transform.scale(coin, (18, 18)), (vx, y + 27))
            vx += 24
        val = self.font_hud.render(value, True, value_color)
        self.screen.blit(val, (vx, y + 27))

    def _draw_lives_card(self, y, h):
        value = "x INF" if self.infinite_lives else f"x {self.lives}"
        val_w = self.font_hud.size(value)[0]
        w = val_w + 24 + 22  # heart + spacing + value
        x = SCREEN_WIDTH - w - 18

        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 52, 122, 225), (0, 0, w, h), border_radius=11)
        pygame.draw.rect(panel, (120, 160, 240, 170), (0, 0, w, h), width=2,
                         border_radius=11)
        self.screen.blit(panel, (x, y))

        lbl = self.font_small.render("LIVES", True, (175, 198, 240))
        self.screen.blit(lbl, (x + 12, y + 6))

        self._draw_heart(x + 12, y + 28, 18)
        val = self.font_hud.render(value, True, (255, 255, 255))
        self.screen.blit(val, (x + 12 + 24, y + 27))

    def _draw_heart(self, x, y, s):
        """Draw a small heart with its top edge at y, fitting in an s x s box."""
        r = s // 4
        red, dark = (235, 60, 80), (150, 25, 45)
        pygame.draw.circle(self.screen, red, (x + r, y + r), r)
        pygame.draw.circle(self.screen, red, (x + s - r, y + r), r)
        pygame.draw.polygon(self.screen, red,
                            [(x, y + r), (x + s, y + r), (x + s // 2, y + s)])
        # A soft white glint for a bit of polish.
        pygame.draw.circle(self.screen, (255, 180, 195), (x + r - 1, y + r - 2), max(1, r // 3))

    def _draw_flagpole_and_castle(self):
        px = self.flagpole_x - self.camera_x
        pygame.draw.rect(self.screen, (200, 200, 200), (px + 18, self.flagpole_y, 4, 360))
        pygame.draw.circle(self.screen, (220, 180, 50), (int(px + 20), self.flagpole_y), 8)
        self.screen.blit(self.sprites.flag, (px - 20, self.flag_y))

        cx = self.castle_x - self.camera_x
        pygame.draw.rect(self.screen, (160, 60, 40), (cx,      TILE_SIZE * 10, 140, TILE_SIZE * 3))
        pygame.draw.rect(self.screen, (130, 40, 20), (cx + 20, TILE_SIZE * 9,   30, TILE_SIZE))
        pygame.draw.rect(self.screen, (130, 40, 20), (cx + 90, TILE_SIZE * 9,   30, TILE_SIZE))
        pygame.draw.rect(self.screen, (10,  10, 10), (cx + 50, TILE_SIZE * 11,  40, TILE_SIZE * 2))
        pygame.draw.rect(self.screen, (0, 0, 0), (cx,      TILE_SIZE * 10, 140, TILE_SIZE * 3), 2)
        pygame.draw.rect(self.screen, (0, 0, 0), (cx + 20, TILE_SIZE * 9,   30, TILE_SIZE), 2)
        pygame.draw.rect(self.screen, (0, 0, 0), (cx + 90, TILE_SIZE * 9,   30, TILE_SIZE), 2)

    def _draw_world(self):
        self._draw_background(self.camera_x)
        if not self.is_boss:
            self._draw_flagpole_and_castle()
        for tile     in self.tile_group:     tile.draw(self.screen, self.camera_x)
        if self.theme.get('city'):
            self._draw_city_grass()
        for hazard   in self.hazard_group:   hazard.draw(self.screen, self.camera_x)
        for coin     in self.coin_group:     coin.draw(self.screen, self.camera_x)
        for item     in self.item_group:     item.draw(self.screen, self.camera_x)
        for enemy    in self.enemy_group:    enemy.draw(self.screen, self.camera_x)
        if self.is_boss and self.boss is not None:
            self.boss.draw(self.screen, self.camera_x)
        for proj     in self.projectile_group: proj.draw(self.screen, self.camera_x)
        self.player.draw(self.screen, self.camera_x)
        if self.is_boss and self.skills is not None:
            self.skills.draw_world(self.screen, self.camera_x)
        for particle in self.particle_group: particle.draw(self.screen, self.camera_x)
        self._draw_hud()
        if self.is_boss and self.boss is not None and not self.boss.is_dead:
            self._draw_boss_health()
        if self.is_boss and self.skills is not None:
            self.skills.draw_hud(self.screen, self._hud_score_x,
                                 self._hud_coins_x, self._hud_skill_y,
                                 self.font_small)
            self.render_shake = self.skills.camera_shake_offset()

    def _draw_boss_health(self):
        boss = self.boss
        bar_w, bar_h = 360, 18
        x = SCREEN_WIDTH // 2 - bar_w // 2
        y = 84
        label = self.font_hud.render(self._boss_name(), True, (255, 90, 90))
        self.screen.blit(label, (x, y - 24))
        pygame.draw.rect(self.screen, (20, 20, 30), (x - 3, y - 3, bar_w + 6, bar_h + 6),
                         border_radius=6)
        ratio = max(0.0, boss.hp / boss.max_hp)
        pygame.draw.rect(self.screen, (60, 20, 20), (x, y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.screen, (230, 50, 50),
                         (x, y, int(bar_w * ratio), bar_h), border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_w, bar_h), 2, border_radius=5)
        hp_txt = self.font_small.render(f"{boss.hp}/{boss.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_txt, (x + bar_w // 2 - hp_txt.get_width() // 2, y))

    def _dim(self, alpha=150):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_title_banner(self, text, y, color=(255, 220, 0), big=True):
        font = self.font_big if big else self.font_title
        shadow = font.render(text, True, (0, 0, 0))
        main   = font.render(text, True, color)
        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - main.get_width() // 2 + 4, y + 4))
        self.screen.blit(main,   (SCREEN_WIDTH // 2 - main.get_width() // 2, y))

    def draw_menu(self):
        self.menu_scroll += 0.6
        self._draw_background(self.menu_scroll)
        self._dim(60)

        bob = math.sin(pygame.time.get_ticks() * 0.003) * 8
        self._draw_title_banner("SUPER", 90 + int(bob), color=(255, 70, 70))
        self._draw_title_banner("JIN", 165 + int(bob), color=(255, 220, 0))

        hs = self.font_menu.render(f"HIGH SCORE  {self.high_score:06d}", True, (255, 220, 90))
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 250))

        mp = self._logical_mouse()
        for b in (self.btn_play, self.btn_shop, self.btn_menu_settings, self.btn_exit):
            b.update(mp)
            b.draw(self.screen)

        tip = self.font_small.render("v2.5.0  -  Enhanced Edition", True, (220, 220, 230))
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, 560))

    def draw_modeselect(self):
        self.menu_scroll += 0.6
        self._draw_background(self.menu_scroll)
        self._dim(110)

        self._draw_title_banner("CHOOSE MODE", 70, color=(255, 220, 0), big=True)

        mp = self._logical_mouse()
        self.btn_mode_endless.update(mp)
        self.btn_mode_pvp.update(mp)
        self.btn_mode_back.update(mp)
        self.btn_mode_endless.draw(self.screen)
        self.btn_mode_pvp.draw(self.screen)

        # Endless card: Mario logo + label.
        mario = pygame.transform.scale(self.sprites.player_small['idle'], (88, 110))
        self._draw_mode_card_content(
            self.btn_mode_endless, mario, "ENDLESS",
            "Classic run - bosses every", "4th stage", (180, 230, 255))

        # PvP / Boss-Rush card: Mech logo + label.
        mech = pygame.transform.scale(self.sprites.boss_city['walk1'], (118, 122))
        self._draw_mode_card_content(
            self.btn_mode_pvp, mech, "PvP  -  BOSS RUSH",
            "10 bosses, each smarter", "and deadlier", (255, 200, 200))

        self.btn_mode_back.draw(self.screen)

    def _draw_mode_card_content(self, btn, logo, title, line1, line2, color):
        r = btn.rect
        # Logo near the top of the card.
        self.screen.blit(logo, (r.centerx - logo.get_width() // 2, r.y + 24))
        # Title.
        t = self.font_menu.render(title, True, (255, 255, 255))
        if t.get_width() > r.width - 16:
            t = pygame.transform.smoothscale(
                t, (r.width - 16, t.get_height()))
        self.screen.blit(t, (r.centerx - t.get_width() // 2, r.bottom - 70))
        # Two-line description.
        for i, ln in enumerate((line1, line2)):
            d = self.font_small.render(ln, True, color)
            self.screen.blit(d, (r.centerx - d.get_width() // 2, r.bottom - 42 + i * 18))

    def _draw_card(self, cx, cy, w, h, accent, fill=(18, 21, 36), alpha=215):
        """Draw a modern rounded translucent panel with an accent border."""
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (cx, cy)
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*fill, alpha), (0, 0, w, h), border_radius=16)
        self.screen.blit(panel, rect.topleft)
        pygame.draw.rect(self.screen, accent, rect, width=3, border_radius=16)
        pygame.draw.rect(self.screen, accent, (rect.x + 14, rect.y + 12, w - 28, 5),
                         border_radius=3)
        return rect

    def _boss_name(self):
        if self.boss_name:
            return self.boss_name
        return "MEGA MECH" if self.is_boss and self.theme.get('city') else "GORTHRAX"

    def draw_intro(self):
        self._draw_background(self.camera_x)
        self._dim(150)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 - 10
        if self.is_boss:
            accent = (255, 80, 80)
            rect = self._draw_card(cx, cy, 560, 366, accent)
            self._draw_title_banner("BOSS BATTLE", rect.y + 28, color=accent,
                                    big=False)
            nm = self.font_title.render(self._boss_name(), True, (255, 220, 130))
            self.screen.blit(nm, (cx - nm.get_width() // 2, rect.y + 96))
            if self.mode == MODE_PVP:
                sub = self.font_menu.render(
                    f"PvP   Level {self.level_num} / {pvp_level_count()}",
                    True, (255, 170, 170))
            else:
                sub = self.font_menu.render("Stomp it to win!", True, (235, 235, 245))
            self.screen.blit(sub, (cx - sub.get_width() // 2, rect.y + 152))

            # Remind the player their character's skills are available here.
            if self.skills is not None:
                q_name = self.skills.q_def['name']
                u_name = self.skills.ult_def['name']
                hint1 = self.font_small.render(
                    f"Q  -  {q_name}        E  -  {u_name}", True, (150, 220, 255))
                self.screen.blit(hint1, (cx - hint1.get_width() // 2, rect.y + 204))
                hint2 = self.font_small.render(
                    "Press Q for your Skill and E for your Ultimate!",
                    True, (200, 210, 230))
                self.screen.blit(hint2, (cx - hint2.get_width() // 2, rect.y + 230))
        else:
            accent = tuple(self.theme.get('sun', (255, 220, 0)))[:3]
            rect = self._draw_card(cx, cy, 560, 300, accent)
            self._draw_title_banner(f"WORLD {self.level.world_name}", rect.y + 36,
                                    color=(255, 255, 255))
            sub = self.font_menu.render(self.theme['name'], True, (185, 212, 255))
            self.screen.blit(sub, (cx - sub.get_width() // 2, rect.y + 118))
            lvl = self.font_menu.render(f"Level {self.level_num}", True, (255, 255, 255))
            self.screen.blit(lvl, (cx - lvl.get_width() // 2, rect.y + 162))
            icon = pygame.transform.scale(self.sprites.player_small['idle'], (26, 32))
            lives_txt = self.font_menu.render(f"x  {self.lives}", True, (255, 255, 255))
            total_w = icon.get_width() + 8 + lives_txt.get_width()
            ix = cx - total_w // 2
            self.screen.blit(icon, (ix, rect.y + 206))
            self.screen.blit(lives_txt, (ix + icon.get_width() + 8, rect.y + 208))

        self._draw_intro_progress(rect, accent)

    def _draw_intro_progress(self, rect, accent):
        frac = 1.0
        if getattr(self, 'intro_timer_max', 0) > 0:
            frac = 1.0 - max(0, self.intro_timer) / self.intro_timer_max
        bw = rect.width - 80
        bx = rect.centerx - bw // 2
        by = rect.bottom - 30
        hint = self.font_small.render("Get ready...", True, (210, 215, 230))
        self.screen.blit(hint, (rect.centerx - hint.get_width() // 2, by - 24))
        pygame.draw.rect(self.screen, (48, 54, 74), (bx, by, bw, 8), border_radius=4)
        pygame.draw.rect(self.screen, accent, (bx, by, int(bw * frac), 8), border_radius=4)

    def draw_pause(self):
        self._draw_world()
        self._dim(150)
        self._draw_title_banner("PAUSED", 110, color=(255, 255, 255))
        mp = self._logical_mouse()
        for b in (self.btn_resume, self.btn_settings, self.btn_mainmenu):
            b.update(mp)
            b.draw(self.screen)
        hint = self.font_small.render(
            "Move: A / D    Jump: Space    Dash: Shift    "
            "Skill: Q    Ultimate: E", True, (200, 208, 228))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT - 40))

    def draw_settings(self):
        if self.settings_return == MENU:
            self._draw_background(self.menu_scroll)
        else:
            self._draw_world()
        self._dim(170)
        self._draw_title_banner("SETTINGS", 22, color=(255, 220, 0), big=False)

        cx = SCREEN_WIDTH // 2
        left_cx, right_cx = cx - 230, cx + 230

        ah = self.font_menu.render("AUDIO", True, (255, 230, 120))
        self.screen.blit(ah, (left_cx - ah.get_width() // 2, 84))
        gh = self.font_menu.render("GAME", True, (255, 230, 120))
        self.screen.blit(gh, (right_cx - gh.get_width() // 2, 84))

        self.slider_master.draw(self.screen)
        self.slider_music.draw(self.screen)
        self.slider_sfx.draw(self.screen)

        mp = self._logical_mouse()
        self.btn_music_toggle.label = self._music_label()
        self.btn_display.label = self._display_label()
        self.btn_lives.label = self._lives_label()
        self.btn_god.label = self._god_label()
        for b in (self.btn_music_toggle, self.btn_lives, self.btn_display,
                  self.btn_reset, self.btn_god, self.btn_controls,
                  self.btn_tos, self.btn_legal, self.btn_back):
            b.update(mp)
            b.draw(self.screen)

        if self.reset_confirm:
            self._draw_reset_confirm()

    def draw_controls(self):
        """A dedicated, organized 'How to Play' screen. Lists movement, skills
        and system keys. Built to grow as more skills are added later."""
        if self.settings_return == MENU:
            self._draw_background(self.menu_scroll)
        else:
            self._draw_world()
        self._dim(185)
        self._draw_title_banner("HOW TO PLAY", 28, color=(255, 220, 0), big=False)

        cx = SCREEN_WIDTH // 2
        panel = self._draw_card(cx, 316, 660, 430, (120, 160, 240))

        # (section title, [(action, keys, optional note), ...])
        sections = [
            ("MOVEMENT", [
                ("Move Left / Right", "Arrow Keys   or   A / D", None),
                ("Jump  (double jump)", "Space  /  W  /  Up", None),
                ("Duck  /  Fast Drop", "Down  /  S", None),
            ]),
            ("SKILLS", [
                ("Dash", "Left Shift   or   Right Shift",
                 "Instantly dash in the direction you're facing."),
                ("Skill 1", "Q",
                 "Your hero's quick skill (5s). Boss battles only."),
                ("Ultimate", "E",
                 "Your hero's powerful Ultimate (30s). Boss battles only."),
            ]),
            ("SYSTEM", [
                ("Pause", "Esc", None),
                ("Fullscreen", "F11", None),
            ]),
        ]

        lx = panel.x + 34
        rx = panel.right - 34
        y = panel.y + 24
        for title, rows in sections:
            hdr = self.font_menu.render(title, True, (255, 230, 120))
            self.screen.blit(hdr, (lx, y))
            y += 34
            for action, keys, note in rows:
                a = self.font_small.render(action, True, (235, 240, 250))
                self.screen.blit(a, (lx + 12, y))
                k = self.font_small.render(keys, True, (150, 220, 255))
                self.screen.blit(k, (rx - k.get_width(), y))
                y += 24
                if note:
                    nt = self.font_small.render(note, True, (165, 175, 200))
                    self.screen.blit(nt, (lx + 12, y))
                    y += 22
            y += 12

        mp = self._logical_mouse()
        self.btn_controls_back.update(mp)
        self.btn_controls_back.draw(self.screen)

    def _draw_reset_confirm(self):
        self._dim(170)
        bw, bh = 580, 300
        box = pygame.Rect(SCREEN_WIDTH // 2 - bw // 2,
                          SCREEN_HEIGHT // 2 - bh // 2, bw, bh)
        pygame.draw.rect(self.screen, (40, 18, 22), box, border_radius=16)
        pygame.draw.rect(self.screen, (200, 90, 90), box, width=3, border_radius=16)
        self._draw_title_banner("RESET PROGRESS?", box.y + 24,
                                color=(255, 120, 120), big=False)
        lines = [
            "This erases your coins, owned characters",
            "and skins, and your high score.",
            "This cannot be undone.",
        ]
        for i, ln in enumerate(lines):
            t = self.font_small.render(ln, True, (235, 220, 220))
            self.screen.blit(t, (box.centerx - t.get_width() // 2, box.y + 92 + i * 26))
        mp = self._logical_mouse()
        for b in (self.btn_reset_yes, self.btn_reset_no):
            b.update(mp)
            b.draw(self.screen)

    def _draw_document(self, title, lines, scroll):
        """Render a scrollable block of text (used by TOS and Legal screens)."""
        if self.settings_return == MENU:
            self._draw_background(self.menu_scroll)
        else:
            self._draw_world()
        self._dim(190)
        self._draw_title_banner(title, 40, color=(255, 220, 0), big=False)

        # The reading viewport (text is clipped to this region while scrolling).
        view = pygame.Rect(SCREEN_WIDTH // 2 - 340, 110, 680, 380)
        pygame.draw.rect(self.screen, (12, 14, 30), view, border_radius=10)
        pygame.draw.rect(self.screen, (90, 100, 150), view, width=2, border_radius=10)

        line_h = 22
        content_h = len(lines) * line_h
        self._doc_max_scroll = max(0.0, content_h - (view.height - 24))
        scroll = max(0.0, min(scroll, self._doc_max_scroll))

        prev_clip = self.screen.get_clip()
        self.screen.set_clip(view)
        y = view.y + 12 - int(scroll)
        for line in lines:
            if y + line_h >= view.y and y <= view.bottom:
                if line and line == line.upper() and not line.startswith(" ") \
                        and len(line) > 2 and not line[0].isdigit():
                    color = (255, 220, 120)  # section headings
                elif line[:2].strip().isdigit() or (line and line[0].isdigit()):
                    color = (160, 220, 255)  # numbered clauses
                else:
                    color = (220, 225, 240)
                txt = self.font_small.render(line, True, color)
                self.screen.blit(txt, (view.x + 18, y))
            y += line_h
        self.screen.set_clip(prev_clip)

        # Scrollbar indicator on the right edge of the viewport.
        if self._doc_max_scroll > 0:
            track = pygame.Rect(view.right - 10, view.y + 6, 5, view.height - 12)
            pygame.draw.rect(self.screen, (40, 45, 70), track, border_radius=3)
            frac = view.height / (content_h + 24)
            bar_h = max(24, int(track.height * frac))
            bar_y = track.y + int((track.height - bar_h) *
                                  (scroll / self._doc_max_scroll))
            pygame.draw.rect(self.screen, (140, 160, 220),
                             (track.x, bar_y, track.width, bar_h), border_radius=3)

        hint = self.font_small.render(
            "Scroll: Mouse Wheel / Up-Down arrows", True, (180, 185, 205))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, view.bottom + 6))

        mp = self._logical_mouse()
        self.btn_doc_back.update(mp)
        self.btn_doc_back.draw(self.screen)
        return scroll

    def draw_tos(self):
        self.tos_scroll = self._draw_document(
            "TERMS OF SERVICE", TOS_TEXT, self.tos_scroll)

    def draw_legal(self):
        self.legal_scroll = self._draw_document(
            "LEGAL", LEGAL_TEXT, self.legal_scroll)

    def draw_clear(self):
        self._draw_world()
        self._dim(90)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 - 20
        if self.cleared_boss:
            accent, title = (255, 120, 120), "BOSS DEFEATED!"
        else:
            accent, title = (255, 226, 72), "STAGE CLEAR!"

        card_w, card_h = 600, 250
        rect = self._draw_card(cx, cy, card_w, card_h, accent)

        # Render the title and shrink it to fit inside the card if needed, so
        # long titles like "BOSS DEFEATED!" never spill outside the box.
        main = self.font_big.render(title, True, accent)
        shadow = self.font_big.render(title, True, (0, 0, 0))
        max_w = card_w - 70
        if main.get_width() > max_w:
            s = max_w / main.get_width()
            size = (int(main.get_width() * s), int(main.get_height() * s))
            main = pygame.transform.smoothscale(main, size)
            shadow = pygame.transform.smoothscale(shadow, size)
        ty = rect.y + 44
        self.screen.blit(shadow, (cx - main.get_width() // 2 + 3, ty + 3))
        self.screen.blit(main, (cx - main.get_width() // 2, ty))

        bonus = self.font_menu.render(
            f"+{max(0, self.timer) * 10} time bonus", True, (255, 255, 255))
        self.screen.blit(bonus, (cx - bonus.get_width() // 2, rect.y + 150))
        nxt = self.font_small.render(
            "Next level starting...   (Enter to skip)", True, (225, 230, 245))
        self.screen.blit(nxt, (cx - nxt.get_width() // 2, rect.y + 196))

    def draw_gameover(self):
        self._draw_background(self.camera_x)
        self._dim(190)
        if self.victory:
            self._draw_title_banner("YOU WIN!", 110, color=(120, 255, 140))
            sub = self.font_menu.render("All 10 bosses defeated!", True, (255, 220, 90))
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 168))
        else:
            self._draw_title_banner("GAME OVER", 110, color=(220, 40, 40))
        sc = self.font_menu.render(f"Score: {self.score:06d}", True, (255, 255, 255))
        self.screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, 200))
        hs = self.font_menu.render(f"High Score: {self.high_score:06d}", True, (255, 220, 90))
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 236))
        coins_txt = self.font_menu.render(
            f"Coins earned: +{self.coins}", True, (255, 215, 70))
        self.screen.blit(coins_txt, (SCREEN_WIDTH // 2 - coins_txt.get_width() // 2, 272))
        if self.new_record:
            flash = (pygame.time.get_ticks() // 250) % 2 == 0
            if flash:
                nr = self.font_menu.render("NEW HIGH SCORE!", True, (120, 255, 140))
                self.screen.blit(nr, (SCREEN_WIDTH // 2 - nr.get_width() // 2, 308))
        mp = self._logical_mouse()
        for b in (self.btn_retry, self.btn_go_menu):
            b.update(mp)
            b.draw(self.screen)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            # Translate real window mouse coords into the game's logical space
            # so buttons and sliders work regardless of the window size.
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP):
                event = pygame.event.Event(
                    event.type, {**event.dict, "pos": self._to_logical(event.pos)}
                )

            if event.type == pygame.USEREVENT + 10:
                pygame.time.set_timer(pygame.USEREVENT + 10, 0)
                play_coin_second_tone()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self._toggle_fullscreen()
                continue

            if self.state == MENU:
                self._events_menu(event)
            elif self.state == MODESELECT:
                self._events_modeselect(event)
            elif self.state == PLAYING:
                self._events_playing(event)
            elif self.state == PAUSED:
                self._events_paused(event)
            elif self.state == SETTINGS:
                self._events_settings(event)
            elif self.state == CONTROLS:
                self._events_controls(event)
            elif self.state == SHOP:
                self._events_shop(event)
            elif self.state in (TOS, LEGAL):
                self._events_document(event)
            elif self.state == CLEAR:
                self._events_clear(event)
            elif self.state == GAMEOVER:
                self._events_gameover(event)
            elif self.state == INTRO:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.intro_timer = 0

    def _events_menu(self, event):
        if self.btn_play.is_clicked(event):
            sfx_menu_select()
            self.state = MODESELECT
        elif self.btn_menu_settings.is_clicked(event):
            sfx_menu_select()
            self.settings_return = MENU
            self.slider_master.value = settings.master_volume
            self.slider_music.value = settings.music_volume
            self.slider_sfx.value   = settings.sfx_volume
            self.state = SETTINGS
        elif self.btn_shop.is_clicked(event):
            sfx_menu_select()
            self.state = SHOP
        elif self.btn_exit.is_clicked(event):
            self._quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            sfx_menu_select()
            self.state = MODESELECT

    def _events_modeselect(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            self.state = MENU
            return
        if self.btn_mode_endless.is_clicked(event):
            sfx_menu_select()
            self.mode = MODE_ENDLESS
            self.start_new_game()
        elif self.btn_mode_pvp.is_clicked(event):
            sfx_menu_select()
            self.mode = MODE_PVP
            self.start_new_game()
        elif self.btn_mode_back.is_clicked(event):
            sfx_menu_select()
            self.state = MENU

    def _events_playing(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.player.register_jump_press()
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.player.try_dash()
            elif event.key == pygame.K_q:
                if self.skills is not None:
                    self.skills.activate_q()
            elif event.key == pygame.K_e:
                if self.skills is not None:
                    self.skills.activate_ult()
            elif event.key == pygame.K_ESCAPE:
                self.state = PAUSED
                sfx_pause()
                self._save_all()

    def _events_paused(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = PLAYING
            sfx_unpause()
            return
        if self.btn_resume.is_clicked(event):
            sfx_unpause()
            self.state = PLAYING
        elif self.btn_settings.is_clicked(event):
            sfx_menu_select()
            self.settings_return = PAUSED
            self.slider_master.value = settings.master_volume
            self.slider_music.value = settings.music_volume
            self.slider_sfx.value   = settings.sfx_volume
            self.state = SETTINGS
        elif self.btn_mainmenu.is_clicked(event):
            sfx_menu_select()
            self.state = MENU
            start_music(0)

    def _events_settings(self, event):
        if self.reset_confirm:
            self._events_reset_confirm(event)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            settings.save()
            self.state = self.settings_return
            return
        if self.slider_master.handle_event(event):
            settings.master_volume = self.slider_master.value
            settings.clamp()
            update_music_volume()
        if self.slider_music.handle_event(event):
            settings.music_volume = self.slider_music.value
            settings.clamp()
            update_music_volume()
        if self.slider_sfx.handle_event(event):
            settings.sfx_volume = self.slider_sfx.value
            settings.clamp()
        if event.type == pygame.MOUSEBUTTONUP:
            # Persist after a slider drag finishes.
            settings.save()
        if self.btn_music_toggle.is_clicked(event):
            settings.music_enabled = not settings.music_enabled
            sfx_menu_select()
            if settings.music_enabled:
                start_music(self.theme_index())
            else:
                stop_music()
            settings.save()
        elif self.btn_lives.is_clicked(event):
            sfx_menu_select()
            self._cycle_starting_lives()
            settings.save()
        elif self.btn_display.is_clicked(event):
            sfx_menu_select()
            self._cycle_display_mode()
            settings.save()
        elif self.btn_reset.is_clicked(event):
            sfx_menu_select()
            self.reset_confirm = True
        elif self.btn_god.is_clicked(event):
            sfx_menu_select()
            settings.god_mode = not settings.god_mode
            settings.save()
        elif self.btn_controls.is_clicked(event):
            sfx_menu_select()
            self.state = CONTROLS
        elif self.btn_tos.is_clicked(event):
            sfx_menu_select()
            self.tos_scroll = 0.0
            self.state = TOS
        elif self.btn_legal.is_clicked(event):
            sfx_menu_select()
            self.legal_scroll = 0.0
            self.state = LEGAL
        elif self.btn_back.is_clicked(event):
            sfx_menu_select()
            settings.save()
            self.state = self.settings_return

    def _events_controls(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            self.state = SETTINGS
            return
        if self.btn_controls_back.is_clicked(event):
            sfx_menu_select()
            self.state = SETTINGS

    def _cycle_starting_lives(self):
        order = [3, 5, -1]
        try:
            i = order.index(settings.starting_lives)
        except ValueError:
            i = 0
        settings.starting_lives = order[(i + 1) % len(order)]

    def _events_reset_confirm(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            self.reset_confirm = False
            return
        if self.btn_reset_no.is_clicked(event):
            sfx_menu_select()
            self.reset_confirm = False
        elif self.btn_reset_yes.is_clicked(event):
            sfx_menu_select()
            self._reset_progress()
            self.reset_confirm = False

    def _reset_progress(self):
        self.progress = default_progress()
        self.wallet = 0
        self.high_score = 0
        self.prev_high = 0
        save_high_score(0)
        save_progress(self.progress)
        self.apply_selected_character()

    def _events_shop(self, event):
        if self.shop.handle_event(event):
            self.persist_progress()
            self.state = MENU

    def _events_document(self, event):
        """Shared event handling for the TOS / Legal reading screens."""
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            self.state = SETTINGS
            return
        if self.btn_doc_back.is_clicked(event):
            sfx_menu_select()
            self.state = SETTINGS
            return

        scroll_attr = 'tos_scroll' if self.state == TOS else 'legal_scroll'
        cur = getattr(self, scroll_attr)
        if event.type == pygame.MOUSEWHEEL:
            cur -= event.y * 40
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                cur += 40
            elif event.key == pygame.K_UP:
                cur -= 40
            elif event.key == pygame.K_PAGEDOWN:
                cur += 240
            elif event.key == pygame.K_PAGEUP:
                cur -= 240
        cur = max(0.0, min(cur, self._doc_max_scroll))
        setattr(self, scroll_attr, cur)

    def _events_clear(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.clear_timer = 0

    def _events_gameover(self, event):
        if self.btn_retry.is_clicked(event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            sfx_menu_select()
            self.start_new_game()
            self._start_level_music()
        elif self.btn_go_menu.is_clicked(event):
            sfx_menu_select()
            self.state = MENU
            start_music(0)

    def _build_display_modes(self):
        """Fullscreen plus windowed sizes that keep the game's aspect ratio."""
        aspect = SCREEN_WIDTH / SCREEN_HEIGHT
        modes = [("Fullscreen", "fullscreen")]

        try:
            info = pygame.display.Info()
            desk_w, desk_h = info.current_w, info.current_h
        except Exception:
            desk_w, desk_h = 1920, 1080

        for height in (600, 720, 864, 1080):
            width = round(height * aspect)
            # Only offer windowed sizes that comfortably fit on the desktop.
            if width <= desk_w - 40 and height <= desk_h - 80:
                modes.append((f"{width} x {height}", (width, height)))

        return modes

    def _apply_display_mode(self):
        name, mode = self.display_modes[settings.display_mode]
        if mode == "fullscreen":
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(mode)
        self._recompute_scale()

    def _recompute_scale(self):
        win_w, win_h = self.window.get_size()
        self._scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        dst_w = int(SCREEN_WIDTH * self._scale)
        dst_h = int(SCREEN_HEIGHT * self._scale)
        self._dst = pygame.Rect((win_w - dst_w) // 2, (win_h - dst_h) // 2, dst_w, dst_h)

    def _to_logical(self, pos):
        """Map a real window coordinate to the game's logical coordinate space."""
        if self._scale <= 0:
            return pos
        return ((pos[0] - self._dst.x) / self._scale,
                (pos[1] - self._dst.y) / self._scale)

    def _logical_mouse(self):
        return self._to_logical(pygame.mouse.get_pos())

    def _present(self):
        """Scale the offscreen render surface onto the actual window."""
        self.window.fill((0, 0, 0))
        scaled = pygame.transform.scale(self.render, self._dst.size)
        sx = self._dst.x + int(self.render_shake[0] * self._scale)
        sy = self._dst.y + int(self.render_shake[1] * self._scale)
        self.window.blit(scaled, (sx, sy))

    def _cycle_display_mode(self):
        settings.display_mode = (settings.display_mode + 1) % len(self.display_modes)
        self._apply_display_mode()

    def _toggle_fullscreen(self):
        if self.display_modes[settings.display_mode][1] == "fullscreen":
            # Switch to the first available windowed mode (if any).
            for i, (_, mode) in enumerate(self.display_modes):
                if mode != "fullscreen":
                    settings.display_mode = i
                    break
        else:
            settings.display_mode = 0
        self._apply_display_mode()

    def _quit(self):
        try:
            save_high_score(max(self.high_score, self.score))
        except Exception:
            pass
        try:
            self.persist_progress()
        except Exception:
            pass
        try:
            settings.save()
        except Exception:
            pass
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self._handle_events()
            self.render_shake = (0, 0)

            if self.state == PLAYING:
                self.player.handle_input()
                self.update_playing()
            elif self.state == CLEAR:
                self.update_clear()
            elif self.state == INTRO:
                self.intro_timer -= 1
                if self.intro_timer <= 0:
                    self.state = PLAYING
                    self._start_level_music()

            if self.state == MENU:
                self.draw_menu()
            elif self.state == MODESELECT:
                self.draw_modeselect()
            elif self.state == INTRO:
                self.draw_intro()
            elif self.state == PLAYING:
                self._draw_world()
            elif self.state == PAUSED:
                self.draw_pause()
            elif self.state == SETTINGS:
                self.draw_settings()
            elif self.state == CONTROLS:
                self.draw_controls()
            elif self.state == SHOP:
                self.shop.draw()
            elif self.state == TOS:
                self.draw_tos()
            elif self.state == LEGAL:
                self.draw_legal()
            elif self.state == CLEAR:
                self.draw_clear()
            elif self.state == GAMEOVER:
                self.draw_gameover()

            self._present()
            pygame.display.flip()
            self.clock.tick(FPS)
