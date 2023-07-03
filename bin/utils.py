from constants import *
import pygame


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
        if not isinstance(self, ToggleButton):
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


class ToggleButton(Button):
    def __init__(self, text, left, top, border_colour, background_colour, active_background_colour, font_size, active):
        super().__init__(text, left, top, border_colour, background_colour, font_size, None)
        self.active = active
        self.active_background_colour = active_background_colour

    @classmethod
    def from_centre_coords(cls, text, centre_x, centre_y, border_colour, background_colour, active_background_colour, font_size, active):
        font = pygame.font.SysFont('Arial', font_size)
        rendered_text = font.render(text, True, BLACK)
        rect = pygame.Rect(0, 0, rendered_text.get_width(),
                           rendered_text.get_height())
        rect.center = (centre_x, centre_y)
        return cls(text, rect.left, rect.top, border_colour, background_colour, active_background_colour, font_size, active)

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
