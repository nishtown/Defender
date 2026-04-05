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
        self.damage = 1
        self.turn_tolerance = 8
        self.range = 128
        self.image = pygame.image.load("towers/assets/tower2.png").convert_alpha()
        self.image_firing = pygame.image.load("towers/assets/tower2_fire.png").convert_alpha()
        self.fire_sound = pygame.mixer.Sound("towers/assets/tower1_fire.mp3")
        self.build_time = 3  # total seconds to build
        self.cost = 150


        self.reload() #needed to reload all the images\sounds of the base


    def apply_attack(self):
        if self.target:
            self.target.health -= self.damage