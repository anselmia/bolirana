import pygame

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
PIN_H100 = [25, 17]
PIN_HBOTTLE = [23, 26]
PIN_HSFROG = [27]
PIN_HLFROG = [33]
PIN_BNEXT = 0
PIN_BENTER = 19
PIN_RIGHT = 12

KEY_TO_PIN_MAP = {
    pygame.K_DOWN: PIN_BNEXT,
    pygame.K_RIGHT: PIN_RIGHT,
    pygame.K_RETURN: PIN_BENTER,
    pygame.K_q: PIN_H20[0],
    pygame.K_s: PIN_H25[0],
    pygame.K_d: PIN_H40[0],
    pygame.K_f: PIN_H50[0],
    pygame.K_g: PIN_H100[0],
    pygame.K_h: PIN_HBOTTLE[0],
    pygame.K_j: PIN_HSFROG[0],
    pygame.K_k: PIN_HLFROG[0],
    pygame.K_w: PIN_H20[1],
    pygame.K_x: PIN_H25[1],
    pygame.K_c: PIN_H40[1],
    pygame.K_v: PIN_H50[1],
    pygame.K_b: PIN_H100[1],
    pygame.K_n: PIN_HBOTTLE[1],
}

ACTION_NEXT = "NEXT"
ACTION_RIGHT = "RIGHT"
ACTION_ENTER = "ENTER"

PIN_TO_ACTION_MAP = {
    PIN_BNEXT: ACTION_NEXT,
    PIN_RIGHT: ACTION_RIGHT,
    PIN_BENTER: ACTION_ENTER,
}

MODE_NORMAL = "NORMAL"
MODE_FROG = "FROG"
MODE_BOTTLE = "BOTTLE"
TEAM_MODE_SOLO = "SOLO"
TEAM_MODE_DUO = "DUO"
TEAM_MODE_TEAM = "TEAM"

ON = "ON"
OFF = "OFF"

# Defines Holes

HOLE_RADIUS = 30
BLINK_INTERVAL = 0.2

# Game Logic

FPS = 30
ACTION_COOLDOWN = 3
BLINK_INTERVAL = 0.2
