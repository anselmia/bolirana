import unittest
import time

from src.constants import (
    ACTION_COOLDOWN,
    CHALLENGE_ALL_HOLES,
    CHALLENGE_ORDER,
    CHALLENGE_TIME_ATTACK,
    MODE_NORMAL,
    OFF,
    PIN_H20,
    PIN_HBOTTLE,
    TEAM_MODE_DUO,
    TEAM_MODE_SOLO,
)
from src.end_menu import EndMenu, OPTION_SENSOR_ANALYSIS
from src.game import Game
from src.game_logic import GameLogic
from src.menu import (
    Menu,
    OPTION_GAME_MODE,
    OPTION_PENALTY,
    OPTION_SCORE,
    OPTION_TIME_ATTACK_SECONDS,
    OPTION_TIME_ATTACK_TURNS,
)
from src.pin import PIN
from src.player import Player


class DummyDisplay:
    def __init__(self, penalty_value=None, roulette_value=120):
        self.penalty_value = penalty_value
        self.roulette_value = roulette_value
        self.holes_drawn = False
        self.winner = None
        self.goal_animation_calls = 0
        self.roulette_animation_calls = 0
        self.bonus_roulette_animation_calls = 0
        self.malus_roulette_animation_calls = 0

    def draw_penalty(self):
        return self.penalty_value

    def draw_holes(self, holes):
        self.holes_drawn = True

    def get_hole_position(self, text, position_index):
        return (100, 100)

    def draw_goal_animation(self, hole, pin):
        self.goal_animation_calls += 1
        return None

    def animation_roulette(self):
        self.roulette_animation_calls += 1
        return self.roulette_value

    def animation_bonus_roulette(self):
        self.bonus_roulette_animation_calls += 1
        return self.roulette_value

    def animation_malus_roulette(self):
        self.malus_roulette_animation_calls += 1
        return self.roulette_value

    def draw_player_win(self, winner):
        self.winner = winner


class RegressionTests(unittest.TestCase):
    def test_player_penalty_can_clear_winner_state(self):
        player = Player(1)
        player.goal(500, 400)
        player.rank = 1

        player.apply_score_delta(-200, 400, reset_rank_on_loss=True)

        self.assertEqual(player.score, 300)
        self.assertFalse(player.won)
        self.assertEqual(player.rank, 0)

    def test_group_players_are_sorted_by_team_id(self):
        logic = GameLogic()
        logic.players = [Player(1, 2), Player(2, 1), Player(3, 2), Player(4, 1)]

        groups = logic.group_players_by_duo_or_team(is_team=False)

        self.assertEqual([group[0].team for group in groups], [1, 2])
        self.assertEqual(
            [[player.id for player in group] for group in groups], [[2, 4], [1, 3]]
        )

    def test_invalid_penalty_value_is_ignored(self):
        logic = GameLogic()
        logic.team_mode = TEAM_MODE_SOLO
        logic.penalty = True
        logic.score = 400
        logic.players = [Player(1), Player(2)]
        for index, player in enumerate(logic.players, start=1):
            player.order = index
        logic.current_player = logic.players[0]
        logic.current_player.activate()

        display = DummyDisplay(penalty_value=None)
        logic.next_player(display)

        self.assertEqual(logic.players[0].score, 0)
        self.assertTrue(display.holes_drawn)
        self.assertIs(logic.current_player, logic.players[1])
        self.assertTrue(logic.players[1].is_active)

    def test_penalty_mode_initializes_side_bonus_and_malus(self):
        logic = GameLogic()
        logic.game_mode = MODE_NORMAL
        logic.penalty = True
        display = DummyDisplay()

        logic.setup_normal_mode(display)
        logic.initialize_side_hole_bonus()

        self.assertIsNotNone(logic.active_side_bonus_hole)
        self.assertIsNotNone(logic.active_side_malus_hole)
        self.assertIsNot(logic.active_side_bonus_hole, logic.active_side_malus_hole)
        self.assertTrue(logic.active_side_bonus_hole.bonus_active)
        self.assertTrue(logic.active_side_malus_hole.malus_active)
        self.assertIn(logic.active_side_bonus_pin, logic.active_side_bonus_hole.pin)
        self.assertEqual(
            logic.active_side_bonus_hole.bonus_active_pin,
            logic.active_side_bonus_pin,
        )
        self.assertIn(logic.active_side_malus_pin, logic.active_side_malus_hole.pin)
        self.assertEqual(
            logic.active_side_malus_hole.malus_active_pin,
            logic.active_side_malus_pin,
        )

    def test_penalty_mode_malus_side_hole_triggers_negative_roulette(self):
        logic = GameLogic()
        logic.game_mode = MODE_NORMAL
        logic.penalty = True
        logic.score = 400
        logic.num_players = 1
        logic.setup_players()
        display = DummyDisplay(roulette_value=130)
        logic.setup_normal_mode(display)
        bonus_hole = logic.holes[0]
        malus_hole = logic.holes[1]
        logic.activate_side_hole_bonus(bonus_hole, notify=False, malus_hole=malus_hole)

        result = logic.goal(malus_hole.pin[0], display)

        self.assertEqual(result["status"], "scored")
        self.assertEqual(result["points"], -130)
        self.assertEqual(logic.current_player.score, -130)
        self.assertEqual(logic.current_player.turn_score, -130)
        self.assertIn("malus", result["detail"].lower())

    def test_side_bonus_roulette_skips_normal_hole_animation(self):
        logic = GameLogic()
        logic.game_mode = MODE_NORMAL
        logic.penalty = False
        logic.score = 400
        logic.num_players = 1
        logic.setup_players()
        display = DummyDisplay(roulette_value=110)
        logic.setup_normal_mode(display)
        bonus_hole = logic.holes[0]
        logic.activate_side_hole_bonus(bonus_hole, notify=False)

        result = logic.goal(bonus_hole.pin[0], display)

        self.assertEqual(result["points"], 110)
        self.assertEqual(display.goal_animation_calls, 0)
        self.assertEqual(display.roulette_animation_calls, 0)
        self.assertEqual(display.bonus_roulette_animation_calls, 1)
        self.assertEqual(display.malus_roulette_animation_calls, 0)

    def test_side_malus_roulette_skips_normal_hole_animation(self):
        logic = GameLogic()
        logic.game_mode = MODE_NORMAL
        logic.penalty = True
        logic.score = 400
        logic.num_players = 1
        logic.setup_players()
        display = DummyDisplay(roulette_value=130)
        logic.setup_normal_mode(display)
        bonus_hole = logic.holes[0]
        malus_hole = logic.holes[1]
        logic.activate_side_hole_bonus(bonus_hole, notify=False, malus_hole=malus_hole)

        result = logic.goal(malus_hole.pin[0], display)

        self.assertEqual(result["points"], -130)
        self.assertEqual(display.goal_animation_calls, 0)
        self.assertEqual(display.roulette_animation_calls, 0)
        self.assertEqual(display.bonus_roulette_animation_calls, 0)
        self.assertEqual(display.malus_roulette_animation_calls, 1)

    def test_bonus_side_special_only_triggers_on_active_pin(self):
        logic = GameLogic()
        logic.game_mode = MODE_NORMAL
        logic.penalty = False
        logic.score = 400
        logic.num_players = 1
        logic.setup_players()
        display = DummyDisplay(roulette_value=110)
        logic.setup_normal_mode(display)
        bonus_hole = logic.holes[0]
        active_pin = bonus_hole.pin[1]
        inactive_pin = bonus_hole.pin[0]
        logic.activate_side_hole_bonus(
            bonus_hole,
            notify=False,
            bonus_pin=active_pin,
        )

        result = logic.goal(inactive_pin, display)

        self.assertEqual(result["points"], bonus_hole.value)
        self.assertEqual(display.goal_animation_calls, 1)
        self.assertEqual(display.bonus_roulette_animation_calls, 0)

    def test_malus_side_special_only_triggers_on_active_pin(self):
        logic = GameLogic()
        logic.game_mode = MODE_NORMAL
        logic.penalty = True
        logic.score = 400
        logic.num_players = 1
        logic.setup_players()
        display = DummyDisplay(roulette_value=130)
        logic.setup_normal_mode(display)
        bonus_hole = logic.holes[0]
        malus_hole = logic.holes[1]
        active_malus_pin = malus_hole.pin[1]
        inactive_malus_pin = malus_hole.pin[0]
        logic.activate_side_hole_bonus(
            bonus_hole,
            notify=False,
            malus_hole=malus_hole,
            bonus_pin=bonus_hole.pin[0],
            malus_pin=active_malus_pin,
        )

        result = logic.goal(inactive_malus_pin, display)

        self.assertEqual(result["points"], malus_hole.value)
        self.assertEqual(logic.current_player.score, malus_hole.value)
        self.assertEqual(display.goal_animation_calls, 1)
        self.assertEqual(display.malus_roulette_animation_calls, 0)

    def test_inactive_game_hole_pins_do_not_consume_shot_lockout(self):
        pin_reader = PIN(None, use_i2c=False)
        pin_reader.set_active_game_hole_pins(PIN_HBOTTLE)

        self.assertIsNone(
            pin_reader._get_next_pin(PIN_H20[0], "game", event_time_ms=1000)
        )
        self.assertEqual(
            pin_reader._get_next_pin(PIN_HBOTTLE[0], "game", event_time_ms=1001),
            PIN_HBOTTLE[0],
        )

    def test_single_player_turn_rotation_finishes_turn(self):
        player = Player(1)
        player.order = 1
        player.activate()
        player.turn_score = 150
        player.turn_hits = 2
        player.little_frog_streak = 1

        next_player = Player.activate_next_player(player, [player])

        self.assertIs(next_player, player)
        self.assertTrue(player.is_active)
        self.assertEqual(player.turns_played, 1)
        self.assertEqual(player.turn_score, 0)
        self.assertEqual(player.turn_hits, 0)
        self.assertEqual(player.little_frog_streak, 0)

    def test_last_remaining_player_is_activated_after_winner_turn(self):
        winner = Player(1)
        winner.order = 1
        winner.won = True
        winner.activate()
        winner.turn_score = 200

        survivor = Player(2)
        survivor.order = 2

        next_player = Player.activate_next_player(winner, [winner, survivor])

        self.assertIs(next_player, survivor)
        self.assertFalse(winner.is_active)
        self.assertEqual(winner.turns_played, 1)
        self.assertTrue(survivor.is_active)

    def test_menu_sound_fallback_is_silent(self):
        menu = Menu()
        menu.frog_sound = None
        menu.play_frog_sound()
        self.assertIsNone(menu.frog_sound)

    def test_end_menu_sound_fallback_is_silent(self):
        end_menu = EndMenu()
        end_menu.frog_sound = None
        end_menu.play_frog_sound()
        self.assertEqual(end_menu.options[0], "Continuer")

    def test_menu_uses_game_mode_as_single_mode_selector(self):
        menu = Menu()
        menu.values[OPTION_GAME_MODE] = CHALLENGE_TIME_ATTACK
        menu.sync_options()

        option_names = [option["name"] for option in menu.options]

        self.assertNotIn("Challenge", option_names)
        self.assertNotIn(OPTION_SCORE, option_names)
        self.assertNotIn(OPTION_PENALTY, option_names)
        self.assertIn(OPTION_TIME_ATTACK_SECONDS, option_names)
        self.assertEqual(menu.get_game_mode(), "NORMAL")
        self.assertEqual(menu.get_challenge_mode(), CHALLENGE_TIME_ATTACK)
        self.assertEqual(menu.get_score(), 0)

    def test_menu_maps_all_holes_mode_to_normal_arena(self):
        menu = Menu()
        menu.values[OPTION_GAME_MODE] = CHALLENGE_ALL_HOLES
        menu.sync_options()

        self.assertEqual(menu.get_game_mode(), "NORMAL")
        self.assertEqual(menu.get_challenge_mode(), CHALLENGE_ALL_HOLES)
        option_names = [option["name"] for option in menu.options]
        self.assertNotIn(OPTION_SCORE, option_names)
        self.assertNotIn(OPTION_PENALTY, option_names)

    def test_numeric_menu_values_wrap_back_to_minimum(self):
        menu = Menu()
        score_option = next(
            option for option in menu.options if option["name"] == OPTION_SCORE
        )
        menu.values[OPTION_SCORE] = score_option["max"]

        menu.cycle_option_value(score_option)

        self.assertEqual(menu.values[OPTION_SCORE], score_option["min"])

    def test_time_attack_turns_are_clamped_to_visible_menu_max(self):
        menu = Menu()
        menu.values[OPTION_TIME_ATTACK_TURNS] = 12

        menu.normalize_values(OPTION_TIME_ATTACK_TURNS)

        self.assertEqual(menu.values[OPTION_TIME_ATTACK_TURNS], 6)

    def test_end_menu_always_exposes_sensor_analysis(self):
        end_menu = EndMenu()
        end_menu.set_context(can_continue=True)
        self.assertIn(OPTION_SENSOR_ANALYSIS, end_menu.options)

        end_menu.set_context(can_continue=False)
        self.assertIn(OPTION_SENSOR_ANALYSIS, end_menu.options)

    def test_all_holes_challenge_counts_unique_holes_only(self):
        logic = GameLogic()
        logic.challenge_mode = CHALLENGE_ALL_HOLES
        logic.num_players = 1
        logic.setup_players()
        display = DummyDisplay()
        logic.setup_normal_mode(display)
        logic.initialize_challenge_state()

        first_hole = logic.holes[0]

        first_result = logic.handle_all_holes_goal(
            first_hole, first_hole.pin[0], display
        )
        duplicate_result = logic.handle_all_holes_goal(
            first_hole, first_hole.pin[0], display
        )

        self.assertEqual(first_result["status"], "scored")
        self.assertEqual(logic.challenge_progress[logic.get_group_key()], 1)
        self.assertEqual(duplicate_result["status"], "blocked")
        self.assertEqual(duplicate_result["reason"], "already_validated")
        self.assertEqual(logic.challenge_progress[logic.get_group_key()], 1)

    def test_order_challenge_ends_when_all_solo_players_are_done(self):
        logic = GameLogic()
        logic.challenge_mode = CHALLENGE_ORDER
        logic.num_players = 2
        logic.setup_players()
        for rank, player in enumerate(logic.players, start=1):
            player.won = True
            player.rank = rank

        logic.check_game_end(DummyDisplay())

        self.assertTrue(logic.game_ended)

    def test_all_holes_challenge_ends_when_all_duo_groups_are_done(self):
        logic = GameLogic()
        logic.challenge_mode = CHALLENGE_ALL_HOLES
        logic.team_mode = TEAM_MODE_DUO
        logic.num_pairs = 2
        logic.setup_players()
        for rank, team_id in enumerate((1, 2), start=1):
            for player in logic.players:
                if player.team == team_id:
                    player.won = True
                    player.rank = rank

        logic.check_game_end(DummyDisplay())

        self.assertTrue(logic.game_ended)

    def test_single_player_end_state_preserves_existing_rank(self):
        logic = GameLogic()
        logic.num_players = 1
        logic.setup_players()
        logic.players[0].won = True
        logic.players[0].rank = 1

        logic.check_game_end(DummyDisplay())

        self.assertTrue(logic.game_ended)
        self.assertEqual(logic.players[0].rank, 1)

    def test_reset_next_action_cooldown_allows_immediate_press(self):
        game = Game.__new__(Game)
        game.last_next_action_time = time.monotonic()

        Game.reset_next_action_cooldown(game)

        self.assertGreaterEqual(
            time.monotonic() - game.last_next_action_time,
            ACTION_COOLDOWN,
        )


if __name__ == "__main__":
    unittest.main()
