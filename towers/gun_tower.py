import random
import math

import pygame.draw
from pygame import Vector2

from settings import *
from entity import *
from .base_tower import BaseTower

class GunTower(BaseTower):
    def __init__(self, main, x, y, width, height):
        super().__init__(main, x, y, width, height)
        self.rotation_speed = 120
        self.fire_rate = 2.0  # shots per second
        self.damage = 2
        self.turn_tolerance = 8
        self.range = 128
        self.image = pygame.image.load(asset_path("towers","assets","tower2.png")).convert_alpha()
        self.image_firing = pygame.image.load(asset_path("towers","assets","tower2_fire.png")).convert_alpha()
        self.fire_sound = pygame.mixer.Sound(asset_path("towers","assets","tower2_fire.ogg"))
        self.build_time = 10  # total seconds to build
        self.cost = 750
        self.set_volume(0.08)


        self.reload() #needed to reload all the images\sounds of the base


    def apply_attack(self):
        if self.target:
            self.target.take_damage(self.damage)