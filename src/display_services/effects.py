import math
import time

import pygame

from src.constants import (
    BLACK,
    BLUE,
    CHROME_COLORS,
    DARK_BLUE,
    DARK_GREEN,
    DARK_GREY,
    DARK_ORANGE,
    GOAL_ANIMATION_DURATION,
    GOLD_COLORS,
    GROUP_COLORS,
    HOLE_RADIUS,
    LIGHT_GREY,
    RED,
    TEAM_MODE_DUO,
    TEAM_MODE_SOLO,
    TEAM_MODE_TEAM,
    WHITE,
    YELLOW,
)
from src.roulette import RouletteAnimation


class DisplayEffectsService:
    LITTLE_FROG_SOUND_MAXTIME_MS = 1450
    LARGE_FROG_SOUND_MAXTIME_MS = 1750

    def __init__(self, display):
        self.display = display

    def handle_animation_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def wait_with_event_pump(self, seconds):
        end_time = time.monotonic() + seconds
        while time.monotonic() < end_time:
            if not self.handle_animation_events():
                return False
            self.display.clock.tick(30)
        return True

    def ease_out_cubic(self, progress):
        return 1 - (1 - progress) ** 3

    def ease_in_out_sine(self, progress):
        return -(math.cos(math.pi * progress) - 1) / 2

    def ease_out_back(self, progress):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (progress - 1) ** 3 + c1 * (progress - 1) ** 2

    def clamp(self, value, minimum=0.0, maximum=1.0):
        return max(minimum, min(maximum, value))

    def lerp(self, start, end, progress):
        return start + (end - start) * progress

    def get_rgb(self, color):
        if isinstance(color, pygame.Color):
            return color.r, color.g, color.b
        return color[:3]

    def animate_scene(self, duration, renderer, background=None, fps=60):
        start_time = time.monotonic()
        while True:
            if not self.handle_animation_events():
                return False

            progress = min((time.monotonic() - start_time) / duration, 1.0)
            if background is not None:
                self.display.screen.blit(background, (0, 0))

            renderer(progress)
            pygame.display.flip()

            if progress >= 1.0:
                return True

            self.display.clock.tick(fps)

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

    def play_sound_cue(
        self,
        sound_name,
        volume=1.0,
        fade_ms=0,
        maxtime=0,
        stop_existing=False,
    ):
        sound = self.display.resources.get(sound_name)
        if sound is None:
            return
        if stop_existing:
            sound.stop()
        channel = pygame.mixer.find_channel(True)
        if channel is None:
            return
        channel.set_volume(volume)
        channel.play(sound, maxtime=maxtime, fade_ms=fade_ms)
        return channel

    def trigger_cue(
        self,
        tracker,
        cue_name,
        threshold,
        progress,
        sound_name,
        volume=1.0,
        fade_ms=0,
        maxtime=0,
    ):
        if cue_name in tracker or progress < threshold:
            return
        tracker.add(cue_name)
        self.play_sound_cue(
            sound_name,
            volume=volume,
            fade_ms=fade_ms,
            maxtime=maxtime,
        )

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
        score_sound_name = "coin_sound" if hole.type == "side" else "applause"
        score_sound_volume = 0.42 if hole.type == "side" else 0.28
        score_sound_maxtime = 140 if hole.type == "side" else 0

        def render(progress):
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
            badge_surface = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                badge_surface,
                (10, 26, 54, 190),
                badge_surface.get_rect(),
                border_radius=18,
            )
            pygame.draw.rect(
                badge_surface,
                (*self.get_rgb(accent), 110),
                badge_surface.get_rect(),
                border_radius=18,
                width=3,
            )
            self.display.screen.blit(badge_surface, badge_rect.topleft)
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

        self.animate_scene(GOAL_ANIMATION_DURATION, render, background=backdrop)

    def draw_penalty(self):
        self.play_sound_cue("penalty_sound", volume=0.8)
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
            self.trigger_cue(
                cues_triggered,
                "panic",
                0.32,
                progress,
                "applause",
                volume=0.22,
                fade_ms=40,
            )
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 5)
            self.draw_overlay((32, 0, 0), int(120 + 60 * pulse))
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
            self.display.ui.draw_text_with_shadow(
                "PENALITE",
                self.display.font_large,
                WHITE,
                BLACK,
                (center[0] + text_jitter, center[1] - 180),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                "Roulette punitive",
                self.display.font_small,
                YELLOW,
                BLACK,
                (center[0], center[1] + 150),
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
        self.play_sound_cue("applause", volume=0.75, fade_ms=120)
        backdrop = self.display.screen.copy()
        message = f"Bravo {winner}"
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
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
            frame_width = 520 + int(60 * self.ease_out_back(progress))
            frame_rect = pygame.Rect(0, 0, frame_width, 170)
            frame_rect.center = center

            self.draw_overlay((8, 18, 38), 150)
            self.draw_party_ribbons(progress, alpha=36, speed=0.45)
            self.draw_star_field(
                progress, density=26, color=(255, 244, 186), drift=18, alpha=130
            )
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

            frame_surface = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                frame_surface,
                (18, 38, 76, 210),
                frame_surface.get_rect(),
                border_radius=28,
            )
            self.display.screen.blit(frame_surface, frame_rect.topleft)
            self.display.ui.draw_chrome_rect(frame_rect, GOLD_COLORS, 24, 5)

            banner_offset = 28 + int(6 * pulse)
            left_image_rect = self.display.resources["winner_banner"].get_rect(
                midright=(frame_rect.left - banner_offset, frame_rect.centery)
            )
            right_image_rect = self.display.resources["winner_banner"].get_rect(
                midleft=(frame_rect.right + banner_offset, frame_rect.centery)
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
                message,
                self.display.font_large,
                DARK_ORANGE,
                BLACK,
                frame_rect.center,
                shadow_offset=(3, 3),
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

    def draw_win(self, players, team_mode):
        self.play_sound_cue("win_sound", volume=0.95)
        background = self.display.resources["win_background"]
        self.run_fireworks(background)
        cues_triggered = set()

        if team_mode == TEAM_MODE_TEAM:
            groups = self.display.ui.group_players(players, "team")
        elif team_mode == TEAM_MODE_DUO:
            groups = self.display.ui.group_players(players, "team")
        else:
            groups = [players]

        if team_mode in [TEAM_MODE_TEAM, TEAM_MODE_DUO]:
            winner_group = next(
                (
                    group
                    for group in groups
                    if any(player.rank == 1 for player in group)
                ),
                None,
            )
            winner_name = None
            if winner_group:
                winner_name = (
                    f"Team {winner_group[0].team}"
                    if team_mode == TEAM_MODE_TEAM
                    else f"Duo {winner_group[0].team}"
                )
            message = f"Bravo {winner_name}" if winner_group else "Game Over!"
        else:
            winner = next((player for player in players if player.rank == 1), None)
            message = f"Bravo {winner}" if winner else "Game Over!"

        sorted_groups = sorted(
            groups, key=lambda group: min(player.rank for player in group)
        )
        for group in sorted_groups:
            group.sort(key=lambda player: player.rank)

        group_color_map = {
            id(group): GROUP_COLORS[index % len(GROUP_COLORS)]
            for index, group in enumerate(sorted_groups)
        }

        margin_top = 200
        box_height = 40
        gap_between_boxes = 20
        total_height = (
            sum(len(group) for group in sorted_groups)
            * (box_height + gap_between_boxes)
            - gap_between_boxes
        )
        columns = (
            2
            if total_height > self.display.screen.get_height() - margin_top - 50
            else 1
        )

        if columns == 1:
            start_x = self.display.screen_width / 4
            box_width = self.display.screen.get_width() / 2
            hor_gap = 0
        else:
            start_x = self.display.screen_width / 6
            box_width = self.display.screen.get_width() / 3 - 10
            hor_gap = 20

        def render(progress):
            self.trigger_cue(
                cues_triggered,
                "crowd-rise",
                0.22,
                progress,
                "applause",
                volume=0.34,
                fade_ms=80,
            )
            self.trigger_cue(
                cues_triggered,
                "scoreboard-hit",
                0.62,
                progress,
                "applause",
                volume=0.5,
                fade_ms=40,
            )
            self.draw_overlay((4, 10, 30), 62)
            self.draw_star_field(
                0.35 + progress * 0.45,
                density=34,
                color=(255, 248, 220),
                drift=14,
                alpha=118,
            )
            self.draw_party_ribbons(progress, alpha=34, speed=0.4)
            self.draw_aurora_ribbon(
                progress,
                (140, 220, 255),
                base_y=118,
                amplitude=22,
                thickness=5,
                speed=0.32,
                alpha=44,
                phase=0.8,
            )
            self.draw_crowd_bounce(progress)

            title_progress = self.clamp(progress / 0.28)
            title_y = self.lerp(-40, 74, self.ease_out_back(title_progress))
            title_glow_y = self.lerp(
                self.display.screen_height // 2, 110, title_progress
            )

            text_surface = self.display.font_large.render(message, True, DARK_ORANGE)
            text_rect = text_surface.get_rect(
                center=(self.display.screen.get_width() // 2, int(title_y))
            )
            frame_rect = pygame.Rect(
                text_rect.left - 20,
                text_rect.top - 20,
                text_rect.width + 40,
                text_rect.height + 40,
            )
            left_image_rect = self.display.resources["winner_banner"].get_rect(
                midright=(frame_rect.left - 10, frame_rect.centery)
            )
            right_image_rect = self.display.resources["winner_banner"].get_rect(
                midleft=(frame_rect.right + 10, frame_rect.centery)
            )

            self.draw_glow_circle(
                (frame_rect.centerx, int(title_glow_y)),
                26,
                YELLOW,
                glow_radius=54,
                alpha=120,
            )
            self.draw_light_beam(
                (frame_rect.centerx, self.display.screen_height // 2),
                max(0.2, progress),
                YELLOW,
                width=320,
                alpha=40,
            )
            self.display.ui.draw_chrome_rect(frame_rect, GOLD_COLORS, 10, 5)
            self.display.ui.draw_text_with_shadow(
                message,
                self.display.font_large,
                DARK_ORANGE,
                BLACK,
                frame_rect.center,
                shadow_offset=(2, 2),
                center=True,
            )
            self.display.screen.blit(
                self.display.resources["winner_banner"], left_image_rect
            )
            self.display.screen.blit(
                self.display.resources["winner_banner"], right_image_rect
            )
            self.draw_comic_caption(
                "CHAMPIONS!" if team_mode != TEAM_MODE_SOLO else "LEGENDE!",
                (frame_rect.centerx + 170, frame_rect.top + 8),
                min(1.0, progress * 1.1),
                fill_color=(255, 232, 152),
                wobble=8.0,
            )
            self.draw_sticker_burst(
                frame_rect.midtop,
                min(1.0, progress * 1.08),
                [YELLOW, WHITE, (255, 196, 86)],
                count=8,
                distance=86,
                size=13,
                twist=0.1,
            )
            self.draw_reaction_signs(progress, ["CHAMP!", "OLE!", "MAGIQUE!"])

            x = start_x
            y = margin_top
            row_counter = 0
            for index, group in enumerate(sorted_groups):
                group_color = group_color_map[id(group)]
                for player_index, player in enumerate(group):
                    local = self.clamp((progress - 0.18 - row_counter * 0.05) / 0.24)
                    row_counter += 1
                    if local <= 0:
                        y += box_height + gap_between_boxes
                        continue

                    bg_color = (
                        group_color
                        if team_mode != TEAM_MODE_SOLO
                        else DARK_BLUE if player_index % 2 == 0 else DARK_GREY
                    )
                    column_index = 0 if columns == 1 or x == start_x else 1
                    slide = (1 - self.ease_out_back(local)) * (
                        82 if column_index == 0 else -82
                    )
                    reveal_y = self.lerp(y + 16, y, local)
                    row_rect = pygame.Rect(
                        int(x + slide),
                        int(reveal_y),
                        int(box_width),
                        box_height,
                    )

                    panel_surface = pygame.Surface(row_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(
                        panel_surface,
                        (*self.get_rgb(bg_color), 212),
                        panel_surface.get_rect(),
                        border_radius=10,
                    )
                    self.display.screen.blit(panel_surface, row_rect.topleft)
                    self.display.ui.draw_chrome_rect(
                        row_rect,
                        GOLD_COLORS if player.rank == 1 else CHROME_COLORS,
                        10,
                        5,
                    )

                    if player.rank == 1:
                        self.draw_glow_circle(
                            (row_rect.left + 16, row_rect.centery),
                            10,
                            YELLOW,
                            glow_radius=26,
                            alpha=90,
                        )
                        self.draw_impact_cloud(
                            row_rect.center,
                            local,
                            color=YELLOW,
                            puff_count=6,
                            spread=64,
                            alpha=58,
                            y_scale=0.5,
                        )

                    player_label = self.display.font_small.render(
                        str(player), True, WHITE
                    )
                    score_text = self.display.font_medium.render(
                        f"{player.score}", True, WHITE
                    )
                    rank_text = self.display.font_small.render(
                        f"{player.rank}", True, WHITE
                    )
                    self.display.screen.blit(
                        player_label,
                        (
                            row_rect.x + 14,
                            row_rect.y + (box_height - player_label.get_height()) // 2,
                        ),
                    )
                    self.display.screen.blit(
                        score_text,
                        (
                            row_rect.x
                            + (row_rect.width // 2)
                            - (score_text.get_width() // 2),
                            row_rect.y + (box_height - score_text.get_height()) // 2,
                        ),
                    )
                    self.display.screen.blit(
                        rank_text,
                        (
                            row_rect.right - 42,
                            row_rect.y + (box_height - rank_text.get_height()) // 2,
                        ),
                    )
                    y += box_height + gap_between_boxes

                y += gap_between_boxes
                if columns > 1 and index + 1 == math.ceil(len(groups) / 2):
                    x += hor_gap + box_width
                    y = margin_top

        self.animate_scene(1.7, render, background=background)
        self.display.screen.blit(background, (0, 0))
        render(1.0)
        pygame.display.flip()

    def animation_bottle(self):
        self.play_sound_cue("bottle_sound", volume=0.85)
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2)
        cues_triggered = set()

        def render(progress):
            self.trigger_cue(
                cues_triggered,
                "pop",
                0.18,
                progress,
                "applause",
                volume=0.24,
                fade_ms=30,
            )
            wobble = math.sin(progress * math.tau * 3) * (1 - progress) * 14
            self.draw_overlay((40, 20, 0), 90)
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
            self.draw_star_field(
                progress, density=18, color=(255, 220, 130), drift=10, alpha=80
            )
            self.draw_speed_lines(
                progress, (255, 214, 96), count=7, alpha=42, angle=0.1
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
            self.draw_glow_circle(center, 95, YELLOW, glow_radius=46, alpha=150)
            self.display.screen.blit(
                bottle_surface, bottle_surface.get_rect(center=center)
            )

            cap_progress = self.clamp((progress - 0.08) / 0.3)
            cap_center = (
                center[0] + int(math.sin(progress * math.tau * 6) * 18),
                center[1] - 170 - int(140 * self.ease_out_cubic(cap_progress)),
            )
            if cap_progress > 0:
                pygame.draw.circle(self.display.screen, (232, 184, 52), cap_center, 16)
                pygame.draw.circle(self.display.screen, WHITE, cap_center, 16, width=2)
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
                "GLUG GLUG!",
                (center[0] + 170, center[1] - 120),
                min(1.0, progress * 1.1),
                fill_color=(255, 238, 176),
                outline_color=(188, 120, 20),
                wobble=10.0,
            )
            self.draw_reaction_signs(progress, ["POP!", "SANTE!", "HAHA!"])

        self.animate_scene(1.35, render, background=backdrop)

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
            self.draw_overlay((3, 26, 20), 95)
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

            firefly_pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 6)
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

            tongue_window = self.clamp((progress - 0.34) / 0.18)
            tongue_release = self.clamp((progress - 0.56) / 0.14)
            tongue_progress = max(0.0, tongue_window * (1 - tongue_release))
            eye_focus = (0.7, -0.45) if progress < 0.62 else (0.0, 0.0)
            croak = 0.1 + 0.18 * (1 - airborne)

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

            if progress > 0.68:
                landing_progress = self.clamp((progress - 0.68) / 0.18)
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

            if progress > 0.7:
                caption_alpha = self.clamp((progress - 0.7) / 0.18)
                caption_surface = self.display.font_small.render(
                    "Super saut", True, WHITE
                )
                caption_surface.set_alpha(int(255 * caption_alpha))
                caption_rect = caption_surface.get_rect(
                    center=(center[0], lily_center[1] + 128)
                )
                shadow = self.display.font_small.render("Super saut", True, BLACK)
                shadow.set_alpha(int(180 * caption_alpha))
                self.display.screen.blit(shadow, caption_rect.move(2, 2))
                self.display.screen.blit(caption_surface, caption_rect)
            self.draw_reaction_signs(progress, ["MIAM!", "BOING!", "YES!"])

        self.animate_scene(1.55, render, background=backdrop)
        frog_sound = self.display.resources.get("frog_sound")
        if frog_sound is not None:
            frog_sound.stop()

    def animation_large_frog(self):
        backdrop = self.display.screen.copy()
        center = (self.display.screen_width // 2, self.display.screen_height // 2 + 24)
        lily_center = (center[0], center[1] + 154)
        cues_triggered = set()

        self.play_sound_cue(
            "frog_sound",
            volume=0.8,
            fade_ms=50,
            maxtime=self.LARGE_FROG_SOUND_MAXTIME_MS,
            stop_existing=True,
        )

        def render(progress):
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 3.5)
            self.draw_overlay((2, 18, 16), 145)
            self.draw_cinematic_bars(
                progress, color=(0, 0, 0), max_height=58, reveal_portion=0.16
            )
            self.draw_party_ribbons(
                progress,
                palette=[(110, 255, 210), (90, 180, 255), WHITE],
                alpha=28,
                speed=0.5,
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
            self.draw_speed_lines(
                progress, (120, 255, 210), count=10, alpha=42, angle=-0.5
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
            self.trigger_cue(
                cues_triggered,
                "title-hit",
                0.76,
                progress,
                "win_sound",
                volume=0.24,
                fade_ms=100,
            )
            self.draw_crowd_bounce(progress * 0.9)

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
            scale = 0.88 + self.ease_out_back(summon) * 0.38
            crouch = max(0.0, 0.55 * (1 - summon))
            stretch = self.clamp((progress - 0.18) / 0.24) * 0.55
            croak = 0.24 + self.clamp((progress - 0.44) / 0.22) * (0.5 + pulse * 0.2)
            heroic_glow = 0.34 + pulse * 0.4
            eye_focus = (
                (0.0, -0.2)
                if progress <= 0.58
                else (math.sin(progress * 8) * 0.08, -0.34)
            )
            shake_x = math.sin(progress * 70) * 6 if progress > 0.58 else 0
            shake_y = math.cos(progress * 54) * 4 if progress > 0.58 else 0

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
            self.draw_sticker_burst(
                center,
                min(1.0, progress * 1.08),
                [(110, 255, 190), WHITE, YELLOW],
                count=9,
                distance=136,
                size=16,
                twist=0.15,
            )

            if progress > 0.5:
                title_progress = self.clamp((progress - 0.5) / 0.24)
                title_y = self.lerp(
                    center[1] + 214, center[1] + 182, self.ease_out_back(title_progress)
                )
                self.display.ui.draw_text_with_shadow(
                    "ROULETTE",
                    self.display.font_large,
                    YELLOW,
                    BLACK,
                    (center[0], title_y),
                    shadow_offset=(4, 4),
                    center=True,
                )
                subtitle = self.display.font_small.render(
                    "Le boss entre en scene", True, WHITE
                )
                subtitle.set_alpha(int(255 * title_progress))
                subtitle_rect = subtitle.get_rect(center=(center[0], title_y + 44))
                shadow = self.display.font_small.render(
                    "Le boss entre en scene", True, BLACK
                )
                shadow.set_alpha(int(180 * title_progress))
                self.display.screen.blit(shadow, subtitle_rect.move(2, 2))
                self.display.screen.blit(subtitle, subtitle_rect)
                self.draw_comic_caption(
                    "MEGA CROAK!",
                    (center[0] + 190, center[1] - 130),
                    title_progress,
                    fill_color=(212, 255, 176),
                    outline_color=(66, 142, 88),
                    wobble=11.0,
                )
            self.draw_reaction_signs(progress, ["BOSS!", "CROAK!", "RUN!"])

        self.animate_scene(1.9, render, background=backdrop)
        frog_sound = self.display.resources.get("frog_sound")
        if frog_sound is not None:
            frog_sound.stop()
        return self.animation_roulette()

    def animation_roulette(self):
        roulette_animation = RouletteAnimation(
            self.display.screen,
            self.display.resources["roulette_sound"],
            self.display.resources["roulette_end_sound"],
            self.display.resources["roulette_image"],
            self.display.resources["roulette_pointer"],
        )
        return roulette_animation.run()

    def run_fireworks(self, background=None):
        if background is None:
            background = self.display.resources["win_background"]

        palette = [
            (255, 106, 106),
            (255, 196, 86),
            (120, 220, 255),
            (132, 255, 168),
            (255, 142, 214),
        ]
        bursts = []
        for index in range(8):
            bursts.append(
                {
                    "start": index * 0.08,
                    "duration": 0.46 + (index % 3) * 0.06,
                    "center": (
                        int(
                            self.display.screen_width
                            * (0.18 + 0.1 * (index % 5) + (0.05 if index % 2 else 0))
                        ),
                        int(self.display.screen_height * (0.18 + 0.08 * (index % 4))),
                    ),
                    "radius": 150 + (index % 4) * 24,
                    "particles": 18 + (index % 5) * 2,
                    "color": palette[index % len(palette)],
                    "twist": index * 0.31,
                    "launch": (
                        int(self.display.screen_width * (0.1 + (index % 6) * 0.14)),
                        self.display.screen_height + 40,
                    ),
                }
            )

        def render(progress):
            self.draw_overlay((2, 8, 24), 75)
            self.draw_cinematic_bars(
                progress * 0.8, color=(0, 0, 0), max_height=26, reveal_portion=0.3
            )
            self.draw_vignette(66, (0, 4, 18))
            self.draw_party_ribbons(progress, alpha=26, speed=0.35)
            self.draw_star_field(
                progress, density=34, color=(255, 255, 255), drift=20, alpha=120
            )
            self.draw_crowd_bounce(progress)
            self.draw_comic_caption(
                "OOOH!",
                (self.display.screen_width // 2, 120),
                min(1.0, progress * 1.15),
                fill_color=(255, 226, 130),
                wobble=6.0,
            )
            self.draw_reaction_signs(progress, ["OOOH!", "AAAH!", "WOW!"])
            for burst in bursts:
                launch_progress = (progress - burst["start"] * 0.72) / max(
                    0.18, burst["duration"] * 0.34
                )
                if 0 <= launch_progress < 1:
                    self.draw_comet_trail(
                        burst["launch"],
                        burst["center"],
                        launch_progress,
                        burst["color"],
                        width=4,
                    )

                local_progress = (progress - burst["start"]) / burst["duration"]
                if not 0 <= local_progress <= 1:
                    continue
                radius = burst["radius"] * self.ease_out_cubic(local_progress)
                alpha = max(0, int(220 * (1 - local_progress)))
                center = burst["center"]
                color = burst["color"]
                self.draw_shockwave(
                    center,
                    local_progress,
                    color,
                    start_radius=28,
                    end_radius=180,
                    width=4,
                    y_scale=0.8,
                    alpha=100,
                )
                self.draw_glow_circle(
                    center,
                    6 + 18 * (1 - local_progress),
                    color,
                    glow_radius=28,
                    alpha=alpha,
                )

                for particle_index in range(burst["particles"]):
                    angle = (
                        burst["twist"]
                        + particle_index / burst["particles"] * math.tau
                        + local_progress * 0.7
                    )
                    particle_x = center[0] + math.cos(angle) * radius
                    particle_y = center[1] + math.sin(angle) * radius
                    pygame.draw.line(
                        self.display.screen,
                        (*self.get_rgb(color), max(0, alpha // 2)),
                        center,
                        (particle_x, particle_y),
                        2,
                    )
                    particle_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(
                        particle_surface,
                        (*self.get_rgb(color), alpha),
                        (10, 10),
                        max(2, int(5 * (1 - local_progress * 0.5))),
                    )
                    self.display.screen.blit(
                        particle_surface, (particle_x - 10, particle_y - 10)
                    )

        self.animate_scene(1.5, render, background=background)
