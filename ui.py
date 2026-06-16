import pygame


class Button:
    def __init__(self, cx, cy, w, h, label, font, icon=None,
                 base_color=(40, 50, 90), hover_color=(70, 90, 160),
                 text_color=(255, 255, 255)):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.label = label
        self.font = font
        self.icon = icon
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self._scale = 1.0

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.06 if self.hovered else 1.0
        self._scale += (target - self._scale) * 0.25

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface):
        w = int(self.rect.width * self._scale)
        h = int(self.rect.height * self._scale)
        r = pygame.Rect(0, 0, w, h)
        r.center = self.rect.center

        shadow = r.copy()
        shadow.move_ip(0, 5)
        pygame.draw.rect(surface, (0, 0, 0, 120), shadow, border_radius=12)

        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(surface, color, r, border_radius=12)
        top = r.copy()
        top.height = h // 2
        hl = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        pygame.draw.rect(surface, hl, top, border_radius=12)
        pygame.draw.rect(surface, color, pygame.Rect(r.x, r.centery, w, h // 2),
                         border_radius=12)
        border = (255, 220, 90) if self.hovered else (20, 25, 50)
        pygame.draw.rect(surface, border, r, width=3, border_radius=12)

        text_x_offset = 0
        if self.icon:
            self._draw_icon(surface, r)
            text_x_offset = 18

        if self.label:
            txt = self.font.render(self.label, True, self.text_color)
            surface.blit(
                txt,
                (r.centerx - txt.get_width() // 2 + text_x_offset,
                 r.centery - txt.get_height() // 2),
            )

    def _draw_icon(self, surface, r):
        cy = r.centery
        ix = r.x + 26
        col = self.text_color
        if self.icon == 'play':
            pts = [(ix - 8, cy - 10), (ix - 8, cy + 10), (ix + 10, cy)]
            pygame.draw.polygon(surface, (120, 255, 140), pts)
            pygame.draw.polygon(surface, (20, 60, 30), pts, 2)
        elif self.icon == 'gear':
            pygame.draw.circle(surface, (210, 210, 230), (ix, cy), 10, 0)
            pygame.draw.circle(surface, (60, 60, 90), (ix, cy), 4, 0)
        elif self.icon == 'home':
            pygame.draw.polygon(surface, (255, 220, 120),
                                [(ix, cy - 10), (ix - 11, cy), (ix + 11, cy)])
            pygame.draw.rect(surface, (255, 220, 120), (ix - 8, cy, 16, 11))
        elif self.icon == 'exit':
            pygame.draw.line(surface, (255, 120, 120), (ix - 8, cy - 8), (ix + 8, cy + 8), 4)
            pygame.draw.line(surface, (255, 120, 120), (ix + 8, cy - 8), (ix - 8, cy + 8), 4)
        elif self.icon == 'shop':
            # A little shopping cart.
            pygame.draw.rect(surface, (255, 230, 150), (ix - 9, cy - 7, 15, 10), 2)
            pygame.draw.line(surface, (255, 230, 150), (ix - 11, cy - 9), (ix - 9, cy - 7), 3)
            pygame.draw.circle(surface, (255, 230, 150), (ix - 6, cy + 8), 2)
            pygame.draw.circle(surface, (255, 230, 150), (ix + 4, cy + 8), 2)


class Slider:
    def __init__(self, cx, cy, w, label, font, value=0.5):
        self.rect = pygame.Rect(0, 0, w, 10)
        self.rect.center = (cx, cy)
        self.label = label
        self.font = font
        self.value = value
        self.dragging = False
        self.knob_r = 12

    def _knob_x(self):
        return int(self.rect.x + self.value * self.rect.width)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            kx = self._knob_x()
            knob_rect = pygame.Rect(kx - self.knob_r, self.rect.centery - self.knob_r,
                                    self.knob_r * 2, self.knob_r * 2)
            track = self.rect.inflate(20, 30)
            if knob_rect.collidepoint(event.pos) or track.collidepoint(event.pos):
                self.dragging = True
                return self._set_from_x(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return self._set_from_x(event.pos[0])
        return False

    def nudge(self, delta):
        old = self.value
        self.value = max(0.0, min(1.0, self.value + delta))
        return self.value != old

    def _set_from_x(self, mx):
        old = self.value
        self.value = max(0.0, min(1.0, (mx - self.rect.x) / self.rect.width))
        return self.value != old

    def draw(self, surface):
        lbl = self.font.render(self.label, True, (235, 235, 245))
        surface.blit(lbl, (self.rect.x, self.rect.y - 34))
        pct = self.font.render(f"{int(self.value * 100)}%", True, (255, 220, 90))
        surface.blit(pct, (self.rect.right - pct.get_width(), self.rect.y - 34))

        pygame.draw.rect(surface, (30, 30, 50), self.rect, border_radius=5)
        filled = self.rect.copy()
        filled.width = int(self.value * self.rect.width)
        pygame.draw.rect(surface, (90, 180, 255), filled, border_radius=5)
        pygame.draw.rect(surface, (15, 15, 30), self.rect, width=2, border_radius=5)

        kx = self._knob_x()
        pygame.draw.circle(surface, (255, 255, 255), (kx, self.rect.centery), self.knob_r)
        pygame.draw.circle(surface, (60, 110, 200), (kx, self.rect.centery), self.knob_r, 3)


def draw_vertical_gradient(surface, rect, top_color, bottom_color):
    x, y, w, h = rect
    for i in range(h):
        ratio = i / max(1, h - 1)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))
