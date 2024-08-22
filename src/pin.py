import logging
from logging.handlers import RotatingFileHandler
import platform
import os

if platform.system() != "Windows":
    from smbus2 import SMBus
else:
    # Mock classes for Windows development
    class SMBus:
        def __init__(self, bus):
            print(f"Mock SMBus initialized on bus {bus}")

        def write_i2c_block_data(self, *args):
            print("Mock write called with", args)

        def read_i2c_block_data(self, address, register, length):
            print(
                f"Mock read_i2c_block_data: address={address}, register={register}, length={length}"
            )
            return [0] * length  # Return dummy data

    class i2c_msg:
        @staticmethod
        def write(address, data):
            print(f"Mock i2c_msg.write called: address={address}, data={data}")
            return None


import time
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

I2C_BUS = 1  # I2C bus number (usually 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the ESP32 (or other I2C device)


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


class PIN:
    def __init__(self):
        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus
        logging.info("Initializing communication with the I2C slave...")

        while True:
            try:
                logging.debug("Attempting to send data to I2C slave...")
                self.bus.write_i2c_block_data(I2C_ADDRESS, 0, b"Hello")
                logging.info("Data sent successfully.")

                # Attempt to read back a response
                raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 5)
                response = list(raw_data)

                logging.info(f"Received response: {response}")

                if response:  # If a response is received, break the loop
                    break

            except Exception as e:
                logging.error(f"Failed to send data: {e}")
                logging.info("Retrying in 1 second...")
                time.sleep(1)  # Wait before retrying

        logging.info("Communication with the I2C slave was successful.")

    def read_pin_states(self, game_action):
        try:

            # Request data from the ESP32, assuming 2 bytes are needed
            raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
            # Parse the received data into pin states
            pin = self._parse_i2c_data(raw_data, game_action)

            return pin
        except Exception as e:
            logging.error(f"Failed to read from I2C bus: {e}")
            return None

    def _parse_i2c_data(self, data, game_action):
        logging.debug(f"Parsing I2C data: {data} for game action: {game_action}")
        # Convert the raw I2C data into a dictionary of pin states
        pin_number = data[0]
        if pin_number == 0xFF:
            return None  # Neutral signal, nothing to process

        state = "LOW" if data[1] == 0 else "HIGH"
        logging.debug(f"Pin {pin_number} state is {state}")

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
            return int(pin)
        return None
