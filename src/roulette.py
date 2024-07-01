import pygame
import random
import sys
import time
import os
from pygame.locals import *
from src.constants import *


class RouletteAnimation:
    def __init__(self, screen, type):
        self.screen = screen
        self.clock = pygame.time.Clock()

        screen_width, screen_height = self.screen.get_size()
        center_x, center_y = screen_width // 2, screen_height // 2

        self.posx = [
            center_x + 75,
            center_x + 170,
            center_x + 170,
            center_x + 75,
            center_x - 75,
            center_x - 170,
            center_x - 170,
            center_x - 75,
        ]
        self.posy = [
            center_y - 170,
            center_y - 70,
            center_y + 65,
            center_y + 170,
            center_y + 170,
            center_y + 65,
            center_y - 70,
            center_y - 170,
        ]

        if type == "frog":
            self.posibles = [300, 350, 400, 450, 300, 350, 400, 450]
        else:
            self.posibles = [10, 20, 40, 50, 10, 20, 40, 50]
        self.vivo = [GREEN, BLUE, RED, MAGENTA, GREEN, BLUE, RED, MAGENTA]
        self.muerto = [
            GREENDARK,
            BLUEDARK,
            REDDARK,
            MAGENTADARK,
            GREENDARK,
            BLUEDARK,
            REDDARK,
            MAGENTADARK,
        ]

        self.ruletaFont = pygame.font.Font(None, 165)
        self.posiblesFont = pygame.font.Font(None, 80)

        self.radio = 65
        self.ajustx = 48
        self.ajusty = 30

        self.roulette_sound = pygame.mixer.Sound(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "sounds",
                "roulette.mp3",
            )
        )

    def run(self):
        while True:
            self.screen.fill((0, 0, 0))  # Clear the screen

            pygame.draw.circle(
                self.screen,
                ORANGE2,
                [self.screen.get_width() // 2, self.screen.get_height() // 2],
                250,
            )
            pygame.draw.circle(
                self.screen,
                BLUE3,
                [self.screen.get_width() // 2, self.screen.get_height() // 2],
                100,
            )
            for i in range(8):
                pygame.draw.circle(
                    self.screen,
                    self.muerto[i],
                    [self.posx[i], self.posy[i]],
                    self.radio,
                )
                text_surface = self.posiblesFont.render(
                    str(self.posibles[i]), True, WHITE
                )
                text_rect = text_surface.get_rect(center=(self.posx[i], self.posy[i]))
                self.screen.blit(text_surface, text_rect)

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
                        self.vivo[j],
                        [self.posx[j], self.posy[j]],
                        self.radio,
                    )
                    text_surface = self.posiblesFont.render(
                        str(self.posibles[j]), True, WHITE
                    )
                    text_rect = text_surface.get_rect(
                        center=(self.posx[j], self.posy[j])
                    )
                    self.screen.blit(text_surface, text_rect)

                    if j != 0:
                        pygame.draw.circle(
                            self.screen,
                            self.muerto[j - 1],
                            [self.posx[j - 1], self.posy[j - 1]],
                            self.radio,
                        )
                        text_surface = self.posiblesFont.render(
                            str(self.posibles[j - 1]), True, WHITE
                        )
                        text_rect = text_surface.get_rect(
                            center=(self.posx[j - 1], self.posy[j - 1])
                        )
                        self.screen.blit(text_surface, text_rect)
                    else:
                        pygame.draw.circle(
                            self.screen,
                            self.muerto[7],
                            [self.posx[7], self.posy[7]],
                            self.radio,
                        )
                        text_surface = self.posiblesFont.render(
                            str(self.posibles[7]), True, WHITE
                        )
                        text_rect = text_surface.get_rect(
                            center=(self.posx[7], self.posy[7])
                        )
                        self.screen.blit(text_surface, text_rect)

                    pygame.display.update()
                    time.sleep(0.1)

            for k in range(rand):
                pygame.draw.circle(
                    self.screen, self.vivo[k], [self.posx[k], self.posy[k]], self.radio
                )
                text_surface = self.posiblesFont.render(
                    str(self.posibles[k]), True, WHITE
                )
                text_rect = text_surface.get_rect(center=(self.posx[k], self.posy[k]))
                self.screen.blit(text_surface, text_rect)
                if k != 0:
                    pygame.draw.circle(
                        self.screen,
                        self.muerto[k - 1],
                        [self.posx[k - 1], self.posy[k - 1]],
                        self.radio,
                    )
                    text_surface = self.posiblesFont.render(
                        str(self.posibles[k - 1]), True, WHITE
                    )
                    text_rect = text_surface.get_rect(
                        center=(self.posx[k - 1], self.posy[k - 1])
                    )
                    self.screen.blit(text_surface, text_rect)
                else:
                    pygame.draw.circle(
                        self.screen,
                        self.muerto[7],
                        [self.posx[7], self.posy[7]],
                        self.radio,
                    )
                    text_surface = self.posiblesFont.render(
                        str(self.posibles[7]), True, WHITE
                    )
                    text_rect = text_surface.get_rect(
                        center=(self.posx[7], self.posy[7])
                    )
                    self.screen.blit(text_surface, text_rect)

                pygame.display.update()
                time.sleep(0.2)

            pygame.draw.circle(
                self.screen,
                self.vivo[rand - 1],
                [self.posx[rand - 1], self.posy[rand - 1]],
                self.radio,
            )
            text_surface = self.posiblesFont.render(
                str(self.posibles[rand - 1]), True, WHITE
            )
            text_rect = text_surface.get_rect(
                center=(self.posx[rand - 1], self.posy[rand - 1])
            )
            self.screen.blit(text_surface, text_rect)
            final_value_text = self.ruletaFont.render(
                str(self.posibles[rand - 1]), True, MANGOBICHE
            )
            final_value_rect = final_value_text.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
            )
            self.screen.blit(final_value_text, final_value_rect)

            pygame.display.update()
            time.sleep(2)

            return self.posibles[rand - 1]
