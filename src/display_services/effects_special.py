# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame

from src.constants import BLACK, CHROME_COLORS, GOLD_COLORS, WHITE, YELLOW


class EffectsSpecialMixin:
    def animation_bottle(self):
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

    def animation_little_frog(self):
        backdrop = self.display.screen.copy()
        center = (
            self.display.screen_width // 2 - 10,
            self.display.screen_height // 2 + 34,
        )
        lily_center = (center[0], center[1] + 132)
        fly_center = (center[0] + 240, center[1] - 126)
        cues_triggered = set()

        self.play_sound_cue(
            "frog_sound",
            volume=0.72,
            fade_ms=50,
            maxtime=self.LITTLE_FROG_SOUND_MAXTIME_MS,
            stop_existing=True,
        )

        def render(progress):
            phase = time.monotonic()
            self.draw_overlay((3, 26, 20), 95)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.78, tint=(166, 255, 214)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.79, tint=(120, 255, 210), alpha=24
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(120, 255, 210),
                secondary_color=(255, 232, 140),
            )
            self.display.ui.draw_scene_badges("PETITE GRENOUILLE", "SUPER SAUT", phase)
            self.draw_vignette(76, (2, 18, 12))
            self.draw_cinematic_bars(
                progress, color=(0, 0, 0), max_height=42, reveal_portion=0.2
            )
            self.draw_party_ribbons(
                progress,
                palette=[(120, 255, 210), YELLOW, WHITE],
                alpha=26,
                speed=0.8,
            )
            self.draw_light_beam(
                (center[0] - 18, center[1] - 30),
                progress,
                (126, 255, 210),
                width=260,
                alpha=52,
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
            self.draw_speed_lines(
                progress, (120, 255, 210), count=8, alpha=32, angle=0.8
            )
            header_rect = pygame.Rect(center[0] - 246, 88, 492, 86)
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
                (8, 34, 28, 216),
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
                color=(120, 255, 210),
                alpha=10,
                step=56,
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
                "PETITE GRENOUILLE",
                self.display.font_title_small,
                (255, 248, 222),
                BLACK,
                (header_rect.centerx, header_rect.top + 30),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                "Precision, elan et capture parfaite",
                self.display.font_small,
                YELLOW,
                BLACK,
                (header_rect.centerx, header_rect.bottom - 20),
                center=True,
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
            self.draw_crowd_bounce(progress * 0.85)

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
            self.draw_cartoon_flash(
                lily_center,
                min(1.0, progress * 0.88),
                (120, 255, 210),
                radius=160,
                alpha=70,
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
                self.draw_cartoon_starburst(
                    (center[0] - 26, center[1] + 74),
                    smear_progress,
                    (120, 255, 210),
                    rays=7,
                    inner_radius=10,
                    outer_radius=56,
                    alpha=126,
                    twist=0.22,
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
                scale=1.02,
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

            if progress >= 0.5:
                burst_progress = self.clamp((progress - 0.5) / 0.16)
                self.draw_cartoon_starburst(
                    fly_center,
                    burst_progress,
                    (255, 236, 164),
                    rays=8,
                    inner_radius=10,
                    outer_radius=74,
                    alpha=220,
                    twist=0.1,
                )
                self.draw_radial_burst(
                    fly_center,
                    burst_progress,
                    YELLOW,
                    particle_count=10,
                    distance=44,
                    size=6,
                    rotation=progress * 2.0,
                )
                self.draw_comic_caption(
                    "SLURP!",
                    (fly_center[0] + 46, fly_center[1] - 24),
                    burst_progress,
                    fill_color=(255, 232, 164),
                    outline_color=(214, 96, 126),
                    wobble=14.0,
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
                self.draw_sticker_burst(
                    fly_center,
                    burst_progress,
                    [YELLOW, WHITE, (255, 232, 164)],
                    count=6,
                    distance=52,
                    size=10,
                    twist=0.2,
                )
                self.draw_confetti_fountain(
                    fly_center,
                    burst_progress,
                    palette=[YELLOW, WHITE, (255, 170, 190)],
                    count=10,
                    spread=90,
                    height=70,
                    alpha=170,
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
                self.draw_sticker_burst(
                    lily_center,
                    landing_progress,
                    [(120, 255, 210), WHITE, YELLOW],
                    count=7,
                    distance=94,
                    size=12,
                    twist=0.6,
                )
                self.draw_confetti_fountain(
                    (lily_center[0], lily_center[1] + 32),
                    landing_progress,
                    palette=[(120, 255, 210), YELLOW, WHITE],
                    count=12,
                    spread=120,
                    height=92,
                    alpha=160,
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
                    (8, 24, 44, int(188 * caption_alpha)),
                    footer_surface.get_rect(),
                    border_radius=18,
                )
                self.display.screen.blit(footer_surface, footer_rect.topleft)
                self.display.ui.draw_chrome_rect(footer_rect, CHROME_COLORS, 18, 3)
                self.display.ui.draw_marquee_lights(
                    footer_rect,
                    phase + 0.4,
                    (255, 214, 110),
                    count=12,
                    radius=3,
                )
                self.display.ui.draw_text_with_shadow(
                    "Super saut cartoon",
                    self.display.font_medium,
                    WHITE,
                    BLACK,
                    footer_rect.center,
                    center=True,
                )
            self.draw_reaction_signs(progress, ["MIAM!", "BOING!", "HERO!"])

        self.animate_scene(1.92, render, background=backdrop)
        frog_sound = self.display.resources.get("frog_sound")
        if frog_sound is not None:
            frog_sound.stop()
