import pygame
import random
import time
import os
import math
from pygame.locals import *

# Define the solid gold color
GOLD_COLOR = (255, 215, 0)


class RouletteAnimation:
    def __init__(self, screen, type):
        self.screen = screen
        self.clock = pygame.time.Clock()

        screen_width, screen_height = self.screen.get_size()
        self.center_x, self.center_y = screen_width // 2, screen_height // 2

        self.sections = 8
        self.radius = 250
        self.inner_radius = 100
        self.section_colors = [
            pygame.Color("red"),
            pygame.Color("blue"),
            pygame.Color("green"),
            pygame.Color("yellow"),
            pygame.Color("orange"),
            pygame.Color("purple"),
            pygame.Color("pink"),
            pygame.Color("cyan"),
        ]

        if type == "frog":
            self.values = [300, 350, 400, 450, 300, 350, 400, 450]
        else:
            self.values = [10, 20, 40, 50, 10, 20, 40, 50]

        self.font = pygame.font.Font(None, 80)  # Double the font size
        self.roulette_font = pygame.font.Font(None, 160)  # Double the font size

        self.roulette_sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "roulette.mp3",
            )
        )
        self.roulette_end_sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "roulette_end.mp3",
            )
        )

    def draw_circle_with_border(self, center, radius, border_color, border_width):
        """Draws a circle with a border effect."""
        for i in range(border_width):
            pygame.draw.circle(
                self.screen,
                border_color,
                center,
                radius + i,
                width=1,
            )

    def draw_roulette(self, angle=0):
        # Draw the light grey background circle
        pygame.draw.circle(
            self.screen,
            pygame.Color("lightgrey"),
            (self.center_x, self.center_y),
            self.radius + 10,
        )

        # Draw the main roulette sections
        for i in range(self.sections):
            start_angle = (360 / self.sections) * i + angle
            end_angle = start_angle + (360 / self.sections)
            points = [
                (self.center_x, self.center_y),
                (
                    self.center_x + self.radius * math.cos(math.radians(start_angle)),
                    self.center_y + self.radius * math.sin(math.radians(start_angle)),
                ),
                (
                    self.center_x + self.radius * math.cos(math.radians(end_angle)),
                    self.center_y + self.radius * math.sin(math.radians(end_angle)),
                ),
            ]
            pygame.draw.polygon(self.screen, self.section_colors[i], points)
            # Draw thin gold borders for each section
            pygame.draw.line(
                self.screen,
                GOLD_COLOR,
                (self.center_x, self.center_y),
                (
                    self.center_x + self.radius * math.cos(math.radians(start_angle)),
                    self.center_y + self.radius * math.sin(math.radians(start_angle)),
                ),
                5,
            )
            pygame.draw.line(
                self.screen,
                GOLD_COLOR,
                (self.center_x, self.center_y),
                (
                    self.center_x + self.radius * math.cos(math.radians(end_angle)),
                    self.center_y + self.radius * math.sin(math.radians(end_angle)),
                ),
                5,
            )

        # Draw the text for each section
        for i in range(self.sections):
            angle_offset = (360 / self.sections) / 2
            angle2 = (360 / self.sections) * i + angle_offset + angle
            x = self.center_x + (self.radius * 0.7) * math.cos(math.radians(angle2))
            y = self.center_y + (self.radius * 0.7) * math.sin(math.radians(angle2))

            # Render the text
            text_surface = self.font.render(
                str(self.values[i]), True, pygame.Color("black")
            )
            text_surface_rotated = pygame.transform.rotate(text_surface, -angle2)
            text_rect = text_surface_rotated.get_rect(center=(x, y))
            self.screen.blit(text_surface_rotated, text_rect)

        # Draw the gold border around the main circle
        self.draw_circle_with_border(
            (self.center_x, self.center_y), self.radius, GOLD_COLOR, 10
        )

        # Draw the gold border around the inner circle
        self.draw_circle_with_border(
            (self.center_x, self.center_y), self.inner_radius, GOLD_COLOR, 5
        )

        # Draw the inner circle
        pygame.draw.circle(
            self.screen,
            pygame.Color("white"),
            (self.center_x, self.center_y),
            self.inner_radius - 5,
        )

    def draw_pointer(self):
        pointer = [
            (self.center_x, self.center_y - self.radius - 20),
            (self.center_x - 20, self.center_y - self.radius - 60),
            (self.center_x + 20, self.center_y - self.radius - 60),
        ]
        pygame.draw.polygon(self.screen, pygame.Color("black"), pointer)
        pygame.draw.polygon(self.screen, pygame.Color("grey"), pointer, 1)

    def draw_roulette_with_blur(self, angle=0):
        blurred_screen = self.screen.copy()
        self.draw_roulette(angle)
        self.screen.blit(blurred_screen, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.screen.fill(
                pygame.Color("white")
            )  # Clear the screen with white before starting
            self.draw_roulette()
            self.draw_pointer()

            pygame.display.update()
            time.sleep(1)
            self.roulette_sound.play()

            current_angle = 0
            start_time = time.time()
            
            self.roulette_sound.play(loops=-1)

            while time.time() - start_time < 3:
                # Clear only the area behind the roulette
                clear_rect = pygame.Rect(
                    self.center_x - self.radius - 20,
                    self.center_y - self.radius - 20,
                    (self.radius + 20) * 2,
                    (self.radius + 20) * 2,
                )
                pygame.draw.rect(self.screen, pygame.Color("white"), clear_rect)
                pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect, 10)
                self.draw_roulette_with_blur(current_angle)
                self.draw_pointer()

                # Increment the angle to simulate rotation
                current_angle += 15  # Adjust this value for faster/slower spinning
                current_angle %= 360

                pygame.display.update()
                time.sleep(0.05)  # Reduce sleep time for faster update

            # Continue spinning for random time within 1 second
            additional_time = random.uniform(0.1, 2.0)
            end_time = time.time() + additional_time

            while time.time() < end_time:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False

                clear_rect = pygame.Rect(
                    self.center_x - self.radius - 20,
                    self.center_y - self.radius - 20,
                    (self.radius + 20) * 2,
                    (self.radius + 20) * 2,
                )
                pygame.draw.rect(self.screen, pygame.Color("white"), clear_rect)
                pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect, 10)

                self.draw_roulette(current_angle)
                self.draw_pointer()

                # Increment the angle to simulate rotation
                current_angle += 10  # Adjust this value for faster/slower spinning
                current_angle %= 360

                pygame.display.update()
                time.sleep(0.05)  # Reduce sleep time for faster update

            # Calculate the final stopping section
            final_section = int(
                (current_angle // (360 / self.sections)) % self.sections
            )

            # Blink the final value for 1.5 seconds
            blink_duration = 1.5
            blink_interval = 0.25  # Blinking interval
            end_blink_time = time.time() + blink_duration
            
            self.roulette_sound.stop()
            self.roulette_end_sound.play()

            while time.time() < end_blink_time:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False

                clear_rect = pygame.Rect(
                    self.center_x - self.radius - 20,
                    self.center_y - self.radius - 20,
                    (self.radius + 20) * 2,
                    (self.radius + 20) * 2,
                )
                pygame.draw.rect(self.screen, pygame.Color("white"), clear_rect)
                pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect, 10)

                # Draw the final state of the roulette
                self.draw_roulette(current_angle)
                self.draw_pointer()

                # Blink the final value in the inner circle
                if int(time.time() * 2) % 2 == 0:
                    final_value_text = self.roulette_font.render(
                        str(self.values[final_section]), True, pygame.Color("black")
                    )
                    final_value_rect = final_value_text.get_rect(
                        center=(self.center_x, self.center_y)
                    )
                    self.screen.blit(final_value_text, final_value_rect)

                pygame.display.update()
                time.sleep(blink_interval / 2)  # Half interval to control the blink

            # Display the final value in the center
            clear_rect = pygame.Rect(
                self.center_x - self.radius - 20,
                self.center_y - self.radius - 20,
                (self.radius + 20) * 2,
                (self.radius + 20) * 2,
            )
            pygame.draw.rect(self.screen, pygame.Color("white"), clear_rect)
            pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect, 10)

            final_value_text = self.roulette_font.render(
                str(self.values[final_section]), True, pygame.Color("black")
            )
            final_value_rect = final_value_text.get_rect(
                center=(self.center_x, self.center_y)
            )
            self.screen.blit(final_value_text, final_value_rect)
            pygame.display.update()

            return self.values[final_section]
