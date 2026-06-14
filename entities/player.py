import pygame
from constants import GRAVITY, TERMINAL_VELOCITY, SCREEN_HEIGHT
from sounds import sfx_jump, sfx_shrink, sfx_die


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprites):
        super().__init__()
        self.sprites = sprites
        self.is_big  = False

        self.x  = x
        self.y  = y
        self.vx = 0.0
        self.vy = 0.0

        self.accel      = 0.4
        self.friction   = 0.88
        self.max_speed  = 5.0
        self.jump_power = -12.5

        self.on_ground     = False
        self.facing_right  = True
        self.is_ducking    = False
        self.invincible_timer = 0
        self.death_timer   = 0
        self.is_dead       = False
        self.flag_sliding  = False
        self.victory_walk  = False

        # ── Responsive jump state ─────────────────────────────────────────────
        self.jump_buffered    = False  # set by event loop on KEYDOWN
        self.jump_buffer_timer = 0     # counts down; clears buffer when 0
        self.coyote_timer     = 0      # frames of grace after leaving ground
        self.can_double_jump  = True

        self.anim_frame = 0.0
        self.anim_speed = 0.15

        self.fast_fall = False   # set when Down/S held in mid-air

        self.update_image()

    # ── Sprite selection ──────────────────────────────────────────────────────
    def update_image(self):
        if self.is_big:
            sprite_set = self.sprites.player_big if self.facing_right else self.sprites.player_big_left
        else:
            sprite_set = self.sprites.player_small if self.facing_right else self.sprites.player_small_left

        if self.is_dead:
            self.image = self.sprites.player_small['jump']
        elif self.flag_sliding:
            self.image = sprite_set['walk1']
        elif not self.on_ground:
            self.image = sprite_set['jump']
        elif self.is_ducking:
            self.image = sprite_set['duck']
        elif abs(self.vx) > 0.2:
            frame_idx  = int(self.anim_frame) % 2
            self.image = sprite_set['walk1'] if frame_idx == 0 else sprite_set['walk2']
        else:
            self.image = sprite_set['idle']

        old_bottom = self.y + (80 if self.is_big else 40)
        self.rect  = self.image.get_rect()
        self.rect.width  = 30
        if self.is_ducking:
            # Crouch low enough to slip under flying enemies (both sizes).
            self.rect.height = 20
        elif self.is_big:
            self.rect.height = 70
        else:
            self.rect.height = 35
        self.rect.bottom  = old_bottom
        self.rect.centerx = self.x

    # ── Jump input (called from the event loop on KEYDOWN) ────────────────────
    def register_jump_press(self):
        """Buffer a jump intent so quick taps are never dropped."""
        self.jump_buffered     = True
        self.jump_buffer_timer = 8   # keep intent alive for up to 8 frames

    # ── Per-frame input ───────────────────────────────────────────────────────
    def handle_input(self):
        if self.is_dead or self.flag_sliding or self.victory_walk:
            return

        keys = pygame.key.get_pressed()

        # ── Horizontal movement (Arrows or A/D) ──────────────────────────────
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = min(self.vx + self.accel, self.max_speed)
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = max(self.vx - self.accel, -self.max_speed)
            self.facing_right = False
        else:
            self.vx *= self.friction
            if abs(self.vx) < 0.1:
                self.vx = 0.0

        # ── Duck (on ground) / Fast-fall (in air) with Down or S ──────────────
        duck_held = keys[pygame.K_DOWN] or keys[pygame.K_s]
        self.fast_fall = False
        if duck_held and self.on_ground:
            self.is_ducking = True
            self.vx *= 0.5
        else:
            self.is_ducking = False
            if duck_held and not self.on_ground and self.vy > -3:
                # Slam downward for a quick, controlled landing.
                self.fast_fall = True

        # ── Jump buffer tick ──────────────────────────────────────────────────
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            if self.jump_buffer_timer == 0:
                self.jump_buffered = False

        # ── Coyote time ───────────────────────────────────────────────────────
        if self.on_ground:
            self.coyote_timer = 6
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # ── Resolve buffered jump ─────────────────────────────────────────────
        if self.jump_buffered:
            if self.coyote_timer > 0 and not self.is_ducking:
                self.vy               = self.jump_power
                self.on_ground        = False
                self.coyote_timer     = 0
                self.can_double_jump  = True
                self.jump_buffered    = False
                self.jump_buffer_timer = 0
                sfx_jump()
            elif self.coyote_timer == 0 and self.can_double_jump:
                self.vy              = self.jump_power * 0.9
                self.can_double_jump = False
                self.jump_buffered   = False
                self.jump_buffer_timer = 0
                sfx_jump()

        # ── Variable jump height (release early = lower arc) ─────────────────
        if not (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.vy < -4:
            self.vy = -4

    # ── Damage / death ────────────────────────────────────────────────────────
    def take_damage(self):
        if self.invincible_timer > 0 or self.is_dead:
            return
        if self.is_big:
            self.is_big = False
            self.invincible_timer = 90
            sfx_shrink()
        else:
            self.die()

    def die(self):
        self.is_dead     = True
        self.death_timer = 120
        self.vy          = -10
        self.vx          = 0
        sfx_die()

    # ── Physics update ────────────────────────────────────────────────────────
    def update(self):
        if self.is_dead:
            self.vy    += 0.4
            self.y     += self.vy
            self.rect.y = self.y
            self.update_image()
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.flag_sliding:
            self.vx     = 0
            self.vy     = 2
            self.y     += self.vy
            self.rect.y = self.y
            self.update_image()
            return

        if self.victory_walk:
            self.vx  = 2
            self.vy  = min(self.vy + GRAVITY, TERMINAL_VELOCITY)
            self.x  += self.vx
            self.rect.centerx = self.x
            self.update_image()
            return

        if self.fast_fall:
            # Slam downward: skip the normal terminal cap for a fast landing.
            self.vy = min(self.vy + GRAVITY * 2.2, 22)
        else:
            self.vy = min(self.vy + GRAVITY, TERMINAL_VELOCITY)
        self.x += self.vx
        self.rect.centerx = self.x

        if abs(self.vx) > 0.1:
            self.anim_frame += self.anim_speed

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, camera_x):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return  # blink effect

        draw_x = self.rect.x - camera_x
        draw_y = self.rect.bottom - (80 if self.is_big else 40)
        surface.blit(self.image, (draw_x - 5, draw_y))
