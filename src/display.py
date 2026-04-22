import io
import logging
import os
import struct
import sys
import time
from array import array
from math import pi, sin

import pygame

from src.constants import HOLE_RADIUS
from src.display_services import DisplayEffectsService, DisplayUIService

_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "cache")


class Display:
    def __init__(self, debug, screen=None):
        pygame.display.set_caption("Bolirana Game")
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if screen is not None:
            # Reuse the screen created by Game.__init__ — avoids a second
            # set_mode() call which triggers a costly Wayland surface renegotiation.
            self.screen = screen
        elif debug:
            self.screen = pygame.display.set_mode((1024, 768), flags)
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | flags)

        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        # Show a loading splash immediately so the screen isn't black while assets load
        self._show_loading_screen()
        font_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
        font_path = os.path.join(font_dir, "AntonSC-Regular.ttf")
        title_font_path = os.path.join(font_dir, "GaMaamli-Regular.ttf")
        # Read font files once as bytes — avoids re-parsing the TTF for each size
        with open(font_path, "rb") as f:
            font_bytes = f.read()
        with open(title_font_path, "rb") as f:
            title_font_bytes = f.read()

        def _font(data, size):
            return pygame.font.Font(io.BytesIO(data), size)

        if self.screen_height >= 900:
            self.font_title = _font(title_font_bytes, 78)
            self.font_title_small = _font(title_font_bytes, 60)
            self.font_hud_score = _font(font_bytes, 76)
            self.font_large = _font(font_bytes, 56)
            self.font_medium = _font(font_bytes, 34)
            self.font_small = _font(font_bytes, 28)
            self.font_verysmall = _font(font_bytes, 22)
            self.font_micro = _font(font_bytes, 19)
            self.font_tiny = _font(font_bytes, 17)
        else:
            self.font_title = _font(title_font_bytes, 68)
            self.font_title_small = _font(title_font_bytes, 54)
            self.font_hud_score = _font(font_bytes, 66)
            self.font_large = _font(font_bytes, 50)
            self.font_medium = _font(font_bytes, 30)
            self.font_small = _font(font_bytes, 25)
            self.font_verysmall = _font(font_bytes, 20)
            self.font_micro = _font(font_bytes, 17)
            self.font_tiny = _font(font_bytes, 15)
        self.half_width = self.screen_width // 2
        self.half_height = self.screen_height // 2
        self.third_width = self.screen_width // 3
        min_horizontal_gap = max(12, self.screen_width // 58)
        preferred_side_width = max(172, min(308, int(self.screen_width * 0.205)))
        minimum_hole_width = int(self.screen_width * 0.47)
        maximum_hole_width = int(self.screen_width * 0.56)
        max_side_width = (
            self.screen_width - minimum_hole_width - 4 * min_horizontal_gap
        ) // 2
        self.frame_score_width = max(156, min(preferred_side_width, max_side_width))
        self.hole_frame_width = (
            self.screen_width - 2 * self.frame_score_width - 4 * min_horizontal_gap
        )
        self.hole_frame_width = max(
            minimum_hole_width,
            min(maximum_hole_width, self.hole_frame_width),
        )
        remaining_width = (
            self.screen_width - (2 * self.frame_score_width) - self.hole_frame_width
        )
        self.frame_space_x = max(min_horizontal_gap, remaining_width // 4)
        self.frame_player_width = self.frame_score_width
        self.hole_rect_height = int(self.screen_height / 2.18)
        self.frame_space_y = 16
        self.border_holes = 0
        self.hole_frame_border = 7
        self.hole_space = self.hole_rect_height / 23.5
        self.clock = pygame.time.Clock()
        self.resources = {}
        self.time_warning_channel = None
        self.time_warning_next_allowed = 0.0
        self.time_warning_level = -1
        self.load_ressources()
        self.ui = DisplayUIService(self)
        self.effects = DisplayEffectsService(self)

    def load_ressources(self):
        try:
            self.resources["game_background"] = self.load_background(
                "images", "game_background.png"
            )
            self.resources["menu_background"] = self.load_background(
                "images", "intro.jpg"
            )
            self.resources["win_background"] = self.load_background("images", "win.png")
            self.resources["winner_banner"] = self.load_background(
                "images", "winner.png"
            )
            self.resources["roulette_image"] = self.load_image(
                "images", "roulette_image.png", scale=0.8
            )
            self.resources["roulette_devil"] = self.load_image(
                "images", "roulette_devil.png", scale=0.8
            )
            self.resources["roulette_pointer"] = self.load_image(
                "images", "roulette_pointer.png", scale=0.1
            )
            self.resources["frame_player_select"] = self.load_image(
                "images",
                "frame_player_select.png",
                width=self.frame_player_width,
                height=70,
            )
            self.resources["frame_player"] = self.load_image(
                "images", "frame_player.png", width=self.frame_player_width, height=70
            )
            self.resources["hole"] = self.load_image(
                "images", "hole.png", width=2 * HOLE_RADIUS, height=2 * HOLE_RADIUS
            )
            self.resources["hole_score"] = self.load_image(
                "images",
                "hole_score.png",
                width=2 * HOLE_RADIUS,
                height=2 * HOLE_RADIUS,
            )
            self.resources["penalty_sound"] = self.load_sound("sounds", "fail.mp3")
            self.resources["win_sound"] = self.load_sound("sounds", "victoire.mp3")
            self.resources["intro_sound"] = self.load_sound("sounds", "intro.mp3")
            self.resources["frog_sound"] = self.load_sound("sounds", "frog.mp3")
            self.resources["stadium_celebration"] = self.load_sound(
                "sounds", "stadium_celebration.mp3"
            )
            self.resources["kool_sound"] = self.load_sound("sounds", "kool.mp3")
            self.resources["devil_laugh_sound"] = self.load_sound(
                "sounds", "devil_laugh.mp3"
            )
            self.resources["bottle_sound"] = self.load_sound("sounds", "bouteille.mp3")
            self.resources["coin_sound"] = self.create_coin_sound()
            self.resources["warning_sirens"] = [
                self.create_warning_siren_sound(level) for level in range(3)
            ]
            self.resources["warning_siren"] = self.resources["warning_sirens"][0]
            self.resources["roulette_sound"] = self.load_sound("sounds", "roulette.mp3")
            self.resources["roulette_end_sound"] = self.load_sound(
                "sounds", "roulette_end.mp3"
            )
            self.resources["applause"] = self.load_sound("sounds", "aplaudissement.mp3")
            self.resources["winner_banner"] = pygame.transform.scale(
                self.resources["winner_banner"], (50, 50)
            )
            if pygame.mixer.get_init() is not None:
                channel_count = pygame.mixer.get_num_channels()
                if channel_count > 0:
                    self.time_warning_channel = pygame.mixer.Channel(channel_count - 1)
        except Exception as error:
            logging.error(f"Failed to load resources: {error}")
            self.display_error_message("Failed to load resources. Exiting...")
            raise RuntimeError("Failed to load display resources") from error

    def draw_i2c_connecting(self):
        """Draw a small banner at the bottom of the screen while I2C is connecting."""
        bar_h = max(28, self.screen_height // 24)
        bar = pygame.Surface((self.screen_width, bar_h), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 180))
        font = pygame.font.SysFont(None, bar_h - 4)
        text = font.render("⏳  Connexion manette en cours…", True, (255, 200, 60))
        bar.blit(text, text.get_rect(center=(self.screen_width // 2, bar_h // 2)))
        self.screen.blit(bar, (0, self.screen_height - bar_h))
        pygame.display.flip()

    def prepare_surface(self, surface):
        if surface.get_alpha() is not None:
            return surface.convert_alpha()
        return surface.convert()

    def _show_loading_screen(self):
        self.screen.fill((10, 10, 10))
        font = pygame.font.SysFont(None, max(32, self.screen_height // 20))
        text = font.render("Chargement...", True, (200, 200, 200))
        self.screen.blit(
            text,
            text.get_rect(center=(self.screen_width // 2, self.screen_height // 2)),
        )
        pygame.display.flip()

    def _surface_cache_path(self, src_path, width, height, ext):
        """Return cache file path keyed by source filename + target dimensions."""
        os.makedirs(_CACHE_DIR, exist_ok=True)
        basename = os.path.basename(src_path).replace(".", "_")
        return os.path.join(_CACHE_DIR, f"{basename}_{width}x{height}{ext}")

    def _save_surface_cache(self, surface, cache_path, has_alpha):
        """Serialise a surface to cache: BMP for opaque, binary for alpha."""
        if has_alpha:
            w, h = surface.get_size()
            raw = pygame.image.tostring(surface, "RGBA")
            header = struct.pack(">HHBI", w, h, 1, len(raw))
            with open(cache_path, "wb") as f:
                f.write(header)
                f.write(raw)
        else:
            pygame.image.save(surface, cache_path)

    def _load_surface_cache(self, cache_path, has_alpha):
        """Deserialise a surface from cache."""
        if has_alpha:
            with open(cache_path, "rb") as f:
                header = f.read(9)
                w, h, _, _ = struct.unpack(">HHBI", header)
                raw = f.read()
            return pygame.image.frombytes(raw, (w, h), "RGBA").convert_alpha()
        else:
            return pygame.image.load(cache_path).convert()

    @staticmethod
    def _read_png_size(path):
        """Read PNG image dimensions from the file header (no full decode)."""
        try:
            with open(path, "rb") as f:
                f.seek(16)
                w, h = struct.unpack(">II", f.read(8))
            return w, h
        except Exception:
            return None

    @staticmethod
    def _source_has_alpha(path):
        """Check if an image file has an alpha channel from its raw header.

        This avoids dependence on the display surface format (which varies between
        dummy and real Wayland display modes).
        """
        lower = path.lower()
        if lower.endswith((".jpg", ".jpeg")):
            return False  # JPEG never carries an alpha channel
        if lower.endswith(".png"):
            try:
                with open(path, "rb") as f:
                    f.seek(25)
                    color_type = struct.unpack("B", f.read(1))[0]
                    # PNG color types 4 (greyscale+alpha) and 6 (RGBA) have alpha
                    return color_type in (4, 6)
            except Exception:
                pass
        return True  # Safe default: treat unknown formats as having alpha

    def _cached_surface(self, src_path, build_fn, target_size=None):
        """Load a surface from cache if fresh, otherwise build once and cache.

        Uses BMP for opaque surfaces (fastest SDL load) and raw RGBA binary
        for surfaces with an alpha channel.
        """
        try:
            src_mtime = os.path.getmtime(src_path)
            w, h = target_size or self.screen.get_size()
            has_alpha = self._source_has_alpha(src_path)
            ext = ".surfcache" if has_alpha else ".bmp"
            cache_path = self._surface_cache_path(src_path, w, h, ext)
            if os.path.exists(cache_path) and os.path.getmtime(cache_path) >= src_mtime:
                return self._load_surface_cache(cache_path, has_alpha)
            surface = build_fn()
            self._save_surface_cache(surface, cache_path, has_alpha)
            return surface
        except Exception as e:
            logging.warning(f"Surface cache miss ({src_path}): {e}")
            return build_fn()

    def load_background(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        return self._cached_surface(
            path,
            lambda: pygame.transform.smoothscale(
                self.prepare_surface(pygame.image.load(path)), self.screen.get_size()
            ),
        )

    def load_image(self, folder, filename, scale=None, width=None, height=None):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)

        if scale is None and width is None:
            return self.prepare_surface(pygame.image.load(path))

        # Determine target size — avoid loading the full image if possible
        _loaded = []
        if scale is not None:
            png_size = self._read_png_size(path)
            if png_size:
                orig_w, orig_h = png_size
            else:
                # Fallback for non-PNG: load image once and reuse below
                _loaded = [self.prepare_surface(pygame.image.load(path))]
                orig_w, orig_h = _loaded[0].get_size()
            _, screen_h = self.screen.get_size()
            new_h = int(screen_h * scale)
            new_w = int(new_h * orig_w / orig_h)
            target = (new_w, new_h)
        else:
            if width is None or height is None:
                raise ValueError(
                    "width and height are required when scale is not provided"
                )
            target = (int(width), int(height))

        # Check cache with known target and source-derived alpha flag — zero decode on hit
        has_alpha = self._source_has_alpha(path)
        ext = ".surfcache" if has_alpha else ".bmp"
        try:
            src_mtime = os.path.getmtime(path)
            cache_path = self._surface_cache_path(path, *target, ext)
            if os.path.exists(cache_path) and os.path.getmtime(cache_path) >= src_mtime:
                return self._load_surface_cache(cache_path, has_alpha)
        except Exception as e:
            logging.warning(f"Image cache check failed ({path}): {e}")

        # Cache miss: load once (reuse surface if already loaded above for dimensions)
        orig = _loaded[0] if _loaded else self.prepare_surface(pygame.image.load(path))
        result = self.prepare_surface(pygame.transform.smoothscale(orig, target))
        try:
            self._save_surface_cache(
                result, self._surface_cache_path(path, *target, ext), has_alpha
            )
        except Exception as e:
            logging.warning(f"Image cache save failed ({path}): {e}")
        return result

    def load_sound(self, folder, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "assets", folder, filename)
        if pygame.mixer.get_init() is None:
            return None
        if (folder, filename) not in self.resources:
            try:
                self.resources[(folder, filename)] = pygame.mixer.Sound(path)
            except Exception as error:
                logging.warning(
                    "Failed to load sound %s/%s: %s",
                    folder,
                    filename,
                    error,
                )
                self.resources[(folder, filename)] = None
        return self.resources[(folder, filename)]

    def create_coin_sound(self):
        mixer_config = pygame.mixer.get_init()
        if mixer_config is None:
            return None

        sample_rate, _, channels = mixer_config
        duration = 0.12
        frame_count = int(sample_rate * duration)
        fade_start = int(frame_count * 0.55)
        amplitude = 0.34
        samples = array("h")

        for index in range(frame_count):
            progress = index / sample_rate
            envelope = 1.0 - (index / frame_count)
            if index >= fade_start:
                envelope *= max(
                    0.0, 1.0 - ((index - fade_start) / (frame_count - fade_start))
                )

            tone = sin(2 * pi * 1320 * progress)
            tone += 0.55 * sin(2 * pi * 1760 * progress)
            tone += 0.25 * sin(2 * pi * 2640 * progress)
            sample_value = int(32767 * amplitude * envelope * tone / 1.8)
            for _ in range(channels):
                samples.append(sample_value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def create_warning_siren_sound(self, level=0):
        mixer_config = pygame.mixer.get_init()
        if mixer_config is None:
            return None

        sample_rate, _, channels = mixer_config
        level = max(0, min(2, int(level)))
        duration = (0.42, 0.31, 0.22)[level]
        frame_count = int(sample_rate * duration)
        amplitude = (0.18, 0.21, 0.25)[level]
        low_freq = (720, 860, 980)[level]
        high_freq = (980, 1180, 1420)[level]
        tremolo_rate = 5.6 + level * 1.35
        samples = array("h")

        for index in range(frame_count):
            progress = index / max(1, frame_count - 1)
            timeline = index / sample_rate

            if progress < 0.58:
                local_progress = progress / 0.58
                frequency = low_freq + (high_freq - low_freq) * (local_progress**0.72)
            else:
                local_progress = (progress - 0.58) / 0.42
                tail_freq = low_freq + (high_freq - low_freq) * 0.32
                frequency = high_freq - (high_freq - tail_freq) * (local_progress**0.82)

            attack = min(1.0, progress / 0.08)
            release = min(1.0, (1.0 - progress) / 0.16)
            envelope = min(attack, release)
            envelope *= 0.82 + 0.18 * sin(progress * pi)
            tremolo = 0.86 + 0.14 * sin(2 * pi * tremolo_rate * timeline)

            tone = sin(2 * pi * frequency * timeline)
            tone += 0.36 * sin(2 * pi * (frequency * 1.5) * timeline)
            tone += 0.26 * sin(2 * pi * (frequency * 2.0) * timeline)
            tone += 0.1 * sin(2 * pi * (frequency * 2.98) * timeline)
            tone += 0.08 * sin(2 * pi * (frequency * 0.5) * timeline)
            sample_value = int(32767 * amplitude * envelope * tremolo * tone / 1.8)
            for _ in range(channels):
                samples.append(sample_value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def stop_time_warning_audio(self):
        if (
            self.time_warning_channel is not None
            and self.time_warning_channel.get_busy()
        ):
            self.time_warning_channel.fadeout(90)
        self.time_warning_next_allowed = 0.0
        self.time_warning_level = -1

    def update_time_warning_audio(self, challenge_state):
        if (
            challenge_state is None
            or challenge_state.get("type") != "time_attack"
            or challenge_state.get("awaiting_start")
            or not challenge_state.get("low_time")
        ):
            self.stop_time_warning_audio()
            return

        warning_sirens = self.resources.get("warning_sirens") or []
        if not warning_sirens or self.time_warning_channel is None:
            return

        now = time.monotonic()
        remaining = max(0.0, float(challenge_state.get("remaining_seconds", 0.0)))
        duration = max(1.0, float(challenge_state.get("turn_duration", 1.0)))
        urgency = 1.0 - min(1.0, remaining / duration)

        if remaining <= 1.5 or urgency >= 0.88:
            level = 2
        elif remaining <= 3.0 or urgency >= 0.68:
            level = 1
        else:
            level = 0

        pulse_interval = max(0.14, 0.82 - 0.68 * urgency)
        volume = 0.24 + 0.36 * urgency
        warning_sound = warning_sirens[min(level, len(warning_sirens) - 1)]

        if self.time_warning_channel.get_busy() or now < self.time_warning_next_allowed:
            return

        self.time_warning_channel.set_volume(volume)
        self.time_warning_channel.play(warning_sound, fade_ms=40)
        self.time_warning_next_allowed = now + pulse_interval
        self.time_warning_level = level

    def display_error_message(self, message):
        self.screen.fill((0, 0, 0))
        error_text = self.font_large.render(message, True, (255, 0, 0))
        self.screen.blit(
            error_text,
            (
                self.half_width - error_text.get_width() // 2,
                self.half_height,
            ),
        )
        pygame.display.flip()
        time.sleep(3)

    def get_hole_position(self, hole_value, position):
        center_x = self.screen_width / 2
        outer_column_offset = self.hole_frame_width * 0.382
        inner_column_offset = self.hole_frame_width * 0.222
        if hole_value == "20":
            return (
                [
                    center_x - outer_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 5 * HOLE_RADIUS
                    + 5 * self.border_holes
                    + 2 * self.hole_space,
                ]
                if position == 1
                else [
                    center_x + outer_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 5 * HOLE_RADIUS
                    + 5 * self.border_holes
                    + 2 * self.hole_space,
                ]
            )
        if hole_value == "25":
            return (
                [
                    center_x - outer_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 3 * HOLE_RADIUS
                    + 3 * self.border_holes
                    + self.hole_space,
                ]
                if position == 1
                else [
                    center_x + outer_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + 3 * HOLE_RADIUS
                    + 3 * self.border_holes
                    + self.hole_space,
                ]
            )
        if hole_value == "40":
            return (
                [
                    center_x - inner_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 1.5
                    + HOLE_RADIUS * 4
                    + self.border_holes * 4,
                ]
                if position == 1
                else [
                    center_x + inner_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 1.5
                    + HOLE_RADIUS * 4
                    + self.border_holes * 4,
                ]
            )
        if hole_value == "50":
            return (
                [
                    center_x - inner_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space / 2
                    + HOLE_RADIUS * 2
                    + self.border_holes * 2,
                ]
                if position == 1
                else [
                    center_x + inner_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space / 2
                    + HOLE_RADIUS * 2
                    + self.border_holes * 2,
                ]
            )
        if hole_value == "100":
            return (
                [
                    center_x - inner_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 2.5
                    + HOLE_RADIUS * 6
                    + self.border_holes * 6,
                ]
                if position == 1
                else [
                    center_x + inner_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + self.hole_space * 2.5
                    + HOLE_RADIUS * 6
                    + self.border_holes * 6,
                ]
            )
        if hole_value == "150":
            return (
                [
                    center_x - outer_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + HOLE_RADIUS
                    + self.border_holes,
                ]
                if position == 1
                else [
                    center_x + outer_column_offset,
                    self.frame_space_y
                    + self.hole_frame_border
                    + HOLE_RADIUS
                    + self.border_holes,
                ]
            )
        if hole_value == "200":
            return [
                center_x,
                self.frame_space_y
                + self.hole_frame_border
                + 3 * HOLE_RADIUS
                + 3 * self.border_holes
                + self.hole_space,
            ]
        if hole_value == "ROUL":
            return [
                center_x,
                self.frame_space_y
                + self.hole_frame_border
                + HOLE_RADIUS
                + self.border_holes,
            ]
        return None

    def draw_chrome_rect(self, *args, **kwargs):
        return self.ui.draw_chrome_rect(*args, **kwargs)

    def draw_text_with_outline(self, *args, **kwargs):
        return self.ui.draw_text_with_outline(*args, **kwargs)

    def draw_menu(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.ui.draw_menu(*args, **kwargs)

    def draw_sensor_analysis(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.ui.draw_sensor_analysis(*args, **kwargs)

    def draw_end_menu(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.ui.draw_end_menu(*args, **kwargs)

    def play_intro(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.ui.play_intro(*args, **kwargs)

    def draw_game(self, *args, **kwargs):
        return self.ui.draw_game(*args, **kwargs)

    def draw_holes(self, *args, **kwargs):
        return self.ui.draw_holes(*args, **kwargs)

    def draw_static_elements(self, *args, **kwargs):
        return self.ui.draw_static_elements(*args, **kwargs)

    def display_grouped_players(self, *args, **kwargs):
        return self.ui.display_grouped_players(*args, **kwargs)

    def draw_status_banner(self, *args, **kwargs):
        return self.ui.draw_status_banner(*args, **kwargs)

    def draw_text_with_shadow(self, *args, **kwargs):
        return self.ui.draw_text_with_shadow(*args, **kwargs)

    def calculate_group_layout(self, *args, **kwargs):
        return self.ui.calculate_group_layout(*args, **kwargs)

    def group_players(self, *args, **kwargs):
        return self.ui.group_players(*args, **kwargs)

    def handle_animation_events(self, *args, **kwargs):
        return self.effects.handle_animation_events(*args, **kwargs)

    def wait_with_event_pump(self, *args, **kwargs):
        return self.effects.wait_with_event_pump(*args, **kwargs)

    def ease_out_cubic(self, *args, **kwargs):
        return self.effects.ease_out_cubic(*args, **kwargs)

    def ease_in_out_sine(self, *args, **kwargs):
        return self.effects.ease_in_out_sine(*args, **kwargs)

    def ease_out_back(self, *args, **kwargs):
        return self.effects.ease_out_back(*args, **kwargs)

    def get_rgb(self, *args, **kwargs):
        return self.effects.get_rgb(*args, **kwargs)

    def animate_scene(self, *args, **kwargs):
        return self.effects.animate_scene(*args, **kwargs)

    def draw_overlay(self, *args, **kwargs):
        return self.effects.draw_overlay(*args, **kwargs)

    def draw_glow_circle(self, *args, **kwargs):
        return self.effects.draw_glow_circle(*args, **kwargs)

    def draw_radial_burst(self, *args, **kwargs):
        return self.effects.draw_radial_burst(*args, **kwargs)

    def draw_confetti(self, *args, **kwargs):
        return self.effects.draw_confetti(*args, **kwargs)

    def clamp(self, *args, **kwargs):
        return self.effects.clamp(*args, **kwargs)

    def lerp(self, *args, **kwargs):
        return self.effects.lerp(*args, **kwargs)

    def draw_lily_pad(self, *args, **kwargs):
        return self.effects.draw_lily_pad(*args, **kwargs)

    def draw_frog_character(self, *args, **kwargs):
        return self.effects.draw_frog_character(*args, **kwargs)

    def draw_goal_animation(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_goal_animation(*args, **kwargs)

    def draw_penalty(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_penalty(*args, **kwargs)

    def draw_player_win(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_player_win(*args, **kwargs)

    def draw_win(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.draw_win(*args, **kwargs)

    def animation_bottle(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_bottle(*args, **kwargs)

    def animation_little_frog(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_little_frog(*args, **kwargs)

    def animation_roulette(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_roulette(*args, **kwargs)

    def animation_bonus_roulette(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_bonus_roulette(*args, **kwargs)

    def animation_malus_roulette(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_malus_roulette(*args, **kwargs)

    def animation_large_frog(self, *args, **kwargs):
        self.stop_time_warning_audio()
        return self.effects.animation_large_frog(*args, **kwargs)

    def run_fireworks(self, *args, **kwargs):
        return self.effects.run_fireworks(*args, **kwargs)
