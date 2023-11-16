from hashlib import sha1
import pygame
from constants import *
from utils import *
from copy import copy, deepcopy
from itertools import cycle, combinations, pairwise
from math import cos, pi, sin, atan2
from functools import reduce
import operator
from string import ascii_lowercase, ascii_uppercase


class MiniGame:
    @staticmethod
    def translate_coords(x, y):
        """Converts whole screen coords to coords within sub_rect"""
        return x-5, y-(SCREEN_HEIGHT*0.13)

    def __init__(self, global_info_bar):
        self.rect = pygame.Rect(5, SCREEN_HEIGHT*0.13,
                                MINIGAME_WIDTH, MINIGAME_HEIGHT)
        self.sub_rect = pygame.Rect(
            0, 0, MINIGAME_WIDTH, MINIGAME_HEIGHT)
        self.clicks_to_handle = []
        self.font = pygame.font.SysFont('Arial', 70)
        self.instruction_font = pygame.font.SysFont('Arial', 40)
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
        self.forfeited = False

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
        self.forfeited = True
        self.ending_message = self.font.render(
            'Task Forfeited!', True, BLACK, GREY)
        self.ending_message_rect = self.ending_message.get_rect(
            center=self.sub_rect.center)

    def update_ending_sequence(self):
        self.clicks_to_handle = []
        if self.countdown_start_time is None:
            self.countdown_start_time = self.global_info_bar.get_time_elapsed()
        if (self.global_info_bar.get_time_elapsed() - self.countdown_start_time >= 2) or DEBUG:
            self.ready_to_exit = True

    def draw_ending_screen(self, screen: pygame.Surface):
        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.ending_message, self.ending_message_rect)
        self.draw_border()
        screen.blit(self.sub_surface, self.rect)

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

    def check_time(self):
        if self.info_bar.time_left == 0:
            self.running = False
            self.success = False
            self.ending_message = self.font.render(
                'Time over!', True, BLACK, GREY)
            self.ending_message_rect = self.ending_message.get_rect(
                center=self.sub_rect.center)

    def take_event(self, event):
        pass


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

        if not DEBUG:
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
        self.catapult_back = Image(240, MINIGAME_HEIGHT*0.46,
                                   r'images\MM\catapult_back.png')
        self.catapult_front = Image(240, MINIGAME_HEIGHT*0.46,
                                    r'images\MM\catapult_front.png')
        self.setup_bins()
        self.setup_walls()
        self.garbage_dict: dict[int, MMGarbage] = {}
        self.add_garbage()

    @property
    def catapult_garbage(self):
        return self.garbage_dict[self.catapult_garbage_ID]

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)

        pygame.draw.rect(self.sub_surface, BLACK, pygame.Rect(
            0, MINIGAME_HEIGHT*0.55, 250, 10), 0, 2)
        self.draw_bin_backs(self.sub_surface)
        self.catapult_back.draw(self.sub_surface)
        self.draw_garbage(self.sub_surface)
        self.draw_bin_fronts(self.sub_surface)
        self.catapult_front.draw(self.sub_surface)
        self.draw_walls(self.sub_surface)

        self.info_bar.draw(self.sub_surface)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()

        if not DEBUG:
            self.check_time_and_target()  # Check for game over

        for wall in self.walls:
            wall.update()

        for garbage in copy(self.garbage_dict).values():
            garbage.update()

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

            if self.catapult_garbage.rect.collidepoint(x, y):
                self.catapult_garbage.grabbed = True
                click_used = True
            if click_used:
                continue

    def setup_bins(self):
        scores = [10, 20, 30, 40, 30, 20, 10, 50]
        self.bins: list[MMBin] = []
        for i in range(8):
            bin = MMBin(460+98*i, MINIGAME_HEIGHT*0.902, scores.pop(0))
            self.bins.append(bin)

    def draw_bin_backs(self, screen):
        for bin in self.bins:
            bin.draw_back(screen)

    def draw_bin_fronts(self, screen):
        for bin in self.bins:
            bin.draw_front(screen)

    def draw_garbage(self, screen):
        for garbage in self.garbage_dict.values():
            garbage.draw(screen)

    def draw_walls(self, screen):
        for wall in self.walls:
            wall.draw(screen)

    def add_garbage(self):
        self.garbage_dict[MMGarbage.ID -
                          1] = MMGarbage(self.delete_garbage, self.walls)
        self.catapult_garbage_ID = MMGarbage.ID - 1

    def delete_garbage(self, ID):
        garbage = self.garbage_dict[ID]
        for bin in self.bins:
            if abs(garbage.rect.right - bin.back_wall_edge) <= 5:
                self.info_bar.add_score(bin.score)
                if DEBUG:
                    bin.highlight_start_time = time.time()
                break
        self.garbage_dict.pop(ID)

    def setup_walls(self):
        self.walls: list[MMWall] = [
            MMWall(self.bins[0].back_wall_edge),
            MMWall(self.bins[1].back_wall_edge),
            MMWall(self.bins[2].back_wall_edge),
            MMWall(self.bins[3].back_wall_edge),
            MMWall(self.bins[4].back_wall_edge),
            MMWall(self.bins[5].back_wall_edge),
            MMWall(self.bins[6].back_wall_edge),
            MMWall(self.bins[7].back_wall_edge)
        ]

    def take_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            if self.catapult_garbage.grabbed:
                self.catapult_garbage.drag(
                    *MiniGame.translate_coords(*event.pos))

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.catapult_garbage.grabbed:
                    garbage_thrown = self.catapult_garbage.throw()
                    if garbage_thrown:
                        self.add_garbage()
                        # pass


class DefragDisk(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.occupied_tiles = set()
        self.cell_size = 50
        grid_size = self.cell_size*8

        self.grid_rect = pygame.Rect(self.sub_rect.centerx-(grid_size/2),
                                     self.sub_rect.centery-(grid_size/2), grid_size, grid_size)
        self.info_bar = TimeInfoBar(120, global_info_bar)
        self.reset_button = Button('Reset blocks', self.info_bar.rect.centerx +
                                   350, self.info_bar.rect.centery, BLACK, WHITE, 30, self.reset_blocks)
        self.setup_blocks()

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)

        self.draw_grid(self.sub_surface)
        self.draw_blocks(self.sub_surface)

        self.info_bar.draw(self.sub_surface)
        self.reset_button.draw(self.sub_surface)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        if not DEBUG:
            self.check_time()  # Check for game over

        if len(self.occupied_tiles) == 64:  # Game won
            self.running = False
            self.success = True
            self.ending_message = self.font.render(
                'Puzzle Completed!', True, BLACK, GREY)
            self.ending_message_rect = self.ending_message.get_rect(
                center=self.sub_rect.center)

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            if self.reset_button.rect.collidepoint(x, y):
                self.reset_button.click()
                click_used = True
            if click_used:
                continue

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

            for block in reversed(copy(self.blocks)):  # Check in reverse draw order
                if block.collide(x, y):
                    # Move block to end of list
                    self.blocks.append(self.blocks.pop(
                        self.blocks.index(block)))
                    block.grabbed = True
                    self.occupied_tiles.difference_update(
                        block.occupied_tiles())
                    click_used = True
                    break
            if click_used:
                continue

    def draw_grid(self, surface):
        for i in range(0, 9):
            pygame.draw.line(surface, BLACK, (self.grid_rect.left+i*self.cell_size,
                             self.grid_rect.top), (self.grid_rect.left+i*self.cell_size, self.grid_rect.bottom))
        for i in range(0, 9):
            pygame.draw.line(surface, BLACK, (self.grid_rect.left, self.grid_rect.top+i *
                             self.cell_size), (self.grid_rect.right, self.grid_rect.top+i*self.cell_size))

    def draw_blocks(self, surface):
        for block in self.blocks:
            block.draw(surface)

    def setup_blocks(self):
        """
        1. Generate all coords
        2. While there are still unallocated tiles:
            - Put a random unallocated tile into a working_list
            - Between 1 and 10 times try and change the position of one tile in working_list by one square ensuring it's in bounds and not already taken
            - If a tile is out of bounds a regeneration is attempted
            - If a tile is already allocated a regeneration is attempted
        """
        self.blocks: list[DDBlock] = []
        block_arrangements: list[list[tuple[int, int]]] = []
        unallocated_coords = [(x, y) for x in range(0, 8) for y in range(0, 8)]
        valid_coords = deepcopy(unallocated_coords)
        while unallocated_coords:
            working_list = [unallocated_coords.pop(
                random.randint(0, len(unallocated_coords)-1))]
            for i in range(random.randint(1, 5)):
                choice = random.choice(working_list)
                new_tile = (-1, -1)
                attempts = 0
                MAX_ATTEMPTS = 20
                while ((new_tile not in valid_coords) or (new_tile not in unallocated_coords+[(-1, -1)])) and (attempts <= MAX_ATTEMPTS):
                    attempts += 1
                    indicie_to_change = random.randint(0, 1)
                    delta = random.choice((-1, 1))
                    if indicie_to_change == 0:
                        new_tile = (choice[0]+delta, choice[1])
                    if indicie_to_change == 1:
                        new_tile = (choice[0], choice[1]+delta)
                if attempts != MAX_ATTEMPTS+1:
                    working_list.append(new_tile)
                    unallocated_coords.remove(new_tile)
            block_arrangements.append(working_list)
        if DEBUG:
            print(f'Total blocks: {len(block_arrangements)}')

        vertical_spacing = 700//(len(block_arrangements)/4)
        column_1_centers = []
        column_2_centers = []
        column_3_centers = []
        column_4_centers = []
        extra_centers = [(400, 750), (600, 750), (800, 750)]
        for i in range(len(block_arrangements)//4):
            column_1_centers.append((100, 180+i*vertical_spacing))

        for i in range(len(block_arrangements)//4):
            column_2_centers.append((300, 180+i*vertical_spacing))

        for i in range(len(block_arrangements)//4):
            column_3_centers.append((900, 180+i*vertical_spacing))

        for i in range(len(block_arrangements)//4):
            column_4_centers.append((1100, 180+i*vertical_spacing))

        remaining_blocks = len(block_arrangements) - \
            (len(block_arrangements)//4)*4
        extra_centers = extra_centers[0:remaining_blocks]

        centers = column_1_centers + column_2_centers + \
            column_3_centers + column_4_centers + extra_centers
        # Place blocks in places irrespective of generation order
        random.shuffle(centers)
        colour_generator = cycle(
            ['blue', 'green', 'pink', 'red', 'yellow', 'purple'])
        for i in range(len(block_arrangements)):
            self.blocks.append(DDBlock(
                block_arrangements[i], centers[i][0], centers[i][1], next(colour_generator), self.grid_rect))

    def take_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            for block in self.blocks:
                if block.grabbed:
                    block.drag(event.rel)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for block in self.blocks:
                    if block.grabbed:
                        newly_occupied_tiles = block.ungrab(
                            self.occupied_tiles)
                        if newly_occupied_tiles is not None:
                            self.occupied_tiles.update(newly_occupied_tiles)

    def reset_blocks(self):
        self.occupied_tiles = set()
        for block in self.blocks:
            block.go_home()


class OrganiseDrivers(MiniGame):
    @staticmethod
    def convert_top_left_to_cartesian(coord: tuple[int]):
        return (coord[0], MINIGAME_HEIGHT-coord[1])

    @staticmethod
    def convert_cartesian_to_top_left(coord: pygame.math.Vector2):
        return (coord[0], MINIGAME_HEIGHT-coord[1])

    @staticmethod
    def cross_product_2d(a: pygame.math.Vector2, b: pygame.math.Vector2):
        return a[0]*b[1] - a[1]*b[0]

    @staticmethod
    def dot_product_2d(a: pygame.math.Vector2, b: pygame.math.Vector2):
        return a[0]*b[0] + a[1]*b[1]

    @staticmethod
    def check_line_intersection(p1: tuple[int], p2: tuple[int], p3: tuple[int], p4: tuple[int]):
        """2D specialisation of Ronald Goldman's 3D line intersection algorithm
            Returns False for no intersection or infinite intersection, tuple for unique intersection point"""
        p1 = pygame.math.Vector2(
            OrganiseDrivers.convert_top_left_to_cartesian(p1))
        p2 = pygame.math.Vector2(
            OrganiseDrivers.convert_top_left_to_cartesian(p2))
        p3 = pygame.math.Vector2(
            OrganiseDrivers.convert_top_left_to_cartesian(p3))
        p4 = pygame.math.Vector2(
            OrganiseDrivers.convert_top_left_to_cartesian(p4))
        l1_delta = p2-p1
        l2_delta = p4-p3

        try:
            lamda = OrganiseDrivers.cross_product_2d(
                p3-p1, l2_delta/OrganiseDrivers.cross_product_2d(l1_delta, l2_delta))
            mu = OrganiseDrivers.cross_product_2d(
                p3-p1, l1_delta/OrganiseDrivers.cross_product_2d(l1_delta, l2_delta))
        except ZeroDivisionError:  # Seems to happen when collinear
            return False

        # Lines are collinear
        if OrganiseDrivers.cross_product_2d(l1_delta, l2_delta) == 0 and OrganiseDrivers.cross_product_2d(p3-p1, l1_delta) == 0:
            return False
        # Lines are parallel and non-intersecting
        elif OrganiseDrivers.cross_product_2d(l1_delta, l2_delta) == 0 and OrganiseDrivers.cross_product_2d(p3-p1, l1_delta) != 0:
            return False
        # Intersect at unique point
        elif OrganiseDrivers.cross_product_2d(l1_delta, l2_delta) != 0 and (0 <= lamda <= 1) and (0 <= mu <= 1):
            if DEBUG:
                assert p1 + lamda*l1_delta == p3 + mu*l2_delta
            intersect_point = p1 + lamda*l1_delta

            # Check if intersection is at a node, disregard if so.
            if intersect_point in [p1, p2, p3, p4]:
                return False
            else:
                return OrganiseDrivers.convert_cartesian_to_top_left(intersect_point)
        # Also lines are parallel and non-intersecting
        else:
            return False

    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.intersections = []
        self.info_bar = TimeInfoBar(20, global_info_bar)
        self.instruction_text = self.instruction_font.render(
            'Move the circles to remove line crossings!', True, BLACK, WHITE)
        self.instruction_rect = self.instruction_text.get_rect(
            center=(MINIGAME_WIDTH/2, 100))
        self.setup_nodes()

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)
        self.sub_surface.blit(self.instruction_text, self.instruction_rect)

        if DEBUG:
            for node in self.nodes:
                node.draw(self.sub_surface, len(self.intersections) == 0)

            for connection in self.connections:
                pygame.draw.aaline(self.sub_surface, RED,
                                   self.nodes[connection[0]].pos, self.nodes[connection[1]].pos)

            for intersection in self.intersections:
                pygame.draw.circle(self.sub_surface, BLUE, intersection, 5)
        else:
            for connection in self.connections:
                pygame.draw.aaline(self.sub_surface, BLACK,
                                   self.nodes[connection[0]].pos, self.nodes[connection[1]].pos)

            for node in self.nodes:
                node.draw(self.sub_surface, len(self.intersections) == 0)

        self.info_bar.draw(self.sub_surface)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()

        self.intersections = []
        for connection_pair in combinations(self.connections, 2):
            intersect = self.check_line_intersection(
                self.nodes[connection_pair[0][0]].pos, self.nodes[connection_pair[0][1]].pos, self.nodes[connection_pair[1][0]].pos, self.nodes[connection_pair[1][1]].pos)
            if intersect:
                self.intersections.append(intersect)

        self.info_bar.set_custom_field_value(
            'Line Crossings', len(self.intersections))

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

            for node in reversed(copy(self.nodes)):  # Check in reverse draw order
                if tuple_pythag(tuple_addition((-x, -y), node.pos)) <= ODNode.RADIUS:
                    # Move node to end of list
                    # self.nodes.append(self.nodes.pop(self.nodes.index(node)))
                    node.grabbed = True
                    click_used = True
                    break
            if click_used:
                continue

    @property
    def invalid_new_connections(self):
        return self.connections+[tuple(reversed(x)) for x in self.connections]

    def setup_nodes(self):
        self.nodes: list[ODNode] = []
        self.connections = []
        radius = 340
        initial_nodes = random.randint(4, 7)
        rel_coords = []  # List of coords relative to center of screen

        for i in range(initial_nodes):  # Place nodes evenly around circle
            rel_coords.append(
                (radius*(cos((i*2*pi)/initial_nodes)), radius*(sin((i*2*pi)/initial_nodes))))

        abs_coords = [tuple_addition(
            (MINIGAME_WIDTH/2, MINIGAME_HEIGHT/2), coord) for coord in rel_coords]
        for coord in abs_coords:
            self.nodes.append(ODNode(coord))

        # Connect all initial nodes
        for connection in pairwise(range(initial_nodes)):
            self.connections.append(connection)
        self.connections.append((0, initial_nodes-1))

        # Add connections between initial nodes
        connections_left = random.randint(
            min(4, initial_nodes-3), initial_nodes-3)
        while connections_left > 0:
            new_connection = self.connections[0]
            while new_connection in self.invalid_new_connections or new_connection[0] == new_connection[1]:
                new_connection = (random.randint(
                    0, initial_nodes-1), random.randint(0, initial_nodes-1))
            if DEBUG:
                assert new_connection[0] != new_connection[1]

            casues_intersections = False
            for connection_pair in combinations(self.connections+[new_connection], 2):
                intersect = self.check_line_intersection(
                    self.nodes[connection_pair[0][0]].pos, self.nodes[connection_pair[0][1]].pos, self.nodes[connection_pair[1][0]].pos, self.nodes[connection_pair[1][1]].pos)
                if intersect:
                    casues_intersections = True

            if casues_intersections:
                continue
            else:
                self.connections.append(new_connection)
                connections_left -= 1

        # Add two nodes in middle
        self.nodes.extend([
            ODNode(((MINIGAME_WIDTH/2)+30, (MINIGAME_HEIGHT/2)+30)),
            ODNode(((MINIGAME_WIDTH/2)-30, (MINIGAME_HEIGHT/2)-30))
        ])

        # Try and connect extra nodes
        for i in range(2):
            node_index = len(self.nodes)-1-i
            attempts_left = 10
            while attempts_left > 0:
                new_connection = self.connections[0]
                while new_connection in self.invalid_new_connections or new_connection[0] == new_connection[1]:
                    new_connection = (
                        node_index, random.randint(0, len(self.nodes)-1))

                casues_intersections = False
                for connection_pair in combinations(self.connections+[new_connection], 2):
                    intersect = self.check_line_intersection(
                        self.nodes[connection_pair[0][0]].pos, self.nodes[connection_pair[0][1]].pos, self.nodes[connection_pair[1][0]].pos, self.nodes[connection_pair[1][1]].pos)
                    if intersect:
                        casues_intersections = True

                if not casues_intersections:
                    self.connections.append(new_connection)
                attempts_left -= 1

        while self.count_intersections() == 0:
            for node in self.nodes:
                node.randomise_position()

        self.info_bar.add_custom_field(
            'Line Crossings', self.count_intersections())
        self.update()

    def count_intersections(self):
        num_intersections = 0
        for connection_pair in combinations(self.connections, 2):
            intersect = self.check_line_intersection(
                self.nodes[connection_pair[0][0]].pos, self.nodes[connection_pair[0][1]].pos, self.nodes[connection_pair[1][0]].pos, self.nodes[connection_pair[1][1]].pos)
            if intersect:
                num_intersections += 1
        return num_intersections

    def take_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            for node in self.nodes:
                if node.grabbed:
                    node.drag(event.rel)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for node in self.nodes:
                    node.grabbed = False
                if len(self.intersections) == 0:
                    self.success = True
                    self.running = False
                    self.ending_message = self.font.render(
                        'Puzzle Completed!', True, BLACK, GREY)
                    self.ending_message_rect = self.ending_message.get_rect(
                        center=self.sub_rect.center)


class UserAuthentication(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.info_bar = STTInfoBar(10, 60, global_info_bar)
        self.small_font = pygame.font.SysFont('Arial', 29)
        button_offset = 150
        button_center = (MINIGAME_WIDTH/2)-75
        self.tick = UAButton(button_center-button_offset,
                             700, r'images/UA/tick.png', self.tick_response)
        self.cross = UAButton(button_center, 700,
                              r'images/UA/cross.png', self.cross_response)
        self.lock = UAButton(button_center+button_offset,
                             700, r'images/UA/lock.png', self.lock_response)
        self.buttons = [self.tick, self.cross, self.lock]
        self.clipboard = Image(1000, 410, r'images/UA/clipboard.png')
        self.hashinator = Image(600, 400, r'images/UA/hashinator.png')
        self.hashinator_text = ''

        self.instruction_text = self.small_font.render(
            'System Policy: Accounts must be locked on the third incorrect login attempt', True, BLACK, WHITE)
        self.instruction_text_rect = self.instruction_text.get_rect(
            center=(410, 140))

        self.setup_users()
        self.setup_clipboard_text_surf()
        self.new_request()

    def setup_users(self):
        active_users = set()
        while len(active_users) < 10:
            active_users.add(random.choice(UA_USERNAMES))
        self.inactive_users = list(set(UA_USERNAMES).difference(active_users))
        active_users = list(active_users)
        self.failed_attempts = {user: random.choice(
            [0, 0, 0, 1, 1, 1, 2, 2]) for user in UA_USERNAMES}

        active_passwords = set()
        while len(active_passwords) < 10:
            active_passwords.add(random.choice(UA_PASSWORDS))
        self.inactive_passwords = list(
            set(UA_PASSWORDS).difference(active_passwords))
        active_passwords = list(active_passwords)

        self.user_dict = {}
        for i in range(10):
            self.user_dict[active_users.pop(random.randint(0, len(
                active_users)-1))] = active_passwords.pop(random.randint(0, len(active_passwords)-1))

        self.hash_dict = {password: sha1(password.encode(
            'utf-8')).hexdigest()[0:10] for password in UA_PASSWORDS}

    def new_request(self):
        self.hide_hashinator_output()
        registered_user = random.randint(1, 100) <= 70
        if registered_user:
            username = random.choice(list(self.user_dict.keys()))
            password_correct = random.randint(1, 100) <= 60
            password = self.user_dict[username]
            if not password_correct:
                while password == self.user_dict[username]:
                    password = random.choice(UA_PASSWORDS)
        else:
            username = random.choice(self.inactive_users)
            password = random.choice(UA_PASSWORDS)
        failed_attempts = self.failed_attempts[username]

        if registered_user and password_correct:
            correct_response = UA_TICK
            self.failed_attempts[username] = 0
        elif failed_attempts >= 2:
            correct_response = UA_LOCK
            self.failed_attempts[username] += 10
            try:
                self.user_dict.pop(username)
            except KeyError:  # User was not active
                self.inactive_users.remove(username)
        else:
            correct_response = UA_CROSS
            self.failed_attempts[username] += 1

        self.request = UARequest(
            username, password, failed_attempts, correct_response)

    def tick_response(self):
        if self.request.correct_response == UA_TICK:
            self.tick.highlight(GREEN)
            self.info_bar.add_score(1)
        elif self.request.correct_response == UA_LOCK:
            self.lock.highlight(GREEN)
            self.tick.highlight(RED)
            self.info_bar.subtract_score(3)
        elif self.request.correct_response == UA_CROSS:
            self.cross.highlight(GREEN)
            self.tick.highlight(RED)
            self.info_bar.subtract_score(2)
        self.new_request()

    def cross_response(self):
        if self.request.correct_response == UA_CROSS:
            self.cross.highlight(GREEN)
            self.info_bar.add_score(2)
        elif self.request.correct_response == UA_TICK:
            self.tick.highlight(GREEN)
            self.cross.highlight(RED)
            self.info_bar.subtract_score(1)
        elif self.request.correct_response == UA_LOCK:
            self.lock.highlight(GREEN)
            self.cross.highlight(RED)
            self.info_bar.subtract_score(2)
        self.new_request()

    def lock_response(self):
        if self.request.correct_response == UA_LOCK:
            self.lock.highlight(GREEN)
            self.info_bar.add_score(3)
        elif self.request.correct_response == UA_TICK:
            self.tick.highlight(GREEN)
            self.lock.highlight(RED)
            self.info_bar.subtract_score(3)
        elif self.request.correct_response == UA_CROSS:
            self.cross.highlight(GREEN)
            self.lock.highlight(RED)
            self.info_bar.subtract_score(1)
        self.new_request()

    def draw_clipboard_text(self, screen: pygame.Surface):
        left = 865
        top = 220
        screen.blit(self.clipboard_text_surf, (left, top))

    def setup_clipboard_text_surf(self):
        top = 220
        left = 865
        hdelta = 135
        vdelta = 40
        users = list(self.user_dict.keys())
        passwords = list(self.user_dict.values())
        last_text_rect = self.small_font.render(
            self.hash_dict[passwords[-1]], True, BLACK).get_rect(topleft=(left+hdelta, top+9*vdelta))

        self.clipboard_text_surf = pygame.Surface(
            tuple_addition((-left, -top), (last_text_rect.right+30, last_text_rect.bottom)),  pygame.SRCALPHA, 32)
        for i in range(len(self.user_dict)):
            self.clipboard_text_surf.blit(self.small_font.render(
                users[i], True, BLACK), (0, i*vdelta))
            self.clipboard_text_surf.blit(self.small_font.render(
                self.hash_dict[passwords[i]], True, BLACK), (hdelta, i*vdelta))

    @property
    def hashinator_text_rect(self):
        return self.rendered_hashinator_text.get_rect(topleft=(590, 450))

    @property
    def rendered_hashinator_text(self):
        return self.small_font.render(self.hashinator_text, True, BLACK, GREY)

    def show_hashinator_output(self):
        self.hashinator_text = self.hash_dict[self.request.password.text]

    def hide_hashinator_output(self):
        self.hashinator_text = ''

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)

        self.sub_surface.blit(self.instruction_text,
                              self.instruction_text_rect)
        self.tick.draw(self.sub_surface)
        self.cross.draw(self.sub_surface)
        self.lock.draw(self.sub_surface)
        self.clipboard.draw(self.sub_surface)
        self.draw_clipboard_text(self.sub_surface)
        self.hashinator.draw(self.sub_surface)
        self.sub_surface.blit(self.rendered_hashinator_text,
                              self.hashinator_text_rect)
        self.request.draw(self.sub_surface)

        self.info_bar.draw(self.sub_surface)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()

        if not DEBUG:
            self.check_time_and_target()

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

            if self.request.password.rect.collidepoint(x, y):
                self.request.password.grabbed = True
                self.hide_hashinator_output()
                click_used = True
            if click_used:
                continue

            for button in self.buttons:
                if not click_used and button.rect.collidepoint(x, y):
                    button.action()
                    click_used = True
            if click_used:
                continue

    def take_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                snapped_to_hashinator = self.request.password.ungrab()
                if snapped_to_hashinator:
                    self.show_hashinator_output()

        if event.type == pygame.MOUSEMOTION:
            if self.request.password.grabbed:
                self.request.password.drag(event.rel)


class BackupFiles(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.instruction_text = self.instruction_font.render(
            'Watch the sequence, then use WASD to repeat it', True, BLACK, WHITE)
        self.instruction_text_rect = self.instruction_text.get_rect(
            center=(MINIGAME_WIDTH/2, 40))
        self.current_phase = BF_WATCH
        self.watch_phase_end = -1
        self.keys_previously_pressed = set()
        self.keys_currently_pressed = set()
        self.last_index_revealed = 0
        self.setup_dots()
        self.setup_arrows()
        self.setup_sequence()
        self.schedule_sequence(self.last_index_revealed+1)

    @property
    def phase_text(self):
        return self.instruction_font.render(f'Current phase: {"Watch" if self.current_phase == BF_WATCH else "Copy"}', True, BLACK, WHITE)

    def setup_arrows(self):
        arrow_spacing = 220
        vcenter = MINIGAME_HEIGHT/2+80
        hcenter = MINIGAME_WIDTH/2
        self.left = BFArrow(
            (hcenter-arrow_spacing, vcenter), 'left', self.global_info_bar)
        self.right = BFArrow(
            (hcenter+arrow_spacing, vcenter), 'right', self.global_info_bar)
        self.up = BFArrow(
            (hcenter, vcenter-arrow_spacing), 'up', self.global_info_bar)
        self.down = BFArrow(
            (hcenter, vcenter+arrow_spacing), 'down', self.global_info_bar)
        self.arrows = {'left': self.left,
                       'right': self.right,
                       'up': self.up,
                       'down': self.down}

    def setup_dots(self):
        x = 403
        x_delta = 50
        y = 160

        # index: (pos, colour)
        self.dots: dict[int, tuple[tuple[int, int], tuple[int, int, int]]] = {}

        for i in range(10):
            self.dots[i] = ((x+i*x_delta, y), WHITE)

    def setup_sequence(self):
        buttons = ['u', 'd', 'l', 'r']
        self.sequence = []
        for i in range(6):
            self.sequence.append(random.choice(buttons))
        for i in range(4):
            new = copy(buttons)
            new.pop(random.randint(0, 3))
            new.pop(random.randint(0, 2))
            if random.randint(1, 100) <= 15:  # 15% chance
                new.pop(random.randint(0, 1))
            self.sequence.append(''.join(sorted(reduce(operator.add, new))))
        # for i in range(2):
        #     new = copy(buttons)
        #     new.pop(random.randint(0, 3))
        #     self.sequence.append(''.join(sorted(reduce(operator.add, new))))

    def set_dot_colour(self, index, colour):
        self.dots[index] = (self.dots[index][0], colour)

    def schedule_sequence(self, length):
        self.current_phase = BF_WATCH
        for i in range(length):
            self.set_dot_colour(i, GREY)
        highlight_duration = 1
        gap = 0.3
        button_duration = highlight_duration+gap
        start_time = self.global_info_bar.get_time_elapsed()+gap
        self.watch_phase_end = start_time+length*button_duration
        for i in range(length):
            buttons = self.sequence[i]
            for button in buttons:
                if button == 'u':
                    self.up.scheduled_highlights.append(
                        (start_time+i*button_duration, (start_time+i*button_duration)+highlight_duration))
                elif button == 'l':
                    self.left.scheduled_highlights.append(
                        (start_time+i*button_duration, (start_time+i*button_duration)+highlight_duration))
                elif button == 'd':
                    self.down.scheduled_highlights.append(
                        (start_time+i*button_duration, (start_time+i*button_duration)+highlight_duration))
                elif button == 'r':
                    self.right.scheduled_highlights.append(
                        (start_time+i*button_duration, (start_time+i*button_duration)+highlight_duration))

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)
        self.sub_surface.fill(WHITE)

        for arrow in self.arrows.values():
            arrow.draw(self.sub_surface, self.current_phase)
        self.sub_surface.blit(self.instruction_text,
                              self.instruction_text_rect)
        self.sub_surface.blit(self.phase_text, (450, 80))
        for dot in self.dots.items():
            pygame.draw.circle(self.sub_surface, dot[1][1], dot[1][0], 10)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        for arrow in self.arrows.values():
            arrow.update()

        if self.current_phase == BF_WATCH and self.watch_phase_end < self.global_info_bar.get_time_elapsed():
            self.current_phase = BF_COPY
            self.input_index = 0

        elif self.current_phase == BF_COPY:
            if len(self.keys_currently_pressed) == 0 and len(self.keys_previously_pressed) != 0:
                inputted_keys = ''.join(
                    sorted(reduce(operator.add, self.keys_previously_pressed)))
                self.keys_previously_pressed = set()
                if inputted_keys == self.sequence[self.input_index]:
                    self.set_dot_colour(self.input_index, GREEN)
                    self.input_index += 1
                    if self.input_index == 10:
                        self.running = False
                        self.success = True
                        self.ending_message = self.font.render(
                            'Files succesfully backed up!', True, BLACK, GREY)
                        self.ending_message_rect = self.ending_message.get_rect(
                            center=self.sub_rect.center)
                    elif self.input_index-1 == self.last_index_revealed:
                        self.input_index = 0
                        self.last_index_revealed += 1
                        self.schedule_sequence(self.last_index_revealed+1)
                else:
                    self.running = False
                    self.success = False
                    self.ending_message = self.font.render(
                        'Incorrect Sequence!', True, BLACK, GREY)
                    self.ending_message_rect = self.ending_message.get_rect(
                        center=self.sub_rect.center)

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(x, y)
            if click_used:
                continue

    def take_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.current_phase == BF_COPY:
                if event.key == pygame.K_a:
                    self.left.pressed = True
                    self.keys_previously_pressed.add('l')
                    self.keys_currently_pressed.add('l')
                elif event.key == pygame.K_d:
                    self.right.pressed = True
                    self.keys_previously_pressed.add('r')
                    self.keys_currently_pressed.add('r')
                elif event.key == pygame.K_s:
                    self.down.pressed = True
                    self.keys_previously_pressed.add('d')
                    self.keys_currently_pressed.add('d')
                elif event.key == pygame.K_w:
                    self.up.pressed = True
                    self.keys_previously_pressed.add('u')
                    self.keys_currently_pressed.add('u')

        if event.type == pygame.KEYUP:
            if self.current_phase == BF_COPY:
                if event.key == pygame.K_a:
                    self.left.pressed = False
                    self.keys_currently_pressed.discard('l')
                elif event.key == pygame.K_d:
                    self.right.pressed = False
                    self.keys_currently_pressed.discard('r')
                elif event.key == pygame.K_s:
                    self.down.pressed = False
                    self.keys_currently_pressed.discard('d')
                elif event.key == pygame.K_w:
                    self.up.pressed = False
                    self.keys_currently_pressed.discard('u')


class DataDecryption(MiniGame):
    num_to_lower_alpha = {idx: letter for idx,
                          letter in enumerate(ascii_lowercase)}
    num_to_upper_alpha = {idx: letter for idx,
                          letter in enumerate(ascii_uppercase)}

    lower_alpha_to_num = {letter: idx for idx,
                          letter in enumerate(ascii_lowercase)}
    upper_alpha_to_num = {letter: idx for idx,
                          letter in enumerate(ascii_uppercase)}

    @classmethod
    def ceaser_shift(cls, text: str, delta: int):
        if delta == 0:
            return text
        shifted_text = ''
        for char in text:
            if not char.isalpha():
                shifted_text += char
                continue
            if char.islower():
                old_index = cls.lower_alpha_to_num[char]
                new_index = (old_index+delta) % 26
                new_char = cls.num_to_lower_alpha[new_index]
                shifted_text += new_char
                continue
            if char.isupper():
                old_index = cls.upper_alpha_to_num[char]
                new_index = (old_index+delta) % 26
                new_char = cls.num_to_upper_alpha[new_index]
                shifted_text += new_char
                continue
            raise RuntimeError(f'Character {char} not handled')
        return shifted_text

    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.info_bar = STTInfoBar(10, 60, global_info_bar)
        self.phrase_font = pygame.font.SysFont('Arial', 35)

        self.ring_center = (MINIGAME_WIDTH/2, MINIGAME_HEIGHT/2+100)
        self.outer = CSOuter(self.ring_center, r'images/cs/outer.png')
        self.inner = Image(*self.ring_center, r'images/cs/inner.png')
        self.outer_grabbed = False
        self.initial_grab_angle = 0
        self.shift_delta = 0
        self.mouse_angle = 0
        self.distance = 0
        self.unused_phrases = copy(CS_PHRASES)
        self.phrase_colour = BLACK
        self.green_text_end = -1
        self.new_phrase()

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)
        self.inner.draw(self.sub_surface)
        self.outer.draw(self.sub_surface)

        self.sub_surface.blit(self.rendered_phrase, self.phrase_rect)
        self.info_bar.draw(self.sub_surface)
        self.common_drawing(screen)

    def new_phrase(self):
        if len(self.unused_phrases) == 0:
            self.unused_phrases = copy(CS_PHRASES)

        self.correct_phrase = random.choice(self.unused_phrases)
        self.unused_phrases.remove(self.correct_phrase)
        self.encrypted_phrase = self.correct_phrase
        while self.encrypted_phrase == self.correct_phrase:
            self.encrypted_phrase = DataDecryption.ceaser_shift(
                self.correct_phrase, random.randint(0, 25))
        self.render_phrase()

    def change_range(self, angle):
        """Changes range from {-180, 180} to {0, 360}"""
        if angle < 0:
            angle += 2*pi

        return angle

    def get_angle_to_mouse(self, mouse_x, mouse_y):
        delta = tuple_addition(self.ring_center, (-mouse_x, -mouse_y))
        self.mouse_angle = self.change_range(atan2(delta[1], delta[0]))
        return self.mouse_angle

    def get_distance_to_mouse(self, mouse_x, mouse_y):
        delta = tuple_addition(self.ring_center, (-mouse_x, -mouse_y))
        self.distance = tuple_pythag(delta)
        return self.distance

    def update_shift_delta(self):
        delta = CS_ANGLE_TO_INDEX[self.outer.find_closest_angle()]
        if delta != self.shift_delta:
            self.shift_delta = delta
            self.render_phrase()

    def render_phrase(self):
        self.rendered_phrase = self.phrase_font.render(DataDecryption.ceaser_shift(
            self.encrypted_phrase, self.shift_delta), True, self.phrase_colour, WHITE)
        self.phrase_rect = self.rendered_phrase.get_rect(
            center=(MINIGAME_WIDTH/2, 150))

    def make_text_green(self):
        self.green_text_end = self.global_info_bar.get_time_elapsed() + 0.5
        self.phrase_colour = GREEN
        self.render_phrase()

    def update(self):
        if not self.running:
            return self.update_ending_sequence()

        if not DEBUG:
            self.check_time_and_target()

        if self.phrase_colour == GREEN and self.green_text_end < self.global_info_bar.get_time_elapsed():
            self.phrase_colour = BLACK
            self.new_phrase()

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

            if 250 <= self.get_distance_to_mouse(x, y) <= 310:
                self.outer_grabbed = True
                self.initial_grab_angle = self.get_angle_to_mouse(x, y)
                self.initial_wheel_angle = self.outer.get_angle()

    def take_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.outer_grabbed and not self.phrase_colour == GREEN:
                self.outer.rotate_image_to(self.initial_wheel_angle+(self.get_angle_to_mouse(
                    *MiniGame.translate_coords(*event.pos))-self.initial_grab_angle))
                self.update_shift_delta()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.outer_grabbed:
                    self.outer_grabbed = False
                    self.outer.snap()
                    if DataDecryption.ceaser_shift(self.encrypted_phrase, self.shift_delta) == self.correct_phrase:
                        self.info_bar.add_score(1)
                        self.make_text_green()


class DataCompression(MiniGame):
    @staticmethod
    def grid_coords_to_pixel_top_left(coords):
        return tuple_addition(DC_GRID_TOP_LEFT, (50*coords[0]+1, 50*coords[1]+1))

    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.num_rows_cleared = 0
        self.row_clear_target = random.randint(4, 6)
        self.info_bar = TimeInfoBar(500, global_info_bar)
        self.info_bar.add_custom_field(
            'Rows to clear', self.rows_to_clear)
        self.setup_images()
        # Grid Coord -> colour
        self.blocked_slots = {(i, 13): None for i in range(11)}
        self.new_block()

    @property
    def rows_to_clear(self):
        return self.row_clear_target-self.num_rows_cleared

    def setup_images(self):
        self.colours = ['blue', 'green', 'pink', 'purple', 'red', 'yellow']
        self.surfaces = {colour: pygame.image.load(
            f'images/DC/{colour}.png') for colour in self.colours}
        self.colours = cycle(self.colours)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)
        self.sub_surface.fill(WHITE)
        self.block.draw(self.sub_surface)
        self.draw_blocked_slots()
        self.draw_grid()

        self.info_bar.draw(self.sub_surface)
        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        if not DEBUG:
            self.check_time()

        if self.block.solid:
            colour = self.block.get_colour()
            for coord in self.block.get_grid_coords():
                self.blocked_slots[coord] = colour
            self.new_block()
        self.block.update(self.blocked_slots)

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

    def draw_grid(self):
        # Vertical
        for i in range(12):
            pygame.draw.line(self.sub_surface, GREY, tuple_addition(DC_GRID_TOP_LEFT, (
                i*50, 0)), tuple_addition(DC_GRID_TOP_LEFT, (i*50, MINIGAME_HEIGHT)), 2)
        # Horizontal
        for i in range(14):
            pygame.draw.line(self.sub_surface, GREY, tuple_addition(DC_GRID_TOP_LEFT, (
                0, i*50)), tuple_addition(DC_GRID_TOP_LEFT, (50*11, i*50)), 2)

    def draw_blocked_slots(self):
        for coord, colour in self.blocked_slots.items():
            if colour is None:
                continue
            pixel_coords = DataCompression.grid_coords_to_pixel_top_left(coord)
            self.sub_surface.blit(self.surfaces[colour], pixel_coords)

    def new_block(self):
        self.check_completed_rows()
        if self.rows_to_clear <= 0:
            self.running = False
            self.success = True
            self.ending_message = self.font.render(
                'Data Successfully Compressed!', True, BLACK, GREY)
            self.ending_message_rect = self.ending_message.get_rect(
                center=self.sub_rect.center)
        self.info_bar.set_custom_field_value(
            'Rows to clear', self.rows_to_clear)
        new_colour = next(self.colours)
        self.block = DCBlock(
            self.surfaces[new_colour], new_colour, self.global_info_bar)
        successful_spawn = self.block.get_spawn_success(self.blocked_slots)
        if not successful_spawn:
            self.running = False
            self.success = False
            self.ending_message = self.font.render(
                'Overflow: Data Corrupted!', True, BLACK, GREY)
            self.ending_message_rect = self.ending_message.get_rect(
                center=self.sub_rect.center)

    def check_completed_rows(self):
        cleared_rows = []
        for row_number in range(13):
            taken_slots_in_row = [
                coord for coord in self.blocked_slots if coord[1] == row_number]
            if len(taken_slots_in_row) == 11:
                cleared_rows.append(row_number)

        self.num_rows_cleared += len(cleared_rows)
        for row_number in cleared_rows:
            for item in sorted(self.blocked_slots.items(), key=lambda x: x[0][1], reverse=True):
                coord, colour = item
                if coord[1] == row_number:
                    self.blocked_slots.pop(coord)
                if coord[1] < row_number:
                    self.blocked_slots.pop(coord)
                    new_coord = tuple_addition(coord, (0, 1))
                    assert new_coord not in self.blocked_slots
                    self.blocked_slots[new_coord] = colour

    def take_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.block.rotate('clockwise', self.blocked_slots)
            elif event.key == pygame.K_q:
                self.block.rotate('anticlockwise', self.blocked_slots)
            elif event.key == pygame.K_a:
                self.block.move('left', self.blocked_slots)
            elif event.key == pygame.K_d:
                self.block.move('right', self.blocked_slots)
            elif event.key == pygame.K_s:
                self.block.attempt_fall(self.blocked_slots, True)
