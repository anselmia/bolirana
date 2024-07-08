import pygame
import os
import time
import logging
import sys
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
    MAGENTA,
    RED,
    DARK_RED,
    GROUP_COLORS,
)
import random
from src.firework import Firework
from src.roulette import RouletteAnimation
from PIL import Image


class Display:
    def __init__(self):
        pygame.display.set_caption("Bolirana Game")
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        font_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "fonts", "AntonSC-Regular.ttf"
        )
        self.font_large = pygame.font.Font(font_path, 50)
        self.font_medium = pygame.font.Font(font_path, 30)
        self.font_small = pygame.font.Font(font_path, 25)
        self.font_verysmall = pygame.font.Font(font_path, 20)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.load_ressources()

    def load_ressources(self):
        try:
            self.game_background = self.load_image("images", "game3.jpg")
            self.menu_background = self.load_image("images", "intro.jpg")
            self.win_background = self.load_image("images", "win.jpg")
            self.penalty_frames, self.penalty_duration = self.load_gif(
                "gif", "fail.gif"
            )
            self.penalty_sound = self.load_sound("sounds", "fail.mp3")
            self.win_sound = self.load_sound("sounds", "victoire.mp3")
            self.large_frog_frames, self.large_frog_duration = self.load_gif(
                "gif", "large_frog_animation.gif"
            )
            self.large_frog_sound = self.load_sound(
                "sounds", "aplaudissement_largefrog.mp3"
            )
            self.little_frog_frames, self.little_frog_duration = self.load_gif(
                "gif", "small_frog_animation.gif"
            )
            self.little_frog_sound = self.load_sound(
                "sounds", "aplaudissement_smallfrog.mp3"
            )
        except Exception as e:
            logging.error(f"Failed to load resources: {e}")
            self.display_error_message("Failed to load resources. Exiting...")
            pygame.quit()
            sys.exit()

    def load_image(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        image = pygame.image.load(path)
        return pygame.transform.scale(image, self.screen.get_size())

    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        return pygame.mixer.Sound(path)

    def display_error_message(self, message):
        self.screen.fill((0, 0, 0))
        error_text = self.font_large.render(message, True, RED)
        self.screen.blit(
            error_text,
            (
                self.screen_width // 2 - error_text.get_width() // 2,
                self.screen_height // 2,
            ),
        )
        pygame.display.flip()
        time.sleep(3)  # Display the message for 3 seconds

    def get_hole_position(self, hole_value, position):
        # Adjust the function to handle all cases and default return None
        if hole_value == "20":
            return (
                (((self.screen_width / 3 + 20) + HOLE_RADIUS, 255),)
                if position == 1
                else (((self.screen_width / 3 + 20) + HOLE_RADIUS + 240, 255),)
            )
        elif hole_value == "25":
            return (
                (((self.screen_width / 3 + 20) + HOLE_RADIUS, 150),)
                if position == 1
                else ((self.screen_width / 3 + 20 + HOLE_RADIUS + 240, 155),)
            )
        elif hole_value == "40":
            return (
                (((self.screen_width / 3 + 20) + HOLE_RADIUS + 60, 205),)
                if position == 1
                else ((self.screen_width / 3 + 20 + HOLE_RADIUS + 180, 205),)
            )
        elif hole_value == "50":
            return (
                (((self.screen_width / 3 + 20) + HOLE_RADIUS + 60, 105),)
                if position == 1
                else ((self.screen_width / 3 + 20 + HOLE_RADIUS + 180, 105),)
            )
        elif hole_value == "100":
            return (
                (((self.screen_width / 3 + 20) + HOLE_RADIUS + 60, 305),)
                if position == 1
                else ((self.screen_width / 3 + 20 + HOLE_RADIUS + 180, 305),)
            )
        elif hole_value == "150":
            return (
                (((self.screen_width / 3 + 20) + HOLE_RADIUS, 55),)
                if position == 1
                else (((self.screen_width / 3 + 20) + HOLE_RADIUS + 240, 55),)
            )
        elif hole_value == "200":
            return (((self.screen_width / 2) + 120, 155),)
        elif hole_value == "ROUL":
            return (((self.screen_width / 2) + 120, 55),)
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

    def draw_menu(self, menu):
        self.screen.blit(self.menu_background, (0, 0))  # Draw the background image

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

        pygame.display.flip()

    def play_intro(self):
        sound = self.load_sound("sounds", "intro.mp3")
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
        self.screen.blit(self.game_background, (0, 0))
        self.draw_static_elements(current_player, score, game_mode, team_mode, holes)
        self.display_grouped_players(players, team_mode, player_in_team)
        pygame.display.flip()

    def draw_static_elements(self, current_player, score, game_mode, team_mode, holes):
        """Draws static elements like scores and game info."""
        current_player_score = f"Score: {current_player.score}"
        remaining_points_text = f"Points Restants: {score - current_player.score}"

        current_player_name_text = self.font_large.render(
            str(current_player), True, DARK_GREEN
        )
        current_player_score_text = self.font_medium.render(
            current_player_score, True, DARK_ORANGE
        )
        remaining_points_text_rendered = self.font_verysmall.render(
            remaining_points_text, True, DARK_GREY
        )

        # Define the area for the current player info and add chrome border
        current_player_rect = (20, 20, self.screen_width / 3 - 40, 200)
        self.draw_chrome_rect(current_player_rect, CHROME_COLORS, 15, 5)

        # Calculate center positions for the texts within the rectangle
        rect_x, rect_y, rect_width, rect_height = current_player_rect
        name_text_rect = current_player_name_text.get_rect(
            center=(rect_x + rect_width / 2, rect_y + 40)
        )
        score_text_rect = current_player_score_text.get_rect(
            center=(rect_x + rect_width / 2, rect_y + 100)
        )
        remaining_points_text_rect = remaining_points_text_rendered.get_rect(
            center=(rect_x + rect_width / 2, rect_y + 160)
        )

        # Blit the centered text
        self.screen.blit(current_player_name_text, name_text_rect.topleft)
        self.screen.blit(current_player_score_text, score_text_rect.topleft)
        self.screen.blit(
            remaining_points_text_rendered, remaining_points_text_rect.topleft
        )

        # Define the area for the holes and add chrome border
        holes_area_rect = (
            self.screen_width // 3,
            20,
            self.screen_width // 3,
            self.screen_height // 2.4,
        )
        self.draw_chrome_rect(holes_area_rect, CHROME_COLORS, 20, 5)

        # Draw holes
        for hole in holes:
            x1, y1 = hole.position[0]

            pygame.draw.circle(self.screen, BLACK, (x1, y1), HOLE_RADIUS)
            pygame.draw.circle(self.screen, RED, (x1, y1), HOLE_RADIUS, 2)
            font = self.font_medium if hole.type != "large_frog" else self.font_small
            points_text = font.render(hole.text, True, LIGHT_GREY)
            text_rect = points_text.get_rect(center=(x1, y1))
            self.screen.blit(points_text, text_rect)

            if hole.type == "side" or hole.type == "bottle":
                x2, y2 = hole.position2[0]

                pygame.draw.circle(self.screen, BLACK, (x2, y2), HOLE_RADIUS)
                pygame.draw.circle(self.screen, RED, (x2, y2), HOLE_RADIUS, 2)
                text_rect = points_text.get_rect(center=(x2, y2))
                self.screen.blit(points_text, text_rect)

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
        game_mode_text = self.font_medium.render(game_mode, True, DARK_ORANGE)
        score_text = self.font_medium.render(str(score) + " points", True, DARK_ORANGE)
        team_mode_text = self.font_medium.render(team_mode, True, DARK_ORANGE)

        game_mode_text_rect = game_mode_text.get_rect(
            center=(rect_x + rect_width / 2, rect_y + 40)
        )
        score_text_rect = score_text.get_rect(
            center=(rect_x + rect_width / 2, rect_y + 100)
        )
        team_mode_text_rect = team_mode_text.get_rect(
            center=(rect_x + rect_width / 2, rect_y + 160)
        )

        # Blit the centered game options texts
        self.screen.blit(game_mode_text, game_mode_text_rect.topleft)
        self.screen.blit(score_text, score_text_rect.topleft)
        self.screen.blit(team_mode_text, team_mode_text_rect.topleft)

    def display_grouped_players(self, players, team_mode, player_in_team):
        """Handles the display of player groups on the screen."""
        if team_mode == "Equipe":
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
        elif team_mode == "Duo":
            pairs = {}
            for player in players:
                pair_id = player.team
                if pair_id not in pairs:
                    pairs[pair_id] = []
                pairs[pair_id].append(player)
            groups = list(pairs.values())
            players_per_row, display_score = 4, True
        else:  # For "Seul" mode, treat all players as a single group
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
            group_total_score = sum(player.score for player in group)

            if display_score:
                # Display total score above each group
                total_score_text = self.font_small.render(
                    f"Total: {group_total_score}", True, DARK_ORANGE
                )
                self.screen.blit(total_score_text, (x, y))

            # Layout players within the group
            for player in group:
                # Draw player box
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

                rank_text = self.font_small.render(f"{player.rank}", True, WHITE)
                rank_text_rect = rank_text.get_rect(
                    center=(
                        square_x + rank_square_size / 2,
                        square_y + rank_square_size / 2,
                    )
                )
                self.screen.blit(rank_text, rank_text_rect)

                # Player details
                player_label = self.font_verysmall.render(str(player), True, DARK_GREY)
                score_text = self.font_medium.render(str(player.score), True, DARK_GREY)
                self.screen.blit(
                    player_label, (x + 10, y + height_score + 5)
                )  # Reduced gap from top
                self.screen.blit(
                    score_text, (x + 10, y + height_score + 25)
                )  # Increased gap from bottom

                if team_mode in ["Seul", "Duo"] or (
                    team_mode == "Equipe" and len(group) == 2
                ):
                    x += box_width + gap_between_boxes
                    players_in_row += 1  # Increment players in row counter
                    if players_in_row >= players_per_row:
                        x = start_x  # Reset x position for new row
                        y += (
                            box_height + gap_between_boxes + height_score
                        )  # Move down to next row
                        players_in_row = 0  # Reset players in row counter
                elif team_mode == "Equipe":
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

            if team_mode == "Equipe":
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
        if team_mode == "Seul":
            return 4
        elif team_mode == "Duo":
            return 4
        elif team_mode == "Equipe":
            if len(group) == 3:
                return 1
            elif len(group) > 4:
                return 2
            return len(group)
        return 4

    def draw_goal_animation(self, hole):
        start_time = time.time()
        current_color = WHITE
        last_blink_time = start_time

        while time.time() - start_time < 1.5:
            current_time = time.time()
            if current_time - last_blink_time > BLINK_INTERVAL:
                # Toggle the color
                current_color = RED if current_color == DARK_ORANGE else DARK_ORANGE
                last_blink_time = current_time

            # Draw the circle with the current color
            x1, y1 = hole.position
            # Draw the border with specified thickness
            pygame.draw.circle(self.screen, current_color, (x1, y1), HOLE_RADIUS, 5)
            if hole.type in ["side", "bottle"]:
                x2, y2 = hole.position2
                # Draw the border with specified thickness
                pygame.draw.circle(self.screen, current_color, (x2, y2), HOLE_RADIUS, 5)

            # Update the display
            pygame.display.flip()

    def draw_penalty(self):
        self.penalty_sound.play()
        self.play_gif(self.penalty_frames, self.penalty_duration)
        self.play_gif(self.penalty_frames, self.penalty_duration)
        roulette_animation = RouletteAnimation(self.screen, "null")
        points = roulette_animation.run()

        return points

    def draw_win(self, players, team_mode):
        self.win_sound.play()
        self.run_fireworks()
        self.screen.blit(self.win_background, (0, 0))

        # Display the congratulatory message for the winner
        winner = next((player for player in players if player.rank == 1), None)
        message = f"Bravo {winner}!" if winner else "Game Over!"
        text_surface = self.font_large.render(message, True, YELLOW)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(text_surface, text_rect)

        # Group players by team or pairs
        if team_mode == "Equipe":
            teams = {}
            for player in players:
                team_id = player.team
                if team_id not in teams:
                    teams[team_id] = []
                teams[team_id].append(player)
            groups = teams.values()
        elif team_mode == "Duo":
            pairs = {}
            for player in players:
                pair_id = player.team
                if pair_id not in pairs:
                    pairs[pair_id] = []
                pairs[pair_id].append(player)
            groups = pairs.values()
        else:
            groups = [players]

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

        # Calculate positions for displaying player groups
        margin_left, margin_top, gap_between_boxes = self.screen.get_width() / 4, 150, 2
        box_width, box_height = self.screen.get_width() / 2, 40

        # Calculate total height required for all groups
        num_rows = sum(len(group) for group in sorted_groups)  # Number of rows needed
        total_height = num_rows * (box_height + gap_between_boxes) - gap_between_boxes

        # Calculate vertical offset to center the player groups
        vertical_offset = (self.screen.get_height() - total_height - margin_top) // 2

        y = margin_top + vertical_offset
        for group in sorted_groups:
            group_color = group_color_map[id(group)]
            for i, player in enumerate(group):
                x = margin_left

                # Draw the player box with the group's color
                bg_color = group_color
                border_color = MAGENTA if player.won else BLACK

                # Draw the background
                pygame.draw.rect(
                    self.screen,
                    bg_color,
                    (x, y, box_width, box_height),
                    border_radius=0,
                )

                # Player information
                player_label = self.font_small.render(str(player), True, WHITE)
                score_text = self.font_medium.render(f"{player.score}", True, WHITE)
                rank_text = self.font_small.render(f"{player.rank}", True, YELLOW)

                self.screen.blit(player_label, (x + 10, y + 10))
                self.screen.blit(score_text, (x + box_width // 2, y + 10))
                self.screen.blit(rank_text, (x + box_width - 50, y + 10))

                y += box_height + gap_between_boxes

        pygame.display.flip()

        # Add a condition to exit the loop
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False
                    break

    def draw_end_menu(self, players):
        dark_green, dark_red = DARK_GREEN, DARK_RED

        self.screen.fill((0, 0, 0))
        self.win_sound.play()
        self.run_fireworks()

        winner = next((player for player in players if player.rank == 1), None)
        message = f"Bravo {winner}!" if winner else "Game Over!"
        text_surface = self.font_large.render(message, True, YELLOW)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(text_surface, text_rect)

        sorted_players = sorted(
            players, key=lambda x: x.rank if x.rank > 0 else float("inf")
        )

        margin_left, margin_top, gap_between_boxes = 50, 100, 10
        box_width = (self.screen.get_width() - 2 * margin_left) // 4
        box_height = 90

        for i, player in enumerate(sorted_players):
            x = margin_left + (i % 4) * (box_width + gap_between_boxes)
            y = margin_top + (i // 4) * (box_height + gap_between_boxes + 20)

            bg_color = dark_green if i % 2 == 0 else dark_red
            border_color = MAGENTA if player.won else BLACK

            pygame.draw.rect(
                self.screen,
                border_color,
                (x, y, box_width, box_height),
                border_radius=5,
                width=5,
            )
            pygame.draw.rect(
                self.screen,
                bg_color,
                (x + 5, y + 5, box_width - 10, box_height - 10),
                border_radius=5,
            )

            player_label = self.font_small.render(f"{player}", True, YELLOW)
            score_text = self.font_medium.render(f"Score: {player.score}", True, WHITE)
            self.screen.blit(player_label, (x + 10, y + 10))
            self.screen.blit(score_text, (x + 10, y + 50))

            if player.rank > 0:
                square_size = 30
                square_x, square_y = x + box_width - square_size - 5, y + 5
                pygame.draw.rect(
                    self.screen,
                    MAGENTA,
                    (square_x, square_y, square_size, square_size),
                )
                rank_text = self.font_small.render(f"{player.rank}", True, WHITE)
                rank_text_rect = rank_text.get_rect(
                    center=(square_x + square_size / 2, square_y + square_size / 2)
                )
                self.screen.blit(rank_text, rank_text_rect)

        pygame.display.flip()

    def animation_bottle(self):
        sound = self.load_sound("sounds", "bouteille.mp3")
        sound.play()

    def animation_little_frog(self):
        self.little_frog_sound.play()
        self.play_gif(self.little_frog_frames, self.little_frog_duration)

    def animation_large_frog(self):
        self.large_frog_sound.play()
        self.play_gif(self.large_frog_frames, self.large_frog_duration)
        roulette_animation = RouletteAnimation(self.screen, "frog")
        return roulette_animation.run()

    def load_gif(self, folder, filename):
        # Load GIF using PIL
        gif_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", folder, filename
        )
        gif = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = gif.copy().convert("RGBA")  # Convert to RGBA for consistency
                frames.append(frame)
                gif.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass
        return frames, gif.info["duration"]

    def play_gif(self, frames, duration):
        clock = pygame.time.Clock()
        frame_index = 0
        running = True

        screen_width, screen_height = self.screen.get_size()

        while running and frame_index < len(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Get the current frame
            frame = frames[frame_index]
            mode, size = frame.mode, frame.size
            data = frame.tobytes()

            surface = pygame.image.fromstring(
                data, size, "RGBA" if mode == "RGBA" else "RGB"
            )

            # Calculate position to center the frame
            frame_width, frame_height = size
            x, y = (screen_width - frame_width) // 2, (
                screen_height - frame_height
            ) // 2

            # Define the rectangle area for the GIF
            padding = 10
            rect_x, rect_y, rect_width, rect_height = (
                x - padding,
                y - padding,
                frame_width + 2 * padding,
                frame_height + 2 * padding,
            )

            # Draw the white rectangle with a black border
            pygame.draw.rect(
                self.screen,
                BLACK,
                (rect_x, rect_y, rect_width, rect_height),
            )
            pygame.draw.rect(
                self.screen,
                WHITE,
                (rect_x + 1, rect_y + 1, rect_width - 2, rect_height - 2),
            )

            # Draw the frame
            self.screen.blit(surface, (x, y))
            pygame.display.flip()

            frame_index += 1
            clock.tick(1000 // duration)

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
