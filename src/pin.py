import logging
import platform
import time
from smbus2 import SMBus
import tkinter as tk

I2C_BUS = 1  # I2C bus number (usually 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the ESP32 (or other I2C device)


class PIN:
    def __init__(self):
        self.bus = SMBus(I2C_BUS)  # Initialize the I2C bus
        self.last_pin_time = {}  # Dictionary to track last detection time for each pin
        self.COOLDOWN_MS_PIN = 1200  # Cooldown period in milliseconds
        self.COOLDOWN_MS_Button = 500  # Cooldown period in milliseconds
        self.pin_hole = [
            # Define your pin holes here, e.g., PIN_H20, PIN_H25, ...
        ]
        self.button_pin = [0]  # Example placeholder

        # Initialize the Tkinter pop-up window
        self.root = tk.Tk()
        self.root.title("I2C Connection")
        self.label = tk.Label(
            self.root, text="Waiting for I2C slave to respond...", padx=20, pady=20
        )
        self.label.pack()
        self.root.update()

        logging.info("Initializing communication with the I2C slave...")

        while True:
            try:
                # Attempt to read back a response
                raw_data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
                response = list(raw_data)

                logging.info(f"Received response: {response}")

                if response:  # If a response is received, break the loop
                    logging.info(f"I2C slave connected. Received response: {response}")
                    break

            except Exception as e:
                logging.error(f"Failed to receive data: {e}")
                logging.info("Retrying in 1 second...")
                time.sleep(1)  # Wait before retrying

        logging.info("Communication with the I2C slave was successful.")
        self.root.destroy()  # Close the pop-up window once communication is established

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

        if int(pin) in self.pin_hole:
            cooldown = self.COOLDOWN_MS_PIN
        else:
            cooldown = self.COOLDOWN_MS_Button
        # Apply cooldown
        if current_time - last_time < cooldown:
            logging.debug(f"Pin {pin} ignored due to cooldown.")
            return None

        # Update last detection time for the pin
        self.last_pin_time[pin] = current_time

        return pin if game_action == "game" else None
