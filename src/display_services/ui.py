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


class DisplayUIService:
    def __init__(self, display):
        self.display = display

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

    def draw_progress_meter(self, rect, current_progress, score, accent_color):
        pygame.draw.rect(self.display.screen, (18, 24, 32), rect, border_radius=18)
        pygame.draw.rect(
            self.display.screen, (255, 255, 255), rect, width=2, border_radius=18
        )
        ratio = 0 if score <= 0 else max(0.0, min(1.0, current_progress / score))
        if ratio <= 0:
            return
        fill_rect = rect.inflate(-8, -8)
        fill_rect.width = max(12, int(fill_rect.width * ratio))
        pygame.draw.rect(self.display.screen, accent_color, fill_rect, border_radius=14)
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

    def draw_marquee_lights(self, rect, phase, color, count=16, radius=4):
        x, y, width, height = rect
        red, green, blue = color[:3]
        for index in range(count):
            ratio = index / count
            if ratio < 0.25:
                light_x = x + width * ratio * 4
                light_y = y
            elif ratio < 0.5:
                light_x = x + width
                light_y = y + height * (ratio - 0.25) * 4
            elif ratio < 0.75:
                light_x = x + width - width * (ratio - 0.5) * 4
                light_y = y + height
            else:
                light_x = x
                light_y = y + height - height * (ratio - 0.75) * 4

            pulse = 0.45 + 0.55 * math.sin(phase * 4.2 + index * 0.9)
            light_radius = max(2, int(radius + pulse * 2))
            glow = pygame.Surface((light_radius * 6, light_radius * 6), pygame.SRCALPHA)
            glow_center = glow.get_width() // 2
            pygame.draw.circle(
                glow,
                (red, green, blue, int(34 + pulse * 54)),
                (glow_center, glow_center),
                light_radius * 2,
            )
            pygame.draw.circle(
                glow,
                (255, 255, 255, int(115 + pulse * 100)),
                (glow_center, glow_center),
                light_radius,
            )
            self.display.screen.blit(
                glow,
                (int(light_x) - glow_center, int(light_y) - glow_center),
            )

    def draw_ambient_backdrop(self, phase):
        overlay = pygame.Surface(
            (self.display.screen_width, self.display.screen_height), pygame.SRCALPHA
        )
        for ribbon_index, color in enumerate(
            ((120, 220, 255), (255, 210, 120), (140, 255, 190))
        ):
            points = []
            base_y = 140 + ribbon_index * 120
            step = max(36, self.display.screen_width // 16)
            for x in range(-step, self.display.screen_width + step, step):
                wave = math.sin(phase * (0.8 + ribbon_index * 0.2) + x * 0.008)
                wave += math.cos(phase * 0.55 + ribbon_index + x * 0.012) * 0.4
                points.append((x, base_y + wave * (18 + ribbon_index * 6)))
            pygame.draw.lines(
                overlay,
                (*color, 18),
                False,
                points,
                6 - ribbon_index,
            )

        for sparkle_index in range(14):
            orbit = phase * (10 + sparkle_index * 0.35)
            sparkle_x = (
                sparkle_index * 123 + math.sin(phase * 0.8 + sparkle_index) * 90
            ) % self.display.screen_width
            sparkle_y = 80 + (
                sparkle_index * 67 + phase * 28 + math.cos(phase + sparkle_index) * 18
            ) % (self.display.screen_height - 180)
            radius = 2 + (sparkle_index % 3)
            sparkle_surface = pygame.Surface((radius * 8, radius * 8), pygame.SRCALPHA)
            center = sparkle_surface.get_width() // 2
            alpha = 24 + int((0.5 + 0.5 * math.sin(orbit)) * 42)
            pygame.draw.circle(
                sparkle_surface,
                (255, 248, 220, alpha),
                (center, center),
                radius * 2,
            )
            pygame.draw.circle(
                sparkle_surface,
                (255, 255, 255, alpha + 36),
                (center, center),
                radius,
            )
            self.display.screen.blit(
                sparkle_surface,
                (int(sparkle_x) - center, int(sparkle_y) - center),
            )

        self.display.screen.blit(overlay, (0, 0))

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
        pygame.draw.rect(
            overlay,
            (255, 70, 70, alpha),
            overlay.get_rect(),
            width=16,
            border_radius=22,
        )
        self.display.screen.blit(overlay, (0, 0))

    def draw_challenge_panel(self, challenge_state):
        if not challenge_state:
            return

        if challenge_state["type"] == "order":
            panel_rect = pygame.Rect(
                self.display.screen_width // 2 - 280,
                self.display.screen_height - 166,
                560,
                88,
            )
            panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                panel_surface,
                (8, 24, 46, 208),
                panel_surface.get_rect(),
                border_radius=22,
            )
            self.display.screen.blit(panel_surface, panel_rect.topleft)
            self.draw_chrome_rect(panel_rect, CHROME_COLORS, 22, 4)

            title = self.display.font_small.render(
                f"Ordre : {challenge_state['progress']}/{challenge_state['total']}",
                True,
                YELLOW,
            )
            self.display.screen.blit(title, (panel_rect.left + 18, panel_rect.top + 10))

            visible_labels = challenge_state["sequence_labels"]
            step_width = 48
            gap = 6
            start_x = panel_rect.left + 18
            start_y = panel_rect.top + 42
            for index, label in enumerate(visible_labels):
                step_rect = pygame.Rect(
                    start_x + index * (step_width + gap),
                    start_y,
                    step_width,
                    28,
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
                short_label = label[:6]
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
            pulse = 0.5 + 0.5 * math.sin(time.monotonic() * (9.0 if low_time else 4.0))
            panel_rect = pygame.Rect(
                self.display.screen_width // 2 - 140,
                20,
                280,
                92,
            )
            panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            panel_color = (84, 12, 12, 214) if low_time else (6, 26, 56, 214)
            pygame.draw.rect(
                panel_surface,
                panel_color,
                panel_surface.get_rect(),
                border_radius=22,
            )
            self.display.screen.blit(panel_surface, panel_rect.topleft)
            self.draw_chrome_rect(
                panel_rect,
                (
                    CHROME_COLORS
                    if not low_time
                    else [(255, 180, 180), (255, 90, 90), WHITE]
                ),
                22,
                4,
            )
            seconds_text = self.display.font_large.render(
                f"{remaining:04.1f}s",
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
            details = self.display.font_small.render(
                f"Tours restants : {challenge_state['turns_left']}",
                True,
                YELLOW,
            )
            self.display.screen.blit(
                details,
                details.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 20)),
            )

    def draw_chrome_rect(self, rect, colors, border_radius, width):
        x, y, rect_width, rect_height = rect
        for index in range(width):
            pygame.draw.rect(
                self.display.screen,
                colors[index % len(colors)],
                (
                    x - index,
                    y - index,
                    rect_width + 2 * index,
                    rect_height + 2 * index,
                ),
                border_radius=border_radius - index if border_radius > index else 0,
                width=1,
            )

    def draw_text_with_outline(
        self,
        text,
        font,
        text_color,
        outline_color,
        position,
        outline_width=2,
        center=False,
    ):
        outline_font = pygame.font.Font(font, font.size + outline_width * 2)
        outline_text = outline_font.render(text, True, outline_color)
        outline_rect = outline_text.get_rect()
        if center:
            outline_rect.center = position
        else:
            outline_rect.topleft = position
        self.display.screen.blit(outline_text, outline_rect)

        actual_text = font.render(text, True, text_color)
        actual_rect = actual_text.get_rect()
        if center:
            actual_rect.center = outline_rect.center
        else:
            actual_rect.topleft = outline_rect.topleft
        self.display.screen.blit(actual_text, actual_rect)

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
        shadow_text = font.render(text, True, shadow_color)
        shadow_position = (
            position[0] + shadow_offset[0],
            position[1] + shadow_offset[1],
        )
        if center:
            shadow_position = (
                shadow_position[0] - shadow_text.get_width() // 2,
                shadow_position[1] - shadow_text.get_height() // 2,
            )
        self.display.screen.blit(shadow_text, shadow_position)

        actual_text = font.render(text, True, text_color)
        actual_position = position
        if center:
            actual_position = (
                actual_position[0] - actual_text.get_width() // 2,
                actual_position[1] - actual_text.get_height() // 2,
            )
        self.display.screen.blit(actual_text, actual_position)

    def draw_menu(self, menu):
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self._draw_option_grid(menu.options, menu.selected_option, show_value=True)
        pygame.display.update()

    def draw_end_menu(self, menu):
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self._draw_option_grid(menu.options, menu.selected_option, show_value=False)
        pygame.display.update()

    def _draw_option_grid(self, options, selected_option, show_value):
        box_width, box_height, margin_x, margin_y = 400, 100, 20, 20
        border_radius, border_width = 15, 5

        semi_transparent_blue, semi_transparent_darkblue = BLUE, DARK_BLUE
        semi_transparent_blue.a, semi_transparent_darkblue.a = 128, 128

        num_rows = (len(options) + 1) // 2
        total_height = num_rows * box_height + (num_rows - 1) * margin_y
        start_x = (self.display.screen.get_width() - (2 * box_width + margin_x)) // 2
        start_y = (self.display.screen.get_height() - total_height) // 2

        for index, option in enumerate(options):
            color = (
                semi_transparent_blue
                if index == selected_option
                else semi_transparent_darkblue
            )
            x = start_x + (index % 2) * (box_width + margin_x)
            y = start_y + (index // 2) * (box_height + margin_y)

            self.draw_chrome_rect(
                (x, y, box_width, box_height),
                CHROME_COLORS,
                border_radius,
                border_width,
            )

            rect_surface = pygame.Surface(
                (box_width - 2 * border_width, box_height - 2 * border_width),
                pygame.SRCALPHA,
            )
            rect_surface = rect_surface.convert_alpha()
            pygame.draw.rect(
                rect_surface,
                color,
                rect_surface.get_rect(),
                border_radius=border_radius - border_width,
            )
            self.display.screen.blit(rect_surface, (x + border_width, y + border_width))

            if show_value:
                name_text = self.display.font_medium.render(option["name"], True, WHITE)
                value_text = self.display.font_medium.render(
                    str(option["value"]), True, YELLOW
                )
                name_text_rect = name_text.get_rect(
                    center=(x + box_width // 2, y + box_height // 2 - 20)
                )
                value_text_rect = value_text.get_rect(
                    center=(x + box_width // 2, y + box_height // 2 + 20)
                )
                self.display.screen.blit(name_text, name_text_rect)
                self.display.screen.blit(value_text, value_text_rect)
            else:
                name_text = self.display.font_medium.render(str(option), True, WHITE)
                name_text_rect = name_text.get_rect(
                    center=(x + box_width // 2, y + box_height // 2)
                )
                self.display.screen.blit(name_text, name_text_rect)

    def play_intro(self):
        sound = self.display.resources.get("intro_sound")
        if sound:
            sound.play()

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

        self.display.screen.blit(self.display.resources["game_background"], (0, 0))
        self.draw_ambient_backdrop(time.monotonic())
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
            self.draw_status_banner(status_text)
        pygame.display.flip()

    def draw_holes(self, holes, challenge_state=None):
        phase = time.monotonic()
        holes_area_rect = (
            2 * self.display.frame_space_x + self.display.frame_score_width,
            self.display.frame_space_y,
            self.display.hole_frame_width,
            self.display.hole_rect_height,
        )
        self.draw_chrome_rect(holes_area_rect, CHROME_COLORS, 20, 5)
        self.draw_marquee_lights(holes_area_rect, phase, (255, 222, 132), count=20)

        for hole in holes:
            x1, y1 = hole.position[0], hole.position[1]
            self.draw_special_hole_accent(hole, (int(x1), int(y1)), phase)
            is_target = (
                challenge_state
                and challenge_state.get("type") == "order"
                and challenge_state.get("target_hole_type") == hole.type
                and challenge_state.get("target_hole_text") == hole.text
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
                self.display.resources["hole"], (x1 - HOLE_RADIUS, y1 - HOLE_RADIUS)
            )
            font = (
                self.display.font_medium
                if hole.type != "large_frog"
                else self.display.font_small
            )
            points_text = font.render(hole.text, True, LIGHT_GREY)
            text_rect = points_text.get_rect(center=(x1, y1))
            self.display.screen.blit(points_text, text_rect)

            if hole.type in {"side", "bottle"}:
                x2, y2 = hole.position2[0], hole.position2[1]
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
                    self.display.resources["hole"],
                    (x2 - HOLE_RADIUS, y2 - HOLE_RADIUS),
                )
                text_rect = points_text.get_rect(center=(x2, y2))
                self.display.screen.blit(points_text, text_rect)

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

        pygame.draw.rect(self.display.screen, PLAYER_OPTION_COLOR, score_rect)
        pygame.draw.rect(
            self.display.screen, PLAYER_OPTION_COLOR, remaining_points_rect
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
            progress_meter_rect, current_progress, score, (84, 214, 126)
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
        self.draw_text_with_shadow(
            f"{team_mode} | {challenge_mode}",
            self.display.font_medium,
            DARK_ORANGE,
            BLACK,
            team_mode_position,
            shadow_offset=(2, 2),
            center=True,
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
            opponent_meter_rect, leader_progress, score, (255, 206, 84)
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
                self.draw_text_with_shadow(
                    f"Total: {sum(player.score for player in group)}",
                    self.display.font_small,
                    WHITE,
                    BLACK,
                    (x, y),
                )

            for player in group:
                frame_key = (
                    "frame_player_select" if player.is_active else "frame_player"
                )
                self.display.screen.blit(
                    self.display.resources[frame_key], (x, y + height_score)
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

                player_label = self.display.font_small.render(
                    str(player), True, DARK_ORANGE
                )
                player_label_pos = (
                    x + 20,
                    y + height_score + (box_height - player_label.get_height()) // 2,
                )
                self.draw_text_with_shadow(
                    str(player),
                    self.display.font_small,
                    DARK_ORANGE,
                    BLACK,
                    player_label_pos,
                )
                score_text_pos = (
                    player_label_pos[0] + player_label.get_width() + 20,
                    y + height_score + (box_height - player_label.get_height()) // 2,
                )
                self.draw_text_with_shadow(
                    str(player.score),
                    self.display.font_small,
                    DARK_ORANGE,
                    BLACK,
                    score_text_pos,
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

    def draw_status_banner(self, status_text):
        phase = time.monotonic()
        banner_width = min(self.display.screen_width - 80, 720)
        banner_height = 54
        banner_rect = pygame.Rect(
            (self.display.screen_width - banner_width) // 2,
            self.display.screen_height - banner_height - 30,
            banner_width,
            banner_height,
        )
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
