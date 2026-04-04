from settings import *
from scene import Scene
from world import World

class Menu(Scene):
    def __init__(self, main):
        super().__init__(main)
        self.font = pygame.font.SysFont(None, 60)
        self.bg_image_original = pygame.image.load("assets/background.png")
        self.bg_image = pygame.transform.scale(self.bg_image_original, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.main.world_scene = World(self.main)
                self.main.current_scene = self.main.world_scene
                self.main.current_scene.load_scene()

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BLACK)
        surface.blit(self.bg_image, (0, 0))

        title_text = self.font.render("Defender", True, BLACK)
        start_text = self.font.render("Press ENTER to Start", True, BLACK)

        surface.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
        surface.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))