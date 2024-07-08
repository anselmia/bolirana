from src.constants import (
    PIN_STATES_FILE,
    PIN_BENTER,
    PIN_BNEXT,
    PIN_DOWN,
    PIN_UP,
    PIN_LEFT,
    PIN_RIGHT,
    PIN_H20,
    PIN_H25,
    PIN_H40,
    PIN_H50,
    PIN_H100,
    PIN_HBOTTLE,
    PIN_HSFROG,
    PIN_HLFROG,
)
import json
import time
import logging


class PIN:
    def __init__(self):
        self.pin_states = {}
        self.last_read_time = time.time()

    def read_pin_states(self, game_action):
        try:
            with open(PIN_STATES_FILE, "r") as file:
                self.pin_states = json.load(file)
            logging.debug(f"Pin states read: {self.pin_states}")
        except (json.JSONDecodeError, FileNotFoundError):
            self.pin_states = {}

        return self._get_next_pin(game_action)

    def _reset_pin_states(self):
        for pin in self.pin_states:
            self.pin_states[pin] = "LOW"
        with open(PIN_STATES_FILE, "w") as file:
            json.dump(self.pin_states, file)
        logging.debug(f"Pin states reset to LOW: {self.pin_states}")

    def _get_next_pin(self, game_action):
        current_time = time.time()
        if current_time - self.last_read_time < 0.3:
            return None  # Ignore if less than 0.3 seconds have passed

        for pin, state in self.pin_states.items():
            if (
                game_action == "menu"
                and int(pin) in {PIN_BENTER, PIN_DOWN, PIN_UP, PIN_LEFT, PIN_RIGHT}
                and state == "LOW"
            ):
                self.last_read_time = current_time  # Update the last read time
                self._reset_pin_states()  # Reset pin states to LOW
                return int(pin)
            elif (
                game_action == "game"
                and int(pin)
                in {
                    PIN_BNEXT,
                    PIN_BENTER,
                    PIN_H20,
                    PIN_H25,
                    PIN_H40,
                    PIN_H50,
                    PIN_H100,
                    PIN_HBOTTLE,
                    PIN_HSFROG,
                    PIN_HLFROG,
                }
                and state == "LOW"
            ):
                self.last_read_time = current_time  # Update the last read time
                self._reset_pin_states()  # Reset pin states to LOW
                return int(pin)
        return None
