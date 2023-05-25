import pygame
from constants import *


class MiniGame:
    def __init__(self):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.85)
        self.clicks_to_handle = []

    def draw(self, screen: pygame.Surface):
        raise NotImplementedError('Can\'t draw base minigame')

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))

    def update(self):
        raise NotImplementedError('Can\'t update base minigame')

class EmptyMiniGame(MiniGame):
    def __init__(self):
        super().__init__()
        font = pygame.font.SysFont('Arial', 70)

        self.label1 = font.render('Hurry! Select a task from the task', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

        self.label2 = font.render('list to lower the user\'s frustration!', True, BLACK, GREY)
        self.label2_rect = pygame.Rect(0, 0, self.label2.get_width(), self.label2.get_height())
        self.label2_rect.center = (self.rect.centerx, self.rect.height*0.6)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 5, 1)
        screen.blit(self.label1, self.label1_rect)
        screen.blit(self.label2, self.label2_rect)


    def update(self):
        self.clicks_to_handle = []
