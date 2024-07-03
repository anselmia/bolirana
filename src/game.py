import pygame
import time
import sys
import os
import queue
import random
import logging
from src.constants import *
from src.menu import Menu
from src.holes import Hole
from src.player import Player
from src.display import Display


class Game:
    def __init__(self, queue):
        logging.basicConfig(level=logging.INFO)
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Bolirana Game")
        self.display = Display()
        self.queue = queue
        self.menu = Menu()
        self.init_game()

    def init_game(self):
        # Initialize game state
        self.next_game = False
        self.num_players = 1  # Default number of players
        self.team_mode = "Seul"  # Default team mode
        self.game_mode = "Normal"  # Default game mode
        self.num_pairs = 1  # Default number of pairs
        self.num_teams = 1  # Default number of teams
        self.players_per_team = 1  # Default number of players per team
        self.players = []
        self.current_player = None
        self.selecting_mode = True
        self.game_ended = False
        self.penalty = False
        self.winner = 0

        self.holes = []

    def run(self):
        while self.selecting_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event.key)

            # Check the queue for new data
            # pin = self.process_queue("menu")
            # if pin is not None:
            #    self.handle_menu_button(pin)

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
            self.setup_game()

    def setup_game(self):
        self.num_players = self.menu.get_num_players()
        self.team_mode = self.menu.get_team_mode()
        self.score = self.menu.get_score()
        self.game_mode = self.menu.get_game_mode()
        self.num_pairs = self.menu.get_num_pairs()
        self.num_teams = self.menu.get_num_teams()
        self.players_per_team = self.menu.get_players_per_team()
        self.setup_players()

        penalty = self.menu.get_penalty()
        if penalty == "Avec":
            self.penalty = True

        if self.game_mode == "Normal":
            self.holes.append(
                Hole(
                    "side",
                    20,
                    PIN_H20,
                    "20",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS,
                        250,
                    ),
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 240,
                        250,
                    ),
                ),
            )
            self.holes.append(
                Hole(
                    "side",
                    25,
                    PIN_H25,
                    "25",
                    ((self.display.screen_width / 3.2) + HOLE_RADIUS, 150),
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 240,
                        150,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "side",
                    40,
                    PIN_H40,
                    "40",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 60,
                        200,
                    ),
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 180,
                        200,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "side",
                    50,
                    PIN_H50,
                    "50",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 60,
                        100,
                    ),
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 180,
                        100,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "side",
                    100,
                    PIN_H100,
                    "100",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 60,
                        300,
                    ),
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 180,
                        300,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "bottle",
                    150,
                    PIN_HBOTTLE,
                    "150",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS,
                        50,
                    ),
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 240,
                        50,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "little_frog",
                    200,
                    PIN_HSFROG,
                    "200",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 120,
                        150,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "large_frog",
                    0,
                    PIN_HLFROG,
                    "ROUL",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 120,
                        50,
                    ),
                )
            )
        elif self.game_mode == "Grenouille":
            self.holes.append(
                Hole(
                    "little_frog",
                    200,
                    PIN_HSFROG,
                    "200",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 120,
                        150,
                    ),
                )
            )
            self.holes.append(
                Hole(
                    "large_frog",
                    0,
                    PIN_HLFROG,
                    "ROUL",
                    (
                        (self.display.screen_width / 3.2) + HOLE_RADIUS + 120,
                        50,
                    ),
                )
            )
        elif self.game_mode == "Bouteille":
            Hole(
                "bottle",
                150,
                PIN_HBOTTLE,
                "150",
                (
                    (self.display.screen_width / 3.2) + HOLE_RADIUS,
                    50,
                ),
                (
                    (self.display.screen_width / 3.2) + HOLE_RADIUS + 240,
                    50,
                ),
            )

        self.selecting_mode = False

    def setup_players(self):
        player_id = 1  # Initialize player ID counter
        if self.team_mode == "Seul":
            for i in range(self.num_players):
                self.players.append(Player(player_id))
                player_id += 1
        elif self.team_mode == "Duo":
            for i in range(self.num_pairs):
                for j in range(2):
                    self.players.append(Player(player_id, i + 1))
                    player_id += 1
        elif self.team_mode == "Equipe":
            for i in range(self.num_teams):
                for j in range(self.players_per_team):
                    self.players.append(Player(player_id, i + 1))
                    player_id += 1

        random.shuffle(self.players)

        # Assign order based on their position in the shuffled list
        for index, player in enumerate(self.players):
            player.order = index + 1

        self.players.sort(key=lambda player: player.id)
        self.current_player = next(
            player for player in self.players if player.order == 1
        )
        self.current_player.activate()

    def play(self):
        sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "intro.mp3",
            )
        )
        sound.play()

        while not self.game_ended:
            self.display.draw_game(
                self.players,
                self.current_player,
                self.holes,
                self.score,
                self.game_mode,
                self.team_mode,
                (
                    len(self.players)
                    if self.team_mode == "Seul"
                    else self.players_per_team
                ),
            )
            self.handle_turn()
            self.check_game_end()

        self.display.draw_win(self.players, self.team_mode)

    def handle_turn(self):
        # pin = self.process_queue("game")
        pin = self.read_input()
        if pin is not None:
            if pin == PIN_BNEXT:
                self.next_player()
            elif (
                next((hole for hole in self.holes if hole.pin == pin), None) is not None
            ):
                self.goal(pin)
            elif pin == PIN_BENTER:
                self.display.draw_end_menu()

    def next_player(self):
        if self.current_player.turn_score == 0 and self.penalty:
            points = self.display.draw_penalty()
            self.current_player.score -= points

        self.current_player = Player.activate_next_player(self.players)
        if self.current_player is None:
            self.game_ended = True
            if len(self.players) > 1:
                last = next(player for player in self.players if player.rank == 0)
                last.rank = len(self.players)

    def goal(self, pin):
        hole = next((hole for hole in self.holes if pin == hole.pin), None)
        points = 0
        if hole is not None:
            points = hole.value
            self.display.draw_goal_animation(hole)
            if hole.type == "bottle":
                self.display.animation_bottle()
            if hole.type == "little_frog":
                self.display.animation_little_frog()
            if hole.type == "large_frog":
                points = self.display.animation_large_frog()

        self.current_player.score += points
        self.current_player.turn_score += points

        if self.current_player.score >= self.score:
            self.current_player.update_rank(self.players)
            self.next_player()

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
