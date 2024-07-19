import os
import pygame

class Menu:
    def __init__(self):

        self.selected_option = 0
        self.options = [
            {
                "name": "Mode de jeu",
                "value": "Normal",
                "values": ["Normal", "Grenouille", "Bouteille"],
            },
            {"name": "Score", "value": 400, "min": 400, "max": 10000, "step": 200},
            {
                "name": "Pénalité",
                "value": "Sans",
                "values": ["Sans", "Avec"],
            },
            {"name": "Equipe", "value": "Seul", "values": ["Seul", "Duo", "Equipe"]},
            {
                "name": "Nombre de joueurs",
                "value": 1,
                "min": 1,
                "max": 12,
                "step": 1,
            },
        ]

        self.frog_sound = self.load_sound(
                "sounds", "frog.mp3"
            )
        
    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        return pygame.mixer.Sound(path)

    def handle_button_press(self, button):
        option = self.options[self.selected_option]
        self.frog_sound.play()
        if button == "UP":
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif button == "DOWN":
            self.selected_option = (self.selected_option + 1) % len(self.options)
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
        for idx, option in enumerate(self.options):
            if option["name"] == option_name:
                del self.options[idx]
                break

    def update_player_selection(self, option):
        if option["value"] == "Seul":
            self.options.append(
                {
                    "name": "Nombre de joueurs",
                    "value": 1,
                    "min": 1,
                    "max": 12,
                    "step": 1,
                }
            )
            self.remove_menu_option("Nombre d'équipes")
            self.remove_menu_option("Joueurs / équipe")
            self.remove_menu_option("Nombre de Duo")
        elif option["value"] == "Duo":
            self.options.append(
                {
                    "name": "Nombre de Duo",
                    "value": 2,
                    "min": 2,
                    "max": 6,
                    "step": 1,
                },
            )
            self.remove_menu_option("Nombre d'équipes")
            self.remove_menu_option("Joueurs / équipe")
            self.remove_menu_option("Nombre de joueurs")
        elif option["value"] == "Equipe":
            self.options.append(
                {
                    "name": "Nombre d'équipes",
                    "value": 2,
                    "min": 2,
                    "max": 6,
                    "step": 1,
                },
            )
            self.options.append(
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
            option for option in self.options if option["name"] == "Joueurs / équipe"
        )["value"]
        number_of_team = next(
            option for option in self.options if option["name"] == "Nombre d'équipes"
        )["value"]
        if player_in_team * number_of_team > 12:
            for option in self.options:
                if option["name"] == option_selected["name"]:
                    option["value"] = option["value"] - 1
                    break

    def get_num_players(self):
        return self.options[4]["value"]

    def get_team_mode(self):
        return self.options[3]["value"]

    def get_score(self):
        return self.options[1]["value"]

    def get_game_mode(self):
        return self.options[0]["value"]

    def get_num_pairs(self):
        for option in self.options:
            if option["name"] == "Nombre de Duo":
                return option["value"]
        return 1

    def get_num_teams(self):
        for option in self.options:
            if option["name"] == "Nombre d'équipes":
                return option["value"]
        return 1

    def get_penalty(self):
        for option in self.options:
            if option["name"] == "Pénalité":
                return option["value"]
        return 1

    def get_players_per_team(self):
        for option in self.options:
            if option["name"] == "Joueurs / équipe":
                return option["value"]
        return 1
