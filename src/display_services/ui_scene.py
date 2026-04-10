# pyright: reportAttributeAccessIssue=false
import math

import pygame

from src.constants import BLACK, CHROME_COLORS, WHITE, YELLOW


class UISceneMixin:
    def draw_vertical_gradient(self, top_color, bottom_color, alpha=150, steps=24):
        gradient = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        for index in range(steps):
            ratio = index / max(1, steps - 1)
            band_top = int(self.display.screen_height * index / steps)
            band_height = max(
                2,
                int(self.display.screen_height * (index + 1) / steps) - band_top,
            )
            color = (
                int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio),
                int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio),
                int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio),
            )
            pygame.draw.rect(
                gradient,
                (*color, alpha),
                (0, band_top, self.display.screen_width, band_height),
            )
        self.display.screen.blit(gradient, (0, 0))

    def draw_spotlight_canopy(self, phase, intensity=1.0, tint=(255, 228, 170)):
        canopy = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        red, green, blue = tint[:3]
        centers = [
            self.display.screen_width * 0.18,
            self.display.screen_width * 0.5,
            self.display.screen_width * 0.82,
        ]
        for index, base_x in enumerate(centers):
            sweep = math.sin(phase * (0.85 + index * 0.18) + index) * 95
            beam_width = 170 + index * 34
            beam_alpha = int((18 + index * 7) * intensity)
            points = [
                (int(base_x - 38 + sweep), 0),
                (int(base_x + 38 + sweep), 0),
                (int(base_x + beam_width), self.display.screen_height),
                (int(base_x - beam_width), self.display.screen_height),
            ]
            pygame.draw.polygon(canopy, (red, green, blue, beam_alpha), points)

        beam_center = int(self.display.screen_width * 0.5 + math.sin(phase * 0.9) * 80)
        pygame.draw.ellipse(
            canopy,
            (255, 255, 255, int(30 * intensity)),
            (beam_center - 180, -120, 360, 220),
        )
        self.display.screen.blit(canopy, (0, 0))

    def draw_stage_floor(
        self, phase, horizon_ratio=0.68, tint=(255, 214, 120), alpha=34
    ):
        horizon_y = int(self.display.screen_height * horizon_ratio)
        floor = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        pygame.draw.polygon(
            floor,
            (10, 18, 34, min(180, alpha * 3)),
            [
                (0, horizon_y),
                (self.display.screen_width, horizon_y),
                (self.display.screen_width, self.display.screen_height),
                (0, self.display.screen_height),
            ],
        )
        for line_index in range(8):
            ratio = (line_index + 1) / 9
            y = int(horizon_y + (self.display.screen_height - horizon_y) * ratio**1.6)
            current_alpha = max(8, int(alpha * (1 - ratio * 0.45)))
            pygame.draw.line(
                floor,
                (*tint, current_alpha),
                (60, y),
                (self.display.screen_width - 60, y),
                1,
            )

        center_x = self.display.screen_width // 2
        for spoke_index in range(9):
            ratio = spoke_index / 8 if spoke_index else 0
            x = int(80 + ratio * (self.display.screen_width - 160))
            wobble = math.sin(phase * 1.6 + spoke_index * 0.7) * 18
            pygame.draw.line(
                floor,
                (*tint, max(10, alpha - 8)),
                (int(center_x + wobble), horizon_y),
                (x, self.display.screen_height),
                1,
            )
        self.display.screen.blit(floor, (0, 0))

    def draw_title_panel(self, title, subtitle, phase, y=38):
        title_rect = pygame.Rect(self.display.screen_width // 2 - 310, y, 620, 106)
        self.draw_panel_shadow(title_rect, alpha=110, inflate=24, offset=(0, 14))
        panel_surface = pygame.Surface(title_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (8, 24, 52, 220),
            panel_surface.get_rect(),
            border_radius=26,
        )
        shimmer_x = int((phase * 160) % (title_rect.width + 180)) - 90
        pygame.draw.polygon(
            panel_surface,
            (255, 255, 255, 28),
            [
                (shimmer_x, 0),
                (shimmer_x + 90, 0),
                (shimmer_x + 150, title_rect.height),
                (shimmer_x + 60, title_rect.height),
            ],
        )
        self.display.screen.blit(panel_surface, title_rect.topleft)
        self.draw_panel_grid(
            title_rect.inflate(-18, -18), phase, (255, 220, 126), 12, 72
        )
        self.draw_chrome_rect(title_rect, CHROME_COLORS, 24, 4)
        self.draw_marquee_lights(title_rect, phase, (255, 220, 126), count=18)
        divider_y = title_rect.top + 68
        pygame.draw.line(
            self.display.screen,
            (255, 214, 118),
            (title_rect.left + 78, divider_y),
            (title_rect.right - 78, divider_y),
            2,
        )
        title_font = (
            self.display.font_title
            if len(title) <= 10
            else self.display.font_title_small
        )
        self.draw_text_with_shadow(
            title,
            title_font,
            (255, 248, 222),
            BLACK,
            (title_rect.centerx, title_rect.top + 34),
            center=True,
        )
        self.draw_text_with_shadow(
            subtitle,
            self.display.font_verysmall,
            YELLOW,
            BLACK,
            (title_rect.centerx, title_rect.bottom - 22),
            center=True,
        )

    def draw_footer_prompt(self, text, phase):
        prompt_rect = pygame.Rect(
            self.display.screen_width // 2 - 290,
            self.display.screen_height - 58,
            580,
            34,
        )
        self.draw_panel_shadow(prompt_rect, alpha=54, inflate=14, offset=(0, 8))
        prompt_surface = pygame.Surface(prompt_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            prompt_surface,
            (8, 20, 42, 176),
            prompt_surface.get_rect(),
            border_radius=16,
        )
        shimmer_x = int((phase * 180) % (prompt_rect.width + 140)) - 70
        pygame.draw.polygon(
            prompt_surface,
            (255, 255, 255, 24),
            [
                (shimmer_x, 0),
                (shimmer_x + 48, 0),
                (shimmer_x + 96, prompt_rect.height),
                (shimmer_x + 48, prompt_rect.height),
            ],
        )
        self.display.screen.blit(prompt_surface, prompt_rect.topleft)
        self.draw_chrome_rect(prompt_rect, CHROME_COLORS, 14, 2)
        self.draw_marquee_lights(prompt_rect, phase + 0.4, (255, 218, 118), count=14)
        self.draw_text_with_shadow(
            text,
            self.display.font_verysmall,
            WHITE,
            BLACK,
            (prompt_rect.centerx, prompt_rect.centery + math.sin(phase * 3.2) * 1.5),
            center=True,
        )

    def draw_scene_badges(self, left_text, right_text, phase):
        badge_specs = ((left_text, 28), (right_text, None))
        for text, fixed_x in badge_specs:
            width = max(140, self.display.font_verysmall.size(text)[0] + 28)
            x = (
                fixed_x
                if fixed_x is not None
                else self.display.screen_width - width - 28
            )
            rect = pygame.Rect(x, 24, width, 28)
            self.draw_panel_shadow(rect, alpha=40, inflate=10, offset=(0, 6))
            badge_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                badge_surface,
                (8, 24, 44, 182),
                badge_surface.get_rect(),
                border_radius=14,
            )
            glow_width = 40 + int((0.5 + 0.5 * math.sin(phase * 3.4)) * 34)
            pygame.draw.rect(
                badge_surface,
                (255, 218, 118, 28),
                (8, 6, min(glow_width, rect.width - 16), rect.height - 12),
                border_radius=10,
            )
            self.display.screen.blit(badge_surface, rect.topleft)
            self.draw_chrome_rect(rect, CHROME_COLORS, 14, 2)
            self.draw_text_with_shadow(
                text,
                self.display.font_verysmall,
                WHITE,
                BLACK,
                rect.center,
                shadow_offset=(1, 1),
                center=True,
            )

    def draw_screen_frame(
        self,
        phase,
        accent_color=(255, 220, 126),
        secondary_color=(120, 214, 255),
    ):
        overlay = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        outer_rect = pygame.Rect(
            10,
            10,
            self.display.screen_width - 20,
            self.display.screen_height - 20,
        )
        inner_rect = pygame.Rect(
            24,
            24,
            self.display.screen_width - 48,
            self.display.screen_height - 48,
        )
        pygame.draw.rect(
            overlay,
            (*secondary_color[:3], 20),
            outer_rect,
            width=2,
            border_radius=30,
        )
        pygame.draw.rect(
            overlay,
            (*accent_color[:3], 16),
            inner_rect,
            width=1,
            border_radius=24,
        )

        corner_length = 34
        corners = [
            (outer_rect.left + 10, outer_rect.top + 10, 1, 1),
            (outer_rect.right - 10, outer_rect.top + 10, -1, 1),
            (outer_rect.left + 10, outer_rect.bottom - 10, 1, -1),
            (outer_rect.right - 10, outer_rect.bottom - 10, -1, -1),
        ]
        for base_x, base_y, direction_x, direction_y in corners:
            pygame.draw.line(
                overlay,
                (*accent_color[:3], 94),
                (base_x, base_y),
                (base_x + corner_length * direction_x, base_y),
                3,
            )
            pygame.draw.line(
                overlay,
                (*accent_color[:3], 94),
                (base_x, base_y),
                (base_x, base_y + corner_length * direction_y),
                3,
            )

        for index in range(6):
            ratio = (index + 1) / 7
            light_x = int(outer_rect.left + ratio * outer_rect.width)
            pulse = 0.45 + 0.55 * math.sin(phase * 4.2 + index * 0.7)
            radius = 3 + int(pulse * 3)
            pygame.draw.circle(
                overlay,
                (*accent_color[:3], 42 + int(pulse * 40)),
                (light_x, outer_rect.top + 2),
                radius,
            )
            pygame.draw.circle(
                overlay,
                (*secondary_color[:3], 38 + int(pulse * 34)),
                (light_x, outer_rect.bottom - 2),
                max(2, radius - 1),
            )

        sweep_x = int((phase * 140) % (self.display.screen_width + 220)) - 110
        pygame.draw.polygon(
            overlay,
            (255, 255, 255, 10),
            [
                (sweep_x, 0),
                (sweep_x + 70, 0),
                (sweep_x - 50, self.display.screen_height),
                (sweep_x - 120, self.display.screen_height),
            ],
        )
        self.display.screen.blit(overlay, (0, 0))

    def draw_ambient_backdrop(self, phase):
        overlay = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        for ribbon_index, color in enumerate(
            ((120, 220, 255), (255, 210, 120), (140, 255, 190))
        ):
            points = []
            base_y = 140 + ribbon_index * 120
            step = max(36, self.display.screen_width // 16)
            for x in range(-step, self.display.screen_width + step, step):
                wave = math.sin(phase * (0.8 + ribbon_index * 0.2) + x * 0.008)
                wave += math.cos(phase * 0.55 + ribbon_index + x * 0.012) * 0.4
                points.append((x, base_y + wave * (18 + ribbon_index * 6)))
            pygame.draw.lines(
                overlay,
                (*color, 18),
                False,
                points,
                6 - ribbon_index,
            )

        for sparkle_index in range(14):
            orbit = phase * (10 + sparkle_index * 0.35)
            sparkle_x = (
                sparkle_index * 123 + math.sin(phase * 0.8 + sparkle_index) * 90
            ) % self.display.screen_width
            sparkle_y = 80 + (
                sparkle_index * 67 + phase * 28 + math.cos(phase + sparkle_index) * 18
            ) % (self.display.screen_height - 180)
            radius = 2 + (sparkle_index % 3)
            sparkle_surface = pygame.Surface((radius * 8, radius * 8), pygame.SRCALPHA)
            center = sparkle_surface.get_width() // 2
            alpha = 24 + int((0.5 + 0.5 * math.sin(orbit)) * 42)
            pygame.draw.circle(
                sparkle_surface,
                (255, 248, 220, alpha),
                (center, center),
                radius * 2,
            )
            pygame.draw.circle(
                sparkle_surface,
                (255, 255, 255, alpha + 36),
                (center, center),
                radius,
            )
            self.display.screen.blit(
                sparkle_surface,
                (int(sparkle_x) - center, int(sparkle_y) - center),
            )

        self.display.screen.blit(overlay, (0, 0))
