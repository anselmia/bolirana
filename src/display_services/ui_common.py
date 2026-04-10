# pyright: reportAttributeAccessIssue=false
import math

import pygame

from src.constants import BLACK, WHITE


class UICommonMixin:
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
        shadow_surface = pygame.Surface(
            (panel_rect.width + inflate * 2, panel_rect.height + inflate * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            shadow_surface,
            (*color, alpha),
            shadow_surface.get_rect(),
            border_radius=border_radius,
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
        border_alpha = border_color[3] if len(border_color) == 4 else 90
        pygame.draw.rect(
            badge_surface,
            (*fill_color[:3], fill_alpha),
            badge_surface.get_rect(),
            border_radius=radius,
        )
        pygame.draw.rect(
            badge_surface,
            (*border_color[:3], border_alpha),
            badge_surface.get_rect(),
            width=2,
            border_radius=radius,
        )
        self.display.screen.blit(badge_surface, badge_rect.topleft)
        self.draw_text_with_shadow(
            text,
            self.display.font_verysmall if font is None else font,
            text_color,
            shadow_color,
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
        self.display.screen.blit(grid_surface, panel_rect.topleft)

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
        shadow_text = font.render(text, True, shadow_color)
        shadow_position = (
            position[0] + shadow_offset[0],
            position[1] + shadow_offset[1],
        )
        if center:
            shadow_position = (
                shadow_position[0] - shadow_text.get_width() // 2,
                shadow_position[1] - shadow_text.get_height() // 2,
            )
        self.display.screen.blit(shadow_text, shadow_position)

        actual_text = font.render(text, True, text_color)
        actual_position = position
        if center:
            actual_position = (
                actual_position[0] - actual_text.get_width() // 2,
                actual_position[1] - actual_text.get_height() // 2,
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
            pygame.draw.circle(
                glow,
                (red, green, blue, int(34 + pulse * 54)),
                (glow_center, glow_center),
                light_radius * 2,
            )
            pygame.draw.circle(
                glow,
                (255, 255, 255, int(115 + pulse * 100)),
                (glow_center, glow_center),
                light_radius,
            )
            self.display.screen.blit(
                glow,
                (int(light_x) - glow_center, int(light_y) - glow_center),
            )
