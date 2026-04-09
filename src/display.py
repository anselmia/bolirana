import logging
import os
import sys
import time
from array import array
from math import pi, sin

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

        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        font_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
        font_path = os.path.join(font_dir, "AntonSC-Regular.ttf")
        title_font_path = os.path.join(font_dir, "GaMaamli-Regular.ttf")
        self.font_title = pygame.font.Font(title_font_path, 68)
        self.font_title_small = pygame.font.Font(title_font_path, 54)
        self.font_large = pygame.font.Font(font_path, 50)
        self.font_medium = pygame.font.Font(font_path, 30)
        self.font_small = pygame.font.Font(font_path, 25)
        self.font_verysmall = pygame.font.Font(font_path, 20)
        if self.screen_height >= 900:
            self.font_title = pygame.font.Font(title_font_path, 78)
            self.font_title_small = pygame.font.Font(title_font_path, 60)
            self.font_large = pygame.font.Font(font_path, 56)
            self.font_medium = pygame.font.Font(font_path, 34)
            self.font_small = pygame.font.Font(font_path, 28)
            self.font_verysmall = pygame.font.Font(font_path, 22)
        self.half_width = self.screen_width // 2
        self.half_height = self.screen_height // 2
        self.third_width = self.screen_width // 3
        self.hole_frame_width = self.half_width
        self.frame_score_width = self.screen_width // 5
        self.frame_player_width = self.screen_width // 5
        self.hole_rect_height = int(self.screen_height / 2.4)
        self.frame_space_x = (
            int(
                self.screen_width - (2 * self.frame_score_width) - self.hole_frame_width
            )
            // 4
        )
        self.frame_space_y = 20
        self.border_holes = 0
        self.hole_frame_border = 7
        self.hole_space = self.hole_rect_height / 30
        self.clock = pygame.time.Clock()
        self.resources = {}
        self.time_warning_channel = None
        self.time_warning_next_allowed = 0.0
        self.load_ressources()
        self.ui = DisplayUIService(self)
        self.effects = DisplayEffectsService(self)

    def load_ressources(self):
        try:
            self.resources["game_background"] = self.load_background(
                "images", "game3.jpg"
            )
            self.resources["menu_background"] = self.load_background(
                "images", "intro.jpg"
            )
            self.resources["win_background"] = self.load_background("images", "win.jpg")
            self.resources["winner_banner"] = self.load_background(
                "images", "winner.png"
            )
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
            self.resources["frog_sound"] = self.load_sound("sounds", "frog.mp3")
            self.resources["bottle_sound"] = self.load_sound("sounds", "bouteille.mp3")
            self.resources["coin_sound"] = self.create_coin_sound()
            self.resources["warning_siren"] = self.create_warning_siren_sound()
            self.resources["roulette_sound"] = self.load_sound("sounds", "roulette.mp3")
            self.resources["roulette_end_sound"] = self.load_sound(
                "sounds", "roulette_end.mp3"
            )
            self.resources["applause"] = self.load_sound("sounds", "aplaudissement.mp3")
            self.resources["winner_banner"] = pygame.transform.scale(
                self.resources["winner_banner"], (50, 50)
            )
            channel_count = pygame.mixer.get_num_channels()
            if channel_count > 0:
                self.time_warning_channel = pygame.mixer.Channel(channel_count - 1)
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

    def create_coin_sound(self):
        mixer_config = pygame.mixer.get_init()
        if mixer_config is None:
            return None

        sample_rate, _, channels = mixer_config
        duration = 0.12
        frame_count = int(sample_rate * duration)
        fade_start = int(frame_count * 0.55)
        amplitude = 0.34
        samples = array("h")

        for index in range(frame_count):
            progress = index / sample_rate
            envelope = 1.0 - (index / frame_count)
            if index >= fade_start:
                envelope *= max(
                    0.0, 1.0 - ((index - fade_start) / (frame_count - fade_start))
                )

            tone = sin(2 * pi * 1320 * progress)
            tone += 0.55 * sin(2 * pi * 1760 * progress)
            tone += 0.25 * sin(2 * pi * 2640 * progress)
            sample_value = int(32767 * amplitude * envelope * tone / 1.8)
            for _ in range(channels):
                samples.append(sample_value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def create_warning_siren_sound(self):
        mixer_config = pygame.mixer.get_init()
        if mixer_config is None:
            return None

        sample_rate, _, channels = mixer_config
        duration = 0.38
        frame_count = int(sample_rate * duration)
        amplitude = 0.24
        samples = array("h")

        for index in range(frame_count):
            progress = index / max(1, frame_count - 1)
            sweep = sin(progress * pi)
            frequency = 620 + 240 * sweep
            overtone = frequency * 1.52
            envelope = 0.72 + 0.28 * sin(progress * pi)
            envelope *= 1.0 - 0.18 * progress
            timeline = index / sample_rate

            tone = sin(2 * pi * frequency * timeline)
            tone += 0.42 * sin(2 * pi * overtone * timeline)
            tone += 0.12 * sin(2 * pi * (frequency * 0.5) * timeline)
            sample_value = int(32767 * amplitude * envelope * tone / 1.54)
            for _ in range(channels):
                samples.append(sample_value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def stop_time_warning_audio(self):
        if (
            self.time_warning_channel is not None
            and self.time_warning_channel.get_busy()
        ):
            self.time_warning_channel.fadeout(90)
        self.time_warning_next_allowed = 0.0

    def update_time_warning_audio(self, challenge_state):
        if (
            challenge_state is None
            or challenge_state.get("type") != "time_attack"
            or challenge_state.get("awaiting_start")
            or not challenge_state.get("low_time")
        ):
            self.stop_time_warning_audio()
            return

        warning_sound = self.resources.get("warning_siren")
        if warning_sound is None or self.time_warning_channel is None:
            return

        now = time.monotonic()
        remaining = max(0.0, float(challenge_state.get("remaining_seconds", 0.0)))
        duration = max(1.0, float(challenge_state.get("turn_duration", 1.0)))
        urgency = 1.0 - min(1.0, remaining / duration)
        pulse_interval = 0.95 - 0.45 * urgency
        volume = 0.28 + 0.32 * urgency

        if self.time_warning_channel.get_busy() or now < self.time_warning_next_allowed:
            return

        self.time_warning_channel.set_volume(volume)
        self.time_warning_channel.play(warning_sound, fade_ms=40)
        self.time_warning_next_allowed = now + pulse_interval

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
                    self.frame_space_y
                    + self.hole_frame_border
                    + HOLE_RADIUS
                    + self.border_holes,
                ]
                if position == 1
                else [
                    (self.screen_width / 2) + self.hole_frame_width / 3,
                    self.frame_space_y
                    + self.hole_frame_border
                    + HOLE_RADIUS
                    + self.border_holes,
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
                self.frame_space_y
                + self.hole_frame_border
                + HOLE_RADIUS
                + self.border_holes,
            ]
        return None

    def draw_chrome_rect(self, *args, **kwargs):
        return self.ui.draw_chrome_rect(*args, **kwargs)

    def draw_text_with_outline(self, *args, **kwargs):
        return self.ui.draw_text_with_outline(*args, **kwargs)

    def draw_menu(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.ui.draw_menu(*args, **kwargs)

    def draw_end_menu(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.ui.draw_end_menu(*args, **kwargs)

    def play_intro(self, *args, **kwargs):
        self.stop_time_warning_audio()
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
        self.stop_time_warning_audio()
        return self.effects.draw_goal_animation(*args, **kwargs)

    def draw_penalty(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_penalty(*args, **kwargs)

    def draw_player_win(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_player_win(*args, **kwargs)

    def draw_win(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_win(*args, **kwargs)

    def animation_bottle(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_bottle(*args, **kwargs)

    def animation_little_frog(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_little_frog(*args, **kwargs)

    def animation_roulette(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_roulette(*args, **kwargs)

    def animation_large_frog(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_large_frog(*args, **kwargs)

    def run_fireworks(self, *args, **kwargs):
        return self.effects.run_fireworks(*args, **kwargs)
