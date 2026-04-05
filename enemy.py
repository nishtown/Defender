import random
import math

from pygame import Vector2

from settings import *
from entity import *
from particle_animation import *

class Enemy(Entity):
    def __init__(self, main, width, height, waypoints, health):
        super().__init__(main, waypoints[0][0], waypoints[0][1], width, height)
        self.image = pygame.image.load(asset_path("assets", "enemy", "enemy.png")).convert_alpha()
        self.original_image = self.image.copy()
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.pos = Vector2(waypoints[0])
        self.speed = 1
        self.direction = None
        self.health = health
        self.max_health = health
        self.rect.center = self.pos

        self.has_escaped = False
        self.is_dead = False
        self.score_value = 10
        valueincrement = (self.health // 4)
        if valueincrement > 0:
            self.gold_value = 10 * valueincrement
        else:
            self.gold_value = 10


        self.visible_width = pygame.mask.from_surface(self.original_image).get_bounding_rects()[0].width

    def update(self, dt):
        if self.current_waypoint_index >= len(self.waypoints) - 1:
            return

        target_index = self.current_waypoint_index + 1
        target_pos = Vector2(self.waypoints[target_index])

        if self.pos.distance_to(target_pos) < 1:
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.waypoints) - 1:
                self.has_escaped = True
                return

            target_index = self.current_waypoint_index + 1
            target_pos = Vector2(self.waypoints[target_index])


        direction = target_pos - self.pos
        direction_angle = direction.as_polar()[1]
        change_direction = False
        if self.direction is None or direction_angle != direction:
            self.direction = direction_angle
            change_direction = True


        self.pos = self.pos.move_towards(target_pos, self.speed)
        self.rect.center = self.pos
        if change_direction:
            self.image = pygame.transform.rotate(self.original_image, -self.direction)
            self.rect = self.image.get_rect(center=self.pos)


        if self.health <= 0:
            self.die()


        super().update(dt)

    def take_damage(self, amount):
        if self.is_dead:
            return False

        self.health -= amount

        if self.health <= 0:
            self.die()
            return True

        return False

    def die(self):
        if self.is_dead:
            return

        self.is_dead = True
        particle = ParticleAnimation(
            x=self.rect.centerx,
            y=self.rect.centery,
            sheet_path=asset_path("assets", "enemy", "blood.png"),
            frame_width=100,
            frame_height=100,
            frame_count=18,
            fps=30,
            loop=False,
            kill_on_finish=True
        )
        self.main.particle_group.add(particle, layer=1)


    def draw(self, surface):
        super().draw(surface)

        if self.health < self.max_health:
            bar_width = self.visible_width
            bar_x = (self.rect.centerx - self.visible_width/2)
            ratio = self.health / self.max_health
            pygame.draw.rect(surface, RED, (bar_x, self.rect.centery - 20, self.visible_width, 3))
            pygame.draw.rect(surface, GREEN, (bar_x, self.rect.centery - 20, self.visible_width * ratio,3))





