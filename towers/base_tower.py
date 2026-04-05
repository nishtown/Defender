import random
import math

import pygame.draw
from pygame import Vector2

from settings import *
from entity import *

class BaseTower(Entity):
    def __init__(self, main, x, y, width, height):
        super().__init__(main, x,y, width, height)

        #ADJUSTABLE SETTINGS
        self.rotation_speed = 90
        self.fire_rate = 1.0  # shots per second
        self.damage = 1
        self.turn_tolerance = 8
        self.range = 128
        self.image = None
        self.image_firing = None
        self.fire_sound = None
        self.build_time = 3  # total seconds to build
        self.cost = 150

        #STATIC VARIABLES (SHOULD NOT CHANGE OUTSIDE THE CLASS)

        if self.image is not None:
            self.original_image = self.image.copy() #creates a copy of the original image so we only manipulate the original
        else:
            self.original_image = None

        if self.image is not None:
            self.image = pygame.transform.rotate(self.image, 0)

        if self.fire_sound is not None:
            self.fire_sound.set_volume(0.2)

        self.pos = Vector2(x, y)
        self.rect.center = self.pos
        self.angle = 0

        self.firing = False
        self.firing_frame_count = 0
        self.firing_frame_duration = 3  # exactly 3 frames
        self.fire_cooldown = 0.0

        self.target = None

        self.selected = False
        self.is_hovered = False

        self.is_building = True
        self.build_progress = 0.0  # current elapsed build time
        self.min_build_transparency = 128  # 50% transparent
        self.max_build_transparency = 255
        self.build_font = pygame.font.SysFont(None, 16)


        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_rect = self.range_image.get_rect()

    def set_volume(self, volume):
        self.fire_sound.set_volume(volume)

    def rebuild_image(self):
        if self.image is not None:
            self.original_image = self.image.copy()
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.pos)

    def rebuild_range(self):
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            self.range_image,
            (220, 220, 220),
            (self.range, self.range),
            self.range,
            self.range
        )

        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect(center=self.rect.center)

    def reload(self):
        self.rebuild_image()
        self.rebuild_range()

    def update_build_timer(self, dt):
        if not self.is_building:
            return

        self.build_progress += dt

        if self.build_progress >= self.build_time:
            self.build_progress = self.build_time
            self.is_building = False

    def get_build_transparency(self):
        if not self.is_building:
            return self.max_build_transparency

        progress_ratio = self.build_progress / self.build_time
        transparency = self.min_build_transparency + (self.max_build_transparency - self.min_build_transparency) * progress_ratio
        return int(transparency)

    def get_build_ratio(self):
        if self.build_time <= 0:
            return 1.0

        return max(0.0, min(1.0, self.build_progress / self.build_time))

    #Finds a target that may of entered in the range area
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

    def build_range_image(self):
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(
            self.range_image,
            (220, 220, 220),
            (self.range, self.range),
            self.range,
            self.range
        )
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect(center=self.rect.center)

    #Determines if the tower has an actual target, used for handling the targetting rotation
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

    #rotates the tower towards the target
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

    #used to determine the angle different between current angle and the target
    def angle_difference(self, target_angle):
        return (target_angle - self.angle + 180) % 360 - 180


    #Fires - Plays the sound and does damage.
    def fire(self):
        if self.target is None:
            return
        self.firing = True
        self.firing_frame_count = 0
        if self.fire_sound:
            self.fire_sound.play()
        self.apply_attack()


    def apply_attack(self):
        raise NotImplementedError("tower must implement apply_attack()")



    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        self.update_build_timer(dt)


        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt
            if self.fire_cooldown < 0:
                self.fire_cooldown = 0

        if self.firing:
            self.firing_frame_count += 1

            if self.firing_frame_count >= self.firing_frame_duration:
                self.firing = False
                self.firing_frame_count = 0

        if not self.is_building and self.has_valid_target():
            direction = self.target.pos - self.pos

            if direction.length_squared() > 0:
                target_angle = direction.as_polar()[1]
                self.rotate_towards(target_angle, dt)

                angle_diff = abs(self.angle_difference(target_angle))

                if angle_diff <= self.turn_tolerance and self.fire_cooldown <= 0:
                    self.fire()
                    self.fire_cooldown = 1 / self.fire_rate

        base_image = self.image_firing if self.firing else self.original_image
        if base_image is not None:
            self.image = pygame.transform.rotate(base_image, -self.angle)
            self.rect = self.image.get_rect(center=self.pos)

        super().update(dt)



    def draw(self, surface):

        if self.selected:
            self.draw_range(surface)

        if self.image is not None:
            img = self.image.copy()

            if self.is_building:
                img.set_alpha(self.get_build_transparency())
                self.draw_build_text(surface)
                self.draw_build_bar(surface)

            surface.blit(img, self.rect)
            if self.main.debug_mode:
                pygame.draw.rect(surface, RED, self.rect, 1)


    #draws the range circle
    def draw_range(self, surface, center=None):
        if center is None:
            center = self.rect.center

        surface.blit(self.range_image, self.range_image.get_rect(center=center))

    def draw_build_bar(self, surface):
        if not self.is_building:
            return

        ratio = self.get_build_ratio()

        bar_width = self.rect.width
        bar_height = 6
        bar_x = self.rect.left
        bar_y = self.rect.bottom + 12

        # background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (40, 40, 40), bg_rect)

        # fill
        fill_width = int(bar_width * ratio)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(surface, (100, 220, 100), fill_rect)

        # border
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 1)

    def draw_build_text(self, surface):
        if not self.is_building:
            return

        text_surface = self.build_font.render("Building...", True, (255, 255, 255))

        text_rect = text_surface.get_rect()
        text_rect.centerx = self.rect.centerx
        text_rect.bottom = self.rect.bottom + 8  # sits just above the bar

        # Optional: add subtle shadow for readability
        shadow = self.build_font.render("Building...", True, (0, 0, 0))
        shadow_rect = text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1

        surface.blit(shadow, shadow_rect)
        surface.blit(text_surface, text_rect)