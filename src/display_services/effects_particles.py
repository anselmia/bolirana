# pyright: reportAttributeAccessIssue=false
import math

import pygame

from src.constants import BLACK, GROUP_COLORS, WHITE, YELLOW


class EffectsParticlesMixin:
    def draw_overlay(self, color, alpha):
        overlay = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.get_rgb(color), alpha))
        self.display.screen.blit(overlay, (0, 0))

    def draw_glow_circle(self, center, radius, color, glow_radius=26, alpha=140):
        radius = max(1, int(radius))
        glow_radius = max(1, int(glow_radius))
        extent = radius + glow_radius
        surface = pygame.Surface((extent * 2, extent * 2), pygame.SRCALPHA)
        local_center = (extent, extent)
        red, green, blue = self.get_rgb(color)

        for layer in range(4, 0, -1):
            current_radius = radius + int(glow_radius * layer / 4)
            current_alpha = max(12, alpha // (layer + 1))
            pygame.draw.circle(
                surface,
                (red, green, blue, current_alpha),
                local_center,
                current_radius,
            )

        pygame.draw.circle(surface, (red, green, blue, 235), local_center, radius)
        self.display.screen.blit(surface, (center[0] - extent, center[1] - extent))

    def draw_radial_burst(
        self,
        center,
        progress,
        color,
        particle_count=14,
        distance=160,
        size=8,
        rotation=0.0,
    ):
        red, green, blue = self.get_rgb(color)
        for index in range(particle_count):
            angle = rotation + (index / particle_count) * math.tau
            travel = distance * self.ease_out_cubic(progress)
            particle_x = center[0] + math.cos(angle) * travel
            particle_y = center[1] + math.sin(angle) * travel
            particle_radius = max(2, int(size * (1 - progress * 0.7)))
            particle_alpha = max(0, int(220 * (1 - progress)))
            particle_surface = pygame.Surface(
                (particle_radius * 4, particle_radius * 4), pygame.SRCALPHA
            )
            pygame.draw.circle(
                particle_surface,
                (red, green, blue, particle_alpha),
                (particle_radius * 2, particle_radius * 2),
                particle_radius,
            )
            self.display.screen.blit(
                particle_surface,
                (particle_x - particle_radius * 2, particle_y - particle_radius * 2),
            )

    def draw_confetti(self, progress, density=28):
        for index in range(density):
            column_ratio = (index + 0.5) / density
            sway = math.sin(progress * 10 + index * 1.7) * 18
            x = column_ratio * self.display.screen_width + sway
            y = ((progress * 1.25) + (index * 0.073)) % 1.25
            y = y * self.display.screen_height - 120
            width = 10 + (index % 3) * 2
            height = 18 + (index % 4) * 2
            color = GROUP_COLORS[index % len(GROUP_COLORS)]
            confetti_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(
                confetti_surface,
                (*self.get_rgb(color), 210),
                confetti_surface.get_rect(),
                border_radius=3,
            )
            rotation = math.sin(progress * 12 + index) * 35
            rotated = pygame.transform.rotate(confetti_surface, rotation)
            self.display.screen.blit(rotated, (x, y))

    def draw_vignette(self, alpha=110, color=(0, 0, 0)):
        overlay = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        red, green, blue = self.get_rgb(color)
        max_width = max(
            24, min(self.display.screen_width, self.display.screen_height) // 14
        )
        for layer in range(5):
            inset = layer * (max_width // 4)
            current_alpha = max(0, int(alpha * (1 - layer / 5)))
            pygame.draw.rect(
                overlay,
                (red, green, blue, current_alpha),
                (
                    inset,
                    inset,
                    self.display.screen_width - inset * 2,
                    self.display.screen_height - inset * 2,
                ),
                border_radius=36,
                width=max(4, max_width // 5),
            )
        self.display.screen.blit(overlay, (0, 0))

    def draw_light_beam(
        self, center, progress, color, width=220, height=None, alpha=90
    ):
        height = height or self.display.screen_height
        beam_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        red, green, blue = self.get_rgb(color)
        for layer in range(4, 0, -1):
            beam_width = int(width * (0.18 + layer * 0.18))
            top_width = int(beam_width * (0.18 + 0.08 * progress))
            current_alpha = max(10, int(alpha / (5 - layer)))
            points = [
                (width // 2 - top_width // 2, 0),
                (width // 2 + top_width // 2, 0),
                (width // 2 + beam_width // 2, height),
                (width // 2 - beam_width // 2, height),
            ]
            pygame.draw.polygon(beam_surface, (red, green, blue, current_alpha), points)
        self.display.screen.blit(
            beam_surface, beam_surface.get_rect(midtop=(center[0], 0))
        )

    def draw_orbiting_particles(
        self,
        center,
        progress,
        color,
        orbit_radius=150.0,
        count=10,
        size=6,
        speed=1.4,
        vertical_scale=0.58,
    ):
        for index in range(count):
            angle = progress * math.tau * speed + (index / count) * math.tau
            particle_x = center[0] + math.cos(angle) * orbit_radius
            particle_y = center[1] + math.sin(angle) * orbit_radius * vertical_scale
            particle_size = max(2, int(size + math.sin(angle * 2.0) * 1.5))
            self.draw_glow_circle(
                (int(particle_x), int(particle_y)),
                particle_size,
                color,
                glow_radius=particle_size * 2,
                alpha=120,
            )

    def draw_comet_trail(self, start, end, progress, color, width=4):
        eased = self.ease_out_cubic(progress)
        current_x = self.lerp(start[0], end[0], eased)
        current_y = self.lerp(start[1], end[1], eased)
        tail_x = self.lerp(start[0], current_x, 0.82)
        tail_y = self.lerp(start[1], current_y, 0.82)
        pygame.draw.line(
            self.display.screen,
            (*self.get_rgb(color), 180),
            (tail_x, tail_y),
            (current_x, current_y),
            width,
        )
        self.draw_glow_circle(
            (int(current_x), int(current_y)),
            max(3, width + 1),
            color,
            glow_radius=14,
            alpha=180,
        )

    def draw_cinematic_bars(
        self, progress, color=(0, 0, 0), max_height=72, reveal_portion=0.22
    ):
        red, green, blue = self.get_rgb(color)
        local = self.clamp(progress / max(reveal_portion, 0.01))
        bar_height = int(max_height * self.ease_in_out_sine(local))
        if bar_height <= 0:
            return
        pygame.draw.rect(
            self.display.screen,
            (red, green, blue),
            (0, 0, self.display.screen_width, bar_height),
        )
        pygame.draw.rect(
            self.display.screen,
            (red, green, blue),
            (
                0,
                self.display.screen_height - bar_height,
                self.display.screen_width,
                bar_height,
            ),
        )

    def draw_scanlines(self, alpha=22, spacing=6, color=(255, 255, 255)):
        red, green, blue = self.get_rgb(color)
        overlay = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        for y in range(0, self.display.screen_height, spacing):
            pygame.draw.line(
                overlay,
                (red, green, blue, alpha),
                (0, y),
                (self.display.screen_width, y),
                1,
            )
        self.display.screen.blit(overlay, (0, 0))

    def draw_shockwave(
        self,
        center,
        progress,
        color,
        start_radius=30,
        end_radius=220,
        width=6,
        y_scale=0.62,
        alpha=140,
    ):
        if not 0 <= progress <= 1:
            return
        radius = int(self.lerp(start_radius, end_radius, self.ease_out_cubic(progress)))
        ellipse_rect = pygame.Rect(0, 0, radius * 2, max(20, int(radius * y_scale)))
        ellipse_rect.center = center
        surface = pygame.Surface(
            (ellipse_rect.width + 16, ellipse_rect.height + 16), pygame.SRCALPHA
        )
        draw_rect = surface.get_rect().inflate(-16, -16)
        pygame.draw.ellipse(
            surface,
            (*self.get_rgb(color), max(0, int(alpha * (1 - progress)))),
            draw_rect,
            width=max(1, int(width * (1 - progress * 0.5))),
        )
        self.display.screen.blit(surface, surface.get_rect(center=center))

    def draw_aurora_ribbon(
        self,
        progress,
        color,
        base_y=None,
        amplitude=34,
        thickness=7,
        speed=1.0,
        alpha=65,
        phase=0.0,
    ):
        base_y = (
            base_y if base_y is not None else int(self.display.screen_height * 0.32)
        )
        surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        points = []
        step = max(24, self.display.screen_width // 18)
        for x in range(-step, self.display.screen_width + step, step):
            wave = math.sin(progress * math.tau * speed + x * 0.01 + phase)
            wave += (
                math.sin(progress * math.tau * speed * 0.56 + x * 0.015 + phase * 0.4)
                * 0.4
            )
            y = base_y + wave * amplitude
            points.append((x, y))
        pygame.draw.lines(
            surface, (*self.get_rgb(color), alpha), False, points, thickness
        )
        self.display.screen.blit(surface, (0, 0))

    def draw_star_field(
        self, progress, density=28, color=(255, 255, 255), drift=26, alpha=180
    ):
        red, green, blue = self.get_rgb(color)
        surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        for index in range(density):
            base_x = ((index * 127) % (self.display.screen_width + 120)) - 60
            base_y = ((index * 83) % (self.display.screen_height + 80)) - 40
            twinkle = 0.45 + 0.55 * math.sin(progress * math.tau * 2 + index * 0.9)
            star_alpha = max(0, min(255, int(alpha * self.clamp(twinkle, 0.0, 1.0))))
            x = base_x + math.sin(progress * 3 + index) * drift
            y = base_y + math.cos(progress * 2.2 + index * 0.5) * (drift * 0.35)
            radius = 1 + (index % 3 == 0)
            pygame.draw.circle(
                surface,
                (red, green, blue, star_alpha),
                (int(x), int(y)),
                radius,
            )
        self.display.screen.blit(surface, (0, 0))

    def draw_speed_lines(self, progress, color, count=12, alpha=90, angle=0.0):
        surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        red, green, blue = self.get_rgb(color)
        travel = self.ease_out_cubic(progress)
        for index in range(count):
            row_ratio = (index + 0.5) / count
            start_x = -120 + row_ratio * 80 + math.sin(index * 1.2) * 18
            start_y = row_ratio * self.display.screen_height
            end_x = start_x + 240 + travel * 620
            end_y = start_y + math.sin(angle + index) * 30
            pygame.draw.line(
                surface,
                (red, green, blue, max(0, int(alpha * (1 - row_ratio * 0.45)))),
                (start_x, start_y),
                (end_x, end_y),
                3,
            )
        self.display.screen.blit(surface, (0, 0))

    def draw_comic_caption(
        self,
        text,
        center,
        progress,
        fill_color,
        outline_color=None,
        text_color=None,
        wobble=0.0,
    ):
        local = self.clamp(progress)
        if outline_color is None:
            outline_color = WHITE
        if text_color is None:
            text_color = BLACK
        scale = 0.76 + self.ease_out_back(local) * 0.38
        fade = 1 - max(0.0, local - 0.72) / 0.28
        alpha = max(0, min(255, int(255 * fade)))
        font = self.display.font_medium if len(text) < 10 else self.display.font_small
        text_surface = font.render(text, True, text_color)
        bubble_width = int((text_surface.get_width() + 46) * scale)
        bubble_height = int((text_surface.get_height() + 30) * scale)
        bubble_surface = pygame.Surface(
            (bubble_width + 24, bubble_height + 32), pygame.SRCALPHA
        )
        bubble_rect = bubble_surface.get_rect().inflate(-24, -20)
        pygame.draw.ellipse(
            bubble_surface,
            (*self.get_rgb(fill_color), min(230, alpha)),
            bubble_rect,
        )
        pygame.draw.ellipse(
            bubble_surface,
            (*self.get_rgb(outline_color), alpha),
            bubble_rect,
            width=4,
        )
        tail_points = [
            (bubble_rect.left + 26, bubble_rect.bottom - 6),
            (bubble_rect.left + 54, bubble_rect.bottom + 18),
            (bubble_rect.left + 76, bubble_rect.bottom - 8),
        ]
        pygame.draw.polygon(
            bubble_surface,
            (*self.get_rgb(fill_color), min(230, alpha)),
            tail_points,
        )
        pygame.draw.polygon(
            bubble_surface,
            (*self.get_rgb(outline_color), alpha),
            tail_points,
            width=3,
        )
        shadow_surface = font.render(text, True, BLACK)
        shadow_surface.set_alpha(min(140, alpha))
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=bubble_rect.center)
        bubble_surface.blit(shadow_surface, text_rect.move(2, 2))
        bubble_surface.blit(text_surface, text_rect)
        rotation = math.sin(local * math.tau * 2.2) * wobble
        bubble_surface = pygame.transform.rotate(bubble_surface, rotation)
        self.display.screen.blit(bubble_surface, bubble_surface.get_rect(center=center))

    def draw_party_ribbons(self, progress, palette=None, alpha=52, speed=1.0):
        if palette is None:
            palette = [(255, 214, 110), (120, 220, 255), (132, 255, 186)]
        surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        step = max(30, self.display.screen_width // 18)
        for ribbon_index, color in enumerate(palette):
            points = []
            base_y = 108 + ribbon_index * 86
            thickness = max(4, 10 - ribbon_index * 2)
            for x in range(-step, self.display.screen_width + step, step):
                wave = math.sin(progress * math.tau * speed + x * 0.01 + ribbon_index)
                wave += (
                    math.cos(
                        progress * math.tau * speed * 0.55
                        + x * 0.016
                        + ribbon_index * 0.6
                    )
                    * 0.45
                )
                points.append((x, base_y + wave * (20 + ribbon_index * 8)))
            ribbon_alpha = max(12, int(alpha * (1 - ribbon_index * 0.16)))
            pygame.draw.lines(
                surface,
                (*self.get_rgb(color), ribbon_alpha),
                False,
                points,
                thickness,
            )
        self.display.screen.blit(surface, (0, 0))

    def draw_star_sticker(
        self,
        center,
        size,
        fill_color,
        outline_color=WHITE,
        alpha=220,
        rotation=0.0,
    ):
        size = max(8, int(size))
        surface = pygame.Surface((size * 5, size * 5), pygame.SRCALPHA)
        local_center = surface.get_width() // 2
        points = []
        for index in range(10):
            angle = rotation - math.pi / 2 + index * (math.pi / 5)
            radius = size if index % 2 == 0 else size * 0.46
            points.append(
                (
                    local_center + math.cos(angle) * radius,
                    local_center + math.sin(angle) * radius,
                )
            )
        pygame.draw.polygon(surface, (*self.get_rgb(fill_color), alpha), points)
        pygame.draw.polygon(
            surface, (*self.get_rgb(outline_color), alpha), points, width=3
        )
        self.display.screen.blit(surface, surface.get_rect(center=center))

    def draw_sticker_burst(
        self,
        center,
        progress,
        colors,
        count=8,
        distance=140,
        size=18,
        twist=0.0,
    ):
        local = self.clamp(progress)
        for index in range(count):
            angle = twist + (index / count) * math.tau + local * 0.9
            travel = distance * self.ease_out_back(local)
            sticker_center = (
                center[0] + math.cos(angle) * travel,
                center[1] + math.sin(angle) * travel * 0.72,
            )
            sticker_size = size * (0.7 + 0.3 * math.sin(local * math.tau + index))
            sticker_alpha = max(0, int(215 * (1 - local * 0.6)))
            self.draw_star_sticker(
                sticker_center,
                sticker_size,
                colors[index % len(colors)],
                outline_color=WHITE,
                alpha=sticker_alpha,
                rotation=angle,
            )

    def draw_crowd_bounce(self, progress, baseline=None):
        baseline = baseline if baseline is not None else self.display.screen_height - 24
        surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        glow_palette = [(255, 214, 110), (120, 220, 255), (132, 255, 186)]
        for index in range(12):
            x = int(self.display.screen_width * ((index + 0.5) / 12))
            bounce = math.sin(progress * math.tau * 3.2 + index * 0.8)
            body_top = baseline - 38 - int(max(0, bounce) * 18)
            head_y = body_top - 16
            pygame.draw.circle(surface, (14, 18, 28, 205), (x, head_y), 14)
            pygame.draw.line(
                surface, (18, 22, 34, 215), (x, head_y + 10), (x, baseline), 9
            )
            left_hand = (x - 20, body_top + 6 - int(bounce * 6))
            right_hand = (x + 20, body_top - 10 - int(bounce * 10))
            pygame.draw.line(
                surface, (18, 22, 34, 215), (x, body_top + 8), left_hand, 6
            )
            pygame.draw.line(
                surface, (18, 22, 34, 215), (x, body_top + 4), right_hand, 6
            )
            glow_color = glow_palette[index % len(glow_palette)]
            glow_surface = pygame.Surface((22, 46), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surface,
                (*self.get_rgb(glow_color), 120),
                (8, 4, 6, 36),
                border_radius=4,
            )
            glow_surface = pygame.transform.rotate(
                glow_surface, math.sin(progress * 4 + index) * 28
            )
            surface.blit(glow_surface, glow_surface.get_rect(center=right_hand))
        self.display.screen.blit(surface, (0, 0))

    def draw_impact_cloud(
        self,
        center,
        progress,
        color=(255, 255, 255),
        puff_count=7,
        spread=90,
        alpha=160,
        y_scale=0.68,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        red, green, blue = self.get_rgb(color)
        for index in range(puff_count):
            angle = (index / puff_count) * math.tau + local * 0.5
            travel = spread * self.ease_out_cubic(local)
            puff_center = (
                center[0] + math.cos(angle) * travel,
                center[1] + math.sin(angle) * travel * y_scale,
            )
            puff_radius = max(8, int(24 * (1 - local * 0.45) + (index % 3) * 4))
            puff_alpha = max(0, int(alpha * (1 - local * 0.75)))
            pygame.draw.circle(
                surface,
                (red, green, blue, puff_alpha),
                (int(puff_center[0]), int(puff_center[1])),
                puff_radius,
            )
            pygame.draw.circle(
                surface,
                (255, 255, 255, min(255, puff_alpha + 25)),
                (int(puff_center[0]), int(puff_center[1])),
                max(4, puff_radius // 2),
                width=2,
            )
        self.display.screen.blit(surface, (0, 0))

    def draw_reaction_signs(self, progress, labels, baseline=None):
        baseline = baseline if baseline is not None else self.display.screen_height - 18
        sign_count = min(3, len(labels))
        for index in range(sign_count):
            local = self.clamp((progress - index * 0.08) / 0.3)
            if local <= 0:
                continue
            x = int(self.display.screen_width * (0.24 + index * 0.26))
            bounce = math.sin(local * math.pi)
            pole_top = baseline - int(54 + bounce * 18)
            pygame.draw.line(
                self.display.screen,
                (108, 78, 36),
                (x, baseline),
                (x, pole_top + 18),
                5,
            )
            sign_rect = pygame.Rect(0, 0, 124, 44)
            sign_rect.center = (x, pole_top)
            sign_surface = pygame.Surface(sign_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                sign_surface,
                (255, 250, 220, 228),
                sign_surface.get_rect(),
                border_radius=14,
            )
            pygame.draw.rect(
                sign_surface,
                (90, 54, 20, 220),
                sign_surface.get_rect(),
                border_radius=14,
                width=3,
            )
            label = labels[index]
            font = (
                self.display.font_small
                if len(label) <= 8
                else self.display.font_verysmall
            )
            text_surface = font.render(label, True, BLACK)
            text_rect = text_surface.get_rect(center=sign_surface.get_rect().center)
            sign_surface.blit(text_surface, text_rect)
            rotation = math.sin(progress * 5 + index) * 8
            sign_surface = pygame.transform.rotate(sign_surface, rotation)
            self.display.screen.blit(
                sign_surface, sign_surface.get_rect(center=sign_rect.center)
            )

    def draw_lily_pad(self, center, radius, rotation=0.0, glow=0.0):
        radius = max(20, int(radius))
        pad_surface = pygame.Surface((radius * 3, radius * 2 + 40), pygame.SRCALPHA)
        local_center = (pad_surface.get_width() // 2, pad_surface.get_height() // 2 + 8)

        if glow > 0:
            pygame.draw.ellipse(
                pad_surface,
                (120, 255, 180, int(60 + glow * 90)),
                (20, 18, pad_surface.get_width() - 40, pad_surface.get_height() - 36),
            )

        pygame.draw.ellipse(
            pad_surface,
            (38, 118, 76, 230),
            (24, 24, pad_surface.get_width() - 48, pad_surface.get_height() - 40),
        )
        pygame.draw.ellipse(
            pad_surface,
            (72, 164, 106, 235),
            (38, 34, pad_surface.get_width() - 76, pad_surface.get_height() - 62),
        )
        pygame.draw.line(
            pad_surface,
            (132, 220, 156, 210),
            (local_center[0] - radius + 12, local_center[1] + 8),
            (local_center[0] + radius - 8, local_center[1] - 2),
            3,
        )

        notch_points = [
            (local_center[0], local_center[1] + 6),
            (local_center[0] + radius + 18, local_center[1] - 14),
            (local_center[0] + radius - 10, local_center[1] + 22),
        ]
        pygame.draw.polygon(pad_surface, (0, 0, 0, 0), notch_points)
        rotated = pygame.transform.rotate(pad_surface, rotation)
        self.display.screen.blit(rotated, rotated.get_rect(center=center))

    def draw_frog_character(
        self,
        center,
        scale=1.0,
        crouch=0.0,
        stretch=0.0,
        airborne=0.0,
        croak=0.0,
        tongue_progress=0.0,
        tongue_angle=-0.1,
        eye_focus=(0.0, 0.0),
        heroic=False,
        glow_strength=0.0,
    ):
        scale = max(0.4, scale)
        crouch = self.clamp(crouch)
        stretch = self.clamp(stretch)
        airborne = self.clamp(airborne)
        croak = self.clamp(croak)
        tongue_progress = self.clamp(tongue_progress)
        eye_focus_x = self.clamp(eye_focus[0], -1.0, 1.0)
        eye_focus_y = self.clamp(eye_focus[1], -1.0, 1.0)

        surface = pygame.Surface((int(560 * scale), int(440 * scale)), pygame.SRCALPHA)
        width = surface.get_width()
        height = surface.get_height()
        cx = width // 2
        cy = int(height * 0.56)
        ground_y = int(height * 0.78)

        shadow_width = int((180 + crouch * 30 - stretch * 38) * scale)
        shadow_height = int((38 + crouch * 8) * scale)
        shadow_surface = pygame.Surface(
            (shadow_width * 2, shadow_height * 2), pygame.SRCALPHA
        )
        pygame.draw.ellipse(
            shadow_surface,
            (0, 0, 0, max(20, int(110 * (1 - airborne * 0.7)))),
            shadow_surface.get_rect(),
        )
        surface.blit(shadow_surface, (cx - shadow_width, ground_y - shadow_height // 2))

        if glow_strength > 0:
            glow_radius = int((120 + glow_strength * 40) * scale)
            glow_surface = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surface,
                (110, 255, 170, int(40 + glow_strength * 90)),
                (glow_radius, glow_radius),
                glow_radius,
            )
            surface.blit(
                glow_surface, (cx - glow_radius, cy - glow_radius + int(20 * scale))
            )

        body_width = int((205 + crouch * 24 - stretch * 22) * scale)
        body_height = int((116 - crouch * 24 + stretch * 34) * scale)
        body_rect = pygame.Rect(0, 0, body_width, body_height)
        body_rect.center = (cx, cy + int(18 * scale))
        head_width = int(
            (168 + (18 if heroic else 0) - crouch * 6 + stretch * 12) * scale
        )
        head_height = int(
            (108 + (10 if heroic else 0) - crouch * 8 + stretch * 12) * scale
        )
        head_rect = pygame.Rect(0, 0, head_width, head_height)
        head_rect.center = (cx, cy - int((62 - crouch * 12 - stretch * 8) * scale))

        hip_left = (cx - int(86 * scale), cy + int(36 * scale))
        hip_right = (cx + int(86 * scale), cy + int(36 * scale))
        knee_offset_x = int((70 + crouch * 26 - stretch * 10) * scale)
        knee_offset_y = int((60 + crouch * 32 - stretch * 12) * scale)
        foot_offset_x = int((122 + crouch * 34) * scale)
        foot_offset_y = int((88 + crouch * 22 - stretch * 8) * scale)

        for direction, hip in ((-1, hip_left), (1, hip_right)):
            knee = (hip[0] + direction * knee_offset_x, hip[1] + knee_offset_y)
            foot = (
                hip[0] + direction * foot_offset_x,
                min(ground_y + int(10 * scale), hip[1] + foot_offset_y),
            )
            pygame.draw.line(
                surface, (42, 116, 52, 235), hip, knee, max(8, int(18 * scale))
            )
            pygame.draw.line(
                surface, (56, 138, 64, 235), knee, foot, max(8, int(16 * scale))
            )
            pygame.draw.circle(
                surface, (68, 162, 82, 230), knee, max(8, int(14 * scale))
            )
            pygame.draw.ellipse(
                surface,
                (90, 180, 98, 220),
                (
                    foot[0] - int(24 * scale),
                    foot[1] - int(10 * scale),
                    int(48 * scale),
                    int(20 * scale),
                ),
            )

        arm_y = cy + int(18 * scale)
        hand_y = cy + int((54 + crouch * 10) * scale)
        for direction in (-1, 1):
            shoulder = (cx + direction * int(72 * scale), arm_y)
            elbow = (
                cx + direction * int((102 + crouch * 6) * scale),
                cy + int((44 + crouch * 10 - stretch * 6) * scale),
            )
            hand = (cx + direction * int((118 + crouch * 8) * scale), hand_y)
            pygame.draw.line(
                surface, (56, 148, 70, 220), shoulder, elbow, max(6, int(12 * scale))
            )
            pygame.draw.line(
                surface, (72, 172, 84, 220), elbow, hand, max(6, int(10 * scale))
            )
            pygame.draw.circle(
                surface, (98, 192, 104, 220), hand, max(6, int(11 * scale))
            )

        pygame.draw.ellipse(surface, (50, 142, 68, 240), body_rect)
        pygame.draw.ellipse(
            surface,
            (82, 186, 96, 240),
            body_rect.inflate(-int(24 * scale), -int(22 * scale)),
        )
        belly_rect = body_rect.inflate(-int(78 * scale), -int(42 * scale))
        belly_rect.centery += int(12 * scale)
        pygame.draw.ellipse(surface, (175, 238, 172, 220), belly_rect)

        for spot in (
            (cx - int(46 * scale), cy + int(2 * scale), int(16 * scale)),
            (cx + int(54 * scale), cy - int(10 * scale), int(12 * scale)),
            (cx + int(6 * scale), cy + int(26 * scale), int(14 * scale)),
        ):
            pygame.draw.circle(
                surface, (40, 108, 52, 180), (spot[0], spot[1]), max(4, spot[2])
            )

        if croak > 0:
            croak_radius = int((18 + croak * 36) * scale)
            croak_surface = pygame.Surface(
                (croak_radius * 4, croak_radius * 4), pygame.SRCALPHA
            )
            pygame.draw.circle(
                croak_surface,
                (214, 245, 164, int(70 + croak * 120)),
                (croak_radius * 2, croak_radius * 2),
                croak_radius,
            )
            surface.blit(
                croak_surface,
                (
                    cx - croak_surface.get_width() // 2,
                    head_rect.bottom - int(6 * scale),
                ),
            )

        pygame.draw.ellipse(surface, (56, 152, 72, 245), head_rect)
        pygame.draw.ellipse(
            surface,
            (84, 194, 102, 235),
            head_rect.inflate(-int(20 * scale), -int(18 * scale)),
        )
        eye_stalk_height = int((28 + stretch * 10 + (8 if heroic else 0)) * scale)
        eye_spacing = int((46 + (8 if heroic else 0)) * scale)
        eye_radius = int((18 + (4 if heroic else 0)) * scale)
        eye_y = head_rect.top + int(22 * scale) - eye_stalk_height
        mouth_y = head_rect.centery + int(18 * scale)

        for direction in (-1, 1):
            eye_x = cx + direction * eye_spacing
            stalk_bottom = (
                cx + direction * int(34 * scale),
                head_rect.top + int(18 * scale),
            )
            stalk_top = (eye_x, eye_y + eye_radius)
            pygame.draw.line(
                surface,
                (56, 152, 72, 230),
                stalk_bottom,
                stalk_top,
                max(5, int(10 * scale)),
            )
            pygame.draw.circle(
                surface, (244, 255, 246, 245), (eye_x, eye_y), eye_radius
            )
            iris_radius = max(5, int(eye_radius * 0.52))
            iris_color = YELLOW if heroic else (40, 62, 28)
            pygame.draw.circle(surface, iris_color, (eye_x, eye_y), iris_radius)
            pupil_x = eye_x + int(eye_focus_x * eye_radius * 0.28)
            pupil_y = eye_y + int(eye_focus_y * eye_radius * 0.2)
            pygame.draw.circle(
                surface, BLACK, (pupil_x, pupil_y), max(3, int(eye_radius * 0.28))
            )
            pygame.draw.circle(
                surface,
                (255, 255, 255, 240),
                (eye_x - max(2, eye_radius // 3), eye_y - max(2, eye_radius // 3)),
                max(2, eye_radius // 5),
            )

        mouth_points = [
            (cx - int(34 * scale), mouth_y),
            (cx - int(12 * scale), mouth_y + int((8 + croak * 14) * scale)),
            (cx + int(12 * scale), mouth_y + int((8 + croak * 14) * scale)),
            (cx + int(34 * scale), mouth_y),
        ]
        pygame.draw.lines(
            surface, (28, 80, 38, 240), False, mouth_points, max(3, int(5 * scale))
        )

        if tongue_progress > 0:
            tongue_start = (cx + int(34 * scale), mouth_y - int(2 * scale))
            tongue_length = int(
                self.lerp(0, 180 * scale, self.ease_out_back(tongue_progress))
            )
            tongue_mid = (
                tongue_start[0]
                + int(math.cos(tongue_angle * 0.5) * tongue_length * 0.55),
                tongue_start[1]
                + int(math.sin(tongue_angle * 0.5 - 0.18) * tongue_length * 0.22),
            )
            tongue_tip = (
                tongue_start[0] + int(math.cos(tongue_angle) * tongue_length),
                tongue_start[1] + int(math.sin(tongue_angle) * tongue_length),
            )
            pygame.draw.line(
                surface,
                (214, 68, 118, 225),
                tongue_start,
                tongue_mid,
                max(5, int(10 * scale)),
            )
            pygame.draw.line(
                surface,
                (244, 112, 148, 225),
                tongue_mid,
                tongue_tip,
                max(4, int(8 * scale)),
            )
            pygame.draw.circle(
                surface, (255, 170, 190, 240), tongue_tip, max(6, int(10 * scale))
            )

        self.display.screen.blit(surface, surface.get_rect(center=center))
