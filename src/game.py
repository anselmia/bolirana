import logging
import time
from typing import cast

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
from src.end_menu import EndMenu, OPTION_SENSOR_ANALYSIS
from src.display import Display
from src.game_logic import GameLogic


class Game:
    MAX_PIN_EVENTS_PER_FRAME = 8

    def __init__(self, debug=False, keyboard_mode=False):
        self.keyboard_mode = keyboard_mode
        self.debug = debug
        self.display: Display = cast(Display, None)
        self.menu: Menu = cast(Menu, None)
        self.end_menu: EndMenu = cast(EndMenu, None)
        self.pin: PIN = cast(PIN, None)
        self.gamelogic: GameLogic = cast(GameLogic, None)
        self.last_next_action_time = 0.0
        self.in_end_menu = False
        self.menu_screen = "menu"
        self.sensor_analysis_page = 0
        self.running = True
        self.clock = pygame.time.Clock()
        self._cleaned_up = False

        try:
            # Initialize only required subsystems — pygame.init() scans joysticks
            # and takes 20-25 seconds on Raspberry Pi when no joystick is connected.
            # Note: SDL_VIDEODRIVER=x11 is required — Wayland+EGL init takes 25s+ on Pi.
            t0 = time.monotonic()
            pygame.display.init()
            pygame.font.init()

            # Create the window ONCE here and pass it to Display.
            # Calling set_mode() a second time inside Display.__init__ triggers a full
            # Wayland surface renegotiation (~87s). Passing the screen avoids that.
            pygame.display.set_caption("Bolirana Game")
            flags = pygame.HWSURFACE | pygame.DOUBLEBUF
            screen = pygame.display.set_mode(
                (1024, 768) if debug else (0, 0),
                flags if debug else flags | pygame.FULLSCREEN,
            )

            # Show loading screen immediately before mixer init
            _h = screen.get_height()
            _font = pygame.font.SysFont(None, max(32, _h // 20))
            _text = _font.render("Chargement...", True, (200, 200, 200))
            screen.fill((10, 10, 10))
            screen.blit(
                _text,
                _text.get_rect(center=(screen.get_width() // 2, _h // 2)),
            )
            pygame.display.flip()
            del _font, _text

            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            try:
                pygame.mixer.init()
            except Exception as error:
                logging.warning("Audio disabled: %s", error)

            self.display = Display(debug, screen=screen)
            self.menu = Menu()
            self.end_menu = EndMenu()
            self.pin = PIN(self.display.screen, use_i2c=not keyboard_mode)
            self.gamelogic = GameLogic()
            self.gamelogic.reset_game()
            self.reset_next_action_cooldown()
            logging.warning(f"Game ready in {time.monotonic()-t0:.2f}s")
        except Exception:
            self.cleanup()
            raise

    def reset_next_action_cooldown(self):
        self.last_next_action_time = time.monotonic() - ACTION_COOLDOWN

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
            action = self.process_events(self.menu_screen)
            if action == "open_sensor_analysis":
                self.menu_screen = "sensor_analysis"
                self.sensor_analysis_page = 0
                self.pin.reset_diagnostics()
                continue
            if action == "close_sensor_analysis":
                self.menu_screen = "menu"
                continue

            if self.menu_screen == "sensor_analysis":
                snapshot = self.pin.get_diagnostics_snapshot()
                self.display.draw_sensor_analysis(
                    snapshot,
                    page_index=self.sensor_analysis_page,
                )
            else:
                self.display.draw_menu(self.menu)
                if not self.pin.is_connected():
                    self.display.draw_i2c_connecting()
            self.clock.tick(FPS)

    def reset_to_menu(self):
        self.menu = Menu()
        self.end_menu = EndMenu()
        self.gamelogic.reset_game()
        self.pin.set_active_game_hole_pins(self.pin.pin_hole)
        self.reset_next_action_cooldown()
        self.in_end_menu = False
        self.menu_screen = "menu"
        self.sensor_analysis_page = 0

    def process_events(self, mode):
        keyboard_enabled = self.debug or self.keyboard_mode
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup()
                return "quit"
            if event.type == pygame.KEYDOWN and keyboard_enabled:
                if event.key == pygame.K_ESCAPE:
                    if mode == "menu":
                        self.cleanup()
                        return "quit"
                    if mode == "game":
                        return "open_end_menu"
                if event.key in KEY_TO_PIN_MAP:
                    pin = KEY_TO_PIN_MAP[event.key]
                    if mode == "sensor_analysis":
                        self.pin.record_manual_pin(pin, game_action=mode)
                    action = self.handle_event(mode, pin)
                    if action is not None:
                        return action

        for _ in range(self.MAX_PIN_EVENTS_PER_FRAME):
            pin = self.pin.read_pin_states(mode)
            if pin is None:
                break
            action = self.handle_event(mode, pin)
            if action is not None:
                return action

        return None

    def handle_event(self, mode, pin):
        if mode == "menu" and pin in PIN_TO_ACTION_MAP:
            action = PIN_TO_ACTION_MAP[pin]
            if action in [ACTION_NEXT, ACTION_RIGHT]:
                self.menu.handle_button_press(action)
            else:
                if self.menu.is_sensor_analysis_selected():
                    return "open_sensor_analysis"
                self.setup_game_from_menu()
                self.gamelogic.selecting_mode = False
        elif mode == "game":
            return self.handle_game_event(pin)
        elif mode == "sensor_analysis":
            return self.handle_sensor_analysis_event(pin)
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
            score_result = self.gamelogic.goal(pin, self.display)
            self.pin.record_game_score_event(score_result)

        return None

    def handle_sensor_analysis_event(self, pin):
        if pin == PIN_BENTER:
            return "close_sensor_analysis"
        if pin == PIN_BNEXT:
            self.sensor_analysis_page = (self.sensor_analysis_page + 1) % 4
            return None
        if pin == PIN_RIGHT:
            self.pin.reset_diagnostics()
            return None
        if pin in self.pin.pin_hole:
            score_result = self.gamelogic.preview_goal_result(pin, self.display)
            self.pin.record_game_score_event(score_result)
        return None

    def execute_end_menu_option(self):
        option = self.end_menu.options[self.end_menu.selected_option]

        if option == "Continuer":
            return "continue"
        if option == "Nouveau":
            return "new_game"
        if option == "Recommencer":
            return "restart"
        if option == OPTION_SENSOR_ANALYSIS:
            return "open_sensor_analysis"
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
        self.pin.set_active_game_hole_pins(self.gamelogic.pin_to_hole.keys())
        self.reset_next_action_cooldown()
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
                        self.reset_next_action_cooldown()
                        continue
                    else:
                        return menu_action

                if not self.running:
                    return "quit"

                self.gamelogic.update_challenge_runtime(self.display)
                self.gamelogic.check_game_end(self.display)
                # Keep the HUD animating even when gameplay state is idle.
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
                self.reset_next_action_cooldown()
                self.display.play_intro()
                continue
            return menu_action

        return "quit"

    def enter_end_menu(self, can_continue):
        self.end_menu.set_context(can_continue)
        self.in_end_menu = True
        current_screen = "end_menu"
        while self.running and self.in_end_menu:
            if current_screen == "sensor_analysis":
                snapshot = self.pin.get_diagnostics_snapshot()
                self.display.draw_sensor_analysis(
                    snapshot,
                    page_index=self.sensor_analysis_page,
                )
                action = self.process_events("sensor_analysis")
            else:
                self.display.draw_end_menu(self.end_menu)
                action = self.process_events("end_menu")

            if (
                current_screen == "sensor_analysis"
                and action == "close_sensor_analysis"
            ):
                current_screen = "end_menu"
                continue
            if current_screen == "end_menu" and action == "open_sensor_analysis":
                current_screen = "sensor_analysis"
                self.sensor_analysis_page = 0
                self.pin.reset_diagnostics()
                continue
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

        status_text = self.gamelogic.get_status_message()
        if self.keyboard_mode and not status_text:
            status_text = "TEST MODE  |  Left/Down: next  |  Right/Up: action  |  Enter/Space: menu/select  |  1-8 or Q-N: score"

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
            status_text,
            challenge_state=self.gamelogic.get_challenge_state(),
        )

    def cleanup(self):
        if self._cleaned_up:
            return

        logging.info("Cleaning up and shutting down the game.")
        self._cleaned_up = True
        self.running = False
        if self.pin is not None:
            self.pin.stop()
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit()
        pygame.quit()
