import pygame
from src.constants import GRAY, BLACK
import os


class Menu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.selected_option = 0
        self.menu_options = [
            {
                "name": "Mode de jeu",
                "value": "Normal",
                "values": ["Normal", "Grenouille", "Bouteille"],
            },
            {"name": "Score", "value": 400, "min": 400, "max": 10000, "step": 200},
            {"name": "Equipe", "value": "Seul", "values": ["Seul", "Duo", "Equipe"]},
            {
                "name": "Nombre de joueurs",
                "value": 1,
                "min": 1,
                "max": 12,
                "step": 1,
            },
        ]
        # Construct the relative path to the background image
        background_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "images", "option_background.png"
        )

        # Debugging: Check if the file exists
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"No such file: {background_path}")

        # Load the image
        self.menu_background = pygame.image.load(background_path)

        # Scale the background image to fit the screen size
        self.menu_background = pygame.transform.scale(
            self.menu_background, self.screen.get_size()
        )

    def draw(self):
        self.screen.blit(self.menu_background, (0, 0))  # Draw the background image

        # Draw the options
        box_width = 400
        box_height = 100
        margin_x = 20
        margin_y = 20
        start_x = 50
        start_y = 150

        for i, option in enumerate(self.menu_options):
            color = (
                pygame.Color("blue")
                if i == self.selected_option
                else pygame.Color("darkblue")
            )
            # Calculate position
            x = start_x + (i % 2) * (box_width + margin_x)
            y = start_y + (i // 2) * (box_height + margin_y)
            # Draw rectangle
            pygame.draw.rect(
                self.screen, color, (x, y, box_width, box_height), border_radius=10
            )
            # Render text
            name_text = self.font.render(option["name"], True, pygame.Color("white"))
            value_text = self.font.render(
                str(option["value"]), True, pygame.Color("yellow")
            )
            # Blit text
            self.screen.blit(name_text, (x + 20, y + 20))
            self.screen.blit(value_text, (x + 20, y + 60))

        pygame.display.flip()

    def handle_button_press(self, button):
        option = self.menu_options[self.selected_option]

        if button == "UP":
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif button == "DOWN":
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif button == "LEFT":
            if "values" in option:
                current_index = option["values"].index(option["value"])
                option["value"] = option["values"][
                    (current_index - 1) % len(option["values"])
                ]
            else:
                option["value"] = max(option["min"], option["value"] - option["step"])

            if option["name"] == "Equipe":
                self.update_player_selection(option)
            elif (
                option["name"] == "Nombre d'équipes"
                or option["name"] == "Joueurs / équipe"
            ):
                self.set_max_plaxer_in_team(option)

        elif button == "RIGHT":
            if "values" in option:
                current_index = option["values"].index(option["value"])
                option["value"] = option["values"][
                    (current_index + 1) % len(option["values"])
                ]
            else:
                option["value"] = min(option["max"], option["value"] + option["step"])

            if option["name"] == "Equipe":
                self.update_player_selection(option)
            elif (
                option["name"] == "Nombre d'équipes"
                or option["name"] == "Joueurs / équipe"
            ):
                self.set_max_plaxer_in_team(option)

    def remove_menu_option(self, option_name):
        for idx, option in enumerate(self.menu_options):
            if option["name"] == option_name:
                del self.menu_options[idx]
                break

    def update_player_selection(self, option):
        if option["value"] == "Seul":
            self.menu_options.insert(
                3,
                {
                    "name": "Nombre de joueurs",
                    "value": 1,
                    "min": 1,
                    "max": 12,
                    "step": 1,
                },
            )
            self.remove_menu_option("Nombre d'équipes")
            self.remove_menu_option("Joueurs / équipe")
            self.remove_menu_option("Nombre de Duo")
        elif option["value"] == "Duo":
            self.menu_options.insert(
                3,
                {
                    "name": "Nombre de Duo",
                    "value": 1,
                    "min": 1,
                    "max": 6,
                    "step": 1,
                },
            )
            self.remove_menu_option("Nombre d'équipes")
            self.remove_menu_option("Joueurs / équipe")
            self.remove_menu_option("Nombre de joueurs")
        elif option["value"] == "Equipe":
            self.menu_options.insert(
                3,
                {
                    "name": "Nombre d'équipes",
                    "value": 2,
                    "min": 2,
                    "max": 6,
                    "step": 1,
                },
            )
            self.menu_options.insert(
                4,
                {
                    "name": "Joueurs / équipe",
                    "value": 2,
                    "min": 2,
                    "max": 6,
                    "step": 1,
                },
            )
            self.remove_menu_option("Nombre de Duo")
            self.remove_menu_option("Nombre de joueurs")

    def set_max_plaxer_in_team(self, option_selected):
        player_in_team = next(
            option
            for option in self.menu_options
            if option["name"] == "Joueurs / équipe"
        )["value"]
        number_of_team = next(
            option
            for option in self.menu_options
            if option["name"] == "Nombre d'équipes"
        )["value"]
        if player_in_team * number_of_team > 12:
            for option in self.menu_options:
                if option["name"] == option_selected["name"]:
                    option["value"] = option["value"] - 1
                    break

    def get_num_players(self):
        return self.menu_options[3]["value"]

    def get_team_mode(self):
        return self.menu_options[2]["value"]

    def get_score(self):
        return self.menu_options[1]["value"]

    def get_game_mode(self):
        return self.menu_options[0]["value"]

    def get_num_pairs(self):
        for option in self.menu_options:
            if option["name"] == "Nombre de Duo":
                return option["value"]
        return 1

    def get_num_teams(self):
        for option in self.menu_options:
            if option["name"] == "Nombre d'équipes":
                return option["value"]
        return 1

    def get_players_per_team(self):
        for option in self.menu_options:
            if option["name"] == "Joueurs / équipe":
                return option["value"]
        return 1
