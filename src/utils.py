import time
from constants import *
import pygame
import random
from math import radians, sin, sqrt


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


class TimeInfoBar:
    def __init__(self, time_allowed, global_info_bar):
        self.global_info_bar = global_info_bar
        self.time_allowed = time_allowed
        self.start_timestamp = self.global_info_bar.score
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
        return max(int(self.time_allowed-(self.global_info_bar.score-self.start_timestamp)), 0)

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

    def change_custom_field_value(self, name, value):
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


class SDNode:
    RADIUS = 15

    def __init__(self, pos):
        self.pos = tuple(pos)
        self.grabbed = False

    def __repr__(self) -> str:
        return str(self.pos)

    def define_partners(self, partners):
        self.partners: list[SDNode] = partners

    def draw(self, surface, success):
        pygame.draw.circle(surface, BLACK, self.pos, self.RADIUS)
        pygame.draw.circle(surface, GREEN if success else BLUE,
                           self.pos, 0.9*SDNode.RADIUS)

    def drag(self, delta):
        self.pos = tuple_addition(self.pos, delta)

    def randomise_position(self):
        self.pos = (random.randint(round(0.1*MINIGAME_WIDTH), round(0.9*MINIGAME_WIDTH)),
                    random.randint(round(0.1*MINIGAME_HEIGHT), round(0.9*MINIGAME_HEIGHT)))


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
