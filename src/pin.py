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
from smbus2 import SMBus, i2c_msg

I2C_BUS = 1  # I2C bus number (usually 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the ESP32 (or other I2C device)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PIN:
    def __init__(self):
        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus
        while True:
            try:
                logging.debug("Attempting to send data to I2C slave...")
                write = i2c_msg.write(I2C_ADDRESS, "Hello")
                self.bus.i2c_rdwr(write)
                logging.info("Data sent successfully.")

                # Attempt to read back a response
                read = i2c_msg.read(I2C_ADDRESS, 5)
                self.bus.i2c_rdwr(read)
                response = list(read)

                logging.info(f"Received response: {response}")

                if response:  # If a response is received, break the loop
                    break

            except Exception as e:
                logging.error(f"Failed to send data: {e}")
                logging.info("Retrying...")
                time.sleep(1)  # Wait before retrying

        logging.info("Communication with the I2C slave was successful.")

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
