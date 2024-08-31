import logging

from src.holes import Hole
from src.constants import (
    PIN_H20,
    PIN_H25,
    PIN_H40,
    PIN_H50,
    PIN_H100,
    PIN_HBOTTLE,
    PIN_HSFROG,
    PIN_HLFROG,
    MODE_NORMAL,
    MODE_FROG,
    MODE_BOTTLE,
    TEAM_MODE_SOLO,
    TEAM_MODE_DUO,
    TEAM_MODE_TEAM,
    ON,
)
from src.player import Player


class GameLogic:
    def __init__(self):
        logging.info("Initializing GameLogic...")
        self.reset_game()

    def reset_game(self):
        logging.info("Resetting the game...")
        self.num_players = 1
        self.team_mode = TEAM_MODE_SOLO
        self.game_mode = MODE_NORMAL
        self.num_pairs = 1
        self.num_teams = 1
        self.players_per_team = 1
        self.players = []
        self.current_player = None
        self.selecting_mode = True
        self.game_ended = False
        self.penalty = False
        self.score = 0
        self.holes = []
        self.draw_game = True
        self.draw_score = False
        logging.info("Game reset complete.")

    def restart_game(self):
        logging.info("Restarting the game...")
        for player in self.players:
            player.reset()
        self.current_player = self.players[0] if self.players else None
        if self.current_player:
            self.current_player.activate()
        self.game_ended = False
        self.draw_game = True
        self.draw_score = False
        logging.info("Game restarted.")

    def setup_game(self, display):
        logging.info("Setting up the game...")
        self.setup_players()
        self.penalty = self.penalty == ON
        setup_methods = {
            MODE_NORMAL: self.setup_normal_mode,
            MODE_FROG: self.setup_grenouille_mode,
            MODE_BOTTLE: self.setup_bouteille_mode,
        }
        setup_method = setup_methods.get(self.game_mode, None)
        if setup_method:
            setup_method(display)
            logging.info(f"Game mode '{self.game_mode}' setup complete.")
        else:
            logging.error(f"Unknown game mode: {self.game_mode}")
        self.selecting_mode = False

    def setup_normal_mode(self, display):
        self.holes = [
            Hole(display, "side", 20, PIN_H20, "20"),
            Hole(display, "side", 25, PIN_H25, "25"),
            Hole(display, "side", 40, PIN_H40, "40"),
            Hole(display, "side", 50, PIN_H50, "50"),
            Hole(display, "side", 100, PIN_H100, "100"),
            Hole(display, "bottle", 150, PIN_HBOTTLE, "150"),
            Hole(display, "little_frog", 200, PIN_HSFROG, "200"),
            Hole(display, "large_frog", 0, PIN_HLFROG, "ROUL"),
        ]

    def setup_grenouille_mode(self, display):
        self.holes = [
            Hole(display, "little_frog", 200, PIN_HSFROG, "200"),
            Hole(display, "large_frog", 0, PIN_HLFROG, "ROUL"),
        ]

    def setup_bouteille_mode(self, display):
        self.holes = [Hole(display, "bottle", 150, PIN_HBOTTLE, "150")]

    def setup_players(self):
        player_id = 1
        if self.team_mode == TEAM_MODE_SOLO:
            self.players = [Player(player_id + i) for i in range(self.num_players)]
            for i, player in enumerate(self.players):
                player.order = i + 1
        else:
            self.setup_team_players(player_id)

        self.players.sort(key=lambda player: player.id)
        self.current_player = self.players[0] if self.players else None
        if self.current_player:
            self.current_player.activate()

    def setup_team_players(self, player_id):
        temp_teams = {}
        num_members = 2 if self.team_mode == TEAM_MODE_DUO else self.players_per_team
        num_teams = (
            self.num_pairs if self.team_mode == TEAM_MODE_DUO else self.num_teams
        )

        if num_teams == 0 or num_members == 0:
            logging.error("No teams or team members specified.")
            return

        for i in range(num_teams):
            for j in range(num_members):
                player = Player(player_id, i + 1)
                temp_teams.setdefault(i + 1, []).append(player)
                self.players.append(player)
                player_id += 1

        self.players = self.interleave_players(temp_teams)

        for index, player in enumerate(self.players):
            player.order = index + 1

    def interleave_players(self, temp_teams):
        max_team_size = max(len(team) for team in temp_teams.values())
        return [
            player
            for j in range(max_team_size)
            for team_id in sorted(temp_teams.keys())
            if j < len(temp_teams[team_id])
            for player in temp_teams[team_id][j : j + 1]
        ]

    def check_game_end(self, display):
        if self.team_mode == TEAM_MODE_SOLO:
            self.handle_seul_mode(display)
        elif self.team_mode == TEAM_MODE_DUO:
            self.handle_duo_or_team_mode(display, is_team=False)
        elif self.team_mode == TEAM_MODE_TEAM:
            self.handle_duo_or_team_mode(display, is_team=True)
        else:
            logging.error(f"Unknown team mode: {self.team_mode}")

    def handle_seul_mode(self, display):
        remaining_players = [p for p in self.players if not p.won]
        if (len(remaining_players) == 1 and not len(self.players) == 1) or (
            len(self.players) == 1 and self.players[0].won
        ):
            remaining_players[0].rank = self.find_next_available_rank()
            self.game_ended = True
            logging.info("Game ended.")

    def handle_duo_or_team_mode(self, display, is_team):
        groups = self.group_players_by_duo_or_team(is_team)
        remaining_groups = [group for group in groups if not any(p.won for p in group)]

        if len(remaining_groups) == 1:
            next_rank = self.find_next_available_rank()
            for player in remaining_groups[0]:
                player.won = True
                player.rank = next_rank
            self.game_ended = True
            logging.info(
                f"Game ended. {'Team' if is_team else 'Duo'} {remaining_groups[0][0].team} won."
            )

    def group_players_by_duo_or_team(self, is_team):
        return [
            [player for player in self.players if player.team == team_id]
            for team_id in {player.team for player in self.players}
        ]

    def adjust_player_order_after_win(self):
        active_players = sorted(
            [p for p in self.players if not p.won], key=lambda p: p.order
        )
        index = 0
        while index < len(active_players) - 1:
            if active_players[index].team == active_players[index + 1].team:
                for swap_index in range(index + 2, len(active_players)):
                    if active_players[swap_index].team != active_players[index].team:
                        active_players[index + 1], active_players[swap_index] = (
                            active_players[swap_index],
                            active_players[index + 1],
                        )
                        break
                else:
                    break
            index += 1

        for i, player in enumerate(active_players):
            player.order = i + 1

    def find_next_available_rank(self):
        used_ranks = {player.rank for player in self.players if player.rank != 0}
        next_rank = max(used_ranks, default=0) + 1
        return next_rank

    def next_player(self, display):
        if self.current_player.turn_score == 0 and self.penalty:
            points = display.draw_penalty()
            display.draw_holes(self.holes)
            self.current_player.score -= points

        self.current_player = Player.activate_next_player(
            self.current_player, self.players
        )

    def goal(self, pin, display):
        hole = next((hole for hole in self.holes if pin in hole.pin), None)
        if hole is not None:
            points = hole.value
            display.draw_goal_animation(hole, pin)

            if hole.type == "bottle":
                display.animation_bottle()
                self.draw_score = True
            elif hole.type == "little_frog":
                display.animation_little_frog()
                self.draw_game = True
            elif hole.type == "large_frog":
                points = display.animation_large_frog()
                self.draw_game = True
            else:
                self.draw_score = True
            self.current_player.goal(points, self.score)
            next_rank = self.find_next_available_rank()
            if self.team_mode == TEAM_MODE_SOLO:
                if self.current_player.won:
                    self.current_player.rank = next_rank
                    display.draw_player_win(str(self.current_player))
                    self.next_player(display)
                    self.draw_game = True
            else:
                group = [
                    player
                    for player in self.players
                    if player.team == self.current_player.team
                ]

                if sum(player.score for player in group) >= self.score:
                    for player in group:
                        player.won = True
                        player.rank = next_rank
                    next_rank = self.find_next_available_rank()
                    if self.team_mode == TEAM_MODE_DUO:
                        display.draw_player_win(f"Duo {self.current_player.team}")
                    else:
                        display.draw_player_win(f"Team {self.current_player.team}")

                    self.next_player(display)
                    self.adjust_player_order_after_win()
                    self.draw_game = True
        else:
            logging.warning(f"No matching hole found for pin {pin}.")
