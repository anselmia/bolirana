import pygame
import sys
import logging
import time
import os

from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
    PIN_DOWN,
    PIN_RIGHT,
    PIN_H20,
    PIN_H25,
    PIN_H40,
    PIN_H50,
    PIN_H100,
    PIN_HBOTTLE,
    PIN_HLFROG,
    PIN_HSFROG,
    ACTION_COOLDOWN,
    FPS,
)
from src.pin import PIN
from src.menu import Menu
from src.end_menu import EndMenu
from src.display import Display
from src.game_logic import GameLogic


class Game:
    def __init__(self, debug=False):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Bolirana Game")
        logging.info("Initializing game components...")
        self.display = Display()
        self.menu = Menu()
        self.end_menu = EndMenu()
        self.pin = PIN()
        self.gamelogic = GameLogic()
        self.gamelogic.reset_game()
        self.last_next_action_time = time.time()
        self.in_end_menu = False
        self.debug = debug
        logging.info("Game initialized successfully.")

    def run(self):
        while self.gamelogic.selecting_mode:
            self.process_events("menu")
            self.display.draw_menu(self.menu)
            pygame.time.Clock().tick(FPS)

        self.play()

    def process_events(self, mode):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup()
            elif event.type == pygame.KEYDOWN:
                if mode == "menu":
                    self.handle_key_event(event.key)
                elif mode == "game":
                    self.handle_turn(self.keyboard_input(event.key))
                elif mode == "end_menu":
                    self.handle_end_menu_key_event(event.key)

        if not self.debug:
            pin = self.pin.read_pin_states(mode)
            if pin is not None:
                logging.info(f"Processing event for pin {pin}")
                if mode == "menu":
                    self.handle_menu_button(pin)
                elif mode == "game":
                    self.handle_turn(pin)
                elif mode == "end_menu":
                    self.handle_end_menu_key_event(pin)
                    logging.debug(
                        f"Handled end menu event for pin {pin}, in_end_menu = {self.in_end_menu}"
                    )

    def handle_menu_button(self, pin):
        if pin in [PIN_DOWN, PIN_RIGHT]:
            direction = {
                PIN_DOWN: "DOWN",
                PIN_RIGHT: "RIGHT",
            }[pin]
            self.menu.handle_button_press(direction)
        elif pin == PIN_BENTER:
            self.setup_game_from_menu()
            self.gamelogic.selecting_mode = False

    def setup_game_from_menu(self):
        logging.info("Setting up game from menu selections.")
        self.gamelogic.num_players = self.menu.get_num_players()
        self.gamelogic.team_mode = self.menu.get_team_mode()
        self.gamelogic.score = self.menu.get_score()
        self.gamelogic.game_mode = self.menu.get_game_mode()
        self.gamelogic.num_pairs = self.menu.get_num_pairs()
        self.gamelogic.num_teams = self.menu.get_num_teams()
        self.gamelogic.players_per_team = self.menu.get_players_per_team()
        self.gamelogic.penalty = self.menu.get_penalty()
        self.gamelogic.setup_game(self.display)
        logging.info("Game setup complete.")

    def play(self):
        self.display.play_intro()

        while not self.gamelogic.game_ended:
            self.process_events("game")
            self.gamelogic.check_game_end(self.display)
            if self.gamelogic.draw_game:
                self.update_game_display()
                self.gamelogic.draw_game = False

            pygame.time.Clock().tick(FPS)

        self.display.draw_win(self.gamelogic.players, self.gamelogic.team_mode)
        time.sleep(10)
        self.enter_end_menu()

    def enter_end_menu(self):
        self.in_end_menu = True
        logging.debug("Entering end menu...")
        while self.in_end_menu:
            self.display.draw_end_menu(self.end_menu)
            self.process_events("end_menu")
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)
        logging.debug("Exiting end menu...")
        self.gamelogic.draw_game = True

    def handle_turn(self, pin):
        if pin is not None:
            current_time = time.time()
            if pin == PIN_BNEXT:
                if current_time - self.last_next_action_time >= ACTION_COOLDOWN:
                    self.gamelogic.next_player(self.display)
                    self.gamelogic.draw_game = True
                    self.last_next_action_time = current_time
            elif pin == PIN_BENTER:
                self.enter_end_menu()  # Directly call the end menu when needed
            elif any(pin in hole.pin for hole in self.gamelogic.holes):
                self.gamelogic.goal(pin, self.display)

    def handle_key_event(self, key):
        key_map = {
            pygame.K_DOWN: "DOWN",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_RETURN: self.setup_game_from_menu,
        }
        action = key_map.get(key)
        if isinstance(action, str):
            self.menu.handle_button_press(action)
        elif callable(action):
            action()
            self.gamelogic.selecting_mode = False

    def handle_end_menu_key_event(self, key):
        logging.info(f"handle_end_menu_key_event for pin {key}")
        if self.debug:
            if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN]:
                key_map = {
                    pygame.K_DOWN: "DOWN",
                    pygame.K_RETURN: self.execute_end_menu_option,
                }
                action = key_map[key]
                if callable(action):
                    action()
                    self.in_end_menu = False
                else:
                    self.end_menu.handle_button_press(action)
        else:
            logging.info(f"handling pin end menu for pin {key}")
            if key == PIN_BENTER:
                self.execute_end_menu_option()
            elif key == PIN_DOWN:
                self.end_menu.handle_button_press("DOWN")

    def execute_end_menu_option(self):
        option = self.end_menu.options[self.end_menu.selected_option]
        logging.debug(f"Selected end menu option: {option}")

        if option == "Continuer":
            logging.debug("Continuing the game...")
            self.in_end_menu = False  # Exit the menu and continue the game
        elif option == "Nouveau":
            logging.debug("Starting a new game...")
            self.gamelogic.reset_game()
            self.run()
        elif option == "Recommencer":
            logging.debug("Restarting the game...")
            self.gamelogic.restart_game()
            self.play()
        elif option == "Quitter":
            logging.debug("Quitting the game...")
            self.cleanup()

        logging.debug("Exiting the end menu...")
        self.in_end_menu = False  # Ensure we exit the menu after executing an option

    def keyboard_input(self, key):
        key_map = {
            pygame.K_q: PIN_H20[0],
            pygame.K_s: PIN_H25[0],
            pygame.K_d: PIN_H40[0],
            pygame.K_f: PIN_H50[0],
            pygame.K_g: PIN_H100[0],
            pygame.K_h: PIN_HBOTTLE[0],
            pygame.K_j: PIN_HSFROG[0],
            pygame.K_k: PIN_HLFROG[0],
            pygame.K_n: PIN_BNEXT,
            pygame.K_RETURN: PIN_BENTER,
        }
        return key_map.get(key, None)

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
        logging.info("Cleaning up and shutting down the game.")
        pygame.quit()
        os.system("sudo shutdown now")
        sys.exit()
