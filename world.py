import pygame.mask
from pygame import surface

from settings import *
from scene import Scene
from enemy import Enemy
from towers.basic_tower import BasicTower
from towers.gun_tower import GunTower
from towers.canon_tower import CanonTower
from towers.rocket_tower import RocketTower
from button import Button
import json

class World(Scene):
    def __init__(self, main):
        super().__init__(main)
        self.font = pygame.font.SysFont(None, 60)
        self.ui_font = pygame.font.SysFont(None, 32)
        self.bg_image_original = pygame.image.load(asset_path("assets","levels","level1.png"))
        self.bg_image_menu = pygame.image.load(asset_path("assets","levels","level1_menu.png")).convert_alpha()
        self.wave_completed_sound = pygame.mixer.Sound(asset_path("assets","sounds","wave_completed.ogg"))
        self.background_music = pygame.mixer.Sound(asset_path("assets","sounds","background.ogg"))
        self.background_music.set_volume(0.2)
        self.wave_completed_sound.set_volume(0.5)
        self.bg_image = pygame.transform.scale(self.bg_image_original, (LEVEL_WIDTH, LEVEL_HEIGHT))
        self.level_data = None
        self.waypoints = []
        self.path_rects = []
        self.enemy_group = pygame.sprite.Group()
        self.tower_group = pygame.sprite.Group()
        self.selected_tower = None

        self.lives = 100
        self.wave = 1
        self.spawn_quantity = 10
        self.spawned_count = 0
        self.enemy_count = 10
        self.spawn_timer = min(100, 100 - (self.spawn_quantity * self.wave))
        self.spawn_timer_count = 0
        self.started_wave = False
        self.between_wave_delay = 10
        self.between_wave_timer = self.between_wave_delay #so the initial wave starts with a delay
        self.waiting_for_next_wave = True

        self.preview_tower = BasicTower(self.main, 0, 0, 96, 64)
        self.build_tower_class = BasicTower
        self.preview_valid = False

        self.place_zone = False
        self.build_mode = False


        self.gold = 500
        self.score = 0


        self.button_list = []
        self.basic_tower_button = Button(self.main, 1216, 256, 192, 64, "TOWER 1")
        self.button_list.append(self.basic_tower_button)
        self.tier2_tower_button = Button(self.main, 1216, 336, 192, 64, "TOWER 2")
        self.button_list.append(self.tier2_tower_button)
        self.canon_tower_button = Button(self.main, 1216, 416, 192, 64, "TOWER 3")
        self.button_list.append(self.canon_tower_button)
        self.rocket_tower_button = Button(self.main, 1216, 496, 192, 64, "TOWER 4")
        self.button_list.append(self.rocket_tower_button)



    def load_scene(self):
        self.level_data = self.load_level_json()
        self.process_data()
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
        if self.wave > 1:
            self.spawn_quantity = 10 + (self.wave * 2)
        self.spawned_count = 1
        self.spawn_timer_count = 1
        self.enemy_count = self.spawn_quantity
        enemy = Enemy(self.main, 64, 64, self.waypoints, self.wave)
        self.enemy_group.add(enemy)

    def can_place_tower(self, tower):
        if self.gold < tower.cost:
            return False

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

        if self.basic_tower_button.handle_event(event): #TOWER BUTTON
            self.build_mode = not self.build_mode
            if self.build_mode:
                self.preview_tower = BasicTower(self.main, 0, 0, 96, 64)
                self.build_tower_class = BasicTower
        if self.tier2_tower_button.handle_event(event): #TOWER BUTTON
            self.build_mode = not self.build_mode
            if self.build_mode:
                self.preview_tower = GunTower(self.main, 0, 0, 96, 64)
                self.build_tower_class = GunTower
        if self.canon_tower_button.handle_event(event): #TOWER BUTTON
            self.build_mode = not self.build_mode
            if self.build_mode:
                self.preview_tower = CanonTower(self.main, 0, 0, 96, 64)
                self.build_tower_class = CanonTower
        if self.rocket_tower_button.handle_event(event): #TOWER BUTTON
            self.build_mode = not self.build_mode
            if self.build_mode:
                self.preview_tower = RocketTower(self.main, 0, 0, 96, 64)
                self.build_tower_class = RocketTower

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if self.place_zone:
                    if self.build_mode:  # BUILD MODE FOR PLACING TOWER
                        if self.preview_valid:
                            tower = self.build_tower_class(self.main, mouse_pos[0], mouse_pos[1], 64, 64)
                            self.tower_group.add(tower)
                            self.gold -= tower.cost
                            self.build_mode = False


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
                    if self.wave > 1:
                        enemy.speed = enemy.speed + (enemy.speed / enemy.speed * self.wave)
                        print(enemy.speed)
                    self.enemy_group.add(enemy)
                    self.spawned_count += 1

            if self.spawn_timer_count == self.spawn_timer:
                self.spawn_timer_count = 0
            else:
                self.spawn_timer_count += 1

            for enemy in self.enemy_group:
                enemy.update(dt)
                if enemy.is_dead:
                    self.score += enemy.score_value
                    self.gold += enemy.gold_value
                    self.enemy_count -= 1
                    enemy.kill()
                if enemy.has_escaped:
                    self.enemy_count -= 1
                    self.lives -= 1
                    enemy.kill()

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
        for button in self.button_list:
            button.update(dt)

        if self.lives <= 0:
            self.main.current_scene = self.main.menu_scene


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

        # captures all buttons
        for button in self.button_list:
            button.draw(surface)

        if self.place_zone and self.build_mode:
            self.draw_tower_preview(surface)

        self.draw_ui(surface)

        if self.main.debug_mode:
            pygame.draw.lines(surface, RED, False, self.waypoints , 1)
            for rect in self.path_rects:
                pygame.draw.rect(surface, BLUE, rect, 1)



    def draw_ui(self, surface):
        score_text = self.ui_font.render(f"Score: {self.score}", True, (255, 255, 255))
        gold_text = self.ui_font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        wave_text = self.ui_font.render(f"Wave: {self.wave}", True, (0, 0, 255))
        enemy_text = self.ui_font.render(f"Enemies: {self.enemy_count}", True, (255, 125, 0))

        score_rect = score_text.get_rect(topleft=(10, 10))
        gold_rect = gold_text.get_rect(topleft=(10, 40))
        wave_rect = wave_text.get_rect(topleft=(10, 70))
        enemy_rect = enemy_text.get_rect(topleft=(10, 100))


        # optional shadow
        score_shadow = self.ui_font.render(f"Score: {self.score}", True, (0, 0, 0))
        gold_shadow = self.ui_font.render(f"Gold: {self.gold}", True, (0, 0, 0))
        wave_shadow = self.ui_font.render(f"Wave: {self.wave}", True, (0, 0, 0))
        enemy_shadow = self.ui_font.render(f"Enemies: {self.enemy_count}", True, (0, 0, 0))

        surface.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
        surface.blit(gold_shadow, (gold_rect.x + 2, gold_rect.y + 2))
        surface.blit(wave_shadow, (wave_rect.x + 2, wave_rect.y + 2))
        surface.blit(enemy_shadow, (enemy_rect.x + 2, enemy_rect.y + 2))

        surface.blit(score_text, score_rect)
        surface.blit(gold_text, gold_rect)
        surface.blit(wave_text, wave_rect)
        surface.blit(enemy_text, enemy_rect)