import logging
import platform
import os
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
)
from src.player import Player
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


class GameLogic:
    def __init__(self):
        logging.info("Initializing GameLogic...")
        self.reset_game()

    def reset_game(self):
        logging.info("Resetting the game...")
        self.num_players = 1
        self.team_mode = "Seul"
        self.game_mode = "Normal"
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
        logging.info("Game restarted.")

    def setup_game(self, display):
        logging.info("Setting up the game...")
        self.setup_players()
        self.penalty = self.penalty == "Avec"
        setup_methods = {
            "Normal": self.setup_normal_mode,
            "Grenouille": self.setup_grenouille_mode,
            "Bouteille": self.setup_bouteille_mode,
        }
        setup_method = setup_methods.get(self.game_mode, None)
        if setup_method:
            setup_method(display)
            logging.info(f"Game mode '{self.game_mode}' setup complete.")
        else:
            logging.error(f"Unknown game mode: {self.game_mode}")
        self.selecting_mode = False

    def setup_normal_mode(self, display):
        logging.info("Setting up normal mode...")
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
        logging.info("Normal mode setup complete.")

    def setup_grenouille_mode(self, display):
        logging.info("Setting up grenouille mode...")
        self.holes = [
            Hole(display, "little_frog", 200, PIN_HSFROG, "200"),
            Hole(display, "large_frog", 0, PIN_HLFROG, "ROUL"),
        ]
        logging.info("Grenouille mode setup complete.")

    def setup_bouteille_mode(self, display):
        logging.info("Setting up bouteille mode...")
        self.holes = [Hole(display, "bottle", 150, PIN_HBOTTLE, "150")]
        logging.info("Bouteille mode setup complete.")

    def setup_players(self):
        logging.info("Setting up players...")
        player_id = 1
        if self.team_mode == "Seul":
            self.players = [Player(player_id + i) for i in range(self.num_players)]
            for i, player in enumerate(self.players):
                player.order = i + 1
        else:
            self.setup_team_players(player_id)

        self.players.sort(key=lambda player: player.id)
        self.current_player = self.players[0] if self.players else None
        if self.current_player:
            self.current_player.activate()
        logging.info(f"{len(self.players)} players set up.")

    def setup_team_players(self, player_id):
        logging.info("Setting up team players...")
        temp_teams = {}
        num_members = 2 if self.team_mode == "Duo" else self.players_per_team
        num_teams = self.num_pairs if self.team_mode == "Duo" else self.num_teams

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

        logging.info("Team players setup complete.")

    def interleave_players(self, temp_teams):
        logging.debug("Interleaving players...")
        max_team_size = max(len(team) for team in temp_teams.values())
        return [
            player
            for j in range(max_team_size)
            for team_id in sorted(temp_teams.keys())
            if j < len(temp_teams[team_id])
            for player in temp_teams[team_id][j : j + 1]
        ]

    def check_game_end(self, display):
        logging.info("Checking if the game has ended...")
        check_methods = {
            "Seul": self.handle_seul_mode,
            "Duo": lambda display: self.handle_duo_or_team_mode(display, is_team=False),
            "Equipe": lambda display: self.handle_duo_or_team_mode(
                display, is_team=True
            ),
        }
        check_method = check_methods.get(self.team_mode, None)
        if check_method:
            check_method(display)
        else:
            logging.error(f"Unknown team mode: {self.team_mode}")

    def handle_seul_mode(self, display):
        logging.debug("Handling 'Seul' mode...")
        remaining_players = [p for p in self.players if not p.won]
        if (len(remaining_players) == 1 and not len(self.players) == 1) or (
            len(self.players) == 1 and self.players[0].score >= self.score
        ):
            remaining_players[0].won = True
            remaining_players[0].rank = self.find_next_available_rank()
            self.game_ended = True
            logging.info(f"Game ended. Player {remaining_players[0].id} won.")
        else:
            self.update_player_status(display)

    def handle_duo_or_team_mode(self, display, is_team):
        mode = "Equipe" if is_team else "Duo"
        logging.debug(f"Handling '{mode}' mode...")
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
        else:
            self.update_group_status(groups, display)

    def group_players_by_duo_or_team(self, is_team):
        return [
            [player for player in self.players if player.team == team_id]
            for team_id in {player.team for player in self.players}
        ]

    def update_player_status(self, display):
        logging.debug("Updating player status...")
        for player in self.players:
            if player.score >= self.score and not player.won:
                player.won = True
                display.draw_player_win(str(player))
                player.rank = self.find_next_available_rank()
                self.next_player(display)
                self.draw_game = True
                logging.info(f"Player {player.id} won their round.")
                break

    def update_group_status(self, groups, display):
        logging.debug("Updating group status...")
        for group in groups:
            if sum(player.score for player in group) >= self.score and not any(
                player.won for player in group
            ):
                next_rank = self.find_next_available_rank()
                team_id = next(player.team for player in group)
                if self.team_mode == "Duo":
                    display.draw_player_win(f"Duo {team_id}")
                else:
                    display.draw_player_win(f"Team {team_id}")
                for player in group:
                    player.won = True
                    player.rank = next_rank

                self.next_player(display)
                self.adjust_player_order_after_win()
                self.draw_game = True
                logging.info(f"Group {team_id} won their round.")
                break

    def adjust_player_order_after_win(self):
        logging.debug("Adjusting player order after win...")
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

        logging.debug("Player order adjusted.")

    def find_next_available_rank(self):
        used_ranks = {player.rank for player in self.players if player.rank != 0}
        next_rank = max(used_ranks, default=0) + 1
        logging.debug(f"Next available rank is {next_rank}.")
        return next_rank

    def next_player(self, display):
        logging.info(
            f"Moving to the next player after {self.current_player.id}'s turn."
        )
        if self.current_player.turn_score == 0 and self.penalty:
            points = display.draw_penalty()
            display.draw_holes(self.holes)
            self.current_player.score -= points
            logging.debug(
                f"Penalty applied to player {self.current_player.id}. Score deducted by {points}."
            )

        self.current_player = Player.activate_next_player(
            self.current_player, self.players
        )
        logging.info(
            f"Next player is {self.current_player.id if self.current_player else 'None'}."
        )

    def goal(self, pin, display):
        logging.info(f"Player {self.current_player.id} scored with pin {pin}.")
        hole = next((hole for hole in self.holes if pin == hole.pin), None)
        if hole is not None:
            points = hole.value
            display.draw_goal_animation(hole)
            logging.debug(f"Points for hole type '{hole.type}': {points}")

            if hole.type == "bottle":
                display.animation_bottle()
                self.current_player.score += points
                self.current_player.turn_score += points
                display.draw_score(
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
            elif hole.type == "little_frog":
                display.animation_little_frog()
                self.current_player.turn_score += points
                self.current_player.score += points
                self.draw_game = True
            elif hole.type == "large_frog":
                points = display.animation_large_frog()
                self.current_player.score += points
                self.current_player.turn_score += points
                self.draw_game = True
            else:
                self.current_player.turn_score += points
                self.current_player.score += points
                display.draw_score(
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
            logging.info(
                f"Player {self.current_player.id} now has a score of {self.current_player.score}."
            )
        else:
            logging.warning(f"No matching hole found for pin {pin}.")
