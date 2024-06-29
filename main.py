import os
os.environ["DISPLAY"] = ":0"

import pygame
import sys
from zeroconf import ServiceBrowser, Zeroconf
import time

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Bolirana Game')

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Set up fonts
font = pygame.font.Font(None, 36)

# Menu options and their ranges or values
menu_options = [
    {"name": "Nombre de joueur", "value": 1, "min": 1, "max": 8, "step": 1},
    {"name": "Score", "value": 400, "min": 400, "max": 10000, "step": 200},
    {"name": "Equipe", "value": "Seul", "values": ["Seul", "Paire", "Equipe"]},
    {"name": "Mode de jeu", "value": "Normal", "values": ["Normal", "Côté", "Bouteille"]}
]
selected_option = 0

# Draw the menu
def draw_menu():
    screen.fill(BLACK)
    for i, option in enumerate(menu_options):
        if i == selected_option:
            color = WHITE
        else:
            color = GRAY
        text = font.render(f"{option['name']}: {option['value']}", True, color)
        screen.blit(text, (250, 250 + i * 40))

# Handle button presses
def handle_button_press(button):
    global selected_option
    option = menu_options[selected_option]

    if button == "UP":
        selected_option = (selected_option - 1) % len(menu_options)
    elif button == "DOWN":
        selected_option = (selected_option + 1) % len(menu_options)
    elif button == "LEFT":
        if "values" in option:
            current_index = option["values"].index(option["value"])
            option["value"] = option["values"][(current_index - 1) % len(option["values"])]
        else:
            option["value"] = max(option["min"], option["value"] - option["step"])
    elif button == "RIGHT":
        if "values" in option:
            current_index = option["values"].index(option["value"])
            option["value"] = option["values"][(current_index + 1) % len(option["values"])]
        else:
            option["value"] = min(option["max"], option["value"] + option["step"])
    elif button == "ENTER":
        print("Starting game with settings:")
        for option in menu_options:
            print(f"{option['name']}: {option['value']}")
        # Here you would add logic to start the game

# mDNS Listener class
class MDNSListener:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.listener = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(f"Service {name} added, service info: {info}")

# Initialize MDNS Listener
mdns_listener = MDNSListener()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                handle_button_press("UP")
            elif event.key == pygame.K_DOWN:
                handle_button_press("DOWN")
            elif event.key == pygame.K_LEFT:
                handle_button_press("LEFT")
            elif event.key == pygame.K_RIGHT:
                handle_button_press("RIGHT")
            elif event.key == pygame.K_RETURN:
                handle_button_press("ENTER")

    # Placeholder for reading button inputs from mDNS (you need to implement this based on your ESP32 setup)
    # Example: button = read_mdns_button()
    # if button:
    #     handle_button_press(button)

    draw_menu()
    pygame.display.flip()

    time.sleep(0.1)  # Small delay to make the loop run smoothly

pygame.quit()
sys.exit()