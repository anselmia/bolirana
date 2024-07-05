from src.holes import Hole
from src.constants import *
from src.player import Player


class GameLogic:
    def __init__(self):
        pass

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

    def setup_game(self, screen_width):
        self.setup_players()
        if self.penalty == "Avec":
            self.penalty = True
        else:
            self.penalty = False

        if self.game_mode == "Normal":
            self.holes.append(
                Hole(
                    "side",
                    20,
                    PIN_H20,
                    "20",
                    (
                        (screen_width / 3 + 20) + HOLE_RADIUS,
                        255,
                    ),
                    (
                        (screen_width / 3 + 20) + HOLE_RADIUS + 240,
                        255,
                    ),
                ),
            )
            self.holes.append(
                Hole(
                    "side",
                    25,
                    PIN_H25,
                    "25",
                    ((screen_width / 3 + 20) + HOLE_RADIUS, 150),
                    (
                        screen_width / 3 + 20 + HOLE_RADIUS + 240,
                        155,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS + 60,
                        205,
                    ),
                    (
                        (screen_width / 3 + 20) + HOLE_RADIUS + 180,
                        205,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS + 60,
                        105,
                    ),
                    (
                        (screen_width / 3 + 20) + HOLE_RADIUS + 180,
                        105,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS + 60,
                        305,
                    ),
                    (
                        (screen_width / 3 + 20) + HOLE_RADIUS + 180,
                        305,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS,
                        55,
                    ),
                    (
                        (screen_width / 3 + 20) + HOLE_RADIUS + 240,
                        55,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS + 120,
                        155,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS + 120,
                        55,
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
                        (screen_width / 3 +20) + HOLE_RADIUS + 120,
                        155,
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
                        (screen_width / 3 + 20) + HOLE_RADIUS + 120,
                        55,
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
                    (screen_width / 3 + 20) + HOLE_RADIUS,
                    55,
                ),
                (
                    (screen_width / 3 + 20) + HOLE_RADIUS + 240,
                    55,
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
                # If only one player in the game, they automatically win when they reach the game score
                if remaining_players[0].score >= self.score:
                    remaining_players[0].won = True
                    remaining_players[0].rank = self.find_next_available_rank()
                    self.game_ended = True
            else:
                # Last remaining player automatically wins if they haven't already
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
            # Last remaining group automatically wins
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
