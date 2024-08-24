import pygame
import sys
import logging
import time
import os
import platform

from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
    PIN_DOWN,
    PIN_UP,
    PIN_LEFT,
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
from logging.handlers import RotatingFileHandler

# Determine log file path based on platform
if platform.system() == "Windows":
    log_path = os.path.join(os.getenv("APPDATA"), "bolirana", "bolirana.log")
else:
    log_path = "/var/log/bolirana.log"

# Ensure the log directory exists
log_dir = os.path.dirname(log_path)
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3),
        logging.StreamHandler(),
    ],
)


class Game:
    def __init__(self, debug=False):
        log_file_path = "/etc/var/bolirana.log"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",  # Include the timestamp
            datefmt="%Y-%m-%d %H:%M:%S",  # Specify the format for the timestamp
            handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
        )

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
        self.display.draw_end_menu(self.end_menu)

    def process_events(self, mode):
        if self.debug:
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
        else:
            pin = self.pin.read_pin_states(mode)
            if pin is not None:
                if mode == "menu":
                    self.handle_menu_button(pin)
                elif mode == "game":
                    self.handle_turn(pin)
                elif mode == "end_menu":
                    self.handle_end_menu_key_event(pin)

    def handle_menu_button(self, pin):
        if pin in [PIN_UP, PIN_DOWN, PIN_LEFT, PIN_RIGHT]:
            direction = {
                PIN_UP: "UP",
                PIN_DOWN: "DOWN",
                PIN_LEFT: "LEFT",
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
        time.sleep(5)
        self.in_end_menu = True
        while self.in_end_menu:
            self.process_events("end_menu")
            self.display.draw_end_menu(self.end_menu)
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

    def handle_turn(self, pin):
        if pin is not None:
            current_time = time.time()
            if pin == PIN_BNEXT:
                if current_time - self.last_next_action_time >= ACTION_COOLDOWN:
                    self.gamelogic.next_player(self.display)
                    self.gamelogic.draw_game = True
                    self.last_next_action_time = current_time
            elif pin == PIN_BENTER:
                self.in_end_menu = True
                while self.in_end_menu:
                    self.process_events("end_menu")
                    self.display.draw_end_menu(self.end_menu)
                    pygame.time.Clock().tick(FPS)
                self.gamelogic.draw_game = True
            elif any(hole.pin == pin for hole in self.gamelogic.holes):
                self.gamelogic.goal(pin, self.display)

    def handle_key_event(self, key):
        key_map = {
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT",
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
        if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN]:
            key_map = {
                pygame.K_UP: "UP",
                pygame.K_DOWN: "DOWN",
                pygame.K_RETURN: self.execute_end_menu_option,
            }
            action = key_map[key]
            if callable(action):
                action()
                self.in_end_menu = False
            else:
                self.end_menu.handle_button_press(action)

    def execute_end_menu_option(self):
        option = self.end_menu.options[self.end_menu.selected_option]
        if option == "Continuer":
            pass
        elif option == "Nouveau":
            self.gamelogic.reset_game()
            self.run()
        elif option == "Recommencer":
            self.gamelogic.restart_game()
            self.play()
        elif option == "Quitter":
            self.cleanup()

    def keyboard_input(self, key):
        key_map = {
            pygame.K_q: PIN_H20,
            pygame.K_s: PIN_H25,
            pygame.K_d: PIN_H40,
            pygame.K_f: PIN_H50,
            pygame.K_g: PIN_H100,
            pygame.K_h: PIN_HBOTTLE,
            pygame.K_j: PIN_HSFROG,
            pygame.K_k: PIN_HLFROG,
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
