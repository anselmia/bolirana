# pyright: reportAttributeAccessIssue=false
import math

import pygame

from src.constants import BLACK, WHITE


class UICommonMixin:
    def get_cached_surface(self, cache_name, cache_key, builder, max_entries=192):
        full_key = (cache_name, cache_key)
        cached_surface = self._surface_cache.get(full_key)
        if cached_surface is not None:
            return cached_surface

        if len(self._surface_cache) >= max_entries:
            self._surface_cache.clear()

        cached_surface = builder()
        self._surface_cache[full_key] = cached_surface
        return cached_surface

    def draw_halftone_dots(
        self,
        rect,
        color=(255, 255, 255),
        alpha=22,
        spacing=18,
        radius=2,
        drift=0.0,
    ):
        panel_rect = pygame.Rect(rect)
        dots_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        red, green, blue = color[:3]
        offset = int(drift % max(1, spacing))
        for row, y in enumerate(range(spacing // 2, panel_rect.height, spacing)):
            row_shift = (spacing // 2) if row % 2 else 0
            for x in range(-spacing, panel_rect.width + spacing, spacing):
                pygame.draw.circle(
                    dots_surface,
                    (red, green, blue, alpha),
                    (x + row_shift + offset, y),
                    radius,
                )
        self.display.screen.blit(dots_surface, panel_rect.topleft)

    def draw_arcade_screws(
        self,
        rect,
        color=(255, 248, 220),
        alpha=140,
        inset=12,
        radius=4,
    ):
        panel_rect = pygame.Rect(rect)
        if panel_rect.width < 90 or panel_rect.height < 50:
            return

        def build_screw_surface():
            screw_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            positions = [
                (inset, inset),
                (panel_rect.width - inset, inset),
                (inset, panel_rect.height - inset),
                (panel_rect.width - inset, panel_rect.height - inset),
            ]
            red, green, blue = color[:3]
            for x, y in positions:
                pygame.draw.circle(
                    screw_surface, (red, green, blue, alpha), (x, y), radius
                )
                pygame.draw.line(
                    screw_surface,
                    (40, 40, 40, alpha),
                    (x - radius + 1, y - radius + 1),
                    (x + radius - 1, y + radius - 1),
                    1,
                )
            return screw_surface

        screw_surface = self.get_cached_surface(
            "arcade_screws",
            (panel_rect.size, color[:3], alpha, inset, radius),
            build_screw_surface,
        )
        self.display.screen.blit(screw_surface, panel_rect.topleft)

    def draw_panel_shadow(
        self,
        rect,
        alpha=86,
        inflate=18,
        offset=(0, 10),
        border_radius=26,
        color=(0, 0, 0),
    ):
        panel_rect = pygame.Rect(rect)

        def build_shadow_surface():
            shadow_surface = pygame.Surface(
                (panel_rect.width + inflate * 2, panel_rect.height + inflate * 2),
                pygame.SRCALPHA,
            )
            for layer in range(3, 0, -1):
                layer_inset = (3 - layer) * 4
                layer_alpha = max(0, int(alpha * (0.22 + layer * 0.18)))
                pygame.draw.rect(
                    shadow_surface,
                    (*color, layer_alpha),
                    shadow_surface.get_rect().inflate(
                        -layer_inset * 2, -layer_inset * 2
                    ),
                    border_radius=max(0, border_radius + layer * 6),
                )
            glow_rect = pygame.Rect(
                0, 0, panel_rect.width + inflate, panel_rect.height + inflate
            )
            glow_rect.center = shadow_surface.get_rect().center
            pygame.draw.rect(
                shadow_surface,
                (255, 214, 110, max(8, alpha // 5)),
                glow_rect,
                width=3,
                border_radius=max(0, border_radius + 4),
            )
            return shadow_surface

        shadow_surface = self.get_cached_surface(
            "panel_shadow",
            (panel_rect.size, alpha, inflate, border_radius, color),
            build_shadow_surface,
        )
        self.display.screen.blit(
            shadow_surface,
            (
                panel_rect.x - inflate + offset[0],
                panel_rect.y - inflate + offset[1],
            ),
        )

    def draw_badge(
        self,
        text,
        rect,
        fill_color,
        text_color=WHITE,
        border_color=(255, 255, 255, 90),
        font=None,
        shadow_color=BLACK,
    ):
        badge_rect = pygame.Rect(rect)
        badge_surface = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
        radius = min(14, max(10, badge_rect.height // 2))
        fill_alpha = fill_color[3] if len(fill_color) == 4 else 214
        fill_alpha = max(228, fill_alpha)
        border_alpha = border_color[3] if len(border_color) == 4 else 90
        badge_shadow = pygame.Surface(
            (badge_rect.width + 10, badge_rect.height + 10), pygame.SRCALPHA
        )
        pygame.draw.rect(
            badge_shadow,
            (0, 0, 0, 58),
            badge_shadow.get_rect(),
            border_radius=radius + 4,
        )
        self.display.screen.blit(
            badge_shadow, (badge_rect.left - 5, badge_rect.top + 3)
        )
        pygame.draw.rect(
            badge_surface,
            (*fill_color[:3], fill_alpha),
            badge_surface.get_rect(),
            border_radius=radius,
        )
        pygame.draw.rect(
            badge_surface,
            (255, 255, 255, max(24, fill_alpha // 6)),
            (4, 3, badge_rect.width - 8, max(8, badge_rect.height // 2 - 2)),
            border_radius=max(8, radius - 2),
        )
        pygame.draw.polygon(
            badge_surface,
            (255, 255, 255, 32),
            [
                (badge_rect.width - 30, 0),
                (badge_rect.width, 0),
                (badge_rect.width, badge_rect.height),
                (badge_rect.width - 14, badge_rect.height),
            ],
        )
        pygame.draw.rect(
            badge_surface,
            (*border_color[:3], border_alpha),
            badge_surface.get_rect(),
            width=2,
            border_radius=radius,
        )
        self.display.screen.blit(badge_surface, badge_rect.topleft)
        candidate_fonts = [self.display.font_verysmall if font is None else font]
        for fallback_name in ("font_micro", "font_tiny"):
            fallback_font = getattr(self.display, fallback_name, None)
            if fallback_font is not None and fallback_font not in candidate_fonts:
                candidate_fonts.append(fallback_font)
        badge_font = candidate_fonts[-1]
        max_text_width = max(10, badge_rect.width - 12)
        max_text_height = max(10, badge_rect.height - 4)
        for candidate in candidate_fonts:
            text_width, text_height = candidate.size(str(text))
            if text_width <= max_text_width and text_height <= max_text_height:
                badge_font = candidate
                break
        text_components = tuple(text_color)
        red = text_components[0] if len(text_components) >= 1 else 255
        green = text_components[1] if len(text_components) >= 2 else red
        blue = text_components[2] if len(text_components) >= 3 else green
        text_luma = (red * 299 + green * 587 + blue * 114) / 1000
        text_surface = badge_font.render(str(text), True, text_color)
        text_rect = text_surface.get_rect(center=badge_rect.center)
        if text_luma < 96:
            outline_surface = badge_font.render(str(text), True, (255, 248, 228))
            for offset_x, offset_y, alpha in (
                (-1, 0, 235),
                (1, 0, 235),
                (0, -1, 235),
                (0, 1, 235),
                (1, 1, 125),
            ):
                outline_layer = outline_surface.copy()
                outline_layer.set_alpha(alpha)
                self.display.screen.blit(
                    outline_layer,
                    (text_rect.x + offset_x, text_rect.y + offset_y),
                )
            self.display.screen.blit(text_surface, text_rect)
        else:
            effective_shadow = shadow_color
            if shadow_color == BLACK and text_luma < 140:
                effective_shadow = (255, 248, 228)
            self.draw_text_with_shadow(
                text,
                badge_font,
                text_color,
                effective_shadow,
                badge_rect.center,
                shadow_offset=(1, 1),
                center=True,
            )

    def draw_panel_grid(self, rect, phase, color=(120, 214, 255), alpha=16, step=54):
        panel_rect = pygame.Rect(rect)
        grid_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        offset_x = -int((phase * 18) % step)
        for x in range(offset_x, panel_rect.width + step, step):
            pygame.draw.line(
                grid_surface,
                (*color[:3], alpha),
                (x, 0),
                (x, panel_rect.height),
                1,
            )
        row_count = max(3, panel_rect.height // 46)
        for row in range(row_count + 1):
            y = int(row * panel_rect.height / row_count)
            pygame.draw.line(
                grid_surface,
                (*color[:3], max(8, alpha - 6)),
                (0, y),
                (panel_rect.width, y),
                1,
            )
        diagonal_x = int((phase * 110) % (panel_rect.width + 120)) - 60
        pygame.draw.polygon(
            grid_surface,
            (*color[:3], max(10, alpha + 6)),
            [
                (diagonal_x, 0),
                (diagonal_x + 36, 0),
                (diagonal_x - 22, panel_rect.height),
                (diagonal_x - 58, panel_rect.height),
            ],
        )
        self.display.screen.blit(grid_surface, panel_rect.topleft)
        self.draw_halftone_dots(
            panel_rect,
            color=color,
            alpha=max(8, alpha - 2),
            spacing=max(14, step // 3),
            radius=1,
            drift=phase * 10,
        )

    def draw_chrome_rect(self, rect, colors, border_radius, width):
        x, y, rect_width, rect_height = rect
        for index in range(width):
            pygame.draw.rect(
                self.display.screen,
                colors[index % len(colors)],
                (
                    x - index,
                    y - index,
                    rect_width + 2 * index,
                    rect_height + 2 * index,
                ),
                border_radius=border_radius - index if border_radius > index else 0,
                width=1,
            )
        if rect_width >= 110 and rect_height >= 42:
            accent = colors[0]
            corners = [
                (x + 10, y + 10, 1, 1),
                (x + rect_width - 10, y + 10, -1, 1),
                (x + 10, y + rect_height - 10, 1, -1),
                (x + rect_width - 10, y + rect_height - 10, -1, -1),
            ]
            for base_x, base_y, direction_x, direction_y in corners:
                pygame.draw.line(
                    self.display.screen,
                    accent,
                    (base_x, base_y),
                    (base_x + direction_x * 14, base_y),
                    2,
                )
                pygame.draw.line(
                    self.display.screen,
                    accent,
                    (base_x, base_y),
                    (base_x, base_y + direction_y * 14),
                    2,
                )

    def draw_text_with_outline(
        self,
        text,
        font,
        text_color,
        outline_color,
        position,
        outline_width=2,
        center=False,
    ):
        outline_font = pygame.font.Font(font, font.size + outline_width * 2)
        outline_text = outline_font.render(text, True, outline_color)
        outline_rect = outline_text.get_rect()
        if center:
            outline_rect.center = position
        else:
            outline_rect.topleft = position
        self.display.screen.blit(outline_text, outline_rect)

        actual_text = font.render(text, True, text_color)
        actual_rect = actual_text.get_rect()
        if center:
            actual_rect.center = outline_rect.center
        else:
            actual_rect.topleft = outline_rect.topleft
        self.display.screen.blit(actual_text, actual_rect)

    def draw_text_with_shadow(
        self,
        text,
        font,
        text_color,
        shadow_color,
        position,
        shadow_offset=(2, 2),
        center=False,
    ):
        actual_text = font.render(text, True, text_color)
        shadow_text = font.render(text, True, shadow_color)
        actual_position = position
        shadow_layers = [
            (shadow_offset[0] + 2, shadow_offset[1] + 2, 90),
            (shadow_offset[0], shadow_offset[1], 150),
        ]
        if center:
            actual_position = (
                actual_position[0] - actual_text.get_width() // 2,
                actual_position[1] - actual_text.get_height() // 2,
            )
        for offset_x, offset_y, alpha in shadow_layers:
            layer = shadow_text.copy()
            layer.set_alpha(alpha)
            self.display.screen.blit(
                layer,
                (actual_position[0] + offset_x, actual_position[1] + offset_y),
            )
        self.display.screen.blit(actual_text, actual_position)

    def draw_marquee_lights(self, rect, phase, color, count=16, radius=4):
        x, y, width, height = rect
        red, green, blue = color[:3]
        for index in range(count):
            ratio = index / count
            if ratio < 0.25:
                light_x = x + width * ratio * 4
                light_y = y
            elif ratio < 0.5:
                light_x = x + width
                light_y = y + height * (ratio - 0.25) * 4
            elif ratio < 0.75:
                light_x = x + width - width * (ratio - 0.5) * 4
                light_y = y + height
            else:
                light_x = x
                light_y = y + height - height * (ratio - 0.75) * 4

            pulse = 0.45 + 0.55 * math.sin(phase * 4.2 + index * 0.9)
            light_radius = max(2, int(radius + pulse * 2))
            glow = pygame.Surface((light_radius * 6, light_radius * 6), pygame.SRCALPHA)
            glow_center = glow.get_width() // 2
            bulb_color = (255, 228, 148) if index % 2 == 0 else (red, green, blue)
            pygame.draw.circle(
                glow,
                (red, green, blue, int(34 + pulse * 54)),
                (glow_center, glow_center),
                light_radius * 2,
            )
            pygame.draw.circle(
                glow,
                (*bulb_color[:3], int(115 + pulse * 100)),
                (glow_center, glow_center),
                light_radius,
            )
            self.display.screen.blit(
                glow,
                (int(light_x) - glow_center, int(light_y) - glow_center),
            )
