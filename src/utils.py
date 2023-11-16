import time
from constants import *
import pygame
import random
from math import radians, sin, sqrt, degrees, pi
from statistics import median
import requests
import json
from datetime import date, timedelta


class Button:
    def __init__(self, text, center_x, center_y, border_colour, background_colour, font_size, action):
        self.font = pygame.font.SysFont('Arial', font_size)
        self.text = text
        self.rendered_text = self.font.render(self.text, True, BLACK)
        if self.text == 'All':
            self.rect = pygame.Rect(
                0, 0, self.rendered_text.get_width()*1.3, self.rendered_text.get_height()*1.2)
        else:
            self.rect = pygame.Rect(
                0, 0, self.rendered_text.get_width()*1.1, self.rendered_text.get_height()*1.2)
        self.rect.center = (center_x, center_y)
        self.text_rect = pygame.Rect(
            0, 0, self.rendered_text.get_width(), self.rendered_text.get_height())
        self.text_rect.center = self.rect.center
        self.border_colour = border_colour
        self.background_colour = background_colour
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
    def __init__(self, text, center_x, center_y, border_colour, background_colour, active_background_colour, font_size, active, action=None):
        super().__init__(text, center_x, center_y,
                         border_colour, background_colour, font_size, action)
        self.active = active
        self.active_background_colour = active_background_colour

    def set_partners(self, partners):
        self.partners = partners

    def click(self, x, y):
        self.active = True
        for partner in self.partners:
            partner.active = False
        if self.action is not None:
            self.action()

    def draw(self, screen: pygame.Surface):
        if self.active:
            pygame.draw.rect(screen, self.active_background_colour, self.rect)
        else:
            pygame.draw.rect(screen, self.background_colour, self.rect)
        pygame.draw.rect(screen, self.border_colour, self.rect, 2)
        screen.blit(self.rendered_text, self.text_rect)


class Image:
    def __init__(self, center_x, center_y, image_name, scale=1):
        self.image = pygame.image.load(image_name).convert_alpha()
        if scale != 1:
            self.image = pygame.transform.smoothscale(
                self.image, (scale*self.image.get_width(), scale*self.image.get_height()))
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        pass

    def click(self, *args, **kwargs):
        pass


class STTInfoBar:  # Score, target, time, info bar
    def __init__(self, target, time_allowed, global_info_bar):
        self.score = 0
        self.global_info_bar = global_info_bar
        self.target = target
        self.time_allowed = time_allowed
        self.start_timestamp = self.global_info_bar.get_time_elapsed()
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
        return max(int(self.time_allowed-(self.global_info_bar.get_time_elapsed()-self.start_timestamp)), 0)

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


class TimeInfoBar:
    def __init__(self, time_allowed, global_info_bar):
        self.global_info_bar = global_info_bar
        self.time_allowed = time_allowed
        self.start_timestamp = self.global_info_bar.get_time_elapsed()
        self.rect = pygame.Rect(
            10, 10, MINIGAME_WIDTH*0.8, MINIGAME_HEIGHT*0.08)
        self.font = pygame.font.SysFont("Arial", 30)

        time_text = self.font.render(
            f'Time Remaining: {self.time_left}', True, BLACK, GREY)

        self.time_rect = time_text.get_rect(center=self.rect.center)
        # Name:(value, rect, rendered text)
        self.custom_fields: dict[str,
                                 tuple[int | float, pygame.Rect, str]] = {}

    @property
    def time_left(self):
        return max(int(self.time_allowed-(self.global_info_bar.get_time_elapsed()-self.start_timestamp)), 0)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, GREY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3, 2)

        time_text = self.font.render(
            f'Time Remaining: {self.time_left}', True, BLACK, GREY)
        screen.blit(time_text, self.time_rect)

        self.update_custom_field_text()
        self.draw_custom_fields(screen)

    def add_custom_field(self, name, inital_value):
        text = self.font.render(f'{name}: {inital_value}', True, BLACK, GREY)
        total_number_of_fields = len(self.custom_fields) + 2
        field_spacing = self.rect.width/(total_number_of_fields+1)
        rect = text.get_rect(center=(
            self.rect.left+(len(self.custom_fields)+1)*field_spacing, self.rect.centery))
        self.custom_fields[name] = (inital_value, rect, text)

        self.time_rect.centerx = self.rect.left + \
            (len(self.custom_fields)+1)*field_spacing

    def update_custom_field_text(self):
        for field in self.custom_fields.items():
            key = field[0]
            value = field[1]
            value = (value[0], value[1], self.font.render(
                f'{key}: {value[0]}', True, BLACK, GREY))
            self.custom_fields[key] = value

    def draw_custom_fields(self, screen: pygame.Surface):
        for field in self.custom_fields.items():
            screen.blit(field[1][2], field[1][1])

    def set_custom_field_value(self, name, value):
        old_tuple = self.custom_fields[name]
        self.custom_fields[name] = (value, old_tuple[1], old_tuple[2])


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
            self.pos = pygame.math.Vector2(
                MMGarbage.HOME_POS) + displacement_from_home.normalize()*-170
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


class DDBlock:
    def __init__(self, coordinates: list[tuple[int, int]], center_x, center_y, colour, grid_rect: pygame.Rect):
        self.tile_size = 50
        self.grid_rect = grid_rect
        self.home_pos = (center_x, center_y)
        self.tile_image = pygame.image.load(f'images/DD/{colour}.png')
        self.normalise_coordinates(coordinates)

        no_tiles_wide = len(set(coord[0] for coord in self.coordinates))
        no_tiles_high = len(set(coord[1] for coord in self.coordinates))
        self.rect = pygame.Rect(0, 0, no_tiles_wide *
                                self.tile_size, no_tiles_high*self.tile_size)
        self.rect.center = (center_x, center_y)
        self.setup_collision_rects()
        self.grabbed = False

    def draw(self, screen: pygame.Surface):
        for tile in self.coordinates:
            screen.blit(self.tile_image, (self.rect.left + self.tile_size *
                        tile[0], self.rect.top + self.tile_size*tile[1]))
        if DEBUG:
            pygame.draw.circle(screen, BLACK, self.rect.center, 5)

    def normalise_coordinates(self, coordinates):
        min_x = min(coordinates, key=lambda x: x[0])[0]
        min_y = min(coordinates, key=lambda x: x[1])[1]
        delta = (-min_x, -min_y)
        self.coordinates = [tuple_addition(
            coord, delta) for coord in coordinates]

    def setup_collision_rects(self):
        self.collision_rects: list[pygame.Rect] = []
        for tile in self.coordinates:
            self.collision_rects.append(pygame.Rect(self.rect.left + self.tile_size *
                                                    tile[0], self.rect.top + self.tile_size*tile[1], self.tile_size, self.tile_size))

    def occupied_tiles(self):
        """Returns set of coords of occupied tiles"""
        coords = set()
        for tile in self.collision_rects:
            try:
                coords.add(DD_TILE_CENTERS_TO_COORDS[tile.center])
            except KeyError:  # Tile is not snapped to grid
                return set()
        return coords

    def ungrab(self, occupied_tiles: set):
        """Returns None if snap unsuccessful else returns newly occupied coords"""
        self.grabbed = False
        snap_delta = None

        # Check grid alignment
        if rect_full_collision(self.grid_rect.inflate(40, 40), self.rect):
            tile = self.collision_rects[0]
            deltas = [tuple_addition(
                (-tile.centerx, -tile.centery), tile_center) for tile_center in DD_TILE_CENTERS]
            snap_delta = min(deltas, key=tuple_pythag)
        else:
            if self.grid_rect.colliderect(self.rect):
                return self.go_home()
            else:
                return

        # passed_rects = 0
        # for rect in self.collision_rects:
        #     for grid_center in DD_TILE_CENTERS:
        #         if tuple_pythag(tuple_addition((-rect.centerx, -rect.centery), grid_center)) <= 25:
        #             passed_rects += 1
        #             if snap_delta is None:
        #                 snap_delta = tuple_addition(
        #                     (-rect.centerx, -rect.centery), grid_center)
        #             break
        # if passed_rects != len(self.collision_rects):
        #     if self.grid_rect.colliderect(self.rect):
        #         return self.go_home()
        #     else:
        #         return

        # Check grid occupation
        potential_occupations = set()
        for tile in self.collision_rects:
            moved_tile = tile.move(*snap_delta)
            coords = DD_TILE_CENTERS_TO_COORDS[moved_tile.center]
            if coords in occupied_tiles:
                if self.grid_rect.colliderect(self.rect):
                    return self.go_home()
                else:
                    return
            else:
                potential_occupations.add(coords)
        # Snap
        self.drag(snap_delta)
        return potential_occupations

    def drag(self, delta):
        self.rect.move_ip(*delta)
        for rect in self.collision_rects:
            rect.move_ip(*delta)

    def collide(self, x, y):
        for rect in self.collision_rects:
            if rect.collidepoint(x, y):
                return True
        return False

    def go_home(self):
        self.goto(*self.home_pos)

    def goto(self, x, y):
        self.rect.center = (x, y)
        self.setup_collision_rects()


class ODNode:
    RADIUS = 15

    def __init__(self, pos):
        self.pos = tuple(pos)
        self.grabbed = False

    def __repr__(self) -> str:
        return str(self.pos)

    def define_partners(self, partners):
        self.partners: list[ODNode] = partners

    def draw(self, surface, success):
        pygame.draw.circle(surface, BLACK, self.pos, self.RADIUS)
        pygame.draw.circle(surface, GREEN if success else BLUE,
                           self.pos, 0.9*ODNode.RADIUS)

    def drag(self, delta):
        self.pos = tuple_addition(self.pos, delta)

    def randomise_position(self):
        self.pos = (random.randint(round(0.2*MINIGAME_WIDTH), round(0.8*MINIGAME_WIDTH)),
                    random.randint(round(0.2*MINIGAME_HEIGHT), round(0.8*MINIGAME_HEIGHT)))


class UAPassword:
    def __init__(self, text, start_pos):
        self.hashinator_input_location = (583, 314)
        self.snap_locations = [self.hashinator_input_location, start_pos]
        self.font = pygame.font.SysFont('Arial', 24)
        self.text = text
        self.rendered_text = self.font.render(self.text, True, BLACK, GREY)
        self.rect = pygame.Rect(*start_pos, 170, 35)
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)
        self.grabbed = False

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, GREY, self.rect.inflate(-6, -6))
        screen.blit(self.rendered_text, self.text_rect)

    def drag(self, delta):
        self.rect.move_ip(*delta)
        self.text_rect.move_ip(*delta)

    def ungrab(self):
        """Returns true if snapped to hashinator"""
        self.grabbed = False
        for location in self.snap_locations:
            snap_tolerance = 30
            if tuple_pythag(tuple_addition((-location[0], -location[1]), self.rect.topleft)) < snap_tolerance:
                self.rect.topleft = location
                self.text_rect.center = self.rect.center
                if location == self.hashinator_input_location:
                    return True


class UARequest:
    def __init__(self, username, password, failed_attempts, correct_repsonse):
        self.correct_response = correct_repsonse
        self.title_font = pygame.font.SysFont('Arial', 50)
        self.body_font = pygame.font.SysFont('Arial', 30)
        self.username = username
        self.failed_attempts = failed_attempts
        self.rect = pygame.Rect(0, 0, 350, 200)
        self.rect.center = (200, 400)

        self.title_text = self.title_font.render('Login Request', True, BLACK)
        self.title_text_rect = self.title_text.get_rect(
            center=(self.rect.centerx, self.rect.top+30))

        self.username_text = self.body_font.render(
            f'Username: {self.username}', True, BLACK, GREY)
        self.username_text_rect = self.username_text.get_rect(
            topleft=(self.rect.left+20, self.rect.top+70))

        self.password_text = self.body_font.render(
            'Password:', True, BLACK, GREY)
        self.password_text_rect = self.password_text.get_rect(
            topleft=(self.rect.left+20, self.rect.top+110))
        self.password = UAPassword(
            password, (self.password_text_rect.right+10, self.password_text_rect.top+2))
        self.password_start_rect = pygame.Rect(
            self.password_text_rect.right+10, self.password_text_rect.top+2, 170, 35)

        self.failed_attempts_text = self.body_font.render(
            f'Failed Attempts: {self.failed_attempts}', True, BLACK, GREY)
        self.failed_attempts_text_rect = self.failed_attempts_text.get_rect(
            topleft=(self.rect.left+20, self.rect.top+150))

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, GREY, self.rect.inflate(-6, -6))
        pygame.draw.rect(screen, WHITE, self.password_start_rect)
        screen.blit(self.title_text, self.title_text_rect)
        screen.blit(self.username_text, self.username_text_rect)
        screen.blit(self.password_text, self.password_text_rect)
        screen.blit(self.failed_attempts_text, self.failed_attempts_text_rect)
        self.password.draw(screen)


class UAButton(Image):
    def __init__(self, center_x, center_y, image_name, action):
        super().__init__(center_x, center_y, image_name)
        self.action = action
        self.highlight_start_time = 0
        self.highlight_colour = WHITE
        self.highlighted = False

    def highlight(self, colour):
        self.highlight_start_time = time.time()
        self.highlight_colour = colour
        self.highlighted = True

    def draw(self, screen: pygame.Surface):
        if self.highlighted:
            if time.time()-self.highlight_start_time < 0.7:
                pygame.draw.circle(
                    screen, self.highlight_colour, self.rect.center, 70)
            else:
                self.highlighted = False
        screen.blit(self.image, self.rect)


class BFArrow:
    def __init__(self, pos, direction, globabl_info_bar):
        self.global_info_bar = globabl_info_bar
        self.image = pygame.image.load(rf'images/BF/{direction}.png')
        self.highlighted_image = pygame.image.load(
            rf'images/BF/highlighted/{direction}.png')
        self.rect = self.image.get_rect(center=pos)
        self.pressed = False
        self.highlighted = False
        self.scheduled_highlights = []

    def update(self):
        self.highlighted = False
        for highlight in self.scheduled_highlights:
            if highlight[0] <= self.global_info_bar.get_time_elapsed() <= highlight[1]:
                self.highlighted = True
                break
        try:
            if self.scheduled_highlights[-1][-1] < self.global_info_bar.get_time_elapsed():
                self.scheduled_highlights = []  # Clear schedule if all have been done
        except IndexError:  # There are no scheduled highlights
            pass

    def draw(self, screen: pygame.Surface, phase):
        if phase == BF_COPY:
            if self.pressed:
                screen.blit(self.highlighted_image, self.rect)
            else:
                screen.blit(self.image, self.rect)
        else:
            if self.highlighted:
                screen.blit(self.highlighted_image, self.rect)
            else:
                screen.blit(self.image, self.rect)


class CSOuter:
    def __init__(self, center, image_name):
        self.center = center
        self.angle = 0
        self.initial_image = pygame.image.load(image_name)
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect(center=self.center)

    def rotate_image_to(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(
            self.initial_image, -degrees(self.get_angle()))
        self.rect = self.image.get_rect(center=self.center)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def normalise_angle(self):
        if self.angle < 0 or self.angle <= 360:
            self.angle = self.angle % (2*pi)
            if self.angle < 0:
                self.angle += 2*pi

    def get_angle(self):
        self.normalise_angle()
        return self.angle

    def find_closest_angle(self):
        angle = min(CS_ANGLES, key=lambda x: abs(x-self.get_angle()))
        if angle == CS_ANGLES[-1]:
            angle = 0
        return angle

    def snap(self):
        self.rotate_image_to(self.find_closest_angle())


class DCBlock:
    TYPES = ['straight',
             'square',
             'L',
             'reverseL',
             'T',
             'Z',
             'reverseZ']

    def __init__(self, image, colour, global_info_bar):
        self.global_info_bar = global_info_bar
        self.colour = colour
        self.last_fall_time = self.global_info_bar.get_time_elapsed()
        self.tile_size = 50
        self.tile_image = image
        self.type = random.choice(DCBlock.TYPES)
        self.rotation_state = 0
        self.grid_offset = (4, -1)
        self.solid = False
        self.update_rect()

    def draw(self, screen: pygame.Surface):
        self.update_rect()
        # pygame.draw.rect(screen, BLACK, self.rect)
        for tile in self.get_tile_coords():
            screen.blit(self.tile_image, (self.rect.left + self.tile_size *
                        tile[0], self.rect.top + self.tile_size*tile[1]))
        # if DEBUG:
        #     pygame.draw.circle(screen, BLACK, self.rect.center, 5)

    def update(self, blocked_slots):
        if self.global_info_bar.get_time_elapsed()-self.last_fall_time >= 0.8:
            self.attempt_fall(blocked_slots)

    def update_rect(self):
        if self.type in ['straight', 'square']:
            self.rect = pygame.Rect(0, 0, 50*4, 50*4)
        else:
            self.rect = pygame.Rect(0, 0, 50*3, 50*3)
        self.rect.center = self.pixel_center_from_grid_offset()

    def pixel_center_from_grid_offset(self):
        if self.type in ['straight', 'square']:
            return tuple_addition(DC_GRID_TOP_LEFT, (50*(2+self.grid_offset[0])+1, 50*(2+self.grid_offset[1])+1))
        else:
            return tuple_addition(DC_GRID_TOP_LEFT, (50*(1.5+self.grid_offset[0])+1, 50*(1.5+self.grid_offset[1])+1))

    def rotate(self, direction, blocked_slots):
        assert direction in ['clockwise', 'anticlockwise']
        if direction == 'clockwise':
            self.change_rotation_state(1)
            potential_coords = self.get_grid_coords()
            self.change_rotation_state(-1)
        if direction == 'anticlockwise':
            self.change_rotation_state(-1)
            potential_coords = self.get_grid_coords()
            self.change_rotation_state(1)

        for coord in potential_coords:
            if coord in blocked_slots:
                return
            if coord[0] < 0 or coord[0] > 10:
                return
            if coord[1] < 0 or coord[1] > 12:
                return

        if direction == 'clockwise':
            self.change_rotation_state(1)
        elif direction == 'anticlockwise':
            self.change_rotation_state(-1)

    def change_rotation_state(self, delta):
        self.rotation_state += delta
        self.rotation_state %= 4

    def move(self, direction, blocked_slots):
        # self.grid_offset = tuple_addition(self.grid_offset, (-1, 0))
        if direction == 'left':
            potential_coords = [tuple_addition(
                (-1, 0), coord) for coord in self.get_grid_coords()]
        elif direction == 'right':
            potential_coords = [tuple_addition(
                (1, 0), coord) for coord in self.get_grid_coords()]
        success = True
        for coord in potential_coords:
            if coord in blocked_slots:
                success = False
                break
            if coord[0] < 0 or coord[0] > 10:
                success = False
                break
        if success:
            if direction == 'left':
                self.grid_offset = tuple_addition(self.grid_offset, (-1, 0))
            if direction == 'right':
                self.grid_offset = tuple_addition(self.grid_offset, (1, 0))

    def attempt_fall(self, blocked_slots, forced=False):
        if not forced:
            self.last_fall_time = self.global_info_bar.get_time_elapsed()
        potential_coords = [tuple_addition(
            (0, 1), coord) for coord in self.get_grid_coords()]
        success = True
        for coord in potential_coords:
            if coord in blocked_slots:
                success = False
                break
        if success:
            self.grid_offset = tuple_addition(self.grid_offset, (0, 1))
        else:
            self.solid = True

    def get_grid_coords(self):
        return [tuple_addition(self.grid_offset, coord) for coord in self.get_tile_coords()]

    def get_colour(self):
        return self.colour

    def get_tile_coords(self):
        return DC_TILES[self.type][self.rotation_state]

    def get_spawn_success(self, blocked_slots):
        for coord in self.get_grid_coords():
            if coord in blocked_slots:
                return False
        return True


class LeaderBoard:
    VERTICAL_LINES = [SCREEN_WIDTH *
                      (1/4), SCREEN_WIDTH*(1/2), SCREEN_WIDTH*(3/4)]

    def __init__(self):
        self.difficulty = 'All'
        self.time_period = 'All time'
        self.rect = pygame.Rect(14, 160, 1700, 800)
        self.font = pygame.font.SysFont('Arial', 30)

        self.position_text = self.font.render('Position', True, BLACK, GREY)
        self.position_text_rect = self.position_text.get_rect(
            centery=179, right=LeaderBoard.VERTICAL_LINES[0]-10)

        self.username_text = self.font.render('Username', True, BLACK, GREY)
        self.username_text_rect = self.username_text.get_rect(
            centery=179, right=LeaderBoard.VERTICAL_LINES[1]-10)

        self.score_text = self.font.render('Score', True, BLACK, GREY)
        self.score_text_rect = self.score_text.get_rect(
            centery=179, right=LeaderBoard.VERTICAL_LINES[2]-10)

        self.difficulty_text = self.font.render(
            'Difficulty', True, BLACK, GREY)
        self.difficulty_text_rect = self.difficulty_text.get_rect(
            centery=179, right=self.rect.right-10)

        self.download_data()
        self.update_rows()

    def draw(self, screen):
        pygame.draw.rect(screen, GREY, self.rect)
        for line in LeaderBoard.VERTICAL_LINES:
            pygame.draw.line(screen, BLACK, (line, self.rect.top),
                             (line, self.rect.bottom))

        screen.blit(self.position_text, self.position_text_rect)
        screen.blit(self.username_text, self.username_text_rect)
        screen.blit(self.score_text, self.score_text_rect)
        screen.blit(self.difficulty_text, self.difficulty_text_rect)

        for row in self.rows:
            row.draw(screen)

    def set_time_period(self, time_period):
        self.time_period = time_period
        self.update_rows()

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.update_rows()

    def download_data(self):
        r = requests.get('http://140.238.101.107/doorsos/read.php')
        self.all_data = json.loads(r.text)

    def matches_filters(self, data):
        if data['difficulty'] != self.difficulty and self.difficulty != 'All':
            return False
        date_achieved = data['date'].split('-')
        date_achieved = date(int(date_achieved[2]), int(
            date_achieved[1]), int(date_achieved[0]))

        if self.time_period == 'Past day':
            delta = timedelta(days=1)
        elif self.time_period == 'Past week':
            delta = timedelta(days=7)
        elif self.time_period == 'Past month':
            delta = timedelta(days=30)
        elif self.time_period == 'Past year':
            delta = timedelta(days=365)
        elif self.time_period == 'All time':
            delta = 'ALL'
        else:
            raise ValueError('Unknown date filter')

        if delta != 'ALL':
            target_date = date.today()-delta
            if date_achieved < target_date:
                return False

        return True

    def update_rows(self):
        filtered_data = [
            data for data in self.all_data if self.matches_filters(data)]
        filtered_data.sort(key=lambda x: x['score'], reverse=True)
        self.rows = [LeaderBoardRow((self.rect.left, self.rect.top+((i+1)*38)), data, i+1)
                     for i, data in enumerate(filtered_data[:20])]


class LeaderBoardRow:
    def __init__(self, topleft, data, position):
        self.rect = pygame.Rect(0, 0, 1700, 38)
        self.rect.topleft = topleft
        self.font = pygame.font.SysFont('Arial', 30)

        self.position_text = self.font.render(str(position), True, BLACK, GREY)
        self.position_text_rect = self.position_text.get_rect(
            centery=self.rect.centery, right=LeaderBoard.VERTICAL_LINES[0]-10)

        self.username_text = self.font.render(
            data['username'], True, BLACK, GREY)
        self.username_text_rect = self.username_text.get_rect(
            centery=self.rect.centery, right=LeaderBoard.VERTICAL_LINES[1]-10)

        self.score_text = self.font.render(
            str(data['score']), True, BLACK, GREY)
        self.score_text_rect = self.score_text.get_rect(
            centery=self.rect.centery, right=LeaderBoard.VERTICAL_LINES[2]-10)

        self.difficulty_text = self.font.render(
            data['difficulty'], True, BLACK, GREY)
        self.difficulty_text_rect = self.difficulty_text.get_rect(
            centery=self.rect.centery, right=self.rect.right-10)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.position_text, self.position_text_rect)
        screen.blit(self.username_text, self.username_text_rect)
        screen.blit(self.score_text, self.score_text_rect)
        screen.blit(self.difficulty_text, self.difficulty_text_rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)

    def click(self, x, y):
        pass


def tuple_addition(a, b):
    return tuple(sum(x) for x in zip(a, b))


def tuple_pythag(x):
    return sqrt(x[0]**2 + x[1]**2)


def rect_full_collision(big: pygame.Rect, small: pygame.Rect):
    if not big.colliderect(small):
        return False
    if small.top < big.top:
        return False
    if small.bottom > big.bottom:
        return False
    if small.left < big.left:
        return False
    if small.right > big.right:
        return False
    return True


def step_towards_number(value, step_size, target):
    return median([value-step_size, value+step_size, target])
