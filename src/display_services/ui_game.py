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
            self.draw_text_with_shadow(
                label_left,
                self.display.font_verysmall,
                WHITE,
                BLACK,
                (meter_rect.left, meter_rect.top - 16),
            )
        if label_right:
            label_surface = self.display.font_verysmall.render(
                str(label_right), True, WHITE
            )
            self.draw_text_with_shadow(
                str(label_right),
                self.display.font_verysmall,
                WHITE,
                BLACK,
                (meter_rect.right - label_surface.get_width(), meter_rect.top - 16),
            )
        self.draw_panel_shadow(
            meter_rect,
            alpha=64,
            inflate=12,
            offset=(0, 6),
            border_radius=18,
        )
        pygame.draw.rect(
            self.display.screen, (18, 24, 32), meter_rect, border_radius=18
        )
        pygame.draw.rect(
            self.display.screen, (255, 255, 255), meter_rect, width=2, border_radius=18
        )
        ratio = 0 if score <= 0 else max(0.0, min(1.0, current_progress / score))
        if ratio <= 0:
            return
        fill_rect = meter_rect.inflate(-8, -8)
        fill_rect.width = max(12, int(fill_rect.width * ratio))
        pygame.draw.rect(self.display.screen, accent_color, fill_rect, border_radius=14)
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
        self.draw_text_with_shadow(
            current_label,
            self.display.font_verysmall,
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

        if challenge_state["type"] == "order":
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
            self.draw_chrome_rect(panel_rect, CHROME_COLORS, 22, 4)

            title = self.display.font_small.render(
                f"Ordre : {challenge_state['progress']}/{challenge_state['total']}",
                True,
                YELLOW,
            )
            self.display.screen.blit(title, (panel_rect.left + 18, panel_rect.top + 10))

            next_target_text = f"Cible : {challenge_state['next_target']}"
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
            for index, label in enumerate(sequence_labels):
                step_rect = pygame.Rect(
                    start_x + index * (step_width + gap),
                    start_y,
                    step_width,
                    34,
                )
                if index < challenge_state["progress"]:
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
                    BLACK if index <= challenge_state["progress"] else WHITE,
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

        phase = time.monotonic()
        self.display.update_time_warning_audio(challenge_state)
        self.display.screen.blit(self.display.resources["game_background"], (0, 0))
        self.draw_vertical_gradient((6, 14, 22), (8, 28, 46), alpha=86)
        self.draw_spotlight_canopy(phase, intensity=0.62, tint=(255, 220, 148))
        self.draw_stage_floor(phase, horizon_ratio=0.66, tint=(132, 222, 255), alpha=18)
        self.draw_ambient_backdrop(phase)
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
        self.display_grouped_players(players, team_mode, player_in_team)
        self.draw_challenge_panel(challenge_state)
        self.draw_low_time_warning(challenge_state)
        if status_text:
            self.draw_status_banner(status_text, challenge_state=challenge_state)
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
        self.draw_chrome_rect(holes_area_rect, CHROME_COLORS, 20, 5)
        self.draw_marquee_lights(holes_area_rect, phase, (255, 222, 132), count=20)
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
            is_target = (
                challenge_state
                and challenge_state.get("type") == "order"
                and challenge_state.get("target_hole_type") == hole.type
                and challenge_state.get("target_hole_text") == hole.text
            )
            hole_surface = (
                self.display.resources["hole_score"]
                if is_target
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
            self.display.screen.blit(hole_surface, (x1 - HOLE_RADIUS, y1 - HOLE_RADIUS))
            font = (
                self.display.font_medium
                if hole.type != "large_frog"
                else self.display.font_small
            )
            self.draw_text_with_shadow(
                hole.text,
                font,
                (255, 248, 228) if is_target else LIGHT_GREY,
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
                if is_target:
                    self.draw_glow_ring(
                        (int(x2), int(y2)),
                        HOLE_RADIUS + 22,
                        (255, 226, 110),
                        width=5,
                        alpha=130,
                    )
                self.display.screen.blit(
                    hole_surface,
                    (x2 - HOLE_RADIUS, y2 - HOLE_RADIUS),
                )
                self.draw_text_with_shadow(
                    hole.text,
                    font,
                    (255, 248, 228) if is_target else LIGHT_GREY,
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
        current_player_rect = (
            self.display.frame_space_x,
            self.display.frame_space_y,
            self.display.frame_score_width,
            self.display.hole_rect_height,
        )
        current_player_panel_rect = pygame.Rect(current_player_rect)

        name_text_position = (
            self.display.frame_space_x + self.display.frame_score_width / 2,
            self.display.frame_space_y + (self.display.hole_rect_height / 3),
        )
        score_text_position = (
            self.display.frame_space_x + self.display.frame_score_width / 2,
            name_text_position[1] + (self.display.hole_rect_height / 5),
        )
        remaining_points_text_position = (
            self.display.frame_space_x + self.display.frame_score_width / 2,
            score_text_position[1] + (self.display.hole_rect_height / 5),
        )

        if team_mode == TEAM_MODE_TEAM:
            score_label = "Score équipe"
        elif team_mode == TEAM_MODE_DUO:
            score_label = "Score duo"
        else:
            score_label = "Score"

        if challenge_state and challenge_state.get("type") == "order":
            current_player_score = (
                f"Étape : {challenge_state['progress']}/{challenge_state['total']}"
            )
            remaining_points_text = f"Prochaine : {challenge_state['next_target']}"
        elif challenge_state and challenge_state.get("type") == "time_attack":
            current_player_score = f"{score_label} : {current_progress}"
            remaining_points_text = f"Tours restants : {challenge_state['turns_left']}"
        else:
            current_player_score = f"{score_label} : {current_progress}"
            remaining_points_text = (
                f"Points Restants : {max(score - current_progress, 0)}"
            )

        score_surface = self.display.font_medium.render(
            current_player_score, True, DARK_ORANGE
        )
        remaining_points_surface = self.display.font_verysmall.render(
            remaining_points_text, True, DARK_GREEN
        )

        score_rect = score_surface.get_rect(center=score_text_position)
        remaining_points_rect = remaining_points_surface.get_rect(
            center=remaining_points_text_position
        )
        score_rect.inflate_ip(10, 10)
        remaining_points_rect.inflate_ip(10, 10)

        self.draw_panel_shadow(
            current_player_panel_rect, alpha=84, inflate=20, offset=(0, 12)
        )
        current_panel_surface = pygame.Surface(
            current_player_panel_rect.size, pygame.SRCALPHA
        )
        pygame.draw.rect(
            current_panel_surface,
            (8, 28, 48, 196),
            current_panel_surface.get_rect(),
            border_radius=22,
        )
        pygame.draw.rect(
            current_panel_surface,
            (255, 255, 255, 18),
            (
                10,
                10,
                current_player_panel_rect.width - 20,
                current_player_panel_rect.height // 2,
            ),
            border_radius=20,
        )
        self.display.screen.blit(
            current_panel_surface, current_player_panel_rect.topleft
        )
        self.draw_panel_grid(
            current_player_panel_rect.inflate(-18, -18),
            phase,
            color=(124, 255, 190),
            alpha=10,
            step=56,
        )

        pygame.draw.rect(
            self.display.screen, PLAYER_OPTION_COLOR, score_rect, border_radius=10
        )
        pygame.draw.rect(
            self.display.screen,
            PLAYER_OPTION_COLOR,
            remaining_points_rect,
            border_radius=10,
        )

        pulse_glow = pygame.Surface(
            (current_player_rect[2] + 24, current_player_rect[3] + 24),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            pulse_glow,
            (120, 255, 190, int(24 + (0.5 + 0.5 * math.sin(phase * 3.2)) * 52)),
            pulse_glow.get_rect(),
            border_radius=24,
            width=4,
        )
        self.display.screen.blit(
            pulse_glow, (current_player_rect[0] - 12, current_player_rect[1] - 12)
        )
        self.draw_marquee_lights(current_player_rect, phase, (124, 255, 190), count=18)

        self.draw_text_with_shadow(
            current_player_score,
            self.display.font_medium,
            DARK_ORANGE,
            BLACK,
            score_text_position,
            shadow_offset=(2, 2),
            center=True,
        )
        self.draw_text_with_shadow(
            remaining_points_text,
            self.display.font_verysmall,
            DARK_GREEN,
            BLACK,
            remaining_points_text_position,
            shadow_offset=(2, 2),
            center=True,
        )

        self.draw_chrome_rect(current_player_rect, CHROME_COLORS, 15, 5)

        current_player_name_text = str(current_player)
        if team_mode != TEAM_MODE_SOLO and current_player.team is not None:
            current_player_name_text = (
                f"{current_player_name_text} - {current_player.team}"
            )

        self.draw_text_with_shadow(
            "AU TOUR DE",
            self.display.font_verysmall,
            YELLOW,
            BLACK,
            (name_text_position[0], current_player_panel_rect.top + 18),
            center=True,
        )
        self.draw_text_with_shadow(
            current_player_name_text,
            self.display.font_large,
            DARK_GREEN,
            BLACK,
            name_text_position,
            shadow_offset=(2, 2),
            center=True,
        )

        self.draw_holes(holes, challenge_state=challenge_state)

        progress_meter_rect = pygame.Rect(
            current_player_rect[0] + 18,
            current_player_rect[1] + current_player_rect[3] - 40,
            current_player_rect[2] - 36,
            20,
        )
        self.draw_progress_meter(
            progress_meter_rect,
            current_progress,
            score,
            (84, 214, 126),
            label_left="PROGRESSION",
            label_right=str(score),
        )

        frame_x = (
            self.display.screen_width
            - self.display.frame_score_width
            - self.display.frame_space_x
        )
        frame_y = self.display.frame_space_y
        game_mode_rect = (
            frame_x,
            frame_y,
            self.display.frame_score_width,
            self.display.hole_rect_height,
        )
        game_mode_panel_rect = pygame.Rect(game_mode_rect)
        self.draw_panel_shadow(
            game_mode_panel_rect, alpha=84, inflate=20, offset=(0, 12)
        )
        mode_surface = pygame.Surface(game_mode_panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            mode_surface,
            (28, 20, 42, 198),
            mode_surface.get_rect(),
            border_radius=22,
        )
        pygame.draw.rect(
            mode_surface,
            (255, 210, 126, 18),
            (10, 10, game_mode_panel_rect.width - 20, game_mode_panel_rect.height // 2),
            border_radius=20,
        )
        self.display.screen.blit(mode_surface, game_mode_panel_rect.topleft)
        self.draw_panel_grid(
            game_mode_panel_rect.inflate(-18, -18),
            phase,
            color=(255, 214, 110),
            alpha=10,
            step=56,
        )
        self.draw_chrome_rect(game_mode_rect, CHROME_COLORS, 15, 5)
        self.draw_marquee_lights(game_mode_rect, phase + 0.4, (255, 214, 110), count=18)

        game_mode_text_position = (
            frame_x + self.display.frame_score_width / 2,
            frame_y + (self.display.hole_rect_height / 3),
        )
        score_position = (
            frame_x + self.display.frame_score_width / 2,
            name_text_position[1] + (self.display.hole_rect_height / 5),
        )
        team_mode_position = (
            frame_x + self.display.frame_score_width / 2,
            score_position[1] + (self.display.hole_rect_height / 5),
        )
        leader_position = (
            frame_x + self.display.frame_score_width / 2,
            team_mode_position[1] + (self.display.hole_rect_height / 7),
        )

        self.draw_text_with_shadow(
            "MODE LIVE",
            self.display.font_verysmall,
            YELLOW,
            BLACK,
            (game_mode_text_position[0], game_mode_panel_rect.top + 18),
            center=True,
        )
        self.draw_text_with_shadow(
            game_mode,
            self.display.font_medium,
            DARK_ORANGE,
            BLACK,
            game_mode_text_position,
            shadow_offset=(2, 2),
            center=True,
        )
        self.draw_text_with_shadow(
            f"{score} points",
            self.display.font_medium,
            DARK_ORANGE,
            BLACK,
            score_position,
            shadow_offset=(2, 2),
            center=True,
        )
        team_badge_width = max(82, self.display.font_verysmall.size(team_mode)[0] + 28)
        challenge_badge_width = max(
            96, self.display.font_verysmall.size(challenge_mode)[0] + 28
        )
        total_badge_width = team_badge_width + challenge_badge_width + 12
        badge_start_x = int(game_mode_panel_rect.centerx - total_badge_width / 2)
        badge_y = int(team_mode_position[1] - 12)
        self.draw_badge(
            team_mode,
            (badge_start_x, badge_y, team_badge_width, 24),
            (6, 20, 42, 198),
            text_color=WHITE,
            border_color=(255, 255, 255, 70),
        )
        self.draw_badge(
            challenge_mode,
            (
                badge_start_x + team_badge_width + 12,
                badge_y,
                challenge_badge_width,
                24,
            ),
            (76, 48, 12, 206),
            text_color=YELLOW,
            border_color=(255, 220, 126, 90),
        )
        self.draw_text_with_shadow(
            f"Leader : {leader_progress}",
            self.display.font_small,
            WHITE,
            BLACK,
            leader_position,
            shadow_offset=(2, 2),
            center=True,
        )
        opponent_meter_rect = pygame.Rect(
            frame_x + 18,
            frame_y + self.display.hole_rect_height - 40,
            self.display.frame_score_width - 36,
            20,
        )
        self.draw_progress_meter(
            opponent_meter_rect,
            leader_progress,
            score,
            (255, 206, 84),
            label_left="LEADER",
            label_right=str(score),
        )

    def display_grouped_players(self, players, team_mode, player_in_team):
        phase = time.monotonic()
        if team_mode == TEAM_MODE_TEAM:
            teams = {}
            for player in players:
                teams.setdefault(player.team, []).append(player)
            groups = list(teams.values())
            players_per_row = (
                1
                if player_in_team == 3
                else (
                    2
                    if player_in_team > 4
                    else (player_in_team if player_in_team != 2 else 4)
                )
            )
            display_score = True
        elif team_mode == TEAM_MODE_DUO:
            pairs = {}
            for player in players:
                pairs.setdefault(player.team, []).append(player)
            groups = list(pairs.values())
            players_per_row, display_score = 4, True
        else:
            groups = [players]
            players_per_row, display_score = 4, False

        group_color_map = {
            id(group): GROUP_COLORS[index % len(GROUP_COLORS)]
            for index, group in enumerate(groups)
        }

        start_y = self.display.screen_height / 2 - 20
        gap_between_boxes = 20
        box_width, box_height = self.display.resources["frame_player"].get_size()
        start_x = (
            self.display.screen_width - (4 * box_width) - (3 * gap_between_boxes)
        ) / 2
        x, y = start_x, start_y
        players_in_row = 0
        rank_square_size = 20
        height_score = (
            self.display.font_small.render("T", True, DARK_GREY).get_height() + 5
            if display_score
            else 0
        )

        for group in groups:
            group_color = group_color_map[id(group)]
            if team_mode != TEAM_MODE_SOLO:
                total_rect = pygame.Rect(int(x), int(y), box_width, 28)
                total_surface = pygame.Surface(total_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    total_surface,
                    (*group_color[:3], 156),
                    total_surface.get_rect(),
                    border_radius=12,
                )
                self.display.screen.blit(total_surface, total_rect.topleft)
                self.draw_text_with_shadow(
                    f"Total: {sum(player.score for player in group)}",
                    self.display.font_small,
                    WHITE,
                    BLACK,
                    total_rect.center,
                    center=True,
                )

            for player in group:
                frame_key = (
                    "frame_player_select" if player.is_active else "frame_player"
                )
                frame_rect = pygame.Rect(x, y + height_score, box_width, box_height)
                self.draw_panel_shadow(
                    frame_rect,
                    alpha=84 if player.is_active else 56,
                    inflate=12,
                    offset=(0, 8),
                    border_radius=16,
                )
                self.display.screen.blit(
                    self.display.resources[frame_key], frame_rect.topleft
                )
                tint_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                pygame.draw.rect(
                    tint_surface,
                    (*group_color[:3], 38 if player.is_active else 18),
                    tint_surface.get_rect(),
                    border_radius=14,
                )
                pygame.draw.rect(
                    tint_surface,
                    (*group_color[:3], 118),
                    (6, 8, 8, box_height - 16),
                    border_radius=6,
                )
                self.display.screen.blit(tint_surface, frame_rect.topleft)
                self.draw_panel_grid(
                    frame_rect.inflate(-10, -10),
                    phase + player.rank * 0.2,
                    color=group_color[:3],
                    alpha=8,
                    step=48,
                )

                if player.is_active:
                    pulse_surface = pygame.Surface(
                        (box_width + 18, box_height + 18), pygame.SRCALPHA
                    )
                    pygame.draw.rect(
                        pulse_surface,
                        (*group_color[:3], 58),
                        pulse_surface.get_rect(),
                        border_radius=18,
                        width=3,
                    )
                    self.display.screen.blit(
                        pulse_surface, (x - 9, y + height_score - 9)
                    )
                    self.draw_marquee_lights(
                        (x, y + height_score, box_width, box_height),
                        phase + player.rank * 0.15,
                        group_color,
                        count=12,
                        radius=3,
                    )
                    live_rect = pygame.Rect(
                        frame_rect.right - 66, frame_rect.top + 8, 52, 18
                    )
                    live_surface = pygame.Surface(live_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(
                        live_surface,
                        (255, 214, 82, 214),
                        live_surface.get_rect(),
                        border_radius=10,
                    )
                    self.display.screen.blit(live_surface, live_rect.topleft)
                    self.draw_text_with_shadow(
                        "LIVE",
                        self.display.font_verysmall,
                        BLACK,
                        WHITE,
                        live_rect.center,
                        shadow_offset=(1, 1),
                        center=True,
                    )

                square_x = x + box_width - rank_square_size - (box_width / 18)
                square_y = (
                    y
                    + height_score
                    + (box_height / 10)
                    + math.sin(phase * 3 + player.rank * 0.8) * 2
                )
                rank_background_surface = pygame.Surface(
                    (rank_square_size, rank_square_size), pygame.SRCALPHA
                )
                rank_background_surface.fill((*group_color[:3], 150))
                self.display.screen.blit(rank_background_surface, (square_x, square_y))
                pygame.draw.rect(
                    self.display.screen,
                    pygame.Color("white"),
                    (square_x, square_y, rank_square_size, rank_square_size),
                    width=1,
                    border_radius=5,
                )

                rank_text = self.display.font_verysmall.render(
                    f"{player.rank}", True, pygame.Color("white")
                )
                rank_text_shadow = self.display.font_verysmall.render(
                    f"{player.rank}", True, pygame.Color(0, 0, 0, 150)
                )
                rank_text_rect = rank_text.get_rect(
                    center=(
                        square_x + rank_square_size / 2,
                        square_y + rank_square_size / 2,
                    )
                )
                self.display.screen.blit(rank_text_shadow, rank_text_rect.move(1, 1))
                self.display.screen.blit(rank_text, rank_text_rect)

                player_label_pos = (
                    x + 20,
                    y
                    + height_score
                    + (box_height - self.display.font_small.get_height()) // 2,
                )
                self.draw_text_with_shadow(
                    str(player),
                    self.display.font_small,
                    DARK_ORANGE,
                    BLACK,
                    player_label_pos,
                )
                score_pill_rect = pygame.Rect(
                    frame_rect.right - 88, frame_rect.y + 22, 64, 24
                )
                score_pill_surface = pygame.Surface(
                    score_pill_rect.size, pygame.SRCALPHA
                )
                pygame.draw.rect(
                    score_pill_surface,
                    (6, 20, 38, 196),
                    score_pill_surface.get_rect(),
                    border_radius=12,
                )
                self.display.screen.blit(score_pill_surface, score_pill_rect.topleft)
                self.draw_text_with_shadow(
                    str(player.score),
                    self.display.font_small,
                    DARK_ORANGE,
                    BLACK,
                    score_pill_rect.center,
                    center=True,
                )

                if player.team is not None and team_mode != TEAM_MODE_SOLO:
                    team_text = str(player.team)
                    team_badge_width = max(
                        42, self.display.font_verysmall.size(team_text)[0] + 20
                    )
                    self.draw_badge(
                        team_text,
                        (
                            frame_rect.left + 12,
                            frame_rect.bottom - 20,
                            team_badge_width,
                            16,
                        ),
                        (*group_color[:3], 182),
                        text_color=WHITE,
                        border_color=(255, 255, 255, 68),
                    )

                if team_mode in [TEAM_MODE_SOLO, TEAM_MODE_DUO] or (
                    team_mode == TEAM_MODE_TEAM and len(group) == 2
                ):
                    x += box_width + gap_between_boxes
                    players_in_row += 1
                    if players_in_row >= players_per_row:
                        x = start_x
                        y += box_height + gap_between_boxes + height_score
                        players_in_row = 0
                elif team_mode == TEAM_MODE_TEAM:
                    if len(group) == 3:
                        x = start_x
                        y += box_height + gap_between_boxes + height_score
                    elif len(group) > 4:
                        x += box_width + gap_between_boxes
                        players_in_row += 1
                        if players_in_row == 2:
                            x = start_x
                            y += box_height + gap_between_boxes + height_score
                            players_in_row = 0
                    elif len(group) != 2:
                        x += box_width + gap_between_boxes

            if team_mode == TEAM_MODE_TEAM:
                if len(group) == 3:
                    start_x += box_width + gap_between_boxes
                    x = start_x
                    y = start_y
                elif len(group) > 4:
                    players_in_row = 0
                    start_x += 2 * (box_width + gap_between_boxes)
                    x = start_x
                    y = start_y
                elif len(group) != 2:
                    x = start_x
                    y += box_height + gap_between_boxes + height_score

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
        self.draw_chrome_rect(banner_rect, CHROME_COLORS, 18, 4)
        self.draw_marquee_lights(banner_rect, phase, (255, 228, 148), count=18)
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
