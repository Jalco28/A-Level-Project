import time
from constants import *
import pygame
import random
from math import radians, sin


class Button:
    def __init__(self, text, center_x, center_y, border_colour, background_colour, font_size, action):
        self.font = pygame.font.SysFont('Arial', font_size)
        self.text = text
        self.rendered_text = self.font.render(self.text, True, BLACK)
        self.rect = pygame.Rect(
            0, 0, self.rendered_text.get_width()*1.1, self.rendered_text.get_height()*1.2)
        self.rect.center = (center_x, center_y)
        self.text_rect = pygame.Rect(
            0, 0, self.rendered_text.get_width(), self.rendered_text.get_height())
        self.text_rect.center = self.rect.center
        self.border_colour = border_colour
        self.background_colour = background_colour
        if not isinstance(self, ToggleButton):
            self.action = action

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.background_colour, self.rect)
        pygame.draw.rect(screen, self.border_colour, self.rect, 2)
        screen.blit(self.rendered_text, self.text_rect)

    def update(self):
        pass

    def click(self, *args, **kwargs):
        self.action()


class ToggleButton(Button):
    def __init__(self, text, left, top, border_colour, background_colour, active_background_colour, font_size, active):
        super().__init__(text, left, top, border_colour, background_colour, font_size, None)
        self.active = active
        self.active_background_colour = active_background_colour

    def set_partners(self, partners):
        self.partners = partners

    def click(self, x, y):
        self.active = True
        for partner in self.partners:
            partner.active = False

    def draw(self, screen: pygame.Surface):
        if self.active:
            pygame.draw.rect(screen, self.active_background_colour, self.rect)
        else:
            pygame.draw.rect(screen, self.background_colour, self.rect)
        pygame.draw.rect(screen, self.border_colour, self.rect, 2)
        screen.blit(self.rendered_text, self.text_rect)


class Image:
    def __init__(self, center_x, center_y, image_name, scale=1):
        self.image = pygame.image.load(image_name)
        if scale != 1:
            self.image = pygame.transform.smoothscale(
                self.image, (scale*self.image.get_width(), scale*self.image.get_height()))
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        pass


class STTInfoBar:  # Score, target, time, info bar
    def __init__(self, target, time_allowed, global_info_bar):
        self.score = 0
        self.global_info_bar = global_info_bar
        self.target = target
        self.time_allowed = time_allowed
        self.start_timestamp = self.global_info_bar.score
        self.rect = pygame.Rect(
            10, 10, MINIGAME_WIDTH*0.8, MINIGAME_HEIGHT*0.08)
        self.font = pygame.font.SysFont("Arial", 30)

        score_text = self.font.render(
            f'Score: {self.score}', True,  BLACK, GREY)
        target_text = self.font.render(
            f'Target: {self.target}', True, BLACK, GREY)
        time_text = self.font.render(
            f'Time Remaining: {self.time_left}', True, BLACK, GREY)

        self.score_rect = score_text.get_rect(
            center=(self.rect.left+self.rect.width*0.25, self.rect.centery))

        self.target_rect = target_text.get_rect(
            center=(self.rect.left+self.rect.width*0.5, self.rect.centery))

        self.time_rect = time_text.get_rect(
            center=(self.rect.left+self.rect.width*0.75, self.rect.centery))

    @property
    def time_left(self):
        return max(int(self.time_allowed-(self.global_info_bar.score-self.start_timestamp)), 0)

    def add_score(self, delta):
        self.score += delta

    def subtract_score(self, delta):
        self.score -= delta

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3, 2)

        score_text = self.font.render(
            f'Score: {self.score}', True,  BLACK, GREY)
        target_text = self.font.render(
            f'Target: {self.target}', True, BLACK, GREY)
        time_text = self.font.render(
            f'Time Remaining: {self.time_left}', True, BLACK, GREY)

        screen.blit(score_text, self.score_rect)
        screen.blit(target_text, self.target_rect)
        screen.blit(time_text, self.time_rect)


class RMIButton:
    ID = 0
    IMAGE_NAMES = ['download',
                   'play',
                   'tick',
                   'cross',
                   'left',
                   'right',
                   'windows',
                   'apple',
                   'google']
    OFFSCREEN_OFFSET = 50

    def __init__(self, scam_chance, action, screen_rect: pygame.Rect, delete_button):
        self.ID = RMIButton.ID
        RMIButton.ID += 1
        self.screen_rect = screen_rect
        self.scam = (random.randint(1, 100) <= scam_chance)
        if self.scam:
            image_name = 'images\RMI\scam' + str(random.randint(1, 3)) + '.png'
        else:
            image_name = 'images\RMI\\' + \
                random.choice(RMIButton.IMAGE_NAMES) + '.png'
        self.image = pygame.image.load(image_name)
        # self.image = pygame.transform.smoothscale(self.image, (100, 100))
        self.speed = random.uniform(1.8, 3.7)

        # Pick random point on perimiter and push offscreen
        position = random.randint(
            0, 2*self.screen_rect.width+2*self.screen_rect.height)
        if 0 <= position <= self.screen_rect.width:  # Top Edge
            center_x = position
            center_y = -RMIButton.OFFSCREEN_OFFSET
        elif self.screen_rect.width < position <= self.screen_rect.width+self.screen_rect.height:  # Right Edge
            center_x = self.screen_rect.right+RMIButton.OFFSCREEN_OFFSET
            center_y = position-self.screen_rect.width
        elif self.screen_rect.width+self.screen_rect.height < position <= 2*self.screen_rect.width+self.screen_rect.height:  # Bottom Edge
            center_x = self.screen_rect.right - \
                (position-self.screen_rect.width-self.screen_rect.height)
            center_y = self.screen_rect.bottom+RMIButton.OFFSCREEN_OFFSET
        elif 2*self.screen_rect.width+self.screen_rect.height < position <= 2*self.screen_rect.width+2*self.screen_rect.height:  # Left Edge
            center_x = -RMIButton.OFFSCREEN_OFFSET
            center_y = self.screen_rect.bottom - \
                (position-2*self.screen_rect.width-self.screen_rect.height)

        self.x, self.y = center_x, center_y
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.target_coords = (random.randint(round(self.screen_rect.width*0.1), round(self.screen_rect.width*0.9)),
                              random.randint(round(self.screen_rect.height*0.1), round(self.screen_rect.height*0.9)))
        self.velocity = pygame.math.Vector2(
            (self.target_coords[0]-self.x, self.target_coords[1]-self.y))
        self.velocity.normalize_ip()
        self.velocity *= self.speed
        self.action = action
        self.has_been_on_screen = False
        self.delete_button = delete_button

    def draw(self, screen: pygame.Surface):
        if self.scam and DEBUG:
            pygame.draw.rect(screen, RED,
                             self.rect.inflate(20, 20))
        if DEBUG:
            pygame.draw.aaline(
                screen, BLUE, self.rect.center, self.target_coords)
        screen.blit(self.image, self.rect)

    def click(self):
        # Action will be function in RMI class that accepts ID of an RMIButton and deals with its click
        self.action(self.ID)

    def update(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.rect.center = (self.x, self.y)

        if self.rect.colliderect(self.screen_rect):
            self.has_been_on_screen = True

        if self.has_been_on_screen and not self.rect.colliderect(self.screen_rect):
            self.delete_button(self.ID)


class MMBin:
    def __init__(self, center_x, center_y, score):
        self.score = score
        self.back_image = pygame.image.load(r'images\MM\full_bin.png')
        self.front_image = pygame.image.load(r'images\MM\front_bin.png')
        self.font = pygame.font.SysFont('Arial', 20)
        self.score_text = self.font.render(str(self.score), True, WHITE)
        self.rect = self.back_image.get_rect(center=(center_x, center_y))
        self.back_wall_edge = self.rect.right-14

        self.highlight_start_time = 0

    def draw_back(self, screen: pygame.Surface):
        if DEBUG and time.time()-self.highlight_start_time < 2:
            pygame.draw.rect(screen, GREEN, self.rect.inflate(20, 20))
        screen.blit(self.back_image, self.rect)

    def draw_front(self, screen: pygame.Surface):
        screen.blit(self.front_image, self.rect)
        screen.blit(self.score_text, (self.rect.centerx-8, self.rect.top+20))
        if DEBUG:
            # pygame.draw.aalines(screen, RED, False, [
            #                     self.rect.topleft,
            #                     self.rect.bottomleft,
            #                     self.rect.bottomright,
            #                     self.rect.topright])
            pygame.draw.line(screen, RED, (self.back_wall_edge,
                             MINIGAME_HEIGHT), (self.back_wall_edge, 0))


class MMGarbage:
    ID = 0
    HOME_POS = (240, MINIGAME_HEIGHT*0.41)

    def __init__(self, delete_garbage, walls):
        self.image = pygame.image.load(r'images\MM\garbage.png')

        self.velocity = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(MMGarbage.HOME_POS)
        self.update_rect()
        self.walls: list[MMWall] = walls
        self.delete_garbage = delete_garbage
        self.freefall = False
        self.grabbed = False
        self.ID = MMGarbage.ID
        MMGarbage.ID += 1

    def update_rect(self):
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, screen: pygame.Surface):
        if not self.freefall:
            pygame.draw.line(screen, BLACK, (self.rect.right-10, self.rect.centery),
                             (250, MINIGAME_HEIGHT*0.405), 5)
        screen.blit(self.image, self.rect)
        if not self.freefall:
            pygame.draw.line(screen, BLACK, (self.rect.left+2, self.rect.centery),
                             (230, MINIGAME_HEIGHT*0.395), 5)

    def update(self):
        if self.freefall:
            self.velocity.y += MM_GRAVITY
            self.pos.x += self.velocity.x
            self.pos.y += self.velocity.y
        self.update_rect()

        COLLISSION_TOLERANCE = 0
        for wall in self.walls:
            if self.rect.colliderect(wall.rect):
                if abs(self.rect.bottom-wall.rect.top) <= COLLISSION_TOLERANCE and self.velocity.y > 0:
                    self.velocity.y *= -1
                elif abs(self.rect.top-wall.rect.bottom) <= COLLISSION_TOLERANCE and self.velocity.y < 0:
                    self.velocity.y *= -1
                else:
                    self.velocity.x = 0
                    self.rect.right = wall.rect.left
                    self.pos.x = self.rect.centerx

        if self.rect.y > 725:
            self.delete_garbage(self.ID)

    def drag(self, mouse_x, mouse_y):
        mouse_vector = pygame.math.Vector2(mouse_x, mouse_y)
        displacement_from_home = pygame.math.Vector2(
            MMGarbage.HOME_POS) - mouse_vector
        if displacement_from_home.magnitude() < 170:
            self.pos = mouse_vector
            self.update_rect()
        else:
            self.pos = pygame.math.Vector2(MMGarbage.HOME_POS) + displacement_from_home.normalize()*-170
            self.update_rect()
    def throw(self):
        """Returns if garbage was actually thrown"""
        self.grabbed = False
        displacement_from_home = pygame.math.Vector2(
            MMGarbage.HOME_POS) - self.pos
        if displacement_from_home.magnitude() > 50:
            self.velocity = 0.3*displacement_from_home
            self.freefall = True
            return True
        else:
            self.pos = pygame.math.Vector2(MMGarbage.HOME_POS)
            return False


class MMWall:
    def __init__(self, left):
        self.rect = pygame.Rect(left, 0, 10, 70)
        self.time = random.randint(0, 359)
        self.speed = random.uniform(0.3, 2)
        self.update()

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)

    def update(self):
        self.rect.top = 0.4*MINIGAME_HEIGHT + \
            sin(self.speed*radians(self.time))*200
        self.time += 1
        if self.time >= 360/self.speed:
            self.time = 0
