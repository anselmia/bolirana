# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame

from src.constants import (
    BLACK,
    BLUE,
    CHROME_COLORS,
    DARK_GREEN,
    GOAL_ANIMATION_DURATION,
    GOLD_COLORS,
    HOLE_RADIUS,
    LIGHT_GREY,
    RED,
    WHITE,
    YELLOW,
)
from src.roulette import RouletteAnimation


class EffectsScoreMixin:
    def draw_goal_animation(self, hole, pin):
        if pin == hole.pin[0]:
            center = (int(hole.position[0]), int(hole.position[1]))
        else:
            center = (int(hole.position2[0]), int(hole.position2[1]))

        accent_map = {
            "side": LIGHT_GREY,
            "bottle": YELLOW,
            "little_frog": DARK_GREEN,
            "large_frog": BLUE,
        }
        accent = accent_map.get(hole.type, YELLOW)
        backdrop = self.display.screen.copy()
        label = hole.text if hole.text == "ROUL" else f"+{hole.text}"
        label_font = (
            self.display.font_large if hole.type != "side" else self.display.font_medium
        )
        cues_triggered = set()
        score_sound_name = "roulette_end_sound" if hole.type == "side" else "applause"
        score_sound_volume = 0.42 if hole.type == "side" else 0.28
        score_sound_maxtime = 0 if hole.type == "side" else 420

        def render(progress):
            phase = time.monotonic()
            self.trigger_cue(
                cues_triggered,
                "cheer",
                0.18,
                progress,
                score_sound_name,
                volume=score_sound_volume,
                fade_ms=80,
                maxtime=score_sound_maxtime,
            )
            flash = max(0.0, 1 - progress * 3.8)
            if flash > 0:
                self.draw_overlay((255, 248, 220), int(70 * flash))
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.54, tint=(255, 230, 176)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.79, tint=self.get_rgb(accent), alpha=18
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=self.get_rgb(accent),
                secondary_color=(255, 230, 176),
            )
            left_badge = {
                "side": "PRECISION",
                "bottle": "BONUS",
                "little_frog": "FROG SHOT",
                "large_frog": "BOSS HIT",
            }.get(hole.type, "SCORE")
            right_badge = "ROULETTE" if hole.type == "large_frog" else label
            self.display.ui.draw_scene_badges(left_badge, right_badge, phase)
            self.draw_cinematic_bars(
                progress * 0.9, color=(4, 10, 20), max_height=44, reveal_portion=0.3
            )
            self.draw_vignette(72, (6, 12, 24))
            self.draw_crowd_bounce(progress * 0.9)
            self.draw_party_ribbons(
                progress,
                palette=[accent, WHITE, YELLOW],
                alpha=26,
                speed=0.55,
            )
            self.draw_light_beam(center, progress, accent, width=210, alpha=105)
            self.draw_speed_lines(progress, accent, count=9, alpha=58, angle=0.6)
            self.draw_impact_cloud(
                center,
                min(1.0, progress * 1.22),
                color=accent,
                puff_count=8,
                spread=76,
                alpha=92,
            )
            self.draw_shockwave(
                center,
                progress * 1.1,
                accent,
                start_radius=46,
                end_radius=210,
                width=7,
                y_scale=0.7,
                alpha=155,
            )
            pulse = 0.65 + 0.35 * math.sin(progress * math.tau * 3)
            self.draw_glow_circle(
                center,
                HOLE_RADIUS + 10 + pulse * 12,
                accent,
                glow_radius=28 + progress * 12,
                alpha=150,
            )
            self.draw_orbiting_particles(
                center,
                progress,
                WHITE,
                orbit_radius=56 + progress * 48,
                count=8,
                size=4,
                speed=1.7,
                vertical_scale=0.75,
            )
            for ring_index in range(3):
                ring_progress = progress * 1.25 - ring_index * 0.18
                if 0 <= ring_progress <= 1:
                    radius = HOLE_RADIUS + int(110 * self.ease_out_cubic(ring_progress))
                    width = max(2, int(8 * (1 - ring_progress)))
                    alpha = max(0, int(160 * (1 - ring_progress)))
                    ring_surface = pygame.Surface(
                        (radius * 2 + 24, radius * 2 + 24), pygame.SRCALPHA
                    )
                    pygame.draw.circle(
                        ring_surface,
                        (*self.get_rgb(accent), alpha),
                        (ring_surface.get_width() // 2, ring_surface.get_height() // 2),
                        radius,
                        width,
                    )
                    self.display.screen.blit(
                        ring_surface,
                        (
                            center[0] - ring_surface.get_width() // 2,
                            center[1] - ring_surface.get_height() // 2,
                        ),
                    )

            for shard_index in range(12):
                angle = progress * math.tau * 1.6 + (shard_index / 12) * math.tau
                inner = 30 + progress * 8
                outer = 72 + progress * 96
                start_pos = (
                    center[0] + math.cos(angle) * inner,
                    center[1] + math.sin(angle) * inner,
                )
                end_pos = (
                    center[0] + math.cos(angle) * outer,
                    center[1] + math.sin(angle) * outer,
                )
                pygame.draw.line(self.display.screen, WHITE, start_pos, end_pos, 2)

            self.draw_radial_burst(
                center,
                min(1.0, progress * 1.15),
                accent,
                particle_count=16,
                distance=140,
                size=10,
                rotation=progress * 1.8,
            )
            self.draw_sticker_burst(
                center,
                min(1.0, progress * 1.22),
                [accent, YELLOW, WHITE],
                count=7,
                distance=116,
                size=13,
                twist=0.3,
            )
            floating_y = center[1] - 36 - int(70 * self.ease_out_cubic(progress))
            label_surface = label_font.render(label, True, WHITE)
            label_alpha = max(0, int(255 * (1 - progress * 0.12)))
            label_surface.set_alpha(label_alpha)
            badge_rect = pygame.Rect(
                0, 0, label_surface.get_width() + 42, label_surface.get_height() + 22
            )
            badge_rect.center = (
                center[0],
                floating_y - int(6 * math.sin(progress * math.tau * 2.6)),
            )
            self.display.ui.draw_panel_shadow(
                badge_rect,
                alpha=84,
                inflate=16,
                offset=(0, 10),
                border_radius=18,
            )
            badge_surface = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                badge_surface,
                (10, 26, 54, 190),
                badge_surface.get_rect(),
                border_radius=18,
            )
            pygame.draw.rect(
                badge_surface,
                (255, 255, 255, 14),
                (10, 8, badge_rect.width - 20, 18),
                border_radius=10,
            )
            pygame.draw.rect(
                badge_surface,
                (*self.get_rgb(accent), 110),
                badge_surface.get_rect(),
                border_radius=18,
                width=3,
            )
            self.display.screen.blit(badge_surface, badge_rect.topleft)
            self.display.ui.draw_panel_grid(
                badge_rect.inflate(-10, -8),
                phase,
                color=self.get_rgb(accent),
                alpha=10,
                step=42,
            )
            label_rect = label_surface.get_rect(center=badge_rect.center)
            label_shadow = label_font.render(label, True, BLACK)
            label_shadow.set_alpha(min(180, label_alpha))
            self.display.screen.blit(label_shadow, label_rect.move(3, 3))
            self.display.screen.blit(label_surface, label_rect)
            funny_text = {
                "little_frog": "BOING!",
                "large_frog": "CROAK!",
                "bottle": "GLUP!",
            }.get(hole.type, "BAM!")
            self.draw_reaction_signs(progress, [funny_text, label, "OLE!"])
            self.draw_comic_caption(
                funny_text,
                (center[0] + 60, center[1] - 90),
                min(1.0, progress * 1.4),
                fill_color=(255, 244, 132),
                outline_color=WHITE,
                wobble=8.0,
            )
            footer_text = {
                "side": "Point marque avec style.",
                "bottle": "Bonus actif.",
                "little_frog": "Petite grenouille validee.",
                "large_frog": "Grande grenouille declenchee.",
            }.get(hole.type, "Score valide.")
            footer_rect = pygame.Rect(center[0] - 160, center[1] + 86, 320, 38)
            self.display.ui.draw_panel_shadow(
                footer_rect,
                alpha=56,
                inflate=12,
                offset=(0, 8),
                border_radius=16,
            )
            footer_surface = pygame.Surface(footer_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                footer_surface,
                (8, 24, 44, 184),
                footer_surface.get_rect(),
                border_radius=16,
            )
            self.display.screen.blit(footer_surface, footer_rect.topleft)
            self.display.ui.draw_chrome_rect(footer_rect, CHROME_COLORS, 16, 2)
            self.display.ui.draw_text_with_shadow(
                footer_text,
                self.display.font_verysmall,
                WHITE,
                BLACK,
                footer_rect.center,
                center=True,
            )

        self.animate_scene(GOAL_ANIMATION_DURATION, render, background=backdrop)

    def draw_penalty(self):
        self.play_sound_cue("penalty_sound", volume=0.8)
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
            phase = time.monotonic()
            self.trigger_cue(
                cues_triggered,
                "panic",
                0.32,
                progress,
                "applause",
                volume=0.22,
                fade_ms=40,
                maxtime=320,
            )
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 5)
            self.draw_overlay((32, 0, 0), int(120 + 60 * pulse))
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.76, tint=(255, 170, 140)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.77, tint=(255, 98, 78), alpha=22
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(255, 210, 86),
                secondary_color=(255, 120, 120),
            )
            self.display.ui.draw_scene_badges("ALERTE", "ROULETTE PUNITIVE", phase)
            self.draw_cinematic_bars(
                progress, color=(0, 0, 0), max_height=56, reveal_portion=0.18
            )
            self.draw_vignette(130, (18, 0, 0))
            self.draw_crowd_bounce(progress * 0.85)
            self.draw_party_ribbons(
                progress,
                palette=[RED, (255, 214, 86), (255, 160, 160)],
                alpha=22,
                speed=1.25,
            )
            self.draw_scanlines(alpha=18, spacing=8, color=(255, 160, 160))
            self.draw_speed_lines(
                progress, (255, 120, 120), count=12, alpha=48, angle=-0.4
            )
            for lane_y in (38, self.display.screen_height - 96):
                pygame.draw.rect(
                    self.display.screen,
                    (48, 8, 8),
                    (0, lane_y, self.display.screen_width, 58),
                    border_radius=10,
                )
                for chevron in range(10):
                    offset_x = (
                        int(
                            (progress * 360 + chevron * 118)
                            % (self.display.screen_width + 140)
                        )
                        - 70
                    )
                    points = [
                        (offset_x, lane_y + 8),
                        (offset_x + 46, lane_y + 8),
                        (offset_x + 88, lane_y + 50),
                        (offset_x + 42, lane_y + 50),
                    ]
                    pygame.draw.polygon(self.display.screen, (255, 210, 60), points)

            self.draw_orbiting_particles(
                center,
                progress,
                (255, 220, 120),
                orbit_radius=140,
                count=10,
                size=5,
                speed=1.8,
                vertical_scale=0.7,
            )
            for beam_index in range(12):
                angle = progress * math.tau * 2 + beam_index * (math.tau / 12)
                inner_radius = 95
                outer_radius = 270 + 25 * pulse
                start = (
                    center[0] + math.cos(angle) * inner_radius,
                    center[1] + math.sin(angle) * inner_radius,
                )
                end = (
                    center[0] + math.cos(angle) * outer_radius,
                    center[1] + math.sin(angle) * outer_radius,
                )
                pygame.draw.line(self.display.screen, RED, start, end, 5)

            header_rect = pygame.Rect(center[0] - 248, 92, 496, 84)
            self.display.ui.draw_panel_shadow(
                header_rect,
                alpha=108,
                inflate=24,
                offset=(0, 14),
                border_radius=28,
            )
            header_surface = pygame.Surface(header_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                header_surface,
                (50, 8, 8, 220),
                header_surface.get_rect(),
                border_radius=28,
            )
            pygame.draw.rect(
                header_surface,
                (255, 255, 255, 14),
                (12, 12, header_rect.width - 24, 28),
                border_radius=18,
            )
            self.display.screen.blit(header_surface, header_rect.topleft)
            self.display.ui.draw_panel_grid(
                header_rect.inflate(-16, -14),
                phase,
                color=(255, 214, 86),
                alpha=11,
                step=58,
            )
            self.display.ui.draw_chrome_rect(header_rect, GOLD_COLORS, 24, 4)
            self.display.ui.draw_badge(
                "DANGER",
                (header_rect.centerx - 52, header_rect.top - 12, 104, 24),
                (255, 214, 82, 224),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )
            self.display.ui.draw_text_with_shadow(
                "PENALITE",
                self.display.font_title_small,
                (255, 248, 222),
                BLACK,
                (header_rect.centerx, header_rect.top + 30),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                "Roulette punitive en approche",
                self.display.font_small,
                YELLOW,
                BLACK,
                (header_rect.centerx, header_rect.bottom - 20),
                center=True,
            )

            triangle = [
                (center[0], center[1] - 120),
                (center[0] - 108, center[1] + 86),
                (center[0] + 108, center[1] + 86),
            ]
            pygame.draw.polygon(self.display.screen, (255, 210, 60), triangle)
            pygame.draw.polygon(self.display.screen, RED, triangle, width=8)
            self.draw_impact_cloud(
                (center[0], center[1] + 40),
                min(1.0, progress * 1.1),
                color=(255, 220, 120),
                puff_count=8,
                spread=92,
                alpha=78,
                y_scale=0.55,
            )
            self.draw_light_beam(center, progress, RED, width=240, alpha=68)
            self.draw_shockwave(
                (center[0], center[1] + 84),
                pulse,
                (255, 220, 120),
                start_radius=20,
                end_radius=160,
                width=4,
                y_scale=0.42,
                alpha=115,
            )
            pygame.draw.rect(
                self.display.screen,
                BLACK,
                (center[0] - 9, center[1] - 54, 18, 82),
                border_radius=8,
            )
            pygame.draw.circle(
                self.display.screen, BLACK, (center[0], center[1] + 48), 12
            )
            text_jitter = int(math.sin(progress * math.tau * 18) * 5 * (1 - progress))
            warning_rect = pygame.Rect(center[0] - 220, center[1] + 126, 440, 50)
            self.display.ui.draw_panel_shadow(
                warning_rect,
                alpha=86,
                inflate=18,
                offset=(0, 10),
                border_radius=20,
            )
            warning_surface = pygame.Surface(warning_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                warning_surface,
                (22, 4, 4, 210),
                warning_surface.get_rect(),
                border_radius=20,
            )
            self.display.screen.blit(warning_surface, warning_rect.topleft)
            self.display.ui.draw_chrome_rect(warning_rect, CHROME_COLORS, 18, 3)
            self.display.ui.draw_marquee_lights(
                warning_rect,
                phase + 0.4,
                (255, 214, 86),
                count=12,
                radius=3,
            )
            self.display.ui.draw_text_with_shadow(
                "Roulette punitive",
                self.display.font_medium,
                YELLOW,
                BLACK,
                (center[0] + text_jitter, warning_rect.centery),
                center=True,
            )
            self.draw_comic_caption(
                "OUPS!",
                (center[0] + 150, center[1] - 80),
                min(1.0, progress * 1.8),
                fill_color=(255, 214, 86),
                outline_color=RED,
                wobble=12.0,
            )
            self.draw_reaction_signs(progress, ["NON!", "AIE!", "SPIN!"])
            self.draw_sticker_burst(
                (center[0], center[1] - 10),
                min(1.0, progress * 1.25),
                [(255, 214, 86), RED, WHITE],
                count=8,
                distance=154,
                size=16,
                twist=0.4,
            )

        self.animate_scene(1.15, render, background=backdrop)
        roulette_animation = RouletteAnimation(
            self.display.screen,
            self.display.resources["roulette_sound"],
            self.display.resources["roulette_end_sound"],
            self.display.resources["roulette_image"],
            self.display.resources["roulette_pointer"],
        )
        return roulette_animation.run()

    def draw_player_win(self, winner):
        self.play_sound_cue("applause", volume=0.75, fade_ms=120, maxtime=1200)
        backdrop = self.display.screen.copy()
        message = f"Bravo {winner}"
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
            phase = time.monotonic()
            self.trigger_cue(
                cues_triggered,
                "victory-hit",
                0.34,
                progress,
                "win_sound",
                volume=0.3,
                fade_ms=120,
            )
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 4)
            frame_width = 660 + int(70 * self.ease_out_back(progress))
            frame_rect = pygame.Rect(0, 0, frame_width, 236)
            frame_rect.center = (center[0], center[1] + 18)

            self.draw_overlay((6, 14, 32), 170)
            self.draw_party_ribbons(progress, alpha=36, speed=0.45)
            self.draw_star_field(
                progress, density=26, color=(255, 244, 186), drift=18, alpha=130
            )
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.92, tint=(255, 228, 170)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.77, tint=(255, 214, 110), alpha=28
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(255, 220, 126),
                secondary_color=(120, 214, 255),
            )
            self.display.ui.draw_scene_badges("MVP MOMENT", "SHOWTIME", phase)
            self.draw_aurora_ribbon(
                progress,
                (255, 220, 120),
                base_y=120,
                amplitude=24,
                thickness=6,
                speed=0.45,
                alpha=52,
                phase=0.2,
            )
            self.draw_aurora_ribbon(
                progress,
                (120, 220, 255),
                base_y=154,
                amplitude=18,
                thickness=5,
                speed=0.65,
                alpha=40,
                phase=1.1,
            )
            self.draw_vignette(92, (0, 10, 28))
            self.draw_confetti(progress, density=24)
            self.draw_crowd_bounce(progress)
            self.draw_glow_circle(
                center, 82 + pulse * 18, YELLOW, glow_radius=56, alpha=170
            )
            self.draw_light_beam(center, progress, YELLOW, width=280, alpha=64)
            self.draw_orbiting_particles(
                center,
                progress,
                YELLOW,
                orbit_radius=190,
                count=12,
                size=5,
                speed=1.0,
                vertical_scale=0.62,
            )

            spotlight_surface = pygame.Surface(
                self.display.screen.get_size(), pygame.SRCALPHA
            )
            for beam_index in range(3):
                sweep = math.sin(progress * math.tau * 1.3 + beam_index * 0.8) * 120
                spotlight = [
                    (center[0] - 110 + sweep, 0),
                    (center[0] + 110 + sweep, 0),
                    (center[0] + 56, center[1] + 120),
                    (center[0] - 56, center[1] + 120),
                ]
                pygame.draw.polygon(spotlight_surface, (255, 245, 180, 42), spotlight)
            self.display.screen.blit(spotlight_surface, (0, 0))

            self.display.ui.draw_panel_shadow(
                frame_rect,
                alpha=116,
                inflate=28,
                offset=(0, 16),
                border_radius=34,
            )
            frame_surface = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                frame_surface,
                (18, 38, 76, 222),
                frame_surface.get_rect(),
                border_radius=34,
            )
            pygame.draw.rect(
                frame_surface,
                (255, 255, 255, 18),
                (14, 14, frame_rect.width - 28, 72),
                border_radius=24,
            )
            pygame.draw.ellipse(
                frame_surface,
                (255, 255, 255, 14),
                (frame_rect.width // 2 - 190, -36, 380, 110),
            )
            self.display.screen.blit(frame_surface, frame_rect.topleft)
            self.display.ui.draw_panel_grid(
                frame_rect.inflate(-24, -24),
                phase,
                color=(255, 214, 110),
                alpha=11,
                step=68,
            )
            self.display.ui.draw_chrome_rect(frame_rect, GOLD_COLORS, 28, 5)
            self.display.ui.draw_marquee_lights(
                frame_rect, phase, (255, 220, 126), count=22
            )
            self.display.ui.draw_badge(
                "STAR PLAYER",
                (frame_rect.centerx - 68, frame_rect.top - 14, 136, 26),
                (255, 214, 82, 224),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )

            banner_offset = 28 + int(6 * pulse)
            left_image_rect = self.display.resources["winner_banner"].get_rect(
                midright=(frame_rect.left - banner_offset, frame_rect.centery + 10)
            )
            right_image_rect = self.display.resources["winner_banner"].get_rect(
                midleft=(frame_rect.right + banner_offset, frame_rect.centery + 10)
            )
            self.display.screen.blit(
                self.display.resources["winner_banner"], left_image_rect
            )
            self.display.screen.blit(
                self.display.resources["winner_banner"], right_image_rect
            )
            crown_points = [
                (frame_rect.centerx - 58, frame_rect.top - 18),
                (frame_rect.centerx - 28, frame_rect.top - 56),
                (frame_rect.centerx, frame_rect.top - 24),
                (frame_rect.centerx + 28, frame_rect.top - 56),
                (frame_rect.centerx + 58, frame_rect.top - 18),
            ]
            pygame.draw.polygon(self.display.screen, (255, 214, 70), crown_points)
            pygame.draw.polygon(self.display.screen, WHITE, crown_points, width=2)
            self.draw_sticker_burst(
                (frame_rect.centerx, frame_rect.top - 18),
                min(1.0, progress * 1.12),
                [YELLOW, WHITE, (255, 196, 86)],
                count=7,
                distance=88,
                size=14,
                twist=0.1,
            )
            self.display.ui.draw_text_with_shadow(
                "VICTOIRE",
                self.display.font_medium,
                YELLOW,
                BLACK,
                (frame_rect.centerx, frame_rect.top + 34),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                message,
                self.display.font_title_small,
                (255, 248, 222),
                BLACK,
                (frame_rect.centerx, frame_rect.centery + 2),
                shadow_offset=(3, 3),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                "Le public est debout pour ce finish.",
                self.display.font_small,
                WHITE,
                BLACK,
                (frame_rect.centerx, frame_rect.bottom - 34),
                center=True,
            )
            self.draw_comic_caption(
                "WOW!",
                (frame_rect.centerx + 160, frame_rect.top + 18),
                min(1.0, progress * 1.25),
                fill_color=(255, 226, 130),
                outline_color=WHITE,
                wobble=6.0,
            )
            self.draw_reaction_signs(progress, ["BRAVO!", "OLE!", "ROI!"])

        self.animate_scene(2.2, render, background=backdrop)
