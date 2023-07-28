import pygame
from constants import *
from utils import *
from copy import copy


class MiniGame:
    @classmethod
    def translate_coords(cls, x, y):
        return x-5, y-(SCREEN_HEIGHT*0.13)

    def __init__(self, global_info_bar):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                MINIGAME_WIDTH, MINIGAME_HEIGHT)
        self.sub_rect = pygame.Rect(
            0, 0, MINIGAME_WIDTH, MINIGAME_HEIGHT)
        self.clicks_to_handle = []
        self.font = pygame.font.SysFont('Arial', 70)
        self.forfeit_button = Button(
            'Forfeit', self.sub_rect.right-70, self.sub_rect.top+40, BLACK, GREY, 40, self.question_forfeit)
        self.confirm_forfeit_button = Button(
            'Confirm', self.sub_rect.right-70, self.sub_rect.top+100, BLACK, GREEN, 40, self.confirm_forfeit)
        self.cancel_forfeit_button = Button(
            'Cancel', self.sub_rect.right-70, self.sub_rect.top+40, BLACK, RED, 40, self.cancel_forfeit)
        self.global_info_bar = global_info_bar
        self.ready_to_exit = False
        self.running = True
        self.sub_surface = pygame.Surface(self.rect.size)
        self.questioning_forfeit = False
        self.countdown_start_time = None

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

    def check_forfeit_buttons_clicked(self, x, y):
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
        return click_used

    def check_info_bar_clicked(self, x, y):
        return self.info_bar.rect.collidepoint(x, y)

    def common_drawing(self, screen: pygame.Surface):
        self.draw_forfeit_button()
        self.draw_border()
        screen.blit(self.sub_surface, self.rect)

    def click(self, x, y):
        self.clicks_to_handle.append(MiniGame.translate_coords(x, y))

    def update(self):
        raise NotImplementedError('Can\'t update base minigame')

    def question_forfeit(self):
        self.questioning_forfeit = True

    def cancel_forfeit(self):
        self.questioning_forfeit = False

    def confirm_forfeit(self):
        self.running = False
        self.success = False
        self.ending_message = self.font.render(
            'Task Forfeited!', True, BLACK, GREY)
        self.ending_message_rect = self.ending_message.get_rect(
            center=self.sub_rect.center)

    def update_ending_sequence(self):
        self.clicks_to_handle = []
        if self.countdown_start_time is None:
            self.countdown_start_time = self.global_info_bar.score
        if self.global_info_bar.score - self.countdown_start_time >= 2:
            self.ready_to_exit = True

    def draw_ending_screen(self, screen: pygame.Surface):
        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.ending_message, self.ending_message_rect)
        self.draw_border()
        screen.blit(self.sub_surface, self.rect)

    def exit(self):
        self.ready_to_exit = True

    def check_time_and_target(self):
        if self.info_bar.target <= self.info_bar.score:
            self.running = False
            self.success = True
            self.ending_message = self.font.render(
                'Target Met!', True, BLACK, GREY)
            self.ending_message_rect = self.ending_message.get_rect(
                center=self.sub_rect.center)
        elif self.info_bar.time_left == 0:
            self.running = False
            self.success = False
            self.ending_message = self.font.render(
                'Time over!', True, BLACK, GREY)
            self.ending_message_rect = self.ending_message.get_rect(
                center=self.sub_rect.center)


class EmptyMiniGame(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)

        del self.forfeit_button
        del self.confirm_forfeit_button
        del self.cancel_forfeit_button
        self.label1 = self.font.render(
            'Hurry! Select a task from the task', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=(
            self.sub_rect.centerx, self.sub_rect.height*0.45))

        self.label2 = self.font.render(
            'list to lower the user\'s frustration!', True, BLACK, GREY)
        self.label2_rect = self.label2.get_rect(center=(
            self.sub_rect.centerx, self.sub_rect.height*0.55))

    def draw(self, screen: pygame.Surface):
        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)
        self.sub_surface.blit(self.label2, self.label2_rect)

        self.draw_border()
        screen.blit(self.sub_surface, self.rect)

    def update(self):
        self.clicks_to_handle = []


class RegisterMouseInputs(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.buttons: dict[int, RMIButton] = {}  # {buttonID:Button object}
        self.info_bar = STTInfoBar(20, 60, self.global_info_bar)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)
        for button in self.buttons.values():
            button.draw(self.sub_surface)

        self.info_bar.draw(self.sub_surface)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()

        self.check_time_and_target()  # Check for game over

        while len(self.buttons) < 5:  # Ensure 5 buttons exist
            self.buttons[RMIButton.ID-1] = RMIButton(
                10, self.handle_clicked_button, self.sub_rect, self.delete_button)

        for button in copy(self.buttons).values():  # Update buttons for motion
            button.update()

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
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
        """Delete missed offscreen button"""
        if not self.buttons[button_id].scam:
            self.info_bar.subtract_score(1)

        self.buttons.pop(button_id)


class MemoryManagement(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)

        self.info_bar = STTInfoBar(50, 20, self.global_info_bar)
        self.ram = Image(220, 160, r'images\MM\RAM.png')
        self.bin = MMBin(MINIGAME_WIDTH*0.5, MINIGAME_HEIGHT*0.5, 0, 12)
        self.garbage = Image(0, 0, r'images\MM\garbage.png')

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)

        self.bin.draw_back(self.sub_surface)
        self.garbage.draw(self.sub_surface)
        self.bin.draw_front(self.sub_surface)

        self.ram.draw(self.sub_surface)
        self.info_bar.draw(self.sub_surface)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class DefragDisk(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'Defrag Disk', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class SelectDrivers(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'Select Drivers', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class UserAuthentication(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'User Authentication', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class FileAccessControl(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'File Access Control', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class DataEncryption(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'Data Encryption', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class DataCompression(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'Data Compression', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue
