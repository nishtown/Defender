import random
import math

import pygame.draw
from pygame import Vector2

from settings import *
from entity import *

class Tower(Entity):
    def __init__(self, main, x, y, width, height):
        super().__init__(main, x,y, width, height)
        self.image = pygame.image.load("assets/tower/tower1.png").convert_alpha()
        self.image_firing = pygame.image.load("assets/tower/tower1_fire.png").convert_alpha()
        self.fire_sound = pygame.mixer.Sound("assets/sounds/tower1_fire.mp3")
        self.fire_sound.set_volume(0.5)
        self.pos = Vector2(x, y)
        self.original_image = self.image.copy()
        self.rotation_speed = 90
        self.angle = 0
        self.image = pygame.transform.rotate(self.image, 0)

        self.rect.center = self.pos

        self.firing = False
        self.firing_frame_count = 0
        self.firing_frame_duration = 3  # exactly 3 frames
        self.fire_rate = 1.0  # shots per second
        self.fire_cooldown = 0.0
        self.damage = 1
        self.turn_tolerance = 8

        self.target = None

        self.selected = False
        self.is_hovered = False

        self.range = 128
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, (220, 220, 220), (self.range, self.range), self.range, self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center



    def find_target(self, enemy_group):
        x_dist = 0
        y_dist = 0
        found_enemy = False
        for enemy in enemy_group:
            x_dist = enemy.pos[0] - self.pos.x
            y_dist = enemy.pos[1] - self.pos.y
            dist = math.sqrt(x_dist**2 + y_dist**2)
            if dist <= self.range:
                found_enemy = True
                self.target = enemy
                return

        if not found_enemy:
            self.target = None

    def has_valid_target(self):
        if self.target is None:
            return False

        if not self.target.alive():
            self.target = None
            return False

        if self.pos.distance_to(self.target.pos) > self.range:
            self.target = None
            return False

        return True

    def rotate_towards(self, target_angle, dt):
        # difference wrapped to -180 to 180
        diff = (target_angle - self.angle + 180) % 360 - 180

        max_step = self.rotation_speed * dt

        if abs(diff) <= max_step:
            self.angle = target_angle
        else:
            if diff > 0:
                self.angle += max_step
            else:
                self.angle -= max_step

        self.angle %= 360

    def angle_difference(self, target_angle):
        return (target_angle - self.angle + 180) % 360 - 180

    def fire(self):
        if self.target is None:
            return

        self.firing = True
        self.firing_frame_count = 0
        self.target.health -= self.damage
        self.fire_sound.play()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt
            if self.fire_cooldown < 0:
                self.fire_cooldown = 0

        if self.firing:
            self.firing_frame_count += 1

            if self.firing_frame_count >= self.firing_frame_duration:
                self.firing = False
                self.firing_frame_count = 0

        if self.has_valid_target():
            direction = self.target.pos - self.pos

            if direction.length_squared() > 0:
                target_angle = direction.as_polar()[1]
                self.rotate_towards(target_angle, dt)

                angle_diff = abs(self.angle_difference(target_angle))

                if angle_diff <= self.turn_tolerance and self.fire_cooldown <= 0:
                    self.fire()
                    self.fire_cooldown = 1 / self.fire_rate

        base_image = self.image_firing if self.firing else self.original_image
        self.image = pygame.transform.rotate(base_image, -self.angle)
        self.rect = self.image.get_rect(center=self.pos)

        super().update(dt)



    def draw(self, surface):
        if self.selected:
            self.draw_range(surface)

        super().draw(surface)


    def draw_range(self, surface, center=None):
        if center is None:
            center = self.rect.center

        surface.blit(self.range_image, self.range_image.get_rect(center=center))