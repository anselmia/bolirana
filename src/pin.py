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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PIN:
    def __init__(self):
        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus

    def read_pin_states(self, game_action):
        try:
            # Request data from the ESP32, assuming 16 bytes are needed
            raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
            # Parse the received data into pin states
            pin = self._parse_i2c_data(raw_data, game_action)
            return pin
        except Exception as e:
            logging.error(f"Failed to read from I2C bus: {e}")
            self.pin_states = {}
            return None

    def _parse_i2c_data(self, data, game_action):
        # Convert the raw I2C data into a dictionary of pin states
        pin_number = data[0]
        if pin_number == 0xFF:
            return None  # Neutral signal, nothing to process

        state = "LOW" if data[1] == 0 else "HIGH"
        if state == "HIGH":
            return self._get_next_pin(pin_number, game_action)
        return None

    def _get_next_pin(self, pin, game_action):
        if game_action == "menu" and int(pin) in {
            PIN_BENTER,
            PIN_DOWN,
            PIN_UP,
            PIN_LEFT,
            PIN_RIGHT,
        }:
            logging.info(f"Pin {pin} state changed to High")  # Log the pin change
            return int(pin)
        elif game_action == "game" and int(pin) in {
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
        }:
            self._reset_pin_states()  # Reset pin states to LOW
            logging.info(f"Pin {pin} state changed to High")  # Log the pin change
            return int(pin)
        return None
