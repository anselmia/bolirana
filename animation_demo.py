import logging
import sys
from dataclasses import dataclass

import pygame

from src.constants import TEAM_MODE_SOLO
from src.display import Display
from src.holes import Hole
from src.player import Player


@dataclass(frozen=True)
class DemoAction:
    key: int
    label: str
    description: str
    runner_name: str


class AnimationDemo:
    ACTIONS = [
        DemoAction(pygame.K_1, "Goal Burst", "Premium score impact on a standard hole", "run_goal_demo"),
        DemoAction(pygame.K_2, "Penalty", "Warning sequence followed by the roulette wheel", "run_penalty_demo"),
        DemoAction(pygame.K_3, "Bottle", "Celebration bottle with spray, glow, and bubbles", "run_bottle_demo"),
        DemoAction(pygame.K_4, "Little Frog", "Cinematic jump, catch, splash, and landing", "run_little_frog_demo"),
        DemoAction(pygame.K_5, "Boss Frog", "Large frog summon with portal energy and roulette", "run_large_frog_demo"),
        DemoAction(pygame.K_6, "Winner Spotlight", "Single-player victory stage presentation", "run_player_win_demo"),
        DemoAction(pygame.K_7, "Final Victory", "Full end screen with fireworks and ranking card", "run_final_win_demo"),
        DemoAction(pygame.K_8, "Auto Demo", "Play all premium scenes in sequence", "run_auto_demo"),
        DemoAction(pygame.K_9, "HUD Preview", "Show the polished gameplay HUD and player layout", "draw_demo_scene"),
    ]

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.display = Display(debug=True)
        self.running = True
        self.title_font = self.display.font_large
        self.body_font = self.display.font_small
        self.small_font = self.display.font_verysmall
        self.clock = pygame.time.Clock()
        self.players = self._build_players()
        self.holes = self._build_holes()
        self.demo_goal_hole = self.holes[2]
        self.demo_player = self.players[0]
        self.draw_demo_scene()

    def _build_players(self):
        players = [Player(1), Player(2), Player(3), Player(4)]
        scores = [320, 210, 170, 120]
        ranks = [1, 2, 3, 4]
        for index, player in enumerate(players):
            player.score = scores[index]
            player.rank = ranks[index]
            player.order = index
        players[0].activate()
        return players

    def _build_holes(self):
        return [
            Hole(self.display, "side", 20, [11, 12], "20"),
            Hole(self.display, "bottle", 50, [13, 14], "50"),
            Hole(self.display, "little_frog", 100, [15], "100"),
            Hole(self.display, "large_frog", 0, [16], "ROUL"),
            Hole(self.display, "side", 200, [17], "200"),
        ]

    def draw_demo_scene(self):
        self.display.draw_game(
            self.players,
            self.players[0],
            self.holes,
            500,
            "ARCADE",
            TEAM_MODE_SOLO,
            len(self.players),
            current_progress=self.players[0].score,
            leader_progress=max(player.score for player in self.players),
            challenge_mode="DEMO",
            status_text="Press 1-9 to preview animations | ESC to quit",
        )
        self._draw_demo_overlay()
        pygame.display.flip()

    def _draw_demo_overlay(self):
        panel_width = min(520, self.display.screen_width - 60)
        panel_height = 310
        panel_rect = pygame.Rect(
            self.display.screen_width - panel_width - 24,
            self.display.screen_height - panel_height - 24,
            panel_width,
            panel_height,
        )
        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (4, 18, 38, 220), panel_surface.get_rect(), border_radius=24)
        pygame.draw.rect(panel_surface, (120, 220, 255, 80), panel_surface.get_rect(), border_radius=24, width=2)
        self.display.screen.blit(panel_surface, panel_rect.topleft)

        title = self.title_font.render("Animation Demo", True, (255, 244, 214))
        self.display.screen.blit(title, (panel_rect.left + 24, panel_rect.top + 18))

        y = panel_rect.top + 84
        for action in self.ACTIONS:
            hotkey = pygame.key.name(action.key).upper()
            line = self.body_font.render(f"{hotkey}  {action.label}", True, (255, 214, 96))
            detail = self.small_font.render(action.description, True, (214, 230, 255))
            self.display.screen.blit(line, (panel_rect.left + 24, y))
            self.display.screen.blit(detail, (panel_rect.left + 34, y + 28))
            y += 52

    def run_goal_demo(self):
        self.draw_demo_scene()
        self.display.draw_goal_animation(self.demo_goal_hole, self.demo_goal_hole.pin[0])

    def run_penalty_demo(self):
        self.draw_demo_scene()
        self.display.draw_penalty()

    def run_bottle_demo(self):
        self.draw_demo_scene()
        self.display.animation_bottle()

    def run_little_frog_demo(self):
        self.draw_demo_scene()
        self.display.animation_little_frog()

    def run_large_frog_demo(self):
        self.draw_demo_scene()
        self.display.animation_large_frog()

    def run_player_win_demo(self):
        self.draw_demo_scene()
        self.display.draw_player_win(self.demo_player)

    def run_final_win_demo(self):
        self.display.draw_win(self.players, TEAM_MODE_SOLO)

    def run_auto_demo(self):
        sequence = [
            self.run_goal_demo,
            self.run_bottle_demo,
            self.run_little_frog_demo,
            self.run_penalty_demo,
            self.run_large_frog_demo,
            self.run_player_win_demo,
            self.run_final_win_demo,
        ]
        for runner in sequence:
            if not self.running:
                return
            runner()
            if not self.display.wait_with_event_pump(0.45):
                self.running = False
                return
            self.draw_demo_scene()

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
            return

        for action in self.ACTIONS:
            if key == action.key:
                getattr(self, action.runner_name)()
                self.draw_demo_scene()
                return

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            self.clock.tick(60)

        pygame.quit()


def main():
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        AnimationDemo().run()
    except Exception as error:
        pygame.quit()
        logging.error("Animation demo failed: %s", error)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)