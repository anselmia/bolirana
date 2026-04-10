import logging
import random
import time

from src.holes import Hole
from src.constants import (
    CHALLENGE_ARCADE,
    CHALLENGE_CLASSIC,
    CHALLENGE_ORDER,
    CHALLENGE_TIME_ATTACK,
    COMBO_BONUS_CAP,
    COMBO_BONUS_STEP,
    DEFAULT_TIME_ATTACK_SECONDS,
    DEFAULT_TIME_ATTACK_TURNS,
    FINAL_RUSH_BONUS,
    FINAL_RUSH_THRESHOLD,
    LOW_TIME_WARNING_SECONDS,
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
    OFF,
    ON,
    ORDER_TARGET_SEQUENCE,
    PRESSURE_BONUS,
    PRESSURE_GAP,
    PRESSURE_TRIGGER_POINTS,
)
from src.player import Player


class GameLogic:
    SIDE_HOLE_BONUS_DURATION = 10.0

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
        self.penalty = OFF
        self.score = 0
        self.holes = []
        self.pin_to_hole = {}
        self.challenge_mode = CHALLENGE_CLASSIC
        self.challenge_progress = {}
        self.time_attack_seconds = DEFAULT_TIME_ATTACK_SECONDS
        self.time_attack_turns = DEFAULT_TIME_ATTACK_TURNS
        self.turn_started_at = 0.0
        self.time_attack_waiting_start = False
        self.status_message = ""
        self.status_message_until = 0.0
        self.active_side_bonus_hole = None
        self.active_side_bonus_started_at = 0.0
        self.active_side_bonus_switch_at = 0.0
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
        self.status_message = ""
        self.status_message_until = 0.0
        self.challenge_progress = {}
        self.time_attack_waiting_start = False
        self.initialize_challenge_state()
        self.initialize_side_hole_bonus()
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
            self.initialize_challenge_state()
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
        self.build_pin_lookup()
        self.initialize_side_hole_bonus()

    def setup_grenouille_mode(self, display):
        self.holes = [
            Hole(display, "little_frog", 200, PIN_HSFROG, "200"),
            Hole(display, "large_frog", 0, PIN_HLFROG, "ROUL"),
        ]
        self.build_pin_lookup()
        self.clear_side_hole_bonus()

    def setup_bouteille_mode(self, display):
        self.holes = [Hole(display, "bottle", 150, PIN_HBOTTLE, "150")]
        self.build_pin_lookup()
        self.clear_side_hole_bonus()

    def build_pin_lookup(self):
        self.pin_to_hole = {pin: hole for hole in self.holes for pin in hole.pin}

    def get_hole_for_pin(self, pin):
        if pin in PIN_HSFROG:
            return next(
                (hole for hole in self.holes if hole.type == "little_frog"),
                self.pin_to_hole.get(pin),
            )
        if pin in PIN_HLFROG:
            return next(
                (hole for hole in self.holes if hole.type == "large_frog"),
                self.pin_to_hole.get(pin),
            )
        return self.pin_to_hole.get(pin)

    def clear_side_hole_bonus(self):
        self.active_side_bonus_hole = None
        self.active_side_bonus_started_at = 0.0
        self.active_side_bonus_switch_at = 0.0
        for hole in self.holes:
            hole.bonus_active = False
            hole.bonus_activated_at = 0.0
            hole.bonus_duration = 0.0

    def supports_side_hole_bonus(self):
        return (
            self.game_mode == MODE_NORMAL
            and not self.is_order_challenge()
            and not self.is_time_attack_challenge()
        )

    def get_bonus_side_holes(self):
        return [hole for hole in self.holes if hole.type == "side"]

    def activate_side_hole_bonus(self, hole, notify=True):
        now = time.monotonic()
        for candidate in self.holes:
            candidate.bonus_active = False
            candidate.bonus_activated_at = 0.0
            candidate.bonus_duration = 0.0

        self.active_side_bonus_hole = hole
        self.active_side_bonus_started_at = now
        self.active_side_bonus_switch_at = now + self.SIDE_HOLE_BONUS_DURATION
        if hole is not None:
            hole.bonus_active = True
            hole.bonus_activated_at = now
            hole.bonus_duration = self.SIDE_HOLE_BONUS_DURATION
            if notify:
                self.set_status_message(
                    f"Bonus roulette sur {hole.text} !",
                    duration=1.8,
                )
        self.draw_game = True

    def initialize_side_hole_bonus(self):
        if not self.supports_side_hole_bonus():
            self.clear_side_hole_bonus()
            return
        candidates = self.get_bonus_side_holes()
        if not candidates:
            self.clear_side_hole_bonus()
            return
        self.activate_side_hole_bonus(random.choice(candidates), notify=False)

    def rotate_side_hole_bonus(self, notify=True, exclude_current=False):
        if not self.supports_side_hole_bonus():
            self.clear_side_hole_bonus()
            return
        candidates = self.get_bonus_side_holes()
        if not candidates:
            self.clear_side_hole_bonus()
            return
        if (
            exclude_current
            and len(candidates) > 1
            and self.active_side_bonus_hole in candidates
        ):
            candidates = [
                hole for hole in candidates if hole is not self.active_side_bonus_hole
            ]
        self.activate_side_hole_bonus(random.choice(candidates), notify=notify)

    def update_side_hole_bonus_runtime(self):
        if self.game_ended:
            return
        if not self.supports_side_hole_bonus():
            if self.active_side_bonus_hole is not None:
                self.clear_side_hole_bonus()
            return
        if self.active_side_bonus_hole is None:
            self.initialize_side_hole_bonus()
            return
        if time.monotonic() >= self.active_side_bonus_switch_at:
            self.rotate_side_hole_bonus(notify=True, exclude_current=True)

    def should_trigger_side_hole_bonus_roulette(self, hole):
        return (
            hole is not None
            and hole.type == "side"
            and hole is self.active_side_bonus_hole
            and self.supports_side_hole_bonus()
        )

    def is_order_challenge(self):
        return self.challenge_mode == CHALLENGE_ORDER

    def is_time_attack_challenge(self):
        return self.challenge_mode == CHALLENGE_TIME_ATTACK

    def get_group_key(self, player=None):
        player = player or self.current_player
        if player is None:
            return None
        if self.team_mode == TEAM_MODE_SOLO:
            return f"player:{player.id}"
        return f"team:{player.team}"

    def get_players_for_group_key(self, group_key):
        if group_key is None:
            return []
        if group_key.startswith("player:"):
            player_id = int(group_key.split(":", 1)[1])
            return [player for player in self.players if player.id == player_id]
        team_id = int(group_key.split(":", 1)[1])
        return [player for player in self.players if player.team == team_id]

    def get_current_group(self):
        if self.current_player is None:
            return []
        return self.get_players_for_group_key(self.get_group_key())

    def initialize_challenge_state(self):
        self.challenge_progress = {}
        if self.is_order_challenge():
            for player in self.players:
                group_key = self.get_group_key(player)
                if group_key not in self.challenge_progress:
                    self.challenge_progress[group_key] = 0
            for player in self.players:
                player.score = 0
                player.sequence_progress = 0
            self.set_status_message(
                f"Cible : {self.get_order_target_label(0)}", duration=3.0
            )
        elif self.is_time_attack_challenge():
            self.arm_time_attack_turn(
                f"Chrono {self.time_attack_seconds}s | appuie sur HAUT pour lancer"
            )

    def arm_time_attack_turn(self, message=None):
        if not self.is_time_attack_challenge() or self.current_player is None:
            return
        self.turn_started_at = 0.0
        self.time_attack_waiting_start = True
        turns_left = self.get_turns_left_for_player()
        prompt = message or (
            f"{self.current_player} | {turns_left} tours restants | appuie sur HAUT pour lancer"
        )
        self.set_status_message(prompt, duration=3600)
        self.draw_game = True

    def start_turn_timer(self):
        if not self.is_time_attack_challenge() or self.current_player is None:
            return False
        if not self.time_attack_waiting_start:
            return False
        self.turn_started_at = time.monotonic()
        self.time_attack_waiting_start = False
        self.set_status_message(
            f"{self.current_player} | Chrono lancé : {self.time_attack_seconds}s",
            duration=1.5,
        )
        self.draw_game = True
        return True

    def get_turn_time_remaining(self):
        if not self.is_time_attack_challenge() or self.current_player is None:
            return None
        if self.time_attack_waiting_start:
            return float(self.time_attack_seconds)
        elapsed = time.monotonic() - self.turn_started_at
        return max(0.0, self.time_attack_seconds - elapsed)

    def can_score_in_time_attack(self):
        return self.is_time_attack_challenge() and not self.time_attack_waiting_start

    def get_turns_left_for_player(self, player=None):
        player = player or self.current_player
        if player is None or not self.is_time_attack_challenge():
            return None
        return max(0, self.time_attack_turns - player.turns_played)

    def get_order_target(self, progress=None, player=None):
        if progress is None:
            group_key = self.get_group_key(player)
            progress = self.challenge_progress.get(group_key, 0)
        if 0 <= progress < len(ORDER_TARGET_SEQUENCE):
            return ORDER_TARGET_SEQUENCE[progress]
        return None

    def get_order_target_label(self, progress=None, player=None):
        target = self.get_order_target(progress=progress, player=player)
        if target is None:
            return "Terminé"
        return target[2]

    def sync_order_progress(self, group_key, progress):
        self.challenge_progress[group_key] = progress
        for player in self.get_players_for_group_key(group_key):
            player.score = progress
            player.sequence_progress = progress

    def register_order_hit(self):
        if self.current_player is None:
            return
        self.current_player.turn_score += 1
        self.current_player.turn_hits += 1
        self.current_player.successful_shots += 1
        self.current_player.max_combo = max(
            self.current_player.max_combo, self.current_player.turn_hits
        )
        self.current_player.best_turn = max(
            self.current_player.best_turn, self.current_player.turn_score
        )

    def get_display_target_score(self):
        if self.is_order_challenge():
            return len(ORDER_TARGET_SEQUENCE)
        if self.is_time_attack_challenge():
            return max(
                self.score,
                self.get_leader_progress_score(),
                self.get_current_progress_score(),
                1,
            )
        return self.score

    def get_challenge_state(self):
        if self.is_order_challenge():
            progress = self.challenge_progress.get(self.get_group_key(), 0)
            labels = [target[2] for target in ORDER_TARGET_SEQUENCE]
            target = self.get_order_target(progress=progress)
            return {
                "type": "order",
                "progress": progress,
                "total": len(ORDER_TARGET_SEQUENCE),
                "next_target": self.get_order_target_label(progress=progress),
                "sequence_labels": labels,
                "target_hole_type": None if target is None else target[0],
                "target_hole_text": None if target is None else target[1],
            }
        if self.is_time_attack_challenge():
            remaining = self.get_turn_time_remaining()
            return {
                "type": "time_attack",
                "remaining_seconds": remaining,
                "turn_duration": self.time_attack_seconds,
                "turns_left": self.get_turns_left_for_player(),
                "max_turns": self.time_attack_turns,
                "awaiting_start": self.time_attack_waiting_start,
                "low_time": remaining is not None
                and not self.time_attack_waiting_start
                and remaining <= LOW_TIME_WARNING_SECONDS,
            }
        return None

    def update_challenge_runtime(self, display):
        self.update_side_hole_bonus_runtime()
        if not self.is_time_attack_challenge() or self.game_ended:
            return
        if self.time_attack_waiting_start:
            return
        self.draw_game = True
        remaining = self.get_turn_time_remaining()
        if remaining is not None and remaining <= 0:
            self.set_status_message("Temps écoulé !", duration=1.2)
            self.next_player(display)

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

    def set_status_message(self, message, duration=2.5):
        self.status_message = message
        self.status_message_until = time.monotonic() + duration

    def get_status_message(self):
        if time.monotonic() <= self.status_message_until:
            return self.status_message
        return ""

    def get_current_progress_score(self):
        if self.is_order_challenge():
            return self.challenge_progress.get(self.get_group_key(), 0)
        return sum(player.score for player in self.get_current_group())

    def get_leader_progress_score(self):
        if not self.players:
            return 0
        if self.is_order_challenge():
            return max(self.challenge_progress.values(), default=0)
        if self.team_mode == TEAM_MODE_SOLO:
            return max(player.score for player in self.players)

        groups = self.group_players_by_duo_or_team(self.team_mode == TEAM_MODE_TEAM)
        return max(sum(player.score for player in group) for group in groups)

    def is_final_rush(self):
        return self.score > 0 and self.get_leader_progress_score() >= int(
            self.score * FINAL_RUSH_THRESHOLD
        )

    def calculate_arcade_bonus(self, player, hole, base_points):
        bonuses = []
        total_bonus = 0

        combo_bonus = min(player.turn_hits * COMBO_BONUS_STEP, COMBO_BONUS_CAP)
        if combo_bonus:
            bonuses.append(f"Combo +{combo_bonus}")
            total_bonus += combo_bonus

        leader_progress = self.get_leader_progress_score()
        current_progress = self.get_current_progress_score()
        if (
            leader_progress - current_progress >= PRESSURE_GAP
            and base_points >= PRESSURE_TRIGGER_POINTS
        ):
            bonuses.append(f"Pression +{PRESSURE_BONUS}")
            total_bonus += PRESSURE_BONUS

        if self.is_final_rush() and hole.type in {
            "bottle",
            "little_frog",
            "large_frog",
        }:
            bonuses.append(f"Final rush +{FINAL_RUSH_BONUS}")
            total_bonus += FINAL_RUSH_BONUS

        return total_bonus, bonuses

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
        if self.is_time_attack_challenge():
            if all(
                player.turns_played >= self.time_attack_turns for player in self.players
            ):
                self.finalize_time_attack_game()
            return
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
        if len(self.players) == 1 and self.players[0].won:
            self.players[0].rank = self.find_next_available_rank()
            self.game_ended = True
            logging.info("Game ended.")
        elif len(remaining_players) == 1 and len(self.players) != 1:
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

    def finalize_time_attack_game(self):
        if self.game_ended:
            return

        if self.team_mode == TEAM_MODE_SOLO:
            ranked_players = sorted(
                self.players,
                key=lambda player: (-player.score, -player.best_turn, player.id),
            )
            for rank, player in enumerate(ranked_players, start=1):
                player.rank = rank
                player.won = True
        else:
            ranked_groups = sorted(
                self.group_players_by_duo_or_team(self.team_mode == TEAM_MODE_TEAM),
                key=lambda group: (
                    -sum(player.score for player in group),
                    -max(player.best_turn for player in group),
                    group[0].team,
                ),
            )
            for rank, group in enumerate(ranked_groups, start=1):
                for player in group:
                    player.rank = rank
                    player.won = True

        self.game_ended = True
        self.draw_game = True
        self.set_status_message("Fin du chrono !", duration=2.0)

    def activate_next_time_attack_player(self):
        if self.current_player is None:
            return

        finished_player = self.current_player
        finished_player.finish_turn()
        finished_player.deactivate()

        eligible_players = sorted(
            [
                player
                for player in self.players
                if player.turns_played < self.time_attack_turns
            ],
            key=lambda player: player.order,
        )
        if not eligible_players:
            self.finalize_time_attack_game()
            return

        self.current_player = next(
            (
                player
                for player in eligible_players
                if player.order > finished_player.order
            ),
            eligible_players[0],
        )
        self.current_player.activate()
        self.arm_time_attack_turn()

    def should_trigger_little_frog_roulette(self, hole):
        return (
            self.current_player is not None
            and hole.type == "little_frog"
            and self.current_player.little_frog_streak >= 1
        )

    def update_little_frog_streak(self, hole, triggered_roulette=False):
        if self.current_player is None:
            return
        if hole.type != "little_frog":
            self.current_player.little_frog_streak = 0
            return
        if triggered_roulette:
            self.current_player.little_frog_streak = 0
            return
        self.current_player.little_frog_streak += 1

    def run_hole_animation(self, hole, pin, display, force_roulette=False):
        points = hole.value
        display.draw_goal_animation(hole, pin)

        if hole.type == "bottle":
            display.animation_bottle()
        elif hole.type == "little_frog":
            display.animation_little_frog()
        elif hole.type == "large_frog":
            points = display.animation_large_frog()

        if force_roulette and hole.type != "large_frog":
            points = display.animation_roulette()

        self.draw_game = True
        return points

    def resolve_sequence_win(self, display, group_key):
        winning_group = self.get_players_for_group_key(group_key)
        next_rank = self.find_next_available_rank()
        for player in winning_group:
            player.won = True
            player.rank = next_rank

        if self.team_mode == TEAM_MODE_SOLO:
            display.draw_player_win(str(winning_group[0]))
        elif self.team_mode == TEAM_MODE_DUO:
            display.draw_player_win(f"Duo {winning_group[0].team}")
        else:
            display.draw_player_win(f"Team {winning_group[0].team}")

        self.next_player(display)
        if self.team_mode != TEAM_MODE_SOLO:
            self.adjust_player_order_after_win()

    def handle_order_goal(self, hole, pin, display):
        group_key = self.get_group_key()
        progress = self.challenge_progress.get(group_key, 0)
        target = self.get_order_target(progress=progress)
        if target is None:
            self.set_status_message("Séquence terminée !", duration=1.5)
            return

        expected_type, expected_text, expected_label = target
        if hole.type != expected_type or hole.text != expected_text:
            self.set_status_message(f"Cible actuelle : {expected_label}", duration=1.7)
            self.draw_game = True
            return

        self.run_hole_animation(hole, pin, display)
        self.register_order_hit()
        progress += 1
        self.sync_order_progress(group_key, progress)

        if progress >= len(ORDER_TARGET_SEQUENCE):
            self.set_status_message("Séquence complète !", duration=2.0)
            self.resolve_sequence_win(display, group_key)
            return

        self.set_status_message(
            f"Validé : {expected_label} | Prochaine cible : {self.get_order_target_label(progress=progress)}",
            duration=2.2,
        )

    def apply_points_to_current_player(self, points, win_threshold):
        if self.current_player is None:
            return
        self.current_player.goal(points, win_threshold)

    def handle_standard_goal_result(self, display, points, status_message):
        if self.current_player is None:
            return
        self.set_status_message(status_message)

        next_rank = self.find_next_available_rank()
        if self.team_mode == TEAM_MODE_SOLO:
            if self.current_player.won:
                self.current_player.rank = next_rank
                display.draw_player_win(str(self.current_player))
                self.next_player(display)
                self.draw_game = True
            return

        group = self.get_current_group()
        if sum(player.score for player in group) >= self.score:
            for player in group:
                player.won = True
                player.rank = next_rank
            if self.team_mode == TEAM_MODE_DUO:
                display.draw_player_win(f"Duo {self.current_player.team}")
            else:
                display.draw_player_win(f"Team {self.current_player.team}")

            self.next_player(display)
            self.adjust_player_order_after_win()
            self.draw_game = True

    def next_player(self, display):
        if self.current_player is None:
            return

        if self.current_player.turn_score == 0 and self.penalty:
            points = display.draw_penalty()
            display.draw_holes(self.holes)
            self.current_player.score -= points
            self.set_status_message(f"Pénalité -{points}")

        if self.is_time_attack_challenge():
            self.activate_next_time_attack_player()
        else:
            self.current_player = Player.activate_next_player(
                self.current_player, self.players
            )
        self.draw_game = True

    def goal(self, pin, display):
        if self.current_player is None:
            return

        if self.is_time_attack_challenge() and not self.can_score_in_time_attack():
            self.set_status_message(
                f"{self.current_player} | appuie sur HAUT pour lancer le chrono",
                duration=1.6,
            )
            self.draw_game = True
            return

        hole = self.get_hole_for_pin(pin)
        if hole is not None:
            if self.is_order_challenge():
                self.handle_order_goal(hole, pin, display)
                return

            triggered_little_frog_roulette = self.should_trigger_little_frog_roulette(
                hole
            )
            triggered_side_hole_bonus_roulette = (
                self.should_trigger_side_hole_bonus_roulette(hole)
            )
            points = self.run_hole_animation(
                hole,
                pin,
                display,
                force_roulette=(
                    triggered_little_frog_roulette or triggered_side_hole_bonus_roulette
                ),
            )
            self.update_little_frog_streak(
                hole,
                triggered_roulette=triggered_little_frog_roulette,
            )
            if triggered_side_hole_bonus_roulette:
                self.rotate_side_hole_bonus(notify=True, exclude_current=True)

            bonus_points = 0
            bonus_messages = []
            if self.challenge_mode == CHALLENGE_ARCADE:
                bonus_points, bonus_messages = self.calculate_arcade_bonus(
                    self.current_player,
                    hole,
                    points,
                )
                points += bonus_points

            win_threshold = (
                float("inf") if self.is_time_attack_challenge() else self.score
            )
            self.apply_points_to_current_player(points, win_threshold)
            status_message = f"{self.current_player} +{points}"
            if triggered_little_frog_roulette:
                status_message = (
                    f"{self.current_player} petite grenouille x2 -> roulette +{points}"
                )
            elif triggered_side_hole_bonus_roulette:
                status_message = (
                    f"{self.current_player} bonus {hole.text} -> roulette +{points}"
                )
            if bonus_messages:
                status_message = " | ".join([status_message] + bonus_messages)

            if self.is_time_attack_challenge():
                if triggered_little_frog_roulette:
                    status_message = (
                        f"{self.current_player} petite grenouille x2 -> roulette +{points}"
                        f" | {self.get_turns_left_for_player()} tours"
                    )
                elif triggered_side_hole_bonus_roulette:
                    status_message = (
                        f"{self.current_player} bonus {hole.text} -> roulette +{points}"
                        f" | {self.get_turns_left_for_player()} tours"
                    )
                else:
                    status_message = (
                        f"{self.current_player} +{points}"
                        f" | {self.get_turns_left_for_player()} tours"
                    )
                if bonus_messages:
                    status_message = " | ".join([status_message] + bonus_messages)
                self.set_status_message(status_message)
                return

            self.handle_standard_goal_result(display, points, status_message)
        else:
            logging.warning(f"No matching hole found for pin {pin}.")
