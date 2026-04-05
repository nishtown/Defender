import random
import math

import pygame.draw
from pygame import Vector2

from settings import *
from entity import *
from .base_tower import BaseTower
from particle_animation import ParticleAnimation

class RocketTower(BaseTower):
    def __init__(self, main, x, y, width, height):
        super().__init__(main, x, y, width, height)
        self.rotation_speed = 50
        self.fire_rate = 1.0  # shots per second
        self.damage = 10
        self.turn_tolerance = 16
        self.range = 176
        self.image = pygame.image.load(asset_path("towers", "assets", "tower4.png")).convert_alpha()
        self.image_firing = pygame.image.load(asset_path("towers", "assets", "tower4_fire.png")).convert_alpha()
        self.fire_sound = pygame.mixer.Sound(asset_path("towers", "assets", "explosion.ogg"))
        self.build_time = 30  # total seconds to build
        self.cost = 2500
        self.set_volume(0.2)


        self.reload() #needed to reload all the images\sounds of the base


    def apply_attack(self):
        if self.target:
            self.target.take_damage(self.damage)
            particle = ParticleAnimation(
                x=self.target.rect.centerx,
                y=self.target.rect.centery,
                sheet_path=asset_path("towers", "assets", "explosion.png"),
                frame_width=64,
                frame_height=64,
                frame_count=5,
                fps=15,
                loop=False,
                scale=(196,196),
                kill_on_finish=True
            )
            self.main.particle_group.add(particle, layer=10)