import pygame
from constants import *
from utils import *
from copy import copy


class MiniGame:
    @classmethod
    def translate_coords(cls, x, y):
        return x-5, y-(SCREEN_HEIGHT*0.13)

    def __init__(self):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                MINIGAME_WIDTH, MINIGAME_HEIGHT)
        self.sub_rect = pygame.Rect(
            0, 0, MINIGAME_WIDTH, MINIGAME_HEIGHT)
        self.clicks_to_handle = []
        self.font = pygame.font.SysFont('Arial', 70)
        self.forfeit_button = Button(
            'Forfeit', self.sub_rect.right-70, self.sub_rect.top+40, BLACK, GREY, 40, self.question_forfeit)
        self.confirm_forfeit_button = Button(
            'Confirm', self.sub_rect.right-70, self.sub_rect.top+100, BLACK, GREEN, 40, self.unsuccesful_end)
        self.cancel_forfeit_button = Button(
            'Cancel', self.sub_rect.right-70, self.sub_rect.top+40, BLACK, RED, 40, self.cancel_forfeit)
        self.finished = False
        self.success = None
        self.sub_surface = pygame.Surface(self.rect.size)
        self.questioning_forfeit = False

    def draw(self, screen: pygame.Surface):
        raise NotImplementedError('Can\'t draw base minigame')

    def draw_border(self):
        pygame.draw.rect(self.sub_surface, BLACK, self.sub_rect, 5, 1)

    def draw_forfeit_button(self):
        if self.questioning_forfeit:
            self.confirm_forfeit_button.draw(self.sub_surface)
            self.cancel_forfeit_button.draw(self.sub_surface)
        else:
            self.forfeit_button.draw(self.sub_surface)

    def common_drawing(self, screen: pygame.Surface):
        self.draw_forfeit_button()
        self.draw_border()
        screen.blit(self.sub_surface, self.rect)

    def click(self, x, y):
        self.clicks_to_handle.append(MiniGame.translate_coords(x, y))

    def update(self):
        # if (not isinstance(self, EmptyMiniGame)) or (not isinstance(self, MiniGame)):
        #     self.forfeit_button.update()
        pass

    def question_forfeit(self):
        self.questioning_forfeit = True

    def cancel_forfeit(self):
        self.questioning_forfeit = False

    def unsuccesful_end(self):
        self.finished = True
        self.success = False

    def succesful_end(self):
        self.finished = True
        self.success = True


class EmptyMiniGame(MiniGame):
    def __init__(self, *args):
        super().__init__()

        del self.forfeit_button
        del self.confirm_forfeit_button
        del self.cancel_forfeit_button
        self.label1 = self.font.render(
            'Hurry! Select a task from the task', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

        self.label2 = self.font.render(
            'list to lower the user\'s frustration!', True, BLACK, GREY)
        self.label2_rect = pygame.Rect(
            0, 0, self.label2.get_width(), self.label2.get_height())
        self.label2_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.6)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)
        self.sub_surface.blit(self.label2, self.label2_rect)

        self.draw_border()
        screen.blit(self.sub_surface, self.rect)

    def update(self):
        self.clicks_to_handle = []


class RegisterMouseInputs(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.global_info_bar = global_info_bar
        self.label1 = self.font.render(
            'Register Mouse Inputs', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)
        self.buttons: dict[int, RMIButton] = {}
        self.info_bar = STTInfoBar(20, 60, self.global_info_bar)

    def draw(self, screen: pygame.Surface):
        # pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        # self.sub_surface.blit(self.label1, self.label1_rect)
        self.sub_surface.fill(WHITE)
        for button in self.buttons.values():
            button.draw(self.sub_surface)

        self.info_bar.draw(self.sub_surface)

        self.common_drawing(screen)

    def update(self):
        while len(self.buttons) < 5:
            self.buttons[RMIButton.ID-1] = RMIButton(
                10, self.handle_clicked_button, self.sub_rect, self.delete_button)
        for button in copy(self.buttons).values():
            button.update()

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            if self.questioning_forfeit:
                if self.confirm_forfeit_button.rect.collidepoint(x, y):
                    self.confirm_forfeit_button.click()
                    click_used = True
                elif self.cancel_forfeit_button.rect.collidepoint(x, y):
                    self.cancel_forfeit_button.click()
                    click_used = True
            else:
                if self.forfeit_button.rect.collidepoint(x, y):
                    self.forfeit_button.click()
                    click_used = True

            if click_used:
                continue

            if self.info_bar.rect.collidepoint(x, y):
                click_used = True

            if click_used:
                continue

            # Check clicks in reverse draw order
            for button in reversed(self.buttons.values()):
                if button.rect.collidepoint(x, y):
                    button.click()
                    click_used = True
                    break

            if click_used:
                continue

    def handle_clicked_button(self, button_id):
        button: RMIButton = self.buttons[button_id]
        if button.scam:
            self.info_bar.subtract_score(5)
        else:
            self.info_bar.add_score(1)
        self.buttons.pop(button_id)

    def delete_button(self, button_id):
        if not self.buttons[button_id].scam:
            self.info_bar.subtract_score(1)

        self.buttons.pop(button_id)


class MemoryManagement(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'Memory Management', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class DefragDisk(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'Defrag Disk', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class SelectDrivers(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'Select Drivers', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class UserAuthentication(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'User Authentication', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class FileAccessControl(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'File Access Control', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class DataEncryption(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'Data Encryption', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()


class DataCompression(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__()
        self.label1 = self.font.render(
            'Data Compression', True, BLACK, GREY)
        self.label1_rect = pygame.Rect(
            0, 0, self.label1.get_width(), self.label1.get_height())
        self.label1_rect.center = (
            self.sub_rect.centerx, self.sub_rect.height*0.5)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(self.sub_surface, GREY, self.sub_rect)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.forfeit_button.rect.collidepoint(x, y):
                self.forfeit_button.click()
