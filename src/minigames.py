import pygame
from constants import *
from utils import *
from copy import copy, deepcopy
from itertools import cycle, combinations, pairwise
from math import cos, pi, sin


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
        self.ending_message = self.font.render(
            'Task Forfeited!', True, BLACK, GREY)
        self.ending_message_rect = self.ending_message.get_rect(
            center=self.sub_rect.center)

    def update_ending_sequence(self):
        self.clicks_to_handle = []
        if self.countdown_start_time is None:
            self.countdown_start_time = self.global_info_bar.score
        if (self.global_info_bar.score - self.countdown_start_time >= 2) or DEBUG:
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
        self.info_bar = TimeInfoBar(10, global_info_bar)
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
        How this mess works:

        1. Generate all coords
        2. While there are still unallocated tiles:
            - Put a random unallocated tile into a working_list
            - Between 1 and 10 times try and change the position of one tile in working_list by one square ensuring its in bounds and not already taken
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
            for block in self.blocks:
                if block.grabbed:
                    newely_occupied_tiles = block.ungrab(self.occupied_tiles)
                    if newely_occupied_tiles is not None:
                        self.occupied_tiles.update(newely_occupied_tiles)

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
        """2D specialisation of Ronald Goldman's 3D line intersection
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
        self.setup_nodes()

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(WHITE)

        if DEBUG:
            for node in self.nodes:
                node.draw(self.sub_surface)

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

        self.info_bar.change_custom_field_value(
            'Line Crossings', len(self.intersections))

        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue

            for node in reversed(copy(self.nodes)):  # Check in reverse draw order
                if tuple_pythag(tuple_addition((-x, -y), node.pos)) <= SDNode.RADIUS:
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
        self.nodes: list[SDNode] = []
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
            self.nodes.append(SDNode(coord))

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
            SDNode(((MINIGAME_WIDTH/2)+30, (MINIGAME_HEIGHT/2)+30)),
            SDNode(((MINIGAME_WIDTH/2)-30, (MINIGAME_HEIGHT/2)-30))
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

        for node in self.nodes:
            node.randomise_position()
        self.info_bar.add_custom_field(
            'Line Crossings', self.count_intersections())

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
        self.label1 = self.font.render(
            'User Authentication', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class BackupFiles(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'File Access Control', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class DataEncryption(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'Data Encryption', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue


class DataCompression(MiniGame):
    def __init__(self, global_info_bar):
        super().__init__(global_info_bar)
        self.label1 = self.font.render(
            'Data Compression', True, BLACK, GREY)
        self.label1_rect = self.label1.get_rect(center=self.sub_rect.center)

    def draw(self, screen: pygame.Surface):
        if not self.running:
            return self.draw_ending_screen(screen)

        self.sub_surface.fill(GREY)
        self.sub_surface.blit(self.label1, self.label1_rect)

        self.common_drawing(screen)

    def update(self):
        if not self.running:
            return self.update_ending_sequence()
        while self.clicks_to_handle:
            x, y = self.clicks_to_handle.pop(0)
            click_used = False

            click_used = self.check_forfeit_buttons_clicked(
                x, y) or self.check_info_bar_clicked(x, y)
            if click_used:
                continue
