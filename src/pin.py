from src.constants import (
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
import time
import logging
from smbus2 import SMBus

I2C_BUS = 1  # I2C bus number (usually 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the ESP32 (or other I2C device)


class PIN:
    def __init__(self):
        self.pin_states = {}
        self.last_read_time = time.time()
        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus

    def read_pin_states(self, game_action):
        try:
            # Read 16 bytes from the I2C device (adjust the number of bytes based on your needs)
            raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 16)
            # Convert the raw data to pin states
            self.pin_states = self._parse_i2c_data(raw_data)
            logging.debug(f"Pin states read: {self.pin_states}")
        except Exception as e:
            logging.error(f"Failed to read from I2C bus: {e}")
            self.pin_states = {}

        return self._get_next_pin(game_action)

    def _parse_i2c_data(self, data):
        # Convert the raw I2C data into a dictionary of pin states
        # Assuming each pin state is represented by a single byte: 0x00 = LOW, 0x01 = HIGH
        # The order and structure of the data depend on how the slave device sends it
        pin_states = {}
        for i, value in enumerate(data):
            pin_states[i] = "LOW" if value == 0 else "HIGH"
        return pin_states

    def _reset_pin_states(self):
        # Reset pin states by sending a reset command to the I2C device if necessary
        # For simplicity, we assume the I2C slave automatically resets its states after each read.
        logging.debug(f"Pin states reset to HIGH: {self.pin_states}")

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
