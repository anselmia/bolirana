import logging
import os
import sys
import time

import pygame

from src.constants import HOLE_RADIUS
from src.display_services import DisplayEffectsService, DisplayUIService


class Display:
    def __init__(self, debug):
        pygame.display.set_caption("Bolirana Game")
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if debug:
            self.screen = pygame.display.set_mode((1024, 768), flags)
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | flags)

        font_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "fonts", "AntonSC-Regular.ttf"
        )
        self.font_large = pygame.font.Font(font_path, 50)
        self.font_medium = pygame.font.Font(font_path, 30)
        self.font_small = pygame.font.Font(font_path, 25)
        self.font_verysmall = pygame.font.Font(font_path, 20)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.half_width = self.screen_width // 2
        self.half_height = self.screen_height // 2
        self.third_width = self.screen_width // 3
        self.hole_frame_width = self.half_width
        self.frame_score_width = self.screen_width // 5
        self.frame_player_width = self.screen_width // 5
        self.hole_rect_height = int(self.screen_height / 2.4)
        self.frame_space_x = (
            int(self.screen_width - (2 * self.frame_score_width) - self.hole_frame_width)
            // 4
        )
        self.frame_space_y = 20
        self.border_holes = 0
        self.hole_frame_border = 7
        self.hole_space = self.hole_rect_height / 30
        self.clock = pygame.time.Clock()
        self.resources = {}
        self.load_ressources()
        self.ui = DisplayUIService(self)
        self.effects = DisplayEffectsService(self)

    def load_ressources(self):
        try:
            self.resources["game_background"] = self.load_background("images", "game3.jpg")
            self.resources["menu_background"] = self.load_background("images", "intro.jpg")
            self.resources["win_background"] = self.load_background("images", "win.jpg")
            self.resources["winner_banner"] = self.load_background("images", "winner.png")
            self.resources["roulette_image"] = self.load_image(
                "images", "roulette_image.png", scale=0.8
            )
            self.resources["roulette_pointer"] = self.load_image(
                "images", "roulette_pointer.png", scale=0.1
            )
            self.resources["frame_player_select"] = self.load_image(
                "images",
                "frame_player_select.png",
                width=self.frame_player_width,
                height=70,
            )
            self.resources["frame_player"] = self.load_image(
                "images", "frame_player.png", width=self.frame_player_width, height=70
            )
            self.resources["hole"] = self.load_image(
                "images", "hole.png", width=2 * HOLE_RADIUS, height=2 * HOLE_RADIUS
            )
            self.resources["hole_score"] = self.load_image(
                "images",
                "hole_score.png",
                width=2 * HOLE_RADIUS,
                height=2 * HOLE_RADIUS,
            )

            self.resources["penalty_sound"] = self.load_sound("sounds", "fail.mp3")
            self.resources["win_sound"] = self.load_sound("sounds", "victoire.mp3")
            self.resources["intro_sound"] = self.load_sound("sounds", "intro.mp3")
            self.resources["bottle_sound"] = self.load_sound("sounds", "bouteille.mp3")
            self.resources["roulette_sound"] = self.load_sound("sounds", "roulette.mp3")
            self.resources["roulette_end_sound"] = self.load_sound(
                "sounds", "roulette_end.mp3"
            )
            self.resources["applause"] = self.load_sound("sounds", "aplaudissement.mp3")
            self.resources["winner_banner"] = pygame.transform.scale(
                self.resources["winner_banner"], (50, 50)
            )
        except Exception as error:
            logging.error(f"Failed to load resources: {error}")
            self.display_error_message("Failed to load resources. Exiting...")
            pygame.quit()
            sys.exit()

    def prepare_surface(self, surface):
        if surface.get_alpha() is not None:
            return surface.convert_alpha()
        return surface.convert()

    def load_background(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        surface = self.prepare_surface(pygame.image.load(path))
        return pygame.transform.smoothscale(surface, self.screen.get_size())

    def load_image(self, folder, filename, scale=None, width=None, height=None):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        original_image = self.prepare_surface(pygame.image.load(path))

        if scale is not None:
            original_width, original_height = original_image.get_size()
            _, screen_height = self.screen.get_size()
            new_height = int(screen_height * scale)
            aspect_ratio = original_width / original_height
            new_width = int(new_height * aspect_ratio)
            return self.prepare_surface(
                pygame.transform.smoothscale(original_image, (new_width, new_height))
            )

        if width is not None and height is not None:
            return self.prepare_surface(
                pygame.transform.smoothscale(original_image, (int(width), int(height)))
            )

        return original_image

    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        if (folder, filename) not in self.resources:
            self.resources[(folder, filename)] = pygame.mixer.Sound(path)
        return self.resources[(folder, filename)]

    def display_error_message(self, message):
        self.screen.fill((0, 0, 0))
        error_text = self.font_large.render(message, True, (255, 0, 0))
        self.screen.blit(
            error_text,
            (
                self.half_width - error_text.get_width() // 2,
                self.half_height,
            ),
        )
        pygame.display.flip()
        time.sleep(3)

    def get_hole_position(self, hole_value, position):
        if hole_value == "20":
            return (
                [
                    (self.screen_width / 2) - self.hole_frame_width / 3,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 5 * HOLE_RADIUS
                    + 5 * self.border_holes
                    + 2 * self.hole_space,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 3,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 5 * HOLE_RADIUS
                    + 5 * self.border_holes
                    + 2 * self.hole_space,
                ]
            )
        if hole_value == "25":
            return (
                [
                    (self.screen_width / 2) - self.hole_frame_width / 3,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 3 * HOLE_RADIUS
                    + 3 * self.border_holes
                    + self.hole_space,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 3,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 3 * HOLE_RADIUS
                    + 3 * self.border_holes
                    + self.hole_space,
                ]
            )
        if hole_value == "40":
            return (
                [
                    (self.screen_width / 2) - self.hole_frame_width / 6,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 1.5
                    + HOLE_RADIUS * 4
                    + self.border_holes * 4,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 6,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 1.5
                    + HOLE_RADIUS * 4
                    + self.border_holes * 4,
                ]
            )
        if hole_value == "50":
            return (
                [
                    (self.screen_width / 2) - self.hole_frame_width / 6,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space / 2
                    + HOLE_RADIUS * 2
                    + self.border_holes * 2,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 6,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space / 2
                    + HOLE_RADIUS * 2
                    + self.border_holes * 2,
                ]
            )
        if hole_value == "100":
            return (
                [
                    (self.screen_width / 2) - self.hole_frame_width / 6,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 2.5
                    + HOLE_RADIUS * 6
                    + self.border_holes * 6,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 6,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 2.5
                    + HOLE_RADIUS * 6
                    + self.border_holes * 6,
                ]
            )
        if hole_value == "150":
            return (
                [
                    (self.screen_width / 2) - self.hole_frame_width / 3,
                    self.frame_space_y + self.hole_frame_border + HOLE_RADIUS + self.border_holes,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 3,
                    self.frame_space_y + self.hole_frame_border + HOLE_RADIUS + self.border_holes,
                ]
            )
        if hole_value == "200":
            return [
                self.screen_width / 2,
                self.frame_space_y
                + self.hole_frame_border
                + 3 * HOLE_RADIUS
                + 3 * self.border_holes
                + self.hole_space,
            ]
        if hole_value == "ROUL":
            return [
                self.screen_width / 2,
                self.frame_space_y + self.hole_frame_border + HOLE_RADIUS + self.border_holes,
            ]
        return None

    def draw_chrome_rect(self, *args, **kwargs):
        return self.ui.draw_chrome_rect(*args, **kwargs)

    def draw_text_with_outline(self, *args, **kwargs):
        return self.ui.draw_text_with_outline(*args, **kwargs)

    def draw_menu(self, *args, **kwargs):
        return self.ui.draw_menu(*args, **kwargs)

    def draw_end_menu(self, *args, **kwargs):
        return self.ui.draw_end_menu(*args, **kwargs)

    def play_intro(self, *args, **kwargs):
        return self.ui.play_intro(*args, **kwargs)

    def draw_game(self, *args, **kwargs):
        return self.ui.draw_game(*args, **kwargs)

    def draw_holes(self, *args, **kwargs):
        return self.ui.draw_holes(*args, **kwargs)

    def draw_static_elements(self, *args, **kwargs):
        return self.ui.draw_static_elements(*args, **kwargs)

    def display_grouped_players(self, *args, **kwargs):
        return self.ui.display_grouped_players(*args, **kwargs)

    def draw_status_banner(self, *args, **kwargs):
        return self.ui.draw_status_banner(*args, **kwargs)

    def draw_text_with_shadow(self, *args, **kwargs):
        return self.ui.draw_text_with_shadow(*args, **kwargs)

    def calculate_group_layout(self, *args, **kwargs):
        return self.ui.calculate_group_layout(*args, **kwargs)

    def group_players(self, *args, **kwargs):
        return self.ui.group_players(*args, **kwargs)

    def handle_animation_events(self, *args, **kwargs):
        return self.effects.handle_animation_events(*args, **kwargs)

    def wait_with_event_pump(self, *args, **kwargs):
        return self.effects.wait_with_event_pump(*args, **kwargs)

    def ease_out_cubic(self, *args, **kwargs):
        return self.effects.ease_out_cubic(*args, **kwargs)

    def ease_in_out_sine(self, *args, **kwargs):
        return self.effects.ease_in_out_sine(*args, **kwargs)

    def ease_out_back(self, *args, **kwargs):
        return self.effects.ease_out_back(*args, **kwargs)

    def get_rgb(self, *args, **kwargs):
        return self.effects.get_rgb(*args, **kwargs)

    def animate_scene(self, *args, **kwargs):
        return self.effects.animate_scene(*args, **kwargs)

    def draw_overlay(self, *args, **kwargs):
        return self.effects.draw_overlay(*args, **kwargs)

    def draw_glow_circle(self, *args, **kwargs):
        return self.effects.draw_glow_circle(*args, **kwargs)

    def draw_radial_burst(self, *args, **kwargs):
        return self.effects.draw_radial_burst(*args, **kwargs)

    def draw_confetti(self, *args, **kwargs):
        return self.effects.draw_confetti(*args, **kwargs)

    def clamp(self, *args, **kwargs):
        return self.effects.clamp(*args, **kwargs)

    def lerp(self, *args, **kwargs):
        return self.effects.lerp(*args, **kwargs)

    def draw_lily_pad(self, *args, **kwargs):
        return self.effects.draw_lily_pad(*args, **kwargs)

    def draw_frog_character(self, *args, **kwargs):
        return self.effects.draw_frog_character(*args, **kwargs)

    def draw_goal_animation(self, *args, **kwargs):
        return self.effects.draw_goal_animation(*args, **kwargs)

    def draw_penalty(self, *args, **kwargs):
        return self.effects.draw_penalty(*args, **kwargs)

    def draw_player_win(self, *args, **kwargs):
        return self.effects.draw_player_win(*args, **kwargs)

    def draw_win(self, *args, **kwargs):
        return self.effects.draw_win(*args, **kwargs)

    def animation_bottle(self, *args, **kwargs):
        return self.effects.animation_bottle(*args, **kwargs)

    def animation_little_frog(self, *args, **kwargs):
        return self.effects.animation_little_frog(*args, **kwargs)

    def animation_large_frog(self, *args, **kwargs):
        return self.effects.animation_large_frog(*args, **kwargs)

    def run_fireworks(self, *args, **kwargs):
        return self.effects.run_fireworks(*args, **kwargs)