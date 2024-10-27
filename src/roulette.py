import pygame
import random
import time
from pygame.locals import *


DARK_GOLD_COLOR = (184, 134, 11)
LIGHT_GOLD_COLOR = (255, 239, 153)
VALUES = [400, 50, 350, 250, 300, 200, 450, 0, 400, 50, 350, 250, 300, 200, 450, 0]


class RouletteAnimation:
    def __init__(
        self,
        screen,
        roulette_sound,
        roulette_end_sound,
        roulette_image,
        roulette_pointer,
    ):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.rotated_image = None

        screen_width, screen_height = self.screen.get_size()
        self.center_x, self.center_y = screen_width // 2, screen_height // 2

        self.angular_speed = (
            360 / len(VALUES)
        ) / 2  # Initial angular speed (degrees per frame)
        self.min_turns = 3  # Minimum number of full turns before slowing down
        self.current_angle = 0  # Initial rotation angle

        self.font = pygame.font.Font(None, 80)
        self.roulette_sound = roulette_sound
        self.roulette_end_sound = roulette_end_sound
        self.roulette_image = roulette_image
        self.roulette_pointer = roulette_pointer

        # Calculate the angle per section
        self.sections = len(VALUES)
        self.angle_per_section = 360 / self.sections

    def rotate_roulette(self, angular_speed):
        """Rotate the roulette image by the given angular speed."""
        self.current_angle = (self.current_angle - angular_speed) % 360

        # Rotate the image
        self.rotated_image = pygame.transform.rotate(
            self.roulette_image, -self.current_angle
        )
        self.draw_roulette()

    def draw_roulette(self):
        rect = self.rotated_image.get_rect(center=(self.center_x, self.center_y))

        # Draw the rotated image
        self.screen.blit(self.rotated_image, rect.topleft)

    def get_value_from_angle(self, angle):
        """Get the roulette value based on the stopping angle."""
        # Normalize the angle to 0-360
        normalized_angle = angle % 360
        # Calculate the section the angle points to
        section_index = int(normalized_angle // self.angle_per_section)
        return VALUES[section_index]

    def draw_pointer(self):
        """Draw the pointer image on the screen."""
        # Get the dimensions of the roulette image
        roulette_rect = self.roulette_image.get_rect(
            center=(self.center_x, self.center_y)
        )

        # Position the pointer at the top of the roulette image, centered horizontally
        pointer_rect = self.roulette_pointer.get_rect(
            center=(self.center_x, roulette_rect.top + 20)
        )

        # Draw the pointer on the screen
        self.screen.blit(self.roulette_pointer, pointer_rect.topleft)

    def run(self):
        # Calculate the radius of the circle based on 25% of the roulette's height
        roulette_height = self.roulette_image.get_height()
        circle_radius = int(roulette_height * 0.29) / 2

        running = True
        random.seed(time.time())
        additional_sections = random.randint(0, 2 * self.sections)
        total_sections = (self.min_turns * len(VALUES)) + additional_sections
        deceleration_section = total_sections - int(len(VALUES) / 2)
        final_angle = (additional_sections * self.angle_per_section) % 360
        self.roulette_sound.play(loops=-1)
        actual_section = 0
        section_angle = 360 / len(VALUES)
        actual_section_angle = 0

        # Spin the wheel until it completes at least the minimum number of turns
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill(pygame.Color("black"))  # Clear the screen
            self.rotate_roulette(self.angular_speed)
            self.draw_pointer()
            pygame.display.update()
            self.clock.tick(30)  # Control frame rate
            actual_section_angle += self.angular_speed
            if actual_section_angle == section_angle:
                actual_section += 1
                actual_section_angle = 0

            # Start slowing down if the current angle reaches the deceleration start angle
            if actual_section == deceleration_section:
                distance_to_final = (total_sections - deceleration_section) * (
                    360 / len(VALUES)
                )
                # Decelerate and stop at the final angle
                while running:
                    # Update the current angle
                    self.screen.fill(pygame.Color("black"))
                    self.rotate_roulette(self.angular_speed)
                    self.draw_pointer()
                    pygame.display.update()
                    self.clock.tick(30)

                    # Calculate the distance to the final angle
                    distance_to_final -= self.angular_speed

                    # Gradually reduce the angular speed based on the distance
                    # The closer to the final angle, the slower the speed
                    if distance_to_final < 30 and self.angular_speed > 4:
                        # If very close to the final angle, reduce speed significantly
                        self.angular_speed *= 0.85
                    elif distance_to_final < 60 and self.angular_speed > 4:
                        # Moderately close to the final angle, reduce speed less
                        self.angular_speed *= 0.9
                    elif self.angular_speed > 4:
                        # Far from the final angle, reduce speed minimally
                        self.angular_speed *= 0.95

                    # Stop if the wheel is close enough to the final angle
                    if (
                        distance_to_final < 1
                        or abs(self.current_angle % 360 - final_angle)
                        < self.angular_speed
                    ):
                        self.angular_speed = 0  # Ensure the wheel stops completely
                        running = False

        # Determine the final value based on the stopping angle
        final_value = VALUES[additional_sections % len(VALUES)]

        # Blink the final value for 1.5 seconds
        blink_duration = 2
        end_blink_time = time.time() + blink_duration

        self.roulette_sound.stop()
        self.roulette_end_sound.play()

        while time.time() < end_blink_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_roulette()
            self.draw_pointer()

            if int(time.time() * 2) % 2 == 0:
                pygame.draw.circle(
                    self.screen,
                    pygame.Color(DARK_GOLD_COLOR),  # Border color
                    (self.center_x, self.center_y),
                    circle_radius + 5,  # Slightly larger radius for the border
                    width=5,  # Border width
                )

                pygame.draw.circle(
                    self.screen,
                    pygame.Color(LIGHT_GOLD_COLOR),
                    (self.center_x, self.center_y),
                    circle_radius,
                )

                # Render the final value text
                final_value_text = self.font.render(
                    str(final_value),
                    True,
                    pygame.Color("black"),
                )
                final_value_rect = final_value_text.get_rect(
                    center=(self.center_x, self.center_y)
                )
                self.screen.blit(final_value_text, final_value_rect)

            pygame.display.update()
            self.clock.tick(30)  # Control frame rate consistently

        self.screen.fill(pygame.Color("black"))  # Clear the screen
        self.draw_roulette()
        self.draw_pointer()

        pygame.draw.circle(
            self.screen,
            pygame.Color(DARK_GOLD_COLOR),  # Border color
            (self.center_x, self.center_y),
            circle_radius + 5,  # Slightly larger radius for the border
            width=5,  # Border width
        )

        pygame.draw.circle(
            self.screen,
            pygame.Color(LIGHT_GOLD_COLOR),
            (self.center_x, self.center_y),
            circle_radius,
        )
        final_value_text = self.font.render(
            str(final_value),
            True,
            pygame.Color("black"),
        )
        final_value_rect = final_value_text.get_rect(
            center=(self.center_x, self.center_y)
        )
        self.screen.blit(final_value_text, final_value_rect)
        pygame.display.update()

        return final_value
