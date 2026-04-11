# pyright: reportAttributeAccessIssue=false
import math

import pygame

from src.constants import BLACK, CHROME_COLORS, WHITE, YELLOW


class UISceneMixin:
    def draw_vertical_gradient(self, top_color, bottom_color, alpha=150, steps=24):
        def build_gradient_surface():
            gradient = pygame.Surface(
                (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
            )
            mid_color = (
                int((top_color[0] + bottom_color[0]) / 2 + 16),
                int((top_color[1] + bottom_color[1]) / 2 + 8),
                int((top_color[2] + bottom_color[2]) / 2 + 24),
            )
            for index in range(steps):
                ratio = index / max(1, steps - 1)
                band_top = int(self.display.screen_height * index / steps)
                band_height = max(
                    2,
                    int(self.display.screen_height * (index + 1) / steps) - band_top,
                )
                if ratio < 0.5:
                    local = ratio / 0.5
                    color = (
                        int(top_color[0] + (mid_color[0] - top_color[0]) * local),
                        int(top_color[1] + (mid_color[1] - top_color[1]) * local),
                        int(top_color[2] + (mid_color[2] - top_color[2]) * local),
                    )
                else:
                    local = (ratio - 0.5) / 0.5
                    color = (
                        int(mid_color[0] + (bottom_color[0] - mid_color[0]) * local),
                        int(mid_color[1] + (bottom_color[1] - mid_color[1]) * local),
                        int(mid_color[2] + (bottom_color[2] - mid_color[2]) * local),
                    )
                pygame.draw.rect(
                    gradient,
                    (*color, alpha),
                    (0, band_top, self.display.screen_width, band_height),
                )
            glow_surface = pygame.Surface(
                (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
            )
            pygame.draw.ellipse(
                glow_surface,
                (255, 214, 110, max(20, alpha // 4)),
                (
                    -140,
                    -120,
                    self.display.screen_width + 280,
                    int(self.display.screen_height * 0.44),
                ),
            )
            pygame.draw.ellipse(
                glow_surface,
                (120, 214, 255, max(14, alpha // 6)),
                (
                    40,
                    int(self.display.screen_height * 0.52),
                    self.display.screen_width - 80,
                    int(self.display.screen_height * 0.34),
                ),
            )
            gradient.blit(glow_surface, (0, 0))
            return gradient

        gradient = self.get_cached_surface(
            "vertical_gradient",
            (
                (self.display.screen_width, self.display.screen_height),
                top_color,
                bottom_color,
                alpha,
                steps,
            ),
            build_gradient_surface,
        )
        self.display.screen.blit(gradient, (0, 0))

    def draw_spotlight_canopy(self, phase, intensity=1.0, tint=(255, 228, 170)):
        phase_bucket = int(round(((phase % math.tau) / math.tau) * 16)) % 16
        canopy = self.get_cached_surface(
            "spotlight_canopy",
            (
                (self.display.screen_width, self.display.screen_height),
                tuple(tint[:3]),
                round(float(intensity), 2),
                phase_bucket,
            ),
            lambda: self._build_spotlight_canopy(phase_bucket, intensity, tint),
            max_entries=96,
        )
        self.display.screen.blit(canopy, (0, 0))

    def _build_spotlight_canopy(self, phase_bucket, intensity, tint):
        quantized_phase = (phase_bucket * math.tau) / 16
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
            sweep = math.sin(quantized_phase * (0.85 + index * 0.18) + index) * 95
            beam_width = 170 + index * 34
            beam_alpha = int((18 + index * 7) * intensity)
            points = [
                (int(base_x - 38 + sweep), 0),
                (int(base_x + 38 + sweep), 0),
                (int(base_x + beam_width), self.display.screen_height),
                (int(base_x - beam_width), self.display.screen_height),
            ]
            pygame.draw.polygon(canopy, (red, green, blue, beam_alpha), points)

        beam_center = int(
            self.display.screen_width * 0.5 + math.sin(quantized_phase * 0.9) * 80
        )
        pygame.draw.ellipse(
            canopy,
            (255, 255, 255, int(30 * intensity)),
            (beam_center - 180, -120, 360, 220),
        )
        return canopy

    def draw_stage_floor(
        self, phase, horizon_ratio=0.68, tint=(255, 214, 120), alpha=34
    ):
        horizon_y = int(self.display.screen_height * horizon_ratio)
        floor = self.get_cached_surface(
            "stage_floor_base",
            (
                (self.display.screen_width, self.display.screen_height),
                horizon_y,
                tuple(tint[:3]),
                alpha,
            ),
            lambda: self._build_stage_floor_base(horizon_y, tint, alpha),
            max_entries=64,
        )
        self.display.screen.blit(floor, (0, 0))

        center_x = self.display.screen_width // 2
        spokes_surface = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        for spoke_index in range(9):
            ratio = spoke_index / 8 if spoke_index else 0
            x = int(80 + ratio * (self.display.screen_width - 160))
            wobble = math.sin(phase * 1.6 + spoke_index * 0.7) * 18
            pygame.draw.line(
                spokes_surface,
                (*tint, max(10, alpha - 8)),
                (int(center_x + wobble), horizon_y),
                (x, self.display.screen_height),
                1,
            )
        self.display.screen.blit(spokes_surface, (0, 0))

    def _build_stage_floor_base(self, horizon_y, tint, alpha):
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
        tile_rows = 5
        for row in range(tile_rows):
            row_ratio = (row + 1) / (tile_rows + 1)
            tile_y = int(
                horizon_y + (self.display.screen_height - horizon_y) * row_ratio**1.52
            )
            tile_height = max(10, int(14 + row * 6))
            tile_width = max(36, int(86 - row * 8))
            tile_count = max(6, self.display.screen_width // (tile_width + 8))
            start_x = int((self.display.screen_width - tile_count * tile_width) / 2)
            start_x -= ((row % 2) * tile_width) // 2
            for column in range(tile_count + 2):
                tile_rect = pygame.Rect(
                    start_x + column * tile_width,
                    tile_y,
                    tile_width - 8,
                    tile_height,
                )
                tile_color = (*tint, max(8, int(alpha * (0.18 + row_ratio * 0.44))))
                pygame.draw.rect(floor, tile_color, tile_rect, border_radius=4)
            return floor

    def draw_title_panel(self, title, subtitle, phase, y=38):
        title_rect = pygame.Rect(self.display.screen_width // 2 - 330, y, 660, 122)
        self.draw_panel_shadow(title_rect, alpha=64, inflate=16, offset=(0, 10))
        panel_surface = pygame.Surface(title_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (10, 24, 52, 184),
            panel_surface.get_rect(),
            border_radius=30,
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
        pygame.draw.rect(
            panel_surface,
            (255, 255, 255, 16),
            (14, 12, title_rect.width - 28, 28),
            border_radius=18,
        )
        pygame.draw.rect(
            panel_surface,
            (255, 255, 255, 24),
            panel_surface.get_rect(),
            width=1,
            border_radius=30,
        )
        self.display.screen.blit(panel_surface, title_rect.topleft)
        self.draw_panel_grid(
            title_rect.inflate(-20, -18), phase, (255, 220, 126), 6, 78
        )
        divider_y = title_rect.top + 78
        pygame.draw.line(
            self.display.screen,
            (255, 214, 118, 170),
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
            (title_rect.centerx, title_rect.bottom - 24),
            center=True,
        )
        wing_color = (255, 214, 110, 110)
        for direction in (-1, 1):
            pygame.draw.polygon(
                self.display.screen,
                wing_color,
                [
                    (title_rect.centerx + direction * 286, title_rect.top + 30),
                    (title_rect.centerx + direction * 340, title_rect.top + 52),
                    (title_rect.centerx + direction * 286, title_rect.top + 86),
                ],
            )

    def draw_footer_prompt(self, text, phase):
        prompt_rect = pygame.Rect(
            self.display.screen_width // 2 - 290,
            self.display.screen_height - 58,
            580,
            34,
        )
        self.draw_panel_shadow(prompt_rect, alpha=38, inflate=10, offset=(0, 6))
        prompt_surface = pygame.Surface(prompt_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            prompt_surface,
            (8, 20, 38, 156),
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
        pygame.draw.rect(
            prompt_surface,
            (255, 255, 255, 22),
            prompt_surface.get_rect(),
            width=1,
            border_radius=16,
        )
        self.display.screen.blit(prompt_surface, prompt_rect.topleft)
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
            self.draw_panel_shadow(rect, alpha=28, inflate=8, offset=(0, 5))
            badge_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                badge_surface,
                (8, 24, 40, 154),
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
            pygame.draw.rect(
                badge_surface,
                (255, 255, 255, 20),
                badge_surface.get_rect(),
                width=1,
                border_radius=14,
            )
            self.display.screen.blit(badge_surface, rect.topleft)
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
            width=4,
            border_radius=34,
        )
        pygame.draw.rect(
            overlay,
            (*accent_color[:3], 16),
            inner_rect,
            width=2,
            border_radius=28,
        )

        side_rects = [
            pygame.Rect(24, self.display.screen_height // 2 - 120, 10, 240),
            pygame.Rect(
                self.display.screen_width - 34,
                self.display.screen_height // 2 - 120,
                10,
                240,
            ),
        ]
        for side_rect in side_rects:
            pygame.draw.rect(
                overlay, (*accent_color[:3], 42), side_rect, border_radius=6
            )
            for index in range(10):
                hole_y = side_rect.top + 14 + index * 22
                pygame.draw.circle(
                    overlay,
                    (255, 255, 255, 28),
                    (side_rect.centerx, hole_y),
                    2,
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
        self.draw_halftone_dots(
            pygame.Rect(
                40, 72, self.display.screen_width - 80, self.display.screen_height - 144
            ),
            color=(255, 255, 255),
            alpha=8,
            spacing=24,
            radius=2,
            drift=phase * 4,
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
