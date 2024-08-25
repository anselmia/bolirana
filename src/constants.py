import pygame
import os

# Define colors
DARK_GREEN = pygame.Color(34, 139, 34)  # Dark green
DARK_RED = pygame.Color(128, 0, 0)
LIGHT_GREEN = pygame.Color(144, 238, 144)  # Light green
DARK_ORANGE = pygame.Color(255, 140, 0)  # Gold
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
PLAYER_OPTION_COLOR = pygame.Color(245, 237, 214)


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

GOLD_SOLID = [
    (255, 215, 0),  # Gold
    (255, 223, 34),
    (255, 231, 68),
    (255, 239, 102),
    (255, 247, 136),
]

CHROME_SOLID = [
    (169, 169, 169),  # Dark gray
    (192, 192, 192),  # Silver
    (211, 211, 211),  # Light gray
    (220, 220, 220),
    (230, 230, 230),
]

# Define pin

PIN_H20 = [4, 5]
PIN_H25 = [18, 32]
PIN_H40 = [13, 14]
PIN_H50 = [15, 16]
PIN_H100 = [17, 25]
PIN_HBOTTLE = [23, 26]
PIN_HSFROG = [27]
PIN_HLFROG = [33]
PIN_BNEXT = 34
PIN_BENTER = 19
PIN_UP = 39
PIN_DOWN = 2
PIN_LEFT = 18
PIN_RIGHT = 12
PIN_STATES_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "pin_states.json")

# Defines Holes

HOLE_RADIUS = 30
BLINK_INTERVAL = 0.2

# Game Logic

FPS = 30
ACTION_COOLDOWN = 3
BLINK_INTERVAL = 0.2
