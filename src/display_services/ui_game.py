# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame

from src.constants import (
    BLACK,
    CHROME_COLORS,
    DARK_GREEN,
    DARK_GREY,
    DARK_ORANGE,
    GROUP_COLORS,
    HOLE_RADIUS,
    LIGHT_GREY,
    PLAYER_OPTION_COLOR,
    TEAM_MODE_DUO,
    TEAM_MODE_SOLO,
    TEAM_MODE_TEAM,
    WHITE,
    YELLOW,
)


class UIGameMixin:
    GAMEPLAY_CACHE_FPS = 8
    GAMEPLAY_ALERT_CACHE_FPS = 12

    def freeze_challenge_state(self, challenge_state):
        if not challenge_state:
            return None
        challenge_type = challenge_state.get("type")
        if challenge_type == "order":
            return (
                challenge_type,
                int(challenge_state.get("progress", 0)),
                int(challenge_state.get("total", 0)),
                str(challenge_state.get("next_target", "")),
                tuple(challenge_state.get("sequence_labels", [])),
                challenge_state.get("target_hole_type"),
                challenge_state.get("target_hole_text"),
            )
        if challenge_type == "all_holes":
            return (
                challenge_type,
                int(challenge_state.get("progress", 0)),
                int(challenge_state.get("total", 0)),
                int(challenge_state.get("remaining", 0)),
                tuple(challenge_state.get("sequence_labels", [])),
                tuple(challenge_state.get("target_ids", [])),
                tuple(challenge_state.get("completed_targets", [])),
            )
        if challenge_type == "time_attack":
            remaining = challenge_state.get("remaining_seconds")
            remaining_bucket = None if remaining is None else round(float(remaining), 1)
            return (
                challenge_type,
                remaining_bucket,
                int(challenge_state.get("turn_duration", 0)),
                int(challenge_state.get("turns_left", 0) or 0),
                int(challenge_state.get("max_turns", 0) or 0),
                bool(challenge_state.get("awaiting_start")),
                bool(challenge_state.get("low_time")),
            )
        return tuple(sorted(challenge_state.items()))

    def get_players_render_signature(self, players):
        return tuple(
            (
                player.id,
                player.team,
                player.score,
                player.rank,
                player.won,
                player.is_active,
                player.turns_played,
            )
            for player in players
        )

    def get_holes_render_signature(self, holes):
        return tuple(
            (
                hole.type,
                hole.text,
                hole.value,
                getattr(hole, "bonus_active", False),
                getattr(hole, "bonus_active_pin", None),
                round(getattr(hole, "bonus_activated_at", 0.0), 1),
                round(getattr(hole, "bonus_duration", 0.0), 1),
                getattr(hole, "malus_active", False),
                getattr(hole, "malus_active_pin", None),
                round(getattr(hole, "malus_activated_at", 0.0), 1),
                round(getattr(hole, "malus_duration", 0.0), 1),
            )
            for hole in holes
        )

    def get_game_frame_cache_key(
        self,
        players,
        current_player,
        holes,
        score,
        game_mode,
        team_mode,
        player_in_team,
        current_progress,
        leader_progress,
        challenge_mode,
        status_text,
        challenge_state,
    ):
        now = time.monotonic()
        cache_fps = self.GAMEPLAY_ALERT_CACHE_FPS
        if not challenge_state or not challenge_state.get("low_time"):
            cache_fps = self.GAMEPLAY_CACHE_FPS
        animation_bucket = int(now * cache_fps)
        return (
            animation_bucket,
            game_mode,
            team_mode,
            player_in_team,
            int(score),
            int(current_progress),
            int(leader_progress),
            challenge_mode,
            status_text,
            None if current_player is None else current_player.id,
            self.freeze_challenge_state(challenge_state),
            self.get_players_render_signature(players),
            self.get_holes_render_signature(holes),
        )

    def should_draw_status_banner(self, status_text, challenge_state=None):
        if not status_text:
            return False
        normalized = status_text.strip().lower()
        if challenge_state and challenge_state.get("type") == "order":
            target_label = str(challenge_state.get("next_target", "")).strip().lower()
            redundant_messages = {
                f"cible : {target_label}",
                f"prochaine : {target_label}",
            }
            if normalized in redundant_messages:
                return False
        return True

    def get_fitted_font(self, text, fonts, max_width, max_height=None):
        text_value = str(text)
        for font in fonts:
            text_width, text_height = font.size(text_value)
            if text_width <= max_width and (
                max_height is None or text_height <= max_height
            ):
                return font
        return fonts[-1]

    def draw_panel_sheen(self, rect, phase, color, alpha=24, width=None, speed=150):
        target_rect = pygame.Rect(rect)
        if target_rect.width <= 0 or target_rect.height <= 0:
            return
        sheen_surface = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        sheen_width = width or max(48, target_rect.width // 4)
        slant = max(18, target_rect.height // 2)
        sweep_x = int((phase * speed) % (target_rect.width + sheen_width + slant * 2))
        sweep_x -= sheen_width + slant
        base_color = color[:3]
        pygame.draw.polygon(
            sheen_surface,
            (*base_color, alpha),
            [
                (sweep_x, 0),
                (sweep_x + sheen_width, 0),
                (sweep_x + sheen_width + slant, target_rect.height),
                (sweep_x + slant, target_rect.height),
            ],
        )
        pygame.draw.polygon(
            sheen_surface,
            (*base_color, max(8, alpha // 2)),
            [
                (sweep_x + 18, 0),
                (sweep_x + sheen_width - 10, 0),
                (sweep_x + sheen_width + slant - 18, target_rect.height),
                (sweep_x + slant + 10, target_rect.height),
            ],
        )
        self.display.screen.blit(sheen_surface, target_rect.topleft)

    def draw_panel_orbs(self, rect, phase, color, count=3):
        target_rect = pygame.Rect(rect)
        if target_rect.width <= 0 or target_rect.height <= 0:
            return
        orb_surface = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        base_color = color[:3]
        for index in range(count):
            angle = phase * (0.9 + index * 0.12) + index * 1.4
            center_x = int(
                target_rect.width * (0.18 + index * (0.62 / max(1, count - 1)))
                + math.sin(angle) * target_rect.width * 0.04
            )
            center_y = int(
                target_rect.height * (0.2 + (index % 2) * 0.2)
                + math.cos(angle * 1.35) * 8
            )
            radius = max(10, min(18, target_rect.width // 9) - index)
            pygame.draw.circle(
                orb_surface,
                (*base_color, max(10, 18 - index * 3)),
                (center_x, center_y),
                radius,
            )
            pygame.draw.circle(
                orb_surface,
                (255, 255, 255, max(8, 14 - index * 2)),
                (center_x - radius // 3, center_y - radius // 3),
                max(3, radius // 3),
            )
        self.display.screen.blit(orb_surface, target_rect.topleft)

    def draw_arcade_sparkle(self, center, phase, color, radius=9, alpha=144):
        sparkle_size = max(24, radius * 4)
        sparkle_surface = pygame.Surface((sparkle_size, sparkle_size), pygame.SRCALPHA)
        local_center = sparkle_surface.get_rect().center
        pulse = 0.72 + 0.28 * math.sin(phase * 4.8)
        outer = max(4, int(radius * pulse))
        inner = max(2, outer // 3)
        base_color = color[:3]
        line_alpha = max(24, alpha)
        pygame.draw.line(
            sparkle_surface,
            (*base_color, line_alpha),
            (local_center[0] - outer, local_center[1]),
            (local_center[0] + outer, local_center[1]),
            2,
        )
        pygame.draw.line(
            sparkle_surface,
            (*base_color, line_alpha),
            (local_center[0], local_center[1] - outer),
            (local_center[0], local_center[1] + outer),
            2,
        )
        diagonal = max(3, int(outer * 0.72))
        pygame.draw.line(
            sparkle_surface,
            (*base_color, max(18, alpha - 30)),
            (local_center[0] - diagonal, local_center[1] - diagonal),
            (local_center[0] + diagonal, local_center[1] + diagonal),
            1,
        )
        pygame.draw.line(
            sparkle_surface,
            (*base_color, max(18, alpha - 30)),
            (local_center[0] + diagonal, local_center[1] - diagonal),
            (local_center[0] - diagonal, local_center[1] + diagonal),
            1,
        )
        pygame.draw.circle(
            sparkle_surface,
            (255, 255, 255, max(48, alpha + 30)),
            local_center,
            inner,
        )
        self.display.screen.blit(
            sparkle_surface,
            sparkle_surface.get_rect(center=center),
        )

    def draw_active_player_beacon(self, card_rect, group_color, phase):
        beacon_rect = pygame.Rect(card_rect).inflate(32, 26)
        pulse = 0.5 + 0.5 * math.sin(phase * 6.4)
        beacon_surface = pygame.Surface(beacon_rect.size, pygame.SRCALPHA)
        for index, alpha in enumerate((52, 30)):
            inset = index * 8
            pygame.draw.rect(
                beacon_surface,
                (*group_color[:3], int(alpha + pulse * 26)),
                pygame.Rect(
                    inset,
                    inset,
                    beacon_rect.width - inset * 2,
                    beacon_rect.height - inset * 2,
                ),
                border_radius=24 - index * 4,
                width=3,
            )
        self.display.screen.blit(beacon_surface, beacon_rect.topleft)

        rail_width = max(86, min(card_rect.width - 24, 168))
        rail_rect = pygame.Rect(0, 0, rail_width, 18)
        rail_rect.midbottom = (card_rect.centerx, card_rect.top - 4)
        self.draw_badge(
            "A TOI !",
            rail_rect,
            (*group_color[:3], int(198 + pulse * 32)),
            text_color=WHITE,
            border_color=(255, 255, 255, 92),
            font=self.display.font_tiny,
        )

        chevron_y = rail_rect.centery
        for direction in (-1, 1):
            chevron_center_x = rail_rect.centerx + direction * (
                rail_rect.width // 2 + 18
            )
            points = [
                (chevron_center_x, chevron_y),
                (chevron_center_x - direction * 10, chevron_y - 8),
                (chevron_center_x - direction * 10, chevron_y + 8),
            ]
            pygame.draw.polygon(
                self.display.screen,
                (*group_color[:3], int(172 + pulse * 40)),
                points,
            )

        for corner in (
            (card_rect.left - 10, card_rect.top - 10),
            (card_rect.right + 10, card_rect.top - 8),
            (card_rect.left - 8, card_rect.bottom + 8),
            (card_rect.right + 8, card_rect.bottom + 10),
        ):
            self.draw_arcade_sparkle(corner, phase, group_color, radius=8, alpha=132)

    def draw_interface_backdrop_motion(
        self,
        phase,
        player_count,
        challenge_state=None,
    ):
        left_panel_rect = pygame.Rect(
            self.display.frame_space_x,
            self.display.frame_space_y,
            self.display.frame_score_width,
            self.display.hole_rect_height,
        )
        arena_rect = pygame.Rect(
            2 * self.display.frame_space_x + self.display.frame_score_width,
            self.display.frame_space_y,
            self.display.hole_frame_width,
            self.display.hole_rect_height,
        )
        right_panel_rect = pygame.Rect(
            self.display.screen_width
            - self.display.frame_score_width
            - self.display.frame_space_x,
            self.display.frame_space_y,
            self.display.frame_score_width,
            self.display.hole_rect_height,
        )
        dock_rect = self.get_player_dock_rect(
            player_count,
            challenge_state=challenge_state,
        )

        for region_rect, color, count in (
            (left_panel_rect.inflate(26, 26), (124, 255, 190), 4),
            (right_panel_rect.inflate(26, 26), (255, 214, 110), 4),
            (dock_rect.inflate(24, 20), (255, 214, 110), 6),
        ):
            region_surface = pygame.Surface(region_rect.size, pygame.SRCALPHA)
            for index in range(count):
                angle = phase * (0.72 + index * 0.06) + index * 1.3
                center_x = int(
                    region_rect.width * (0.12 + index * (0.74 / max(1, count - 1)))
                    + math.sin(angle) * region_rect.width * 0.05
                )
                center_y = int(
                    region_rect.height * (0.22 + (index % 3) * 0.18)
                    + math.cos(angle * 1.22) * region_rect.height * 0.05
                )
                radius = max(16, min(34, region_rect.width // (8 + index)))
                pygame.draw.circle(
                    region_surface,
                    (*color, max(10, 18 - index)),
                    (center_x, center_y),
                    radius,
                )
                pygame.draw.circle(
                    region_surface,
                    (255, 255, 255, max(8, 12 - index)),
                    (center_x - radius // 3, center_y - radius // 3),
                    max(4, radius // 4),
                )
            self.display.screen.blit(region_surface, region_rect.topleft)

        bubble_rect = dock_rect.inflate(12, 18)
        bubble_surface = pygame.Surface(bubble_rect.size, pygame.SRCALPHA)
        bubble_count = 8
        for bubble_index in range(bubble_count):
            lane_ratio = bubble_index / max(1, bubble_count - 1)
            travel = (phase * (42 + bubble_index * 4) + bubble_index * 46) % (
                bubble_rect.height + 90
            )
            bubble_center = (
                int(
                    24
                    + lane_ratio * (bubble_rect.width - 48)
                    + math.sin(phase * 1.8 + bubble_index) * 18
                ),
                int(bubble_rect.height - travel),
            )
            bubble_radius = 6 + (bubble_index % 3) * 3
            pygame.draw.circle(
                bubble_surface,
                (120, 214, 255, 24),
                bubble_center,
                bubble_radius,
            )
            pygame.draw.circle(
                bubble_surface,
                (255, 255, 255, 34),
                bubble_center,
                bubble_radius,
                width=1,
            )
            pygame.draw.circle(
                bubble_surface,
                (255, 255, 255, 30),
                (
                    bubble_center[0] - bubble_radius // 3,
                    bubble_center[1] - bubble_radius // 3,
                ),
                max(2, bubble_radius // 3),
            )
        self.display.screen.blit(bubble_surface, bubble_rect.topleft)

        sparkle_specs = [
            (
                (left_panel_rect.left + 18, left_panel_rect.top + 18),
                (124, 255, 190),
                0.0,
            ),
            (
                (left_panel_rect.right - 16, left_panel_rect.bottom - 22),
                (120, 214, 255),
                0.6,
            ),
            (
                (right_panel_rect.left + 18, right_panel_rect.top + 18),
                (255, 214, 110),
                0.4,
            ),
            ((dock_rect.centerx, dock_rect.top + 18), (255, 214, 110), 1.0),
        ]
        for (sparkle_x, sparkle_y), color, offset in sparkle_specs:
            self.draw_arcade_sparkle(
                (
                    sparkle_x,
                    sparkle_y + math.sin(phase * 2.3 + offset) * 3,
                ),
                phase + offset,
                color,
                radius=10,
                alpha=150,
            )

    def draw_hud_stat_card(
        self,
        rect,
        label,
        value,
        accent_color,
        value_color=WHITE,
        value_fonts=None,
        align="center",
        value_top_padding=30,
        value_bottom_padding=10,
    ):
        phase = time.monotonic()
        card_rect = pygame.Rect(rect)
        accent_rgb = accent_color[:3]
        content_inset_x = max(12, min(18, card_rect.width // 12))
        content_inset_y = max(6, min(10, card_rect.height // 8))
        self.draw_panel_shadow(
            card_rect,
            alpha=38,
            inflate=10,
            offset=(0, 6),
            border_radius=18,
        )
        card_surface = pygame.Surface(card_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            card_surface,
            (8, 18, 34, 176),
            card_surface.get_rect(),
            border_radius=18,
        )
        pygame.draw.rect(
            card_surface,
            (*accent_rgb, 76),
            (0, 0, 6, card_rect.height),
            border_radius=18,
        )
        pygame.draw.rect(
            card_surface,
            (255, 255, 255, 12),
            (10, 8, card_rect.width - 20, max(10, card_rect.height // 3)),
            border_radius=12,
        )
        pygame.draw.rect(
            card_surface,
            (255, 255, 255, 24),
            card_surface.get_rect(),
            width=1,
            border_radius=18,
        )
        pygame.draw.rect(
            card_surface,
            (*accent_rgb, 90),
            (12, card_rect.height - 6, card_rect.width - 24, 2),
            border_radius=2,
        )
        self.display.screen.blit(card_surface, card_rect.topleft)
        self.draw_panel_grid(
            card_rect.inflate(-12, -10),
            phase,
            color=accent_rgb,
            alpha=5,
            step=48,
        )

        label_fonts = [self.display.font_verysmall]
        for fallback_name in ("font_micro", "font_tiny"):
            fallback_font = getattr(self.display, fallback_name, None)
            if fallback_font is not None:
                label_fonts.append(fallback_font)
        label_font = self.get_fitted_font(
            str(label),
            label_fonts,
            card_rect.width - content_inset_x * 2,
            max(12, card_rect.height // 3),
        )
        label_height = label_font.size(str(label))[1]
        label_top = card_rect.top + content_inset_y
        divider_gap = max(4, min(8, card_rect.height // 10))
        divider_y = label_top + label_height + divider_gap
        divider_y = min(divider_y, card_rect.bottom - max(18, card_rect.height // 3))
        self.draw_text_with_shadow(
            label,
            label_font,
            WHITE,
            BLACK,
            (card_rect.left + content_inset_x, label_top),
            shadow_offset=(1, 1),
        )

        pygame.draw.line(
            self.display.screen,
            (*accent_rgb, 160),
            (card_rect.left + content_inset_x, divider_y),
            (card_rect.right - content_inset_x, divider_y),
            2,
        )

        fonts = value_fonts or [
            self.display.font_large,
            self.display.font_medium,
            self.display.font_small,
            self.display.font_verysmall,
        ]
        for fallback_name in ("font_micro", "font_tiny"):
            fallback_font = getattr(self.display, fallback_name, None)
            if fallback_font is not None and fallback_font not in fonts:
                fonts.append(fallback_font)
        value_area_top = max(
            divider_y + max(4, min(8, card_rect.height // 9)),
            card_rect.top + min(value_top_padding, max(20, card_rect.height // 2 - 6)),
        )
        value_area_bottom = card_rect.bottom - min(
            value_bottom_padding,
            max(8, card_rect.height // 6),
        )
        value_area_height = max(12, value_area_bottom - value_area_top)
        value_font = self.get_fitted_font(
            str(value),
            fonts,
            card_rect.width - content_inset_x * 2,
            value_area_height,
        )
        if align == "left":
            value_position = (
                card_rect.left + content_inset_x,
                value_area_bottom - value_font.get_height(),
            )
            center_text = False
        else:
            value_center_y = value_area_top + value_area_height // 2
            value_position = (card_rect.centerx, value_center_y)
            center_text = True
        self.draw_text_with_shadow(
            str(value),
            value_font,
            value_color,
            BLACK,
            value_position,
            shadow_offset=(2, 2),
            center=center_text,
        )

    def draw_glow_ring(self, center, radius, color, width=4, alpha=130, y_scale=1.0):
        ellipse_width = max(24, int(radius * 2))
        ellipse_height = max(18, int(radius * 2 * y_scale))
        surface = pygame.Surface(
            (ellipse_width + 20, ellipse_height + 20), pygame.SRCALPHA
        )
        rect = surface.get_rect().inflate(-20, -20)
        pygame.draw.ellipse(surface, (*color[:3], alpha), rect, width=max(1, width))
        self.display.screen.blit(surface, surface.get_rect(center=center))

    def draw_special_hole_accent(self, hole, center, phase):
        if hole.type == "little_frog":
            pulse = 0.55 + 0.45 * math.sin(phase * 3.6)
            self.draw_glow_ring(
                center,
                HOLE_RADIUS + 14 + pulse * 8,
                (124, 255, 166),
                width=3,
                alpha=100,
            )
            eye_y = center[1] - HOLE_RADIUS - 10
            for eye_offset in (-10, 10):
                pygame.draw.circle(
                    self.display.screen,
                    (220, 255, 220),
                    (int(center[0] + eye_offset), int(eye_y)),
                    6,
                )
                pygame.draw.circle(
                    self.display.screen,
                    BLACK,
                    (
                        int(center[0] + eye_offset + math.sin(phase * 2.8) * 1.5),
                        int(eye_y + math.cos(phase * 2.4) * 1.2),
                    ),
                    2,
                )
        elif hole.type == "large_frog":
            portal = 0.5 + 0.5 * math.sin(phase * 2.2)
            self.draw_glow_ring(
                center,
                HOLE_RADIUS + 18 + portal * 10,
                (110, 255, 220),
                width=4,
                alpha=110,
            )
            self.draw_glow_ring(
                center,
                HOLE_RADIUS + 30 + portal * 12,
                (80, 180, 255),
                width=2,
                alpha=72,
            )
        elif hole.type == "bottle":
            sparkle = 0.5 + 0.5 * math.sin(phase * 5.4)
            self.draw_glow_ring(
                center,
                HOLE_RADIUS + 10 + sparkle * 6,
                (255, 214, 110),
                width=3,
                alpha=96,
                y_scale=1.15,
            )
            for bubble_index in range(3):
                rise = (phase * 2.2 + bubble_index * 0.4) % 1.6
                bubble_center = (
                    int(
                        center[0]
                        - 10
                        + bubble_index * 10
                        + math.sin(phase * 4 + bubble_index) * 4
                    ),
                    int(center[1] - 18 - rise * 26),
                )
                pygame.draw.circle(
                    self.display.screen,
                    (255, 244, 214),
                    bubble_center,
                    3 + bubble_index,
                )
                pygame.draw.circle(
                    self.display.screen,
                    (190, 120, 40),
                    bubble_center,
                    3 + bubble_index,
                    width=1,
                )
        else:
            glint = 0.5 + 0.5 * math.sin(phase * 4.4)
            glint_pos = (
                int(center[0] + math.cos(phase * 1.8) * HOLE_RADIUS * 0.55),
                int(center[1] - math.sin(phase * 2.1) * HOLE_RADIUS * 0.35),
            )
            pygame.draw.circle(
                self.display.screen,
                (255, 255, 255),
                glint_pos,
                max(2, int(2 + glint * 3)),
            )

    def draw_side_bonus_hole_highlight(self, hole, center, phase):
        self.draw_side_special_hole_highlight(hole, center, phase, special_type="bonus")

    def draw_side_malus_hole_highlight(self, hole, center, phase):
        self.draw_side_special_hole_highlight(hole, center, phase, special_type="malus")

    def draw_side_special_hole_highlight(
        self, hole, center, phase, special_type="bonus"
    ):
        is_malus = special_type == "malus"
        activated_attr = "malus_activated_at" if is_malus else "bonus_activated_at"
        duration_attr = "malus_duration" if is_malus else "bonus_duration"
        primary_color = (255, 92, 92) if is_malus else (255, 214, 82)
        secondary_color = (255, 176, 136) if is_malus else (120, 214, 255)
        accent_color = (255, 232, 220) if is_malus else (255, 248, 220)
        timer_fill = (196, 58, 58, 224) if is_malus else (120, 214, 255, 212)

        pulse_fast = 0.5 + 0.5 * math.sin(phase * 6.8)
        pulse_slow = 0.5 + 0.5 * math.sin(phase * 2.7)
        blink = 0.5 + 0.5 * math.sin(phase * 11.0)
        elapsed = max(0.0, time.monotonic() - getattr(hole, activated_attr, 0.0))
        duration = max(0.1, getattr(hole, duration_attr, 0.0) or 20.0)
        remaining_ratio = max(0.08, 1.0 - min(1.0, elapsed / duration))
        seconds_left = max(0, math.ceil(duration - elapsed))
        switch_pulse = max(0.0, 1.0 - min(1.0, elapsed / 0.85))

        halo_surface = pygame.Surface((168, 168), pygame.SRCALPHA)
        halo_center = halo_surface.get_rect().center
        for radius, color, local_alpha in (
            (HOLE_RADIUS + 10 + int(pulse_fast * 3), primary_color, 34),
            (HOLE_RADIUS + 18 + int(pulse_slow * 4), secondary_color, 24),
            (HOLE_RADIUS + 26 + int(pulse_fast * 5), primary_color, 12),
        ):
            pygame.draw.circle(halo_surface, (*color, local_alpha), halo_center, radius)
        self.display.screen.blit(halo_surface, halo_surface.get_rect(center=center))

        for ring_radius, color, width, alpha in (
            (HOLE_RADIUS + 8 + pulse_fast * 2, primary_color, 4, 152),
            (HOLE_RADIUS + 16 + pulse_slow * 3, secondary_color, 3, 128),
            (HOLE_RADIUS + 24 + pulse_fast * 4, primary_color, 2, 82),
        ):
            self.draw_glow_ring(
                center,
                ring_radius,
                color,
                width=width,
                alpha=alpha,
            )

        orbit_radius = HOLE_RADIUS + 22 + pulse_slow * 4
        for orbit_index in range(6):
            angle = phase * 4.0 + orbit_index * (math.tau / 6)
            sparkle_center = (
                int(center[0] + math.cos(angle) * orbit_radius),
                int(center[1] + math.sin(angle) * orbit_radius * 0.88),
            )
            sparkle_color = primary_color if orbit_index % 2 == 0 else secondary_color
            self.draw_arcade_sparkle(
                sparkle_center,
                phase + orbit_index * 0.32,
                sparkle_color,
                radius=5,
                alpha=128,
            )

        reticle_rect = pygame.Rect(0, 0, (HOLE_RADIUS + 20) * 2, (HOLE_RADIUS + 20) * 2)
        reticle_rect.center = center
        sweep_start = phase * 2.8
        for segment_index in range(4):
            start_angle = sweep_start + segment_index * (math.pi / 2)
            end_angle = start_angle + 0.62
            arc_color = (255, 214, 82) if segment_index % 2 == 0 else (120, 214, 255)
            pygame.draw.arc(
                self.display.screen,
                arc_color,
                reticle_rect,
                start_angle,
                end_angle,
                4,
            )

        timer_rect = pygame.Rect(0, 0, (HOLE_RADIUS + 30) * 2, (HOLE_RADIUS + 30) * 2)
        timer_rect.center = center
        pygame.draw.arc(
            self.display.screen,
            (255, 255, 255, 38),
            timer_rect,
            -math.pi / 2,
            math.pi * 1.5,
            2,
        )
        pygame.draw.arc(
            self.display.screen,
            (255, 214, 82),
            timer_rect,
            -math.pi / 2,
            -math.pi / 2 + remaining_ratio * math.tau,
            5,
        )

        if switch_pulse > 0.0:
            flash_surface = pygame.Surface((96, 96), pygame.SRCALPHA)
            flash_center = flash_surface.get_rect().center
            pygame.draw.circle(
                flash_surface,
                (255, 248, 220, int(32 + switch_pulse * 96)),
                flash_center,
                max(10, int(HOLE_RADIUS - 4 + switch_pulse * 12)),
            )
            pygame.draw.circle(
                flash_surface,
                (255, 214, 82, int(24 + switch_pulse * 88)),
                flash_center,
                max(8, int(HOLE_RADIUS - 10 + switch_pulse * 8)),
                4,
            )
            self.display.screen.blit(
                flash_surface, flash_surface.get_rect(center=center)
            )

        bracket_surface = pygame.Surface((180, 180), pygame.SRCALPHA)
        bracket_center = bracket_surface.get_rect().center
        bracket_offset = HOLE_RADIUS + 24 + pulse_fast * 3
        bracket_len = 12 + int(pulse_slow * 4)
        for sign_x, sign_y in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            corner_x = bracket_center[0] + sign_x * bracket_offset
            corner_y = bracket_center[1] + sign_y * bracket_offset
            inner_x = corner_x - sign_x * bracket_len
            inner_y = corner_y - sign_y * bracket_len
            pygame.draw.line(
                bracket_surface,
                (*primary_color, 218),
                (corner_x, corner_y),
                (inner_x, corner_y),
                4,
            )
            pygame.draw.line(
                bracket_surface,
                (*primary_color, 218),
                (corner_x, corner_y),
                (corner_x, inner_y),
                4,
            )
            pygame.draw.line(
                bracket_surface,
                (*secondary_color, 164),
                (corner_x - sign_x * 2, corner_y - sign_y * 2),
                (inner_x - sign_x * 2, corner_y - sign_y * 2),
                2,
            )
            pygame.draw.line(
                bracket_surface,
                (*secondary_color, 164),
                (corner_x - sign_x * 2, corner_y - sign_y * 2),
                (corner_x - sign_x * 2, inner_y - sign_y * 2),
                2,
            )
        self.display.screen.blit(
            bracket_surface, bracket_surface.get_rect(center=center)
        )

        for tick_index in range(12):
            if tick_index % 2 == 1 and blink < 0.42:
                continue
            angle = phase * 1.4 + tick_index * (math.tau / 12)
            inner_radius = HOLE_RADIUS + 18 + (tick_index % 2) * 2
            outer_radius = inner_radius + 8 + blink * 2
            warning_color = primary_color if tick_index % 3 == 0 else secondary_color
            pygame.draw.line(
                self.display.screen,
                warning_color,
                (
                    center[0] + math.cos(angle) * inner_radius,
                    center[1] + math.sin(angle) * inner_radius,
                ),
                (
                    center[0] + math.cos(angle) * outer_radius,
                    center[1] + math.sin(angle) * outer_radius,
                ),
                3,
            )

        arrow_bob = int(math.sin(phase * 7.0) * 3)
        arrow_offset = HOLE_RADIUS + 30
        arrow_size = 11
        left_x = center[0] - arrow_offset - arrow_bob
        right_x = center[0] + arrow_offset + arrow_bob
        pygame.draw.polygon(
            self.display.screen,
            primary_color,
            [
                (left_x, center[1]),
                (left_x + arrow_size, center[1] - arrow_size + 1),
                (left_x + arrow_size, center[1] + arrow_size - 1),
            ],
        )
        pygame.draw.polygon(
            self.display.screen,
            primary_color if blink > 0.58 else accent_color,
            [
                (left_x + 2, center[1]),
                (left_x + arrow_size - 2, center[1] - arrow_size + 3),
                (left_x + arrow_size - 2, center[1] + arrow_size - 3),
            ],
        )
        pygame.draw.polygon(
            self.display.screen,
            primary_color,
            [
                (right_x, center[1]),
                (right_x - arrow_size, center[1] - arrow_size + 1),
                (right_x - arrow_size, center[1] + arrow_size - 1),
            ],
        )
        pygame.draw.polygon(
            self.display.screen,
            primary_color if blink > 0.58 else accent_color,
            [
                (right_x - 2, center[1]),
                (right_x - arrow_size + 2, center[1] - arrow_size + 3),
                (right_x - arrow_size + 2, center[1] + arrow_size - 3),
            ],
        )

        lamp_y = center[1] - HOLE_RADIUS - 6
        lamp_spacing = 10
        lamp_glow_surface = pygame.Surface((64, 22), pygame.SRCALPHA)
        for lamp_index in range(3):
            lamp_x = 16 + lamp_index * lamp_spacing
            lamp_on = blink > 0.52 or lamp_index == 1
            lamp_color = primary_color if lamp_index == 1 else secondary_color
            lamp_alpha = 210 if lamp_on else 82
            pygame.draw.circle(
                lamp_glow_surface,
                (*lamp_color, 42 if lamp_on else 18),
                (lamp_x, 11),
                6,
            )
            pygame.draw.circle(
                lamp_glow_surface,
                (*lamp_color, lamp_alpha),
                (lamp_x, 11),
                3,
            )
        self.display.screen.blit(
            lamp_glow_surface,
            (center[0] - lamp_glow_surface.get_width() // 2, lamp_y - 10),
        )

        timer_badge_width = max(
            44, self.display.font_tiny.size(f"{seconds_left}s")[0] + 18
        )
        timer_badge_rect = pygame.Rect(0, 0, timer_badge_width, 16)
        timer_badge_rect.midtop = (center[0], center[1] + HOLE_RADIUS + 4)
        self.draw_badge(
            f"{seconds_left}s",
            timer_badge_rect,
            timer_fill,
            text_color=WHITE,
            border_color=(255, 255, 255, 86),
            font=self.display.font_tiny,
        )

    def draw_progress_meter(
        self,
        rect,
        current_progress,
        score,
        accent_color,
        label_left=None,
        label_right=None,
    ):
        phase = time.monotonic()
        meter_rect = pygame.Rect(rect)
        if label_left:
            label_fonts = [self.display.font_verysmall]
            for fallback_name in ("font_micro", "font_tiny"):
                fallback_font = getattr(self.display, fallback_name, None)
                if fallback_font is not None:
                    label_fonts.append(fallback_font)
            left_label_font = self.get_fitted_font(
                label_left,
                label_fonts,
                max(40, meter_rect.width // 2 - 10),
                meter_rect.height + 4,
            )
            self.draw_text_with_shadow(
                label_left,
                left_label_font,
                WHITE,
                BLACK,
                (meter_rect.left, meter_rect.top - left_label_font.get_height() - 2),
            )
        if label_right:
            label_fonts = [self.display.font_verysmall]
            for fallback_name in ("font_micro", "font_tiny"):
                fallback_font = getattr(self.display, fallback_name, None)
                if fallback_font is not None:
                    label_fonts.append(fallback_font)
            right_label_font = self.get_fitted_font(
                str(label_right),
                label_fonts,
                max(40, meter_rect.width // 2 - 10),
                meter_rect.height + 4,
            )
            label_surface = right_label_font.render(str(label_right), True, WHITE)
            self.draw_text_with_shadow(
                str(label_right),
                right_label_font,
                WHITE,
                BLACK,
                (
                    meter_rect.right - label_surface.get_width(),
                    meter_rect.top - right_label_font.get_height() - 2,
                ),
            )
        self.draw_panel_shadow(
            meter_rect,
            alpha=64,
            inflate=12,
            offset=(0, 6),
            border_radius=18,
        )
        pygame.draw.rect(
            self.display.screen, (14, 20, 34), meter_rect, border_radius=18
        )
        pygame.draw.rect(
            self.display.screen, (255, 255, 255), meter_rect, width=2, border_radius=18
        )
        self.draw_halftone_dots(
            meter_rect.inflate(-10, -8),
            color=(255, 255, 255),
            alpha=10,
            spacing=16,
            radius=1,
            drift=phase * 4,
        )
        ratio = 0 if score <= 0 else max(0.0, min(1.0, current_progress / score))
        if ratio <= 0:
            return
        fill_rect = meter_rect.inflate(-8, -8)
        fill_rect.width = max(12, int(fill_rect.width * ratio))
        pygame.draw.rect(self.display.screen, accent_color, fill_rect, border_radius=14)
        for tick_index in range(1, 5):
            tick_x = meter_rect.left + int(meter_rect.width * tick_index / 5)
            pygame.draw.line(
                self.display.screen,
                (255, 255, 255, 28),
                (tick_x, meter_rect.top + 5),
                (tick_x, meter_rect.bottom - 5),
                1,
            )
        stripes = pygame.Surface(fill_rect.size, pygame.SRCALPHA)
        for stripe_index in range(-2, 10):
            stripe_x = (
                int((phase * 120 + stripe_index * 24) % (fill_rect.width + 28)) - 28
            )
            pygame.draw.polygon(
                stripes,
                (255, 255, 255, 22),
                [
                    (stripe_x, 0),
                    (stripe_x + 12, 0),
                    (stripe_x + 28, fill_rect.height),
                    (stripe_x + 16, fill_rect.height),
                ],
            )
        self.display.screen.blit(stripes, fill_rect.topleft)
        shine_width = min(42, fill_rect.width)
        shine_rect = pygame.Rect(
            fill_rect.right - shine_width, fill_rect.top, shine_width, fill_rect.height
        )
        shine_surface = pygame.Surface(shine_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            shine_surface,
            (255, 255, 255, 54),
            shine_surface.get_rect(),
            border_radius=14,
        )
        self.display.screen.blit(shine_surface, shine_rect.topleft)
        current_label = (
            f"{int(current_progress)}/{int(score)}"
            if score > 0
            else str(int(current_progress))
        )
        value_font = self.get_fitted_font(
            current_label,
            [
                self.display.font_verysmall,
                self.display.font_micro,
                self.display.font_tiny,
            ],
            meter_rect.width - 16,
            meter_rect.height - 2,
        )
        if (
            meter_rect.height < 16
            or meter_rect.width < 180
            or value_font.get_height() > meter_rect.height - 4
        ):
            return
        self.draw_text_with_shadow(
            current_label,
            value_font,
            BLACK if ratio > 0.35 else WHITE,
            WHITE if ratio > 0.35 else BLACK,
            meter_rect.center,
            shadow_offset=(1, 1),
            center=True,
        )

    def draw_low_time_warning(self, challenge_state):
        if not challenge_state or not challenge_state.get("low_time"):
            return
        remaining = max(0.0, challenge_state.get("remaining_seconds", 0.0))
        urgency = 1.0 - min(1.0, remaining / max(challenge_state["turn_duration"], 1))
        pulse = 0.5 + 0.5 * math.sin(time.monotonic() * 9.0)
        overlay = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        alpha = int((24 + urgency * 50) * pulse)
        for stripe_index in range(-2, 8):
            stripe_x = (
                int(
                    (time.monotonic() * 260 + stripe_index * 170)
                    % (self.display.screen_width + 220)
                )
                - 110
            )
            pygame.draw.polygon(
                overlay,
                (255, 90, 90, max(12, alpha // 3)),
                [
                    (stripe_x, 0),
                    (stripe_x + 54, 0),
                    (stripe_x - 60, self.display.screen_height),
                    (stripe_x - 114, self.display.screen_height),
                ],
            )
        pygame.draw.rect(
            overlay,
            (255, 70, 70, alpha),
            overlay.get_rect(),
            width=16,
            border_radius=22,
        )
        pygame.draw.rect(
            overlay,
            (255, 244, 214, max(18, alpha // 2)),
            (18, 18, self.display.screen_width - 36, self.display.screen_height - 36),
            width=4,
            border_radius=20,
        )
        self.display.screen.blit(overlay, (0, 0))
        warning = self.display.font_medium.render("CHRONO!", True, WHITE)
        self.display.screen.blit(
            warning,
            warning.get_rect(center=(self.display.screen_width // 2, 138 + pulse * 6)),
        )
        badge_rect = pygame.Rect(self.display.screen_width // 2 - 70, 158, 140, 24)
        self.draw_badge(
            "SIRENE ACTIVE",
            badge_rect,
            (255, 90, 90, 220),
            text_color=WHITE,
            border_color=(255, 244, 214, 90),
        )

    def draw_challenge_panel(self, challenge_state):
        if not challenge_state:
            return

        if challenge_state["type"] in {"order", "all_holes"}:
            sequence_labels = challenge_state["sequence_labels"]
            label_count = max(1, len(sequence_labels))
            panel_rect = pygame.Rect(
                24,
                self.display.screen_height - 180,
                self.display.screen_width - 48,
                104,
            )
            self.draw_panel_shadow(panel_rect, alpha=94, inflate=20, offset=(0, 12))
            panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                panel_surface,
                (8, 24, 46, 208),
                panel_surface.get_rect(),
                border_radius=22,
            )
            pygame.draw.rect(
                panel_surface,
                (255, 255, 255, 16),
                (10, 10, panel_rect.width - 20, 34),
                border_radius=18,
            )
            self.display.screen.blit(panel_surface, panel_rect.topleft)
            self.draw_panel_grid(
                panel_rect.inflate(-16, -16),
                time.monotonic(),
                color=(120, 214, 255),
                alpha=10,
                step=56,
            )
            self.draw_arcade_screws(panel_rect, inset=12, radius=3)
            self.draw_chrome_rect(panel_rect, CHROME_COLORS, 22, 4)

            title_text = (
                f"Ordre : {challenge_state['progress']}/{challenge_state['total']}"
                if challenge_state["type"] == "order"
                else f"Tous les trous : {challenge_state['progress']}/{challenge_state['total']}"
            )
            title = self.display.font_small.render(title_text, True, YELLOW)
            self.display.screen.blit(title, (panel_rect.left + 18, panel_rect.top + 10))

            next_target_text = (
                f"Cible : {challenge_state['next_target']}"
                if challenge_state["type"] == "order"
                else f"Reste : {challenge_state['remaining']}"
            )
            next_target_width = max(
                148,
                self.display.font_verysmall.size(next_target_text)[0] + 24,
            )
            self.draw_badge(
                next_target_text,
                (
                    panel_rect.right - next_target_width - 18,
                    panel_rect.top + 10,
                    next_target_width,
                    24,
                ),
                (6, 20, 42, 198),
                text_color=WHITE,
                border_color=(255, 255, 255, 70),
            )

            available_width = panel_rect.width - 36
            gap = 6
            step_width = max(
                42,
                min(64, (available_width - gap * (label_count - 1)) // label_count),
            )
            start_x = panel_rect.left + 18
            start_y = panel_rect.top + 52
            track_y = start_y + 17
            pygame.draw.line(
                self.display.screen,
                (255, 255, 255, 20),
                (start_x + step_width // 2, track_y),
                (
                    start_x + (label_count - 1) * (step_width + gap) + step_width // 2,
                    track_y,
                ),
                6,
            )
            completed_targets = set(challenge_state.get("completed_targets", ()))
            target_ids = tuple(challenge_state.get("target_ids", ()))
            for index, label in enumerate(sequence_labels):
                step_rect = pygame.Rect(
                    start_x + index * (step_width + gap),
                    start_y,
                    step_width,
                    34,
                )
                if challenge_state["type"] == "all_holes":
                    target_key = target_ids[index] if index < len(target_ids) else None
                    matched_target = target_key in completed_targets
                    fill_color = (78, 176, 102) if matched_target else (54, 72, 98)
                elif index < challenge_state["progress"]:
                    fill_color = (78, 176, 102)
                elif index == challenge_state["progress"]:
                    fill_color = (255, 206, 84)
                else:
                    fill_color = (54, 72, 98)
                pygame.draw.rect(
                    self.display.screen,
                    fill_color,
                    step_rect,
                    border_radius=10,
                )
                pygame.draw.rect(
                    self.display.screen,
                    WHITE,
                    step_rect,
                    width=2,
                    border_radius=10,
                )
                short_label = label[:7]
                text_surface = self.display.font_verysmall.render(
                    short_label,
                    True,
                    (
                        BLACK
                        if challenge_state["type"] == "order"
                        and index <= challenge_state["progress"]
                        else WHITE
                    ),
                )
                self.display.screen.blit(
                    text_surface,
                    text_surface.get_rect(center=step_rect.center),
                )
        elif challenge_state["type"] == "time_attack":
            remaining = max(0.0, challenge_state.get("remaining_seconds", 0.0))
            low_time = challenge_state.get("low_time", False)
            awaiting_start = challenge_state.get("awaiting_start", False)
            pulse = 0.5 + 0.5 * math.sin(time.monotonic() * (9.0 if low_time else 4.0))
            panel_rect = pygame.Rect(
                self.display.screen_width // 2 - 140,
                20,
                280,
                92,
            )
            self.draw_panel_shadow(panel_rect, alpha=90, inflate=20, offset=(0, 10))
            panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            if awaiting_start:
                panel_color = (28, 54, 16, 214)
            else:
                panel_color = (84, 12, 12, 214) if low_time else (6, 26, 56, 214)
            pygame.draw.rect(
                panel_surface,
                panel_color,
                panel_surface.get_rect(),
                border_radius=22,
            )
            self.display.screen.blit(panel_surface, panel_rect.topleft)
            self.draw_panel_grid(
                panel_rect.inflate(-14, -14),
                time.monotonic(),
                color=(
                    (210, 255, 180)
                    if awaiting_start
                    else (255, 180, 180) if low_time else (120, 214, 255)
                ),
                alpha=10,
                step=52,
            )
            self.draw_arcade_screws(panel_rect, inset=10, radius=3)
            self.draw_chrome_rect(
                panel_rect,
                (
                    [(210, 255, 180), (90, 180, 90), WHITE]
                    if awaiting_start
                    else (
                        CHROME_COLORS
                        if not low_time
                        else [(255, 180, 180), (255, 90, 90), WHITE]
                    )
                ),
                22,
                4,
            )
            seconds_label = "PRÊT ?" if awaiting_start else f"{remaining:04.1f}s"
            seconds_text = self.display.font_large.render(
                seconds_label,
                True,
                WHITE if not low_time else (255, 244, 214),
            )
            self.display.screen.blit(
                seconds_text,
                seconds_text.get_rect(
                    center=(
                        panel_rect.centerx,
                        panel_rect.centery - 10 + pulse * (3 if low_time else 1),
                    )
                ),
            )
            details_text = (
                "HAUT pour lancer"
                if awaiting_start
                else f"Tours restants : {challenge_state['turns_left']}"
            )
            details = self.display.font_verysmall.render(details_text, True, YELLOW)
            self.display.screen.blit(
                details,
                details.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 26)),
            )
            bar_rect = pygame.Rect(panel_rect.left + 20, panel_rect.bottom - 16, 240, 6)
            pygame.draw.rect(
                self.display.screen,
                (255, 255, 255, 28),
                bar_rect,
                border_radius=4,
            )
            ratio = (
                1.0
                if awaiting_start
                else max(
                    0.0,
                    min(
                        1.0,
                        remaining / max(1.0, challenge_state.get("turn_duration", 1.0)),
                    ),
                )
            )
            fill_rect = bar_rect.copy()
            fill_rect.width = 0 if ratio <= 0 else max(14, int(bar_rect.width * ratio))
            if fill_rect.width > 0:
                pygame.draw.rect(
                    self.display.screen,
                    (
                        (140, 255, 180)
                        if awaiting_start
                        else (255, 120, 120) if low_time else (120, 214, 255)
                    ),
                    fill_rect,
                    border_radius=4,
                )
            self.draw_badge(
                "CHRONO",
                (panel_rect.left + 18, panel_rect.top - 12, 82, 22),
                (255, 214, 82, 214),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )
            if low_time and not awaiting_start:
                self.draw_badge(
                    "ALERTE",
                    (panel_rect.right - 94, panel_rect.top - 12, 76, 22),
                    (255, 90, 90, 220),
                    text_color=WHITE,
                    border_color=(255, 244, 214, 90),
                )

    def draw_game(
        self,
        players,
        current_player,
        holes,
        score,
        game_mode,
        team_mode,
        player_in_team=0,
        current_progress=0,
        leader_progress=0,
        challenge_mode="CLASSIQUE",
        status_text="",
        challenge_state=None,
    ):
        if current_player is None:
            return

        cache_key = self.get_game_frame_cache_key(
            players,
            current_player,
            holes,
            score,
            game_mode,
            team_mode,
            player_in_team,
            current_progress,
            leader_progress,
            challenge_mode,
            status_text,
            challenge_state,
        )
        if (
            self._game_frame_cache_key == cache_key
            and self._game_frame_cache_surface is not None
        ):
            self.display.update_time_warning_audio(challenge_state)
            self.display.screen.blit(self._game_frame_cache_surface, (0, 0))
            pygame.display.flip()
            return

        phase = time.monotonic()
        self.display.update_time_warning_audio(challenge_state)
        self.display.screen.blit(self.display.resources["game_background"], (0, 0))
        self.draw_vertical_gradient((6, 14, 22), (8, 28, 46), alpha=86)
        self.draw_spotlight_canopy(phase, intensity=0.62, tint=(255, 220, 148))
        self.draw_stage_floor(phase, horizon_ratio=0.66, tint=(132, 222, 255), alpha=18)
        self.draw_ambient_backdrop(phase)
        self.draw_interface_backdrop_motion(
            phase,
            len(players),
            challenge_state=challenge_state,
        )
        self.draw_screen_frame(
            phase,
            accent_color=(255, 220, 126),
            secondary_color=(120, 222, 255),
        )
        self.draw_static_elements(
            current_player,
            score,
            game_mode,
            team_mode,
            holes,
            current_progress,
            leader_progress,
            challenge_mode,
            challenge_state,
        )
        self.display_grouped_players(
            players,
            team_mode,
            player_in_team,
            challenge_state=challenge_state,
        )
        self.draw_challenge_panel(challenge_state)
        self.draw_low_time_warning(challenge_state)
        if self.should_draw_status_banner(status_text, challenge_state=challenge_state):
            self.draw_status_banner(status_text, challenge_state=challenge_state)
        self._game_frame_cache_key = cache_key
        self._game_frame_cache_surface = self.display.screen.copy()
        pygame.display.flip()

    def draw_holes(self, holes, challenge_state=None):
        phase = time.monotonic()
        holes_area_rect = pygame.Rect(
            2 * self.display.frame_space_x + self.display.frame_score_width,
            self.display.frame_space_y,
            self.display.hole_frame_width,
            self.display.hole_rect_height,
        )
        self.draw_panel_shadow(holes_area_rect, alpha=92, inflate=26, offset=(0, 16))
        holes_surface = pygame.Surface(holes_area_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            holes_surface,
            (8, 24, 44, 170),
            holes_surface.get_rect(),
            border_radius=24,
        )
        pygame.draw.rect(
            holes_surface,
            (255, 255, 255, 18),
            (12, 12, holes_area_rect.width - 24, holes_area_rect.height // 2),
            border_radius=22,
        )
        pygame.draw.ellipse(
            holes_surface,
            (255, 255, 255, 18),
            (holes_area_rect.width // 2 - 180, -40, 360, 120),
        )
        self.display.screen.blit(holes_surface, holes_area_rect.topleft)
        self.draw_panel_grid(
            holes_area_rect.inflate(-18, -18),
            phase,
            color=(120, 214, 255),
            alpha=10,
            step=58,
        )
        self.draw_halftone_dots(
            holes_area_rect.inflate(-36, -26),
            color=(255, 255, 255),
            alpha=8,
            spacing=24,
            radius=2,
            drift=phase * 4,
        )
        self.draw_chrome_rect(holes_area_rect, CHROME_COLORS, 20, 5)
        self.draw_marquee_lights(holes_area_rect, phase, (255, 222, 132), count=20)
        self.draw_arcade_screws(holes_area_rect, inset=14, radius=4)
        arena_label_rect = pygame.Rect(
            holes_area_rect.centerx - 70,
            holes_area_rect.top - 12,
            140,
            24,
        )
        arena_label_surface = pygame.Surface(arena_label_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            arena_label_surface,
            (255, 210, 82, 210),
            arena_label_surface.get_rect(),
            border_radius=12,
        )
        self.display.screen.blit(arena_label_surface, arena_label_rect.topleft)
        self.draw_text_with_shadow(
            "ARÈNE",
            self.display.font_verysmall,
            BLACK,
            WHITE,
            arena_label_rect.center,
            shadow_offset=(1, 1),
            center=True,
        )

        for hole in holes:
            x1, y1 = hole.position[0], hole.position[1]
            first_pin = hole.pin[0] if hole.pin else None
            second_pin = hole.pin[1] if len(hole.pin) > 1 else None
            is_first_bonus_active = (
                getattr(hole, "bonus_active", False)
                and getattr(hole, "bonus_active_pin", None) == first_pin
            )
            is_first_malus_active = (
                getattr(hole, "malus_active", False)
                and getattr(hole, "malus_active_pin", None) == first_pin
            )
            is_second_bonus_active = (
                getattr(hole, "bonus_active", False)
                and getattr(hole, "bonus_active_pin", None) == second_pin
            )
            is_second_malus_active = (
                getattr(hole, "malus_active", False)
                and getattr(hole, "malus_active_pin", None) == second_pin
            )
            hole_shadow = pygame.Surface(
                (HOLE_RADIUS * 3, HOLE_RADIUS * 2), pygame.SRCALPHA
            )
            pygame.draw.ellipse(
                hole_shadow,
                (0, 0, 0, 64),
                hole_shadow.get_rect(),
            )
            self.display.screen.blit(
                hole_shadow,
                (x1 - hole_shadow.get_width() // 2, y1 + HOLE_RADIUS // 2),
            )
            self.draw_special_hole_accent(hole, (int(x1), int(y1)), phase)
            if is_first_bonus_active:
                self.draw_side_bonus_hole_highlight(hole, (int(x1), int(y1)), phase)
            if is_first_malus_active:
                self.draw_side_malus_hole_highlight(hole, (int(x1), int(y1)), phase)
            is_target = (
                challenge_state
                and challenge_state.get("type") == "order"
                and challenge_state.get("target_hole_type") == hole.type
                and challenge_state.get("target_hole_text") == hole.text
            )
            first_hole_surface = (
                self.display.resources["hole_score"]
                if is_target or is_first_bonus_active or is_first_malus_active
                else self.display.resources["hole"]
            )
            if is_target:
                self.draw_glow_ring(
                    (int(x1), int(y1)),
                    HOLE_RADIUS + 22,
                    (255, 226, 110),
                    width=5,
                    alpha=130,
                )
            self.display.screen.blit(
                first_hole_surface,
                (x1 - HOLE_RADIUS, y1 - HOLE_RADIUS),
            )
            font = (
                self.display.font_medium
                if hole.type != "large_frog"
                else self.display.font_small
            )
            self.draw_text_with_shadow(
                hole.text,
                font,
                (
                    (255, 212, 212)
                    if is_first_malus_active
                    else (
                        (255, 248, 228)
                        if (is_target or is_first_bonus_active)
                        else LIGHT_GREY
                    )
                ),
                BLACK,
                (x1, y1),
                shadow_offset=(2, 2),
                center=True,
            )

            if hole.type in {"side", "bottle"}:
                x2, y2 = hole.position2[0], hole.position2[1]
                self.display.screen.blit(
                    hole_shadow,
                    (x2 - hole_shadow.get_width() // 2, y2 + HOLE_RADIUS // 2),
                )
                self.draw_special_hole_accent(hole, (int(x2), int(y2)), phase + 0.6)
                if is_second_bonus_active:
                    self.draw_side_bonus_hole_highlight(
                        hole, (int(x2), int(y2)), phase + 0.6
                    )
                if is_second_malus_active:
                    self.draw_side_malus_hole_highlight(
                        hole, (int(x2), int(y2)), phase + 0.6
                    )
                if is_target:
                    self.draw_glow_ring(
                        (int(x2), int(y2)),
                        HOLE_RADIUS + 22,
                        (255, 226, 110),
                        width=5,
                        alpha=130,
                    )
                second_hole_surface = (
                    self.display.resources["hole_score"]
                    if is_target or is_second_bonus_active or is_second_malus_active
                    else self.display.resources["hole"]
                )
                self.display.screen.blit(
                    second_hole_surface,
                    (x2 - HOLE_RADIUS, y2 - HOLE_RADIUS),
                )
                self.draw_text_with_shadow(
                    hole.text,
                    font,
                    (
                        (255, 212, 212)
                        if is_second_malus_active
                        else (
                            (255, 248, 228)
                            if (is_target or is_second_bonus_active)
                            else LIGHT_GREY
                        )
                    ),
                    BLACK,
                    (x2, y2),
                    shadow_offset=(2, 2),
                    center=True,
                )

    def draw_static_elements(
        self,
        current_player,
        score,
        game_mode,
        team_mode,
        holes,
        current_progress,
        leader_progress,
        challenge_mode,
        challenge_state=None,
    ):
        phase = time.monotonic()
        left_panel_rect = pygame.Rect(
            self.display.frame_space_x,
            self.display.frame_space_y,
            self.display.frame_score_width,
            self.display.hole_rect_height,
        )
        right_panel_rect = pygame.Rect(
            self.display.screen_width
            - self.display.frame_score_width
            - self.display.frame_space_x,
            self.display.frame_space_y,
            self.display.frame_score_width,
            self.display.hole_rect_height,
        )

        current_player_name_text = str(current_player)
        current_team_text = None
        if team_mode != TEAM_MODE_SOLO and current_player.team is not None:
            current_team_text = str(current_player.team)

        if team_mode == TEAM_MODE_TEAM:
            score_label = "SCORE EQUIPE"
        elif team_mode == TEAM_MODE_DUO:
            score_label = "SCORE DUO"
        else:
            score_label = "SCORE"

        if challenge_state and challenge_state.get("type") == "order":
            left_primary_label = "SEQUENCE"
            left_primary_value = (
                f"{challenge_state['progress']}/{challenge_state['total']}"
            )
            left_secondary_label = "PROCHAINE"
            left_secondary_value = str(challenge_state["next_target"])
        elif challenge_state and challenge_state.get("type") == "all_holes":
            left_primary_label = "VALIDES"
            left_primary_value = (
                f"{challenge_state['progress']}/{challenge_state['total']}"
            )
            left_secondary_label = "RESTE"
            left_secondary_value = str(challenge_state["remaining"])
        elif challenge_state and challenge_state.get("type") == "time_attack":
            left_primary_label = score_label
            left_primary_value = str(current_progress)
            left_secondary_label = "TOURS"
            left_secondary_value = str(challenge_state["turns_left"])
        else:
            left_primary_label = score_label
            left_primary_value = str(current_progress)
            left_secondary_label = "RESTE"
            left_secondary_value = f"{max(score - current_progress, 0)} PTS"

        def draw_arcade_panel_shell(panel_rect, accent_color):
            self.draw_panel_shadow(panel_rect, alpha=54, inflate=14, offset=(0, 8))
            panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                panel_surface,
                (8, 22, 40, 164),
                panel_surface.get_rect(),
                border_radius=22,
            )
            pygame.draw.rect(
                panel_surface,
                (255, 255, 255, 16),
                (12, 10, panel_rect.width - 24, max(18, panel_rect.height // 5)),
                border_radius=18,
            )
            pygame.draw.rect(
                panel_surface,
                (*accent_color, 42),
                (0, 0, 7, panel_rect.height),
                border_radius=22,
            )
            pygame.draw.rect(
                panel_surface,
                (255, 255, 255, 26),
                panel_surface.get_rect(),
                width=1,
                border_radius=22,
            )
            self.display.screen.blit(panel_surface, panel_rect.topleft)
            self.draw_panel_grid(
                panel_rect.inflate(-20, -18),
                phase,
                color=accent_color,
                alpha=5,
                step=62,
            )
            self.draw_panel_sheen(
                panel_rect.inflate(-10, -10),
                phase + panel_rect.left * 0.004,
                accent_color,
                alpha=12,
                width=max(38, panel_rect.width // 5),
                speed=110,
            )
            pygame.draw.rect(
                self.display.screen,
                (*accent_color, 108),
                panel_rect,
                width=2,
                border_radius=22,
            )

        draw_arcade_panel_shell(left_panel_rect, (124, 255, 190))
        draw_arcade_panel_shell(right_panel_rect, (255, 214, 110))

        def build_side_panel_layout(panel_rect):
            inset_x = max(14, min(20, panel_rect.width // 11))
            inset_y = max(8, min(16, panel_rect.height // 18))
            header_height = max(18, min(24, panel_rect.height // 14))
            content_gap = max(4, min(10, panel_rect.height // 40))
            meter_height = max(12, min(18, panel_rect.height // 18))
            available_cards_height = (
                panel_rect.height
                - (2 * inset_y)
                - header_height
                - meter_height
                - (4 * content_gap)
            )
            layout_scale = max(0.82, min(1.0, available_cards_height / 176))
            hero_min = max(48, int(56 * layout_scale))
            stat_min = max(42, int(52 * layout_scale))
            hero_height = max(hero_min, int(available_cards_height * 0.38))
            primary_height = max(stat_min, int(available_cards_height * 0.26))
            secondary_height = max(
                stat_min,
                available_cards_height - hero_height - primary_height,
            )
            overflow = (
                hero_height + primary_height + secondary_height - available_cards_height
            )
            if overflow > 0:
                hero_reduction = min(overflow, max(0, hero_height - hero_min))
                hero_height -= hero_reduction
                overflow -= hero_reduction
            if overflow > 0:
                primary_reduction = min(overflow, max(0, primary_height - stat_min))
                primary_height -= primary_reduction
                overflow -= primary_reduction
            if overflow > 0:
                secondary_height = max(stat_min, secondary_height - overflow)

            header_rect = pygame.Rect(
                panel_rect.left + inset_x,
                panel_rect.top + inset_y,
                panel_rect.width - 2 * inset_x,
                header_height,
            )
            hero_rect = pygame.Rect(
                panel_rect.left + inset_x,
                header_rect.bottom + content_gap,
                panel_rect.width - 2 * inset_x,
                hero_height,
            )
            primary_rect = pygame.Rect(
                panel_rect.left + inset_x,
                hero_rect.bottom + content_gap,
                panel_rect.width - 2 * inset_x,
                primary_height,
            )
            secondary_rect = pygame.Rect(
                panel_rect.left + inset_x,
                primary_rect.bottom + content_gap,
                panel_rect.width - 2 * inset_x,
                secondary_height,
            )
            meter_rect = pygame.Rect(
                panel_rect.left + inset_x,
                panel_rect.bottom - inset_y - meter_height,
                panel_rect.width - 2 * inset_x,
                meter_height,
            )
            return {
                "inset_x": inset_x,
                "header_rect": header_rect,
                "gap": content_gap,
                "hero_rect": hero_rect,
                "primary_rect": primary_rect,
                "secondary_rect": secondary_rect,
                "meter_rect": meter_rect,
            }

        left_layout = build_side_panel_layout(left_panel_rect)
        right_layout = build_side_panel_layout(right_panel_rect)

        left_header_rect = left_layout["header_rect"]
        left_chip_width = max(
            86, self.display.font_verysmall.size(challenge_mode)[0] + 26
        )
        left_chip_rect = pygame.Rect(
            left_header_rect.left,
            left_header_rect.top,
            left_chip_width,
            left_header_rect.height,
        )
        left_title_x = left_chip_rect.right + 10
        left_title_font = self.get_fitted_font(
            "UP NEXT",
            [
                self.display.font_verysmall,
                self.display.font_micro,
                self.display.font_tiny,
            ],
            max(40, left_header_rect.right - left_title_x),
            left_header_rect.height,
        )
        self.draw_badge(
            challenge_mode,
            left_chip_rect,
            (255, 214, 82, 214),
            text_color=BLACK,
            border_color=(255, 255, 255, 80),
        )
        self.draw_text_with_shadow(
            "UP NEXT",
            left_title_font,
            YELLOW,
            BLACK,
            (
                left_title_x,
                left_header_rect.top
                + max(0, (left_header_rect.height - left_title_font.get_height()) // 2)
                + math.sin(phase * 2.6) * 1.2,
            ),
            shadow_offset=(1, 1),
        )

        left_hero_rect = left_layout["hero_rect"]
        self.draw_hud_stat_card(
            left_hero_rect,
            "JOUEUR ACTIF",
            current_player_name_text,
            (84, 214, 126),
            value_color=DARK_GREEN,
            value_fonts=[
                self.display.font_large,
                self.display.font_medium,
                self.display.font_small,
                self.display.font_verysmall,
            ],
            value_top_padding=32,
            value_bottom_padding=12,
        )
        if current_team_text is not None:
            team_badge_width = max(
                48, self.display.font_verysmall.size(current_team_text)[0] + 20
            )
            self.draw_badge(
                current_team_text,
                (
                    left_hero_rect.left + 10,
                    left_hero_rect.bottom - 24,
                    team_badge_width,
                    18,
                ),
                (20, 54, 98, 204),
                text_color=WHITE,
                border_color=(255, 255, 255, 70),
            )

        left_primary_rect = left_layout["primary_rect"]
        self.draw_hud_stat_card(
            left_primary_rect,
            left_primary_label,
            left_primary_value,
            (255, 154, 38),
            value_color=DARK_ORANGE,
            value_fonts=[
                self.display.font_large,
                self.display.font_medium,
                self.display.font_small,
                self.display.font_verysmall,
            ],
            value_top_padding=28,
            value_bottom_padding=10,
        )

        left_secondary_rect = left_layout["secondary_rect"]
        self.draw_hud_stat_card(
            left_secondary_rect,
            left_secondary_label,
            left_secondary_value,
            (98, 220, 150),
            value_color=WHITE,
            value_fonts=[
                self.display.font_medium,
                self.display.font_small,
                self.display.font_verysmall,
            ],
            value_top_padding=28,
            value_bottom_padding=10,
        )

        progress_meter_rect = left_layout["meter_rect"]
        self.draw_progress_meter(
            progress_meter_rect,
            current_progress,
            score,
            (84, 214, 126),
            label_left="PROGRES",
            label_right="GOAL",
        )

        right_header_rect = right_layout["header_rect"]
        right_chip_width = max(72, self.display.font_verysmall.size(team_mode)[0] + 26)
        right_chip_rect = pygame.Rect(
            right_header_rect.left,
            right_header_rect.top,
            right_chip_width,
            right_header_rect.height,
        )
        right_title_font = self.get_fitted_font(
            "MODE",
            [
                self.display.font_verysmall,
                self.display.font_micro,
                self.display.font_tiny,
            ],
            max(32, right_header_rect.right - right_chip_rect.right - 10),
            right_header_rect.height,
        )
        self.draw_badge(
            team_mode,
            right_chip_rect,
            (6, 20, 42, 198),
            text_color=WHITE,
            border_color=(255, 255, 255, 70),
        )
        self.draw_text_with_shadow(
            "MODE",
            right_title_font,
            YELLOW,
            BLACK,
            (
                right_chip_rect.right + 10,
                right_header_rect.top
                + max(
                    0, (right_header_rect.height - right_title_font.get_height()) // 2
                )
                + math.sin(phase * 2.6 + 0.9) * 1.2,
            ),
            shadow_offset=(1, 1),
        )

        right_hero_rect = right_layout["hero_rect"]
        self.draw_hud_stat_card(
            right_hero_rect,
            "MODE ARENE",
            game_mode,
            (255, 196, 84),
            value_color=DARK_ORANGE,
            value_fonts=[
                self.display.font_large,
                self.display.font_medium,
                self.display.font_small,
                self.display.font_verysmall,
            ],
            value_top_padding=32,
            value_bottom_padding=12,
        )

        right_primary_rect = right_layout["primary_rect"]
        self.draw_hud_stat_card(
            right_primary_rect,
            "JACKPOT",
            f"{score} PTS",
            (255, 154, 38),
            value_color=DARK_ORANGE,
            value_fonts=[
                self.display.font_large,
                self.display.font_medium,
                self.display.font_small,
                self.display.font_verysmall,
            ],
            value_top_padding=28,
            value_bottom_padding=10,
        )

        right_secondary_rect = right_layout["secondary_rect"]
        self.draw_hud_stat_card(
            right_secondary_rect,
            "STYLE",
            challenge_mode,
            (255, 214, 82),
            value_color=YELLOW,
            value_fonts=[
                self.display.font_medium,
                self.display.font_small,
                self.display.font_verysmall,
            ],
            value_top_padding=28,
            value_bottom_padding=10,
        )

        opponent_meter_rect = right_layout["meter_rect"]
        self.draw_progress_meter(
            opponent_meter_rect,
            leader_progress,
            score,
            (255, 206, 84),
            label_left="LEADER",
            label_right="GOAL",
        )

        self.draw_holes(holes, challenge_state=challenge_state)

    def get_player_dock_rect(self, player_count, challenge_state=None):
        top = (
            self.display.frame_space_y
            + self.display.hole_rect_height
            + max(18, self.display.screen_height // 34)
        )
        if challenge_state and challenge_state.get("type") == "order":
            bottom_reserved = 186
        else:
            bottom_reserved = 86
        available_height = max(136, self.display.screen_height - bottom_reserved - top)
        target_height = int(
            self.display.screen_height
            * (0.2 if player_count <= 4 else 0.27 if player_count <= 8 else 0.34)
        )
        dock_height = max(150, min(available_height, target_height))
        extra_width = (
            0
            if player_count <= 4
            else (
                self.display.frame_score_width // 2
                if player_count <= 8
                else self.display.frame_score_width
            )
        )
        base_width = (
            self.display.hole_frame_width + self.display.frame_space_x * 2 + extra_width
        )
        width_ratio = 0.72 if player_count <= 4 else 0.86 if player_count <= 8 else 0.95
        dock_width = min(
            self.display.screen_width - self.display.frame_space_x * 2,
            max(base_width, int(self.display.screen_width * width_ratio)),
        )
        return pygame.Rect(
            self.display.half_width - dock_width // 2,
            top,
            dock_width,
            dock_height,
        )

    def get_player_card_layout(self, player_count, cards_rect):
        if player_count <= 0:
            return 1, 1, cards_rect.width, cards_rect.height, 0, 0

        max_columns = min(
            player_count,
            6 if cards_rect.width >= 640 else 5 if cards_rect.width >= 520 else 4,
        )
        best_layout = None
        for columns in range(1, max_columns + 1):
            rows = max(1, math.ceil(player_count / columns))
            column_gap = max(8, min(14, cards_rect.width // max(18, columns * 8)))
            row_gap = max(8, min(14, cards_rect.height // max(12, rows * 7)))
            usable_width = cards_rect.width - column_gap * (columns - 1)
            usable_height = cards_rect.height - row_gap * (rows - 1)
            if usable_width <= 0 or usable_height <= 0:
                continue
            card_width = usable_width // columns
            card_height = usable_height // rows
            if card_width < 86 or card_height < 40:
                continue
            aspect_ratio = card_width / max(1, card_height)
            layout_score = card_width * card_height
            layout_score += min(card_width, card_height) * 22
            layout_score -= abs(aspect_ratio - 1.55) * 600
            layout_score -= max(0, rows - 2) * 420
            if player_count >= 10:
                layout_score += columns * 80
            if best_layout is None or layout_score > best_layout[0]:
                best_layout = (
                    layout_score,
                    columns,
                    rows,
                    card_width,
                    card_height,
                    column_gap,
                    row_gap,
                )

        if best_layout is None:
            columns = min(player_count, 4)
            rows = max(1, math.ceil(player_count / columns))
            column_gap = 8
            row_gap = 8
            card_width = max(
                72,
                (cards_rect.width - column_gap * (columns - 1)) // columns,
            )
            card_height = max(
                38,
                (cards_rect.height - row_gap * (rows - 1)) // rows,
            )
            return columns, rows, card_width, card_height, column_gap, row_gap

        return best_layout[1:]

    def display_grouped_players(
        self,
        players,
        team_mode,
        player_in_team,
        challenge_state=None,
    ):
        phase = time.monotonic()
        if team_mode == TEAM_MODE_TEAM:
            teams = {}
            for player in players:
                teams.setdefault(player.team, []).append(player)
            groups = list(teams.values())
        elif team_mode == TEAM_MODE_DUO:
            pairs = {}
            for player in players:
                pairs.setdefault(player.team, []).append(player)
            groups = list(pairs.values())
        else:
            groups = [players]

        group_color_map = {
            id(group): GROUP_COLORS[index % len(GROUP_COLORS)]
            for index, group in enumerate(groups)
        }

        active_card_rect = None
        active_card_color = None

        player_group_color = {}
        for group in groups:
            for player in group:
                player_group_color[id(player)] = group_color_map[id(group)]

        dock_rect = self.get_player_dock_rect(
            len(players), challenge_state=challenge_state
        )
        self.draw_panel_shadow(dock_rect, alpha=58, inflate=14, offset=(0, 8))
        dock_surface = pygame.Surface(dock_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            dock_surface,
            (8, 18, 32, 176),
            dock_surface.get_rect(),
            border_radius=22,
        )
        pygame.draw.rect(
            dock_surface,
            (255, 255, 255, 14),
            (12, 10, dock_rect.width - 24, 28),
            border_radius=18,
        )
        pygame.draw.rect(
            dock_surface,
            (255, 214, 82, 52),
            (0, 0, 7, dock_rect.height),
            border_radius=22,
        )
        pygame.draw.rect(
            dock_surface,
            (255, 255, 255, 24),
            dock_surface.get_rect(),
            width=1,
            border_radius=22,
        )
        self.display.screen.blit(dock_surface, dock_rect.topleft)
        self.draw_panel_grid(
            dock_rect.inflate(-16, -16),
            phase,
            color=(156, 178, 214),
            alpha=5,
            step=64,
        )
        self.draw_panel_sheen(
            dock_rect.inflate(-12, -12),
            phase + 0.2,
            (255, 255, 255),
            alpha=10,
            width=max(56, dock_rect.width // 6),
            speed=100,
        )
        title_row_y = dock_rect.top + 10
        self.draw_badge(
            "LINE-UP",
            (dock_rect.left + 16, title_row_y, 92, 22),
            (18, 28, 44, 216),
            text_color=WHITE,
            border_color=(255, 214, 82, 104),
        )
        player_count_text = f"{len(players)} JOUEURS"
        player_count_width = max(
            104, self.display.font_verysmall.size(player_count_text)[0] + 20
        )
        self.draw_badge(
            player_count_text,
            (
                dock_rect.right - player_count_width - 16,
                title_row_y,
                player_count_width,
                22,
            ),
            (18, 28, 44, 208),
            text_color=WHITE,
            border_color=(255, 255, 255, 58),
        )
        self.draw_text_with_shadow(
            "ARCADE CREW",
            self.display.font_verysmall,
            WHITE,
            BLACK,
            (dock_rect.centerx, title_row_y + 11 + math.sin(phase * 2.8) * 1.4),
            shadow_offset=(1, 1),
            center=True,
        )
        accent_span = pygame.Rect(
            dock_rect.left + 20,
            dock_rect.top + 38,
            dock_rect.width - 40,
            4,
        )
        pygame.draw.rect(
            self.display.screen,
            (255, 214, 82, 180),
            accent_span,
            border_radius=2,
        )

        cards_rect = pygame.Rect(
            dock_rect.left + 14,
            dock_rect.top + 54,
            dock_rect.width - 28,
            dock_rect.height - 68,
        )
        columns, rows, card_width, card_height, column_gap, row_gap = (
            self.get_player_card_layout(len(players), cards_rect)
        )

        for index, player in enumerate(players):
            group_color = player_group_color.get(
                id(player), GROUP_COLORS[index % len(GROUP_COLORS)]
            )
            row = index // columns
            column = index % columns
            row_start = row * columns
            row_players = players[row_start : min(len(players), row_start + columns)]
            row_width = len(row_players) * card_width + column_gap * (
                len(row_players) - 1
            )
            start_x = cards_rect.centerx - row_width // 2
            card_float = int(
                math.sin(phase * (3.5 if player.is_active else 2.1) + index * 0.65)
                * (3 if player.is_active else 1)
            )
            card_rect = pygame.Rect(
                start_x + column * (card_width + column_gap),
                cards_rect.top + row * (card_height + row_gap) + card_float,
                card_width,
                card_height,
            )
            self.draw_panel_shadow(
                card_rect,
                alpha=86 if player.is_active else 24,
                inflate=8,
                offset=(0, 5),
                border_radius=16,
            )
            card_surface = pygame.Surface(card_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                card_surface,
                (10, 22, 38, 236 if player.is_active else 164),
                card_surface.get_rect(),
                border_radius=16,
            )
            pygame.draw.rect(
                card_surface,
                (*group_color[:3], 74 if player.is_active else 10),
                (0, 0, card_rect.width, max(22, card_rect.height // 3)),
                border_radius=16,
            )
            pygame.draw.rect(
                card_surface,
                (*group_color[:3], 182 if player.is_active else 68),
                (0, 0, 7 if player.is_active else 4, card_rect.height),
                border_radius=16,
            )
            pygame.draw.rect(
                card_surface,
                (255, 255, 255, 24 if player.is_active else 8),
                (10, 8, card_rect.width - 20, max(10, card_rect.height // 3)),
                border_radius=12,
            )
            pygame.draw.rect(
                card_surface,
                (255, 255, 255, 42 if player.is_active else 18),
                card_surface.get_rect(),
                width=2 if player.is_active else 1,
                border_radius=16,
            )
            self.display.screen.blit(card_surface, card_rect.topleft)
            self.draw_panel_grid(
                card_rect.inflate(-10, -10),
                phase + index * 0.15,
                color=group_color[:3],
                alpha=5 if player.is_active else 3,
                step=46,
            )
            self.draw_panel_sheen(
                card_rect.inflate(-6, -6),
                phase + index * 0.18,
                (255, 255, 255),
                alpha=10 if player.is_active else 5,
                width=max(28, card_rect.width // 3),
                speed=82,
            )

            name_plate_height = (
                24 if card_height >= 78 else 20 if card_height >= 62 else 18
            )
            name_plate_rect = pygame.Rect(
                card_rect.left + 10,
                card_rect.top
                + (28 if card_height >= 62 else card_rect.height // 2 - 8),
                card_rect.width - 20,
                name_plate_height,
            )
            name_plate_surface = pygame.Surface(name_plate_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                name_plate_surface,
                (6, 14, 24, 154),
                name_plate_surface.get_rect(),
                border_radius=10,
            )
            pygame.draw.rect(
                name_plate_surface,
                (*group_color[:3], 74),
                name_plate_surface.get_rect(),
                width=1,
                border_radius=10,
            )
            self.display.screen.blit(name_plate_surface, name_plate_rect.topleft)

            if player.is_active:
                active_card_rect = card_rect.copy()
                active_card_color = group_color
                pulse_surface = pygame.Surface(
                    (card_width + 16, card_height + 16), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    pulse_surface,
                    (*group_color[:3], 90),
                    pulse_surface.get_rect(),
                    border_radius=18,
                    width=3,
                )
                self.display.screen.blit(
                    pulse_surface, (card_rect.left - 8, card_rect.top - 8)
                )
                underline_rect = pygame.Rect(
                    card_rect.left + 12,
                    card_rect.bottom - 8,
                    card_rect.width - 24,
                    4,
                )
                pygame.draw.rect(
                    self.display.screen,
                    (*group_color[:3], 220),
                    underline_rect,
                    border_radius=2,
                )
                live_label = "LIVE" if card_height < 62 else "ON AIR"
                live_width = max(44, self.display.font_tiny.size(live_label)[0] + 18)
                live_rect = pygame.Rect(
                    card_rect.left + 10,
                    card_rect.top + 8,
                    live_width,
                    16,
                )
                live_alpha = int(188 + (0.5 + 0.5 * math.sin(phase * 7.0 + index)) * 36)
                self.draw_badge(
                    live_label,
                    live_rect,
                    (*group_color[:3], live_alpha),
                    text_color=WHITE,
                    border_color=(255, 255, 255, 62),
                )

            rank_size = 16 if card_height < 62 else 18
            rank_rect = pygame.Rect(
                card_rect.right - rank_size - 8,
                card_rect.top + 8,
                rank_size,
                rank_size,
            )
            pygame.draw.rect(
                self.display.screen,
                (14, 26, 42),
                rank_rect,
                border_radius=8,
            )
            pygame.draw.rect(
                self.display.screen,
                (*group_color[:3], 148),
                rank_rect,
                width=1,
                border_radius=8,
            )
            self.draw_text_with_shadow(
                str(player.rank),
                self.get_fitted_font(
                    str(player.rank),
                    [self.display.font_verysmall, self.display.font_micro],
                    rank_rect.width - 2,
                    rank_rect.height - 2,
                ),
                PLAYER_OPTION_COLOR,
                BLACK,
                rank_rect.center,
                shadow_offset=(1, 1),
                center=True,
            )

            name_font = self.get_fitted_font(
                str(player),
                [
                    self.display.font_medium,
                    self.display.font_small,
                    self.display.font_verysmall,
                    self.display.font_micro,
                    self.display.font_tiny,
                ],
                name_plate_rect.width - 14,
                name_plate_rect.height - 2,
            )
            self.draw_text_with_shadow(
                str(player),
                name_font,
                WHITE if player.is_active else PLAYER_OPTION_COLOR,
                BLACK,
                name_plate_rect.center,
                shadow_offset=(2, 2),
                center=True,
            )

            status_label = (
                "UP"
                if player.is_active and card_height < 62
                else (
                    "ACTIF"
                    if player.is_active
                    else "NEXT" if card_height < 62 else "READY"
                )
            )
            status_fill = (
                (
                    *group_color[:3],
                    int(176 + (0.5 + 0.5 * math.sin(phase * 6.2 + index)) * 24),
                )
                if player.is_active
                else (18, 30, 46, 204)
            )
            status_width = max(42, self.display.font_tiny.size(status_label)[0] + 18)
            self.draw_badge(
                status_label,
                (
                    card_rect.left + 10,
                    card_rect.bottom - (18 if card_height < 62 else 22),
                    status_width,
                    12 if card_height < 62 else 14,
                ),
                status_fill,
                text_color=WHITE,
                border_color=(255, 255, 255, 62),
                font=self.display.font_tiny,
            )

            score_text = str(player.score)
            score_font = self.get_fitted_font(
                score_text,
                [
                    self.display.font_large,
                    self.display.font_medium,
                    self.display.font_small,
                    self.display.font_verysmall,
                    self.display.font_micro,
                ],
                max(40, min(card_rect.width // 2, 96)),
                max(16, card_rect.height // 3),
            )
            score_badge_width = max(
                44,
                min(card_rect.width // 2, score_font.size(score_text)[0] + 22),
            )
            score_badge_rect = pygame.Rect(
                card_rect.right - score_badge_width - 10,
                card_rect.bottom - (22 if card_height < 62 else 26),
                score_badge_width,
                14 if card_height < 62 else 18,
            )
            self.draw_badge(
                score_text,
                score_badge_rect,
                (12, 24, 40, 224),
                text_color=PLAYER_OPTION_COLOR,
                border_color=(*group_color[:3], 108),
                font=score_font,
            )

            if player.team is not None and team_mode != TEAM_MODE_SOLO:
                team_text = str(player.team)
                team_badge_width = max(
                    34,
                    self.display.font_tiny.size(team_text)[0] + 16,
                )
                self.draw_badge(
                    team_text,
                    (
                        card_rect.left + 10,
                        (
                            card_rect.top + 8
                            if not player.is_active
                            else card_rect.top + 28
                        ),
                        team_badge_width,
                        16,
                    ),
                    (*group_color[:3], 164),
                    text_color=WHITE,
                    border_color=(255, 255, 255, 54),
                    font=self.display.font_tiny,
                )

        if active_card_rect is not None and active_card_color is not None:
            self.draw_active_player_beacon(active_card_rect, active_card_color, phase)

    def draw_status_banner(self, status_text, challenge_state=None):
        phase = time.monotonic()
        banner_width = min(self.display.screen_width - 80, 720)
        banner_height = 54
        banner_bottom = self.display.screen_height - 30
        if challenge_state and challenge_state.get("type") == "order":
            banner_bottom = self.display.screen_height - 194
        banner_rect = pygame.Rect(
            (self.display.screen_width - banner_width) // 2,
            banner_bottom - banner_height,
            banner_width,
            banner_height,
        )
        self.draw_panel_shadow(banner_rect, alpha=72, inflate=18, offset=(0, 10))
        banner_surface = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            banner_surface,
            (8, 32, 64, 185),
            banner_surface.get_rect(),
            border_radius=18,
        )
        shimmer_x = int((phase * 180) % (banner_width + 140)) - 70
        shimmer_surface = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(
            shimmer_surface,
            (255, 255, 255, 26),
            [
                (shimmer_x, 0),
                (shimmer_x + 60, 0),
                (shimmer_x + 120, banner_height),
                (shimmer_x + 60, banner_height),
            ],
        )
        self.display.screen.blit(banner_surface, banner_rect.topleft)
        self.draw_panel_grid(
            banner_rect.inflate(-14, -14),
            phase,
            color=(255, 214, 110),
            alpha=10,
            step=56,
        )
        self.display.screen.blit(shimmer_surface, banner_rect.topleft)
        self.draw_halftone_dots(
            banner_rect.inflate(-20, -16),
            color=(255, 255, 255),
            alpha=8,
            spacing=18,
            radius=1,
            drift=phase * 7,
        )
        self.draw_chrome_rect(banner_rect, CHROME_COLORS, 18, 4)
        self.draw_marquee_lights(banner_rect, phase, (255, 228, 148), count=18)
        self.draw_arcade_screws(banner_rect, inset=10, radius=3)
        self.draw_text_with_shadow(
            status_text,
            self.display.font_small,
            YELLOW,
            BLACK,
            (
                banner_rect.centerx,
                banner_rect.centery + math.sin(phase * 5.0) * 1.5,
            ),
            shadow_offset=(2, 2),
            center=True,
        )

    def calculate_group_layout(self, team_mode, group):
        if team_mode == TEAM_MODE_SOLO:
            return 4
        if team_mode == TEAM_MODE_DUO:
            return 4
        if team_mode == TEAM_MODE_TEAM:
            if len(group) == 3:
                return 1
            if len(group) > 4:
                return 2
            return len(group)
        return 4

    def group_players(self, players, attribute):
        groups = {}
        for player in players:
            key = getattr(player, attribute)
            groups.setdefault(key, []).append(player)
        return list(groups.values())
