from src.holes import Hole
from src.constants import (
    HOLE_RADIUS,
    PIN_H20,
    PIN_H25,
    PIN_H40,
    PIN_H50,
    PIN_H100,
    PIN_HBOTTLE,
    PIN_HSFROG,
    PIN_HLFROG,
)
from src.player import Player


class GameLogic:
    def __init__(self):
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
        self.score = 0
        self.holes = []
        self.draw_game = True

    def reset_game(self):
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
        self.score = 0
        self.holes = []
        self.draw_game = True

    def setup_game(self, display):
        self.setup_players()
        self.penalty = self.penalty == "Avec"

        if self.game_mode == "Normal":
            self.setup_normal_mode(display)
        elif self.game_mode == "Grenouille":
            self.setup_grenouille_mode(display)
        elif self.game_mode == "Bouteille":
            self.setup_bouteille_mode(display)

        self.selecting_mode = False

    def setup_normal_mode(self, display):
        self.holes.extend(
            [
                Hole(
                    display,
                    "side",
                    20,
                    PIN_H20,
                    "20",
                ),
                Hole(
                    display,
                    "side",
                    25,
                    PIN_H25,
                    "25",
                ),
                Hole(
                    display,
                    "side",
                    40,
                    PIN_H40,
                    "40",
                ),
                Hole(
                    display,
                    "side",
                    50,
                    PIN_H50,
                    "50",
                ),
                Hole(
                    display,
                    "side",
                    100,
                    PIN_H100,
                    "100",
                ),
                Hole(
                    display,
                    "bottle",
                    150,
                    PIN_HBOTTLE,
                    "150",
                ),
                Hole(
                    display,
                    "little_frog",
                    200,
                    PIN_HSFROG,
                    "200",
                ),
                Hole(
                    display,
                    "large_frog",
                    0,
                    PIN_HLFROG,
                    "ROUL",
                ),
            ]
        )

    def setup_grenouille_mode(self, display):
        self.holes.extend(
            [
                Hole(
                    display,
                    "little_frog",
                    200,
                    PIN_HSFROG,
                    "200",
                ),
                Hole(
                    display,
                    "large_frog",
                    0,
                    PIN_HLFROG,
                    "ROUL",
                ),
            ]
        )

    def setup_bouteille_mode(self, display):
        self.holes.append(
            Hole(
                display,
                "bottle",
                150,
                PIN_HBOTTLE,
                "150",
            )
        )

    def setup_players(self):
        player_id = 1
        temp_teams = {}

        if self.team_mode == "Seul":
            for _ in range(self.num_players):
                self.players.append(Player(player_id))
                player_id += 1
        else:
            num_members = 2 if self.team_mode == "Duo" else self.players_per_team
            num_teams = self.num_pairs if self.team_mode == "Duo" else self.num_teams

            if num_teams == 0 or num_members == 0:
                print("Error: No teams or team members specified.")
                return

            for i in range(num_teams):
                for j in range(num_members):
                    player = Player(player_id, i + 1)
                    temp_teams.setdefault(i + 1, []).append(player)
                    self.players.append(player)
                    player_id += 1

        if temp_teams:
            self.players = self.interleave_players(temp_teams)

        for index, player in enumerate(self.players):
            player.order = index + 1

        self.players.sort(key=lambda player: player.id)
        self.current_player = self.players[0] if self.players else None
        if self.current_player:
            self.current_player.activate()

    def interleave_players(self, temp_teams):
        interleaved_players = []
        max_team_size = max(len(team) for team in temp_teams.values())

        for j in range(max_team_size):
            for team_id in sorted(temp_teams.keys()):
                if j < len(temp_teams[team_id]):
                    interleaved_players.append(temp_teams[team_id][j])

        return interleaved_players

    def check_game_end(self, display):
        if self.team_mode == "Seul":
            self.handle_seul_mode(display)
        elif self.team_mode == "Duo":
            self.handle_duo_or_team_mode(display, is_team=False)
        elif self.team_mode == "Equipe":
            self.handle_duo_or_team_mode(display, is_team=True)

    def handle_seul_mode(self, display):
        remaining_players = [p for p in self.players if not p.won]
        if len(remaining_players) == 1:
            if len(self.players) == 1:
                if remaining_players[0].score >= self.score:
                    remaining_players[0].won = True
                    remaining_players[0].rank = self.find_next_available_rank()
                    self.game_ended = True
            else:
                remaining_players[0].won = True
                remaining_players[0].rank = self.find_next_available_rank()
                self.game_ended = True
        else:
            self.update_player_status(display)

    def handle_duo_or_team_mode(self, display, is_team):
        groups = self.group_players_by_duo_or_team(is_team)
        remaining_groups = [group for group in groups if not any(p.won for p in group)]

        if len(remaining_groups) == 1:
            next_rank = self.find_next_available_rank()
            for player in remaining_groups[0]:
                player.won = True
                player.rank = next_rank
            self.game_ended = True
        else:
            self.update_group_status(groups, display)

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

    def update_player_status(self, display):
        for player in self.players:
            if player.score >= self.score and not player.won:
                player.won = True
                player.rank = self.find_next_available_rank()
                self.next_player(display)
                self.draw_game = True

    def update_group_status(self, groups, display):
        for group in groups:
            if sum(player.score for player in group) >= self.score and not any(
                player.won for player in group
            ):
                next_rank = self.find_next_available_rank()
                for player in group:
                    player.won = True
                    player.rank = next_rank

                self.next_player(display)
                self.adjust_player_order_after_win()
                self.draw_game = True

    def adjust_player_order_after_win(self):
        active_players = [p for p in self.players if not p.won]
        if len(active_players) <= 1:
            return

        active_players.sort(key=lambda p: p.order)
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
        used_ranks = set(player.rank for player in self.players if player.rank != 0)
        return max(used_ranks, default=0) + 1 if used_ranks else 1

    def next_player(self, display):
        if self.current_player.turn_score == 0 and self.penalty:
            points = display.draw_penalty()
            self.current_player.score -= points

        self.current_player = Player.activate_next_player(
            self.current_player, self.players
        )

    def goal(self, pin, display):
        hole = next((hole for hole in self.holes if pin == hole.pin), None)
        points = 0
        if hole is not None:
            points = hole.value
            display.draw_goal_animation(hole)
            if hole.type == "bottle":
                display.animation_bottle()
            if hole.type == "little_frog":
                display.animation_little_frog()
            if hole.type == "large_frog":
                points = display.animation_large_frog()

        self.current_player.score += points
        self.current_player.turn_score += points
