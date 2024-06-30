import pygame
from src.constants import *
from src.menu import Menu
from src.mdns import MDNSListener
from src.holes import Hole
import time
import sys
import random
import os


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Bolirana Game")
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.menu = Menu(self.screen, self.font_small)
        self.mdns_listener = MDNSListener()

        # Initialize game state
        self.num_players = 1  # Default number of players
        self.team_mode = "Seul"  # Default team mode
        self.game_mode = "Normal"  # Default game mode
        self.num_pairs = 1  # Default number of pairs
        self.num_teams = 1  # Default number of teams
        self.players_per_team = 1  # Default number of players per team
        self.players = []
        self.current_player_index = 0
        self.current_ball = 1
        self.selecting_mode = True
        self.game_ended = False

        # Load the background image
        game_background_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "images", "game_background.jpg"
        )
        if not os.path.exists(game_background_path):
            raise FileNotFoundError(f"No such file: {game_background_path}")
        self.background = pygame.image.load(game_background_path)
        self.background = pygame.transform.scale(
            self.background, self.screen.get_size()
        )

    def run(self):
        while self.selecting_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event.key)

            self.menu.draw()
            pygame.display.flip()
            time.sleep(0.1)

        print("Début du jeu :")
        print(f"Nombre de joueurs: {self.num_players}")
        print(f"Equipe: {self.team_mode}")
        if self.team_mode == "Duo":
            print(f"Nombre de paires: {self.num_pairs}")
        elif self.team_mode == "Equipe":
            print(
                f"Nombre d'équipes: {self.num_teams}, Joueurs / équipe: {self.players_per_team}"
            )
        print(f"Mode de Jeu: {self.game_mode}")
        print(f"Joueurs: {self.players}")

        self.play()

        pygame.quit()
        sys.exit()

    def setup_game(self):
        self.num_players = self.menu.get_num_players()
        self.team_mode = self.menu.get_team_mode()
        self.score = self.menu.get_score()
        self.game_mode = self.menu.get_game_mode()
        self.num_pairs = self.menu.get_num_pairs()
        self.num_teams = self.menu.get_num_teams()
        self.players_per_team = self.menu.get_players_per_team()
        self.players = self.setup_players()
        random.shuffle(self.players)  # Randomize player order
        self.scores = [0] * len(self.players)
        for i in range(len(self.players)):
            self.scores[i] = 0
        self.selecting_mode = False

        self.holes = [
            Hole("20", 20, PIN_H20),
            Hole("25", 25, PIN_H25),
            Hole("40", 40, PIN_H40),
            Hole("50", 50, PIN_H50),
            Hole("100", 100, PIN_H100),
            Hole("bottle", 150, PIN_HBOTTLE),
            Hole("little_frog", 200, PIN_HSFROG),
            Hole("large_frog", 0, PIN_HLFROG),
        ]

    def setup_players(self):
        players = []
        if self.team_mode == "Seul":
            for i in range(self.num_players):
                players.append(f"Joueur {i+1}")
        elif self.team_mode == "Duo":
            for pair_num in range(1, self.num_pairs + 1):
                players.extend(
                    [f"Duo {pair_num} - Joueur 1", f"Duo {pair_num} - Joueur 2"]
                )
        elif self.team_mode == "Equipe":
            for team_num in range(1, self.num_teams + 1):
                for player_num in range(1, self.players_per_team + 1):
                    players.append(f"Equipe {team_num} - Joueur {player_num}")
        return players

    def play(self):
        while not self.game_ended:
            self.display_game()
            self.handle_turn()

        self.end_game()

    def display_game(self):
        self.screen.blit(self.background, (0, 0))  # Draw the background image

        # Draw current player, their score, and remaining points
        current_player_name = f"Joueur {self.current_player_index + 1}"
        current_player_score = f"Score: {self.scores[self.current_player_index]}"
        remaining_points_text = (
            f"Points Restants: {self.score - self.scores[self.current_player_index]}"
        )

        current_player_name_text = self.font_large.render(
            current_player_name, True, pygame.Color("white")
        )
        current_player_score_text = self.font_medium.render(
            current_player_score, True, pygame.Color("white")
        )
        remaining_points_text_rendered = self.font_medium.render(
            remaining_points_text, True, pygame.Color("white")
        )

        self.screen.blit(current_player_name_text, (20, 20))
        self.screen.blit(current_player_score_text, (20, 80))
        self.screen.blit(remaining_points_text_rendered, (20, 120))

        # Draw holes and associated points
        hole_points = [
            150,
            50,
            25,
            40,
            20,
            100,
            "ROUL",
            200,
            150,
            50,
            25,
            40,
            20,
            100,
        ]
        hole_positions = [
            (400, 50),
            (460, 100),
            (400, 150),
            (460, 200),
            (400, 250),
            (460, 300),
            (520, 50),
            (520, 150),
            (640, 50),
            (580, 100),
            (640, 150),
            (580, 200),
            (640, 250),
            (580, 300),
        ]
        circle_radius = 30

        for i, points in enumerate(hole_points):
            x, y = hole_positions[i]
            pygame.draw.circle(
                self.screen, pygame.Color("white"), (x, y), circle_radius
            )
            font = self.font_medium
            if str(points) == "ROUL":
                font = self.font_small
            points_text = font.render(str(points), True, pygame.Color("black"))
            text_rect = points_text.get_rect(center=(x, y))
            self.screen.blit(points_text, text_rect)

        # Draw all players and their scores
        start_x = 50
        start_y = 500
        box_width = 90
        box_height = 50
        margin_y = 10

        for i in range(len(self.scores)):
            x = start_x + (i % 6) * (box_width + 20)
            y = start_y + (i // 6) * (box_height + margin_y)
            player_label = self.font_small.render(
                f"Joueur {i + 1}", True, pygame.Color("yellow")
            )
            score_text = self.font_medium.render(
                f"{self.scores[i]}", True, pygame.Color("white")
            )
            pygame.draw.rect(
                self.screen,
                pygame.Color("black"),
                (x, y, box_width, box_height),
                border_radius=5,
            )
            self.screen.blit(player_label, (x + 5, y + 5))
            self.screen.blit(score_text, (x + 5, y + 25))

        pygame.display.flip()

    def handle_turn(self):
        pin = self.read_input()
        if pin == PIN_BNEXT:
            self.next_player()
        elif (
            pin == PIN_H20
            or pin == PIN_H25
            or pin == PIN_H40
            or pin == PIN_H50
            or pin == PIN_H100
            or pin == PIN_HBOTTLE
            or pin == PIN_HSFROG
            or pin == PIN_HLFROG
        ):
            self.goal(pin)

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def goal(self, pin):
        hole = next((hole for hole in self.holes if pin == hole.pin), None)
        points = 0
        if hole is not None:
            if (
                hole.type == "20"
                or hole.type == "25"
                or hole.type == "40"
                or hole.type == "50"
                or hole.type == "100"
                or hole.type == "bottle"
                or hole.type == "little_frog"
            ):
                points = hole.value
            if hole.type == "bottle":
                self.animation_bottle()
            if hole.type == "little_frog":
                self.animation_little_frog()
            if hole.type == "large_frog":
                self.animation_large_frog()

        self.scores[self.current_player_index] += points

    def animation_bottle(self):
        return

    def animation_little_frog(self):
        return

    def animation_large_frog(self):
        return

    def end_game(self):
        print("Fin du jeu!")
        print("Scores:")
        for player, score in self.scores.items():
            print(f"{player}: {score}")
        # Add logic to handle end of game actions (e.g., display winner, reset, etc.)
        # Example: self.reset_game()

    def handle_key_event(self, key):
        if key == pygame.K_UP:
            self.menu.handle_button_press("UP")
        elif key == pygame.K_DOWN:
            self.menu.handle_button_press("DOWN")
        elif key == pygame.K_LEFT:
            self.menu.handle_button_press("LEFT")
        elif key == pygame.K_RIGHT:
            self.menu.handle_button_press("RIGHT")
        elif key == pygame.K_RETURN:
            self.setup_game()

    def read_input(self):
        pin = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pin = PIN_H20
                    break
                elif event.key == pygame.K_s:
                    pin = PIN_H25
                    break
                elif event.key == pygame.K_d:
                    pin = PIN_H40
                    break
                elif event.key == pygame.K_f:
                    pin = PIN_H50
                    break
                elif event.key == pygame.K_g:
                    pin = PIN_H100
                    break
                elif event.key == pygame.K_h:
                    pin = PIN_HBOTTLE
                    break
                elif event.key == pygame.K_j:
                    pin = PIN_HSFROG
                    break
                elif event.key == pygame.K_k:
                    pin = PIN_HLFROG
                    break
                elif event.key == pygame.K_n:
                    pin = PIN_BNEXT
                    break

        return pin


# Example of starting the game if this file is run directly
if __name__ == "__main__":
    game = Game()
    game.run()
