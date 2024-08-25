import os
import pygame
import logging


class EndMenu:
    def __init__(self):
        logging.info("Initializing EndMenu...")
        self.selected_option = 0
        self.options = ["Continuer", "Nouveau", "Recommencer", "Quitter"]

        try:
            self.frog_sound = self.load_sound("sounds", "frog.mp3")
        except Exception as e:
            logging.error(f"Error loading frog sound: {e}")

    def load_sound(self, folder, filename):
        try:
            path = os.path.join(
                os.path.dirname(__file__), "..", "assets", folder, filename
            )
            sound = pygame.mixer.Sound(path)
            logging.debug(f"Sound loaded from {path}.")
            return sound
        except Exception as e:
            logging.error(f"Failed to load sound from {folder}/{filename}: {e}")
            raise

    def handle_button_press(self, button):
        self.frog_sound.play()
        if button == "DOWN":
            previous_option = self.selected_option
            self.selected_option = (self.selected_option + 1) % len(self.options)
