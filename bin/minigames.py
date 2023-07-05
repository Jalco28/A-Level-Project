import pygame
from constants import *
from utils import *


class MiniGame:
    def __init__(self):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.85)
        self.clicks_to_handle = []
        self.font = pygame.font.SysFont('Arial', 70)
        self.forfeit_button = Button(
            'Forfeit', self.rect.right-70, self.rect.top+40, BLACK, GREY, 40, self.forfeit)
        self.finished = False
        self.success = None

    def draw(self, screen: pygame.Surface):
        raise NotImplementedError('Can\'t draw base minigame')

    def draw_border(self, screen: pygame.Surface):
        pygame.draw.rect(screen, BLACK, self.rect, 5, 1)

    def draw_forfeit_button(self, screen: pygame.Surface):
        self.forfeit_button.draw(screen)

    def common_drawing(self, screen: pygame.Surface):
        self.draw_forfeit_button(screen)
        self.draw_border(screen)

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))

    def update(self):
        if (not isinstance(self, EmptyMiniGame)) or (not isinstance(self, MiniGame)):
            self.forfeit_button.update()

    def forfeit(self):
        self.finished = True
        self.success = False


class EmptyMiniGame(MiniGame):
    def __init__(self):
        super().__init__()

        del self.forfeit_button
        self.label1 = self.font.render(
            'Hurry! Select a task from the task', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

        self.label2 = self.font.render(
            'list to lower the user\'s frustration!', True, BLACK, GREY)
        self.label2_rect = pygame.Rect(
            0, 0, self.label2.get_width(), self.label2.get_height())
        self.label2_rect.center = (self.rect.centerx, self.rect.height*0.6)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)
        screen.blit(self.label2, self.label2_rect)

        self.draw_border(screen)

    def update(self):
        self.clicks_to_handle = []


class RegisterMouseInputs(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'Register Mouse Inputs', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class MemoryManagement(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'Memory Management', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class DefragDisk(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'Defrag Disk', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class SelectDrivers(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'Select Drivers', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class UserAuthentication(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'User Authentication', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class FileAccessControl(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'File Access Control', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class DataEncryption(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'Data Encryption', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class DataCompression(MiniGame):
    def __init__(self):
        super().__init__()
        self.label1 = self.font.render(
            'Data Compression', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (self.rect.centerx, self.rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        screen.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()
