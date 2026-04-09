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
        if self.ui is not None:
            self.ui.draw_panel_shadow(
                panel_rect,
                alpha=90,
                inflate=18,
                offset=(0, 12),
                border_radius=24,
            )
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
        if self.ui is not None:
            self.ui.draw_panel_grid(
                panel_rect.inflate(-16, -14),
                phase,
                color=accent_color,
                alpha=10,
                step=56,
            )
            self.ui.draw_chrome_rect(panel_rect, border_colors, 22, 4)
            self.ui.draw_marquee_lights(
                panel_rect,
                phase + 0.2,
                (255, 220, 126),
                count=12,
                radius=3,
            )
            if title:
                title_width = max(94, self.tiny_font.size(title)[0] + 22)
                self.ui.draw_badge(
                    title,
                    (panel_rect.left + 18, panel_rect.top - 12, title_width, 24),
                    (255, 214, 82, 220),
                    text_color=BLACK,
                    border_color=(255, 255, 255, 90),
                    font=self.tiny_font,
                )
        return panel_rect

    def draw_base_scene(self, phase, status_text, highlighted_value):
        self.screen.fill((4, 10, 28))
        if self.ui is not None:
            self.ui.draw_vertical_gradient((6, 16, 34), (10, 46, 84), alpha=138)
            self.ui.draw_spotlight_canopy(phase, intensity=0.95, tint=(255, 224, 164))
            self.ui.draw_stage_floor(
                phase, horizon_ratio=0.8, tint=(120, 214, 255), alpha=22
            )
            self.ui.draw_screen_frame(
                phase,
                accent_color=(255, 220, 126),
                secondary_color=(120, 214, 255),
            )
            self.ui.draw_ambient_backdrop(phase)
            self.ui.draw_scene_badges(
                "ROULETTE PRESTIGE", f"{highlighted_value} pts", phase
            )
            self.ui.draw_title_panel("ROULETTE", status_text, phase, y=28)
        self.draw_overlay((2, 8, 24), 44)
        self.draw_star_field(phase)

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
            (self.circle_radius * 3, self.circle_radius * 3), pygame.SRCALPHA
        )
        medallion_rect = medallion_surface.get_rect(
            center=(self.center_x, self.center_y + 18)
        )
        center_point = medallion_surface.get_width() // 2
        pulse = 0.5 + 0.5 * math.sin(phase * 5.6)
        pygame.draw.circle(
            medallion_surface,
            (184, 134, 11, 238),
            (center_point, center_point),
            self.circle_radius + 14,
        )
        pygame.draw.circle(
            medallion_surface,
            (255, 239, 153, 245),
            (center_point, center_point),
            self.circle_radius,
        )
        pygame.draw.circle(
            medallion_surface,
            (255, 255, 255, int(28 + pulse * 28)),
            (center_point, center_point - 8),
            self.circle_radius - 24,
        )
        self.screen.blit(medallion_surface, medallion_rect)
        self.draw_text_with_shadow(
            str(value),
            self.value_font,
            BLACK,
            WHITE,
            (self.center_x, self.center_y + 18),
            shadow_offset=(2, 2),
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
