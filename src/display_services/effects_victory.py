# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame

from src.constants import (
    BLACK,
    CHROME_COLORS,
    DARK_BLUE,
    DARK_GREY,
    GOLD_COLORS,
    GROUP_COLORS,
    TEAM_MODE_DUO,
    TEAM_MODE_SOLO,
    TEAM_MODE_TEAM,
    WHITE,
    YELLOW,
)


class EffectsVictoryMixin:
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

        sorted_groups = sorted(
            groups, key=lambda group: min(player.rank for player in group)
        )
        for group in sorted_groups:
            group.sort(key=lambda player: player.rank)

        def describe_group(group):
            if not group:
                return "Partie terminee"
            if team_mode == TEAM_MODE_TEAM:
                return f"Team {group[0].team}"
            if team_mode == TEAM_MODE_DUO:
                return f"Duo {group[0].team}"
            return str(group[0])

        champion_group = sorted_groups[0] if sorted_groups else []
        champion_score = sum(player.score for player in champion_group)
        champion_label = describe_group(champion_group)
        message = (
            f"Victoire de {champion_label}"
            if champion_group
            else "Partie terminee"
        )

        group_color_map = {
            id(group): GROUP_COLORS[index % len(GROUP_COLORS)]
            for index, group in enumerate(sorted_groups)
        }

        margin_top = 280
        box_height = 52
        gap_between_boxes = 18
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
            start_x = self.display.screen_width / 2 - 340
            box_width = 680
            hor_gap = 0
        else:
            start_x = self.display.screen_width / 2 - 720
            box_width = 660
            hor_gap = 34

        def render(progress):
            phase = time.monotonic()
            self.trigger_cue(
                cues_triggered,
                "crowd-rise",
                0.22,
                progress,
                "applause",
                volume=0.34,
                fade_ms=80,
                maxtime=1100,
            )
            self.trigger_cue(
                cues_triggered,
                "scoreboard-hit",
                0.62,
                progress,
                "applause",
                volume=0.5,
                fade_ms=40,
                maxtime=900,
            )
            self.draw_overlay((4, 10, 30), 118)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.62, tint=(255, 226, 164)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.78, tint=(255, 214, 110), alpha=16
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(255, 220, 126),
                secondary_color=(146, 186, 214),
            )
            self.draw_star_field(
                0.22 + progress * 0.18,
                density=14,
                color=(255, 248, 220),
                drift=8,
                alpha=44,
            )

            title_progress = self.clamp(progress / 0.28)
            title_y = self.lerp(-60, 52, self.ease_out_back(title_progress))
            self.display.ui.draw_title_panel(
                "HALL OF FAME",
                message,
                phase,
                y=int(title_y),
            )
            title_badge_rect = pygame.Rect(
                self.display.screen_width // 2 - 58, int(title_y) - 14, 116, 26
            )
            self.display.ui.draw_badge(
                "FINALE",
                title_badge_rect,
                (18, 28, 44, 220),
                text_color=WHITE,
                border_color=(255, 214, 82, 104),
            )

            summary_rect = pygame.Rect(
                self.display.screen_width // 2 - 330, 178, 660, 76
            )
            self.display.ui.draw_panel_shadow(
                summary_rect,
                alpha=96,
                inflate=22,
                offset=(0, 12),
                border_radius=26,
            )
            summary_surface = pygame.Surface(summary_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                summary_surface,
                (10, 24, 42, 198),
                summary_surface.get_rect(),
                border_radius=26,
            )
            pygame.draw.rect(
                summary_surface,
                (255, 255, 255, 14),
                (12, 12, summary_rect.width - 24, 22),
                border_radius=18,
            )
            pygame.draw.rect(
                summary_surface,
                (255, 214, 82, 84),
                (0, 0, 6, summary_rect.height),
                border_radius=26,
            )
            pygame.draw.rect(
                summary_surface,
                (255, 255, 255, 24),
                summary_surface.get_rect(),
                width=1,
                border_radius=26,
            )
            self.display.screen.blit(summary_surface, summary_rect.topleft)
            self.display.ui.draw_panel_grid(
                summary_rect.inflate(-20, -18),
                phase,
                color=(120, 214, 255),
                alpha=4,
                step=72,
            )
            self.display.ui.draw_badge(
                "CHAMPION",
                (summary_rect.left + 20, summary_rect.top + 16, 120, 24),
                (18, 28, 44, 220),
                text_color=WHITE,
                border_color=(255, 214, 82, 104),
            )
            self.display.ui.draw_badge(
                f"{champion_score} pts",
                (summary_rect.right - 136, summary_rect.top + 16, 116, 24),
                (18, 28, 44, 214),
                text_color=WHITE,
                border_color=(255, 214, 82, 90),
            )
            self.display.ui.draw_text_with_shadow(
                champion_label,
                self.display.font_large,
                WHITE,
                BLACK,
                (summary_rect.centerx, summary_rect.top + 48),
                center=True,
            )

            hall_rect = pygame.Rect(
                int(start_x - 26),
                margin_top - 26,
                int((box_width * columns) + (hor_gap * max(0, columns - 1)) + 52),
                self.display.screen_height - margin_top - 76,
            )
            self.display.ui.draw_panel_shadow(
                hall_rect,
                alpha=94,
                inflate=24,
                offset=(0, 16),
                border_radius=28,
            )
            hall_surface = pygame.Surface(hall_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                hall_surface,
                (8, 20, 38, 196),
                hall_surface.get_rect(),
                border_radius=28,
            )
            pygame.draw.rect(
                hall_surface,
                (255, 255, 255, 12),
                (16, 16, hall_rect.width - 32, 34),
                border_radius=20,
            )
            pygame.draw.rect(
                hall_surface,
                (255, 255, 255, 22),
                hall_surface.get_rect(),
                width=1,
                border_radius=28,
            )
            self.display.screen.blit(hall_surface, hall_rect.topleft)
            self.display.ui.draw_panel_grid(
                hall_rect.inflate(-20, -20),
                phase,
                color=(120, 214, 255),
                alpha=4,
                step=74,
            )
            self.display.ui.draw_text_with_shadow(
                "CLASSEMENT FINAL",
                self.display.font_medium,
                WHITE,
                BLACK,
                (hall_rect.centerx, hall_rect.top + 34),
                center=True,
            )

            x = start_x
            y = margin_top
            row_counter = 0
            for index, group in enumerate(sorted_groups):
                group_color = group_color_map[id(group)]
                if team_mode != TEAM_MODE_SOLO:
                    header_text = (
                        f"Team {group[0].team}"
                        if team_mode == TEAM_MODE_TEAM
                        else f"Duo {group[0].team}"
                    )
                    header_width = max(
                        134, self.display.font_small.size(header_text)[0] + 28
                    )
                    self.display.ui.draw_badge(
                        header_text,
                        (int(x), int(y - 36), header_width, 24),
                        (18, 28, 44, 214),
                        text_color=WHITE,
                        border_color=(*group_color[:3], 104),
                        font=self.display.font_small,
                    )
                for player_index, player in enumerate(group):
                    local = self.clamp((progress - 0.18 - row_counter * 0.05) / 0.24)
                    row_counter += 1
                    if local <= 0:
                        y += box_height + gap_between_boxes
                        continue

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

                    self.display.ui.draw_panel_shadow(
                        row_rect,
                        alpha=84 if player.rank == 1 else 60,
                        inflate=14,
                        offset=(0, 8),
                        border_radius=18,
                    )
                    panel_surface = pygame.Surface(row_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(
                        panel_surface,
                        (10, 22, 38, 212),
                        panel_surface.get_rect(),
                        border_radius=18,
                    )
                    pygame.draw.rect(
                        panel_surface,
                        (255, 255, 255, 12),
                        (10, 8, row_rect.width - 20, 16),
                        border_radius=12,
                    )
                    pygame.draw.rect(
                        panel_surface,
                        (*self.get_rgb(group_color), 108 if player.rank == 1 else 84),
                        (0, 0, 6, row_rect.height),
                        border_radius=18,
                    )
                    pygame.draw.rect(
                        panel_surface,
                        (255, 255, 255, 24),
                        panel_surface.get_rect(),
                        width=1,
                        border_radius=18,
                    )
                    self.display.screen.blit(panel_surface, row_rect.topleft)
                    self.display.ui.draw_panel_grid(
                        row_rect.inflate(-12, -10),
                        phase + row_counter * 0.2,
                        color=group_color,
                        alpha=3,
                        step=58,
                    )
                    if player.rank == 1:
                        pygame.draw.rect(
                            self.display.screen,
                            (255, 214, 82, 120),
                            row_rect,
                            width=2,
                            border_radius=18,
                        )

                    if player.rank == 1:
                        self.draw_glow_circle(
                            (row_rect.left + 16, row_rect.centery),
                            8,
                            YELLOW,
                            glow_radius=20,
                            alpha=76,
                        )

                    medal_text = f"#{player.rank}"
                    medal_width = max(
                        56, self.display.font_small.size(medal_text)[0] + 22
                    )
                    self.display.ui.draw_badge(
                        medal_text,
                        (row_rect.left + 24, row_rect.top + 14, medal_width, 24),
                        (18, 28, 44, 220),
                        text_color=WHITE,
                        border_color=((255, 214, 82, 108) if player.rank == 1 else (*group_color[:3], 90)),
                        font=self.display.font_small,
                    )

                    score_label = f"{player.score} pts"
                    score_width = max(
                        92, self.display.font_small.size(score_label)[0] + 24
                    )
                    self.display.ui.draw_badge(
                        score_label,
                        (
                            row_rect.right - score_width - 24,
                            row_rect.top + 14,
                            score_width,
                            24,
                        ),
                        (18, 28, 44, 214),
                        text_color=WHITE,
                        border_color=(*group_color[:3], 90),
                        font=self.display.font_small,
                    )

                    self.display.ui.draw_text_with_shadow(
                        str(player),
                        self.display.font_medium,
                        WHITE,
                        BLACK,
                        (row_rect.left + 34, row_rect.centery + 7),
                    )
                    y += box_height + gap_between_boxes

                y += gap_between_boxes
                if columns > 1 and index + 1 == math.ceil(len(groups) / 2):
                    x += hor_gap + box_width
                    y = margin_top

        self.animate_scene(1.92, render, background=background)
        self.display.screen.blit(background, (0, 0))
        render(1.0)
        pygame.display.flip()

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
            self.draw_confetti(progress, density=22)
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
                self.draw_cartoon_flash(
                    center,
                    local_progress,
                    color,
                    radius=max(96, int(burst["radius"] * 0.78)),
                    alpha=120,
                )
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
                self.draw_cartoon_starburst(
                    center,
                    local_progress,
                    color,
                    rays=9,
                    inner_radius=16,
                    outer_radius=max(72, int(burst["radius"] * 0.72)),
                    alpha=132,
                    twist=burst["twist"],
                )
                self.draw_cartoon_smoke(
                    center,
                    local_progress,
                    color=(255, 248, 224),
                    puff_count=7,
                    spread=max(82, int(burst["radius"] * 0.52)),
                    alpha=112,
                )
                self.draw_confetti_fountain(
                    (center[0], center[1] + 18),
                    local_progress,
                    palette=[color, WHITE, YELLOW],
                    count=8,
                    spread=92,
                    height=64,
                    alpha=136,
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

        self.animate_scene(1.72, render, background=background)
