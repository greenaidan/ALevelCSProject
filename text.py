import pygame
pygame.init()

class Text:
    def __init__(self, pos, txt, size = 50):
        self.pos = pos
        self.font = pygame.font.Font("misc assets/pixelfont.TTF", size)
        self.txt = self.font.render(txt, True, [255]*3)
    def draw(self, screen):
        screen.blit(self.txt, self.pos)
