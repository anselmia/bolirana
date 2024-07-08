import pygame
import sys
import logging
import time
from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
    PIN_DOWN,
    PIN_UP,
    PIN_LEFT,
    PIN_RIGHT,
    ACTION_COOLDOWN,
    FPS,
)
from src.pin import PIN
from src.menu import Menu
from src.display import Display
from src.game_logic import GameLogic


class Game:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Bolirana Game")
        self.display = Display()
        self.menu = Menu()
        self.pin = PIN()
        self.gamelogic = GameLogic()
        self.gamelogic.reset_game()
        self.last_next_action_time = time.time()

    def run(self):
        while self.gamelogic.selecting_mode:
            for event in pygame.event.get():
                logging.debug(f"Event detected: {event}")
                if event.type == pygame.QUIT:
                    self.cleanup()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event.key)

            pin = self.pin.read_pin_states("menu")
            if pin is not None:
                self.handle_menu_button(pin)

            self.display.draw_menu(self.menu)
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)  # Cap the frame rate to FPS

        self.play()
        self.display_end_menu()

    def handle_menu_button(self, pin):
        if pin == PIN_UP:
            self.menu.handle_button_press("UP")
        elif pin == PIN_DOWN:
            self.menu.handle_button_press("DOWN")
        elif pin == PIN_LEFT:
            self.menu.handle_button_press("LEFT")
        elif pin == PIN_RIGHT:
            self.menu.handle_button_press("RIGHT")
        elif pin == PIN_BENTER:
            self.gamelogic.num_players = self.menu.get_num_players()
            self.gamelogic.team_mode = self.menu.get_team_mode()
            self.gamelogic.score = self.menu.get_score()
            self.gamelogic.game_mode = self.menu.get_game_mode()
            self.gamelogic.num_pairs = self.menu.get_num_pairs()
            self.gamelogic.num_teams = self.menu.get_num_teams()
            self.gamelogic.players_per_team = self.menu.get_players_per_team()
            self.gamelogic.penalty = self.menu.get_penalty()
            self.gamelogic.setup_game(self.display)
            self.gamelogic.selecting_mode = False  # Transition to the game

    def play(self):
        logging.debug("Starting game...")
        self.display.play_intro()
        self.update_game_display()

        while not self.gamelogic.game_ended:
            for event in pygame.event.get():
                logging.debug(f"Event detected: {event}")
                if event.type == pygame.QUIT:
                    self.cleanup()

            pin = self.pin.read_pin_states("game")
            self.handle_turn(pin)
            self.gamelogic.check_game_end(self.display)
            if self.gamelogic.draw_game:
                self.update_game_display()
                self.gamelogic.draw_game = False

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)  # Cap the frame rate to FPS

        self.display.draw_win(self.gamelogic.players, self.gamelogic.team_mode)

    def handle_turn(self, pin):
        if pin is not None:
            logging.debug(f"Handling turn for pin: {pin}")
            current_time = time.time()
            if pin == PIN_BNEXT:
                if current_time - self.last_next_action_time >= ACTION_COOLDOWN:
                    self.gamelogic.next_player(self.display)
                    self.update_game_display()
                    self.last_next_action_time = (
                        current_time  # Update the last action time
                    )
            elif (
                next((hole for hole in self.gamelogic.holes if hole.pin == pin), None)
                is not None
            ):
                self.gamelogic.goal(pin, self.display)
                self.update_game_display()
            elif pin == PIN_BENTER:
                self.display.draw_end_menu(self.gamelogic.players)

    def display_end_menu(self):
        # Future implementation for end menu
        pass

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
            self.gamelogic.num_players = self.menu.get_num_players()
            self.gamelogic.team_mode = self.menu.get_team_mode()
            self.gamelogic.score = self.menu.get_score()
            self.gamelogic.game_mode = self.menu.get_game_mode()
            self.gamelogic.num_pairs = self.menu.get_num_pairs()
            self.gamelogic.num_teams = self.menu.get_num_teams()
            self.gamelogic.players_per_team = self.menu.get_players_per_team()
            self.gamelogic.penalty = self.menu.get_penalty()
            self.gamelogic.setup_game(self.display)
            self.gamelogic.selecting_mode = False  # Transition to the game

    def update_game_display(self):
        self.display.draw_game(
            self.gamelogic.players,
            self.gamelogic.current_player,
            self.gamelogic.holes,
            self.gamelogic.score,
            self.gamelogic.game_mode,
            self.gamelogic.team_mode,
            (
                len(self.gamelogic.players)
                if self.gamelogic.team_mode == "Seul"
                else self.gamelogic.players_per_team
            ),
        )

    def cleanup(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
