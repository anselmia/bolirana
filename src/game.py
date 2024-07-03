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
        player_id = 1
        temp_teams = {}

        if self.team_mode == "Seul":
            for i in range(self.num_players):
                self.players.append(Player(player_id))
                player_id += 1
        else:
            num_members = 2 if self.team_mode == "Duo" else self.players_per_team
            num_teams = self.num_pairs if self.team_mode == "Duo" else self.num_teams

            if num_teams == 0 or num_members == 0:
                # Handling potential configuration errors:
                print("Error: No teams or team members specified.")
                return  # Early exit or raise an exception

            for i in range(num_teams):
                for j in range(num_members):
                    player = Player(player_id, i + 1)
                    if i + 1 not in temp_teams:
                        temp_teams[i + 1] = []
                    temp_teams[i + 1].append(player)
                    self.players.append(player)
                    player_id += 1

        if temp_teams:  # Proceed only if temp_teams is not empty
            # Interleave players from each team or duo
            interleaved_players = []
            max_team_size = (
                max(len(team) for team in temp_teams.values()) if temp_teams else 0
            )

            for j in range(max_team_size):
                for team_id in sorted(temp_teams.keys()):
                    if j < len(temp_teams[team_id]):
                        interleaved_players.append(temp_teams[team_id][j])

            self.players = interleaved_players

        # Assign order based on their position in the list
        for index, player in enumerate(self.players):
            player.order = index + 1

        self.players.sort(key=lambda player: player.id)
        self.current_player = self.players[0] if self.players else None
        if self.current_player:
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

    def check_game_end(self):
        if self.team_mode == "Seul":
            self.handle_seul_mode()
        elif self.team_mode == "Duo":
            self.handle_duo_or_team_mode(is_team=False)
        elif self.team_mode == "Equipe":
            self.handle_duo_or_team_mode(is_team=True)

    def handle_seul_mode(self):
        remaining_players = [p for p in self.players if not p.won]
        if len(remaining_players) == 1:
            if len(self.players) == 1:
                # If only one player in the game, they automatically win when they reach the game score
                if remaining_players[0].score >= self.score:
                    remaining_players[0].won = True
                    remaining_players[0].rank = 1
                    self.game_ended = True
            else:
                # Last remaining player automatically wins if they haven't already
                remaining_players[0].won = True
                remaining_players[0].rank = 1
                self.game_ended = True
        else:
            self.update_player_status()

    def handle_duo_or_team_mode(self, is_team):
        groups = self.group_players_by_duo_or_team(is_team)
        remaining_groups = [group for group in groups if not any(p.won for p in group)]

        if len(remaining_groups) == 1:
            # Last remaining group automatically wins
            for player in remaining_groups[0]:
                player.won = True
                player.rank = self.find_next_available_rank()
            self.game_ended = True
        else:
            self.update_group_status(groups)

    def group_players_by_duo_or_team(self, is_team):
        if is_team:
            team_ids = set(player.team for player in self.players)
            return [
                [player for player in self.players if player.team == team_id]
                for team_id in team_ids
            ]
        else:
            pair_ids = set(player.team for player in self.players)
            return [
                [player for player in self.players if player.team == pair_id]
                for pair_id in pair_ids
            ]

    def update_player_status(self):
        for player in self.players:
            if player.score >= self.score and not player.won:
                player.won = True
                player.rank = self.find_next_available_rank()
                self.next_player()

    def update_group_status(self, groups):
        for group in groups:
            if sum(player.score for player in group) >= self.score and not any(
                player.won for player in group
            ):
                next_rank = self.find_next_available_rank()
                for player in group:
                    player.won = True
                    player.rank = next_rank

                self.next_player()
                self.adjust_player_order_after_win()

    def adjust_player_order_after_win(self):
        active_players = [p for p in self.players if not p.won]
        if len(active_players) <= 1:
            return  # No need to adjust if one or no players are active

        active_players.sort(key=lambda p: p.order)
        # Check for consecutive players from the same team and rearrange
        index = 0
        while index < len(active_players) - 1:
            if active_players[index].team == active_players[index + 1].team:
                # Find the next player not from the same team to swap with
                for swap_index in range(index + 2, len(active_players)):
                    if active_players[swap_index].team != active_players[index].team:
                        # Swap to break consecutive team sequence
                        active_players[index + 1], active_players[swap_index] = (
                            active_players[swap_index],
                            active_players[index + 1],
                        )
                        break
                else:
                    # If no suitable player found to swap, break the loop as no further adjustment is possible
                    break
            index += 1

        # Reassign the order based on the new arrangement
        for i, player in enumerate(active_players):
            player.order = i + 1  # Reassign orders starting from 1

    def find_next_available_rank(self):
        used_ranks = set(player.rank for player in self.players if player.rank != 0)
        return max(used_ranks, default=0) + 1 if used_ranks else 1

    def next_player(self):
        if self.current_player.turn_score == 0 and self.penalty:
            points = self.display.draw_penalty()
            self.current_player.score -= points

        self.current_player = Player.activate_next_player(
            self.current_player, self.players
        )

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
