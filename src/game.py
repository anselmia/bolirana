import logging
import time

import pygame

from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
    PIN_RIGHT,
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
        self.pin = PIN(self.display.screen)
        self.gamelogic = GameLogic()
        self.gamelogic.reset_game()
        self.last_next_action_time = time.monotonic()
        self.in_end_menu = False
        self.debug = debug
        self.running = True
        self.clock = pygame.time.Clock()
        logging.info("Game initialized successfully.")

    def run(self):
        while self.running:
            self.run_menu()
            if not self.running:
                break

            action = self.play()
            if action == "new_game":
                self.reset_to_menu()
                continue
            break

    def run_menu(self):
        while self.running and self.gamelogic.selecting_mode:
            self.process_events("menu")
            self.display.draw_menu(self.menu)
            self.clock.tick(FPS)

    def reset_to_menu(self):
        self.menu = Menu()
        self.end_menu = EndMenu()
        self.gamelogic.reset_game()
        self.last_next_action_time = time.monotonic()
        self.in_end_menu = False

    def process_events(self, mode):
        if self.debug:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key in KEY_TO_PIN_MAP:
                        pin = KEY_TO_PIN_MAP[event.key]
                        action = self.handle_event(mode, pin)
                        if action is not None:
                            return action
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return "quit"
            pin = self.pin.read_pin_states(mode)
            if pin is not None:
                return self.handle_event(mode, pin)

        return None

    def handle_event(self, mode, pin):
        if mode == "menu" and pin in PIN_TO_ACTION_MAP:
            action = PIN_TO_ACTION_MAP[pin]
            if action in [ACTION_NEXT, ACTION_RIGHT]:
                self.menu.handle_button_press(action)
            else:
                self.setup_game_from_menu()
                self.gamelogic.selecting_mode = False
        elif mode == "game":
            return self.handle_game_event(pin)
        elif mode == "end_menu":
            if pin == PIN_BENTER:
                return self.execute_end_menu_option()
            elif pin == PIN_BNEXT:
                self.end_menu.handle_button_press(ACTION_NEXT)

        return None

    def handle_game_event(self, pin):
        current_time = time.monotonic()
        if pin == PIN_BNEXT:
            if current_time - self.last_next_action_time >= ACTION_COOLDOWN:
                self.gamelogic.next_player(self.display)
                self.gamelogic.draw_game = True
                self.last_next_action_time = current_time
        elif pin == PIN_RIGHT:
            self.gamelogic.start_turn_timer()
        elif pin == PIN_BENTER:
            return "open_end_menu"
        elif pin in self.gamelogic.pin_to_hole:
            self.gamelogic.goal(pin, self.display)

        return None

    def execute_end_menu_option(self):
        option = self.end_menu.options[self.end_menu.selected_option]

        if option == "Continuer":
            return "continue"
        if option == "Nouveau":
            return "new_game"
        if option == "Recommencer":
            return "restart"
        if option == "Quitter":
            self.cleanup()
            return "quit"

        return None

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
        self.gamelogic.challenge_mode = self.menu.get_challenge_mode()
        self.gamelogic.time_attack_seconds = self.menu.get_time_attack_seconds()
        self.gamelogic.time_attack_turns = self.menu.get_time_attack_turns()
        self.gamelogic.setup_game(self.display)
        logging.info("Game setup complete.")

    def play(self):
        self.display.play_intro()

        while self.running:
            while self.running and not self.gamelogic.game_ended:
                action = self.process_events("game")
                if action == "open_end_menu":
                    menu_action = self.enter_end_menu(can_continue=True)
                    if menu_action == "continue":
                        self.gamelogic.draw_game = True
                    elif menu_action == "restart":
                        self.gamelogic.restart_game()
                        continue
                    else:
                        return menu_action

                if not self.running:
                    return "quit"

                self.gamelogic.update_challenge_runtime(self.display)
                self.gamelogic.check_game_end(self.display)
                if self.gamelogic.draw_game:
                    self.update_game_display()
                    self.gamelogic.draw_game = False

                self.clock.tick(FPS)

            if not self.running:
                return "quit"

            self.display.draw_win(self.gamelogic.players, self.gamelogic.team_mode)
            if not self.display.wait_with_event_pump(4):
                self.cleanup()
                return "quit"
            menu_action = self.enter_end_menu(can_continue=False)
            if menu_action == "restart":
                self.gamelogic.restart_game()
                self.display.play_intro()
                continue
            return menu_action

        return "quit"

    def enter_end_menu(self, can_continue):
        self.end_menu.set_context(can_continue)
        self.in_end_menu = True
        while self.running and self.in_end_menu:
            self.display.draw_end_menu(self.end_menu)
            action = self.process_events("end_menu")
            if action is not None:
                self.in_end_menu = False
                self.gamelogic.draw_game = True
                return action
            self.clock.tick(FPS)

        return "quit"

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
            self.gamelogic.get_display_target_score(),
            self.gamelogic.game_mode,
            self.gamelogic.team_mode,
            num_active_players,
            self.gamelogic.get_current_progress_score(),
            self.gamelogic.get_leader_progress_score(),
            self.gamelogic.challenge_mode,
            self.gamelogic.get_status_message(),
            challenge_state=self.gamelogic.get_challenge_state(),
        )

    def cleanup(self):
        logging.info("Cleaning up and shutting down the game.")
        self.running = False
        pygame.quit()
