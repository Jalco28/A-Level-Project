import pygame
from constants import *

class MiniGame:
    def __init__(self):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.85)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, BLACK, self.rect)

    def update(self):
        pass
