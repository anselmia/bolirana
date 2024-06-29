import pygame
from src.constants import *
from src.menu import Menu
from src.mdns import MDNSListener
import time
import sys
import random


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bolirana Game")
        self.font = pygame.font.Font(None, 36)
        self.menu = Menu(self.screen, self.font)
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
        self.scores = {}
        self.selecting_mode = True

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

        print("Starting game with settings:")
        print(f"Number of players: {self.num_players}")
        print(f"Team mode: {self.team_mode}")
        if self.team_mode == "Paire":
            print(f"Number of pairs: {self.num_pairs}")
        elif self.team_mode == "Equipe":
            print(
                f"Number of teams: {self.num_teams}, Players per team: {self.players_per_team}"
            )
        print(f"Game mode: {self.game_mode}")
        print(f"Players: {self.players}")

        # Start the game loop based on game mode
        if self.game_mode == "Normal":
            self.play_normal_mode()
        elif self.game_mode == "Côté":
            self.play_cote_mode()
        elif self.game_mode == "Bouteille":
            self.play_bouteille_mode()

        pygame.quit()
        sys.exit()

    def setup_players(self):
        players = []
        if self.team_mode == "Seul":
            for i in range(self.num_players):
                players.append(f"Player {i+1}")
        elif self.team_mode == "Paire":
            for pair_num in range(1, self.num_pairs + 1):
                players.extend(
                    [f"Pair {pair_num} - Player 1", f"Pair {pair_num} - Player 2"]
                )
        elif self.team_mode == "Equipe":
            for team_num in range(1, self.num_teams + 1):
                for player_num in range(1, self.players_per_team + 1):
                    players.append(f"Team {team_num} - Player {player_num}")
        return players

    def play_normal_mode(self):
        while self.current_ball <= NUM_BALLS_PER_PLAYER:
            self.display_current_player()
            self.handle_turn()
            self.current_ball += 1

    def play_cote_mode(self):
        while self.current_ball <= NUM_BALLS_PER_PLAYER:
            self.display_current_player()
            self.handle_turn()
            self.current_ball += 1
        self.end_game()

    def play_bouteille_mode(self):
        while self.current_ball <= NUM_BALLS_PER_PLAYER:
            self.display_current_player()
            self.handle_turn()
            self.current_ball += 1
        self.end_game()

    def display_current_player(self):
        self.screen.fill(BLACK)
        current_player_name = self.players[self.current_player_index]
        text = self.font.render(f"Current Player: {current_player_name}", True, WHITE)
        self.screen.blit(text, (250, 250))
        pygame.display.flip()
        time.sleep(1)  # Pause to show current player

    def handle_turn(self):
        # Placeholder for handling user input or mDNS input for ball throw
        # For simplicity, let's just increment score by points per ball
        points = POINTS_PER_BALL
        self.scores[self.players[self.current_player_index]] += points
        print(f"{self.players[self.current_player_index]} scored {points} points.")

        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def end_game(self):
        print("Game ended!")
        print("Final scores:")
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
            self.num_players = self.menu.get_num_players()
            self.team_mode = self.menu.get_team_mode()
            self.score = self.menu.get_score()
            self.game_mode = self.menu.get_game_mode()
            self.num_pairs = self.menu.get_num_pairs()
            self.num_teams = self.menu.get_num_teams()
            self.players_per_team = self.menu.get_players_per_team()
            self.players = self.setup_players()
            random.shuffle(self.players)  # Randomize player order
            self.selecting_mode = False


# Example of starting the game if this file is run directly
if __name__ == "__main__":
    game = Game()
    game.run()
