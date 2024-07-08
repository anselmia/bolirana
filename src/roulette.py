import pygame
import random
import time
import os
import math
from pygame.locals import *
from src.constants import *


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

        self.font = pygame.font.Font(None, 40)
        self.roulette_font = pygame.font.Font(None, 80)

        self.roulette_sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "roulette.mp3",
            )
        )

    def draw_circle_with_border(self, center, radius, border_colors, border_width):
        """Draws a circle with a border effect."""
        for i in range(border_width):
            pygame.draw.circle(
                self.screen,
                border_colors[i % len(border_colors)],
                center,
                radius + i,
                width=1,
            )

    def draw_roulette(self):
        # Draw golden external border around the main big circle
        self.draw_circle_with_border(
            (self.center_x, self.center_y), self.radius, GOLD_COLORS, 10
        )

        # Draw the main roulette sections
        for i in range(self.sections):
            start_angle = (360 / self.sections) * i
            end_angle = start_angle + (360 / self.sections)
            pygame.draw.arc(
                self.screen,
                self.section_colors[i],
                (
                    self.center_x - self.radius,
                    self.center_y - self.radius,
                    self.radius * 2,
                    self.radius * 2,
                ),
                math.radians(start_angle),
                math.radians(end_angle),
                self.radius,
            )

        # Draw chrome border around the number circle
        self.draw_circle_with_border(
            (self.center_x, self.center_y), self.inner_radius, CHROME_COLORS, 10
        )

        # Draw the inner circle
        pygame.draw.circle(
            self.screen,
            pygame.Color("gray"),
            (self.center_x, self.center_y),
            self.inner_radius,
        )

        # Add values to the sections
        for i in range(self.sections):
            angle = (360 / self.sections) * i + (360 / self.sections) / 2
            x = self.center_x + (self.radius / 1.5) * math.cos(
                math.radians(angle)
            )
            y = self.center_y + (self.radius / 1.5) * math.sin(
                math.radians(angle)
            )
            text_surface = self.font.render(
                str(self.values[i]), True, pygame.Color("white")
            )
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)

        # Draw the spinner pointer
        pointer = [
            (self.center_x, self.center_y - self.radius - 20),
            (self.center_x - 20, self.center_y - self.radius + 20),
            (self.center_x + 20, self.center_y - self.radius + 20),
        ]
        pygame.draw.polygon(self.screen, GOLD_COLORS[0], pointer)

    def run(self):
        while True:
            self.screen.fill((0, 0, 0))  # Clear the screen

            self.draw_roulette()

            pygame.display.update()
            time.sleep(1)
            self.roulette_sound.play()

            rand = random.randint(0, 7)
            rand_6 = rand + 8
            rand_6_div_6 = rand_6 // 6

            for i in range(rand_6_div_6 + 1):
                for j in range(8):
                    pygame.draw.circle(
                        self.screen,
                        self.section_colors[j],
                        [self.center_x, self.center_y],
                        self.radius,
                    )
                    text_surface = self.font.render(
                        str(self.values[j]), True, pygame.Color("white")
                    )
                    text_rect = text_surface.get_rect(
                        center=(self.center_x, self.center_y)
                    )
                    self.screen.blit(text_surface, text_rect)

                    if j != 0:
                        pygame.draw.circle(
                            self.screen,
                            self.section_colors[j - 1],
                            [self.center_x, self.center_y],
                            self.radius,
                        )
                        text_surface = self.font.render(
                            str(self.values[j - 1]), True, pygame.Color("white")
                        )
                        text_rect = text_surface.get_rect(
                            center=(self.center_x, self.center_y)
                        )
                        self.screen.blit(text_surface, text_rect)
                    else:
                        pygame.draw.circle(
                            self.screen,
                            self.section_colors[7],
                            [self.center_x, self.center_y],
                            self.radius,
                        )
                        text_surface = self.font.render(
                            str(self.values[7]), True, pygame.Color("white")
                        )
                        text_rect = text_surface.get_rect(
                            center=(self.center_x, self.center_y)
                        )
                        self.screen.blit(text_surface, text_rect)

                    pygame.display.update()
                    time.sleep(0.1)

            for k in range(rand):
                pygame.draw.circle(
                    self.screen,
                    self.section_colors[k],
                    [self.center_x, self.center_y],
                    self.radius,
                )
                text_surface = self.font.render(
                    str(self.values[k]), True, pygame.Color("white")
                )
                text_rect = text_surface.get_rect(center=(self.center_x, self.center_y))
                self.screen.blit(text_surface, text_rect)
                if k != 0:
                    pygame.draw.circle(
                        self.screen,
                        self.section_colors[k - 1],
                        [self.center_x, self.center_y],
                        self.radius,
                    )
                    text_surface = self.font.render(
                        str(self.values[k - 1]), True, pygame.Color("white")
                    )
                    text_rect = text_surface.get_rect(
                        center=(self.center_x, self.center_y)
                    )
                    self.screen.blit(text_surface, text_rect)
                else:
                    pygame.draw.circle(
                        self.screen,
                        self.section_colors[7],
                        [self.center_x, self.center_y],
                        self.radius,
                    )
                    text_surface = self.font.render(
                        str(self.values[7]), True, pygame.Color("white")
                    )
                    text_rect = text_surface.get_rect(
                        center=(self.center_x, self.center_y)
                    )
                    self.screen.blit(text_surface, text_rect)

                pygame.display.update()
                time.sleep(0.2)

            pygame.draw.circle(
                self.screen,
                self.section_colors[rand - 1],
                [self.center_x, self.center_y],
                self.radius,
            )
            text_surface = self.font.render(
                str(self.values[rand - 1]), True, pygame.Color("white")
            )
            text_rect = text_surface.get_rect(center=(self.center_x, self.center_y))
            self.screen.blit(text_surface, text_rect)
            final_value_text = self.roulette_font.render(
                str(self.values[rand - 1]), True, pygame.Color("yellow")
            )
            final_value_rect = final_value_text.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
            )
            self.screen.blit(final_value_text, final_value_rect)

            pygame.display.update()
            time.sleep(2)

            return self.values[rand - 1]
