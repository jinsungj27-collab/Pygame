"""Per-character combat skills used during boss battles.

Every playable character has two skills:

* A first skill ("Q") - a small, frequently usable move on a 5 second
  cooldown. It is a minimal support: either a quick defensive dodge/shield or
  a light offensive poke at the boss.
* An Ultimate ("E") - a powerful move on a 30 second cooldown with a big
  impact (heavy damage, a freeze, a full heal, etc.).

Skills are only available in boss battles (both the Endless mode boss stages
and the PvP boss-rush). When a boss fight starts BOTH skills begin on a short
5 second cooldown; afterwards the first skill keeps its 5s cooldown and the
Ultimate uses its full 30s cooldown.

The :class:`SkillManager` owns all of the runtime state (cooldowns, active
auras, skill projectiles, poison ticks) and draws the on-screen indicators
under the HUD with a ticking-clock cooldown animation.

Each skill is described purely as data in :data:`SKILLS`. The ``fx`` dict lists
which effect primitives a skill applies, so the manager stays a single, simple
dispatcher and the shop can read the names/descriptions for its info panel.
"""
import math

import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from entities import Particle
from sounds import (
    sfx_dash, sfx_powerup, sfx_firework, sfx_hazard, sfx_stomp, sfx_jump,
    sfx_coin,
)

FPS = 60
Q_COOLDOWN = 5 * FPS        # 300 frames - first skill recharge
ULT_COOLDOWN = 30 * FPS     # 1800 frames - ultimate recharge
INITIAL_COOLDOWN = 5 * FPS  # both skills start a boss fight on this short CD

# Colors used for the offensive/defensive accent of skill cards + auras.
OFFENSE_COLOR = (255, 140, 60)
DEFENSE_COLOR = (90, 190, 255)


# ---------------------------------------------------------------------------
# Skill definitions. One entry per character id (see shop.CHARACTERS).
#   kind: 'off' (offensive) or 'def' (defensive) - drives the card accent.
#   fx:   the effect primitives applied on cast (see SkillManager._apply).
# ---------------------------------------------------------------------------
SKILLS = {
    'jin': {
        'q': {'name': 'Flame Dash', 'kind': 'off',
              'desc': 'Dash forward wreathed in fire. Briefly invulnerable, '
                      'burning the boss on contact for 1 damage.',
              'fx': {'dash': True, 'strike': 24, 'strike_dmg': 1,
                     'color': (255, 150, 60)}},
        'ult': {'name': 'Inferno Stomp', 'kind': 'off',
                'desc': 'Leap and crash down in an explosion of fire, dealing '
                        '3 damage and a burst of flame.',
                'fx': {'leap': 13, 'damage': 3, 'color': (255, 110, 40)}},
    },
    'luca': {
        'q': {'name': 'Spring Leap', 'kind': 'def',
              'desc': 'A high evasive hop that carries you over attacks while '
                      'briefly invulnerable.',
              'fx': {'leap': 17, 'color': (90, 220, 120)}},
        'ult': {'name': 'Earthshaker', 'kind': 'off',
                'desc': 'Slam the ground to stun the boss for 3s and deal '
                        '3 damage.',
                'fx': {'damage': 3, 'freeze': 180, 'color': (120, 200, 90)}},
    },
    'aqua': {
        'q': {'name': 'Water Veil', 'kind': 'def',
              'desc': 'Surround yourself in a protective bubble, blocking all '
                      'damage for 1.5s.',
              'fx': {'shield': 90, 'color': (60, 190, 230)}},
        'ult': {'name': 'Tidal Wave', 'kind': 'off',
                'desc': 'Hurl a massive wave that crashes into the boss for '
                        '3 damage.',
                'fx': {'projectile': True, 'damage': 3, 'big': True,
                       'color': (50, 150, 220)}},
    },
    'blaze': {
        'q': {'name': 'Flame Bolt', 'kind': 'off',
              'desc': 'Spit a fast fireball that strikes the boss for 1 damage.',
              'fx': {'projectile': True, 'damage': 1, 'color': (255, 120, 40)}},
        'ult': {'name': 'Meteor Strike', 'kind': 'off',
                'desc': 'Call down a meteor that erupts on the boss for '
                        '4 damage.',
                'fx': {'damage': 4, 'color': (255, 90, 30)}},
    },
    'shadow': {
        'q': {'name': 'Smoke Step', 'kind': 'def',
              'desc': 'Blink a short distance in a puff of smoke, dodging '
                      'attacks and briefly invulnerable.',
              'fx': {'blink': 150, 'color': (160, 120, 220)}},
        'ult': {'name': 'Shadow Assault', 'kind': 'off',
                'desc': 'Teleport onto the boss and strike for 3 damage, '
                        'leaving you invulnerable for a moment.',
                'fx': {'teleport': True, 'damage': 3, 'color': (130, 80, 200)}},
    },
    'goldie': {
        'q': {'name': 'Coin Toss', 'kind': 'off',
              'desc': 'Fling a golden coin for 1 damage and pocket a few '
                      'extra coins.',
              'fx': {'projectile': True, 'damage': 1, 'coins': 100,
                     'color': (255, 215, 70)}},
        'ult': {'name': 'Golden Aegis', 'kind': 'def',
                'desc': 'Wrap yourself in gold: full heal and 4s of complete '
                        'invulnerability.',
                'fx': {'shield': 240, 'heal': True, 'coins': 300,
                       'color': (255, 205, 60)}},
    },
    'rose': {
        'q': {'name': 'Thorn Guard', 'kind': 'def',
              'desc': 'Raise a thorny shield for 1.3s. The boss takes 1 damage '
                      'if it touches you.',
              'fx': {'shield': 80, 'strike': 80, 'strike_dmg': 1,
                     'color': (240, 100, 150)}},
        'ult': {'name': 'Blooming Fury', 'kind': 'off',
                'desc': 'Bloom in a storm of petals: heal up and deal 3 damage '
                        'to the boss.',
                'fx': {'damage': 3, 'heal': True, 'color': (245, 110, 170)}},
    },
    'frost': {
        'q': {'name': 'Ice Armor', 'kind': 'def',
              'desc': 'Encase yourself in ice, blocking all damage for 1.5s.',
              'fx': {'shield': 90, 'color': (150, 215, 245)}},
        'ult': {'name': 'Absolute Zero', 'kind': 'off',
                'desc': 'Freeze the boss solid for 4s and deal 2 damage.',
                'fx': {'damage': 2, 'freeze': 240, 'color': (140, 210, 250)}},
    },
    'viper': {
        'q': {'name': 'Venom Spit', 'kind': 'off',
              'desc': 'Spit venom for 1 damage that poisons the boss over time.',
              'fx': {'projectile': True, 'damage': 1, 'poison': 3,
                     'color': (140, 220, 60)}},
        'ult': {'name': 'Toxic Cloud', 'kind': 'off',
                'desc': 'Engulf the boss in toxin: 1 damage now plus heavy '
                        'poison and a 2s slow.',
                'fx': {'damage': 1, 'poison': 5, 'freeze': 120,
                       'color': (120, 210, 50)}},
    },
    'nova': {
        'q': {'name': 'Star Dash', 'kind': 'off',
              'desc': 'Dash through the stars, invulnerable and dealing '
                      '1 damage on contact.',
              'fx': {'dash': True, 'strike': 24, 'strike_dmg': 1,
                     'color': (210, 130, 240)}},
        'ult': {'name': 'Supernova', 'kind': 'off',
                'desc': 'Detonate a cosmic blast: clears all boss projectiles '
                        'and deals 4 damage.',
                'fx': {'damage': 4, 'clear': True, 'shield': 40,
                       'color': (200, 110, 235)}},
    },
}


def get_skills(char_id):
    """Return the (q, ult) skill definition dicts for a character."""
    defs = SKILLS.get(char_id, SKILLS['jin'])
    return defs['q'], defs['ult']


class _SkillProjectile:
    """A player-fired projectile that flies toward the boss and damages it on
    contact. Kept separate from the boss's projectile group so it never hurts
    the player."""

    def __init__(self, x, y, vx, vy, damage, color, poison=0, big=False):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.color = color
        self.poison = poison
        self.r = 16 if big else 9
        self.life = 120
        self.anim = 0.0
        self.rect = pygame.Rect(0, 0, self.r * 2, self.r * 2)
        self.rect.center = (int(x), int(y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        self.anim += 0.4
        self.life -= 1

    def draw(self, surface, camera_x):
        dx = int(self.x - camera_x)
        dy = int(self.y)
        c = self.color
        dark = (c[0] // 3, c[1] // 3, c[2] // 3)
        light = (min(255, c[0] + 70), min(255, c[1] + 70), min(255, c[2] + 70))
        pygame.draw.circle(surface, dark, (dx, dy), self.r + 2)
        pygame.draw.circle(surface, c, (dx, dy), self.r)
        pygame.draw.circle(surface, light, (dx, dy), max(2, self.r - 5))


class SkillManager:
    """Runtime owner of a character's two skills during a boss battle."""

    def __init__(self, game, char_id):
        self.game = game
        self.char_id = char_id
        self.q_def, self.ult_def = get_skills(char_id)

        # Both skills start a fight on the short initial cooldown.
        self.q_cd = INITIAL_COOLDOWN
        self.ult_cd = INITIAL_COOLDOWN
        self.q_cd_max = INITIAL_COOLDOWN
        self.ult_cd_max = INITIAL_COOLDOWN

        self.q_flash = 0      # brief highlight pulse after casting
        self.ult_flash = 0

        self.auras = []           # active player auras: {color, t, max, r}
        self.projectiles = []     # active _SkillProjectile list
        self.poison = 0           # remaining poison ticks on the boss
        self.poison_t = 0
        self.poison_color = (140, 220, 60)
        self.strike = 0           # frames the player's body damages the boss
        self.strike_dmg = 0
        self.strike_hit = False
        self.shake = 0            # screen-shake frames (Ultimates)

    # --- helpers --------------------------------------------------------
    @property
    def _boss(self):
        return self.game.boss

    @property
    def _player(self):
        return self.game.player

    def _add_aura(self, color, frames, r=40):
        self.auras.append({'color': color, 't': frames, 'max': frames, 'r': r})

    def _burst(self, x, y, color):
        """Spawn a firework-style particle burst into the game's particle
        group (used for skill impacts)."""
        self.game.particle_group.add(*Particle.create_firework(x, y, color))

    # --- activation -----------------------------------------------------
    def can_cast_q(self):
        return self.q_cd <= 0 and self._castable()

    def can_cast_ult(self):
        return self.ult_cd <= 0 and self._castable()

    def _castable(self):
        p = self._player
        if p is None or p.is_dead:
            return False
        if getattr(self.game, 'stage_clear', False):
            return False
        if self._boss is None or self._boss.is_dead:
            return False
        return True

    def activate_q(self):
        if not self.can_cast_q():
            return False
        self.q_cd = Q_COOLDOWN
        self.q_cd_max = Q_COOLDOWN
        self.q_flash = 18
        self._apply(self.q_def['fx'], is_ult=False)
        return True

    def activate_ult(self):
        if not self.can_cast_ult():
            return False
        self.ult_cd = ULT_COOLDOWN
        self.ult_cd_max = ULT_COOLDOWN
        self.ult_flash = 26
        self.shake = 16
        self._apply(self.ult_def['fx'], is_ult=True)
        return True

    # --- effect dispatch ------------------------------------------------
    def _apply(self, fx, is_ult):
        player = self._player
        boss = self._boss
        color = fx.get('color', (255, 255, 255))

        if fx.get('clear'):
            self.game.projectile_group.empty()

        if fx.get('heal'):
            player.is_big = True

        if fx.get('coins'):
            self.game.coins += fx['coins']

        if fx.get('shield'):
            player.invincible_timer = max(player.invincible_timer, fx['shield'])
            self._add_aura(color, fx['shield'], r=44)
            sfx_powerup()

        if fx.get('leap'):
            player.vy = -float(fx['leap'])
            player.on_ground = False
            player.can_double_jump = True
            player.invincible_timer = max(player.invincible_timer, 45)
            self._add_aura(color, 45)
            sfx_jump()

        if fx.get('blink'):
            self._blink(fx['blink'], color)

        if fx.get('dash'):
            self._dash(color)

        if fx.get('teleport') and boss is not None:
            self._teleport_to_boss(color)

        if fx.get('strike'):
            self.strike = fx['strike']
            self.strike_dmg = fx.get('strike_dmg', 1)
            self.strike_hit = False

        if fx.get('freeze') and boss is not None:
            boss.frozen = max(getattr(boss, 'frozen', 0), fx['freeze'])
            self._add_aura(color, 30)

        if fx.get('projectile') and boss is not None:
            self._spawn_projectile(fx, color)

        if fx.get('poison'):
            self.poison = max(self.poison, fx['poison'])
            self.poison_color = color

        if fx.get('damage') and boss is not None:
            self._deal(fx['damage'], explode=is_ult, color=color)

        if is_ult:
            sfx_firework()

    def _deal(self, n, explode, color):
        boss = self._boss
        if boss is None or boss.is_dead:
            return
        boss.take_skill_damage(n)
        bx, by = boss.rect.centerx, boss.rect.centery
        self._burst(bx, by, color)
        if explode:
            self._burst(bx - 24, by - 10, color)
            self._burst(bx + 24, by + 10, color)
        # Floating damage number (screen-space so it reads clearly).
        sx = bx - self.game.camera_x
        self.game.particle_group.add(
            Particle.create_score(sx, boss.rect.top - 8, f"-{n}",
                                  self.game.font_hud, color=(255, 230, 120)))

    def _blink(self, dist, color):
        player = self._player
        direction = 1 if player.facing_right else -1
        new_x = player.x + dist * direction
        new_x = max(self.game.camera_x + 20,
                    min(new_x, self.game.level_width - 20))
        # Smoke at both the start and end of the blink.
        self._burst(int(player.x), int(player.rect.centery), color)
        player.x = new_x
        player.rect.centerx = int(new_x)
        player.invincible_timer = max(player.invincible_timer, 40)
        self._add_aura(color, 40)
        self._burst(int(new_x), int(player.rect.centery), color)
        sfx_dash()

    def _dash(self, color):
        player = self._player
        player.dash_dir = 1 if player.facing_right else -1
        player.dash_timer = player.DASH_DURATION
        player.dash_cooldown = 0
        player.vx = player.dash_dir * player.DASH_SPEED
        player.vy = 0.0
        player.invincible_timer = max(player.invincible_timer, 30)
        self._add_aura(color, 30)
        sfx_dash()

    def _teleport_to_boss(self, color):
        player = self._player
        boss = self._boss
        self._burst(int(player.x), int(player.rect.centery), color)
        player.x = boss.rect.centerx
        player.rect.centerx = int(player.x)
        player.y = boss.rect.top - 50
        player.rect.bottom = boss.rect.top - 10
        player.vy = -6.0
        player.on_ground = False
        player.invincible_timer = max(player.invincible_timer, 50)
        self._add_aura(color, 50)
        self._burst(boss.rect.centerx, boss.rect.centery, color)
        sfx_dash()

    def _spawn_projectile(self, fx, color):
        player = self._player
        boss = self._boss
        sx = player.rect.centerx
        sy = player.rect.centery
        dx = boss.rect.centerx - sx
        dy = boss.rect.centery - sy
        dist = max(1.0, math.hypot(dx, dy))
        speed = 11.0
        self.projectiles.append(_SkillProjectile(
            sx, sy, dx / dist * speed, dy / dist * speed,
            fx.get('damage', 1), color, poison=fx.get('poison', 0),
            big=fx.get('big', False)))
        sfx_hazard()

    # --- per-frame update ----------------------------------------------
    def update(self):
        if self.q_cd > 0:
            self.q_cd -= 1
        if self.ult_cd > 0:
            self.ult_cd -= 1
        if self.q_flash > 0:
            self.q_flash -= 1
        if self.ult_flash > 0:
            self.ult_flash -= 1
        if self.shake > 0:
            self.shake -= 1

        for a in self.auras:
            a['t'] -= 1
        self.auras = [a for a in self.auras if a['t'] > 0]

        boss = self._boss
        player = self._player

        # Body-contact strike window (Flame/Star Dash, Thorn Guard).
        if self.strike > 0:
            self.strike -= 1
            if (boss is not None and not boss.is_dead and not self.strike_hit
                    and player is not None
                    and player.rect.colliderect(boss.rect)):
                boss.take_skill_damage(self.strike_dmg)
                self.strike_hit = True
                self._burst(boss.rect.centerx, boss.rect.centery,
                            (255, 180, 80))

        # Poison damage-over-time on the boss.
        if self.poison > 0 and boss is not None and not boss.is_dead:
            self.poison_t -= 1
            if self.poison_t <= 0:
                self.poison_t = 30
                self.poison -= 1
                boss.take_skill_damage(1)
                self.game.particle_group.add(*Particle.create_firework(
                    boss.rect.centerx, boss.rect.centery, self.poison_color))
        elif boss is None or (boss is not None and boss.is_dead):
            self.poison = 0

        # Skill projectiles.
        for pr in self.projectiles:
            pr.update()
            if boss is not None and not boss.is_dead and pr.rect.colliderect(boss.rect):
                boss.take_skill_damage(pr.damage)
                if pr.poison:
                    self.poison = max(self.poison, pr.poison)
                    self.poison_color = pr.color
                self._burst(boss.rect.centerx, boss.rect.centery, pr.color)
                pr.life = 0
        self.projectiles = [p for p in self.projectiles
                            if p.life > 0 and -50 < p.x - self.game.camera_x < SCREEN_WIDTH + 50]

    def camera_shake_offset(self):
        """A small (x, y) jitter while an Ultimate is shaking the screen."""
        if self.shake <= 0:
            return (0, 0)
        import random
        m = self.shake / 16.0
        return (int(random.uniform(-6, 6) * m), int(random.uniform(-6, 6) * m))

    # --- world-space drawing (auras + projectiles) ----------------------
    def draw_world(self, surface, camera_x):
        player = self._player
        if player is not None and not player.is_dead:
            cx = player.rect.centerx - camera_x
            cy = player.rect.centery
            for a in self.auras:
                frac = a['t'] / max(1, a['max'])
                r = int(a['r'] * (0.7 + 0.3 * frac))
                alpha = int(120 * frac)
                glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*a['color'], alpha), (r, r), r)
                pygame.draw.circle(glow, (*a['color'], min(255, alpha + 60)),
                                   (r, r), r, 3)
                surface.blit(glow, (cx - r, cy - r))

        for pr in self.projectiles:
            pr.draw(surface, camera_x)

    # --- HUD drawing ----------------------------------------------------
    def draw_hud(self, surface, x_q, x_e, y, font_small):
        self._draw_slot(surface, x_q, y, 'Q', self.q_def, self.q_cd,
                        self.q_cd_max, self.q_flash, font_small)
        self._draw_slot(surface, x_e, y, 'E', self.ult_def, self.ult_cd,
                        self.ult_cd_max, self.ult_flash, font_small)

    def _draw_slot(self, surface, x, y, key, sdef, cd, cd_max, flash, font):
        size = 50
        rect = pygame.Rect(x, y, size, size)
        accent = OFFENSE_COLOR if sdef['kind'] == 'off' else DEFENSE_COLOR
        ready = cd <= 0

        # Card background.
        panel = pygame.Surface((size, size), pygame.SRCALPHA)
        bg = (32, 40, 70, 230) if ready else (24, 28, 44, 230)
        pygame.draw.rect(panel, bg, (0, 0, size, size), border_radius=10)
        surface.blit(panel, (x, y))

        # Emblem: a simple shape colored by offensive/defensive accent.
        emblem = accent if ready else tuple(c // 2 + 30 for c in accent)
        self._draw_emblem(surface, rect, sdef['kind'], emblem)

        # Ticking-clock cooldown shadow sweeping over the icon.
        if not ready:
            frac = cd / max(1, cd_max)
            self._draw_clock(surface, rect, frac)
            secs = math.ceil(cd / FPS)
            txt = font.render(str(secs), True, (255, 255, 255))
            surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                               rect.centery - txt.get_height() // 2))

        # Border: glowing accent when ready (with a cast pulse), dim otherwise.
        if ready:
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.006)
            bcol = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in accent)
            width = 3
        else:
            bcol = (70, 80, 110)
            width = 2
        if flash > 0:
            bcol = (255, 255, 255)
            width = 3
        pygame.draw.rect(surface, bcol, rect, width=width, border_radius=10)

        # Key badge in the top-left corner.
        badge = pygame.Rect(x - 2, y - 2, 18, 18)
        pygame.draw.rect(surface, (15, 18, 30), badge, border_radius=5)
        pygame.draw.rect(surface, bcol, badge, width=1, border_radius=5)
        kt = font.render(key, True, (255, 255, 255))
        surface.blit(kt, (badge.centerx - kt.get_width() // 2,
                          badge.centery - kt.get_height() // 2))

    def _draw_emblem(self, surface, rect, kind, color):
        cx, cy = rect.center
        if kind == 'off':
            # An aggressive 4-point star / burst.
            pts = []
            for i in range(8):
                ang = math.pi / 4 * i - math.pi / 2
                r = 15 if i % 2 == 0 else 6
                pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
            pygame.draw.polygon(surface, color, pts)
        else:
            # A protective shield outline.
            pts = [(cx, cy - 15), (cx + 12, cy - 9), (cx + 12, cy + 4),
                   (cx, cy + 15), (cx - 12, cy + 4), (cx - 12, cy - 9)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, (15, 20, 35), pts, 2)

    def _draw_clock(self, surface, rect, frac):
        """Draw a translucent dark wedge over the icon that shrinks like a
        clock hand sweeping as the cooldown ticks down (frac = remaining)."""
        if frac <= 0:
            return
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        cx, cy = rect.width // 2, rect.height // 2
        r = rect.width  # large enough to cover the corners
        start = -90.0
        end = start + 360.0 * frac
        pts = [(cx, cy)]
        a = start
        step = 12.0
        while a < end:
            pts.append((cx + r * math.cos(math.radians(a)),
                        cy + r * math.sin(math.radians(a))))
            a += step
        pts.append((cx + r * math.cos(math.radians(end)),
                    cy + r * math.sin(math.radians(end))))
        if len(pts) >= 3:
            pygame.draw.polygon(overlay, (0, 0, 0, 150), pts)
        # Clip the wedge to the rounded card.
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                         border_radius=10)
        overlay.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(overlay, rect.topleft)
