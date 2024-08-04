import os
import pygame

class EndMenu:
    def __init__(self):
        self.selected_option = 0
        self.options = ["Continuer","Nouveau", "Recommencer", "Quitter"]

        self.frog_sound = self.load_sound(
                "sounds", "frog.mp3"
            )
        
    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        return pygame.mixer.Sound(path)

    def handle_button_press(self, button):
        self.frog_sound.play()
        if button == "UP":
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif button == "DOWN":
            self.selected_option = (self.selected_option + 1) % len(self.options)
        
