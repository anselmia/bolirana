import pygame
import time
import sys
import queue
import logging
from src.constants import *
from src.menu import Menu
from src.display import Display
from src.game_logic import GameLogic


class Game:
    def __init__(self, queue):
        logging.basicConfig(level=logging.INFO)
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Bolirana Game")
        self.display = Display()
        self.queue = queue
        self.menu = Menu()
        self.gamelogic = GameLogic()
        self.gamelogic.reset_game()

    def run(self):
        while self.gamelogic.selecting_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event.key)

            # Check the queue for new data
            pin = self.process_queue("menu")
            if pin is not None:
                self.handle_menu_button(pin)

            self.display.draw_menu(self.menu)
            pygame.display.flip()
            time.sleep(0.1)

        self.play()
        self.display_end_menu()

    def process_queue(self, game_action):
        try:
            if game_action == "menu":
                pin, state = self.queue.get_nowait()  # Non-blocking get
                if (
                    pin == PIN_BENTER
                    or pin == PIN_DOWN
                    or pin == PIN_UP
                    or pin == PIN_LEFT
                    or pin == PIN_RIGHT
                ) and state == "HIGH":
                    return pin
            elif game_action == "game":
                if (
                    pin == PIN_BNEXT
                    or pin == PIN_BENTER
                    or pin == PIN_H20
                    or pin == PIN_H25
                    or pin == PIN_H40
                    or pin == PIN_H50
                    or pin == PIN_H100
                    or pin == PIN_HBOTTLE
                    or pin == PIN_HSFROG
                    or pin == PIN_HLFROG
                ) and state == "HIGH":
                    return pin
        except queue.Empty:
            return None

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

    def play(self):
        self.display.play_intro()

        while not self.gamelogic.game_ended:
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
            self.handle_turn()
            self.gamelogic.check_game_end(self.display)

        self.display.draw_win(self.gamelogic.players, self.gamelogic.team_mode)

    def handle_turn(self):
        # pin = self.process_queue("game")
        pin = self.read_input()
        if pin is not None:
            if pin == PIN_BNEXT:
                self.gamelogic.next_player(self.display)
            elif (
                next((hole for hole in self.gamelogic.holes if hole.pin == pin), None)
                is not None
            ):
                self.gamelogic.goal(pin, self.display)
            elif pin == PIN_BENTER:
                self.display.draw_end_menu()

    def display_end_menu():
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
