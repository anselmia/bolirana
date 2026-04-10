# pyright: reportAttributeAccessIssue=false
import math

import pygame


class EffectsCartoonMixin:
    def draw_cartoon_flash(
        self,
        center,
        progress,
        color,
        radius=180,
        alpha=170,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        progress_bucket = self.get_progress_bucket(local, buckets=10)
        quantized = progress_bucket / 10
        flash_radius = max(12, int(radius * (0.24 + 0.76 * quantized)))
        rgb = self.get_rgb(color)
        flash_surface = self.get_cached_surface(
            "cartoon_flash",
            (flash_radius, rgb, int(alpha), progress_bucket),
            lambda: self._build_cartoon_flash_surface(
                flash_radius,
                rgb,
                alpha,
                quantized,
            ),
        )
        self.display.screen.blit(flash_surface, flash_surface.get_rect(center=center))

    def _build_cartoon_flash_surface(self, flash_radius, rgb, alpha, progress):
        flash_surface = pygame.Surface(
            (flash_radius * 2, flash_radius * 2), pygame.SRCALPHA
        )
        red, green, blue = rgb
        for layer in range(4, 0, -1):
            layer_radius = int(flash_radius * layer / 4)
            layer_alpha = max(0, int(alpha * (1 - progress * 0.72) * (layer / 4)))
            pygame.draw.circle(
                flash_surface,
                (red, green, blue, layer_alpha),
                (flash_radius, flash_radius),
                layer_radius,
            )
        return flash_surface

    def draw_cartoon_starburst(
        self,
        center,
        progress,
        color,
        rays=10,
        inner_radius=18,
        outer_radius=112,
        alpha=220,
        twist=0.0,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        progress_bucket = self.get_progress_bucket(local, buckets=10)
        quantized = progress_bucket / 10
        rgb = self.get_rgb(color)
        burst_surface = self.get_cached_surface(
            "cartoon_starburst",
            (
                outer_radius,
                inner_radius,
                rays,
                rgb,
                int(alpha),
                round(twist, 2),
                progress_bucket,
            ),
            lambda: self._build_cartoon_starburst_surface(
                outer_radius,
                inner_radius,
                rays,
                rgb,
                alpha,
                twist,
                quantized,
            ),
        )
        self.display.screen.blit(burst_surface, burst_surface.get_rect(center=center))

    def _build_cartoon_starburst_surface(
        self,
        outer_radius,
        inner_radius,
        rays,
        rgb,
        alpha,
        twist,
        progress,
    ):
        burst_surface = pygame.Surface(
            (outer_radius * 3, outer_radius * 3), pygame.SRCALPHA
        )
        local_center = burst_surface.get_width() // 2
        points = []
        rotation = twist + progress * 0.55
        for index in range(rays * 2):
            angle = rotation + index * math.pi / rays
            radius = outer_radius if index % 2 == 0 else inner_radius
            radius *= 0.82 + 0.18 * math.sin(progress * math.tau * 2.0 + index)
            points.append(
                (
                    local_center + math.cos(angle) * radius,
                    local_center + math.sin(angle) * radius,
                )
            )
        current_alpha = max(0, int(alpha * (1 - progress * 0.55)))
        pygame.draw.polygon(
            burst_surface,
            (*rgb, current_alpha),
            points,
        )
        pygame.draw.polygon(
            burst_surface,
            (255, 255, 255, min(255, current_alpha + 20)),
            points,
            width=4,
        )
        return burst_surface

    def draw_motion_smear(
        self,
        start,
        end,
        progress,
        color,
        width=40,
        trail=5,
        alpha=60,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        smear_surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        direction_x = end[0] - start[0]
        direction_y = end[1] - start[1]
        length = max(1.0, math.hypot(direction_x, direction_y))
        normal_x = -direction_y / length
        normal_y = direction_x / length
        for layer in range(trail):
            layer_ratio = layer / max(1, trail - 1)
            offset_scale = (1 - layer_ratio) * width
            fade_alpha = max(0, int(alpha * (1 - layer_ratio) * (0.5 + local * 0.5)))
            tail_ratio = max(0.0, local - layer_ratio * 0.12)
            tail_x = self.lerp(start[0], end[0], tail_ratio)
            tail_y = self.lerp(start[1], end[1], tail_ratio)
            points = [
                (
                    start[0] + normal_x * offset_scale,
                    start[1] + normal_y * offset_scale,
                ),
                (
                    start[0] - normal_x * offset_scale,
                    start[1] - normal_y * offset_scale,
                ),
                (
                    tail_x - normal_x * offset_scale * 0.46,
                    tail_y - normal_y * offset_scale * 0.46,
                ),
                (
                    tail_x + normal_x * offset_scale * 0.46,
                    tail_y + normal_y * offset_scale * 0.46,
                ),
            ]
            pygame.draw.polygon(
                smear_surface, (*self.get_rgb(color), fade_alpha), points
            )
        self.display.screen.blit(smear_surface, (0, 0))

    def draw_bubble_fountain(
        self,
        origin,
        progress,
        color=(255, 244, 220),
        count=22,
        width=180,
        height=320,
        sway=18,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        red, green, blue = self.get_rgb(color)
        for index in range(count):
            phase = (local * 1.45 + index * 0.073) % 1.18
            bubble_x = (
                origin[0]
                - width / 2
                + (index / max(1, count - 1)) * width
                + math.sin(local * 8 + index) * sway
            )
            bubble_y = origin[1] + 24 - phase * height
            bubble_radius = 4 + (index % 4)
            bubble_surface = pygame.Surface(
                (bubble_radius * 6, bubble_radius * 6), pygame.SRCALPHA
            )
            center = bubble_surface.get_width() // 2
            bubble_alpha = max(20, int(180 * (1 - phase * 0.62)))
            pygame.draw.circle(
                bubble_surface,
                (red, green, blue, bubble_alpha),
                (center, center),
                bubble_radius * 2,
                width=2,
            )
            pygame.draw.circle(
                bubble_surface,
                (255, 255, 255, min(255, bubble_alpha + 55)),
                (center - 3, center - 3),
                max(2, bubble_radius // 2),
            )
            self.display.screen.blit(
                bubble_surface,
                (bubble_x - center, bubble_y - center),
            )

    def draw_liquid_splash(
        self,
        origin,
        progress,
        color,
        droplet_count=14,
        spread=150,
        height=180,
        alpha=200,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        splash_surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        red, green, blue = self.get_rgb(color)
        arc_height = height * math.sin(local * math.pi)
        for index in range(droplet_count):
            ratio = 0 if droplet_count == 1 else index / (droplet_count - 1)
            angle = -0.9 + ratio * 1.8
            distance = spread * (0.35 + 0.65 * self.ease_out_cubic(local))
            x = origin[0] + math.cos(angle) * distance
            y = (
                origin[1]
                - math.sin(local * math.pi) * arc_height
                + math.sin(angle) * 36
            )
            y -= math.sin(angle) * distance * 0.26
            droplet_radius = 5 + (index % 3) * 2
            pygame.draw.line(
                splash_surface,
                (red, green, blue, max(30, int(alpha * (1 - local * 0.55)))),
                origin,
                (x, y),
                max(2, droplet_radius - 2),
            )
            pygame.draw.circle(
                splash_surface,
                (red, green, blue, max(30, int(alpha * (1 - local * 0.42)))),
                (int(x), int(y)),
                droplet_radius,
            )
            pygame.draw.circle(
                splash_surface,
                (255, 255, 255, max(20, int(alpha * (1 - local * 0.6)))),
                (int(x) - 1, int(y) - 1),
                max(2, droplet_radius // 2),
            )
        self.display.screen.blit(splash_surface, (0, 0))

    def draw_cartoon_smoke(
        self,
        center,
        progress,
        color=(255, 248, 220),
        puff_count=8,
        spread=96,
        alpha=165,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        smoke_surface = pygame.Surface(self.display.screen.get_size(), pygame.SRCALPHA)
        red, green, blue = self.get_rgb(color)
        for index in range(puff_count):
            angle = index / puff_count * math.tau + local * 0.75
            distance = spread * self.ease_out_cubic(local)
            puff_x = center[0] + math.cos(angle) * distance
            puff_y = center[1] + math.sin(angle) * distance * 0.55 - local * 32
            puff_radius = max(10, int(24 + (index % 3) * 6 - local * 8))
            pygame.draw.circle(
                smoke_surface,
                (red, green, blue, max(0, int(alpha * (1 - local * 0.7)))),
                (int(puff_x), int(puff_y)),
                puff_radius,
            )
            pygame.draw.circle(
                smoke_surface,
                (255, 255, 255, max(0, int(alpha * 0.42 * (1 - local * 0.6)))),
                (int(puff_x) - puff_radius // 3, int(puff_y) - puff_radius // 3),
                max(4, puff_radius // 2),
            )
        self.display.screen.blit(smoke_surface, (0, 0))

    def draw_confetti_fountain(
        self,
        origin,
        progress,
        palette=None,
        count=26,
        spread=240,
        height=220,
        alpha=210,
    ):
        local = self.clamp(progress)
        if local <= 0:
            return
        palette = palette or [
            (255, 214, 110),
            (120, 214, 255),
            (255, 132, 176),
            (132, 255, 168),
            (255, 255, 255),
        ]
        for index in range(count):
            ratio = 0.0 if count == 1 else index / (count - 1)
            arc = -0.95 + ratio * 1.9
            distance = spread * (0.22 + 0.78 * local)
            confetti_x = origin[0] + math.cos(arc) * distance
            confetti_y = (
                origin[1]
                - math.sin(local * math.pi) * height
                + math.sin(arc) * 30
                - math.sin(arc) * distance * 0.16
            )
            width = 8 + (index % 3) * 2
            rect_height = 16 + (index % 4) * 2
            rotation = math.degrees(arc) + math.sin(local * 14 + index) * 48
            color = palette[index % len(palette)]
            confetti_surface = pygame.Surface((width, rect_height), pygame.SRCALPHA)
            pygame.draw.rect(
                confetti_surface,
                (*self.get_rgb(color), max(0, int(alpha * (1 - local * 0.52)))),
                confetti_surface.get_rect(),
                border_radius=3,
            )
            rotated = pygame.transform.rotate(confetti_surface, rotation)
            self.display.screen.blit(
                rotated,
                rotated.get_rect(center=(int(confetti_x), int(confetti_y))),
            )
