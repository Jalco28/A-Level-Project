import pygame
from constants import *

class MiniGame:
    def __init__(self):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.85)
        self.clicks_to_handle = []

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, BLACK, self.rect)

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))

    def update(self):
        pass
