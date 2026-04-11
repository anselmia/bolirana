import math
import os
import random
import time

import pygame

from src.constants import BLACK, CHROME_COLORS, GOLD_COLORS, WHITE, YELLOW


DARK_GOLD_COLOR = (184, 134, 11)
LIGHT_GOLD_COLOR = (255, 239, 153)
VALUES = [400, 50, 350, 250, 300, 200, 450, 0, 400, 50, 350, 250, 300, 200, 450, 0]


class RouletteAnimation:
    FAST_ROTATION_STEP_DEGREES = 12.0
    FAST_ROTATION_THRESHOLD = 1.35

    def __init__(
        self,
        screen,
        roulette_sound,
        roulette_end_sound,
        roulette_image,
        roulette_pointer,
        ui=None,
    ):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.ui = ui
        self.rotated_image = roulette_image
        self.current_angle = 0.0

        screen_width, screen_height = self.screen.get_size()
        self.center_x, self.center_y = screen_width // 2, screen_height // 2

        self.angular_speed = (360 / len(VALUES)) / 2
        self.min_turns = 3

        self.roulette_sound = roulette_sound
        self.roulette_end_sound = roulette_end_sound
        self.roulette_image = roulette_image
        self.roulette_pointer = roulette_pointer
        self.base_image_rect = self.roulette_image.get_rect(
            center=(self.center_x, self.center_y + 18)
        )

        self.sections = len(VALUES)
        self.angle_per_section = 360 / self.sections
        self.base_speed = self.angular_speed
        self.title_font = self._get_font("font_title_small", 82)
        self.value_font = self._get_font("font_large", 84)
        self.medium_font = self._get_font("font_medium", 52)
        self.small_font = self._get_font("font_small", 34)
        self.tiny_font = self._get_font("font_verysmall", 24)
        self._surface_cache = {}
        self._fast_rotation_cache = {}

        roulette_height = self.roulette_image.get_height()
        self.circle_radius = max(42, int(roulette_height * 0.29) // 2)

    def _get_font(self, attribute_name, fallback_size):
        if self.ui is not None:
            font = getattr(self.ui.display, attribute_name, None)
            if font is not None:
                return font
        return pygame.font.Font(None, fallback_size)

    def clamp(self, value, minimum=0.0, maximum=1.0):
        return max(minimum, min(maximum, value))

    def lerp(self, start, end, progress):
        return start + (end - start) * progress

    def ease_out_cubic(self, progress):
        return 1 - (1 - progress) ** 3

    def get_cached_surface(self, cache_name, cache_key, builder, max_entries=48):
        full_key = (cache_name, cache_key)
        cached_surface = self._surface_cache.get(full_key)
        if cached_surface is not None:
            return cached_surface

        if len(self._surface_cache) >= max_entries:
            self._surface_cache.clear()

        cached_surface = builder()
        self._surface_cache[full_key] = cached_surface
        return cached_surface

    def render_to_surface(self, builder):
        surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        original_screen = self.screen
        original_ui_screen = None
        if self.ui is not None:
            original_ui_screen = self.ui.display.screen
            self.ui.display.screen = surface
        self.screen = surface
        try:
            builder()
        finally:
            self.screen = original_screen
            if self.ui is not None and original_ui_screen is not None:
                self.ui.display.screen = original_ui_screen
        return surface

    def quantize_angle(self, angle, step_degrees):
        if step_degrees <= 0:
            return angle % 360
        return (round(angle / step_degrees) * step_degrees) % 360

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def draw_overlay(self, color, alpha):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((*color[:3], alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_star_field(self, phase, density=26, color=(255, 244, 190), alpha=88):
        for index in range(density):
            spark_x = (
                index * 97 + math.sin(phase * 0.9 + index * 0.73) * 84
            ) % self.screen.get_width()
            spark_y = 74 + (
                index * 61 + phase * 22 + math.cos(phase + index) * 18
            ) % max(120, self.screen.get_height() - 188)
            radius = 2 + (index % 3)
            sparkle = pygame.Surface((radius * 8, radius * 8), pygame.SRCALPHA)
            glow_center = sparkle.get_width() // 2
            local_alpha = alpha + int((0.5 + 0.5 * math.sin(phase * 5 + index)) * 34)
            pygame.draw.circle(
                sparkle,
                (*color[:3], local_alpha),
                (glow_center, glow_center),
                radius * 2,
            )
            pygame.draw.circle(
                sparkle,
                (255, 255, 255, min(255, local_alpha + 50)),
                (glow_center, glow_center),
                radius,
            )
            self.screen.blit(
                sparkle,
                (int(spark_x) - glow_center, int(spark_y) - glow_center),
            )

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
        if self.ui is not None:
            self.ui.draw_text_with_shadow(
                text,
                font,
                text_color,
                shadow_color,
                position,
                shadow_offset=shadow_offset,
                center=center,
            )
            return

        shadow_text = font.render(text, True, shadow_color)
        actual_text = font.render(text, True, text_color)
        if center:
            shadow_rect = shadow_text.get_rect(
                center=(position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            )
            actual_rect = actual_text.get_rect(center=position)
        else:
            shadow_rect = shadow_text.get_rect(
                topleft=(position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            )
            actual_rect = actual_text.get_rect(topleft=position)
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(actual_text, actual_rect)

    def get_live_value(self):
        section_index = (
            int(self.current_angle // self.angle_per_section) % self.sections
        )
        return VALUES[section_index]

    def draw_panel(self, rect, phase, accent_color, border_colors, title=None):
        panel_rect = pygame.Rect(rect)
        if self.ui is None:
            surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                surface,
                (8, 22, 44, 214),
                surface.get_rect(),
                border_radius=24,
            )
            pygame.draw.rect(
                surface,
                (255, 255, 255, 14),
                (12, 10, panel_rect.width - 24, 24),
                border_radius=12,
            )
            self.screen.blit(surface, panel_rect.topleft)
            return panel_rect

        self.ui.draw_panel_shadow(
            panel_rect,
            alpha=90,
            inflate=18,
            offset=(0, 12),
            border_radius=24,
        )
        panel_surface, top_padding = self.get_cached_surface(
            "panel_shell",
            (
                panel_rect.size,
                tuple(accent_color[:3]),
                tuple(tuple(color[:4]) for color in border_colors),
                title,
                int(round(((phase + 0.2) % math.tau) / math.tau * 12)) % 12,
            ),
            lambda: self._build_panel_surface(
                panel_rect.size,
                accent_color,
                border_colors,
                title,
                phase,
            ),
            max_entries=96,
        )
        self.screen.blit(panel_surface, (panel_rect.left, panel_rect.top - top_padding))
        return panel_rect

    def _build_panel_surface(
        self,
        panel_size,
        accent_color,
        border_colors,
        title,
        phase,
    ):
        top_padding = 18 if title else 0
        panel_surface = pygame.Surface(
            (panel_size[0], panel_size[1] + top_padding), pygame.SRCALPHA
        )
        body_rect = pygame.Rect(0, top_padding, panel_size[0], panel_size[1])
        quantized_phase = (
            int(round(((phase + 0.2) % math.tau) / math.tau * 12)) % 12
        ) * (math.tau / 12)

        pygame.draw.rect(
            panel_surface,
            (8, 22, 44, 214),
            body_rect,
            border_radius=24,
        )
        pygame.draw.rect(
            panel_surface,
            (255, 255, 255, 14),
            (12, top_padding + 10, panel_size[0] - 24, 24),
            border_radius=12,
        )

        local_ui = self.ui
        assert local_ui is not None
        original_screen = self.screen
        original_ui_screen = local_ui.display.screen
        self.screen = panel_surface
        local_ui.display.screen = panel_surface
        try:
            local_ui.draw_panel_grid(
                body_rect.inflate(-16, -14),
                quantized_phase,
                color=accent_color,
                alpha=10,
                step=56,
            )
            local_ui.draw_chrome_rect(body_rect, border_colors, 22, 4)
            local_ui.draw_marquee_lights(
                body_rect,
                quantized_phase,
                (255, 220, 126),
                count=12,
                radius=3,
            )
            if title:
                title_width = max(94, self.tiny_font.size(title)[0] + 22)
                local_ui.draw_badge(
                    title,
                    (18, 6, title_width, 24),
                    (255, 214, 82, 220),
                    text_color=BLACK,
                    border_color=(255, 255, 255, 90),
                    font=self.tiny_font,
                )
        finally:
            self.screen = original_screen
            local_ui.display.screen = original_ui_screen

        return panel_surface, top_padding

    def draw_base_scene(self, phase, status_text, highlighted_value):
        base_scene = self.get_cached_surface(
            "base_scene",
            (status_text, highlighted_value, self.ui is not None),
            lambda: self.render_to_surface(
                lambda: self._draw_cached_base_scene(status_text, highlighted_value)
            ),
            max_entries=24,
        )
        self.screen.blit(base_scene, (0, 0))

    def _draw_cached_base_scene(self, status_text, highlighted_value):
        self.screen.fill((4, 10, 28))
        if self.ui is not None:
            static_phase = 0.0
            self.ui.draw_vertical_gradient((6, 16, 34), (10, 46, 84), alpha=138)
            self.ui.draw_spotlight_canopy(
                static_phase, intensity=0.95, tint=(255, 224, 164)
            )
            self.ui.draw_stage_floor(
                static_phase, horizon_ratio=0.8, tint=(120, 214, 255), alpha=22
            )
            self.ui.draw_screen_frame(
                static_phase,
                accent_color=(255, 220, 126),
                secondary_color=(120, 214, 255),
            )
            self.ui.draw_ambient_backdrop(static_phase)
            self.ui.draw_scene_badges(
                "ROULETTE PRESTIGE",
                f"{highlighted_value} pts",
                static_phase,
            )
            self.ui.draw_title_panel("ROULETTE", status_text, static_phase, y=28)
        self.draw_overlay((2, 8, 24), 44)
        self.draw_star_field(0.0)

    def draw_wheel_stage(self, phase):
        pedestal_rect = pygame.Rect(self.center_x - 220, self.center_y + 210, 440, 76)
        self.draw_panel(
            pedestal_rect, phase, (120, 214, 255), CHROME_COLORS, title="ARENA"
        )
        self.draw_text_with_shadow(
            "La roue decide du score final",
            self.small_font,
            WHITE,
            BLACK,
            pedestal_rect.center,
            center=True,
        )

        glow_surface = pygame.Surface((560, 560), pygame.SRCALPHA)
        glow_center = glow_surface.get_width() // 2
        pulse = 0.5 + 0.5 * math.sin(phase * 4.2)
        for radius, local_alpha in ((190, 28), (220, 18), (248, 10)):
            pygame.draw.circle(
                glow_surface,
                (255, 220, 126, int(local_alpha + pulse * 18)),
                (glow_center, glow_center),
                radius,
                width=6,
            )
        self.screen.blit(
            glow_surface,
            glow_surface.get_rect(center=(self.center_x, self.center_y + 18)),
        )

    def draw_roulette(self):
        rect = self.rotated_image.get_rect(center=self.base_image_rect.center)
        self.screen.blit(self.rotated_image, rect.topleft)

    def rotate_roulette(self, angular_speed):
        self.current_angle = (self.current_angle + angular_speed) % 360
        self.rotated_image = pygame.transform.rotate(
            self.roulette_image, self.current_angle
        )

    def rotate_roulette_fast(self, angular_speed):
        self.current_angle = (self.current_angle + angular_speed) % 360
        display_angle = self.quantize_angle(
            self.current_angle,
            self.FAST_ROTATION_STEP_DEGREES,
        )
        cache_key = int(display_angle)
        rotated_image = self._fast_rotation_cache.get(cache_key)
        if rotated_image is None:
            if (
                len(self._fast_rotation_cache)
                >= int(360 // self.FAST_ROTATION_STEP_DEGREES) + 2
            ):
                self._fast_rotation_cache.clear()
            rotated_image = pygame.transform.rotate(self.roulette_image, display_angle)
            self._fast_rotation_cache[cache_key] = rotated_image
        self.rotated_image = rotated_image

    def draw_pointer(self, phase):
        pointer_rect = self.roulette_pointer.get_rect(
            center=(self.center_x, self.base_image_rect.top + 26)
        )
        glow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        glow_center = glow_surface.get_width() // 2
        pulse = 0.5 + 0.5 * math.sin(phase * 6.4)
        pygame.draw.circle(
            glow_surface,
            (255, 220, 126, int(36 + pulse * 36)),
            (glow_center, glow_center),
            34,
        )
        self.screen.blit(
            glow_surface,
            glow_surface.get_rect(center=pointer_rect.center),
        )
        self.screen.blit(self.roulette_pointer, pointer_rect.topleft)

    def draw_value_track(self, phase, current_value):
        track_rect = pygame.Rect(
            self.center_x - 348, self.screen.get_height() - 118, 696, 58
        )
        self.draw_panel(
            track_rect, phase, (120, 214, 255), CHROME_COLORS, title="TABLE"
        )

        unique_values = [0, 50, 200, 250, 300, 350, 400, 450]
        chip_width = 72
        gap = 10
        total_width = len(unique_values) * chip_width + (len(unique_values) - 1) * gap
        start_x = track_rect.centerx - total_width // 2
        for index, value in enumerate(unique_values):
            chip_rect = pygame.Rect(
                start_x + index * (chip_width + gap),
                track_rect.top + 14,
                chip_width,
                28,
            )
            if value == current_value:
                fill = (255, 214, 82, 224)
                text_color = BLACK
                border = GOLD_COLORS
            else:
                fill = (8, 24, 44, 214)
                text_color = WHITE
                border = CHROME_COLORS
            pygame.draw.rect(self.screen, fill, chip_rect, border_radius=12)
            if self.ui is not None:
                self.ui.draw_chrome_rect(chip_rect, border, 12, 2)
            self.draw_text_with_shadow(
                str(value),
                self.tiny_font,
                text_color,
                WHITE if text_color == BLACK else BLACK,
                chip_rect.center,
                shadow_offset=(1, 1),
                center=True,
            )

    def draw_side_panels(self, phase, current_value, spin_ratio):
        left_rect = pygame.Rect(56, 176, 220, 88)
        right_rect = pygame.Rect(self.screen.get_width() - 276, 176, 220, 88)
        self.draw_panel(left_rect, phase, (255, 214, 110), GOLD_COLORS, title="EN JEU")
        self.draw_panel(
            right_rect, phase, (120, 214, 255), CHROME_COLORS, title="VITESSE"
        )

        self.draw_text_with_shadow(
            "Valeur live",
            self.tiny_font,
            YELLOW,
            BLACK,
            (left_rect.centerx, left_rect.top + 26),
            center=True,
        )
        self.draw_text_with_shadow(
            str(current_value),
            self.medium_font,
            WHITE,
            BLACK,
            (left_rect.centerx, left_rect.bottom - 24),
            center=True,
        )

        self.draw_text_with_shadow(
            "Rotation",
            self.tiny_font,
            YELLOW,
            BLACK,
            (right_rect.centerx, right_rect.top + 26),
            center=True,
        )
        meter_rect = pygame.Rect(
            right_rect.left + 20, right_rect.bottom - 34, right_rect.width - 40, 14
        )
        pygame.draw.rect(self.screen, (255, 255, 255, 26), meter_rect, border_radius=8)
        fill_rect = meter_rect.copy()
        fill_rect.width = max(16, int(fill_rect.width * self.clamp(spin_ratio)))
        pygame.draw.rect(self.screen, (120, 214, 255), fill_rect, border_radius=8)

    def draw_center_medallion(self, value, phase, blink=False):
        visible = True
        if blink:
            visible = int(time.time() * 4) % 2 == 0
        if not visible:
            return

        medallion_surface = pygame.Surface(
            (self.circle_radius * 4, self.circle_radius * 4), pygame.SRCALPHA
        )
        medallion_rect = medallion_surface.get_rect(
            center=(self.center_x, self.center_y + 18)
        )
        center_point = medallion_surface.get_width() // 2
        pulse = 0.5 + 0.5 * math.sin(phase * 5.6)
        outer_radius = self.circle_radius + 18
        rim_radius = self.circle_radius + 10
        hub_radius = max(18, self.circle_radius - 6)
        core_radius = max(14, self.circle_radius - 22)

        for radius, alpha in (
            (outer_radius + 16, int(14 + pulse * 10)),
            (outer_radius + 8, int(26 + pulse * 16)),
        ):
            pygame.draw.circle(
                medallion_surface,
                (74, 178, 255, alpha),
                (center_point, center_point),
                radius,
            )

        pygame.draw.circle(
            medallion_surface,
            (0, 0, 0, 70),
            (center_point, center_point + 8),
            outer_radius,
        )
        pygame.draw.circle(
            medallion_surface,
            (14, 30, 58, 242),
            (center_point, center_point),
            outer_radius,
        )
        pygame.draw.circle(
            medallion_surface,
            (116, 208, 255, 224),
            (center_point, center_point),
            outer_radius,
            width=4,
        )
        pygame.draw.circle(
            medallion_surface,
            (255, 220, 126, 210),
            (center_point, center_point),
            rim_radius,
            width=6,
        )
        pygame.draw.circle(
            medallion_surface,
            (10, 42, 86, 240),
            (center_point, center_point),
            hub_radius,
        )
        pygame.draw.circle(
            medallion_surface,
            (86, 188, 255, 170),
            (center_point, center_point),
            hub_radius,
            width=3,
        )
        pygame.draw.circle(
            medallion_surface,
            (40, 106, 196, 236),
            (center_point, center_point),
            core_radius,
        )

        gloss_rect = pygame.Rect(0, 0, hub_radius + 24, max(14, hub_radius // 2 + 10))
        gloss_rect.center = (center_point - 6, center_point - 16)
        pygame.draw.ellipse(
            medallion_surface,
            (255, 255, 255, int(34 + pulse * 18)),
            gloss_rect,
        )

        inner_glow_rect = pygame.Rect(0, 0, core_radius * 2, max(20, core_radius + 10))
        inner_glow_rect.center = (center_point, center_point + 2)
        pygame.draw.ellipse(
            medallion_surface,
            (132, 214, 255, 76),
            inner_glow_rect,
        )

        for angle in (0, math.pi / 2, math.pi / 4, -math.pi / 4):
            start = (
                int(center_point + math.cos(angle) * 10),
                int(center_point + math.sin(angle) * 10),
            )
            end = (
                int(center_point + math.cos(angle) * (core_radius - 4)),
                int(center_point + math.sin(angle) * (core_radius - 4)),
            )
            pygame.draw.line(
                medallion_surface,
                (255, 255, 255, 22),
                start,
                end,
                2,
            )

        badge_width = max(84, min(132, self.medium_font.size(str(value))[0] + 34))
        badge_height = max(34, self.circle_radius - 6)
        badge_rect = pygame.Rect(0, 0, badge_width, badge_height)
        badge_rect.center = (center_point, center_point)
        pygame.draw.rect(
            medallion_surface,
            (8, 20, 40, 222),
            badge_rect,
            border_radius=18,
        )
        pygame.draw.rect(
            medallion_surface,
            (108, 206, 255, 172),
            badge_rect,
            width=2,
            border_radius=18,
        )
        accent_rect = badge_rect.inflate(-10, -18)
        accent_rect.top = badge_rect.top + 6
        accent_rect.height = max(8, accent_rect.height // 2)
        pygame.draw.rect(
            medallion_surface,
            (255, 255, 255, 26),
            accent_rect,
            border_radius=12,
        )
        self.screen.blit(medallion_surface, medallion_rect)
        self.draw_text_with_shadow(
            str(value),
            self.medium_font,
            WHITE,
            BLACK,
            (self.center_x, self.center_y + 18),
            shadow_offset=(3, 3),
            center=True,
        )

    def draw_result_banner(self, phase, final_value):
        banner_rect = pygame.Rect(
            self.center_x - 250, self.screen.get_height() - 194, 500, 62
        )
        self.draw_panel(
            banner_rect, phase, (255, 214, 110), GOLD_COLORS, title="RESULTAT"
        )
        self.draw_text_with_shadow(
            f"La roulette accorde {final_value} points",
            self.small_font,
            WHITE,
            BLACK,
            banner_rect.center,
            center=True,
        )

    def render_frame(
        self,
        phase,
        status_text,
        current_value,
        spin_ratio,
        final_value=None,
        blink=False,
    ):
        self.draw_base_scene(
            phase, status_text, current_value if final_value is None else final_value
        )
        self.draw_wheel_stage(phase)
        self.draw_roulette()
        self.draw_pointer(phase)
        self.draw_side_panels(phase, current_value, spin_ratio)
        self.draw_value_track(
            phase, current_value if final_value is None else final_value
        )
        self.draw_center_medallion(
            final_value if final_value is not None else current_value,
            phase,
            blink=blink,
        )
        if self.ui is not None:
            footer_text = (
                "La roue revele son verdict"
                if final_value is not None
                else "Suspense maximum, la roue tourne"
            )
            self.ui.draw_footer_prompt(footer_text, phase)
        if final_value is not None:
            self.draw_result_banner(phase, final_value)

    def get_value_from_angle(self, angle):
        normalized_angle = angle % 360
        section_index = int(normalized_angle // self.angle_per_section)
        return VALUES[section_index]

    def run(self):
        random.seed(time.time() + int.from_bytes(os.urandom(8), "big"))
        base_random = random.randint(0, (2 * self.sections) - 1)
        extra_random = random.randint(1, self.sections)
        additional_sections = (
            base_random + extra_random - random.randint(0, extra_random)
        ) % ((2 * self.sections) - 1)
        total_sections = (self.min_turns * self.sections) + additional_sections
        total_rotation = total_sections * self.angle_per_section
        final_angle = (additional_sections * self.angle_per_section) % 360
        self.roulette_sound.play(loops=-1)
        rotated = 0.0
        while rotated < total_rotation:
            if not self.handle_events():
                self.roulette_sound.stop()
                return 0

            progress = 0.0 if total_rotation <= 0 else rotated / total_rotation
            if progress < 0.12:
                frame_speed = self.lerp(
                    self.base_speed, self.base_speed * 1.9, progress / 0.12
                )
            elif progress < 0.74:
                frame_speed = self.base_speed * 1.9
            else:
                frame_speed = self.lerp(
                    self.base_speed * 1.9,
                    max(0.8, self.base_speed * 0.24),
                    self.clamp((progress - 0.74) / 0.26),
                )

            step = min(frame_speed, total_rotation - rotated)
            if frame_speed >= self.base_speed * self.FAST_ROTATION_THRESHOLD:
                self.rotate_roulette_fast(step)
            else:
                self.rotate_roulette(step)
            rotated += step
            phase = time.monotonic()
            current_value = self.get_live_value()
            self.render_frame(
                phase,
                "Suspense maximum avant le verdict",
                current_value,
                1.0 - self.clamp(progress),
            )
            pygame.display.flip()
            self.clock.tick(60)

        self.current_angle = final_angle
        self.rotated_image = pygame.transform.rotate(
            self.roulette_image, self.current_angle
        )
        final_value = VALUES[additional_sections % len(VALUES)]
        blink_duration = 2.0
        end_blink_time = time.time() + blink_duration

        self.roulette_sound.stop()
        self.roulette_end_sound.play()

        while time.time() < end_blink_time:
            if not self.handle_events():
                break
            phase = time.monotonic()
            self.render_frame(
                phase,
                "Verdict final de la roulette",
                final_value,
                0.0,
                final_value=final_value,
                blink=True,
            )
            pygame.display.flip()
            self.clock.tick(60)

        self.render_frame(
            time.monotonic(),
            "Verdict final de la roulette",
            final_value,
            0.0,
            final_value=final_value,
            blink=False,
        )
        pygame.display.flip()

        return final_value
