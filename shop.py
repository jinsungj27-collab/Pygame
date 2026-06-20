"""The Shop: buyable characters and skins (suits).

Currency is the coin wallet (progress.wallet), filled by collecting coins in
levels. Characters cost 10,000 coins; alternate skins cost 5,000 coins.

A character's look is produced by recoloring the base sprite: 'r' is the
hat/shirt (primary identity color) and 'b' is the suit/overalls (the skin).
Each character also has its own jump sound so they feel distinct.
"""

CHARACTER_PRICE = 10000
SKIN_PRICE = 5000

# Each character: primary identity color ('r'), an optional hair color ('k')
# and skin tone ('s') tweak, a jump sound profile, and a list of skins where
# the first one is the free default suit and the rest cost SKIN_PRICE each.
CHARACTERS = [
    {
        'id': 'jin', 'name': 'Jin',
        'desc': 'The original red-capped hero.',
        'primary': (220, 30, 30), 'price': 0,
        'jump': ([160, 680, 820], 'square'),
        'skins': [
            {'id': 'classic', 'name': 'Classic Blue', 'suit': (30, 80, 200), 'price': 0},
            {'id': 'forest',  'name': 'Forest Green', 'suit': (30, 130, 50)},
            {'id': 'shadow',  'name': 'Shadow Black', 'suit': (40, 40, 55)},
        ],
    },
    {
        'id': 'luca', 'name': 'Luca',
        'desc': 'Jin\'s green-clad brother.',
        'primary': (30, 150, 60), 'price': CHARACTER_PRICE,
        'jump': ([150, 600, 900], 'square'),
        'skins': [
            {'id': 'classic', 'name': 'Royal Blue', 'suit': (40, 70, 180), 'price': 0},
            {'id': 'gold',    'name': 'Golden',     'suit': (210, 170, 30)},
        ],
    },
    {
        'id': 'aqua', 'name': 'Aqua',
        'desc': 'A cool ocean diver.',
        'primary': (40, 190, 210), 'price': CHARACTER_PRICE,
        'jump': ([200, 500, 760], 'sine'),
        'skins': [
            {'id': 'classic', 'name': 'Deep Teal', 'suit': (20, 110, 130), 'price': 0},
            {'id': 'coral',   'name': 'Coral',     'suit': (235, 110, 90)},
        ],
    },
]

CHARACTERS += [
    {
        'id': 'blaze', 'name': 'Blaze',
        'desc': 'A fiery daredevil.',
        'primary': (240, 90, 20), 'price': CHARACTER_PRICE,
        'jump': ([180, 720, 1000], 'square'),
        'skins': [
            {'id': 'classic', 'name': 'Ember Red', 'suit': (170, 30, 20), 'price': 0},
            {'id': 'magma',   'name': 'Magma',     'suit': (90, 20, 20)},
        ],
    },
    {
        'id': 'shadow', 'name': 'Shadow',
        'desc': 'A silent purple ninja.',
        'primary': (120, 60, 170), 'price': CHARACTER_PRICE,
        'hair': (20, 20, 30),
        'jump': ([120, 400, 520], 'triangle'),
        'skins': [
            {'id': 'classic', 'name': 'Midnight', 'suit': (40, 30, 60), 'price': 0},
            {'id': 'violet',  'name': 'Violet',   'suit': (140, 70, 210)},
        ],
    },
    {
        'id': 'goldie', 'name': 'Goldie',
        'desc': 'Dripping in gold.',
        'primary': (240, 200, 40), 'price': CHARACTER_PRICE,
        'jump': ([220, 880, 1180], 'sine'),
        'skins': [
            {'id': 'classic', 'name': 'Bronze',  'suit': (170, 110, 40), 'price': 0},
            {'id': 'platinum', 'name': 'Platinum', 'suit': (200, 205, 215)},
        ],
    },
    {
        'id': 'rose', 'name': 'Rose',
        'desc': 'Sweet but tough.',
        'primary': (235, 90, 150), 'price': CHARACTER_PRICE,
        'jump': ([210, 640, 880], 'sine'),
        'skins': [
            {'id': 'classic', 'name': 'Blush', 'suit': (200, 60, 110), 'price': 0},
            {'id': 'cream',   'name': 'Cream', 'suit': (240, 225, 200)},
        ],
    },
]

CHARACTERS += [
    {
        'id': 'frost', 'name': 'Frost',
        'desc': 'An icy wanderer.',
        'primary': (150, 210, 240), 'price': CHARACTER_PRICE,
        'hair': (90, 130, 160),
        'jump': ([260, 540, 700], 'sine'),
        'skins': [
            {'id': 'classic', 'name': 'Glacier', 'suit': (90, 150, 200), 'price': 0},
            {'id': 'snow',    'name': 'Snow',    'suit': (235, 245, 255)},
        ],
    },
    {
        'id': 'viper', 'name': 'Viper',
        'desc': 'A venomous speedster.',
        'primary': (120, 200, 40), 'price': CHARACTER_PRICE,
        'hair': (30, 60, 20),
        'jump': ([140, 560, 760], 'square'),
        'skins': [
            {'id': 'classic', 'name': 'Toxic', 'suit': (60, 120, 30), 'price': 0},
            {'id': 'jungle',  'name': 'Jungle', 'suit': (25, 70, 35)},
        ],
    },
    {
        'id': 'nova', 'name': 'Nova',
        'desc': 'A cosmic traveler.',
        'primary': (210, 70, 220), 'price': CHARACTER_PRICE,
        'hair': (40, 20, 60),
        'jump': ([240, 760, 1100], 'triangle'),
        'skins': [
            {'id': 'classic', 'name': 'Nebula', 'suit': (90, 40, 150), 'price': 0},
            {'id': 'starlight', 'name': 'Starlight', 'suit': (180, 160, 230)},
        ],
    },
]

_CHAR_BY_ID = {c['id']: c for c in CHARACTERS}


def get_character(char_id):
    return _CHAR_BY_ID.get(char_id, CHARACTERS[0])


def get_skin(char, skin_id):
    for skin in char['skins']:
        if skin['id'] == skin_id:
            return skin
    return char['skins'][0]


def skin_price(skin):
    """Default skin (first one) is free; the rest cost SKIN_PRICE."""
    return skin.get('price', SKIN_PRICE)


def character_palette(char_id, skin_id):
    """Build the recolor palette for a character + skin combination."""
    char = get_character(char_id)
    skin = get_skin(char, skin_id)
    palette = {'r': char['primary'], 'b': skin['suit']}
    if 'hair' in char:
        palette['k'] = char['hair']
    if 'skin_tone' in char:
        palette['s'] = char['skin_tone']
    return palette


import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from ui import Button
from sounds import sfx_menu_select, sfx_powerup, sfx_block_bump
from skills import get_skills


class ShopScreen:
    """Draws and handles the Shop. Owned/equip state lives in game.progress."""

    def __init__(self, game):
        self.game = game
        self.tab = 'characters'          # 'characters' or 'skins'
        self._preview_cache = {}
        self._cells = []                 # (button_rect, action, payload) hit-boxes
        self.message = ""
        self.message_timer = 0
        self.confirm = None              # pending purchase awaiting confirmation
        self.info = None                 # character whose info panel is open
        # Which character's skins the SKINS tab shows. Lets the player preview
        # the skins of characters they haven't bought yet.
        self.view_char_id = game.progress['selected_character']

        cx = SCREEN_WIDTH // 2
        f = game.font_small
        self.btn_tab_chars = Button(cx - 150, 96, 200, 44, "CHARACTERS", f)
        self.btn_tab_skins = Button(cx + 150, 96, 200, 44, "SKINS", f)
        self.btn_back = Button(cx, SCREEN_HEIGHT - 36, 200, 46, "BACK", game.font_menu)

        # Confirmation dialog buttons (positioned near the bottom of the box).
        self.btn_confirm_yes = Button(cx - 115, 442, 190, 54, "YES, BUY",
                                      game.font_menu, base_color=(30, 120, 60),
                                      hover_color=(50, 170, 90))
        self.btn_confirm_no = Button(cx + 115, 442, 190, 54, "CANCEL",
                                     game.font_menu, base_color=(120, 40, 40),
                                     hover_color=(170, 60, 60))

        # Close button for the character info panel.
        self.btn_info_close = Button(cx, SCREEN_HEIGHT - 70, 200, 50, "CLOSE",
                                     game.font_menu, base_color=(40, 60, 120),
                                     hover_color=(60, 90, 170))

    def _preview(self, char_id, skin_id, scale=3):
        key = (char_id, skin_id, scale)
        if key not in self._preview_cache:
            palette = character_palette(char_id, skin_id)
            self._preview_cache[key] = self.game.sprites.make_preview(
                char_id, palette, scale)
        return self._preview_cache[key]

    def _notify(self, text):
        self.message = text
        self.message_timer = 120

    # --- ownership queries ---------------------------------------------
    def _owns_char(self, char_id):
        return char_id in self.game.progress['owned_characters']

    def _owns_skin(self, char_id, skin_id):
        return skin_id in self.game.progress['owned_skins'].get(char_id, [])

    def _equipped_char(self):
        return self.game.progress['selected_character']

    def _equipped_skin(self):
        return self.game.progress['selected_skin']

    # --- buy / equip actions -------------------------------------------
    def _buy_character(self, char):
        if self.game.wallet < char['price']:
            sfx_block_bump()
            self._notify("Not enough coins!")
            return
        self.game.wallet -= char['price']
        prog = self.game.progress
        prog['owned_characters'].append(char['id'])
        prog['owned_skins'].setdefault(char['id'], [])
        default_skin = char['skins'][0]['id']
        if default_skin not in prog['owned_skins'][char['id']]:
            prog['owned_skins'][char['id']].append(default_skin)
        sfx_powerup()
        self._notify(f"Unlocked {char['name']}!")
        self._equip_character(char, char['skins'][0])

    def _equip_character(self, char, skin):
        prog = self.game.progress
        prog['selected_character'] = char['id']
        prog['selected_skin'] = skin['id']
        self.game.apply_selected_character()
        self.game.persist_progress()
        sfx_menu_select()

    def _buy_skin(self, char, skin):
        if self.game.wallet < skin_price(skin):
            sfx_block_bump()
            self._notify("Not enough coins!")
            return
        self.game.wallet -= skin_price(skin)
        self.game.progress['owned_skins'].setdefault(char['id'], []).append(skin['id'])
        sfx_powerup()
        self._notify(f"Unlocked {skin['name']}!")
        self._equip_character(char, skin)

    # --- input ----------------------------------------------------------
    def handle_event(self, event):
        """Returns True if the player asked to leave the shop."""
        # While a confirmation dialog is open it captures all input.
        if self.confirm is not None:
            self._handle_confirm_event(event)
            return False

        # The info panel captures input while open.
        if self.info is not None:
            self._handle_info_event(event)
            return False

        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            return True
        if self.btn_back.is_clicked(event):
            sfx_menu_select()
            return True
        if self.btn_tab_chars.is_clicked(event):
            sfx_menu_select()
            self.tab = 'characters'
            return False
        if self.btn_tab_skins.is_clicked(event):
            sfx_menu_select()
            # Default the skins view to the equipped character.
            self.view_char_id = self._equipped_char()
            self.tab = 'skins'
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, action, payload in self._cells:
                if rect.collidepoint(event.pos):
                    self._on_action_click(action, payload)
                    break
        return False

    def _on_action_click(self, action, payload):
        kind, char, skin = payload
        if action == 'view':
            # Preview this character's skins (works for unowned characters).
            sfx_menu_select()
            self.view_char_id = char['id']
            self.tab = 'skins'
        elif action == 'info':
            sfx_menu_select()
            self.info = char
        elif action == 'use':
            if kind == 'char':
                owned = self.game.progress['owned_skins'].get(char['id'], [])
                skin_id = owned[0] if owned else char['skins'][0]['id']
                self._equip_character(char, get_skin(char, skin_id))
            else:
                self._equip_character(char, skin)
        elif action == 'buy':
            # Don't buy yet - open a confirmation so coins aren't spent by
            # accident.
            sfx_menu_select()
            self.confirm = {'kind': kind, 'char': char, 'skin': skin}

    def _handle_confirm_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            self.confirm = None
            return
        if self.btn_confirm_no.is_clicked(event):
            sfx_menu_select()
            self.confirm = None
            return
        if self.btn_confirm_yes.is_clicked(event):
            c = self.confirm
            self.confirm = None
            if c['kind'] == 'char':
                self._buy_character(c['char'])
            else:
                self._buy_skin(c['char'], c['skin'])

    def _handle_info_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_BACKSPACE):
            sfx_menu_select()
            self.info = None
            return
        if self.btn_info_close.is_clicked(event):
            sfx_menu_select()
            self.info = None

    # --- drawing --------------------------------------------------------
    def draw(self):
        game = self.game
        screen = game.screen
        game.menu_scroll += 0.6
        game._draw_background(game.menu_scroll)
        game._dim(180)
        game._draw_title_banner("SHOP", 24, color=(255, 220, 0), big=False)

        self._draw_wallet()

        mp = game._logical_mouse()
        self.btn_tab_chars.base_color = (
            (70, 110, 60) if self.tab == 'characters' else (40, 50, 90))
        self.btn_tab_skins.base_color = (
            (70, 110, 60) if self.tab == 'skins' else (40, 50, 90))
        for b in (self.btn_tab_chars, self.btn_tab_skins, self.btn_back):
            b.update(mp)
            b.draw(screen)

        self._cells = []
        if self.tab == 'characters':
            self._draw_characters()
        else:
            self._draw_skins()

        if self.message_timer > 0:
            self.message_timer -= 1
            msg = game.font_menu.render(self.message, True, (255, 240, 140))
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                              SCREEN_HEIGHT - 86))

        if self.confirm is not None:
            self._draw_confirm()

        if self.info is not None:
            self._draw_info()

    def _draw_confirm(self):
        game = self.game
        screen = game.screen
        game._dim(170)

        c = self.confirm
        if c['kind'] == 'char':
            item = c['char']
            price = item['price']
            question = "Are you sure you want to buy this character?"
            preview = self._preview(item['id'], item['skins'][0]['id'], scale=4)
            name = item['name']
        else:
            item = c['skin']
            price = skin_price(item)
            question = "Are you sure you want to buy this skin?"
            preview = self._preview(c['char']['id'], item['id'], scale=4)
            name = item['name']

        bw, bh = 580, 380
        box = pygame.Rect(SCREEN_WIDTH // 2 - bw // 2, SCREEN_HEIGHT // 2 - bh // 2,
                          bw, bh)
        pygame.draw.rect(screen, (18, 24, 52), box, border_radius=16)
        pygame.draw.rect(screen, (90, 120, 210), box, width=3, border_radius=16)

        q = game.font_menu.render(question, True, (255, 255, 255))
        if q.get_width() > bw - 40:
            q = pygame.transform.smoothscale(q, (bw - 40, q.get_height()))
        screen.blit(q, (box.centerx - q.get_width() // 2, box.y + 26))

        screen.blit(preview, (box.centerx - preview.get_width() // 2, box.y + 64))

        nm = game.font_menu.render(name, True, (255, 230, 120))
        screen.blit(nm, (box.centerx - nm.get_width() // 2, box.y + 150))

        cost = game.font_menu.render(f"Cost: {price} coins", True, (255, 210, 90))
        screen.blit(cost, (box.centerx - cost.get_width() // 2, box.y + 188))

        bal = game.font_small.render(
            f"Your coins: {game.wallet}", True,
            (160, 255, 170) if game.wallet >= price else (255, 130, 130))
        screen.blit(bal, (box.centerx - bal.get_width() // 2, box.y + 224))

        mp = game._logical_mouse()
        for b in (self.btn_confirm_yes, self.btn_confirm_no):
            b.update(mp)
            b.draw(screen)

    def _draw_wallet(self):
        game = self.game
        txt = game.font_menu.render(f"COINS: {game.wallet}", True, (255, 220, 90))
        x = SCREEN_WIDTH - txt.get_width() - 60
        frame = (pygame.time.get_ticks() // 250) % 2
        coin = game.sprites.items['coin1'] if frame == 0 else game.sprites.items['coin2']
        game.screen.blit(pygame.transform.scale(coin, (22, 22)), (x - 30, 30))
        game.screen.blit(txt, (x, 30))

    def _draw_characters(self):
        cols = 5
        margin = 50
        grid_w = SCREEN_WIDTH - margin * 2
        cell_w = grid_w / cols
        cell_h = 188
        top = 138
        gap = 12
        pad = 10
        mp = self.game._logical_mouse()

        for i, char in enumerate(CHARACTERS):
            col, row = i % cols, i // cols
            rect = pygame.Rect(int(margin + col * cell_w + pad),
                               int(top + row * (cell_h + gap)),
                               int(cell_w - pad * 2), cell_h)
            preview = self._preview(char['id'], char['skins'][0]['id'], scale=3)
            equipped = self._equipped_char() == char['id']
            if equipped:
                status, action, btn_label = 'equipped', None, "EQUIPPED"
            elif self._owns_char(char['id']):
                status, action, btn_label = 'owned', 'use', "USE"
            else:
                status, action, btn_label = 'locked', 'buy', f"BUY  {char['price']}"
            btn_rect = self._draw_item_panel(rect, preview, char['name'],
                                             char['desc'], status, btn_label, mp)
            if action:
                self._cells.append((btn_rect, action, ('char', char, None)))

            # An "i" info icon (top-right) opens this character's skill info.
            info_rect = self._draw_info_icon(rect, mp)
            self._cells.append((info_rect, 'info', ('char', char, None)))

            # Clicking the sprite/preview area previews this character's skins
            # (even when it isn't owned yet).
            view_rect = pygame.Rect(rect.x, rect.y, rect.width, 60)
            self._cells.append((view_rect, 'view', ('char', char, None)))

    def _draw_skins(self):
        game = self.game
        char = get_character(self.view_char_id)
        owns_char = self._owns_char(char['id'])
        head = game.font_menu.render(f"{char['name']}'s Suits", True, (255, 255, 255))
        game.screen.blit(head, (SCREEN_WIDTH // 2 - head.get_width() // 2, 142))

        # When previewing a character you don't own yet, make it clear the
        # suits are view-only until the character is unlocked.
        if not owns_char:
            note = game.font_small.render(
                f"Preview only - buy {char['name']} to unlock these suits",
                True, (255, 200, 130))
            game.screen.blit(note, (SCREEN_WIDTH // 2 - note.get_width() // 2, 172))

        skins = char['skins']
        cols = min(len(skins), 4)
        cell_w = 210
        cell_h = 200
        gap = 26
        total_w = cols * cell_w + (cols - 1) * gap
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        top = 200
        mp = game._logical_mouse()

        for i, skin in enumerate(skins):
            rect = pygame.Rect(start_x + i * (cell_w + gap), top, cell_w, cell_h)
            preview = self._preview(char['id'], skin['id'], scale=3)
            if not owns_char:
                # View-only: show the suit but it can't be equipped/bought yet.
                status, action, btn_label = 'locked', None, "LOCKED"
            else:
                equipped = (self._equipped_char() == char['id']
                            and self._equipped_skin() == skin['id'])
                if equipped:
                    status, action, btn_label = 'equipped', None, "EQUIPPED"
                elif self._owns_skin(char['id'], skin['id']):
                    status, action, btn_label = 'owned', 'use', "USE"
                elif skin_price(skin) == 0:
                    status, action, btn_label = 'owned', 'use', "USE"
                else:
                    status, action, btn_label = 'locked', 'buy', f"BUY  {skin_price(skin)}"
            btn_rect = self._draw_item_panel(rect, preview, skin['name'], "",
                                             status, btn_label, mp)
            if action:
                self._cells.append((btn_rect, action, ('skin', char, skin)))

    def _draw_item_panel(self, rect, preview, name, desc, status, btn_label, mp):
        game = self.game
        screen = game.screen
        bg = {
            'equipped': (28, 64, 46),
            'owned':    (26, 36, 74),
            'locked':   (40, 34, 52),
        }[status]
        pygame.draw.rect(screen, bg, rect, border_radius=12)
        if status == 'equipped':
            border = (90, 230, 120)
        elif rect.collidepoint(mp):
            border = (255, 220, 90)
        else:
            border = (20, 25, 50)
        pygame.draw.rect(screen, border, rect, width=3, border_radius=12)

        # Preview sprite centered near the top.
        px = rect.centerx - preview.get_width() // 2
        screen.blit(preview, (px, rect.y + 12))

        name_txt = game.font_menu.render(name, True, (255, 255, 255))
        screen.blit(name_txt, (rect.centerx - name_txt.get_width() // 2, rect.y + 64))

        if desc:
            d = game.font_small.render(desc, True, (200, 205, 220))
            if d.get_width() > rect.width - 14:
                d = pygame.transform.smoothscale(
                    d, (rect.width - 14, d.get_height()))
            screen.blit(d, (rect.centerx - d.get_width() // 2, rect.y + 100))

        # The action button (or an EQUIPPED badge) along the bottom.
        btn_rect = pygame.Rect(rect.x + 14, rect.bottom - 44, rect.width - 28, 34)
        hovered = btn_rect.collidepoint(mp)
        if status == 'equipped':
            pygame.draw.rect(screen, (24, 70, 42), btn_rect, border_radius=9)
            pygame.draw.rect(screen, (90, 230, 120), btn_rect, width=2, border_radius=9)
            col = (130, 255, 160)
        elif status == 'owned':
            base = (50, 90, 170) if not hovered else (70, 120, 210)
            pygame.draw.rect(screen, base, btn_rect, border_radius=9)
            pygame.draw.rect(screen, (150, 190, 255), btn_rect, width=2, border_radius=9)
            col = (255, 255, 255)
        else:  # locked / buy
            base = (180, 130, 35) if not hovered else (215, 165, 55)
            pygame.draw.rect(screen, base, btn_rect, border_radius=9)
            pygame.draw.rect(screen, (255, 220, 120), btn_rect, width=2, border_radius=9)
            col = (255, 255, 255)

        bt = game.font_small.render(btn_label, True, col)
        screen.blit(bt, (btn_rect.centerx - bt.get_width() // 2,
                         btn_rect.centery - bt.get_height() // 2))
        return btn_rect

    def _draw_info_icon(self, cell_rect, mp):
        """Draw a small circular 'i' info badge in the cell's top-right
        corner and return its clickable rect."""
        screen = self.game.screen
        r = 11
        cx = cell_rect.right - r - 6
        cy = cell_rect.y + r + 6
        rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
        hovered = rect.collidepoint(mp)
        fill = (80, 150, 230) if hovered else (40, 90, 160)
        pygame.draw.circle(screen, fill, (cx, cy), r)
        pygame.draw.circle(screen, (200, 225, 255), (cx, cy), r, 2)
        it = self.game.font_small.render("i", True, (255, 255, 255))
        screen.blit(it, (cx - it.get_width() // 2, cy - it.get_height() // 2))
        return rect

    @staticmethod
    def _wrap_text(text, font, max_w):
        """Break text into lines that fit within max_w pixels."""
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if font.size(trial)[0] <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def _draw_info(self):
        game = self.game
        screen = game.screen
        game._dim(180)

        char = self.info
        q_def, ult_def = get_skills(char['id'])

        bw, bh = 740, 486
        box = pygame.Rect(SCREEN_WIDTH // 2 - bw // 2, SCREEN_HEIGHT // 2 - bh // 2 - 6,
                          bw, bh)
        pygame.draw.rect(screen, (18, 24, 52), box, border_radius=16)
        pygame.draw.rect(screen, (90, 120, 210), box, width=3, border_radius=16)

        # Title.
        title = game.font_title.render(char['name'], True, (255, 230, 120))
        screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 16))
        sub = game.font_small.render(char['desc'], True, (200, 210, 235))
        screen.blit(sub, (box.centerx - sub.get_width() // 2, box.y + 56))

        # Left column: big character preview.
        preview = self._preview(char['id'], char['skins'][0]['id'], scale=4)
        left_cx = box.x + 110
        screen.blit(preview, (left_cx - preview.get_width() // 2, box.y + 96))

        # Skin previews row (so the player can review suits before buying).
        sk_label = game.font_small.render("SUITS", True, (180, 200, 240))
        screen.blit(sk_label, (left_cx - sk_label.get_width() // 2, box.y + 210))
        sx = box.x + 28
        sy = box.y + 236
        for skin in char['skins']:
            sp = self._preview(char['id'], skin['id'], scale=2)
            screen.blit(sp, (sx, sy))
            nm = game.font_small.render(skin['name'], True, (210, 215, 235))
            if nm.get_width() > 84:
                nm = pygame.transform.smoothscale(
                    nm, (84, nm.get_height()))
            screen.blit(nm, (sx + sp.get_width() // 2 - nm.get_width() // 2,
                             sy + sp.get_height() + 2))
            sx += sp.get_width() + 16

        # Right column: the two skills.
        rx = box.x + 230
        rw = box.right - rx - 28
        y = box.y + 100
        for key, sdef, cd in (('Q', q_def, '5s'), ('E', ult_def, '30s')):
            is_off = sdef['kind'] == 'off'
            accent = (255, 150, 80) if is_off else (90, 190, 255)
            tag = "OFFENSIVE" if is_off else "DEFENSIVE"
            ult = " (ULTIMATE)" if key == 'E' else ""

            # Key badge.
            badge = pygame.Rect(rx, y, 26, 26)
            pygame.draw.rect(screen, (15, 18, 30), badge, border_radius=6)
            pygame.draw.rect(screen, accent, badge, width=2, border_radius=6)
            kt = game.font_menu.render(key, True, (255, 255, 255))
            screen.blit(kt, (badge.centerx - kt.get_width() // 2,
                             badge.centery - kt.get_height() // 2))

            name = game.font_menu.render(sdef['name'] + ult, True, (255, 255, 255))
            screen.blit(name, (rx + 36, y - 2))
            meta = game.font_small.render(f"{tag}  -  {cd} cooldown", True, accent)
            screen.blit(meta, (rx + 36, y + 26))

            y += 52
            for line in self._wrap_text(sdef['desc'], game.font_small, rw):
                lt = game.font_small.render(line, True, (210, 216, 234))
                screen.blit(lt, (rx + 4, y))
                y += 22
            y += 18

        hint = game.font_small.render(
            "Skills are usable in boss battles.", True, (170, 180, 205))
        screen.blit(hint, (rx + 4, box.bottom - 96))

        mp = game._logical_mouse()
        self.btn_info_close.rect.center = (box.centerx, box.bottom - 34)
        self.btn_info_close.update(mp)
        self.btn_info_close.draw(screen)
