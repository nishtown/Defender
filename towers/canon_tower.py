import random
import math

import pygame.draw
from pygame import Vector2

from settings import *
from entity import *
from .base_tower import BaseTower

class CanonTower(BaseTower):
    def __init__(self, main, x, y, width, height):
        super().__init__(main, x, y, width, height)
        self.rotation_speed = 180
        self.fire_rate = 1.0  # shots per second
        self.damage = 5
        self.turn_tolerance = 14
        self.range = 160
        self.image = pygame.image.load(asset_path("towers","assets","tower3.png")).convert_alpha()
        self.image_firing = pygame.image.load(asset_path("towers","assets","tower3_fire.png")).convert_alpha()
        self.fire_sound = pygame.mixer.Sound(asset_path("towers","assets","tower3_fire.ogg"))
        self.build_time = 20  # total seconds to build
        self.cost = 1750
        self.set_volume(0.1)


        self.reload() #needed to reload all the images\sounds of the base


    def apply_attack(self):
        if self.target:
            self.target.take_damage(self.damage)