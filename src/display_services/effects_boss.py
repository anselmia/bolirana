# pyright: reportAttributeAccessIssue=false
import math
import os
import time

import pygame

from src.constants import BLACK, GOLD_COLORS, WHITE, YELLOW
from src.roulette import RouletteAnimation


class EffectsBossMixin:
    def animation_large_frog(self):
        video_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "assets",
                "videos",
                "large_frog.mp4",
            )
        )
        if self.play_video_clip(
            video_path,
            sound_name="stadium_celebration",
            sound_volume=0.8,
            sound_fade_ms=50,
            fade_out_ms=450,
        ):
            return self.animation_roulette()
        return self._animation_large_frog_procedural()

    def _animation_large_frog_procedural(self):
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2 + 24)
        lily_center = (center[0], center[1] + 154)
        cues_triggered = set()

        self.play_sound_cue(
            "stadium_celebration",
            volume=0.8,
            fade_ms=50,
            maxtime=self.LARGE_FROG_SOUND_MAXTIME_MS,
            stop_existing=True,
        )

        def render(progress):
            phase = time.monotonic()
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 3.5)
            blink = self.clamp((math.sin(progress * math.tau * 7.4) - 0.8) / 0.2)
            self.draw_overlay((2, 14, 16), 156)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.52, tint=(166, 255, 214)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.79, tint=(110, 255, 210), alpha=10
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(110, 255, 210),
                secondary_color=(90, 180, 255),
            )
            self.draw_cinematic_bars(
                progress, color=(0, 0, 0), max_height=58, reveal_portion=0.16
            )
            self.draw_aurora_ribbon(
                progress,
                (110, 255, 210),
                base_y=102,
                amplitude=30,
                thickness=7,
                speed=0.42,
                alpha=58,
                phase=0.1,
            )
            self.draw_aurora_ribbon(
                progress,
                (90, 180, 255),
                base_y=138,
                amplitude=22,
                thickness=5,
                speed=0.7,
                alpha=40,
                phase=1.4,
            )
            self.draw_vignette(110, (0, 10, 8))
            self.draw_light_beam(center, progress, (100, 255, 200), width=340, alpha=78)
            self.draw_glow_circle(
                (center[0], center[1] - 36),
                110 + int(pulse * 16),
                (100, 255, 200),
                glow_radius=126,
                alpha=34,
            )
            for fog_index in range(4):
                fog_phase = (progress * 0.9 + fog_index * 0.16) % 1.0
                fog_width = 280 + fog_index * 56
                fog_height = 72 + fog_index * 12
                fog_surface = pygame.Surface((fog_width, fog_height), pygame.SRCALPHA)
                pygame.draw.ellipse(
                    fog_surface,
                    (100, 255, 200, max(0, int(28 * (1 - fog_phase * 0.86)))),
                    fog_surface.get_rect(),
                )
                self.display.screen.blit(
                    fog_surface,
                    (
                        center[0]
                        - fog_width // 2
                        + int(math.sin(phase * 0.5 + fog_index) * 26),
                        lily_center[1] + 20 - int(fog_phase * 112) + fog_index * 8,
                    ),
                )
            self.draw_glow_circle(
                lily_center,
                58 + int(pulse * 12),
                (120, 255, 210),
                glow_radius=88,
                alpha=52,
            )
            self.display.ui.draw_title_panel(
                "GRANDE GRENOUILLE",
                "Le boss arrive avant la roulette",
                phase,
                y=82,
            )
            self.display.ui.draw_badge(
                "BOSS",
                pygame.Rect(self.display.screen_width // 2 - 48, 70, 96, 24),
                (18, 28, 44, 220),
                text_color=WHITE,
                border_color=(110, 255, 210, 110),
            )
            self.trigger_cue(
                cues_triggered,
                "summon",
                0.18,
                progress,
                "applause",
                volume=0.28,
                fade_ms=120,
            )
            self.trigger_cue(
                cues_triggered,
                "boss",
                0.58,
                progress,
                "applause",
                volume=0.8,
                fade_ms=80,
            )
            self.draw_lily_pad(
                lily_center,
                190,
                rotation=math.sin(progress * math.tau * 0.9) * 3,
                glow=0.4 + pulse * 0.3,
            )
            self.draw_orbiting_particles(
                center,
                progress,
                (130, 255, 210),
                orbit_radius=140 + pulse * 50,
                count=14,
                size=5,
                speed=0.95,
                vertical_scale=0.62,
            )

            for mist_index in range(4):
                mist_progress = (progress * 1.1 + mist_index * 0.13) % 1.15
                mist_width = 240 + mist_index * 60
                mist_height = 70 + mist_index * 12
                mist_surface = pygame.Surface(
                    (mist_width, mist_height), pygame.SRCALPHA
                )
                pygame.draw.ellipse(
                    mist_surface,
                    (120, 255, 210, max(0, int(42 * (1 - mist_progress * 0.7)))),
                    mist_surface.get_rect(),
                )
                mist_x = (
                    center[0]
                    - mist_width // 2
                    + math.sin(progress * 4 + mist_index) * 36
                )
                mist_y = lily_center[1] - 26 - mist_progress * 120 + mist_index * 12
                self.display.screen.blit(mist_surface, (mist_x, mist_y))

            for ring_index in range(5):
                ring_progress = progress * 1.45 - ring_index * 0.12
                if 0 <= ring_progress <= 1:
                    radius = 90 + int(240 * self.ease_out_cubic(ring_progress))
                    alpha = max(0, int(140 * (1 - ring_progress)))
                    ring_surface = pygame.Surface(
                        (radius * 2 + 32, radius * 2 + 32), pygame.SRCALPHA
                    )
                    pygame.draw.circle(
                        ring_surface,
                        (70, 255, 180, alpha),
                        (ring_surface.get_width() // 2, ring_surface.get_height() // 2),
                        radius,
                        width=5,
                    )
                    self.display.screen.blit(
                        ring_surface,
                        (
                            center[0] - ring_surface.get_width() // 2,
                            center[1] - ring_surface.get_height() // 2 + 22,
                        ),
                    )

            summon = self.clamp((progress - 0.1) / 0.46)
            airborne = max(0.0, 0.2 * math.sin(summon * math.pi))
            scale = 0.94 + self.ease_out_back(summon) * 0.42
            crouch = max(0.0, 0.55 * (1 - summon))
            stretch = self.clamp((progress - 0.18) / 0.24) * 0.55
            croak = 0.24 + self.clamp((progress - 0.44) / 0.22) * (0.5 + pulse * 0.2)
            heroic_glow = 0.34 + pulse * 0.4
            grin = self.clamp(0.22 + pulse * 0.58)
            blush = self.clamp(0.08 + pulse * 0.18)
            shimmer = 0.24 + pulse * 0.44
            eye_focus = (
                (0.0, -0.2)
                if progress <= 0.58
                else (math.sin(progress * 8) * 0.08, -0.34)
            )
            shake_x = math.sin(progress * 70) * 6 if progress > 0.58 else 0
            shake_y = math.cos(progress * 54) * 4 if progress > 0.58 else 0

            if summon > 0:
                self.draw_motion_smear(
                    (center[0], lily_center[1] + 84),
                    (center[0], center[1] + 18),
                    summon,
                    (120, 255, 210),
                    width=72,
                    trail=6,
                    alpha=52,
                )

            self.draw_frog_character(
                (
                    center[0] + int(shake_x),
                    center[1] - int(airborne * 44) + int(shake_y),
                ),
                scale=scale,
                crouch=crouch,
                stretch=stretch,
                airborne=airborne,
                croak=croak,
                eye_focus=eye_focus,
                heroic=True,
                glow_strength=heroic_glow,
                blink=blink,
                grin=grin,
                blush=blush,
                shimmer=shimmer,
            )
            self.draw_glow_circle(
                (
                    center[0] + int(shake_x),
                    center[1] - int(airborne * 44) - 34 + int(shake_y),
                ),
                44 + int(pulse * 8),
                (210, 255, 234),
                glow_radius=62,
                alpha=24,
            )

            if progress > 0.26:
                bolt_progress = self.clamp((progress - 0.26) / 0.48)
                for bolt_index in range(4):
                    base_angle = (
                        -0.6
                        + bolt_index * 0.4
                        + math.sin(progress * 9 + bolt_index) * 0.08
                    )
                    start_pos = (center[0] + math.cos(base_angle) * 220, 0)
                    mid_pos = (center[0] + math.cos(base_angle) * 110, center[1] - 60)
                    end_pos = (center[0] + math.cos(base_angle) * 40, center[1] + 40)
                    lightning_alpha = max(0, int(180 * (1 - bolt_progress * 0.7)))
                    lightning_surface = pygame.Surface(
                        self.display.screen.get_size(), pygame.SRCALPHA
                    )
                    pygame.draw.lines(
                        lightning_surface,
                        (170, 255, 220, lightning_alpha),
                        False,
                        [start_pos, mid_pos, end_pos],
                        3,
                    )
                    self.display.screen.blit(lightning_surface, (0, 0))

            portal_progress = self.clamp((progress - 0.08) / 0.5)
            self.draw_cartoon_smoke(
                (center[0], lily_center[1] - 8),
                portal_progress,
                color=(210, 255, 236),
                puff_count=10,
                spread=124,
                alpha=138,
            )
            self.draw_impact_cloud(
                (center[0], lily_center[1] - 8),
                portal_progress,
                color=(120, 255, 210),
                puff_count=9,
                spread=112,
                alpha=74,
                y_scale=0.46,
            )
            self.draw_shockwave(
                (center[0], lily_center[1] - 8),
                portal_progress,
                (120, 255, 210),
                start_radius=48,
                end_radius=260,
                width=6,
                y_scale=0.5,
                alpha=135,
            )

            self.draw_radial_burst(
                center,
                min(1.0, progress * 1.08),
                (110, 255, 190),
                particle_count=22,
                distance=220,
                size=10,
                rotation=progress * 3.2,
            )
            self.draw_liquid_splash(
                (center[0], lily_center[1] - 16),
                min(1.0, progress * 0.92),
                (120, 255, 210),
                droplet_count=12,
                spread=168,
                height=150,
                alpha=146,
            )

            if progress > 0.5:
                title_progress = self.clamp((progress - 0.5) / 0.24)
                title_y = self.lerp(
                    center[1] + 214, center[1] + 182, self.ease_out_back(title_progress)
                )
                footer_rect = pygame.Rect(center[0] - 210, int(title_y - 24), 420, 74)
                self.display.ui.draw_panel_shadow(
                    footer_rect,
                    alpha=92,
                    inflate=18,
                    offset=(0, 12),
                    border_radius=22,
                )
                footer_surface = pygame.Surface(footer_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    footer_surface,
                    (8, 24, 44, 184),
                    footer_surface.get_rect(),
                    border_radius=22,
                )
                pygame.draw.rect(
                    footer_surface,
                    (255, 255, 255, 18),
                    footer_surface.get_rect(),
                    width=1,
                    border_radius=22,
                )
                self.display.screen.blit(footer_surface, footer_rect.topleft)
                self.display.ui.draw_text_with_shadow(
                    "ROULETTE",
                    self.display.font_large,
                    YELLOW,
                    BLACK,
                    (footer_rect.centerx, footer_rect.top + 24),
                    shadow_offset=(4, 4),
                    center=True,
                )
                self.display.ui.draw_text_with_shadow(
                    "Le boss entre en scene",
                    self.display.font_small,
                    WHITE,
                    BLACK,
                    (footer_rect.centerx, footer_rect.bottom - 18),
                    center=True,
                )

        self.animate_scene(2.1, render, background=backdrop)
        frog_sound = self.display.resources.get("frog_sound")
        if frog_sound is not None:
            frog_sound.stop()
        return self.animation_roulette()

    def animation_roulette(self):
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
            phase = time.monotonic()
            self.trigger_cue(
                cues_triggered,
                "roulette-rise",
                0.22,
                progress,
                "applause",
                volume=0.24,
                fade_ms=80,
            )
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 4)
            stage_pop = self.clamp((progress - 0.16) / 0.26)
            self.draw_overlay((4, 10, 28), 128)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.92, tint=(255, 224, 164)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.79, tint=(120, 214, 255), alpha=22
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(255, 220, 126),
                secondary_color=(120, 214, 255),
            )
            self.display.ui.draw_scene_badges("ROULETTE", "SHOWTIME", phase)
            self.draw_cartoon_flash(
                center,
                min(1.0, progress * 0.95),
                (255, 220, 126),
                radius=250,
                alpha=94,
            )
            self.draw_star_field(
                progress, density=30, color=(255, 244, 186), drift=14, alpha=118
            )
            self.draw_party_ribbons(progress, alpha=28, speed=0.42)
            self.draw_confetti(progress * 0.85, density=18)
            self.draw_confetti_fountain(
                (center[0], center[1] + 200),
                self.clamp((progress - 0.18) / 0.48),
                palette=[YELLOW, WHITE, (120, 214, 255), (255, 144, 190)],
                count=18,
                spread=230,
                height=160,
                alpha=180,
            )
            self.draw_light_beam(center, progress, YELLOW, width=320, alpha=54)
            self.draw_glow_circle(
                center, 98 + pulse * 18, YELLOW, glow_radius=70, alpha=138
            )
            self.draw_cartoon_starburst(
                center,
                min(1.0, progress * 1.04),
                (255, 220, 126),
                rays=12,
                inner_radius=28,
                outer_radius=164,
                alpha=128,
                twist=0.08,
            )

            frame_rect = pygame.Rect(center[0] - 272, center[1] - 54, 544, 132)
            self.display.ui.draw_panel_shadow(
                frame_rect,
                alpha=114,
                inflate=24,
                offset=(0, 14),
                border_radius=30,
            )
            frame_surface = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                frame_surface,
                (8, 24, 46, 220),
                frame_surface.get_rect(),
                border_radius=30,
            )
            pygame.draw.rect(
                frame_surface,
                (255, 255, 255, 14),
                (14, 12, frame_rect.width - 28, 34),
                border_radius=18,
            )
            self.display.screen.blit(frame_surface, frame_rect.topleft)
            self.display.ui.draw_panel_grid(
                frame_rect.inflate(-18, -16),
                phase,
                color=(120, 214, 255),
                alpha=10,
                step=60,
            )
            self.display.ui.draw_chrome_rect(frame_rect, GOLD_COLORS, 28, 4)
            self.display.ui.draw_marquee_lights(
                frame_rect,
                phase,
                (255, 220, 126),
                count=18,
            )
            self.display.ui.draw_badge(
                "JACKPOT",
                (frame_rect.centerx - 54, frame_rect.top - 12, 108, 24),
                (255, 214, 82, 224),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )
            self.display.ui.draw_text_with_shadow(
                "ROULETTE",
                self.display.font_title_small,
                (255, 248, 222),
                BLACK,
                (frame_rect.centerx, frame_rect.top + 36),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                "Le destin choisit la valeur finale",
                self.display.font_small,
                YELLOW,
                BLACK,
                (frame_rect.centerx, frame_rect.bottom - 24),
                center=True,
            )
            self.draw_sticker_burst(
                frame_rect.midtop,
                min(1.0, progress * 1.18),
                [YELLOW, WHITE, (120, 214, 255)],
                count=8,
                distance=96,
                size=13,
                twist=0.12,
            )
            medallion_center = (center[0], center[1] + 132)
            medallion_surface = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(medallion_surface, (16, 36, 72, 216), (110, 110), 88)
            pygame.draw.circle(
                medallion_surface, (255, 220, 126, 238), (110, 110), 88, width=8
            )
            pygame.draw.circle(medallion_surface, (255, 255, 255, 18), (110, 88), 54)
            self.display.screen.blit(
                medallion_surface,
                medallion_surface.get_rect(center=medallion_center),
            )
            pointer_length = 72 + int(stage_pop * 18)
            pointer_angle = -math.pi / 2 + math.sin(progress * math.tau * 5.4) * 0.18
            pointer_tip = (
                medallion_center[0] + int(math.cos(pointer_angle) * pointer_length),
                medallion_center[1] + int(math.sin(pointer_angle) * pointer_length),
            )
            self.draw_motion_smear(
                medallion_center,
                pointer_tip,
                min(1.0, 0.32 + pulse * 0.68),
                (255, 220, 126),
                width=20,
                trail=3,
                alpha=30,
            )
            pygame.draw.line(
                self.display.screen,
                (255, 220, 126),
                medallion_center,
                pointer_tip,
                6,
            )
            pygame.draw.circle(self.display.screen, WHITE, medallion_center, 10)
            self.draw_comic_caption(
                "SPIN!",
                (center[0] + 192, center[1] + 120),
                min(1.0, progress * 1.14),
                fill_color=(255, 232, 164),
                outline_color=(86, 138, 196),
                wobble=9.0,
            )
            if progress > 0.52:
                hit_progress = self.clamp((progress - 0.52) / 0.2)
                self.draw_cartoon_smoke(
                    medallion_center,
                    hit_progress,
                    color=(255, 244, 214),
                    puff_count=8,
                    spread=92,
                    alpha=126,
                )
                self.draw_shockwave(
                    medallion_center,
                    hit_progress,
                    (255, 220, 126),
                    start_radius=28,
                    end_radius=130,
                    width=5,
                    y_scale=0.9,
                    alpha=118,
                )
            self.draw_reaction_signs(progress, ["SPIN!", "JACKPOT!", "WOW!"])

        self.animate_scene(1.18, render, background=backdrop)
        roulette_animation = RouletteAnimation(
            self.display.screen,
            self.display.resources["roulette_sound"],
            self.display.resources["roulette_end_sound"],
            self.display.resources["roulette_image"],
            self.display.resources["roulette_pointer"],
            self.display.ui,
        )
        return roulette_animation.run()
