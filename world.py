import pygame.mask
from pygame import surface

from settings import *
from scene import Scene
from enemy import Enemy
from tower import Tower
from button import Button
import json

class World(Scene):
    def __init__(self, main):
        super().__init__(main)
        self.font = pygame.font.SysFont(None, 60)
        self.bg_image_original = pygame.image.load("assets/levels/level1.png")
        self.bg_image_menu = pygame.image.load("assets/levels/level1_menu.png").convert_alpha()
        self.wave_completed_sound = pygame.mixer.Sound("assets/sounds/wave_completed.mp3")
        self.background_music = pygame.mixer.Sound("assets/sounds/background.mp3")
        self.background_music.set_volume(0.05)
        self.wave_completed_sound.set_volume(0.5)
        self.bg_image = pygame.transform.scale(self.bg_image_original, (LEVEL_WIDTH, LEVEL_HEIGHT))
        self.level_data = None
        self.waypoints = []
        self.path_rects = []
        self.enemy_group = pygame.sprite.Group()
        self.tower_group = pygame.sprite.Group()
        self.selected_tower = None

        self.wave = 1
        self.spawn_quantity = 5
        self.spawned_count = 0
        self.spawn_timer = 150
        self.spawn_timer_count = 0
        self.started_wave = False
        self.between_wave_delay = 5
        self.between_wave_timer = 0
        self.waiting_for_next_wave = False

        self.preview_tower = Tower(self.main, 0, 0, 96, 64)
        self.preview_valid = False

        self.place_zone = False
        self.build_mode = False


        self.tower_button = Button(self.main, 1216, 256, 192, 64, "TOWER")



    def load_scene(self):
        self.level_data = self.load_level_json()
        self.process_data()
        self.start_wave()
        self.background_music.play(-1)

    def load_level_json(self):
        with open('assets/levels/level1.tmj') as file:
            return json.load(file)

    def process_data(self):
        #for layer in self.level_data["layers"]:
        #    if layer["name"] == "waypoints":
        #        for obj in layer["objects"]:
        #            waypoint_data = obj["polyline"]
        #            self.process_waypoints(waypoint_data)
        self.waypoints.clear()
        self.waypoints.append([896, -64])
        self.waypoints.append([896, 256])
        self.waypoints.append([704, 256])
        self.waypoints.append([704, 128])
        self.waypoints.append([196, 128])
        self.waypoints.append([196, 704])
        self.waypoints.append([384, 704])
        self.waypoints.append([384, 320])
        self.waypoints.append([576, 320])
        self.waypoints.append([576, 448])
        self.waypoints.append([960, 448])
        self.waypoints.append([960, 896])
        self.waypoints.append([768, 896])
        self.waypoints.append([768, 640])
        self.waypoints.append([576, 640])
        self.waypoints.append([576, 896])
        self.waypoints.append([-64, 896])

        self.build_path_rects()

    def build_path_rects(self):
        #BUILDS PATH RECTANGLES TO AVOID PLACING TOWERS ON THE ROAD

        self.path_rects.clear()

        for i in range(len(self.waypoints) - 1):
            startX, startY = self.waypoints[i]
            endX, endY = self.waypoints[i + 1]

            if startX == endX:
                # vertical
                top = min(startY, endY)
                height = abs(endY - startY)
                rect = pygame.Rect(startX - TILE_SIZE // 2, top, TILE_SIZE, height)

            elif startY == endY:
                # horizontal
                left = min(startX, endX)
                width = abs(endX - startX)
                rect = pygame.Rect(left, startY - TILE_SIZE // 2, width, TILE_SIZE)

            self.path_rects.append(rect)

    def start_wave(self):
        self.started_wave = True
        self.spawned_count = 0
        self.spawn_timer_count = 1
        enemy = Enemy(self.main, 64, 64, self.waypoints, self.wave)
        self.enemy_group.add(enemy)

    def can_place_tower(self, tower):
        padded_rect = tower.rect.copy()
        padded_rect.inflate_ip(TOWER_PLACEMENT_BUFFER, TOWER_PLACEMENT_BUFFER)

        if padded_rect.collidelist(self.path_rects) != -1:
            return False

        if pygame.sprite.spritecollide(tower, self.tower_group, False):
            return False

        return True

    def process_waypoints(self, waypoint_data):
        for point in waypoint_data:
            temp_x = point.get("x")
            temp_y = point.get("y")
            self.waypoints.append([temp_x, temp_y])


    def clear_tower_selection(self, all=False):
        # USED TO MAKE SURE ONLY 1 TOWER CAN BE SELECTED
        for tower in self.tower_group:
            if all:
                tower.selected = False
            elif tower != self.selected_tower:
                tower.selected = False



    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.main.current_scene = self.main.menu_scene

        if self.tower_button.handle_event(event): #TOWER BUTTON
            self.build_mode = not self.build_mode
            if self.build_mode:
                self.tower_button.text = "Building.."
            else:
                self.tower_button.text = "Tower"

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if self.place_zone:
                    if self.build_mode:  # BUILD MODE FOR PLACING TOWER
                        if self.preview_valid:
                            tower = Tower(self.main, mouse_pos[0], mouse_pos[1], 64, 64)
                            self.tower_group.add(tower)

            self.clear_tower_selection(True)

        for tower in self.tower_group:
            if tower.handle_event(event) and not self.build_mode:
                tower.selected = not tower.selected
                self.selected_tower = tower


    def update(self, dt):
        #SPAWN TOWER
        mouse_pos = pygame.mouse.get_pos()

        self.clear_tower_selection()

        #makes sure the mouse is within the level zone not over the menus
        self.place_zone =  (LEVEL_WIDTH > mouse_pos[0] > 0 and mouse_pos[1] < LEVEL_HEIGHT and mouse_pos[1] > 0)


        self.preview_tower.rect.center = mouse_pos
        self.preview_valid = self.can_place_tower(self.preview_tower)

        if self.started_wave:
            if self.spawn_timer_count == 0:
                if self.spawned_count < self.spawn_quantity:
                    enemy = Enemy(self.main, 64, 64, self.waypoints, self.wave)
                    self.enemy_group.add(enemy)
                    self.spawned_count += 1

            if self.spawn_timer_count == self.spawn_timer:
                self.spawn_timer_count = 0
            else:
                self.spawn_timer_count += 1



            self.enemy_group.update(dt)

            for tower in self.tower_group:
                tower.find_target(self.enemy_group)

            if self.spawned_count >= self.spawn_quantity:
                if self.started_wave and len(self.enemy_group) == 0 and not self.waiting_for_next_wave:
                    self.wave_completed_sound.play()
                    self.started_wave = False
                    self.wave += 1
                    self.waiting_for_next_wave = True
                    self.between_wave_timer = self.between_wave_delay

        if self.waiting_for_next_wave:
            self.between_wave_timer -= dt

            if self.between_wave_timer <= 0:
                self.waiting_for_next_wave = False
                self.start_wave()

        for tower in self.tower_group:
            tower.update(dt)

        #captures all buttons
        self.tower_button.update(dt)

    def draw_tower_preview(self, surface):
        # draw range circle first
        range_image = self.preview_tower.range_image.copy()

        if not self.preview_valid:
            range_tint = pygame.Surface(range_image.get_size(), pygame.SRCALPHA)
            range_tint.fill((255, 0, 0, 120))
            range_image.blit(range_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(range_image, range_image.get_rect(center=self.preview_tower.rect.center))

        preview_image = self.preview_tower.image.copy()


        if not self.preview_valid:
            tint = pygame.Surface(preview_image.get_size(), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 180))
            preview_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(preview_image, self.preview_tower.rect)



    def draw(self, surface):
        surface.fill(BLACK)
        surface.blit(self.bg_image, (0, 0))
        surface.blit(self.bg_image_menu, (0,0))

        for enemy in self.enemy_group:
            enemy.draw(surface)

        for tower in self.tower_group:
            tower.draw(surface)

        self.tower_button.draw(surface)

        if self.place_zone and self.build_mode:
            self.draw_tower_preview(surface)

        if self.main.debug_mode:
            pygame.draw.lines(surface, RED, False, self.waypoints , 1)
            for rect in self.path_rects:
                pygame.draw.rect(surface, BLUE, rect, 1)

