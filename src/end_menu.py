import os
import pygame
import logging

from src.constants import ACTION_NEXT


class EndMenu:
    FROG_SOUND_MAXTIME_MS = 320

    def __init__(self):
        logging.info("Initializing EndMenu...")
        self.selected_option = 0
        self.options = []
        self.set_context(can_continue=True)

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

    def play_frog_sound(self):
        self.frog_sound.stop()
        self.frog_sound.play(maxtime=self.FROG_SOUND_MAXTIME_MS, fade_ms=20)

    def handle_button_press(self, button):
        self.play_frog_sound()
        if button == ACTION_NEXT:
            self.selected_option = (self.selected_option + 1) % len(self.options)

    def set_context(self, can_continue):
        self.options = ["Nouveau", "Recommencer", "Quitter"]
        if can_continue:
            self.options.insert(0, "Continuer")
        self.selected_option = min(self.selected_option, len(self.options) - 1)
