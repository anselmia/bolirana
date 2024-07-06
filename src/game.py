import pygame
import sys
import logging
import json
import time
from src.constants import *
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
        self.gamelogic = GameLogic()
        self.gamelogic.reset_game()
        self.pin_states = {}
        self.last_read_time = time.time()
        self.last_next_action_time = time.time()  # Timestamp for the last "next" action

    def read_pin_states(self):
        try:
            with open(PIN_STATES_FILE, "r") as file:
                self.pin_states = json.load(file)
            logging.debug(f"Pin states read: {self.pin_states}")
        except (json.JSONDecodeError, FileNotFoundError):
            self.pin_states = {}

    def reset_pin_states(self):
        for pin in self.pin_states:
            self.pin_states[pin] = "LOW"
        with open(PIN_STATES_FILE, "w") as file:
            json.dump(self.pin_states, file)
        logging.debug(f"Pin states reset to LOW: {self.pin_states}")

    def run(self):
        clock = pygame.time.Clock()
        while self.gamelogic.selecting_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event.key)

            self.read_pin_states()  # Update pin states from file
            pin = self.get_next_pin("menu")
            if pin is not None:
                self.handle_menu_button(pin)

            self.display.draw_menu(self.menu)
            pygame.display.flip()
            clock.tick(60)  # Cap the frame rate to 60 FPS

        self.play()
        self.display_end_menu()

    def get_next_pin(self, game_action):
        current_time = time.time()
        if current_time - self.last_read_time < 0.3:
            return None  # Ignore if less than 0.3 seconds have passed

        for pin, state in self.pin_states.items():
            if (
                game_action == "menu"
                and int(pin) in {PIN_BENTER, PIN_DOWN, PIN_UP, PIN_LEFT, PIN_RIGHT}
                and state == "HIGH"
            ):
                self.last_read_time = current_time  # Update the last read time
                self.reset_pin_states()  # Reset pin states to LOW
                return int(pin)
            elif (
                game_action == "game"
                and int(pin)
                in {
                    PIN_BNEXT,
                    PIN_BENTER,
                    PIN_H20,
                    PIN_H25,
                    PIN_H40,
                    PIN_H50,
                    PIN_H100,
                    PIN_HBOTTLE,
                    PIN_HSFROG,
                    PIN_HLFROG,
                }
                and state == "HIGH"
            ):
                self.last_read_time = current_time  # Update the last read time
                self.reset_pin_states()  # Reset pin states to LOW
                return int(pin)
        return None

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
            self.gamelogic.setup_game(self.display.screen_width)
            self.gamelogic.selecting_mode = False  # Transition to the game

    def play(self):
        logging.debug("Starting game...")
        self.display.play_intro()
        clock = pygame.time.Clock()

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

        while not self.gamelogic.game_ended:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.read_pin_states()  # Update pin states from file
            pin = self.get_next_pin("game")
            logging.debug(f"Next pin: {pin}")

            self.handle_turn(pin)
            self.gamelogic.check_game_end(self.display)

            pygame.display.flip()
            clock.tick(60)  # Cap the frame rate to 60 FPS

        self.display.draw_win(self.gamelogic.players, self.gamelogic.team_mode)

    def handle_turn(self, pin):
        if pin is not None:
            logging.debug(f"Handling turn for pin: {pin}")
            current_time = time.time()
            if pin == PIN_BNEXT:
                if (
                    current_time - self.last_next_action_time >= 3
                ):  # Check if 3 seconds have passed
                    self.gamelogic.next_player(self.display)
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
                    self.last_next_action_time = (
                        current_time  # Update the last action time
                    )
            elif (
                next((hole for hole in self.gamelogic.holes if hole.pin == pin), None)
                is not None
            ):
                self.gamelogic.goal(pin, self.display)
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
            elif pin == PIN_BENTER:
                self.display.draw_end_menu(self.gamelogic.players)

    def display_end_menu(self):
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
            self.gamelogic.setup_game(self.display.screen_width)
            self.gamelogic.selecting_mode = False  # Transition to the game

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


if __name__ == "__main__":
    Game().run()
