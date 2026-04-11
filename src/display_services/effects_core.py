# pyright: reportAttributeAccessIssue=false
import math
import os
import time

import pygame

try:
    import cv2
except Exception:
    cv2 = None


class EffectsCoreMixin:
    def get_cached_surface(self, cache_name, cache_key, builder, max_entries=256):
        full_key = (cache_name, cache_key)
        cached_surface = self._surface_cache.get(full_key)
        if cached_surface is not None:
            return cached_surface

        if len(self._surface_cache) >= max_entries:
            self._surface_cache.clear()

        cached_surface = builder()
        self._surface_cache[full_key] = cached_surface
        return cached_surface

    def get_progress_bucket(self, progress, buckets=12):
        return max(0, min(buckets, int(round(self.clamp(progress) * buckets))))

    def handle_animation_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def wait_with_event_pump(self, seconds):
        end_time = time.monotonic() + seconds
        while time.monotonic() < end_time:
            if not self.handle_animation_events():
                return False
            self.display.clock.tick(30)
        return True

    def ease_out_cubic(self, progress):
        return 1 - (1 - progress) ** 3

    def ease_in_out_sine(self, progress):
        return -(math.cos(math.pi * progress) - 1) / 2

    def ease_out_back(self, progress):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (progress - 1) ** 3 + c1 * (progress - 1) ** 2

    def clamp(self, value, minimum=0.0, maximum=1.0):
        return max(minimum, min(maximum, value))

    def lerp(self, start, end, progress):
        return start + (end - start) * progress

    def get_rgb(self, color):
        if isinstance(color, pygame.Color):
            return color.r, color.g, color.b
        return color[:3]

    def animate_scene(self, duration, renderer, background=None, fps=60):
        start_time = time.monotonic()
        while True:
            if not self.handle_animation_events():
                return False

            progress = min((time.monotonic() - start_time) / duration, 1.0)
            if background is not None:
                self.display.screen.blit(background, (0, 0))

            renderer(progress)
            pygame.display.flip()

            if progress >= 1.0:
                return True

            self.display.clock.tick(fps)

    def play_video_clip(
        self,
        video_path,
        fill_color=(0, 0, 0),
        sound_name=None,
        sound_volume=1.0,
        sound_fade_ms=0,
    ):
        if cv2 is None or not os.path.exists(video_path):
            return False

        capture = cv2.VideoCapture(video_path)
        if not capture.isOpened():
            capture.release()
            return False

        sound_channel = None
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        target_fps = 30 if not source_fps or source_fps <= 1 else int(round(source_fps))
        target_fps = max(12, min(60, target_fps))

        try:
            if sound_name is not None:
                sound_channel = self.play_sound_cue(
                    sound_name,
                    volume=sound_volume,
                    fade_ms=sound_fade_ms,
                    stop_existing=True,
                    loops=-1,
                )

            while True:
                if not self.handle_animation_events():
                    return False

                has_frame, frame = capture.read()
                if not has_frame:
                    break

                frame_height, frame_width = frame.shape[:2]
                if frame_width <= 0 or frame_height <= 0:
                    continue

                scale = min(
                    self.display.screen_width / frame_width,
                    self.display.screen_height / frame_height,
                )
                scaled_size = (
                    max(1, int(frame_width * scale)),
                    max(1, int(frame_height * scale)),
                )
                interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
                resized = cv2.resize(frame, scaled_size, interpolation=interpolation)
                rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.image.frombuffer(
                    rgb_frame.tobytes(), scaled_size, "RGB"
                ).convert()

                self.display.screen.fill(fill_color)
                frame_rect = frame_surface.get_rect(
                    center=(
                        self.display.screen_width // 2,
                        self.display.screen_height // 2,
                    )
                )
                self.display.screen.blit(frame_surface, frame_rect)
                pygame.display.flip()
                self.display.clock.tick(target_fps)
        finally:
            if sound_channel is not None:
                sound_channel.stop()
            capture.release()

        return True

    def play_sound_cue(
        self,
        sound_name,
        volume=1.0,
        fade_ms=0,
        maxtime=0,
        stop_existing=False,
        loops=0,
    ):
        sound = self.display.resources.get(sound_name)
        if sound is None:
            return
        if stop_existing:
            sound.stop()
        channel = pygame.mixer.find_channel(True)
        if channel is None:
            return
        channel.set_volume(volume)
        channel.play(sound, loops=loops, maxtime=maxtime, fade_ms=fade_ms)
        return channel

    def trigger_cue(
        self,
        tracker,
        cue_name,
        threshold,
        progress,
        sound_name,
        volume=1.0,
        fade_ms=0,
        maxtime=0,
    ):
        if cue_name in tracker or progress < threshold:
            return
        tracker.add(cue_name)
        self.play_sound_cue(
            sound_name,
            volume=volume,
            fade_ms=fade_ms,
            maxtime=maxtime,
        )
