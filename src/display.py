import pygame
import os
import time
import logging
import sys
import math
from src.constants import (
    HOLE_RADIUS,
    CHROME_COLORS,
    RED_COLORS,
    GOLD_COLORS,
    BLUE,
    DARK_BLUE,
    YELLOW,
    WHITE,
    DARK_GREEN,
    DARK_ORANGE,
    DARK_GREY,
    LIGHT_GREY,
    BLACK,
    RED,
    GROUP_COLORS,
    BLINK_INTERVAL,
    PLAYER_OPTION_COLOR,
    TEAM_MODE_DUO,
    TEAM_MODE_SOLO,
    TEAM_MODE_TEAM,
)
import random
from src.firework import Firework
from src.roulette import RouletteAnimation
from PIL import Image


class Display:
    def __init__(self, debug):
        pygame.display.set_caption("Bolirana Game")
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if debug:
            self.screen = pygame.display.set_mode((1024, 768), flags)
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | flags)

        # Optionally, you can also set the window title
        font_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "fonts", "AntonSC-Regular.ttf"
        )
        self.font_large = pygame.font.Font(font_path, 50)
        self.font_medium = pygame.font.Font(font_path, 30)
        self.font_small = pygame.font.Font(font_path, 25)
        self.font_verysmall = pygame.font.Font(font_path, 20)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.half_width = self.screen_width // 2
        self.half_height = self.screen_height // 2
        self.third_width = self.screen_width // 3
        self.hole_rect_height = self.screen_height // 2.4
        self.resources = {}  # Cache resources
        self.load_ressources()
        self.roulette_animation = RouletteAnimation(
            self.screen,
            self.resources["roulette_sound"],
            self.resources["roulette_end_sound"],
        )

    def load_ressources(self):
        try:
            self.resources["game_background"] = self.load_image("images", "game3.jpg")
            self.resources["menu_background"] = self.load_image("images", "intro.jpg")
            self.resources["win_background"] = self.load_image("images", "win.jpg")
            self.resources["winner_banner"] = self.load_image("images", "winner.png")
            self.resources["penalty_frames"], self.resources["penalty_duration"] = (
                self.load_gif("gif", "fail.gif")
            )
            self.resources["penalty_sound"] = self.load_sound("sounds", "fail.mp3")
            self.resources["win_sound"] = self.load_sound("sounds", "victoire.mp3")
            self.resources["intro_sound"] = self.load_sound("sounds", "intro.mp3")
            self.resources["roulette_sound"] = self.load_sound("sounds", "roulette.mp3")
            self.resources["roulette_end_sound"] = self.load_sound(
                "sounds", "roulette_end.mp3"
            )
            (
                self.resources["large_frog_frames"],
                self.resources["large_frog_duration"],
            ) = self.load_gif("gif", "large_frog_animation.gif")
            self.resources["applause"] = self.load_sound("sounds", "aplaudissement.mp3")
            (
                self.resources["little_frog_frames"],
                self.resources["little_frog_duration"],
            ) = self.load_gif("gif", "small_frog_animation.gif")

            # Scale winner_banner once and store it
            self.resources["winner_banner"] = pygame.transform.scale(
                self.resources["winner_banner"], (50, 50)
            )

        except Exception as e:
            logging.error(f"Failed to load resources: {e}")
            self.display_error_message("Failed to load resources. Exiting...")
            pygame.quit()
            sys.exit()

    def load_image(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        if (folder, filename) not in self.resources:
            self.resources[(folder, filename)] = pygame.transform.scale(
                pygame.image.load(path), self.screen.get_size()
            )
        return self.resources[(folder, filename)]

    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        if (folder, filename) not in self.resources:
            self.resources[(folder, filename)] = pygame.mixer.Sound(path)
        return self.resources[(folder, filename)]

    def display_error_message(self, message):
        self.screen.fill((0, 0, 0))
        error_text = self.font_large.render(message, True, RED)
        self.screen.blit(
            error_text,
            (
                self.half_width - error_text.get_width() // 2,
                self.half_height,
            ),
        )
        pygame.display.flip()
        time.sleep(3)  # Display the message for 3 seconds

    def get_hole_position(self, hole_value, position):
        # Adjust the function to handle all cases and default return None
        if hole_value == "20":
            return (
                [(self.screen_width / 2) - 160, 255]
                if position == 1
                else [(self.screen_width / 2) + 160, 255]
            )
        elif hole_value == "25":
            return (
                [(self.screen_width / 2) - 160, 150]
                if position == 1
                else [(self.screen_width / 2) + 160, 155]
            )
        elif hole_value == "40":
            return (
                [(self.screen_width / 2) - 80, 205]
                if position == 1
                else [(self.screen_width / 2) + 80, 205]
            )
        elif hole_value == "50":
            return (
                [(self.screen_width / 2) - 80, 105]
                if position == 1
                else [(self.screen_width / 2) + 80, 105]
            )
        elif hole_value == "100":
            return (
                [(self.screen_width / 2) - 80, 305]
                if position == 1
                else [(self.screen_width / 2) + 80, 305]
            )
        elif hole_value == "150":
            return (
                [(self.screen_width / 2) - 160, 55]
                if position == 1
                else [(self.screen_width / 2) + 160, 55]
            )
        elif hole_value == "200":
            return [(self.screen_width / 2), 155]
        elif hole_value == "ROUL":
            return [(self.screen_width / 2), 55]
        return None

    def draw_chrome_rect(self, rect, colors, border_radius, width):
        """Draws a rounded rectangle with a chrome effect."""
        x, y, w, h = rect
        for i in range(width):
            pygame.draw.rect(
                self.screen,
                colors[i % len(colors)],
                (x - i, y - i, w + 2 * i, h + 2 * i),
                border_radius=border_radius - i if border_radius > i else 0,
                width=1,
            )

    def draw_text_with_outline(
        self,
        text,
        font,
        text_color,
        outline_color,
        position,
        outline_width=2,
        center=False,
    ):
        outline_font = pygame.font.Font(font, font.size + outline_width * 2)
        outline_text = outline_font.render(text, True, outline_color)
        outline_rect = outline_text.get_rect()
        if center:
            outline_rect.center = position
        else:
            outline_rect.topleft = position
        self.screen.blit(outline_text, outline_rect)

        actual_text = font.render(text, True, text_color)
        actual_rect = actual_text.get_rect()
        if center:
            actual_rect.center = outline_rect.center
        else:
            actual_rect.topleft = outline_rect.topleft
        self.screen.blit(actual_text, actual_rect)

    def draw_menu(self, menu):
        self.screen.blit(self.resources["menu_background"], (0, 0))

        # Menu options dimensions
        box_width, box_height, margin_x, margin_y = 400, 100, 20, 20
        border_radius, border_width = 15, 5

        # Transparency settings
        semi_transparent_blue, semi_transparent_darkblue = BLUE, DARK_BLUE
        semi_transparent_blue.a, semi_transparent_darkblue.a = 128, 128

        # Calculate the number of rows needed
        num_rows = (len(menu.options) + 1) // 2

        # Calculate total height of the menu
        total_height = num_rows * box_height + (num_rows - 1) * margin_y

        # Calculate starting positions to center the menu
        start_x = (self.screen.get_width() - (2 * box_width + margin_x)) // 2
        start_y = (self.screen.get_height() - total_height) // 2

        for i, option in enumerate(menu.options):
            color = (
                semi_transparent_blue
                if i == menu.selected_option
                else semi_transparent_darkblue
            )
            # Calculate position
            x, y = start_x + (i % 2) * (box_width + margin_x), start_y + (i // 2) * (
                box_height + margin_y
            )

            # Draw chrome effect rectangle
            self.draw_chrome_rect(
                (x, y, box_width, box_height),
                CHROME_COLORS,
                border_radius,
                border_width,
            )

            # Create a semi-transparent surface for the filled rectangle
            rect_surface = pygame.Surface(
                (box_width - 2 * border_width, box_height - 2 * border_width),
                pygame.SRCALPHA,
            )
            rect_surface = rect_surface.convert_alpha()
            pygame.draw.rect(
                rect_surface,
                color,
                rect_surface.get_rect(),
                border_radius=border_radius - border_width,
            )

            # Blit the semi-transparent surface onto the main screen
            self.screen.blit(rect_surface, (x + border_width, y + border_width))

            # Render text
            name_text = self.font_medium.render(option["name"], True, WHITE)
            value_text = self.font_medium.render(str(option["value"]), True, YELLOW)

            # Calculate center positions for the texts within the rectangle
            name_text_rect = name_text.get_rect(
                center=(x + box_width // 2, y + box_height // 2 - 20)
            )
            value_text_rect = value_text.get_rect(
                center=(x + box_width // 2, y + box_height // 2 + 20)
            )

            # Blit centered text
            self.screen.blit(name_text, name_text_rect)
            self.screen.blit(value_text, value_text_rect)

        pygame.display.update()

    def draw_end_menu(self, menu):
        self.screen.blit(self.resources["menu_background"], (0, 0))

        # Menu options dimensions
        box_width, box_height, margin_x, margin_y = 400, 100, 20, 20
        border_radius, border_width = 15, 5

        # Transparency settings
        semi_transparent_blue, semi_transparent_darkblue = BLUE, DARK_BLUE
        semi_transparent_blue.a, semi_transparent_darkblue.a = 128, 128

        # Calculate the number of rows needed
        num_rows = (len(menu.options) + 1) // 2

        # Calculate total height of the menu
        total_height = num_rows * box_height + (num_rows - 1) * margin_y

        # Calculate starting positions to center the menu
        start_x = (self.screen.get_width() - (2 * box_width + margin_x)) // 2
        start_y = (self.screen.get_height() - total_height) // 2

        for i, option in enumerate(menu.options):
            color = (
                semi_transparent_blue
                if i == menu.selected_option
                else semi_transparent_darkblue
            )
            # Calculate position
            x, y = start_x + (i % 2) * (box_width + margin_x), start_y + (i // 2) * (
                box_height + margin_y
            )

            # Draw chrome effect rectangle
            self.draw_chrome_rect(
                (x, y, box_width, box_height),
                CHROME_COLORS,
                border_radius,
                border_width,
            )

            # Create a semi-transparent surface for the filled rectangle
            rect_surface = pygame.Surface(
                (box_width - 2 * border_width, box_height - 2 * border_width),
                pygame.SRCALPHA,
            )
            rect_surface = rect_surface.convert_alpha()
            pygame.draw.rect(
                rect_surface,
                color,
                rect_surface.get_rect(),
                border_radius=border_radius - border_width,
            )

            # Blit the semi-transparent surface onto the main screen
            self.screen.blit(rect_surface, (x + border_width, y + border_width))

            # Render text
            name_text = self.font_medium.render(str(option), True, WHITE)

            # Calculate center positions for the texts within the rectangle
            name_text_rect = name_text.get_rect(
                center=(x + box_width // 2, y + box_height // 2)
            )

            # Blit centered text
            self.screen.blit(name_text, name_text_rect)

        pygame.display.update()

    def play_intro(self):
        sound = self.resources.get("intro_sound")
        if sound:
            sound.play()

    def draw_game(
        self,
        players,
        current_player,
        holes,
        score,
        game_mode,
        team_mode,
        player_in_team=0,
    ):
        self.screen.blit(self.resources["game_background"], (0, 0))
        self.draw_static_elements(current_player, score, game_mode, team_mode, holes)
        self.display_grouped_players(players, team_mode, player_in_team)

    def draw_score(
        self,
        players,
        current_player,
        holes,
        score,
        game_mode,
        team_mode,
        player_in_team=0,
    ):
        self.display_grouped_players(
            players, team_mode, player_in_team, only_score=True
        )
        self.draw_static_elements(
            current_player, score, game_mode, team_mode, holes, only_score=True
        )

    def draw_holes(self, holes):
        # Define the area for the holes and add chrome border
        holes_area_rect = (
            self.third_width,
            20,
            self.third_width,
            self.hole_rect_height,
        )
        self.draw_chrome_rect(holes_area_rect, CHROME_COLORS, 20, 5)

        # Draw holes
        for hole in holes:
            x1, y1 = hole.position[0], hole.position[1]

            pygame.draw.circle(self.screen, BLACK, (x1, y1), HOLE_RADIUS)
            pygame.draw.circle(self.screen, RED, (x1, y1), HOLE_RADIUS, 5)
            font = self.font_medium if hole.type != "large_frog" else self.font_small
            points_text = font.render(hole.text, True, LIGHT_GREY)
            text_rect = points_text.get_rect(center=(x1, y1))
            self.screen.blit(points_text, text_rect)

            if hole.type == "side" or hole.type == "bottle":
                x2, y2 = hole.position2[0], hole.position2[1]

                pygame.draw.circle(self.screen, BLACK, (x2, y2), HOLE_RADIUS)
                pygame.draw.circle(self.screen, RED, (x2, y2), HOLE_RADIUS, 5)
                text_rect = points_text.get_rect(center=(x2, y2))
                self.screen.blit(points_text, text_rect)

    def draw_static_elements(
        self, current_player, score, game_mode, team_mode, holes, only_score=False
    ):
        """Draws static elements like scores and game info."""
        # Define the area for the current player info and add chrome border
        current_player_rect = (20, 20, self.screen_width / 3 - 40, 200)

        # Calculate center positions for the texts within the rectangle
        rect_x, rect_y, rect_width, rect_height = current_player_rect
        score_text_position = (rect_x + rect_width / 2, rect_y + 100)
        remaining_points_text_position = (rect_x + rect_width / 2, rect_y + 160)

        # Define text strings
        current_player_score = f"Score: {current_player.score}"
        remaining_points_text = f"Points Restants: {score - current_player.score}"

        if only_score:
            # Render the text to get the dimensions
            score_surface = self.font_medium.render(
                current_player_score, True, DARK_ORANGE
            )
            remaining_points_surface = self.font_verysmall.render(
                remaining_points_text, True, DARK_GREEN
            )

            # Calculate rectangle positions and sizes
            score_rect = score_surface.get_rect(center=score_text_position)
            remaining_points_rect = remaining_points_surface.get_rect(
                center=remaining_points_text_position
            )

            # Add padding around the text for the rectangle
            padding = 10
            score_rect.inflate_ip(padding, padding)  # Inflate the rectangle by padding
            remaining_points_rect.inflate_ip(padding, padding)

            rectangle_color = PLAYER_OPTION_COLOR  # Color of the rectangle border

            pygame.draw.rect(self.screen, rectangle_color, score_rect)
            pygame.draw.rect(self.screen, rectangle_color, remaining_points_rect)

        # Draw the text with shadow
        self.draw_text_with_shadow(
            current_player_score,
            self.font_medium,
            DARK_ORANGE,
            BLACK,
            score_text_position,
            shadow_offset=(2, 2),
            center=True,
        )

        self.draw_text_with_shadow(
            remaining_points_text,
            self.font_verysmall,
            DARK_GREEN,
            BLACK,
            remaining_points_text_position,
            shadow_offset=(2, 2),
            center=True,
        )

        if not only_score:
            self.draw_chrome_rect(current_player_rect, CHROME_COLORS, 15, 5)

            current_player_name_text = str(current_player)
            name_text_position = (rect_x + rect_width / 2, rect_y + 40)

            # Draw the current player name with shadow
            self.draw_text_with_shadow(
                current_player_name_text,
                self.font_large,
                DARK_GREEN,
                BLACK,
                name_text_position,
                shadow_offset=(2, 2),
                center=True,
            )

            self.draw_holes(holes)

            # Define the area for the game options and add chrome border
            game_mode_rect = (
                self.screen_width - (self.screen_width / 3 - 20),
                20,
                self.screen_width / 3 - 40,
                200,
            )
            self.draw_chrome_rect(game_mode_rect, CHROME_COLORS, 15, 5)

            # Calculate center positions for the game options texts within the rectangle
            rect_x, rect_y, rect_width, rect_height = game_mode_rect
            game_mode_text_position = (rect_x + rect_width / 2, rect_y + 40)
            score_text_position = (rect_x + rect_width / 2, rect_y + 100)
            team_mode_text_position = (rect_x + rect_width / 2, rect_y + 160)

            # Draw the game mode with shadow
            self.draw_text_with_shadow(
                game_mode,
                self.font_medium,
                DARK_ORANGE,
                BLACK,
                game_mode_text_position,
                shadow_offset=(2, 2),
                center=True,
            )
            # Draw the game score with shadow
            self.draw_text_with_shadow(
                str(score) + " points",
                self.font_medium,
                DARK_ORANGE,
                BLACK,
                score_text_position,
                shadow_offset=(2, 2),
                center=True,
            )
            # Draw the team mode with shadow
            self.draw_text_with_shadow(
                team_mode,
                self.font_medium,
                DARK_ORANGE,
                BLACK,
                team_mode_text_position,
                shadow_offset=(2, 2),
                center=True,
            )

        pygame.display.update()

    def display_grouped_players(
        self, players, team_mode, player_in_team, only_score=False
    ):
        """Handles the display of player groups on the screen."""
        if team_mode == TEAM_MODE_TEAM:
            teams = {}
            for player in players:
                team_id = player.team
                if team_id not in teams:
                    teams[team_id] = []
                teams[team_id].append(player)
            groups = list(teams.values())
            players_per_row = (
                1
                if player_in_team == 3
                else (
                    2
                    if player_in_team > 4
                    else (player_in_team if player_in_team != 2 else 4)
                )
            )
            display_score = True
        elif team_mode == TEAM_MODE_DUO:
            pairs = {}
            for player in players:
                pair_id = player.team
                if pair_id not in pairs:
                    pairs[pair_id] = []
                pairs[pair_id].append(player)
            groups = list(pairs.values())
            players_per_row, display_score = 4, True
        else:  # For TEAM_MODE_SOLO mode, treat all players as a single group
            groups = [players]
            players_per_row, display_score = 4, False

        # Define colors for each group
        group_colors = GROUP_COLORS
        group_color_map = {
            id(group): group_colors[i % len(group_colors)]
            for i, group in enumerate(groups)
        }
        border_radius, border_width = 15, 5

        # Set initial coordinates and layout settings
        start_y = self.screen_height / 2 - 30
        gap_between_boxes = 20
        box_width = self.screen_width / 5
        box_height = 70  # Adjusted height to fit more players
        start_x = (self.screen_width - (4 * box_width) - (3 * gap_between_boxes)) / 2
        x, y = start_x, start_y
        players_in_row = 0

        rank_square_size = 25  # Adjusted size to fit better

        if display_score:
            height_score = self.font_small.render("T", True, DARK_GREY)
            height_score = height_score.get_height() + 5
        else:
            height_score = 0

        for group in groups:
            group_color = group_color_map[id(group)]
            if team_mode != TEAM_MODE_SOLO:
                group_total_score = sum(player.score for player in group)

                total_score_text = f"Total: {group_total_score}"
                self.draw_text_with_shadow(
                    total_score_text,
                    self.font_small,
                    DARK_ORANGE,  # Text color
                    pygame.Color("black"),  # Shadow color
                    (x, y),  # Position
                )

            # Layout players within the group
            for player in group:
                # Draw player box
                if only_score == False or player.is_active:
                    border_color = (
                        GOLD_COLORS
                        if player.won
                        else (RED_COLORS if player.is_active else CHROME_COLORS)
                    )
                    self.draw_chrome_rect(
                        (x, y + height_score, box_width, box_height),
                        border_color,
                        border_radius,
                        border_width,
                    )
                    pygame.draw.rect(
                        self.screen,
                        group_color,
                        (x + 5, y + 5 + height_score, box_width - 10, box_height - 10),
                        border_radius=5,
                    )

                    square_x = x + box_width - rank_square_size - 5
                    square_y = y + 5 + height_score
                    pygame.draw.rect(
                        self.screen,
                        group_color,
                        (square_x, square_y, rank_square_size, rank_square_size),
                    )

                    rank_text = self.font_verysmall.render(
                        f"{player.rank}", True, WHITE
                    )
                    rank_text_rect = rank_text.get_rect(
                        center=(
                            square_x + rank_square_size / 2,
                            square_y + rank_square_size / 2,
                        )
                    )
                    self.screen.blit(rank_text, rank_text_rect)

                    # Player details
                    player_label = self.font_small.render(str(player), True, DARK_GREY)
                    player_label_pos = (
                        x + 10,
                        y
                        + height_score
                        + (box_height - player_label.get_height()) // 2,
                    )
                    self.draw_text_with_shadow(
                        str(player), self.font_small, DARK_GREY, WHITE, player_label_pos
                    )

                    # Calculate the position for the score text
                    score_text_pos = (
                        player_label_pos[0] + player_label.get_width() + 40,
                        y
                        + height_score
                        + (box_height - player_label.get_height()) // 2,
                    )
                    self.draw_text_with_shadow(
                        str(player.score),
                        self.font_small,
                        DARK_GREY,
                        WHITE,
                        score_text_pos,
                    )

                if team_mode in [TEAM_MODE_SOLO, TEAM_MODE_DUO] or (
                    team_mode == TEAM_MODE_TEAM and len(group) == 2
                ):
                    x += box_width + gap_between_boxes
                    players_in_row += 1  # Increment players in row counter
                    if players_in_row >= players_per_row:
                        x = start_x  # Reset x position for new row
                        y += (
                            box_height + gap_between_boxes + height_score
                        )  # Move down to next row
                        players_in_row = 0  # Reset players in row counter
                elif team_mode == TEAM_MODE_TEAM:
                    if len(group) == 3:
                        x = start_x  # Reset x position for new row
                        y += (
                            box_height + gap_between_boxes + height_score
                        )  # Move down to next row
                    elif len(group) > 4:
                        x += box_width + gap_between_boxes
                        players_in_row += 1
                        if players_in_row == 2:
                            x = start_x
                            y += box_height + gap_between_boxes + height_score
                            players_in_row = 0
                    elif len(group) != 2:
                        x += box_width + gap_between_boxes

            if team_mode == TEAM_MODE_TEAM:
                if len(group) == 3:
                    start_x += box_width + gap_between_boxes  #
                    x = start_x
                    y = start_y  # Move down to next row
                elif len(group) > 4:
                    players_in_row = 0
                    start_x += 2 * (box_width + gap_between_boxes)
                    x = start_x
                    y = start_y
                elif len(group) != 2:
                    x = start_x
                    y += box_height + gap_between_boxes + height_score

        pygame.display.flip()

    def draw_text_with_shadow(
        self,
        text,
        font,
        text_color,
        shadow_color,
        position,
        shadow_offset=(2, 2),
        center=False,
    ):
        """
        Renders text with a shadow effect.
        :param text: The text to render.
        :param font: The font to use.
        :param text_color: The color of the text.
        :param shadow_color: The color of the shadow.
        :param position: The position to render the text.
        :param shadow_offset: The offset of the shadow from the text.
        :param center: Whether to center the text at the given position.
        """
        shadow_text = font.render(text, True, shadow_color)
        shadow_position = (
            position[0] + shadow_offset[0],
            position[1] + shadow_offset[1],
        )
        if center:
            shadow_position = (
                shadow_position[0] - shadow_text.get_width() // 2,
                shadow_position[1] - shadow_text.get_height() // 2,
            )
        self.screen.blit(shadow_text, shadow_position)

        actual_text = font.render(text, True, text_color)
        actual_position = position
        if center:
            actual_position = (
                actual_position[0] - actual_text.get_width() // 2,
                actual_position[1] - actual_text.get_height() // 2,
            )
        self.screen.blit(actual_text, actual_position)

    def draw_player(self, x, y, player, box_width, box_height, group_color):
        """Draws individual player boxes and details."""
        border_color = DARK_ORANGE if player.is_active else BLACK
        pygame.draw.rect(
            self.screen,
            border_color,
            (x, y, box_width, box_height),
            border_radius=5,
            width=5,
        )
        pygame.draw.rect(
            self.screen,
            group_color,
            (x + 5, y + 5, box_width - 10, box_height - 10),
            border_radius=5,
        )

        player_label = self.font_small.render(str(player), True, DARK_GREY)
        score_text = self.font_medium.render(str(player.score), True, DARK_GREY)
        self.screen.blit(player_label, (x + 10, y + 10))
        self.screen.blit(score_text, (x + 10, y + 30))

    def calculate_group_layout(self, team_mode, group):
        """Determines layout settings based on team mode and group size."""
        if team_mode == TEAM_MODE_SOLO:
            return 4
        elif team_mode == TEAM_MODE_DUO:
            return 4
        elif team_mode == TEAM_MODE_TEAM:
            if len(group) == 3:
                return 1
            elif len(group) > 4:
                return 2
            return len(group)
        return 4

    def draw_goal_animation(self, hole, pin):
        start_time = time.time()
        current_color = WHITE
        last_blink_time = start_time

        if pin == hole.pin[0]:
            x1, y1 = hole.position
        else:
            x1, y1 = hole.position2

        while time.time() - start_time < 1.5:
            current_time = time.time()
            if current_time - last_blink_time > BLINK_INTERVAL:
                # Toggle the color
                current_color = RED if current_color == DARK_ORANGE else DARK_ORANGE
                last_blink_time = current_time

            # Draw the border with specified thickness
            pygame.draw.circle(self.screen, current_color, (x1, y1), HOLE_RADIUS, 5)

            # Update the display
            pygame.display.flip()

        pygame.draw.circle(self.screen, RED, (x1, y1), HOLE_RADIUS, 5)

        # Update the display
        pygame.display.flip()

    def draw_penalty(self):
        self.resources["penalty_sound"].play()
        self.play_gif(
            self.resources["penalty_frames"], self.resources["penalty_duration"]
        )
        points = self.roulette_animation.run("penalty")

        return points

    def draw_player_win(self, winner):
        # Determine the winner and message
        self.resources["applause"].play()
        BLINK_INTERVAL = 0.5  # Interval in seconds

        # Message and font
        message = f"Bravo {winner}"
        text_surface = self.font_large.render(message, True, DARK_ORANGE)
        text_rect = text_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )

        # Calculate positions for the winner frame and images
        frame_margin = 20
        banner_margin = 10
        banner_width = self.resources["winner_banner"].get_width()

        frame_rect = pygame.Rect(
            text_rect.left - frame_margin - banner_width - banner_margin,
            text_rect.top - frame_margin,
            text_rect.width + 2 * frame_margin + 2 * banner_width + 2 * banner_margin,
            text_rect.height + 2 * frame_margin,
        )

        left_image_rect = self.resources["winner_banner"].get_rect(
            midright=(frame_rect.left - banner_margin, frame_rect.centery)
        )
        right_image_rect = self.resources["winner_banner"].get_rect(
            midleft=(frame_rect.right + banner_margin, frame_rect.centery)
        )

        # Calculate clear rectangle size
        clear_rect = pygame.Rect(
            frame_rect.left - 20 - left_image_rect.width,
            frame_rect.top - 20,
            frame_rect.width + 40 + 2 * left_image_rect.width,
            frame_rect.height + 40,
        )

        # Blinking effect
        start_time = time.time()
        while time.time() - start_time < 3:
            blink = int(
                (time.time() * 2) % 2
            )  # Toggle between 0 and 1 every 0.5 seconds

            # Clear the screen area
            self.screen.fill((0, 0, 0), clear_rect)  # Adjust as necessary

            if blink:
                # Draw the winner frame
                self.draw_chrome_rect(frame_rect, GOLD_COLORS, 10, 5)

                # Draw the text with shadow centered within the frame
                text_center_x = frame_rect.centerx
                text_center_y = frame_rect.centery

                self.draw_text_with_shadow(
                    message,
                    self.font_large,
                    DARK_ORANGE,
                    BLACK,
                    (text_center_x, text_center_y),
                    shadow_offset=(2, 2),
                    center=True,
                )

                # Draw the winner banner images
                self.screen.blit(self.resources["winner_banner"], left_image_rect)
                self.screen.blit(self.resources["winner_banner"], right_image_rect)

            pygame.display.update()
            time.sleep(BLINK_INTERVAL)

        # Ensure the final state is visible
        self.draw_chrome_rect(frame_rect, GOLD_COLORS, 10, 5)
        text_center_x = frame_rect.centerx
        text_center_y = frame_rect.centery

        self.draw_text_with_shadow(
            message,
            self.font_large,
            DARK_ORANGE,
            BLACK,
            (text_center_x, text_center_y),
            shadow_offset=(2, 2),
            center=True,
        )

        self.screen.blit(self.resources["winner_banner"], left_image_rect)
        self.screen.blit(self.resources["winner_banner"], right_image_rect)
        pygame.display.update()
        self.resources["applause"].stop()

    def draw_win(self, players, team_mode):
        self.resources["win_sound"].play()
        self.run_fireworks()
        self.screen.blit(self.resources["win_background"], (0, 0))

        # Group players by team or pairs
        if team_mode == TEAM_MODE_TEAM:
            groups = self.group_players(players, "team")
        elif team_mode == TEAM_MODE_DUO:
            groups = self.group_players(players, "team")
        else:  # For TEAM_MODE_SOLO mode, treat all players as a single group
            groups = [players]

        # Determine the winner and message
        if team_mode in [TEAM_MODE_TEAM, TEAM_MODE_DUO]:
            winner_group = next(
                (
                    group
                    for group in groups
                    if any(player.rank == 1 for player in group)
                ),
                None,
            )
            winner_name = (
                f"Team {next(player.team for player in winner_group)}"
                if team_mode == TEAM_MODE_TEAM
                else f"Duo {next(player.team for player in winner_group)}"
            )
            message = f"Bravo {winner_name}" if winner_group else "Game Over!"
        else:
            winner = next((player for player in players if player.rank == 1), None)
            message = f"Bravo {winner}" if winner else "Game Over!"

        text_surface = self.font_large.render(message, True, DARK_ORANGE)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 70))

        frame_margin = 20
        frame_rect = pygame.Rect(
            text_rect.left - frame_margin,
            text_rect.top - frame_margin,
            text_rect.width + 2 * frame_margin,
            text_rect.height + 2 * frame_margin,
        )
        left_image_rect = self.resources["winner_banner"].get_rect(
            midright=(frame_rect.left - 10, frame_rect.centery)
        )
        right_image_rect = self.resources["winner_banner"].get_rect(
            midleft=(frame_rect.right + 10, frame_rect.centery)
        )

        self.draw_chrome_rect(
            frame_rect,
            GOLD_COLORS,
            10,
            5,
        )

        text_center_x = frame_rect.centerx
        text_center_y = frame_rect.centery

        self.draw_text_with_shadow(
            message,
            self.font_large,
            DARK_ORANGE,
            BLACK,
            (text_center_x, text_center_y),
            shadow_offset=(2, 2),
            center=True,
        )

        self.screen.blit(self.resources["winner_banner"], left_image_rect)
        self.screen.blit(self.resources["winner_banner"], right_image_rect)

        # Sort groups and players within groups by rank
        sorted_groups = sorted(
            groups, key=lambda group: min(player.rank for player in group)
        )
        for group in sorted_groups:
            group.sort(key=lambda player: player.rank)

        # Assign colors to each group
        group_colors = GROUP_COLORS
        group_color_map = {
            id(group): group_colors[i % len(group_colors)]
            for i, group in enumerate(sorted_groups)
        }

        margin_top = 200
        box_height = 40
        gap_between_boxes = 20
        num_rows = sum(len(group) for group in sorted_groups)
        total_height = num_rows * (box_height + gap_between_boxes) - gap_between_boxes

        screen_height = self.screen.get_height()
        columns = 2 if total_height > screen_height - margin_top - 50 else 1

        if columns == 1:
            start_x = self.screen_width / 4
            box_width = self.screen.get_width() / 2
            hor_gap = 0
        else:
            start_x = self.screen_width / 6
            box_width = self.screen.get_width() / 3 - 10
            hor_gap = 20

        x = start_x
        y = margin_top

        for z, group in enumerate(sorted_groups):
            group_color = group_color_map[id(group)]

            for i, player in enumerate(group):
                bg_color = (
                    group_color
                    if team_mode != TEAM_MODE_SOLO
                    else DARK_BLUE if i % 2 == 0 else DARK_GREY
                )

                pygame.draw.rect(
                    self.screen,
                    bg_color,
                    (x, y, box_width, box_height),
                    border_radius=0,
                )

                self.draw_chrome_rect(
                    (x, y, box_width, box_height), CHROME_COLORS, 10, 5
                )

                player_label = self.font_small.render(str(player), True, WHITE)
                score_text = self.font_medium.render(f"{player.score}", True, WHITE)
                rank_text = self.font_small.render(f"{player.rank}", True, WHITE)

                player_label_y = y + (box_height - player_label.get_height()) // 2
                score_text_y = y + (box_height - score_text.get_height()) // 2
                rank_text_y = y + (box_height - rank_text.get_height()) // 2

                self.screen.blit(player_label, (x + 10, player_label_y))
                self.screen.blit(
                    score_text,
                    (
                        x + (box_width // 2) - (score_text.get_width() // 2),
                        score_text_y,
                    ),
                )
                self.screen.blit(rank_text, (x + box_width - 50, rank_text_y))

                y += box_height + gap_between_boxes

            y += gap_between_boxes

            if columns > 1 and z + 1 == math.ceil(len(groups) / 2):
                x += hor_gap + box_width
                y = margin_top

        pygame.display.flip()

    def group_players(self, players, attribute):
        groups = {}
        for player in players:
            key = getattr(player, attribute)
            if key not in groups:
                groups[key] = []
            groups[key].append(player)
        return list(groups.values())

    def animation_bottle(self):
        sound = self.load_sound("sounds", "bouteille.mp3")
        sound.play()

    def animation_little_frog(self):
        self.resources["applause"].play()
        self.play_gif(
            self.resources["little_frog_frames"],
            self.resources["little_frog_duration"],
        )
        self.resources["applause"].stop()

    def animation_large_frog(self):
        self.resources["applause"].play()
        self.play_gif(
            self.resources["large_frog_frames"], self.resources["large_frog_duration"]
        )
        self.resources["applause"].stop()
        return self.roulette_animation.run("frog")

    def load_gif(self, folder, filename):
        # Load GIF using PIL
        gif_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", folder, filename
        )
        gif = Image.open(gif_path)
        frames = []
        try:
            while True:
                # Convert each frame to a format compatible with Pygame
                frame = gif.convert("RGBA")  # Convert to RGBA for transparency support
                pygame_frame = pygame.image.fromstring(
                    frame.tobytes(), frame.size, frame.mode
                )
                frames.append(pygame_frame)
                gif.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass
        return frames, gif.info.get(
            "duration", 100
        )  # Default duration to 100ms if not found

    def play_gif(self, frames, duration):
        clock = pygame.time.Clock()
        running = True
        frame_index = 0

        # Get screen dimensions
        screen_width, screen_height = self.screen.get_size()

        # Get the maximum width and height based on the hole radius and holes_area_rect
        max_width = screen_width // 3
        max_height = screen_height // 2.4

        while running and frame_index < len(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Clear the previous frame area
            self.screen.fill((0, 0, 0))  # Fill the entire screen with black

            # Get the current frame
            surface = frames[frame_index]

            frame_width = surface.get_width()
            frame_height = surface.get_height()

            # Resize the frame to fit within the maximum dimensions if needed
            if frame_width > max_width or frame_height > max_height:
                scale = min(max_width / frame_width, max_height / frame_height)
                surface = pygame.transform.scale(
                    surface, (int(frame_width * scale), int(frame_height * scale))
                )
                frame_width = surface.get_width()
                frame_height = surface.get_height()

            # Calculate position to center the frame in the hole area
            x = max_width + max_width // 2 - frame_width // 2
            y = 20 + max_height // 2 - frame_height // 2

            # Blit the current frame
            self.screen.blit(surface, (x, y))

            pygame.display.flip()

            frame_index += 1
            clock.tick(1000 // duration)

        # Final frame display (optional)
        self.screen.blit(surface, (x, y))
        pygame.display.flip()

    def create_fireworks(self, num_fireworks):
        for _ in range(num_fireworks):
            x = random.randint(100, self.screen.get_width() - 100)
            y = random.randint(100, self.screen.get_height() - 100)
            color = [random.randint(0, 255) for _ in range(3)]
            self.fireworks.append(Firework(x, y, color, num_particles=50))

    def run_fireworks(self):
        self.fireworks = []
        self.create_fireworks(5)
        running = True
        clock = pygame.time.Clock()
        while running and self.fireworks:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            self.screen.fill((0, 0, 0))
            for firework in self.fireworks:
                firework.update()
                firework.draw(self.screen)
            self.fireworks = [f for f in self.fireworks if not f.is_dead()]
            pygame.display.flip()
            clock.tick(30)
