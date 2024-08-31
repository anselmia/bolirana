import pygame
import sys
import logging
import time
import os

from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
    ACTION_NEXT,
    ACTION_RIGHT,
    ACTION_COOLDOWN,
    FPS,
    PIN_TO_ACTION_MAP,
    KEY_TO_PIN_MAP,
    TEAM_MODE_SOLO,
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
        self.display = Display(debug)
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
        if self.debug:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                elif event.type == pygame.KEYDOWN:
                    if event.key in KEY_TO_PIN_MAP:
                        pin = KEY_TO_PIN_MAP[event.key]
                        self.handle_event(mode, pin)
        else:
            pin = self.pin.read_pin_states(mode)
            if pin is not None:
                self.handle_event(mode, pin)

    def handle_event(self, mode, pin):
        if mode == "menu" and pin in PIN_TO_ACTION_MAP:
            action = PIN_TO_ACTION_MAP[pin]
            if action in [ACTION_NEXT, ACTION_RIGHT]:
                self.menu.handle_button_press(action)
            else:
                self.setup_game_from_menu()
                self.gamelogic.selecting_mode = False
        elif mode == "game":
            self.handle_game_event(pin)
        elif mode == "end_menu":
            if pin == PIN_BENTER:
                self.execute_end_menu_option()
            elif pin == PIN_BNEXT:
                self.end_menu.handle_button_press(ACTION_NEXT)

    def handle_game_event(self, pin):
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

    def execute_end_menu_option(self):
        option = self.end_menu.options[self.end_menu.selected_option]

        if option == "Continuer":
            self.in_end_menu = False  # Exit the menu and continue the game
        elif option == "Nouveau":
            self.gamelogic.reset_game()
            self.run()
        elif option == "Recommencer":
            self.gamelogic.restart_game()
            self.play()
        elif option == "Quitter":
            self.cleanup()

        self.in_end_menu = False  # Ensure we exit the menu after executing an option

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
            if self.gamelogic.draw_score:
                self.draw_score()
                self.gamelogic.draw_score = False

            pygame.time.Clock().tick(FPS)

        self.display.draw_win(self.gamelogic.players, self.gamelogic.team_mode)
        time.sleep(10)
        self.enter_end_menu()

    def enter_end_menu(self):
        self.in_end_menu = True
        while self.in_end_menu:
            self.display.draw_end_menu(self.end_menu)
            self.process_events("end_menu")
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)
        self.gamelogic.draw_game = True

    def update_game_display(self):
        num_active_players = (
            len(self.gamelogic.players)
            if self.gamelogic.team_mode == TEAM_MODE_SOLO
            else self.gamelogic.players_per_team
        )

        self.display.draw_game(
            self.gamelogic.players,
            self.gamelogic.current_player,
            self.gamelogic.holes,
            self.gamelogic.score,
            self.gamelogic.game_mode,
            self.gamelogic.team_mode,
            num_active_players,
        )

    def draw_score(self):
        self.display.draw_score(
            self.gamelogic.players,
            self.gamelogic.current_player,
            self.gamelogic.holes,
            self.gamelogic.score,
            self.gamelogic.game_mode,
            self.gamelogic.team_mode,
            (
                len(self.gamelogic.players)
                if self.gamelogic.team_mode == TEAM_MODE_SOLO
                else self.gamelogic.players_per_team
            ),
        )

    def cleanup(self):
        logging.info("Cleaning up and shutting down the game.")
        pygame.quit()
        os.system("sudo shutdown now")
        sys.exit()
