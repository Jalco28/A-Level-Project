from constants import *
import pygame


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
    def __init__(self, centre_x, centre_y):
        pass
