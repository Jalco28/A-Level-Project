from constants import *
import pygame
import random
import time


class Button:
    def __init__(self, text, centre_x, centre_y, border_colour, background_colour, font_size, action):
        self.font = pygame.font.SysFont('Arial', font_size)
        self.text = text
        self.rendered_text = self.font.render(self.text, True, BLACK)
        self.rect = pygame.Rect(
            0, 0, self.rendered_text.get_width()*1.1, self.rendered_text.get_height()*1.2)
        self.rect.center = (centre_x, centre_y)
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
    def __init__(self, centre_x, centre_y, image_name, action):
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.rect.center = (centre_x, centre_y)
        self.action = action

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        pass

    def click(self):
        self.action()


class RMIButton:
    ID = 0
    IMAGE_NAMES = ['download_button',
                   'play_button',
                   '4icons']
    OFFSCREEN_OFFSET = 50

    def __init__(self, scam_chance, action, screen_rect: pygame.Rect, delete_button):
        self.ID = RMIButton.ID
        RMIButton.ID += 1
        self.screen_rect = screen_rect
        image_name = 'images\RMI\\' + \
            random.choice(RMIButton.IMAGE_NAMES) + '.png'
        self.image = pygame.image.load(image_name)
        self.image = pygame.transform.smoothscale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.speed = random.uniform(2, 4)
        self.scam = (random.randint(1, 100) <= scam_chance)

        # Pick random point on perimiter and push offscreen
        position = random.randint(
            0, 2*self.screen_rect.width+2*self.screen_rect.height)
        if 0 <= position <= self.screen_rect.width:  # Top Edge
            centre_x = position
            centre_y = -RMIButton.OFFSCREEN_OFFSET
        elif self.screen_rect.width < position <= self.screen_rect.width+self.screen_rect.height:  # Right Edge
            centre_x = self.screen_rect.right+RMIButton.OFFSCREEN_OFFSET
            centre_y = position-self.screen_rect.width
        elif self.screen_rect.width+self.screen_rect.height < position <= 2*self.screen_rect.width+self.screen_rect.height:  # Bottom Edge
            centre_x = self.screen_rect.right - \
                (position-self.screen_rect.width-self.screen_rect.height)
            centre_y = self.screen_rect.bottom+RMIButton.OFFSCREEN_OFFSET
        elif 2*self.screen_rect.width+self.screen_rect.height < position <= 2*self.screen_rect.width+2*self.screen_rect.height:  # Left Edge
            centre_x = -RMIButton.OFFSCREEN_OFFSET
            centre_y = self.screen_rect.bottom - \
                (position-2*self.screen_rect.width-self.screen_rect.height)

        self.x, self.y = centre_x, centre_y
        self.rect.center = (self.x, self.y)
        target_coords = (random.randint(round(self.screen_rect.width*0.1), round(self.screen_rect.width*0.9)),
                         random.randint(round(self.screen_rect.height*0.1), round(self.screen_rect.height*0.9)))
        self.velocity = pygame.math.Vector2(
            (target_coords[0]-self.x, target_coords[1]-self.y))
        self.velocity.normalize_ip()
        self.velocity *= self.speed
        self.action = action
        self.has_been_on_screen = False
        self.delete_button = delete_button

    def draw(self, screen: pygame.Surface):
        if self.scam and DEBUG:
            pygame.draw.rect(screen, FRUSTRATION_RED, self.rect.inflate(20,20))
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


class STTInfoBar:  # Score, target, time, info bar
    def __init__(self, target, time_allowed):
        self.score = 0
        self.target = target
        self.time_allowed = time_allowed
        self.start_timestamp = time.time()
        self.rect = pygame.Rect(
            10, 10, MINIGAME_WIDTH*0.8, MINIGAME_HEIGHT*0.08)
        self.font = pygame.font.SysFont("Arial", 30)

    @property
    def time_left(self):
        return round(self.time_allowed-(time.time()-self.start_timestamp))

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

        score_rect = pygame.Rect(
            0, 0, score_text.get_width(), score_text.get_height())
        score_rect.midleft = (
            self.rect.left+self.rect.width*0.15, self.rect.centery)

        target_rect = pygame.Rect(
            0, 0, target_text.get_width(), target_text.get_height())
        target_rect.center = (
            self.rect.left+self.rect.width*0.5, self.rect.centery)

        time_rect = pygame.Rect(
            0, 0, time_text.get_width(), time_text.get_height())
        time_rect.midleft = (
            self.rect.left+self.rect.width*0.7, self.rect.centery)

        screen.blit(score_text, score_rect)
        screen.blit(target_text, target_rect)
        screen.blit(time_text, time_rect)
