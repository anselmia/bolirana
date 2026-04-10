# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame


class EffectsCoreMixin:
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

    def play_sound_cue(
        self,
        sound_name,
        volume=1.0,
        fade_ms=0,
        maxtime=0,
        stop_existing=False,
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
        channel.play(sound, maxtime=maxtime, fade_ms=fade_ms)
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
