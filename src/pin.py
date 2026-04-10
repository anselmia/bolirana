import logging
import platform
import pygame

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
            return [0xFF, 0]  # Return dummy data

    class i2c_msg:
        @staticmethod
        def write(address, data):
            print(f"Mock i2c_msg.write called: address={address}, data={data}")
            return None


import time
from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
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
    def __init__(self, screen, use_i2c=True):
        self.use_i2c = use_i2c
        self.bus = None
        self.last_pin_time = {}  # Dictionary to track last detection time for each pin
        self.COOLDOWN_MS_PIN = 1200  # Cooldown period in milliseconds
        self.COOLDOWN_MS_Button = 500  # Cooldown period in milliseconds
        self.pin_hole = set(
            PIN_H20
            + PIN_H25
            + PIN_H40
            + PIN_H50
            + PIN_H100
            + PIN_HBOTTLE
            + PIN_HSFROG
            + PIN_HLFROG
        )
        self.button_pin = {PIN_BNEXT, PIN_BENTER, PIN_RIGHT}
        self.menu_pins = {PIN_BENTER, PIN_RIGHT, PIN_BNEXT}
        self.game_pins = self.pin_hole | {PIN_BNEXT, PIN_BENTER, PIN_RIGHT}
        self.end_menu_pins = {PIN_BENTER, PIN_BNEXT}

        if not self.use_i2c:
            logging.info("Keyboard/test mode enabled: skipping I2C initialization.")
            return

        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus
        logging.info("Initializing communication with the I2C slave...")

        self.display_waiting_popup(screen)

        while True:
            try:
                # Attempt to read back a response
                raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
                response = list(raw_data)

                if response:  # If a response is received, break the loop
                    logging.info(f"I2C slave connected. Received response: {response}")
                    break

            except Exception as e:
                logging.error(f"Failed to receive data: {e}")
                logging.info("Retrying in 1 second...")
                time.sleep(1)  # Wait before retrying

        logging.info("Communication with the I2C slave was successful.")
        self.clear_popup(screen)

    def display_waiting_popup(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render("Waiting for I2C connection...", True, (255, 255, 255))
        text_rect = text.get_rect(center=screen.get_rect().center)

        screen.fill((0, 0, 0))  # Fill the screen with black
        screen.blit(text, text_rect)
        pygame.display.flip()

    def clear_popup(self, screen):
        screen.fill((0, 0, 0))  # Clear the screen
        pygame.display.flip()

    def read_pin_states(self, game_action):
        if not self.use_i2c or self.bus is None:
            return None
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
        pin = int(pin)
        current_time = time.time() * 1000  # Convert to milliseconds
        last_time = self.last_pin_time.get(pin, 0)

        if pin in self.pin_hole:
            cooldown = self.COOLDOWN_MS_PIN
        else:
            cooldown = self.COOLDOWN_MS_Button
        # Apply cooldown
        if current_time - last_time < cooldown:
            logging.debug(f"Pin {pin} ignored due to cooldown.")
            return None

        # Update last detection time for the pin
        self.last_pin_time[pin] = current_time

        if game_action == "menu" and pin in self.menu_pins:
            return pin
        if game_action == "game" and pin in self.game_pins:
            return pin
        if game_action == "end_menu" and pin in self.end_menu_pins:
            return pin
        return None
