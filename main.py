import pygame.sprite

from settings import *
from scene import Scene
from world import World
from mainmenu import Menu

import asyncio

class Main:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Defender")
        self.clock = pygame.time.Clock()

        self.particle_group = pygame.sprite.LayeredUpdates()

        # Create scenes once
        self.menu_scene = Menu(self)
        self.world_scene = World(self)

        self.debug_mode = False

        # Set starting scene
        self.current_scene = self.menu_scene

    async def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000  # delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d and (event.mod & pygame.KMOD_CTRL):
                        self.debug_mode = not self.debug_mode


                self.current_scene.handle_event(event)

            self.current_scene.update(dt)
            self.current_scene.draw(self.display_surface)

            for particle in self.particle_group:
                particle.update(dt)
                particle.draw(self.display_surface)


            pygame.display.update()
            await asyncio.sleep(0)


        pygame.quit()



if __name__ == '__main__':
    main = Main()
    asyncio.run(main.run())