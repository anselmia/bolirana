import os
import pygame

from src.constants import (
    ACTION_NEXT,
    ACTION_RIGHT,
    CHALLENGE_ARCADE,
    CHALLENGE_CLASSIC,
    CHALLENGE_ORDER,
    CHALLENGE_TIME_ATTACK,
    DEFAULT_TIME_ATTACK_SECONDS,
    DEFAULT_TIME_ATTACK_TURNS,
    MODE_NORMAL,
    MODE_FROG,
    MODE_BOTTLE,
    TEAM_MODE_SOLO,
    TEAM_MODE_DUO,
    TEAM_MODE_TEAM,
    OFF,
    ON,
)


OPTION_GAME_MODE = "Mode de jeu"
OPTION_SCORE = "Score"
OPTION_PENALTY = "Pénalité"
OPTION_CHALLENGE = "Challenge"
OPTION_TEAM_MODE = "Mode équipe"
OPTION_NUM_PLAYERS = "Nombre de joueurs"
OPTION_NUM_DUOS = "Nombre de Duo"
OPTION_NUM_TEAMS = "Nombre d'équipes"
OPTION_PLAYERS_PER_TEAM = "Joueurs / équipe"
OPTION_TIME_ATTACK_SECONDS = "Chrono / tour"
OPTION_TIME_ATTACK_TURNS = "Tours chrono"


class Menu:
    FROG_SOUND_MAXTIME_MS = 320

    def __init__(self):
        self.selected_option = 0
        self.values = {
            OPTION_GAME_MODE: MODE_NORMAL,
            OPTION_SCORE: 400,
            OPTION_PENALTY: OFF,
            OPTION_CHALLENGE: CHALLENGE_CLASSIC,
            OPTION_TEAM_MODE: TEAM_MODE_SOLO,
            OPTION_NUM_PLAYERS: 1,
            OPTION_NUM_DUOS: 2,
            OPTION_NUM_TEAMS: 2,
            OPTION_PLAYERS_PER_TEAM: 2,
            OPTION_TIME_ATTACK_SECONDS: DEFAULT_TIME_ATTACK_SECONDS,
            OPTION_TIME_ATTACK_TURNS: DEFAULT_TIME_ATTACK_TURNS,
        }
        self.options = []
        self.sync_options()

        self.frog_sound = self.load_sound("sounds", "frog.mp3")

    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        return pygame.mixer.Sound(path)

    def play_frog_sound(self):
        self.frog_sound.stop()
        self.frog_sound.play(maxtime=self.FROG_SOUND_MAXTIME_MS, fade_ms=20)

    def handle_button_press(self, button):
        option = self.options[self.selected_option]
        self.play_frog_sound()
        if button == ACTION_NEXT:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif button == ACTION_RIGHT:
            self.cycle_option_value(option)
            self.normalize_values(option["name"])
            self.sync_options()

    def build_option(self, name, **kwargs):
        option = {"name": name, "value": self.values[name]}
        option.update(kwargs)
        return option

    def sync_options(self):
        self.options = [
            self.build_option(
                OPTION_GAME_MODE,
                values=[MODE_NORMAL, MODE_FROG, MODE_BOTTLE],
            ),
            self.build_option(OPTION_PENALTY, values=[OFF, ON]),
            self.build_option(
                OPTION_CHALLENGE,
                values=[
                    CHALLENGE_CLASSIC,
                    CHALLENGE_ARCADE,
                    CHALLENGE_ORDER,
                    CHALLENGE_TIME_ATTACK,
                ],
            ),
        ]

        challenge_mode = self.values[OPTION_CHALLENGE]
        if challenge_mode in {CHALLENGE_CLASSIC, CHALLENGE_ARCADE}:
            self.options.append(
                self.build_option(OPTION_SCORE, min=400, max=10000, step=200)
            )
        elif challenge_mode == CHALLENGE_TIME_ATTACK:
            self.options.append(
                self.build_option(
                    OPTION_TIME_ATTACK_SECONDS,
                    min=10,
                    max=60,
                    step=5,
                )
            )
            self.options.append(
                self.build_option(
                    OPTION_TIME_ATTACK_TURNS,
                    min=2,
                    max=15,
                    step=1,
                )
            )

        self.options.extend(
            [
                self.build_option(
                    OPTION_TEAM_MODE,
                    values=[TEAM_MODE_SOLO, TEAM_MODE_DUO, TEAM_MODE_TEAM],
                ),
            ]
        )

        team_mode = self.values[OPTION_TEAM_MODE]
        if team_mode == TEAM_MODE_SOLO:
            self.options.append(
                self.build_option(OPTION_NUM_PLAYERS, min=1, max=12, step=1)
            )
        elif team_mode == TEAM_MODE_DUO:
            self.options.append(
                self.build_option(OPTION_NUM_DUOS, min=2, max=6, step=1)
            )
        else:
            self.options.append(
                self.build_option(OPTION_NUM_TEAMS, min=2, max=6, step=1)
            )
            self.options.append(
                self.build_option(OPTION_PLAYERS_PER_TEAM, min=2, max=6, step=1)
            )

        self.selected_option = min(self.selected_option, len(self.options) - 1)

    def cycle_option_value(self, option):
        if "values" in option:
            current_index = option["values"].index(option["value"])
            self.values[option["name"]] = option["values"][
                (current_index + 1) % len(option["values"])
            ]
            return

        self.values[option["name"]] = min(
            option["max"],
            option["value"] + option["step"],
        )

    def normalize_values(self, changed_option_name):
        self.values[OPTION_TIME_ATTACK_SECONDS] = min(
            60, max(10, self.values[OPTION_TIME_ATTACK_SECONDS])
        )
        self.values[OPTION_TIME_ATTACK_TURNS] = min(
            15, max(2, self.values[OPTION_TIME_ATTACK_TURNS])
        )

        team_mode = self.values[OPTION_TEAM_MODE]
        if team_mode == TEAM_MODE_SOLO:
            self.values[OPTION_NUM_PLAYERS] = min(
                12, max(1, self.values[OPTION_NUM_PLAYERS])
            )
            return

        if team_mode == TEAM_MODE_DUO:
            self.values[OPTION_NUM_DUOS] = min(6, max(2, self.values[OPTION_NUM_DUOS]))
            return

        num_teams = min(6, max(2, self.values[OPTION_NUM_TEAMS]))
        players_per_team = min(6, max(2, self.values[OPTION_PLAYERS_PER_TEAM]))

        while num_teams * players_per_team > 12:
            if changed_option_name == OPTION_NUM_TEAMS and num_teams > 2:
                num_teams -= 1
            elif players_per_team > 2:
                players_per_team -= 1
            elif num_teams > 2:
                num_teams -= 1
            else:
                break

        self.values[OPTION_NUM_TEAMS] = num_teams
        self.values[OPTION_PLAYERS_PER_TEAM] = players_per_team

    def get_num_players(self):
        return int(self.values[OPTION_NUM_PLAYERS])

    def get_team_mode(self):
        return str(self.values[OPTION_TEAM_MODE])

    def get_score(self):
        return int(self.values[OPTION_SCORE])

    def get_game_mode(self):
        return str(self.values[OPTION_GAME_MODE])

    def get_challenge_mode(self):
        return str(self.values[OPTION_CHALLENGE])

    def get_num_pairs(self):
        return int(self.values[OPTION_NUM_DUOS])

    def get_num_teams(self):
        return int(self.values[OPTION_NUM_TEAMS])

    def get_penalty(self):
        return str(self.values[OPTION_PENALTY])

    def get_players_per_team(self):
        return int(self.values[OPTION_PLAYERS_PER_TEAM])

    def get_time_attack_seconds(self):
        return int(self.values[OPTION_TIME_ATTACK_SECONDS])

    def get_time_attack_turns(self):
        return int(self.values[OPTION_TIME_ATTACK_TURNS])
