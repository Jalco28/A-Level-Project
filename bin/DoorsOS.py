import random
import pygame
import time
import minigames
from constants import *
from functools import partial


class InfoBar:
    def __init__(self, difficulty):
        self.rect = pygame.Rect(5, 5, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.1)
        self.background_colour = GREY
        self.border_colour = BLACK
        self.FONT_SIZE = 40
        self.font = pygame.font.SysFont("Arial", self.FONT_SIZE)
        self.start_time = time.time()
        self.paused_intervals: list[tuple[float, float]] = []

        self.mode = 'Regular Play'
        self.score = 0
        if difficulty == GCSE:
            self.difficulty_level = 1
        else:
            self.difficulty_level = 10

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
        if DEBUG:
            for task in Task.TASK_DESCRIPTIONS:
                self.add_task(task)

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

    def add_task(self, description=None):
        if len(self.tasks) < 8:
            self.tasks.append(Task(len(self.tasks), self, description))

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))


class Task:
    TASK_PRIORITIES = {
        'Register Mouse Inputs': 5,
        'Memory Management': 3,
        'Defrag Disk': 2,
        'Select Drivers': 6,
        'User Authentication': 7,
        'File Access Control': 5,
        'Data encryption': 6,
        'Data compression': 4
    }
    TASK_DESCRIPTIONS = [
        'Register Mouse Inputs',
        'Memory Management',
        'Defrag Disk',
        'Select Drivers',
        'User Authentication',
        'File Access Control',
        'Data encryption',
        'Data compression'
    ]
    TASK_OBJECTS = {
        'Register Mouse Inputs': minigames.RegisterMouseInputs,
        'Memory Management': minigames.MemoryManagement,
        'Defrag Disk': minigames.DefragDisk,
        'Select Drivers': minigames.SelectDrivers,
        'User Authentication': minigames.UserAuthentication,
        'File Access Control': minigames.FileAccessControl,
        'Data encryption': minigames.DataEncryption,
        'Data compression': minigames.DataCompression
    }

    def __init__(self, index, parent, description):
        self.parent: TaskList = parent
        self.index = index
        self.HEIGHT = 103  # Mank number so 8 tasks nicely fit into the list
        self.rect = pygame.Rect(self.parent.rect.left, self.parent.rect.top + 1 +
                                index*self.HEIGHT, self.parent.rect.width, self.HEIGHT)
        self.description_font = pygame.font.SysFont('Arial', 35)
        self.sub_font = pygame.font.SysFont('Arial', 25)
        if description is None:
            self.description = random.choice(Task.TASK_DESCRIPTIONS)
        else:
            self.description = description
        self.clicks_to_handle = []

        self.time_required = random.randint(
            1, Task.TASK_PRIORITIES[self.description])

        self.description_text = self.description_font.render(
            self.description, True, BLACK)

        self.priority_text = self.sub_font.render(
            f'Priority: {Task.TASK_PRIORITIES[self.description]}', True, BLACK)

        self.time_text = self.sub_font.render(
            f'Time required: {self.time_required}', True, BLACK)
        self.play_button = Button(
            'Play mini-game', self.rect.right-180, self.rect.bottom-60, BLACK, GREY, 25, self.play_button_action)

    def play_button_action(self):
        main_menu.game.change_minigame(Task.TASK_OBJECTS[self.description])

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


class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('DoorsOS')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.play_button = Button.from_centre_coords(
            'Play game', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.3, BLACK, GREY, 50, self.choose_difficulty)
        self.score_board_button = Button.from_centre_coords(
            'Leaderboard', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, None)
        self.exit_button = Button.from_centre_coords(
            'Exit to desktop', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.7, BLACK, GREY, 50, self.menu_running_false)

        self.gcse_button = Button.from_centre_coords(
            'GCSE', SCREEN_WIDTH*0.4, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, partial(self.play_game, GCSE))
        self.alevel_button = Button.from_centre_coords(
            'A-Level', SCREEN_WIDTH*0.6, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, partial(self.play_game, ALEVEL))

        self.panels = [self.play_button,
                       self.score_board_button, self.exit_button]

    def choose_difficulty(self):
        self.panels = [self.gcse_button, self.alevel_button]

    def play_game(self, difficulty):
        self.panels = [self.play_button,
                       self.score_board_button, self.exit_button]
        self.game = DoorsOS(self.clock, self.screen, difficulty)
        self.game.play_game()
        exit_code = self.game.get_exit_code()
        if exit_code == pygame.QUIT:
            self.running = False

    def menu_running_false(self):
        self.running = False

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)

            if not self.running:
                break

            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_panels()
            self.update_screen()
            self.clock.tick(FPS)

    def update_panels(self):
        for panel in self.panels:
            panel.update()

    def update_screen(self):
        self.screen.fill(WHITE)
        for panel in self.panels:
            panel.draw(self.screen)

        pygame.display.update()

    def send_click_to_panel(self, event: pygame.event.Event):
        x, y = event.pos
        for panel in self.panels:
            if panel.rect.collidepoint(x, y):
                panel.click(x, y)


class DoorsOS:
    def __init__(self, clock, screen, difficulty):
        self.clock = clock
        self.screen = screen
        self.exit_code = 0
        self.difficulty = difficulty
        self.resume_button = Button.from_centre_coords(
            'Resume Game', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.4, BLACK, GREY, 50, self.unpause_game)
        self.exit_to_main_menu_button = Button.from_centre_coords(
            'Exit To Main Menu', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, self.end_game)

    def reset_game(self):
        self.paused = False
        self.info_bar = InfoBar(self.difficulty)
        self.task_list = TaskList()
        self.frustration_bar = FrustrationBar()
        self.current_mini_game = minigames.EmptyMiniGame()
        self.panels: list[InfoBar | FrustrationBar
                          | TaskList | minigames.MiniGame | Button] = [self.info_bar,
                                                                       self.current_mini_game, self.frustration_bar, self.task_list]

    def get_exit_code(self):
        return self.exit_code

    def play_game(self):
        self.reset_game()
        self.game_running = True
        escape_exit_code = 0
        while self.game_running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.end_game(True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # self.info_bar.difficulty_level += 1
                        self.send_click_to_panel(event)
                    if event.button == 3:
                        self.task_list.add_task()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        escape_exit_code = self.pause_game()
                        if escape_exit_code == pygame.QUIT:
                            self.game_running = False
                        else:
                            self.info_bar.paused_intervals.append(
                                escape_exit_code)

                if event.type == pygame.MOUSEWHEEL:
                    self.frustration_bar.frustration_level += event.y

            if not self.game_running:
                break

            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_panels()
            self.update_screen()
            self.clock.tick(FPS)

    def end_game(self, complete_exit=False):
        self.game_running = False
        if complete_exit:
            self.exit_code = pygame.QUIT
        self.unpause_game()

    def change_minigame(self, minigame):
        self.current_mini_game = minigame()
        self.panels[1] = self.current_mini_game

    def update_panels(self):
        for panel in self.panels:
            panel.update()

    def update_screen(self):
        self.screen.fill(WHITE)
        for panel in self.panels:
            panel.draw(self.screen)

        pygame.display.update()

    def pause_game(self):
        self.paused = True
        start_time = time.time()
        self.panels = [self.info_bar,
                       self.resume_button, self.exit_to_main_menu_button]
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

        self.panels = [
            self.info_bar, self.current_mini_game, self.frustration_bar, self.task_list]
        return (start_time, time.time())

    def send_click_to_panel(self, event: pygame.event.Event):
        x, y = event.pos
        for panel in self.panels:
            if panel.rect.collidepoint(x, y):
                panel.click(x, y)

    def unpause_game(self):
        self.paused = False


if __name__ == '__main__':
    main_menu = MainMenu()
    main_menu.run()
