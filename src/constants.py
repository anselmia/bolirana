import pygame
import os

# Display
SCREEN_SIZE = (1024, 768)

# Define colors
DARK_GREEN = pygame.Color(34, 139, 34)  # Dark green
DARK_RED = pygame.Color(128, 0, 0)
LIGHT_GREEN = pygame.Color(144, 238, 144)  # Light green
DARK_YELLOW = pygame.Color(255, 215, 0)  # Gold
LIGHT_GREY = pygame.Color(245, 245, 245)  # Light grey for background
DARK_GREY = pygame.Color(50, 50, 50)  # Dark grey for text
LIGHT_BLUE = pygame.Color(173, 216, 230)  # Light blue
RANK_COLOR = pygame.Color(255, 165, 0)  # Soft orange for rank box
LIGHT_PINK = (pygame.Color(255, 182, 193),)  # Light pink
PEACH_PUFF = (pygame.Color(255, 218, 185),)  # Peach puff
DARK_BLUE = pygame.Color("darkblue")
BLUE = pygame.Color("blue")
WHITE = pygame.Color("white")
YELLOW = pygame.Color("yellow")
BLACK = pygame.Color(0, 0, 0)
MAGENTA = pygame.Color("magenta")
RED = pygame.Color("red")
GROUP_COLORS = [
    pygame.Color(85, 130, 250),
    pygame.Color(250, 85, 85),
    pygame.Color(85, 250, 85),
    pygame.Color(250, 250, 85),
    pygame.Color(250, 85, 250),
]


CHROME_COLORS = [
    pygame.Color(192, 192, 192),
    pygame.Color(128, 128, 128),
    pygame.Color(255, 255, 255),
]
GOLD_COLORS = [
    pygame.Color(255, 215, 0),  # Light gold
    pygame.Color(218, 165, 32),  # Goldenrod
    pygame.Color(184, 134, 11),  # Dark goldenrod
]

RED_COLORS = [
    pygame.Color(255, 69, 0),  # Light red (OrangeRed)
    pygame.Color(220, 20, 60),  # Crimson
    pygame.Color(139, 0, 0),  # Dark red (DarkRed)
]

# Define pin

PIN_H20 = 4
PIN_H25 = 5
PIN_H40 = 13
PIN_H50 = 14
PIN_H100 = 17
PIN_HBOTTLE = 18
PIN_HSFROG = 19
PIN_HLFROG = 21
PIN_BNEXT = 22
PIN_BENTER = 23
PIN_UP = 25
PIN_DOWN = 26
PIN_LEFT = 27
PIN_RIGHT = 32
PIN_STATES_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "pin_states.json")

# Defines Holes

HOLE_RADIUS = 30
BLINK_INTERVAL = 0.2

# Game Logic

FPS = 60
ACTION_COOLDOWN = 3
