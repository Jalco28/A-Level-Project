import random
import pygame
import time
import minigames
from constants import *


class InfoBar:
    def __init__(self):
        self.rect = pygame.Rect(5, 5, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.1)
        self.background_colour = GREY
        self.border_colour = BLACK
        self.FONT_SIZE = 40
        self.font = pygame.font.SysFont("Arial", self.FONT_SIZE)
        self.start_time = time.time()
        self.paused_intervals: list[tuple[float, float]] = []

        self.mode = 'Regular Play'
        self.score = 0
        self.difficulty_level = 1

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.background_colour, self.rect)
        pygame.draw.rect(screen, self.border_colour, self.rect, 5, 2)

        mode_text = self.font.render(
            self.mode, True,  BLACK, self.background_colour)
        score_text = self.font.render(
            f'Score: {self.score}', True, BLACK, self.background_colour)
        difficulty_text = self.font.render(
            f'Difficulty Level: {self.difficulty_level}', True, BLACK, self.background_colour)

        mode_rect = pygame.Rect(
            0, 0, mode_text.get_width(), mode_text.get_height())
        mode_rect.midleft = (self.rect.left+0.02 *
                             self.rect.width, self.rect.centery)

        score_rect = pygame.Rect(
            0, 0, score_text.get_width(), score_text.get_height())
        score_rect.midleft = (self.rect.left+0.4 *
                              self.rect.width, self.rect.centery)

        difficulty_rect = pygame.Rect(
            0, 0, difficulty_text.get_width(), difficulty_text.get_height())
        difficulty_rect.midleft = (
            self.rect.left+0.7*self.rect.width, self.rect.centery)

        screen.blit(mode_text, mode_rect)
        screen.blit(score_text, score_rect)
        screen.blit(difficulty_text, difficulty_rect)

    def update(self):
        time_paused = self.get_time_paused()
        self.score = int(time.time() - time_paused - self.start_time)

    def get_time_paused(self):
        time_paused = 0
        for pair in self.paused_intervals:
            time_paused += pair[1] - pair[0]
        return time_paused

    def click(self, x, y):
        pass


class FrustrationBar:
    def __init__(self):
        self.frustration_level = 50
        self.WIDTH = SCREEN_WIDTH * 0.05
        self.HEIGHT = SCREEN_HEIGHT * 0.85
        self.rect = pygame.Rect(SCREEN_WIDTH-self.WIDTH-40,
                                SCREEN_HEIGHT*0.13, self.WIDTH, self.HEIGHT)
        self.FONT_SIZE = 30
        self.font = pygame.font.SysFont("Arial", self.FONT_SIZE)

    def draw(self, screen: pygame.Surface):
        red_rect = pygame.Rect(self.rect.left, 0, self.WIDTH,
                               self.HEIGHT*0.01*self.frustration_level)
        red_rect.bottom = self.rect.bottom
        pygame.draw.rect(screen, FRUSTRATION_RED, red_rect)

        pygame.draw.rect(screen, BLACK, self.rect, 5, 2)
        for i in range(1, 10):
            i *= 0.1
            dash_height = self.rect.top + i * self.HEIGHT
            pygame.draw.line(screen, BLACK, (self.rect.left,
                             dash_height), (self.rect.left+20, dash_height), 4)

        label = self.font.render('User Frustration', True, BLACK, WHITE)
        label = pygame.transform.rotate(label, 270)
        text_rect = pygame.Rect(0, 0, label.get_width(), label.get_height())
        text_rect.center = (self.rect.centerx+63, self.rect.centery)
        # pygame.draw.rect(screen, DEBUG_GREEN, text_rect)
        screen.blit(label, text_rect)

    def update(self):
        # self.frustration_level += random.randint(-2, 2)
        self.frustration_level = self.frustration_level % 101

    def click(self, x, y):
        pass


class TaskList:
    def __init__(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH*0.715, SCREEN_HEIGHT*0.13, SCREEN_WIDTH*0.2, SCREEN_HEIGHT * 0.85+1)
        self.tasks: list[Task] = []
        self.clicks_to_handle = []

    def draw(self, screen: pygame.Surface):
        for task in self.tasks:
            task.draw(screen)
        pygame.draw.rect(screen, BLACK, self.rect, 5)

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            for task in self.tasks:
                if task.rect.collidepoint(x, y):
                    task.click(x, y)
        for task in self.tasks:
            task.update()

    def add_task(self):
        if len(self.tasks) < 8:
            self.tasks.append(Task(len(self.tasks), self))

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))


class Task:
    def __init__(self, index, parent):
        self.parent: TaskList = parent
        self.index = index
        self.HEIGHT = 103  # Mank number so 8 tasks nicely fit into the list
        self.rect = pygame.Rect(self.parent.rect.left, self.parent.rect.top + 1 +
                                index*self.HEIGHT, self.parent.rect.width, self.HEIGHT)
        self.description_font = pygame.font.SysFont('Arial', 35)
        self.sub_font = pygame.font.SysFont('Arial', 25)
        self.description = random.choice([
            'Register Mouse Inputs',
            'Memory Management',
            'Defrag Disk',
            'Select Drivers',
            'User Authentication',
            'File Access Control',
            'Data encryption',
            'Data compression'
        ])
        self.clicks_to_handle = []

        self.time_required = random.randint(
            1, TASK_PRIORITIES[self.description])

        self.description_text = self.description_font.render(
            self.description, True, BLACK)

        self.priority_text = self.sub_font.render(
            f'Priority: {TASK_PRIORITIES[self.description]}', True, BLACK)

        self.time_text = self.sub_font.render(
            f'Time required: {self.time_required}', True, BLACK)
        self.play_button = Button(
            'Play mini-game', self.rect.right-180, self.rect.bottom-60, BLACK, GREY, 25, self.play_button_action)

    def play_button_action(self):
        pass

    def draw(self, screen: pygame.Surface):
        if self.index % 2 == 0:
            pygame.draw.rect(screen, DEBUG_BLUE, self.rect)
        else:
            pygame.draw.rect(screen, DEBUG_GREEN, self.rect)

        pygame.draw.line(screen, BLACK, self.rect.bottomleft,
                         (self.rect.right-5, self.rect.bottom), 3)

        pygame.draw.line(screen, BLACK, self.rect.topleft,
                         (self.rect.right-5, self.rect.top), 3)

        screen.blit(self.description_text,
                    (self.rect.left+10, self.rect.top+5))
        screen.blit(self.priority_text, (self.rect.left+10, self.rect.top+45))
        screen.blit(self.time_text, (self.rect.left+10, self.rect.top+70))
        self.play_button.draw(screen)

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))

    def update(self):
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            if self.play_button.rect.collidepoint(x, y):
                self.play_button.action()


class Button:
    def __init__(self, text, left, top, border_colour, background_colour, font_size, action):
        self.font = pygame.font.SysFont('Arial', font_size)
        self.text = text
        self.rendered_text = self.font.render(self.text, True, BLACK)
        self.rect = pygame.Rect(
            left, top, self.rendered_text.get_width()*1.1, self.rendered_text.get_height()*1.2)
        self.text_rect = pygame.Rect(
            0, 0, self.rendered_text.get_width(), self.rendered_text.get_height())
        self.text_rect.center = self.rect.center
        self.border_colour = border_colour
        self.background_colour = background_colour
        self.action = action

    @classmethod
    def from_centre_coords(cls, text, centre_x, centre_y, border_colour, background_colour, font_size, action):
        font = pygame.font.SysFont('Arial', font_size)
        rendered_text = font.render(text, True, BLACK)
        rect = pygame.Rect(0, 0, rendered_text.get_width(),
                           rendered_text.get_height())
        rect.center = (centre_x, centre_y)
        return cls(text, rect.left, rect.top, border_colour, background_colour, font_size, action)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.background_colour, self.rect)
        pygame.draw.rect(screen, self.border_colour, self.rect, 2)
        screen.blit(self.rendered_text, self.text_rect)

    def update(self):
        pass

    def click(self, x, y):
        self.action()


class DoorsOS:
    def __init__(self):
        self.setup_game()

    def setup_game(self):
        pygame.init()
        pygame.display.set_caption('DoorsOS')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.paused = False
        self.running = True
        self.info_bar = InfoBar()
        self.task_list = TaskList()
        self.frustration_bar = FrustrationBar()
        self.current_mini_game = minigames.MiniGame()

        self.resume_button = Button.from_centre_coords(
            'Resume Game', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.4, BLACK, GREY, 50, self.unpause_game)
        self.main_menu_button = Button.from_centre_coords(
            'Exit To Main Menu', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, None)

        self.active_panels: list[InfoBar | FrustrationBar
                                 | TaskList | minigames.MiniGame | Button] = [self.info_bar,
                                                                              self.current_mini_game, self.frustration_bar, self.task_list]

    def play_game(self):
        while self.running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # self.info_bar.difficulty_level += 1
                        self.send_click_to_panel(event)
                    if event.button == 3:
                        self.task_list.add_task()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        escape_exit_code = self.pause()
                        if escape_exit_code == pygame.QUIT:
                            self.running = False
                        else:
                            self.info_bar.paused_intervals.append(
                                escape_exit_code)

                if event.type == pygame.MOUSEWHEEL:
                    self.frustration_bar.frustration_level += event.y

            if not self.running:
                break

            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_panels()
            self.update_screen()
            self.clock.tick(FPS)

    def update_panels(self):
        for panel in self.active_panels:
            panel.update()

    def update_screen(self):
        self.screen.fill(WHITE)
        for panel in self.active_panels:
            panel.draw(self.screen)

        if DEBUG:
            for i in range(10):
                i += 0.5
                pygame.draw.line(self.screen, DEBUG_BLUE, (SCREEN_WIDTH *
                                 i*0.1, 0), (SCREEN_WIDTH*i*0.1, SCREEN_HEIGHT))
            for i in range(1, 10):
                pygame.draw.line(self.screen, DEBUG_GREEN, (SCREEN_WIDTH *
                                 i*0.1, 0), (SCREEN_WIDTH*i*0.1, SCREEN_HEIGHT), 3)
            for i in range(10):
                i += 0.5
                pygame.draw.line(self.screen, DEBUG_BLUE, (0, SCREEN_HEIGHT *
                                 i*0.1), (SCREEN_WIDTH, SCREEN_HEIGHT*i*0.1))
            for i in range(1, 10):
                pygame.draw.line(self.screen, DEBUG_GREEN, (0, SCREEN_HEIGHT *
                                 i*0.1), (SCREEN_WIDTH, SCREEN_HEIGHT*i*0.1), 3)
        pygame.display.update()

    def pause(self):
        self.paused = True
        start_time = time.time()
        self.active_panels = [self.info_bar,
                              self.resume_button, self.main_menu_button]
        while self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return pygame.QUIT
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)

            # self.update_panels()
            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_screen()
            self.clock.tick(FPS)

        self.active_panels = [
            self.info_bar, self.current_mini_game, self.frustration_bar, self.task_list]
        return (start_time, time.time())

    def send_click_to_panel(self, event: pygame.event.Event):
        x, y = event.pos
        for panel in self.active_panels:
            if panel.rect.collidepoint(x, y):
                panel.click(x, y)

    def unpause_game(self):
        self.paused = False


def main():
    game = DoorsOS()
    game.play_game()


if __name__ == '__main__':
    main()
