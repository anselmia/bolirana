import pygame
import random
import sys
import math


class FireworkParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 4)
        self.color = color
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-3, 3)
        self.gravity = 0.1
        self.lifespan = 255

    def update(self):
        self.velocity_y += self.gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifespan -= 2

    def draw(self, screen):
        if self.lifespan > 0:
            alpha = max(0, min(255, self.lifespan))
            particle_color = (*self.color, alpha)
            pygame.draw.circle(
                screen, particle_color, (int(self.x), int(self.y)), self.radius
            )


class Firework:
    def __init__(self, x, y, color, num_particles):
        self.particles = [FireworkParticle(x, y, color) for _ in range(num_particles)]

    def update(self):
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

    def is_dead(self):
        return all(particle.lifespan <= 0 for particle in self.particles)
