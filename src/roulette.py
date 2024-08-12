import pygame
import random
import time
import os
import math
from pygame.locals import *

# Define the solid gold color
GOLD_COLOR = (255, 215, 0)
DARK_GOLD_COLOR = (184, 134, 11)
LIGHT_GOLD_COLOR = (255, 239, 153)


class RouletteAnimation:
    def __init__(self, screen, type):
        self.screen = screen
        self.clock = pygame.time.Clock()

        screen_width, screen_height = self.screen.get_size()
        self.center_x, self.center_y = screen_width // 2, screen_height // 2

        self.sections = 8
        self.radius = 250
        self.inner_radius = 50
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
            self.values = [10, 50, 40, 20, 10, 50, 40, 20]

        self.font = pygame.font.Font(None, 80)
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

    def draw_gradient_section(self, start_angle, end_angle, color1, color2):
        steps = 100
        for i in range(steps):
            angle = start_angle + (end_angle - start_angle) * (i / steps)
            r = int(color1.r + (color2.r - color1.r) * (i / steps))
            g = int(color1.g + (color2.g - color1.g) * (i / steps))
            b = int(color1.b + (color2.b - color1.b) * (i / steps))
            pygame.draw.polygon(
                self.screen,
                (r, g, b),
                [
                    (self.center_x, self.center_y),
                    (
                        self.center_x + self.radius * math.cos(math.radians(angle)),
                        self.center_y + self.radius * math.sin(math.radians(angle)),
                    ),
                    (
                        self.center_x
                        + self.radius
                        * math.cos(
                            math.radians(angle + (end_angle - start_angle) / steps)
                        ),
                        self.center_y
                        + self.radius
                        * math.sin(
                            math.radians(angle + (end_angle - start_angle) / steps)
                        ),
                    ),
                ],
            )

    def draw_roulette(self, angle):
        # Draw the dark grey background circle to make it visible against black
        pygame.draw.circle(
            self.screen,
            pygame.Color("darkgrey"),
            (self.center_x, self.center_y),
            self.radius + 10,
        )

        # Offset the angle 0 to the top position
        angle -= 90
        angle %= 360

        # Draw the main roulette sections with gradient shading
        for i in range(self.sections):
            start_angle = (360 / self.sections) * i + angle - (360 / self.sections / 2)
            end_angle = start_angle + (360 / self.sections)
            self.draw_gradient_section(
                start_angle,
                end_angle,
                pygame.Color("gold"),
                pygame.Color("darkgoldenrod"),
            )
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

            angle_offset = angle + (360 / self.sections) * i
            x = self.center_x + (self.radius * 0.7) * math.cos(
                math.radians(angle_offset)
            )
            y = self.center_y + (self.radius * 0.7) * math.sin(
                math.radians(angle_offset)
            )

            # Render the text
            text_surface = self.font.render(
                str(self.values[i]), True, pygame.Color("black")
            )
            text_surface_rotated = pygame.transform.rotate(text_surface, -angle_offset)
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
            self.inner_radius - 1,
        )

    def draw_pointer(self):
        pointer = [
            (self.center_x, self.center_y - self.radius - 20),
            (self.center_x - 20, self.center_y - self.radius - 60),
            (self.center_x + 20, self.center_y - self.radius - 60),
        ]
        pygame.draw.polygon(self.screen, pygame.Color("black"), pointer)
        pygame.draw.polygon(self.screen, pygame.Color("grey"), pointer, 1)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.screen.fill(
                pygame.Color("black")
            )  # Clear the screen with black before
            current_angle = 0
            self.draw_roulette(current_angle)
            self.draw_pointer()

            pygame.display.update()
            time.sleep(1)
            self.roulette_sound.play()
            turns = 2
            actual_turns = 0
            angle_in_turn = current_angle
            self.roulette_sound.play(loops=-1)
            angular_speed = 15

            while actual_turns < turns:
                current_angle += angular_speed
                angle_in_turn += angular_speed
                current_angle %= 360
                angle_in_turn %= 360

                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False

                clear_rect = pygame.Rect(
                    self.center_x - self.radius - 20,
                    self.center_y - self.radius - 20,
                    (self.radius + 20) * 2,
                    (self.radius + 20) * 2,
                )
                pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect)

                self.draw_roulette(current_angle)
                self.draw_pointer()

                if angle_in_turn == 0:
                    actual_turns += 1

                pygame.display.update()
                time.sleep(0.05)
                self.clock.tick(30)

            additional_section = random.randint(0, self.sections - 1)
            current_section = 0
            i = 0

            while current_section < additional_section:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                i += 1
                current_angle += angular_speed
                current_angle %= 360
                if i == 3:
                    current_section += 1
                    i = 0

                clear_rect = pygame.Rect(
                    self.center_x - self.radius - 20,
                    self.center_y - self.radius - 20,
                    (self.radius + 20) * 2,
                    (self.radius + 20) * 2,
                )
                pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect)

                self.draw_roulette(current_angle)
                self.draw_pointer()

                pygame.display.update()
                time.sleep(0.05)

            # Blink the final value for 1.5 seconds
            blink_duration = 1.5
            blink_interval = 0.25  # Blinking interval
            end_blink_time = time.time() + blink_duration

            self.roulette_sound.stop()
            self.roulette_end_sound.play()

            # Translate current section as per positive rotation
            current_section = 0 - current_section
            current_section %= 8

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
                pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect)

                self.draw_roulette(current_angle)
                self.draw_pointer()

                if int(time.time() * 2) % 2 == 0:
                    final_value_text = self.font.render(
                        str(self.values[current_section]),
                        True,
                        pygame.Color("black"),
                    )
                    final_value_rect = final_value_text.get_rect(
                        center=(self.center_x, self.center_y)
                    )
                    self.screen.blit(final_value_text, final_value_rect)

                pygame.display.update()
                time.sleep(blink_interval / 2)

            # Display the final value in the center
            clear_rect = pygame.Rect(
                self.center_x - self.radius - 20,
                self.center_y - self.radius - 20,
                (self.radius + 20) * 2,
                (self.radius + 20) * 2,
            )
            pygame.draw.rect(self.screen, pygame.Color("black"), clear_rect)

            self.draw_roulette(current_angle)
            self.draw_pointer()

            final_value_text = self.font.render(
                str(self.values[current_section]), True, pygame.Color("black")
            )
            final_value_rect = final_value_text.get_rect(
                center=(self.center_x, self.center_y)
            )
            self.screen.blit(final_value_text, final_value_rect)
            pygame.display.update()

            return self.values[current_section]
