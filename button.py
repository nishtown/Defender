from settings import *

class Button(pygame.sprite.Sprite):
    def __init__(self, main, x, y, width, height, text):
        pygame.sprite.Sprite.__init__(self)
        self.main = main
        self.text = text
        self.font = pygame.font.SysFont(None, 42)
        self.image = pygame.image.load("assets/buttons/button.png").convert_alpha()
        self.rect = pygame.Rect(x, y , width, height)
        self.rect.center = x,y

        self.clicked = False
        self.is_hovered = False


    def draw_hover(self, surface):
        preview_image = self.image.copy()


        if self.is_hovered:
            tint = pygame.Surface(preview_image.get_size(), pygame.SRCALPHA)
            tint.fill((20, 20, 20, 40))
            preview_image.blit(tint, (0, 0) , special_flags=pygame.BLEND_RGB_ADD)

        return preview_image




    def handle_event(self, event):
        self.clicked = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.clicked = True
                return True
        return False

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        if self.image is not None:

            img = self.draw_hover(surface)

            if self.text:
                display_text = self.font.render(self.text, True, WHITE)

                text_x = img.get_width() // 2 - display_text.get_width() // 2
                text_y = img.get_height() // 2 - display_text.get_height() // 2

                img.blit(display_text, (text_x, text_y))

            surface.blit(img, self.rect)




            if self.main.debug_mode:
                pygame.draw.rect(surface, RED, self.rect, 1)
