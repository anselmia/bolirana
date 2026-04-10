# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame

from src.constants import BLACK, CHROME_COLORS, WHITE, YELLOW


class UIMenuMixin:
    MENU_CACHE_FPS = 8

    def freeze_menu_cache_value(self, value):
        if isinstance(value, dict):
            return tuple(
                (key, self.freeze_menu_cache_value(item))
                for key, item in sorted(value.items())
            )
        if isinstance(value, (list, tuple)):
            return tuple(self.freeze_menu_cache_value(item) for item in value)
        return value

    def get_menu_frame_cache_key(self, menu, mode):
        options_signature = tuple(
            self.freeze_menu_cache_value(option) for option in menu.options
        )
        return (
            mode,
            int(time.monotonic() * self.MENU_CACHE_FPS),
            menu.selected_option,
            options_signature,
        )

    def draw_menu(self, menu):
        cache_key = self.get_menu_frame_cache_key(menu, "menu")
        cached_surface = self._menu_frame_cache.get(cache_key)
        if cached_surface is not None:
            self.display.screen.blit(cached_surface, (0, 0))
            pygame.display.update()
            return

        phase = time.monotonic()
        selected_option = menu.options[menu.selected_option]
        subtitle = f"{selected_option['name']} : {selected_option['value']}"
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self.draw_vertical_gradient((6, 18, 36), (10, 56, 94), alpha=132)
        self.draw_spotlight_canopy(phase, intensity=1.0, tint=(255, 224, 168))
        self.draw_stage_floor(phase, horizon_ratio=0.74, tint=(120, 214, 255), alpha=24)
        self.draw_ambient_backdrop(phase)
        self.draw_screen_frame(phase)
        self.draw_scene_badges(
            "EDITION PRESTIGE",
            f"OPTION {menu.selected_option + 1:02d}/{len(menu.options):02d}",
            phase,
        )
        self.draw_title_panel("BOLIRANA", subtitle, phase)
        self._draw_option_grid(
            menu.options, menu.selected_option, show_value=True, phase=phase
        )
        self.draw_footer_prompt(
            "NEXT pour naviguer  |  RIGHT pour changer  |  ENTER pour lancer",
            phase,
        )
        self._menu_frame_cache = {cache_key: self.display.screen.copy()}
        pygame.display.update()

    def draw_end_menu(self, menu):
        cache_key = self.get_menu_frame_cache_key(menu, "end_menu")
        cached_surface = self._menu_frame_cache.get(cache_key)
        if cached_surface is not None:
            self.display.screen.blit(cached_surface, (0, 0))
            pygame.display.update()
            return

        phase = time.monotonic()
        title = "PAUSE" if "Continuer" in menu.options else "FIN DE PARTIE"
        subtitle = "Choisis la suite du show"
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self.draw_vertical_gradient((8, 16, 30), (46, 14, 28), alpha=144)
        self.draw_spotlight_canopy(phase, intensity=0.88, tint=(255, 204, 150))
        self.draw_stage_floor(phase, horizon_ratio=0.75, tint=(255, 196, 110), alpha=26)
        self.draw_ambient_backdrop(phase)
        self.draw_screen_frame(
            phase,
            accent_color=(255, 196, 110),
            secondary_color=(255, 120, 120),
        )
        self.draw_scene_badges("ARENA CONTROL", f"{len(menu.options)} CHOIX", phase)
        self.draw_title_panel(title, subtitle, phase)
        self._draw_option_grid(
            menu.options, menu.selected_option, show_value=False, phase=phase
        )
        self.draw_footer_prompt("NEXT pour naviguer  |  ENTER pour valider", phase)
        self._menu_frame_cache = {cache_key: self.display.screen.copy()}
        pygame.display.update()

    def _draw_option_grid(self, options, selected_option, show_value, phase=None):
        phase = time.monotonic() if phase is None else phase
        box_width, box_height, margin_x, margin_y = 408, 112, 24, 24
        border_radius, border_width = 18, 5

        num_rows = (len(options) + 1) // 2
        total_height = num_rows * box_height + (num_rows - 1) * margin_y
        start_x = (self.display.screen.get_width() - (2 * box_width + margin_x)) // 2
        start_y = (self.display.screen.get_height() - total_height) // 2 + 26

        for index, option in enumerate(options):
            x = start_x + (index % 2) * (box_width + margin_x)
            y = start_y + (index // 2) * (box_height + margin_y)
            is_selected = index == selected_option
            lift = int((8 + math.sin(phase * 5.5) * 4) if is_selected else 0)
            card_rect = pygame.Rect(x, y - lift, box_width, box_height)
            base_color = (26, 118, 194, 224) if is_selected else (10, 32, 66, 194)
            inner_color = (92, 214, 255, 92) if is_selected else (255, 255, 255, 18)

            self.draw_panel_shadow(
                card_rect,
                alpha=110 if is_selected else 72,
                inflate=18,
                offset=(0, 12),
                border_radius=22,
            )

            if is_selected:
                burst_surface = pygame.Surface(
                    (card_rect.width + 80, card_rect.height + 80), pygame.SRCALPHA
                )
                burst_center = burst_surface.get_rect().center
                for ray_index in range(10):
                    angle = ray_index * math.tau / 10 + phase * 0.3
                    inner = 26
                    outer = 74
                    pygame.draw.polygon(
                        burst_surface,
                        (255, 220, 126, 34),
                        [
                            (
                                burst_center[0] + math.cos(angle - 0.12) * inner,
                                burst_center[1] + math.sin(angle - 0.12) * inner,
                            ),
                            (
                                burst_center[0] + math.cos(angle) * outer,
                                burst_center[1] + math.sin(angle) * outer,
                            ),
                            (
                                burst_center[0] + math.cos(angle + 0.12) * inner,
                                burst_center[1] + math.sin(angle + 0.12) * inner,
                            ),
                        ],
                    )
                self.display.screen.blit(
                    burst_surface,
                    burst_surface.get_rect(center=card_rect.center),
                )

            self.draw_chrome_rect(
                card_rect,
                CHROME_COLORS,
                border_radius,
                border_width,
            )

            rect_surface = pygame.Surface(
                (box_width - 2 * border_width, box_height - 2 * border_width),
                pygame.SRCALPHA,
            )
            rect_surface = rect_surface.convert_alpha()
            pygame.draw.rect(
                rect_surface,
                base_color,
                rect_surface.get_rect(),
                border_radius=border_radius - border_width,
            )
            pygame.draw.rect(
                rect_surface,
                inner_color,
                (8, 8, rect_surface.get_width() - 16, rect_surface.get_height() // 2),
                border_radius=border_radius - border_width,
            )
            pygame.draw.rect(
                rect_surface,
                (255, 255, 255, 22 if is_selected else 10),
                rect_surface.get_rect(),
                width=2,
                border_radius=border_radius - border_width,
            )
            self.display.screen.blit(
                rect_surface,
                (card_rect.x + border_width, card_rect.y + border_width),
            )
            self.draw_halftone_dots(
                card_rect.inflate(-26, -20),
                color=(255, 255, 255),
                alpha=12 if is_selected else 8,
                spacing=22,
                radius=2,
                drift=phase * 4,
            )
            self.draw_arcade_screws(card_rect, inset=12, radius=3)
            index_rect = pygame.Rect(card_rect.right - 54, card_rect.top + 10, 40, 20)
            self.draw_badge(
                f"{index + 1:02d}",
                index_rect,
                (255, 255, 255, 22 if is_selected else 14),
                text_color=WHITE,
                border_color=(255, 255, 255, 32),
            )

            if is_selected:
                self.draw_marquee_lights(card_rect, phase, (255, 226, 126), count=16)
                chip_rect = pygame.Rect(card_rect.left + 14, card_rect.top - 14, 74, 22)
                chip_surface = pygame.Surface(chip_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    chip_surface,
                    (255, 214, 82, 220),
                    chip_surface.get_rect(),
                    border_radius=12,
                )
                self.display.screen.blit(chip_surface, chip_rect.topleft)
                self.draw_text_with_shadow(
                    "SELECT",
                    self.display.font_verysmall,
                    BLACK,
                    WHITE,
                    chip_rect.center,
                    shadow_offset=(1, 1),
                    center=True,
                )
                pygame.draw.polygon(
                    self.display.screen,
                    (255, 222, 126),
                    [
                        (card_rect.left - 14, card_rect.centery),
                        (card_rect.left - 2, card_rect.centery - 10),
                        (card_rect.left - 2, card_rect.centery + 10),
                    ],
                )
                pygame.draw.polygon(
                    self.display.screen,
                    (255, 222, 126),
                    [
                        (card_rect.right + 14, card_rect.centery),
                        (card_rect.right + 2, card_rect.centery - 10),
                        (card_rect.right + 2, card_rect.centery + 10),
                    ],
                )

            if show_value:
                name_text = self.display.font_medium.render(option["name"], True, WHITE)
                name_text_rect = name_text.get_rect(
                    center=(
                        card_rect.x + box_width // 2,
                        card_rect.y + 34,
                    )
                )
                pygame.draw.line(
                    self.display.screen,
                    (255, 255, 255, 46),
                    (card_rect.left + 24, card_rect.top + 52),
                    (card_rect.right - 24, card_rect.top + 52),
                    1,
                )
                value_rect = pygame.Rect(
                    card_rect.left + 98, card_rect.bottom - 36, 206, 26
                )
                self.draw_badge(
                    str(option["value"]),
                    value_rect,
                    (6, 20, 42, 198),
                    text_color=YELLOW,
                    border_color=(255, 220, 126, 90),
                    font=self.display.font_small,
                )
                hint_rect = pygame.Rect(
                    card_rect.left + 20, card_rect.bottom - 34, 66, 22
                )
                self.draw_badge(
                    "FUN",
                    hint_rect,
                    (255, 214, 82, 214) if is_selected else (8, 24, 44, 188),
                    text_color=BLACK if is_selected else WHITE,
                    border_color=(255, 255, 255, 70),
                )
                self.display.screen.blit(name_text, name_text_rect)
            else:
                name_text = self.display.font_medium.render(str(option), True, WHITE)
                name_text_rect = name_text.get_rect(
                    center=(card_rect.x + box_width // 2, card_rect.y + box_height // 2)
                )
                self.display.screen.blit(name_text, name_text_rect)
                if is_selected:
                    action_rect = pygame.Rect(
                        card_rect.left + 20, card_rect.bottom - 34, 88, 22
                    )
                    self.draw_badge(
                        "GO!",
                        action_rect,
                        (255, 214, 82, 220),
                        text_color=BLACK,
                        border_color=(255, 255, 255, 70),
                    )

    def play_intro(self):
        sound = self.display.resources.get("intro_sound")
        if sound:
            sound.play()
