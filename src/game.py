import pygame
import time
import sys
import random
import os
import queue

from PIL import Image
from src.constants import *
from src.menu import Menu
from src.roulette import RouletteAnimation
from src.holes import Hole
from src.firework import Firework
import logging


class Game:
    def __init__(self, queue):
        logging.basicConfig(level=logging.INFO)
        pygame.init()
        pygame.mixer.init()
        self.queue = queue
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Bolirana Game")
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_verysmall = pygame.font.Font(None, 30)
        self.menu = Menu(self.screen, self.font_small)
        self.load_ressource()
        self.init_game()

    def load_ressources(self):
        # Load the background image
        try:
            game_background_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "images",
                "game_background.jpg",
            )
            if not os.path.exists(game_background_path):
                raise FileNotFoundError(f"No such file: {game_background_path}")
            self.background = pygame.image.load(game_background_path)
            self.background = pygame.transform.scale(
                self.background, self.screen.get_size()
            )
        except Exception as e:
            logging.error(f"Failed to load resources: {e}")
            raise SystemExit

    def init_game(self):
        # Initialize game state
        self.num_players = 1  # Default number of players
        self.team_mode = "Seul"  # Default team mode
        self.game_mode = "Normal"  # Default game mode
        self.num_pairs = 1  # Default number of pairs
        self.num_teams = 1  # Default number of teams
        self.players_per_team = 1  # Default number of players per team
        self.players = []
        self.current_player_index = 0
        self.current_ball = 1
        self.selecting_mode = True
        self.game_ended = False
        self.penalty = False
        self.curent_player_score = 0
        self.winner = 0
        self.fireworks = []

    def run(self):
        while self.selecting_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event.key)

            # Check the queue for new data
            pin = self.process_queue("menu")
            if pin is not None:
                self.handle_menu_button(pin)

            self.menu.draw()
            pygame.display.flip()
            time.sleep(0.1)

        self.play()
        self.display_end_menu()

    def process_queue(self, game_action):
        try:
            if game_action == "menu":
                pin, state = self.queue.get_nowait()  # Non-blocking get
                if (
                    pin == PIN_BENTER
                    or pin == PIN_DOWN
                    or pin == PIN_UP
                    or pin == PIN_LEFT
                    or pin == PIN_RIGHT
                ) and state == "HIGH":
                    return pin
            elif game_action == "game":
                if (
                    pin == PIN_BNEXT
                    or pin == PIN_BENTER
                    or pin == PIN_H20
                    or pin == PIN_H25
                    or pin == PIN_H40
                    or pin == PIN_H50
                    or pin == PIN_H100
                    or pin == PIN_HBOTTLE
                    or pin == PIN_HSFROG
                    or pin == PIN_HLFROG
                ) and state == "HIGH":
                    return pin
        except queue.Empty:
            return None

        return None

    def handle_menu_button(self, pin):
        if pin == PIN_UP:
            self.menu.handle_button_press("UP")
        elif pin == PIN_DOWN:
            self.menu.handle_button_press("DOWN")
        elif pin == PIN_LEFT:
            self.menu.handle_button_press("LEFT")
        elif pin == PIN_RIGHT:
            self.menu.handle_button_press("RIGHT")
        elif pin == PIN_BENTER:
            self.setup_game()

    def setup_game(self):
        self.num_players = self.menu.get_num_players()
        self.team_mode = self.menu.get_team_mode()
        self.score = self.menu.get_score()
        self.game_mode = self.menu.get_game_mode()
        self.num_pairs = self.menu.get_num_pairs()
        self.num_teams = self.menu.get_num_teams()
        self.players_per_team = self.menu.get_players_per_team()
        self.players = self.setup_players()
        penalty = self.menu.get_penalty()
        if penalty == "Avec":
            self.penalty = True
        random.shuffle(self.players)  # Randomize player order
        self.scores = [0] * len(self.players)
        for i in range(len(self.players)):
            self.scores[i] = 0

        if self.game_mode == "Normal":
            self.holes = [
                Hole("20", 20, PIN_H20),
                Hole("25", 25, PIN_H25),
                Hole("40", 40, PIN_H40),
                Hole("50", 50, PIN_H50),
                Hole("100", 100, PIN_H100),
                Hole("bottle", 150, PIN_HBOTTLE),
                Hole("little_frog", 200, PIN_HSFROG),
                Hole("large_frog", 0, PIN_HLFROG),
            ]
        elif self.game_mode == "Grenouille":
            self.holes = [
                Hole("20", 0, PIN_H20),
                Hole("25", 0, PIN_H25),
                Hole("40", 0, PIN_H40),
                Hole("50", 0, PIN_H50),
                Hole("100", 0, PIN_H100),
                Hole("bottle", 0, PIN_HBOTTLE),
                Hole("little_frog", 200, PIN_HSFROG),
                Hole("large_frog", 0, PIN_HLFROG),
            ]
        elif self.game_mode == "Bouteille":
            self.holes = [
                Hole("20", 0, PIN_H20),
                Hole("25", 0, PIN_H25),
                Hole("40", 0, PIN_H40),
                Hole("50", 0, PIN_H50),
                Hole("100", 0, PIN_H100),
                Hole("bottle", 150, PIN_HBOTTLE),
                Hole("little_frog", 0, PIN_HSFROG),
                Hole("large_frog", 0, PIN_HLFROG),
            ]

        self.selecting_mode = False

    def setup_players(self):
        players = []
        if self.team_mode == "Seul":
            for i in range(self.num_players):
                players.append(f"Joueur {i+1}")
        elif self.team_mode == "Duo":
            for pair_num in range(1, self.num_pairs + 1):
                players.extend(
                    [f"Duo {pair_num} - Joueur 1", f"Duo {pair_num} - Joueur 2"]
                )
        elif self.team_mode == "Equipe":
            for team_num in range(1, self.num_teams + 1):
                for player_num in range(1, self.players_per_team + 1):
                    players.append(f"Equipe {team_num} - Joueur {player_num}")
        return players

    def play(self):
        sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "intro.mp3",
            )
        )
        sound.play()
        while not self.game_ended:
            self.display_game()
            self.handle_turn()

        self.end_game()

    def display_game(self):
        dark_green = pygame.Color(GREENDARK)  # A darker shade of green
        dark_red = pygame.Color(REDDARK)  # A darker shade of red
        dark_yellow = pygame.Color(YELLOWDARK)  # A darker shade of red

        self.screen.blit(self.background, (0, 0))  # Draw the background image

        # Draw current player, their score, and remaining points
        current_player_name = f"Joueur {self.current_player_index + 1}"
        current_player_score = f"Score: {self.scores[self.current_player_index]}"
        remaining_points_text = (
            f"Points Restants: {self.score - self.scores[self.current_player_index]}"
        )

        current_player_name_text = self.font_large.render(
            current_player_name, True, dark_green
        )
        current_player_score_text = self.font_medium.render(
            current_player_score, True, dark_yellow
        )
        remaining_points_text_rendered = self.font_verysmall.render(
            remaining_points_text, True, pygame.Color("white")
        )

        self.screen.blit(current_player_name_text, (20, 20))
        self.screen.blit(current_player_score_text, (20, 80))
        self.screen.blit(remaining_points_text_rendered, (20, 150))

        # Draw holes and associated points
        hole_points = [
            150,
            50,
            25,
            40,
            20,
            100,
            "ROUL",
            200,
            150,
            50,
            25,
            40,
            20,
            100,
        ]

        circle_radius = 30

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        hole_positions = [
            ((screen_width / 3.2) + circle_radius, 50),
            ((screen_width / 3.2) + circle_radius + 60, 100),
            ((screen_width / 3.2) + circle_radius, 150),
            ((screen_width / 3.2) + circle_radius + 60, 200),
            ((screen_width / 3.2) + circle_radius, 250),
            ((screen_width / 3.2) + circle_radius + 60, 300),
            ((screen_width / 3.2) + circle_radius + 120, 50),
            ((screen_width / 3.2) + circle_radius + 120, 150),
            ((screen_width / 3.2) + circle_radius + 240, 50),
            ((screen_width / 3.2) + circle_radius + 180, 100),
            ((screen_width / 3.2) + circle_radius + 240, 150),
            ((screen_width / 3.2) + circle_radius + 180, 200),
            ((screen_width / 3.2) + circle_radius + 240, 250),
            ((screen_width / 3.2) + circle_radius + 180, 300),
        ]

        for i, points in enumerate(hole_points):
            x, y = hole_positions[i]
            pygame.draw.circle(
                self.screen, pygame.Color("white"), (x, y), circle_radius
            )
            font = self.font_medium
            if str(points) == "ROUL":
                font = self.font_small
            points_text = font.render(str(points), True, pygame.Color("black"))
            text_rect = points_text.get_rect(center=(x, y))
            self.screen.blit(points_text, text_rect)

        # Draw Game Information
        game_mode_text = self.font_medium.render(self.game_mode, True, dark_yellow)
        score_text = self.font_medium.render(
            str(self.score) + " points", True, dark_yellow
        )
        team_mode_text = self.font_medium.render(self.team_mode, True, dark_yellow)

        self.screen.blit(
            game_mode_text, ((screen_width / 3.2) + circle_radius + 360, 20)
        )
        self.screen.blit(score_text, ((screen_width / 3.2) + circle_radius + 360, 80))
        self.screen.blit(
            team_mode_text, ((screen_width / 3.2) + circle_radius + 360, 140)
        )

        margin_left = 20
        margin_right = 20
        gap_between_boxes = 10
        box_height = 90
        start_y = screen_height - (box_height + gap_between_boxes) * 3 - 50

        box_width = (
            screen_width - margin_left - margin_right - gap_between_boxes * 3
        ) // 4

        for i in range(len(self.scores)):
            x = margin_left + (i % 4) * (box_width + gap_between_boxes)
            y = start_y + (i // 4) * (box_height + gap_between_boxes)

            # Background color for player boxes
            bg_color = dark_red if i % 2 == 0 else dark_green

            # Draw the border
            border_color = (
                pygame.Color("yellow")
                if i == self.current_player_index
                else pygame.Color("black")
            )
            pygame.draw.rect(
                self.screen,
                border_color,
                (x, y, box_width, box_height),
                border_radius=5,
                width=5,  # Border width
            )

            # Draw the background inside the border
            pygame.draw.rect(
                self.screen,
                bg_color,
                (x + 5, y + 5, box_width - 10, box_height - 10),
                border_radius=5,
            )

            player_label = self.font_small.render(
                f"Joueur {i + 1}", True, pygame.Color("yellow")
            )
            score_text = self.font_medium.render(
                f"{self.scores[i]}", True, pygame.Color("white")
            )
            self.screen.blit(player_label, (x + 10, y + 10))
            self.screen.blit(score_text, (x + 10, y + 50))

        pygame.display.flip()

    def handle_turn(self):
        pin = self.process_queue("game")
        if pin is not None:
            if pin == PIN_BNEXT:
                self.next_player()
            elif (
                pin == PIN_H20
                or pin == PIN_H25
                or pin == PIN_H40
                or pin == PIN_H50
                or pin == PIN_H100
                or pin == PIN_HBOTTLE
                or pin == PIN_HSFROG
                or pin == PIN_HLFROG
            ):
                self.goal(pin)
            elif pin == PIN_BENTER:
                self.display_end_menu()

    def next_player(self):
        if self.curent_player_score == 0 and self.penalty:
            # Load the video using moviepy
            frames, duration = self.load_gif(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "assets",
                    "gif",
                    "fail.gif",
                )
            )
            sound = pygame.mixer.Sound(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "assets",
                    "sounds",
                    "fail.mp3",
                )
            )
            sound.play()
            self.play_gif(frames, duration)
            self.play_gif(frames, duration)
            roulette_animation = RouletteAnimation(self.screen, "null")
            points = roulette_animation.run()
            self.scores[self.current_player_index] -= points

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.curent_player_score = 0

    def goal(self, pin):
        hole = next((hole for hole in self.holes if pin == hole.pin), None)
        points = 0
        if hole is not None:
            if (
                hole.type == "20"
                or hole.type == "25"
                or hole.type == "40"
                or hole.type == "50"
                or hole.type == "100"
                or hole.type == "bottle"
                or hole.type == "little_frog"
            ):
                points = hole.value
            if hole.type == "bottle":
                self.animation_bottle()
            if hole.type == "little_frog":
                self.animation_little_frog()
            if hole.type == "large_frog":
                points = self.animation_large_frog()

        self.scores[self.current_player_index] += points
        self.curent_player_score += points

        if self.scores[self.current_player_index] >= self.score:
            self.game_ended = True
            self.winner = self.current_player_index

    def animation_bottle(self):
        sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "bouteille.mp3",
            )
        )
        sound.play()

    def animation_little_frog(self):
        frames, duration = self.load_gif(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "gif",
                "small_frog_animation.gif",
            )
        )
        sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "aplaudissement_smallfrog.mp3",
            )
        )
        sound.play()
        self.play_gif(frames, duration)

    def animation_large_frog(self):
        frames, duration = self.load_gif(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "gif",
                "large_frog_animation.gif",
            )
        )
        sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "aplaudissement_largefrog.mp3",
            )
        )
        sound.play()
        self.play_gif(frames, duration)

        roulette_animation = RouletteAnimation(self.screen, "frog")
        return roulette_animation.run()

    def load_gif(self, gif_path):
        # Load GIF using PIL
        gif = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = gif.copy().convert("RGBA")  # Convert to RGBA for consistency
                frames.append(frame)
                gif.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass
        return frames, gif.info["duration"]

    def play_gif(self, frames, duration):
        clock = pygame.time.Clock()
        frame_index = 0
        running = True

        screen_width, screen_height = self.screen.get_size()

        # Create a transparent surface for clearing
        clear_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        while running and frame_index < len(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Get the current frame
            frame = frames[frame_index]
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()

            if mode == "RGBA":
                surface = pygame.image.fromstring(data, size, "RGBA")
            else:
                surface = pygame.image.fromstring(data, size, "RGB")

            # Calculate position to center the frame
            frame_width, frame_height = size
            x = (screen_width - frame_width) // 2
            y = (screen_height - frame_height) // 2

            # Clear the area where the frame will be drawn with transparency
            clear_surface.fill((0, 0, 0, 0))
            self.screen.blit(clear_surface, (x, y), (x, y, frame_width, frame_height))

            self.display_game()

            # Draw the frame
            self.screen.blit(surface, (x, y))
            pygame.display.flip()

            frame_index += 1
            clock.tick(1000 // duration)

    def end_game(self):
        self.screen.fill((0, 0, 0))  # Clear the screen
        # Display the congratulatory message
        message = f"Bravo Joueur {self.winner + 1}!"
        text_surface = self.font_large.render(message, True, pygame.Color("yellow"))
        text_rect = text_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)  # Display the message for 2 seconds
        sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "victoire.mp3",
            )
        )
        sound.play()
        self.run_fireworks()

    def create_fireworks(self, num_fireworks):
        for _ in range(num_fireworks):
            x = random.randint(100, self.screen.get_width() - 100)
            y = random.randint(100, self.screen.get_height() - 100)
            color = [random.randint(0, 255) for _ in range(3)]
            self.fireworks.append(Firework(x, y, color, num_particles=50))

    def run_fireworks(self):
        self.create_fireworks(5)
        running = True
        clock = pygame.time.Clock()
        while running and self.fireworks:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            self.screen.fill((0, 0, 0))
            for firework in self.fireworks:
                firework.update()
                firework.draw(self.screen)
            self.fireworks = [f for f in self.fireworks if not f.is_dead()]
            pygame.display.flip()
            clock.tick(30)

    def handle_key_event(self, key):
        if key == pygame.K_UP:
            self.menu.handle_button_press("UP")
        elif key == pygame.K_DOWN:
            self.menu.handle_button_press("DOWN")
        elif key == pygame.K_LEFT:
            self.menu.handle_button_press("LEFT")
        elif key == pygame.K_RIGHT:
            self.menu.handle_button_press("RIGHT")
        elif key == pygame.K_RETURN:
            self.setup_game()

    def read_input(self):
        pin = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pin = PIN_H20
                    break
                elif event.key == pygame.K_s:
                    pin = PIN_H25
                    break
                elif event.key == pygame.K_d:
                    pin = PIN_H40
                    break
                elif event.key == pygame.K_f:
                    pin = PIN_H50
                    break
                elif event.key == pygame.K_g:
                    pin = PIN_H100
                    break
                elif event.key == pygame.K_h:
                    pin = PIN_HBOTTLE
                    break
                elif event.key == pygame.K_j:
                    pin = PIN_HSFROG
                    break
                elif event.key == pygame.K_k:
                    pin = PIN_HLFROG
                    break
                elif event.key == pygame.K_n:
                    pin = PIN_BNEXT
                    break

        return pin
