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

        champion_group = sorted_groups[0] if sorted_groups else []
        champion_score = sum(player.score for player in champion_group)
        champion_label = (
            message.replace("Bravo ", "") if message.startswith("Bravo ") else message
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
            self.draw_overlay((4, 10, 30), 88)
            self.display.ui.draw_spotlight_canopy(
                phase, intensity=0.88, tint=(255, 226, 164)
            )
            self.display.ui.draw_stage_floor(
                phase, horizon_ratio=0.78, tint=(255, 214, 110), alpha=26
            )
            self.display.ui.draw_screen_frame(
                phase,
                accent_color=(255, 220, 126),
                secondary_color=(120, 220, 255),
            )
            self.display.ui.draw_scene_badges(
                "HALL OF FAME",
                f"{len(players)} JOUEURS",
                phase,
            )
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
            title_y = self.lerp(-60, 52, self.ease_out_back(title_progress))
            title_rect = pygame.Rect(
                self.display.screen_width // 2 - 350, int(title_y), 700, 112
            )
            self.display.ui.draw_panel_shadow(
                title_rect,
                alpha=118,
                inflate=26,
                offset=(0, 16),
                border_radius=32,
            )
            title_surface = pygame.Surface(title_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                title_surface,
                (10, 26, 54, 224),
                title_surface.get_rect(),
                border_radius=32,
            )
            pygame.draw.rect(
                title_surface,
                (255, 255, 255, 16),
                (14, 14, title_rect.width - 28, 56),
                border_radius=22,
            )
            self.display.screen.blit(title_surface, title_rect.topleft)
            self.display.ui.draw_panel_grid(
                title_rect.inflate(-22, -22),
                phase,
                color=(255, 214, 110),
                alpha=10,
                step=72,
            )
            self.display.ui.draw_chrome_rect(title_rect, GOLD_COLORS, 28, 5)
            self.display.ui.draw_marquee_lights(
                title_rect, phase, (255, 220, 126), count=22
            )
            self.display.ui.draw_badge(
                "FINALE",
                (title_rect.centerx - 58, title_rect.top - 14, 116, 26),
                (255, 214, 82, 224),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )
            self.display.ui.draw_text_with_shadow(
                "HALL OF FAME",
                self.display.font_medium,
                YELLOW,
                BLACK,
                (title_rect.centerx, title_rect.top + 26),
                center=True,
            )
            self.display.ui.draw_text_with_shadow(
                message,
                self.display.font_title_small,
                (255, 248, 222),
                BLACK,
                (title_rect.centerx, title_rect.top + 66),
                center=True,
            )
            self.draw_comic_caption(
                "CHAMPIONS!" if team_mode != TEAM_MODE_SOLO else "LEGENDE!",
                (title_rect.centerx + 238, title_rect.top + 14),
                min(1.0, progress * 1.1),
                fill_color=(255, 232, 152),
                wobble=8.0,
            )
            self.draw_sticker_burst(
                title_rect.midtop,
                min(1.0, progress * 1.08),
                [YELLOW, WHITE, (255, 196, 86)],
                count=8,
                distance=86,
                size=13,
                twist=0.1,
            )
            self.draw_reaction_signs(progress, ["CHAMP!", "OLE!", "MAGIQUE!"])

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
                (10, 28, 56, 214),
                summary_surface.get_rect(),
                border_radius=26,
            )
            pygame.draw.rect(
                summary_surface,
                (255, 255, 255, 14),
                (12, 12, summary_rect.width - 24, 30),
                border_radius=18,
            )
            self.display.screen.blit(summary_surface, summary_rect.topleft)
            self.display.ui.draw_panel_grid(
                summary_rect.inflate(-20, -18),
                phase,
                color=(120, 214, 255),
                alpha=10,
                step=64,
            )
            self.display.ui.draw_chrome_rect(summary_rect, CHROME_COLORS, 24, 4)
            self.display.ui.draw_badge(
                "CHAMPION",
                (summary_rect.left + 20, summary_rect.top + 16, 120, 24),
                (255, 214, 82, 220),
                text_color=BLACK,
                border_color=(255, 255, 255, 90),
            )
            self.display.ui.draw_badge(
                f"{champion_score} pts",
                (summary_rect.right - 136, summary_rect.top + 16, 116, 24),
                (8, 24, 44, 214),
                text_color=YELLOW,
                border_color=(255, 214, 110, 90),
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
                (8, 22, 44, 176),
                hall_surface.get_rect(),
                border_radius=28,
            )
            pygame.draw.rect(
                hall_surface,
                (255, 255, 255, 12),
                (16, 16, hall_rect.width - 32, 52),
                border_radius=20,
            )
            self.display.screen.blit(hall_surface, hall_rect.topleft)
            self.display.ui.draw_panel_grid(
                hall_rect.inflate(-20, -20),
                phase,
                color=(120, 214, 255),
                alpha=8,
                step=66,
            )
            self.display.ui.draw_chrome_rect(hall_rect, CHROME_COLORS, 26, 4)
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
                        (*group_color[:3], 210),
                        text_color=WHITE,
                        border_color=(255, 255, 255, 78),
                        font=self.display.font_small,
                    )
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
                        (*self.get_rgb(bg_color), 206),
                        panel_surface.get_rect(),
                        border_radius=18,
                    )
                    pygame.draw.rect(
                        panel_surface,
                        (255, 255, 255, 14),
                        (10, 8, row_rect.width - 20, 20),
                        border_radius=12,
                    )
                    pygame.draw.rect(
                        panel_surface,
                        (*self.get_rgb(group_color), 150),
                        (10, 10, 10, row_rect.height - 20),
                        border_radius=6,
                    )
                    self.display.screen.blit(panel_surface, row_rect.topleft)
                    self.display.ui.draw_panel_grid(
                        row_rect.inflate(-12, -10),
                        phase + row_counter * 0.2,
                        color=group_color,
                        alpha=8,
                        step=52,
                    )
                    self.display.ui.draw_chrome_rect(
                        row_rect,
                        GOLD_COLORS if player.rank == 1 else CHROME_COLORS,
                        16,
                        4,
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
                        self.display.ui.draw_marquee_lights(
                            row_rect,
                            phase + player.rank * 0.2,
                            (255, 220, 126),
                            count=12,
                            radius=3,
                        )

                    medal_text = f"#{player.rank}"
                    medal_width = max(
                        56, self.display.font_small.size(medal_text)[0] + 22
                    )
                    self.display.ui.draw_badge(
                        medal_text,
                        (row_rect.left + 24, row_rect.top + 14, medal_width, 24),
                        (255, 214, 82, 224) if player.rank == 1 else (8, 24, 44, 214),
                        text_color=BLACK if player.rank == 1 else WHITE,
                        border_color=(255, 255, 255, 88),
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
                        (8, 24, 44, 214),
                        text_color=YELLOW,
                        border_color=(255, 214, 110, 90),
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

        self.animate_scene(1.7, render, background=background)
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
