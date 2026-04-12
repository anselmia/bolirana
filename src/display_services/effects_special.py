# pyright: reportAttributeAccessIssue=false
import math
import os
import time

import pygame

from src.constants import BLACK, CHROME_COLORS, GOLD_COLORS, WHITE, YELLOW


class EffectsSpecialMixin:
    def animation_bottle(self):
        self.play_sound_cue(
            "bottle_sound",
            volume=0.74,
            fade_ms=35,
            maxtime=900,
            stop_existing=True,
        )
        video_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "assets",
                "videos",
                "beer.mp4",
            )
        )
        if self.play_video_clip(
            video_path,
            fill_color=(22, 10, 0),
            sound_name="stadium_celebration",
            sound_volume=0.82,
            sound_fade_ms=50,
            fade_out_ms=420,
            intro_fade_ms=220,
            accent_color=(255, 214, 110),
            title="BOUTEILLE",
            subtitle="Le bonus entre en scene",
        ):
            return
        self._animation_bottle_procedural()

    def _animation_bottle_video_intro(self, backdrop):
        self.play_sound_cue(
            "bottle_sound",
            volume=0.74,
            fade_ms=35,
            maxtime=900,
            stop_existing=True,
        )
        center = (self.display.screen_width // 2, self.display.screen_height // 2 + 6)
        stage_y = int(self.display.screen_height * 0.78)
        warm_gold = (255, 210, 122)
        cool_white = (224, 238, 255)
        copper = (232, 156, 72)

        def draw_spotlight(origin_x, target, spread, color, alpha, top_width):
            beam_surface = pygame.Surface(
                (self.display.screen_width, self.display.screen_height),
                pygame.SRCALPHA,
            )
            red, green, blue = color
            for layer in range(5, 0, -1):
                layer_ratio = layer / 5
                layer_alpha = int(alpha * layer_ratio * 0.28)
                current_spread = spread * (0.42 + layer_ratio * 0.9)
                current_top = max(6, int(top_width * (0.6 + (1.0 - layer_ratio) * 0.4)))
                points = [
                    (int(origin_x - current_top), 0),
                    (int(origin_x + current_top), 0),
                    (int(target[0] + current_spread), int(target[1])),
                    (int(target[0] - current_spread), int(target[1])),
                ]
                pygame.draw.polygon(
                    beam_surface,
                    (red, green, blue, layer_alpha),
                    points,
                )
            self.display.screen.blit(beam_surface, (0, 0))

        def draw_floor_reflection(center_point, width, height, color, alpha):
            reflection_surface = pygame.Surface(
                (width * 2, height * 2),
                pygame.SRCALPHA,
            )
            for layer in range(4, 0, -1):
                layer_alpha = int(alpha * (layer / 4) * 0.28)
                ellipse_rect = pygame.Rect(
                    width - int(width * layer * 0.48),
                    height - int(height * layer * 0.18),
                    int(width * layer * 0.96),
                    int(height * layer * 0.34),
                )
                pygame.draw.ellipse(
                    reflection_surface,
                    (*color, layer_alpha),
                    ellipse_rect,
                )
            self.display.screen.blit(
                reflection_surface,
                reflection_surface.get_rect(center=center_point),
            )

        def draw_bottle_silhouette(center_point, reveal, phase):
            silhouette_surface = pygame.Surface((280, 520), pygame.SRCALPHA)
            body_rect = pygame.Rect(74, 130, 132, 284)
            neck_rect = pygame.Rect(118, 56, 44, 104)
            cap_rect = pygame.Rect(112, 34, 56, 24)
            glass_color = (18, 12, 8, min(255, int(220 * reveal + 18)))
            rim_alpha = min(220, int(170 * reveal + 24))
            label_alpha = min(210, int(84 * reveal))
            pygame.draw.rect(
                silhouette_surface,
                glass_color,
                body_rect,
                border_radius=42,
            )
            pygame.draw.rect(
                silhouette_surface,
                glass_color,
                neck_rect,
                border_radius=16,
            )
            pygame.draw.rect(
                silhouette_surface,
                (78, 52, 18, min(235, int(190 * reveal + 20))),
                cap_rect,
                border_radius=8,
            )
            pygame.draw.rect(
                silhouette_surface,
                (255, 236, 212, rim_alpha),
                (95, 102, 18, 272),
                border_radius=12,
            )
            pygame.draw.rect(
                silhouette_surface,
                (255, 225, 160, label_alpha),
                (86, 190, 108, 90),
                border_radius=20,
            )
            pygame.draw.rect(
                silhouette_surface,
                (255, 244, 230, min(160, int(110 * reveal))),
                (154, 142, 14, 212),
                border_radius=10,
            )
            wobble = math.sin(phase * 2.1) * (1.0 - reveal) * 1.8
            lifted_center = (
                center_point[0] + int(wobble * 5),
                center_point[1] - int((1.0 - reveal) * 22),
            )
            self.draw_glow_circle(
                lifted_center,
                88,
                warm_gold,
                glow_radius=110,
                alpha=min(150, int(108 * reveal + 12)),
            )
            self.display.screen.blit(
                silhouette_surface,
                silhouette_surface.get_rect(center=lifted_center),
            )

        def render(progress):
            phase = time.monotonic()
            reveal = self.ease_out_cubic(self.clamp((progress - 0.08) / 0.78))
            sweep = self.ease_in_out_sine(self.clamp((progress - 0.12) / 0.68))
            self.draw_overlay((4, 2, 0), 176)
            self.display.ui.draw_stage_floor(
                phase,
                horizon_ratio=0.79,
                tint=(255, 188, 96),
                alpha=26,
            )
            self.draw_vignette(154, (10, 4, 0))

            rig_rect = pygame.Rect(0, 0, self.display.screen_width, 92)
            rig_surface = pygame.Surface(rig_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(rig_surface, (12, 12, 14, 232), (0, 0, rig_rect.width, 26))
            pygame.draw.rect(
                rig_surface, (34, 34, 40, 210), (0, 26, rig_rect.width, 10)
            )
            for beam_index in range(11):
                x = int(44 + beam_index * ((self.display.screen_width - 88) / 10))
                pygame.draw.line(
                    rig_surface,
                    (118, 118, 128, 188),
                    (x, 0),
                    (x, 36),
                    2,
                )
            self.display.screen.blit(rig_surface, rig_rect.topleft)

            beam_targets = [
                (center[0] - 132, stage_y),
                (center[0] - 52, stage_y - 18),
                (center[0], stage_y - 30),
                (center[0] + 58, stage_y - 18),
                (center[0] + 140, stage_y),
            ]
            beam_origins = [
                self.display.screen_width * 0.12,
                self.display.screen_width * 0.28,
                self.display.screen_width * 0.5,
                self.display.screen_width * 0.72,
                self.display.screen_width * 0.88,
            ]
            beam_colors = [warm_gold, cool_white, copper, cool_white, warm_gold]
            for index, (origin_x, target, beam_color) in enumerate(
                zip(beam_origins, beam_targets, beam_colors)
            ):
                motion = math.sin(phase * (0.9 + index * 0.12) + index * 0.8)
                shifted_target = (
                    target[0] + int(motion * (24 if index != 2 else 12) * sweep),
                    target[1],
                )
                draw_spotlight(
                    origin_x,
                    shifted_target,
                    spread=72 + index * 10,
                    color=beam_color,
                    alpha=92 + index * 12,
                    top_width=12 + index * 3,
                )
                fixture_radius = 11 + (2 if index == 2 else 0)
                pygame.draw.circle(
                    self.display.screen,
                    (28, 28, 30),
                    (int(origin_x), 48),
                    fixture_radius + 6,
                )
                pygame.draw.circle(
                    self.display.screen,
                    beam_color,
                    (int(origin_x), 48),
                    fixture_radius,
                )
                self.draw_glow_circle(
                    (int(origin_x), 48),
                    fixture_radius - 2,
                    beam_color,
                    glow_radius=28,
                    alpha=118,
                )

            haze_surface = pygame.Surface(
                (self.display.screen_width, self.display.screen_height),
                pygame.SRCALPHA,
            )
            for haze_index in range(10):
                haze_progress = (progress * 0.55 + haze_index * 0.11) % 1.14
                haze_width = 180 + haze_index * 22
                haze_height = 30 + (haze_index % 3) * 8
                haze_alpha = max(
                    0, int((26 - haze_index) * reveal * (1.08 - haze_progress))
                )
                if haze_alpha <= 0:
                    continue
                haze_center = (
                    int(center[0] + math.sin(phase * 0.38 + haze_index * 0.7) * 180),
                    int(stage_y - 220 + haze_index * 22 - haze_progress * 90),
                )
                pygame.draw.ellipse(
                    haze_surface,
                    (255, 234, 202, haze_alpha),
                    pygame.Rect(
                        haze_center[0] - haze_width // 2,
                        haze_center[1] - haze_height // 2,
                        haze_width,
                        haze_height,
                    ),
                )
            self.display.screen.blit(haze_surface, (0, 0))

            draw_floor_reflection(
                (center[0], stage_y + 16), 220, 108, warm_gold, int(148 * reveal)
            )
            draw_floor_reflection(
                (center[0], stage_y + 6), 108, 58, cool_white, int(88 * reveal)
            )

            for dust_index in range(28):
                dust_phase = (progress * 0.8 + dust_index * 0.037) % 1.0
                dust_x = (
                    center[0]
                    - 180
                    + (dust_index % 7) * 58
                    + math.sin(phase * 0.7 + dust_index) * 10
                )
                dust_y = stage_y - 260 + (dust_index // 7) * 46 - dust_phase * 30
                self.draw_glow_circle(
                    (int(dust_x), int(dust_y)),
                    2,
                    WHITE,
                    glow_radius=6,
                    alpha=max(24, int(72 * reveal * (1.0 - dust_phase * 0.4))),
                )

            draw_bottle_silhouette((center[0], stage_y - 98), reveal, phase)

            self.display.ui.draw_screen_frame(
                phase,
                accent_color=warm_gold,
                secondary_color=(255, 234, 188),
            )
            title_alpha = self.clamp((progress - 0.26) / 0.34)
            if title_alpha > 0:
                title_rect = pygame.Rect(center[0] - 248, 96, 496, 72)
                title_surface = pygame.Surface(title_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    title_surface,
                    (18, 12, 6, int(188 * title_alpha)),
                    title_surface.get_rect(),
                    border_radius=24,
                )
                pygame.draw.rect(
                    title_surface,
                    (255, 255, 255, int(18 * title_alpha)),
                    (12, 10, title_rect.width - 24, 22),
                    border_radius=14,
                )
                self.display.screen.blit(title_surface, title_rect.topleft)
                self.display.ui.draw_chrome_rect(title_rect, GOLD_COLORS, 22, 3)
                self.display.ui.draw_text_with_shadow(
                    "BOUTEILLE",
                    self.display.font_title_small,
                    (255, 245, 224),
                    BLACK,
                    (title_rect.centerx, title_rect.top + 24),
                    center=True,
                )
                self.display.ui.draw_text_with_shadow(
                    "Spotlight reveal",
                    self.display.font_small,
                    warm_gold,
                    BLACK,
                    (title_rect.centerx, title_rect.bottom - 18),
                    center=True,
                )

            cue_alpha = self.clamp((progress - 0.62) / 0.22)
            if cue_alpha > 0:
                cue_rect = pygame.Rect(center[0] - 180, stage_y + 54, 360, 34)
                cue_surface = pygame.Surface(cue_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    cue_surface,
                    (12, 10, 8, int(170 * cue_alpha)),
                    cue_surface.get_rect(),
                    border_radius=16,
                )
                self.display.screen.blit(cue_surface, cue_rect.topleft)
                self.display.ui.draw_text_with_shadow(
                    "Le spot s'ouvre avant le clip",
                    self.display.font_verysmall,
                    WHITE,
                    BLACK,
                    cue_rect.center,
                    center=True,
                )

            self.draw_cinematic_bars(
                0.24 + progress * 0.22,
                color=(6, 4, 2),
                max_height=42,
                reveal_portion=0.22,
            )

        return self.animate_scene(1.18, render, background=backdrop, fps=60)

    def _animation_bottle_procedural(self):
        self.play_sound_cue("bottle_sound", volume=0.85)
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
            phase = time.monotonic()
            self.trigger_cue(
                cues_triggered,
                "pop",
                0.18,
                progress,
                "applause",
                volume=0.24,
                fade_ms=30,
            )
            anticipation = self.clamp(progress / 0.16)
            launch = self.clamp((progress - 0.12) / 0.22)
            settle = self.clamp((progress - 0.54) / 0.26)
            wobble = math.sin(progress * math.tau * 3.8) * (1 - progress) * 16
            bottle_bounce = self.lerp(24, -18, self.ease_out_back(launch))
            bottle_bounce += math.sin(settle * math.tau * 1.2) * (1 - settle) * 10
            bottle_center = (center[0], center[1] + int(bottle_bounce))
            self.draw_overlay((40, 20, 0), 90)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.8, tint=(255, 214, 156)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.79, tint=(255, 186, 86), alpha=22
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(255, 214, 110),
                secondary_color=(255, 168, 92),
            )
            self.display.ui.draw_scene_badges("BONUS", "BOUTEILLE", phase)
            self.draw_cinematic_bars(
                progress * 0.7, color=(8, 4, 0), max_height=34, reveal_portion=0.24
            )
            self.draw_vignette(86, (18, 8, 0))
            self.draw_party_ribbons(
                progress,
                palette=[(255, 214, 110), (255, 166, 86), (255, 244, 214)],
                alpha=24,
                speed=0.7,
            )
            self.draw_crowd_bounce(progress * 0.85)
            self.draw_light_beam(center, progress, (255, 196, 64), width=250, alpha=54)
            self.draw_cartoon_flash(
                center, min(1.0, progress * 0.92), (255, 214, 96), radius=220, alpha=78
            )
            self.draw_star_field(
                progress, density=18, color=(255, 220, 130), drift=10, alpha=80
            )
            self.draw_speed_lines(
                progress, (255, 214, 96), count=7, alpha=42, angle=0.1
            )
            self.draw_bubble_fountain(
                (center[0], center[1] + 120),
                progress,
                color=(255, 244, 220),
                count=24,
                width=190,
                height=340,
                sway=20,
            )
            self.draw_confetti_fountain(
                (center[0], center[1] + 184),
                self.clamp((progress - 0.18) / 0.42),
                palette=[(255, 214, 110), (255, 170, 86), WHITE],
                count=18,
                spread=220,
                height=170,
                alpha=180,
            )
            self.draw_radial_burst(
                center,
                min(1.0, progress * 1.1),
                YELLOW,
                particle_count=18,
                distance=170,
                size=9,
                rotation=progress,
            )

            header_rect = pygame.Rect(center[0] - 250, 90, 500, 86)
            self.display.ui.draw_panel_shadow(
                header_rect,
                alpha=96,
                inflate=22,
                offset=(0, 12),
                border_radius=28,
            )
            header_surface = pygame.Surface(header_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                header_surface,
                (44, 24, 6, 220),
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
                color=(255, 214, 110),
                alpha=10,
                step=58,
            )
            self.display.ui.draw_chrome_rect(header_rect, GOLD_COLORS, 24, 4)
            self.display.ui.draw_badge(
                "SPECIAL",
                (header_rect.centerx - 54, header_rect.top - 12, 108, 24),
                (255, 214, 82, 224),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )
            self.display.ui.draw_text_with_shadow(
                "BOUTEILLE",
                self.display.font_title_small,
                (255, 248, 222),
                BLACK,
                (header_rect.centerx, header_rect.top + 30),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                "Le bonus mousse monte a la scene",
                self.display.font_small,
                YELLOW,
                BLACK,
                (header_rect.centerx, header_rect.bottom - 20),
                center=True,
            )

            podium_rect = pygame.Rect(center[0] - 168, center[1] + 170, 336, 58)
            self.display.ui.draw_panel_shadow(
                podium_rect,
                alpha=90,
                inflate=20,
                offset=(0, 12),
                border_radius=24,
            )
            podium_surface = pygame.Surface(podium_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                podium_surface,
                (26, 14, 4, 208),
                podium_surface.get_rect(),
                border_radius=24,
            )
            pygame.draw.rect(
                podium_surface,
                (255, 255, 255, 12),
                (12, 8, podium_rect.width - 24, 18),
                border_radius=12,
            )
            self.display.screen.blit(podium_surface, podium_rect.topleft)
            self.display.ui.draw_panel_grid(
                podium_rect.inflate(-18, -12),
                phase + 0.6,
                color=(255, 214, 110),
                alpha=9,
                step=52,
            )
            self.display.ui.draw_chrome_rect(podium_rect, CHROME_COLORS, 22, 3)
            self.display.ui.draw_marquee_lights(
                podium_rect,
                phase,
                (255, 214, 110),
                count=12,
                radius=3,
            )

            bottle_surface = pygame.Surface((220, 420), pygame.SRCALPHA)
            body_rect = pygame.Rect(45, 105, 130, 250)
            neck_rect = pygame.Rect(82, 40, 56, 92)
            pygame.draw.rect(
                bottle_surface, (65, 42, 10, 220), body_rect, border_radius=36
            )
            pygame.draw.rect(
                bottle_surface, (82, 54, 14, 220), neck_rect, border_radius=16
            )
            pygame.draw.rect(
                bottle_surface, (220, 170, 40, 235), (82, 24, 56, 24), border_radius=8
            )
            fill_height = int(170 + 120 * self.ease_out_cubic(progress))
            fill_rect = pygame.Rect(
                58, body_rect.bottom - fill_height, 104, fill_height
            )
            pygame.draw.rect(
                bottle_surface, (236, 176, 42, 195), fill_rect, border_radius=28
            )
            shine_rect = pygame.Rect(66, 118, 28, 216)
            pygame.draw.rect(
                bottle_surface,
                (255, 248, 220, 74),
                shine_rect,
                border_radius=16,
            )
            label_rect = pygame.Rect(60, 164, 100, 94)
            pygame.draw.rect(
                bottle_surface,
                (246, 222, 164, 228),
                label_rect,
                border_radius=22,
            )
            pygame.draw.rect(
                bottle_surface,
                (168, 98, 24, 214),
                label_rect,
                width=3,
                border_radius=22,
            )
            eye_blink = self.clamp((math.sin(progress * math.tau * 6.5) - 0.7) / 0.3)
            smile_curve = 0.35 + 0.65 * self.ease_out_cubic(progress)
            for eye_x in (92, 128):
                pygame.draw.circle(
                    bottle_surface, (255, 255, 255, 240), (eye_x, 196), 11
                )
                pygame.draw.circle(bottle_surface, BLACK, (eye_x + 1, 197), 5)
                if eye_blink > 0:
                    pygame.draw.rect(
                        bottle_surface,
                        (246, 222, 164, 228),
                        (eye_x - 12, 184, 24, int(22 * eye_blink)),
                        border_radius=10,
                    )
            mouth_rect = pygame.Rect(0, 0, 48, 24)
            mouth_rect.center = (110, 226)
            pygame.draw.arc(
                bottle_surface,
                (148, 72, 14),
                mouth_rect,
                0.15,
                math.pi - 0.15,
                max(3, int(4 + smile_curve * 2)),
            )
            pygame.draw.circle(bottle_surface, (255, 170, 190, 84), (82, 220), 9)
            pygame.draw.circle(bottle_surface, (255, 170, 190, 84), (138, 220), 9)
            label_text = self.display.font_verysmall.render("FIZZ!", True, BLACK)
            bottle_surface.blit(label_text, label_text.get_rect(center=(110, 246)))

            foam_y = fill_rect.top - 12
            for bubble_index in range(6):
                bubble_x = (
                    68 + bubble_index * 17 + math.sin(progress * 12 + bubble_index) * 5
                )
                pygame.draw.circle(
                    bottle_surface,
                    (255, 244, 215, 225),
                    (int(bubble_x), int(foam_y)),
                    11,
                )

            bottle_surface = pygame.transform.rotate(bottle_surface, wobble)
            self.draw_motion_smear(
                (center[0] - 52, center[1] + 10),
                (bottle_center[0] + wobble * 2.8, bottle_center[1] - 8),
                min(1.0, abs(wobble) / 12),
                (255, 224, 150),
                width=44,
                trail=4,
                alpha=36,
            )
            self.draw_glow_circle(bottle_center, 102, YELLOW, glow_radius=52, alpha=164)
            self.display.screen.blit(
                bottle_surface, bottle_surface.get_rect(center=bottle_center)
            )

            cap_progress = self.clamp((progress - 0.08) / 0.3)
            cap_center = (
                center[0] + int(math.sin(progress * math.tau * 6) * 18),
                center[1] - 170 - int(140 * self.ease_out_cubic(cap_progress)),
            )
            if cap_progress > 0:
                pygame.draw.circle(self.display.screen, (232, 184, 52), cap_center, 16)
                pygame.draw.circle(self.display.screen, WHITE, cap_center, 16, width=2)
                self.draw_cartoon_starburst(
                    cap_center,
                    cap_progress,
                    (255, 220, 120),
                    rays=9,
                    inner_radius=14,
                    outer_radius=86,
                    alpha=215,
                    twist=0.18,
                )
                self.draw_cartoon_smoke(
                    cap_center,
                    cap_progress,
                    color=(255, 248, 224),
                    puff_count=9,
                    spread=92,
                    alpha=168,
                )
                self.draw_liquid_splash(
                    (center[0], center[1] - 138),
                    cap_progress,
                    (255, 226, 150),
                    droplet_count=15,
                    spread=134,
                    height=210,
                    alpha=188,
                )
                self.draw_confetti_fountain(
                    (center[0], center[1] - 58),
                    cap_progress,
                    palette=[(255, 214, 110), (255, 244, 214), (255, 170, 86)],
                    count=14,
                    spread=150,
                    height=120,
                    alpha=174,
                )
                self.draw_impact_cloud(
                    cap_center,
                    cap_progress,
                    color=(255, 224, 148),
                    puff_count=6,
                    spread=52,
                    alpha=84,
                    y_scale=0.52,
                )
                self.draw_sticker_burst(
                    cap_center,
                    cap_progress,
                    [YELLOW, WHITE, (255, 196, 86)],
                    count=6,
                    distance=70,
                    size=12,
                    twist=0.5,
                )

            if anticipation < 1.0:
                shake_progress = self.ease_out_cubic(anticipation)
                self.draw_comic_caption(
                    "SHAKE!",
                    (center[0] - 168, center[1] - 132),
                    shake_progress,
                    fill_color=(255, 232, 164),
                    outline_color=(188, 120, 20),
                    wobble=12.0,
                )

            for droplet_index in range(10):
                local = self.clamp((progress - droplet_index * 0.03) / 0.42)
                if local <= 0:
                    continue
                droplet_x = (
                    center[0]
                    - 50
                    + droplet_index * 12
                    + math.sin(droplet_index + progress * 8) * 10
                )
                droplet_y = center[1] - 120 - int(local * 180) + droplet_index * 6
                self.draw_glow_circle(
                    (int(droplet_x), int(droplet_y)),
                    4,
                    WHITE,
                    glow_radius=10,
                    alpha=max(40, int(140 * (1 - local * 0.6))),
                )

            for bubble_index in range(18):
                local = (progress * 1.4 + bubble_index * 0.06) % 1.1
                bubble_x = (
                    center[0]
                    - 70
                    + (bubble_index % 6) * 28
                    + math.sin(bubble_index + progress * 8) * 10
                )
                bubble_y = center[1] + 140 - local * 320
                bubble_radius = 4 + (bubble_index % 3) * 2
                bubble_surface = pygame.Surface(
                    (bubble_radius * 4, bubble_radius * 4), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    bubble_surface,
                    (255, 244, 210, max(40, int(170 * (1 - local * 0.7)))),
                    (bubble_radius * 2, bubble_radius * 2),
                    bubble_radius,
                    width=2,
                )
                self.display.screen.blit(bubble_surface, (bubble_x, bubble_y))

            self.draw_comic_caption(
                "POPFIZZ!",
                (center[0] + 170, center[1] - 120),
                min(1.0, progress * 1.1),
                fill_color=(255, 238, 176),
                outline_color=(188, 120, 20),
                wobble=10.0,
            )
            footer_rect = pygame.Rect(center[0] - 236, center[1] + 238, 472, 46)
            self.display.ui.draw_panel_shadow(
                footer_rect,
                alpha=72,
                inflate=16,
                offset=(0, 10),
                border_radius=18,
            )
            footer_surface = pygame.Surface(footer_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                footer_surface,
                (26, 14, 4, 202),
                footer_surface.get_rect(),
                border_radius=18,
            )
            self.display.screen.blit(footer_surface, footer_rect.topleft)
            self.display.ui.draw_chrome_rect(footer_rect, CHROME_COLORS, 18, 3)
            self.display.ui.draw_text_with_shadow(
                "La bouteille explose en mode cartoon.",
                self.display.font_small,
                WHITE,
                BLACK,
                footer_rect.center,
                center=True,
            )
            self.draw_reaction_signs(progress, ["POP!", "FIZZ!", "OLE!"])

        self.animate_scene(1.72, render, background=backdrop)
        self.play_scene_reentry(
            backdrop,
            (255, 214, 110),
            "BONUS VALIDE",
            subtitle="Retour a l'arene",
            duration=0.18,
        )

    def animation_little_frog(self):
        video_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "assets",
                "videos",
                "little_frog.mp4",
            )
        )
        if self.play_video_clip(
            video_path,
            fill_color=(4, 18, 18),
            sound_name="stadium_celebration",
            sound_volume=0.8,
            sound_fade_ms=50,
            fade_out_ms=450,
            intro_fade_ms=240,
            accent_color=(126, 255, 210),
            title="PETITE GRENOUILLE",
            subtitle="Precision, elan et capture parfaite",
        ):
            return
        self._animation_little_frog_procedural()

    def _animation_little_frog_procedural(self):
        backdrop = self.display.screen.copy()
        center = (
            self.display.screen_width // 2 - 10,
            self.display.screen_height // 2 + 34,
        )
        lily_center = (center[0], center[1] + 132)
        fly_center = (center[0] + 240, center[1] - 126)
        cues_triggered = set()

        self.play_sound_cue(
            "stadium_celebration",
            volume=0.72,
            fade_ms=50,
            maxtime=self.LITTLE_FROG_SOUND_MAXTIME_MS,
            stop_existing=True,
        )

        def render(progress):
            phase = time.monotonic()
            self.draw_overlay((3, 20, 18), 126)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.48, tint=(166, 255, 214)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.79, tint=(120, 255, 210), alpha=10
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(120, 255, 210),
                secondary_color=(255, 232, 140),
            )
            self.draw_vignette(76, (2, 18, 12))
            self.draw_cinematic_bars(
                progress, color=(0, 0, 0), max_height=42, reveal_portion=0.2
            )
            self.draw_light_beam(
                (center[0] - 18, center[1] - 30),
                progress,
                (126, 255, 210),
                width=260,
                alpha=34,
            )
            for mist_index in range(3):
                mist_phase = (progress * 0.82 + mist_index * 0.21) % 1.0
                mist_width = 220 + mist_index * 44
                mist_height = 58 + mist_index * 10
                mist_surface = pygame.Surface(
                    (mist_width, mist_height), pygame.SRCALPHA
                )
                pygame.draw.ellipse(
                    mist_surface,
                    (126, 255, 210, max(0, int(28 * (1 - mist_phase * 0.82)))),
                    mist_surface.get_rect(),
                )
                self.display.screen.blit(
                    mist_surface,
                    (
                        center[0]
                        - mist_width // 2
                        + int(math.sin(phase * 0.7 + mist_index) * 18),
                        center[1] + 96 - int(mist_phase * 76) + mist_index * 10,
                    ),
                )
            self.draw_glow_circle(
                (center[0] - 6, center[1] - 48),
                72 + int(progress * 10),
                (120, 255, 210),
                glow_radius=84,
                alpha=34,
            )
            self.draw_aurora_ribbon(
                progress,
                (120, 255, 210),
                base_y=126,
                amplitude=20,
                thickness=5,
                speed=0.5,
                alpha=42,
                phase=0.4,
            )
            self.display.ui.draw_title_panel(
                "PETITE GRENOUILLE",
                "Precision, elan et capture parfaite",
                phase,
                y=88,
            )
            self.display.ui.draw_badge(
                "SPECIAL",
                pygame.Rect(self.display.screen_width // 2 - 54, 76, 108, 24),
                (18, 28, 44, 220),
                text_color=WHITE,
                border_color=(120, 255, 210, 110),
            )
            self.trigger_cue(
                cues_triggered,
                "takeoff",
                0.16,
                progress,
                "applause",
                volume=0.2,
                fade_ms=100,
            )
            self.trigger_cue(
                cues_triggered,
                "catch",
                0.5,
                progress,
                "applause",
                volume=0.5,
                fade_ms=60,
            )
            self.trigger_cue(
                cues_triggered,
                "landing",
                0.72,
                progress,
                "applause",
                volume=0.32,
                fade_ms=40,
            )
            if progress < 0.2:
                crouch = self.ease_in_out_sine(progress / 0.2)
                stretch = 0.0
            elif progress < 0.38:
                crouch = 1.0 - self.ease_out_cubic((progress - 0.2) / 0.18)
                stretch = self.ease_out_back((progress - 0.2) / 0.18)
            elif progress < 0.72:
                crouch = 0.0
                stretch = max(0.12, 0.4 * (1 - (progress - 0.38) / 0.34))
            else:
                crouch = 0.45 * math.sin(((progress - 0.72) / 0.28) * math.pi)
                stretch = 0.0

            flight_progress = self.clamp((progress - 0.22) / 0.48)
            airborne = (
                math.sin(flight_progress * math.pi) if flight_progress > 0 else 0.0
            )
            lift = airborne * 170
            drift_x = self.lerp(-34, 44, flight_progress)
            blink = self.clamp((math.sin(progress * math.tau * 8.5) - 0.76) / 0.24)
            blush = self.clamp(0.12 + airborne * 0.42)
            firefly_pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 6)

            for ripple_index in range(4):
                ripple_progress = progress * 1.4 - ripple_index * 0.16
                if 0 <= ripple_progress <= 1:
                    radius = 58 + int(170 * ripple_progress)
                    alpha = max(0, int(125 * (1 - ripple_progress)))
                    ripple_surface = pygame.Surface(
                        (radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA
                    )
                    pygame.draw.ellipse(
                        ripple_surface,
                        (110, 250, 180, alpha),
                        ripple_surface.get_rect(),
                        width=4,
                    )
                    self.display.screen.blit(
                        ripple_surface,
                        (
                            lily_center[0] - ripple_surface.get_width() // 2,
                            lily_center[1] - ripple_surface.get_height() // 2 + 22,
                        ),
                    )

            self.draw_lily_pad(
                lily_center,
                156,
                rotation=math.sin(progress * math.tau * 1.5) * 4,
                glow=0.28 + airborne * 0.42,
            )
            self.draw_glow_circle(
                lily_center,
                46 + int(airborne * 18),
                (120, 255, 210),
                glow_radius=68,
                alpha=62,
            )
            self.draw_orbiting_particles(
                lily_center,
                progress,
                (120, 255, 180),
                orbit_radius=96,
                count=9,
                size=4,
                speed=0.75,
                vertical_scale=0.4,
            )

            if progress < 0.57:
                self.draw_glow_circle(
                    fly_center, 6 + firefly_pulse * 4, YELLOW, glow_radius=18, alpha=150
                )
                self.draw_orbiting_particles(
                    fly_center,
                    progress,
                    YELLOW,
                    orbit_radius=20 + firefly_pulse * 8,
                    count=4,
                    size=3,
                    speed=2.8,
                    vertical_scale=0.9,
                )
                for wing_index in (-1, 1):
                    wing_surface = pygame.Surface((24, 14), pygame.SRCALPHA)
                    pygame.draw.ellipse(
                        wing_surface, (255, 255, 255, 120), wing_surface.get_rect()
                    )
                    rotated_wing = pygame.transform.rotate(
                        wing_surface, wing_index * (22 + firefly_pulse * 20)
                    )
                    self.display.screen.blit(
                        rotated_wing, rotated_wing.get_rect(center=fly_center)
                    )

            smear_progress = self.clamp((progress - 0.22) / 0.12) * (
                1 - self.clamp((progress - 0.48) / 0.18)
            )
            if smear_progress > 0:
                self.draw_motion_smear(
                    (center[0] - 68, center[1] + 28),
                    (center[0] + int(drift_x), center[1] - int(lift)),
                    smear_progress,
                    (120, 255, 210),
                    width=54,
                    trail=5,
                    alpha=42,
                )

            tongue_window = self.clamp((progress - 0.34) / 0.18)
            tongue_release = self.clamp((progress - 0.56) / 0.14)
            tongue_progress = max(0.0, tongue_window * (1 - tongue_release))
            eye_focus = (0.7, -0.45) if progress < 0.62 else (0.0, 0.0)
            croak = 0.1 + 0.18 * (1 - airborne)
            grin = self.clamp(0.18 + airborne * 0.8 + tongue_progress * 0.35)
            shimmer = 0.18 + firefly_pulse * 0.42

            if tongue_progress > 0:
                tongue_tip = (
                    center[0]
                    + int(drift_x)
                    + int(math.cos(-0.38) * 180 * tongue_progress),
                    center[1]
                    - int(lift)
                    + int(math.sin(-0.38) * 180 * tongue_progress),
                )
                self.draw_motion_smear(
                    (center[0] + int(drift_x) + 18, center[1] - int(lift) - 18),
                    tongue_tip,
                    tongue_progress,
                    (255, 136, 176),
                    width=20,
                    trail=3,
                    alpha=52,
                )
                self.draw_cartoon_flash(
                    tongue_tip,
                    tongue_progress,
                    (255, 136, 176),
                    radius=48,
                    alpha=94,
                )

            self.draw_frog_character(
                (center[0] + int(drift_x), center[1] - int(lift)),
                scale=1.08,
                crouch=crouch,
                stretch=stretch,
                airborne=airborne,
                croak=croak,
                tongue_progress=tongue_progress,
                tongue_angle=-0.38,
                eye_focus=eye_focus,
                glow_strength=0.18 + airborne * 0.28,
                blink=blink,
                grin=grin,
                blush=blush,
                shimmer=shimmer,
            )
            self.draw_glow_circle(
                (center[0] + int(drift_x), center[1] - int(lift) - 24),
                34,
                (214, 255, 232),
                glow_radius=48,
                alpha=20 + int(airborne * 24),
            )

            if progress >= 0.5:
                burst_progress = self.clamp((progress - 0.5) / 0.16)
                self.draw_radial_burst(
                    fly_center,
                    burst_progress,
                    YELLOW,
                    particle_count=10,
                    distance=44,
                    size=6,
                    rotation=progress * 2.0,
                )
                self.draw_impact_cloud(
                    fly_center,
                    burst_progress,
                    color=YELLOW,
                    puff_count=6,
                    spread=40,
                    alpha=82,
                    y_scale=0.58,
                )

            if progress > 0.68:
                landing_progress = self.clamp((progress - 0.68) / 0.18)
                self.draw_cartoon_smoke(
                    lily_center,
                    landing_progress,
                    color=(206, 255, 226),
                    puff_count=8,
                    spread=82,
                    alpha=120,
                )
                self.draw_shockwave(
                    lily_center,
                    landing_progress,
                    (120, 255, 210),
                    start_radius=40,
                    end_radius=180,
                    width=5,
                    y_scale=0.4,
                    alpha=125,
                )
                splash_radius = 70 + int(90 * landing_progress)
                splash_surface = pygame.Surface(
                    (splash_radius * 2 + 12, splash_radius + 28), pygame.SRCALPHA
                )
                pygame.draw.ellipse(
                    splash_surface,
                    (120, 255, 210, max(0, int(150 * (1 - landing_progress)))),
                    splash_surface.get_rect(),
                    width=5,
                )
                self.display.screen.blit(
                    splash_surface,
                    (
                        lily_center[0] - splash_surface.get_width() // 2,
                        lily_center[1] - 10,
                    ),
                )
                self.draw_impact_cloud(
                    lily_center,
                    landing_progress,
                    color=(120, 255, 210),
                    puff_count=8,
                    spread=88,
                    alpha=72,
                    y_scale=0.42,
                )

            if progress > 0.7:
                caption_alpha = self.clamp((progress - 0.7) / 0.18)
                footer_rect = pygame.Rect(
                    center[0] - 184, lily_center[1] + 104, 368, 48
                )
                self.display.ui.draw_panel_shadow(
                    footer_rect,
                    alpha=78,
                    inflate=16,
                    offset=(0, 10),
                    border_radius=18,
                )
                footer_surface = pygame.Surface(footer_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    footer_surface,
                    (8, 24, 44, int(172 * caption_alpha)),
                    footer_surface.get_rect(),
                    border_radius=18,
                )
                pygame.draw.rect(
                    footer_surface,
                    (255, 255, 255, int(18 * caption_alpha)),
                    footer_surface.get_rect(),
                    width=1,
                    border_radius=18,
                )
                self.display.screen.blit(footer_surface, footer_rect.topleft)
                self.display.ui.draw_text_with_shadow(
                    "Capture nette et trajectoire maitrisee",
                    self.display.font_medium,
                    WHITE,
                    BLACK,
                    footer_rect.center,
                    center=True,
                )

        self.animate_scene(1.92, render, background=backdrop)
        self.play_scene_reentry(
            backdrop,
            (126, 255, 210),
            "PETITE GRENOUILLE",
            subtitle="Retour a l'arene",
            duration=0.18,
        )
        frog_sound = self.display.resources.get("frog_sound")
        if frog_sound is not None:
            frog_sound.stop()
