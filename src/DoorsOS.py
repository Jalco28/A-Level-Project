import requests
from utils import *
from constants import *
import minigames
import time
import pygame
import random
import os
import sys
sys.dont_write_bytecode = True


class InfoBar:
    def __init__(self, mode):
        self.rect = pygame.Rect(5, 5, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.1)
        self.FONT_SIZE = 40
        self.mode = mode
        self.font = pygame.font.SysFont("Arial", self.FONT_SIZE)
        self.start_time = time.time()
        self.paused_intervals: list[tuple[float, float]] = []
        if self.mode == REGULAR_PLAY:
            self.mode_text = 'Regular Play'
        else:
            self.mode_text = 'Zen Mode'
        self.score = 0
        self.difficulty_level = 1

        mode_text = self.font.render(
            self.mode_text, True,  BLACK, GREY)
        score_text = self.font.render(
            f'Score: {self.score}', True, BLACK, GREY)
        difficulty_text = self.font.render(
            f'Difficulty Level: {self.difficulty_level}', True, BLACK, GREY)

        self.mode_rect = pygame.Rect(
            0, 0, mode_text.get_width(), mode_text.get_height())
        self.mode_rect.midleft = (self.rect.left+0.02 *
                                  self.rect.width, self.rect.centery)

        self.score_rect = pygame.Rect(
            0, 0, score_text.get_width(), score_text.get_height())
        self.score_rect.midleft = (self.rect.left+0.4 *
                                   self.rect.width, self.rect.centery)

        self.difficulty_rect = pygame.Rect(
            0, 0, difficulty_text.get_width(), difficulty_text.get_height())
        self.difficulty_rect.midleft = (
            self.rect.left+0.7*self.rect.width, self.rect.centery)

    def get_mode(self):
        return self.mode

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 5, 2)

        mode_text = self.font.render(
            self.mode_text, True,  BLACK, GREY)
        score_text = self.font.render(
            f'Score: {int(self.score)}', True, BLACK, GREY)
        difficulty_text = self.font.render(
            f'Difficulty Level: {self.difficulty_level}', True, BLACK, GREY)

        screen.blit(mode_text, self.mode_rect)
        screen.blit(score_text, self.score_rect)
        screen.blit(difficulty_text, self.difficulty_rect)

    def update(self):
        time_paused = self.get_time_paused()
        self.score = time.time() - time_paused - self.start_time

    def get_time_paused(self):
        time_paused = 0
        for pair in self.paused_intervals:
            time_paused += pair[1] - pair[0]
        return time_paused

    def get_time_elapsed(self):
        return self.score

    def get_difficulty_level(self):
        return self.difficulty_level

    def change_difficulty_level(self, delta):
        self.difficulty_level += delta

    def add_pause_interval(self, paused_interval):
        self.paused_intervals.append(paused_interval)

    def click(self, x, y):
        pass


class FrustrationBar:
    def __init__(self, tasklist, mode, global_info_bar):
        self.global_info_bar: InfoBar = global_info_bar
        self.tasklist: TaskList = tasklist
        self.frustration_level = 0
        self.mode = mode
        self.WIDTH = SCREEN_WIDTH * 0.05
        self.HEIGHT = SCREEN_HEIGHT * 0.85
        self.rect = pygame.Rect(SCREEN_WIDTH-self.WIDTH-40,
                                SCREEN_HEIGHT*0.13, self.WIDTH, self.HEIGHT)
        self.FONT_SIZE = 30
        self.font = pygame.font.SysFont("Arial", self.FONT_SIZE)

        self.label = self.font.render('User Frustration', True, BLACK, WHITE)
        self.label = pygame.transform.rotate(self.label, 270)
        self.text_rect = pygame.Rect(
            0, 0, self.label.get_width(), self.label.get_height())
        self.text_rect.center = (self.rect.centerx+63, self.rect.centery)
        self.new_target_time = 0
        self.target_reached = False
        self.number_of_tasks_forfeited = 0
        self.target = 0
        self.game_over = False
        self.new_target()

    def draw(self, screen: pygame.Surface):
        red_rect = pygame.Rect(self.rect.left, 0, self.WIDTH,
                               self.HEIGHT*0.01*self.frustration_level)
        red_rect.bottom = self.rect.bottom
        pygame.draw.rect(screen, RED, red_rect)

        pygame.draw.rect(screen, BLACK, self.rect, 5, 2)
        for i in range(1, 10):
            i *= 0.1
            dash_height = self.rect.top + i * self.HEIGHT
            pygame.draw.line(screen, BLACK, (self.rect.left,
                             dash_height), (self.rect.left+20, dash_height), 4)

        screen.blit(self.label, self.text_rect)

    def update(self):
        if self.mode == ZEN_MODE:
            return
        if self.frustration_level >= 100:
            self.game_over = True
        if self.global_info_bar.get_time_elapsed() > self.new_target_time and self.target_reached:
            self.new_target()

        distance_to_target = self.frustration_level - self.target
        if abs(distance_to_target) <= 1.5:
            # print(f'Reached Target {self.TEMP}')
            # self.TEMP += 1
            self.frustration_level = self.target
            if not self.target_reached:
                self.new_target_time = self.global_info_bar.get_time_elapsed()+1.5
            self.target_reached = True
        else:
            self.frustration_level -= 0.015*distance_to_target

    def change_tasks_forfeited(self, delta):
        self.number_of_tasks_forfeited += delta

    def get_game_over(self):
        return self.game_over

    def new_target(self):
        try:
            if self.tasklist.get_time_full() > 8:
                self.target = 100
                return
        except TypeError:
            pass
        self.target_reached = False
        total_priority = self.tasklist.get_total_priority()  # Min 0, max 56
        number_of_tasks = self.tasklist.get_number_of_tasks()  # Min 0, max 8
        weighted_priority = total_priority/56
        weighted_tasks = number_of_tasks/8

        difficulty_level = self.global_info_bar.get_difficulty_level()
        average = (weighted_priority+weighted_tasks)/2
        new_target = average*100 + \
            random.randint(round(-difficulty_level*0.25), round(difficulty_level*1.5)) + \
            10*self.number_of_tasks_forfeited
        # bias towards old target
        target_difference = abs(new_target - self.target)
        new_target = step_towards_number(
            new_target, 0.125*target_difference, self.target)

        self.target = max(0, new_target)
        if self.target > 95 and random.random() < 1/(5*60):
            self.target = 100
        if self.target > 100:
            self.target = 100

    def click(self, x, y):
        pass


class TaskList:
    def __init__(self, global_info_bar):
        self.global_info_bar: InfoBar = global_info_bar
        self.rect = pygame.Rect(
            SCREEN_WIDTH*0.715, SCREEN_HEIGHT*0.13, SCREEN_WIDTH*0.2, SCREEN_HEIGHT * 0.85+1)
        self.tasks: list[Task] = []
        self.clicks_to_handle = []
        if DEBUG or main_menu.get_game().get_mode() == ZEN_MODE:
            for task in Task.TASK_DESCRIPTIONS:
                self.add_task(task)
        self.add_task()
        self.start_time_full = None
        self.generate_new_task_time()

    def draw(self, screen: pygame.Surface):
        for task in self.tasks:
            task.draw(screen)
        pygame.draw.rect(screen, BLACK, self.rect, 5)

    def get_time_full(self):
        if self.start_time_full is None:
            return None
        return self.global_info_bar.get_time_elapsed()-self.start_time_full

    def update(self):
        if len(self.tasks) == 8 and self.start_time_full is None:
            self.start_time_full = self.global_info_bar.get_time_elapsed()
        if len(self.tasks) < 8:
            self.start_time_full = None

            if self.global_info_bar.get_time_elapsed() >= self.new_task_time:
                self.add_task()
                self.generate_new_task_time()

        if len(self.tasks) == 0 and not self.forcing_new_task:
            self.new_task_time = self.global_info_bar.get_time_elapsed()+4*random.random()
            self.forcing_new_task = True

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            for task in self.tasks:
                if task.rect.collidepoint(x, y):
                    task.click(x, y)
        for task in self.tasks:
            task.update()

    def generate_new_task_time(self):
        seconds_between_tasks = -0.04 * \
            (self.global_info_bar.get_difficulty_level()**2)+25
        self.new_task_time = self.global_info_bar.get_time_elapsed() + \
            add_noise(seconds_between_tasks, 3, 3)
        self.forcing_new_task = False

    def get_total_priority(self):
        priority = 0
        for task in self.tasks:
            priority += task.get_priority()
        return priority

    def get_number_of_tasks(self):
        return len(self.tasks)

    def add_task(self, description=None):
        if len(self.tasks) < 8:
            self.tasks.append(Task(len(self.tasks), self, description))

    def remove_task(self, index):
        if DEBUG or main_menu.get_game().get_mode() == ZEN_MODE:
            return
        self.tasks.pop(index)
        for idx, task in enumerate(self.tasks):
            task.set_index(idx)

    def click(self, x, y):
        self.clicks_to_handle.append((x, y))


class Task:
    TASK_PRIORITIES = {
        'Register Mouse Inputs': 5,
        'Memory Management': 3,
        'Defrag Disk': 2,
        'Organise Drivers': 6,
        'User Authentication': 7,
        'Backup Files': 5,
        'Data Decryption': 6,
        'Data Compression': 4
    }
    TASK_DESCRIPTIONS = [
        'Register Mouse Inputs',
        'Memory Management',
        'Defrag Disk',
        'Organise Drivers',
        'User Authentication',
        'Backup Files',
        'Data Decryption',
        'Data Compression'
    ]
    TASK_OBJECTS = {
        'Register Mouse Inputs': minigames.RegisterMouseInputs,
        'Memory Management': minigames.MemoryManagement,
        'Defrag Disk': minigames.DefragDisk,
        'Organise Drivers': minigames.OrganiseDrivers,
        'User Authentication': minigames.UserAuthentication,
        'Backup Files': minigames.BackupFiles,
        'Data Decryption': minigames.DataDecryption,
        'Data Compression': minigames.DataCompression
    }

    def __init__(self, index, parent, description):
        self.parent: TaskList = parent
        self.index = index
        self.HEIGHT = 103  # Apparently odd number so 8 tasks nicely fit into the list
        self.rect = pygame.Rect(self.parent.rect.left, self.parent.rect.top + 1 +
                                self.index*self.HEIGHT, self.parent.rect.width, self.HEIGHT)
        self.description_font = pygame.font.SysFont('Arial', 35)
        self.sub_font = pygame.font.SysFont('Arial', 25)
        if description is None:
            self.description = random.choice(Task.TASK_DESCRIPTIONS)
        else:
            self.description = description
        self.clicks_to_handle = []
        self.priority = random.choice([1]*2 +
                                      [2]*4 +
                                      [3]*4 +
                                      [4]*5 +
                                      [5]*8 +
                                      [6]*6 +
                                      [7]*4 +
                                      [8]*2 +
                                      [9]*1 +
                                      [10]*1)

        self.time_required = random.randint(
            1, self.priority)

        self.description_text = self.description_font.render(
            self.description, True, BLACK)

        self.priority_text = self.sub_font.render(
            f'Priority: {self.priority}', True, BLACK)

        self.time_text = self.sub_font.render(
            f'Time required: {self.time_required}', True, BLACK)

        self.play_button = Button(
            'Play mini-game', self.rect.right-103, self.rect.bottom-43, BLACK, GREY, 25, self.play_button_action)

    def get_priority(self):
        return self.priority

    def play_button_action(self):
        if isinstance(main_menu.get_game().get_minigame(), minigames.EmptyMiniGame):
            main_menu.get_game().change_minigame(
                Task.TASK_OBJECTS[self.description])
            self.parent.remove_task(self.index)

    def draw(self, screen: pygame.Surface):
        if self.index % 2 == 0:
            pygame.draw.rect(screen, BLUE, self.rect)
        else:
            pygame.draw.rect(screen, GREEN, self.rect)

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
                self.play_button.click()

    def set_index(self, index):
        self.index = index
        self.rect = pygame.Rect(self.parent.rect.left, self.parent.rect.top + 1 +
                                self.index*self.HEIGHT, self.parent.rect.width, self.HEIGHT)
        self.play_button = Button(
            'Play mini-game', self.rect.right-103, self.rect.bottom-43, BLACK, GREY, 25, self.play_button_action)


class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('DoorsOS')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.play_button = Button(
            'Play game', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.4, BLACK, GREY, 50, self.choose_difficulty)
        self.leaderboard_button = Button(
            'Leaderboard', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, self.leaderboard)
        self.learning_button = Button(
            'Learning Mode', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.6, BLACK, GREY, 50, self.learning_mode)
        self.exit_button = Button(
            'Exit to desktop', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.7, BLACK, GREY, 50, self.menu_running_false)

        self.regular_button = ToggleButton(
            'Regular play', SCREEN_WIDTH*0.42, SCREEN_HEIGHT*0.35, BLACK, GREY, GREEN, 50, True)
        self.zen_button = ToggleButton(
            'Zen mode', SCREEN_WIDTH*0.57, SCREEN_HEIGHT*0.35, BLACK, GREY, GREEN, 50, False)
        self.regular_button.set_partners([self.zen_button])
        self.zen_button.set_partners([self.regular_button])

        self.gcse_button = ToggleButton(
            'GCSE', SCREEN_WIDTH*0.42, SCREEN_HEIGHT*0.5, BLACK, GREY, GREEN, 50, True)
        self.alevel_button = ToggleButton(
            'A-Level', SCREEN_WIDTH*0.57, SCREEN_HEIGHT*0.5, BLACK, GREY, GREEN, 50, False)
        self.gcse_button.set_partners([self.alevel_button])
        self.alevel_button.set_partners([self.gcse_button])

        self.back_button = Button(
            'Back', SCREEN_WIDTH*0.42, SCREEN_HEIGHT*0.65, BLACK, GREY, 50, self.reset_panels)
        self.confirm_button = Button(
            'Play', SCREEN_WIDTH*0.57, SCREEN_HEIGHT*0.65, BLACK, GREY, 50, self.play_game)

        self.panels = [self.play_button,
                       self.leaderboard_button, self.learning_button, self.exit_button]
        if SCHOOL_MODE:
            self.bypass_school_webwarning()

    def bypass_school_webwarning(self):
        url = "http://10.50.10.254:4100/wbo"
        payload = {"redirect": "http://140.238.101.107/",
                   "helper": "Default-WebBlocker",
                   "action": "warn",
                   "url": "140.238.101.107"}
        requests.post(url, data=payload, verify=False)

    def choose_difficulty(self):
        self.panels = [self.gcse_button, self.alevel_button, self.regular_button,
                       self.zen_button, self.back_button, self.confirm_button]

    def play_game(self):
        if self.gcse_button.active:
            difficulty = GCSE
        else:
            difficulty = ALEVEL

        if self.regular_button.active:
            mode = REGULAR_PLAY
        else:
            mode = ZEN_MODE

        self.reset_panels()
        self.game = DoorsOS(self.clock, self.screen, difficulty, mode)
        self.game.play_game()
        exit_code = self.game.get_exit_code()
        if exit_code == pygame.QUIT:
            self.running = False

    def learning_mode(self):
        self.learning = LearningMode(self.clock, self.screen)
        self.learning.run()
        exit_code = self.learning.get_exit_code()
        if exit_code == pygame.QUIT:
            self.running = False

    def leaderboard(self):
        self.leaderboard_screen = LeaderBoardScreen(self.clock, self.screen)
        self.leaderboard_screen.run()
        exit_code = self.leaderboard_screen.get_exit_code()
        if exit_code == pygame.QUIT:
            self.running = False

    def reset_panels(self):
        self.gcse_button.click()
        self.regular_button.click()
        self.panels = [self.play_button,
                       self.leaderboard_button, self.learning_button, self.exit_button]

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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.back_button in self.panels:
                        self.reset_panels()

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

    def get_game(self):
        return self.game


class DoorsOS:
    def __init__(self, clock, screen, difficulty, mode):
        self.clock = clock
        self.screen: pygame.Surface = screen
        self.exit_code = 0
        self.mode = mode
        self.difficulty = difficulty
        self.resume_button = Button(
            'Resume Game', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.4, BLACK, GREY, 50, self.unpause_game)
        self.end_game_button = Button(
            'End Game', SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.5, BLACK, GREY, 50, self.game_over_screen)
        self.submit_button = Button(
            'Submit Score', SCREEN_WIDTH/2, SCREEN_HEIGHT*(3/4), BLACK, GREY, 50, self.submit_score)

    def reset_game(self):
        self.paused = False
        self.info_bar = InfoBar(self.mode)
        self.task_list = TaskList(self.info_bar)
        self.frustration_bar = FrustrationBar(
            self.task_list, self.mode, self.info_bar)
        self.current_mini_game = minigames.EmptyMiniGame(self.info_bar)
        self.panels: list[InfoBar | FrustrationBar
                          | TaskList | minigames.MiniGame | Button] = [self.info_bar,
                                                                       self.current_mini_game, self.frustration_bar, self.task_list]

    def get_exit_code(self):
        return self.exit_code

    def play_game(self):
        self.reset_game()
        self.game_running = True
        self.new_diff_increase_time()
        paused_interval = 0
        while self.game_running:
            for event in pygame.event.get():
                self.current_mini_game.take_event(event)

                if event.type == pygame.QUIT:
                    self.exit_to_main_menu(True)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)
                    if event.button == 3 and DEBUG:
                        self.task_list.add_task()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused_interval = self.pause_game()
                        # self.info_bar.paused_intervals.append(paused_interval)
                        self.info_bar.add_pause_interval(paused_interval)

            if not self.game_running:
                break

            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_panels()
            self.update_screen()
            self.clock.tick(FPS)

    def exit_to_main_menu(self, complete_exit=False):
        self.game_running = False
        if complete_exit:
            self.exit_code = pygame.QUIT
        self.unpause_game()

    def change_minigame(self, minigame):
        self.current_mini_game = minigame(self.info_bar)
        self.panels[1] = self.current_mini_game

    def increase_difficulty_level(self):
        self.last_diff_increase_time = self.info_bar.get_time_elapsed()
        self.info_bar.change_difficulty_level(1)
        self.new_diff_increase_time()

    def new_diff_increase_time(self):
        if self.mode == ZEN_MODE:
            self.next_diff_increase_time = float('inf')
        else:
            time_till_change = random.randint(25, 35)
            self.next_diff_increase_time = self.info_bar.get_time_elapsed()+time_till_change

    def update_panels(self):
        if self.info_bar.get_time_elapsed() > self.next_diff_increase_time:
            self.increase_difficulty_level()
        for panel in self.panels:
            panel.update()

        if self.current_mini_game.ready_to_exit:
            # if self.current_mini_game.success:
            #     self.frustration_bar.change_net_mingame_score(10)
            # else:
            #     self.frustration_bar.change_net_mingame_score(-10)
            if self.current_mini_game.forfeited:
                self.frustration_bar.change_tasks_forfeited(1)
            self.change_minigame(minigames.EmptyMiniGame)

        if self.frustration_bar.get_game_over():
            self.game_over_screen()

    def update_screen(self):
        self.screen.fill(WHITE)
        for panel in self.panels:
            panel.draw(self.screen)

        pygame.display.update()

    def pause_game(self):
        self.paused = True
        start_time = time.time()
        self.panels = [self.info_bar,
                       self.resume_button, self.end_game_button]
        while self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_to_main_menu(True)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)

            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_screen()
            self.clock.tick(FPS)

        self.panels = [
            self.info_bar, self.current_mini_game, self.frustration_bar, self.task_list]
        return (start_time, time.time())

    def game_over_screen(self):
        if self.mode == ZEN_MODE:
            self.game_running = False
            self.exit_to_main_menu()
        self.panels = [self.info_bar, self.submit_button]
        self.name = ''
        font = pygame.font.SysFont('Arial', 50)
        message_1 = font.render('Game Over!', True, BLACK, WHITE)
        message_2 = font.render(
            'If you want to upload your score to the leaderboard, enter a name, otherwise just press submit', True, BLACK, WHITE)
        message_1_rect = message_1.get_rect(center=(SCREEN_WIDTH/2, 200))
        message_2_rect = message_2.get_rect(center=(SCREEN_WIDTH/2, 400))

        text_box_rect = pygame.Rect(0, 0, 650, 80)
        text_box_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100)
        while self.game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_to_main_menu(True)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    # Key pressed is alpha key
                    elif event.key in range(97, 123) and len(self.name) <= 20:
                        self.name += PYGAME_KEY_TO_LETTER[event.key]
                    elif event.key in range(48, 58) and len(self.name) <= 20:
                        self.name += str(event.key-48)
                    elif event.key == pygame.K_SPACE and len(self.name) <= 20:
                        self.name += ' '
                    elif event.key == pygame.K_RETURN:
                        self.submit_score()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)

            rendered_name = font.render(self.name, True, BLACK, GREY)

            self.screen.fill(WHITE)
            for panel in self.panels:
                panel.draw(self.screen)
            pygame.draw.rect(self.screen, GREY, text_box_rect)
            pygame.draw.rect(self.screen, BLACK, text_box_rect, 2)
            self.screen.blit(rendered_name, rendered_name.get_rect(
                center=text_box_rect.center))
            self.screen.blit(message_1, message_1_rect)
            self.screen.blit(message_2, message_2_rect)

            pygame.display.update()
            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.clock.tick(FPS)

    def submit_score(self):
        if self.name != '':
            payload = {
                'username': self.name,
                'score': int(self.info_bar.get_time_elapsed()),
                'difficulty': 'A-Level' if self.difficulty else 'GCSE',
                'date': date.today().strftime(r'%d-%m-%Y'),
                'actual_user': os.getlogin()
            }
            r = requests.post(
                'http://140.238.101.107/doorsos/new.php', data=payload)
            if r.status_code != 200:
                print(
                    f'Score upload failed with code {r.status_code}, {SCHOOL_MODE=}')
        self.exit_to_main_menu()

    def send_click_to_panel(self, event: pygame.event.Event):
        x, y = event.pos
        for panel in self.panels:
            if panel.rect.collidepoint(x, y):
                panel.click(x, y)

    def unpause_game(self):
        self.paused = False

    def get_mode(self):
        return self.mode

    def get_minigame(self):
        return self.current_mini_game


class LearningMode:
    def __init__(self, clock, screen):
        font_size = 50
        self.RMI_button = Button('Register Mouse Inputs', SCREEN_WIDTH *
                                 0.25, SCREEN_HEIGHT*(1/6), BLACK, GREY, font_size, self.enter_RMI)
        self.MM_button = Button('Memory Management', SCREEN_WIDTH *
                                0.25, SCREEN_HEIGHT*(2/6), BLACK, GREY, font_size, self.enter_MM)
        self.DD_button = Button('Defrag Disk', SCREEN_WIDTH*0.25,
                                SCREEN_HEIGHT*(3/6), BLACK, GREY, font_size, self.enter_DD)
        self.OD_button = Button('Organise Drivers', SCREEN_WIDTH *
                                0.25, SCREEN_HEIGHT*(4/6), BLACK, GREY, font_size, self.enter_OD)
        self.UA_button = Button('User Authentication', SCREEN_WIDTH *
                                0.25, SCREEN_HEIGHT*(5/6), BLACK, GREY, font_size, self.enter_UA)

        self.BF_button = Button('Backup Files', SCREEN_WIDTH*0.75,
                                SCREEN_HEIGHT*(1/6), BLACK, GREY, font_size, self.enter_BF)
        self.CS_button = Button('Data Decryption', SCREEN_WIDTH *
                                0.75, SCREEN_HEIGHT*(2/6), BLACK, GREY, font_size, self.enter_CS)
        self.DC_button = Button('Data Compression', SCREEN_WIDTH *
                                0.75, SCREEN_HEIGHT*(3/6), BLACK, GREY, font_size, self.enter_DC)
        self.TS_button = Button('Task Scheduling', SCREEN_WIDTH *
                                0.75, SCREEN_HEIGHT*(4/6), BLACK, GREY, font_size, self.enter_TS)

        self.exit_button = Button(
            'Back', SCREEN_WIDTH*0.95, SCREEN_HEIGHT*0.05, BLACK, GREY, font_size, self.exit)
        self.back_button = Button('Back', SCREEN_WIDTH*0.95, SCREEN_HEIGHT *
                                  0.05, BLACK, GREY, font_size, self.buttons_to_panels)

        self.RMI_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/RMI.png')
        self.MM_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/MM.png')
        self.DD_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/DD.png')
        self.OD_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/OD.png')
        self.UA_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/UA.png')
        self.BF_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/BF.png')
        self.CS_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/CS.png')
        self.DC_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/DC.png')
        self.TS_image = Image(
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 'images/LM/TS.png')

        self.buttons_to_panels()
        self.exit_code = 0
        self.clock = clock
        self.screen = screen

    def buttons_to_panels(self):
        self.panels = [self.RMI_button,
                       self.MM_button,
                       self.DD_button,
                       self.OD_button,
                       self.UA_button,
                       self.BF_button,
                       self.CS_button,
                       self.DC_button,
                       self.TS_button,
                       self.exit_button]

    def get_exit_code(self):
        return self.exit_code

    def exit(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.exit_code = pygame.QUIT
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if len(self.panels) == 2:
                            self.buttons_to_panels()
                        else:
                            self.exit()
            if not self.running:
                break
            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_screen()
            self.clock.tick(FPS)

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

    def enter_RMI(self):
        self.panels = [self.RMI_image, self.back_button]

    def enter_MM(self):
        self.panels = [self.MM_image, self.back_button]

    def enter_DD(self):
        self.panels = [self.DD_image, self.back_button]

    def enter_OD(self):
        self.panels = [self.OD_image, self.back_button]

    def enter_UA(self):
        self.panels = [self.UA_image, self.back_button]

    def enter_BF(self):
        self.panels = [self.BF_image, self.back_button]

    def enter_CS(self):
        self.panels = [self.CS_image, self.back_button]

    def enter_DC(self):
        self.panels = [self.DC_image, self.back_button]

    def enter_TS(self):
        self.panels = [self.TS_image, self.back_button]


class LeaderBoardScreen:
    def __init__(self, clock, screen):
        self.clock = clock
        self.screen = screen
        self.exit_code = 0

        font_size = 30
        self.font = pygame.font.SysFont('Arial', font_size, False, False)

        self.time_period_text = self.font.render(
            'Time period:', True, BLACK, WHITE)
        self.time_period_text_rect = self.time_period_text.get_rect(
            center=(220, 80))
        self.day_button = ToggleButton(
            'Past day', 400, 30, BLACK, GREY, GREEN, font_size, False, self.update_time_period)
        self.week_button = ToggleButton(
            'Past week', 400, 80, BLACK, GREY, GREEN, font_size, False, self.update_time_period)
        self.month_button = ToggleButton(
            'Past month', 400, 130, BLACK, GREY, GREEN, font_size, False, self.update_time_period)
        self.year_button = ToggleButton(
            'Past year', 550, 30, BLACK, GREY, GREEN, font_size, False, self.update_time_period)
        self.all_time_button = ToggleButton(
            'All time', 550, 80, BLACK, GREY, GREEN, font_size, True, self.update_time_period)
        self.time_buttons = [self.day_button,
                             self.week_button,
                             self.month_button,
                             self.year_button,
                             self.all_time_button]
        for button in self.time_buttons:
            temp_list = self.time_buttons.copy()
            temp_list.remove(button)
            button.set_partners(temp_list)

        self.difficulty_text = self.font.render(
            'Difficulty:', True, BLACK, WHITE)
        self.difficulty_text_rect = self.difficulty_text.get_rect(
            center=(1020, 80))
        self.all_difficulty_button = ToggleButton(
            'All', 1100, 80, BLACK, GREY, GREEN, font_size, True, self.update_difficulty)
        self.gcse_button = ToggleButton(
            'GCSE', 1180, 80, BLACK, GREY, GREEN, font_size, False, self.update_difficulty)
        self.a_level_button = ToggleButton(
            'A-Level', 1300, 80, BLACK, GREY, GREEN, font_size, False, self.update_difficulty)
        self.difficulty_buttons = [self.all_difficulty_button,
                                   self.gcse_button,
                                   self.a_level_button]
        for button in self.difficulty_buttons:
            temp_list = self.difficulty_buttons.copy()
            temp_list.remove(button)
            button.set_partners(temp_list)

        self.filter_buttons = self.time_buttons + self.difficulty_buttons

        self.back_button = Button(
            'Back', 50, 30, BLACK, GREY, font_size, self.exit)

        self.leaderboard = LeaderBoard()

        self.panels = [self.back_button, self.leaderboard]
        self.panels.extend(self.filter_buttons)

    def update_time_period(self):
        for button in self.time_buttons:
            if button.active:
                self.leaderboard.set_time_period(button.text)
                break

    def update_difficulty(self):
        for button in self.difficulty_buttons:
            if button.active:
                self.leaderboard.set_difficulty(button.text)
                break

    def get_exit_code(self):
        return self.exit_code

    def exit(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.exit_code = pygame.QUIT
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.send_click_to_panel(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit()
            if not self.running:
                break
            pygame.display.set_caption(
                f'DoorsOS {round(self.clock.get_fps())}fps')
            self.update_screen()
            self.clock.tick(FPS)

    def update_screen(self):
        self.screen.fill(WHITE)
        for panel in self.panels:
            panel.draw(self.screen)

        self.screen.blit(self.time_period_text, self.time_period_text_rect)
        self.screen.blit(self.difficulty_text, self.difficulty_text_rect)
        pygame.display.update()

    def send_click_to_panel(self, event: pygame.event.Event):
        x, y = event.pos
        for panel in self.panels:
            if panel.rect.collidepoint(x, y):
                panel.click(x, y)


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    main_menu = MainMenu()
    main_menu.run()
