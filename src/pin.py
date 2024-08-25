import logging
import platform

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


class PIN:
    def __init__(self):
        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus
        self.last_pin_time = {}  # Dictionary to track last detection time for each pin
        self.button_states = {}  # Dictionary to track the state of each button pin
        self.COOLDOWN_MS = 500  # General cooldown period in milliseconds
        self.BUTTON_COOLDOWN_MS = 300  # Cooldown period for buttons in milliseconds
        logging.info("Initializing communication with the I2C slave...")

        while True:
            try:
                # Attempt to read back a response
                raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
                response = list(raw_data)

                logging.info(f"Received response: {response}")

                if response:  # If a response is received, break the loop
                    break

            except Exception as e:
                logging.error(f"Failed to receive data: {e}")
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
        current_time = time.time() * 1000  # Convert to milliseconds
        last_time = self.last_pin_time.get(pin, 0)

        # Determine the cooldown period
        cooldown_ms = (
            self.BUTTON_COOLDOWN_MS
            if pin in {PIN_BENTER, PIN_DOWN, PIN_RIGHT, PIN_BNEXT}
            else self.COOLDOWN_MS
        )

        # Check if the cooldown period has passed
        if current_time - last_time < cooldown_ms:
            logging.debug(f"Pin {pin} ignored due to cooldown.")
            return self.button_states.get(
                pin, None
            )  # Return the last known state during cooldown

        # If cooldown has passed, update the last detection time and read the new state
        self.last_pin_time[pin] = current_time

        # Store the current state in the button_states dictionary
        if game_action == "menu" and int(pin) in {PIN_BENTER, PIN_DOWN, PIN_RIGHT}:
            self.button_states[pin] = int(pin)
        elif game_action == "game" and int(pin) in {
            PIN_H20,
            PIN_H25,
            PIN_H40,
            PIN_H50,
            PIN_H100,
            PIN_HBOTTLE,
            PIN_HSFROG,
            PIN_HLFROG,
            PIN_BNEXT,
            PIN_BENTER,
        }:
            self.button_states[pin] = int(pin)
        else:
            self.button_states[pin] = None

        # After the cooldown, reset the button state to LOW before the next read
        self.button_states[pin] = None

        return self.button_states[pin]
