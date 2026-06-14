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
from levels import build_level, build_boss_level, is_boss_level, THEMES
from highscore import load_high_score, save_high_score
import sounds
from sounds import (
    play_coin_second_tone, sfx_powerup, sfx_powerup_spawn, sfx_stomp,
    sfx_clear, sfx_menu_select, sfx_pause, sfx_unpause, sfx_level_start,
    sfx_hazard, sfx_firework, sfx_coin, start_music, stop_music, update_music_volume,
)
from entities import Player, Enemy, Item, Tile, Particle


MENU, INTRO, PLAYING, PAUSED, SETTINGS, CLEAR, GAMEOVER = (
    'menu', 'intro', 'playing', 'paused', 'settings', 'clear', 'gameover'
)


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)
        except Exception:
            pass

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Jin  v2.1.0")
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
        self.level_num = 1
        self.high_score = load_high_score()
        self.prev_high  = self.high_score
        self.new_record = False

        self.state = MENU

        self.clouds = [(random.randint(0, 4000), random.randint(40, 200),
                        random.uniform(0.4, 1.0)) for _ in range(14)]
        self.stars  = [(random.randint(0, SCREEN_WIDTH), random.randint(0, 360),
                        random.uniform(0.3, 1.0)) for _ in range(70)]
        self.menu_scroll = 0.0

        self.theme = THEMES[0]
        self.level_width = 3800
        self.is_boss = False
        self.boss = None
        self.projectile_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.cleared_boss = False

        self.intro_timer = 0
        self.clear_timer = 0
        self.firework_cd = 0

        self.level = None
        self._build_ui()

        start_music(0)

    def _build_ui(self):
        cx = SCREEN_WIDTH // 2

        self.btn_play = Button(cx, 360, 260, 64, "PLAY", self.font_menu, icon='play',
                               base_color=(30, 120, 60), hover_color=(50, 170, 90))
        self.btn_exit = Button(cx, 440, 260, 64, "EXIT", self.font_menu, icon='exit',
                               base_color=(120, 40, 40), hover_color=(170, 60, 60))

        self.btn_resume   = Button(cx, 250, 280, 60, "RESUME", self.font_menu, icon='play',
                                   base_color=(30, 120, 60), hover_color=(50, 170, 90))
        self.btn_settings = Button(cx, 325, 280, 60, "SETTINGS", self.font_menu, icon='gear')
        self.btn_mainmenu = Button(cx, 400, 280, 60, "MAIN MENU", self.font_menu, icon='home',
                                   base_color=(110, 70, 30), hover_color=(160, 110, 50))

        self.slider_music = Slider(cx - 150, 250, 300, "Music Volume", self.font_small,
                                   value=settings.music_volume)
        self.slider_sfx   = Slider(cx - 150, 340, 300, "Sound Effects", self.font_small,
                                   value=settings.sfx_volume)
        self.btn_music_toggle = Button(cx, 405, 280, 50, self._music_label(), self.font_small)
        self.btn_back = Button(cx, 470, 200, 54, "BACK", self.font_menu)

        self.btn_retry    = Button(cx, 340, 260, 60, "RETRY", self.font_menu, icon='play',
                                   base_color=(30, 120, 60), hover_color=(50, 170, 90))
        self.btn_go_menu  = Button(cx, 415, 260, 60, "MAIN MENU", self.font_menu, icon='home',
                                   base_color=(110, 70, 30), hover_color=(160, 110, 50))

    def _music_label(self):
        return "Music: ON" if settings.music_enabled else "Music: OFF"

    def start_new_game(self):
        self.score     = 0
        self.coins     = 0
        self.lives     = 3
        self.level_num = 1
        self.prev_high = self.high_score
        self.new_record = False
        self.load_level(self.level_num)
        self._enter_intro()

    def load_level(self, level_num):
        self.is_boss = is_boss_level(level_num)
        if self.is_boss:
            self.level = build_boss_level(level_num, self.sprites)
        else:
            self.level = build_level(level_num, self.sprites)
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

        self.player = Player(100, 300, self.sprites)
        self.player_group = pygame.sprite.GroupSingle(self.player)

    def reset_current_level(self):
        self.load_level(self.level_num)
        start_music(self.theme_index())

    def theme_index(self):
        return self.level.theme_index if self.level else 0

    def next_level(self):
        self.level_num += 1
        self.score += 2000
        self.load_level(self.level_num)
        self._enter_intro()

    def _enter_intro(self):
        self.state = INTRO
        self.intro_timer = int(FPS * 2.4)
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
            self.player.die()

        if (self.player.invincible_timer <= 0 and not self.player.is_dead
                and pygame.sprite.spritecollide(self.player, self.hazard_group, False)):
            sfx_hazard()
            self.player.take_damage()

        for coin in pygame.sprite.spritecollide(self.player, self.coin_group, True):
            self.coins += 1
            self.score += 200
            sfx_coin()
            self.particle_group.add(
                Particle.create_score(coin.rect.x, coin.rect.y - 10, "200", self.font_hud)
            )

        for item in pygame.sprite.spritecollide(self.player, self.item_group, False):
            if item.state == "active" and item.item_type == 'mushroom':
                sfx_powerup()
                self.player.is_big = True
                self.score += 1000
                self.particle_group.add(
                    Particle.create_score(item.rect.x, item.rect.y, "1000", self.font_hud)
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
                    Particle.create_score(enemy.rect.x, enemy.rect.y, "200", self.font_hud)
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
                    Particle.create_score(hit.rect.x, hit.rect.y, "500", self.font_hud)
                )

    def _trigger_block_hit(self, tile):
        tile.bump()

        if tile.tile_type == 'question':
            if tile.contains_item == 'coin':
                self.coins += 1
                self.score += 200
                self.item_group.add(Item(tile.rect.x, tile.rect.y, 'coin', self.sprites))
                self.particle_group.add(
                    Particle.create_score(tile.rect.x, tile.rect.y - 20, "200", self.font_hud)
                )
            elif tile.contains_item == 'mushroom':
                sfx_powerup_spawn()
                self.item_group.add(Item(tile.rect.x, tile.rect.y, 'mushroom', self.sprites))
            tile.tile_type     = 'spent'
            tile.contains_item = None

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

    def _handle_boss_combat(self):
        boss = self.boss

        if boss.is_dead:
            if boss.dead_timer <= 0 and not self.stage_clear:
                self.stage_clear = True
                self.score += 5000
                self.particle_group.add(
                    Particle.create_score(boss.rect.centerx, boss.rect.top, "5000", self.font_hud)
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
            stomped = (self.player.vy > 0
                       and self.player.rect.bottom < boss.rect.centery + 6)
            if stomped:
                self.player.vy = -9.5
                defeated = boss.stomp()
                self.score += 300
                self.particle_group.add(
                    Particle.create_score(boss.rect.centerx, boss.rect.top, "300", self.font_hud)
                )
                if defeated:
                    self.particle_group.add(*Particle.create_firework(
                        boss.rect.centerx, boss.rect.centery))
            else:
                self.player.take_damage()

    def _on_game_over(self):
        stop_music()
        self.new_record = self.score > self.prev_high
        if self.score > self.high_score:
            self.high_score = self.score
        save_high_score(self.high_score)
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

        self.handle_collisions()
        self.check_stage_clear()

        if self.score > self.high_score:
            self.high_score = self.score

        if self.player.is_dead:
            self.player.death_timer -= 1
            if self.player.death_timer <= 0:
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

    def _draw_cloud(self, x, y, scale, color):
        w = int(110 * scale)
        h = int(38 * scale)
        pygame.draw.ellipse(self.screen, color, (x, y, w, h))
        pygame.draw.ellipse(self.screen, color, (x + w * 0.18, y - h * 0.4, w * 0.7, h))
        pygame.draw.ellipse(self.screen, color, (x + w * 0.45, y - h * 0.2, w * 0.6, h))

    def _draw_hud(self):
        score_text = self.font_hud.render(
            "MARIO      COINS      WORLD      TIME", True, (255, 255, 255)
        )
        vals_text = self.font_hud.render(
            f"{self.score:06d}      o x {self.coins:02d}      {self.level.world_name}"
            f"        {max(0, self.timer):03d}",
            True, (255, 255, 255),
        )
        self.screen.blit(score_text, (40, 20))
        self.screen.blit(vals_text,  (40, 45))

        frame    = (pygame.time.get_ticks() // 250) % 2
        coin_img = self.sprites.items['coin1'] if frame == 0 else self.sprites.items['coin2']
        self.screen.blit(pygame.transform.scale(coin_img, (16, 16)), (230, 48))

        lives_img = pygame.transform.scale(self.sprites.player_small['idle'], (20, 24))
        self.screen.blit(lives_img, (SCREEN_WIDTH - 120, 25))
        self.screen.blit(
            self.font_hud.render(f"x {self.lives}", True, (255, 255, 255)),
            (SCREEN_WIDTH - 90, 25),
        )
        hint = self.font_small.render("Esc = Pause", True, (255, 255, 255))
        self.screen.blit(hint, (SCREEN_WIDTH - 110, 52))

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
        for hazard   in self.hazard_group:   hazard.draw(self.screen, self.camera_x)
        for coin     in self.coin_group:     coin.draw(self.screen, self.camera_x)
        for item     in self.item_group:     item.draw(self.screen, self.camera_x)
        for enemy    in self.enemy_group:    enemy.draw(self.screen, self.camera_x)
        if self.is_boss and self.boss is not None:
            self.boss.draw(self.screen, self.camera_x)
        for proj     in self.projectile_group: proj.draw(self.screen, self.camera_x)
        self.player.draw(self.screen, self.camera_x)
        for particle in self.particle_group: particle.draw(self.screen, self.camera_x)
        self._draw_hud()
        if self.is_boss and self.boss is not None and not self.boss.is_dead:
            self._draw_boss_health()

    def _draw_boss_health(self):
        boss = self.boss
        bar_w, bar_h = 360, 18
        x = SCREEN_WIDTH // 2 - bar_w // 2
        y = 84
        label = self.font_hud.render("BOSS", True, (255, 90, 90))
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

        sub = self.font_small.render(
            "Arrows / WASD = Move    Space/W/Up = Jump    S/Down = Duck", True, (235, 235, 245))
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 250))

        hs = self.font_menu.render(f"HIGH SCORE  {self.high_score:06d}", True, (255, 220, 90))
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 290))

        mp = pygame.mouse.get_pos()
        for b in (self.btn_play, self.btn_exit):
            b.update(mp)
            b.draw(self.screen)

        tip = self.font_small.render("v2.1.0  -  Enhanced Edition", True, (220, 220, 230))
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, 540))

    def draw_intro(self):
        self._draw_background(self.camera_x)
        self._dim(140)
        if self.is_boss:
            self._draw_title_banner("BOSS BATTLE", 190, color=(255, 70, 70))
            warn = self.font_menu.render("Stomp the boss to win!", True, (255, 220, 120))
            self.screen.blit(warn, (SCREEN_WIDTH // 2 - warn.get_width() // 2, 300))
        else:
            self._draw_title_banner(f"WORLD {self.level.world_name}", 200)
            sub = self.font_menu.render(self.theme['name'], True, (200, 220, 255))
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 290))

        lvl = self.font_menu.render(f"Level {self.level_num}", True, (255, 255, 255))
        self.screen.blit(lvl, (SCREEN_WIDTH // 2 - lvl.get_width() // 2, 340))

        icon = pygame.transform.scale(self.sprites.player_small['idle'], (28, 34))
        self.screen.blit(icon, (SCREEN_WIDTH // 2 - 40, 400))
        lv = self.font_menu.render(f"x  {self.lives}", True, (255, 255, 255))
        self.screen.blit(lv, (SCREEN_WIDTH // 2 + 0, 405))

    def draw_pause(self):
        self._draw_world()
        self._dim(150)
        self._draw_title_banner("PAUSED", 110, color=(255, 255, 255))
        mp = pygame.mouse.get_pos()
        for b in (self.btn_resume, self.btn_settings, self.btn_mainmenu):
            b.update(mp)
            b.draw(self.screen)

    def draw_settings(self):
        self._draw_world()
        self._dim(170)
        self._draw_title_banner("SETTINGS", 110, color=(255, 220, 0))
        self.slider_music.draw(self.screen)
        self.slider_sfx.draw(self.screen)
        mp = pygame.mouse.get_pos()
        self.btn_music_toggle.label = self._music_label()
        for b in (self.btn_music_toggle, self.btn_back):
            b.update(mp)
            b.draw(self.screen)

    def draw_clear(self):
        self._draw_world()
        self._dim(70)
        if self.cleared_boss:
            self._draw_title_banner("BOSS DEFEATED!", 120, color=(255, 120, 120))
        else:
            self._draw_title_banner("STAGE CLEAR!", 120, color=(255, 230, 60))
        sub = self.font_menu.render(
            f"+{max(0, self.timer) * 10} time bonus", True, (255, 255, 255))
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 210))
        nxt = self.font_small.render(
            "Next level starting...   (Enter to skip)", True, (230, 230, 240))
        self.screen.blit(nxt, (SCREEN_WIDTH // 2 - nxt.get_width() // 2, 260))

    def draw_gameover(self):
        self._draw_background(self.camera_x)
        self._dim(190)
        self._draw_title_banner("GAME OVER", 110, color=(220, 40, 40))
        sc = self.font_menu.render(f"Score: {self.score:06d}", True, (255, 255, 255))
        self.screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, 200))
        hs = self.font_menu.render(f"High Score: {self.high_score:06d}", True, (255, 220, 90))
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 240))
        if self.new_record:
            flash = (pygame.time.get_ticks() // 250) % 2 == 0
            if flash:
                nr = self.font_menu.render("NEW HIGH SCORE!", True, (120, 255, 140))
                self.screen.blit(nr, (SCREEN_WIDTH // 2 - nr.get_width() // 2, 280))
        mp = pygame.mouse.get_pos()
        for b in (self.btn_retry, self.btn_go_menu):
            b.update(mp)
            b.draw(self.screen)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            if event.type == pygame.USEREVENT + 10:
                pygame.time.set_timer(pygame.USEREVENT + 10, 0)
                play_coin_second_tone()

            if self.state == MENU:
                self._events_menu(event)
            elif self.state == PLAYING:
                self._events_playing(event)
            elif self.state == PAUSED:
                self._events_paused(event)
            elif self.state == SETTINGS:
                self._events_settings(event)
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
            self.start_new_game()
        elif self.btn_exit.is_clicked(event):
            self._quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            sfx_menu_select()
            self.start_new_game()

    def _events_playing(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.player.register_jump_press()
            elif event.key == pygame.K_ESCAPE:
                self.state = PAUSED
                sfx_pause()

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
            self.slider_music.value = settings.music_volume
            self.slider_sfx.value   = settings.sfx_volume
            self.state = SETTINGS
        elif self.btn_mainmenu.is_clicked(event):
            sfx_menu_select()
            self.state = MENU
            start_music(0)

    def _events_settings(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = PAUSED
            return
        if self.slider_music.handle_event(event):
            settings.music_volume = self.slider_music.value
            settings.clamp()
            update_music_volume()
        if self.slider_sfx.handle_event(event):
            settings.sfx_volume = self.slider_sfx.value
            settings.clamp()
        if self.btn_music_toggle.is_clicked(event):
            settings.music_enabled = not settings.music_enabled
            sfx_menu_select()
            if settings.music_enabled:
                start_music(self.theme_index())
            else:
                stop_music()
        elif self.btn_back.is_clicked(event):
            sfx_menu_select()
            self.state = PAUSED

    def _events_clear(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.clear_timer = 0

    def _events_gameover(self, event):
        if self.btn_retry.is_clicked(event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            sfx_menu_select()
            self.start_new_game()
            start_music(self.theme_index())
        elif self.btn_go_menu.is_clicked(event):
            sfx_menu_select()
            self.state = MENU
            start_music(0)

    def _quit(self):
        try:
            save_high_score(max(self.high_score, self.score))
        except Exception:
            pass
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self._handle_events()

            if self.state == PLAYING:
                self.player.handle_input()
                self.update_playing()
            elif self.state == CLEAR:
                self.update_clear()
            elif self.state == INTRO:
                self.intro_timer -= 1
                if self.intro_timer <= 0:
                    self.state = PLAYING
                    start_music(self.theme_index())

            if self.state == MENU:
                self.draw_menu()
            elif self.state == INTRO:
                self.draw_intro()
            elif self.state == PLAYING:
                self._draw_world()
            elif self.state == PAUSED:
                self.draw_pause()
            elif self.state == SETTINGS:
                self.draw_settings()
            elif self.state == CLEAR:
                self.draw_clear()
            elif self.state == GAMEOVER:
                self.draw_gameover()

            pygame.display.flip()
            self.clock.tick(FPS)
