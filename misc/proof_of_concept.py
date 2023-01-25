import sys
import pygame as pg
import random


class Piece:
    def __init__(self, movable) -> None:
        if movable:
            self.x = random.randint((SCREEN_X/2)-100, (SCREEN_X/2)+100)
            self.y = random.randint((SCREEN_Y/2)-100, (SCREEN_Y/2)+100)
            self.image = colorize(pg.image.load('puzzle.png'), (255, 0, 0))
        else:
            self.x = SCREEN_X / 4
            self.y = SCREEN_Y / 4
            self.image = pg.image.load('puzzle.png')
            self.partner_locations = [
                (self.x-PARTNER_DISTANCE, self.y), (self.x+PARTNER_DISTANCE, self.y), (self.x, self.y+PARTNER_DISTANCE), (self.x, self.y-PARTNER_DISTANCE)]
        self.moving = False
        self.movable = movable

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self) -> pg.rect:
        return self.image.get_rect(topleft=(self.x, self.y))

    def motion(self, event):
        if not self.moving or not self.movable:
            return False
        self.x += event.rel[0]
        self.y += event.rel[1]
        return True

    def snap(self):
        for solid_piece in frozenset(solid_pieces):
            for location in solid_piece.partner_locations:
                if coordinate_difference((self.x, self.y), location) < SNAP_DISTANCE:
                    self.x, self.y = location
                    self.image = colorize(self.image, (0, 255, 0))
                    self.movable = False
                    self.partner_locations = [
                        (self.x-PARTNER_DISTANCE, self.y), (self.x+PARTNER_DISTANCE, self.y), (self.x, self.y+PARTNER_DISTANCE), (self.x, self.y-PARTNER_DISTANCE)]
                    solid_pieces.add(self)
                    solid_piece.partner_locations.remove(location)
                    try:
                        moving_pieces.remove(self)
                    except ValueError:
                        pass
                    break


def draw_screen() -> None:
    screen.fill((255, 255, 255))
    for solid_piece in solid_pieces:
        solid_piece.draw()
    for moving_piece in moving_pieces:
        moving_piece.draw()
    screen.blit(hud.render('Press "a" to spawn a new piece',
                True, pg.Color("coral")), (0, 0))
    pg.display.update()


def colorize(image, newColor):
    image.fill((0, 0, 0, 255), None, pg.BLEND_RGBA_MULT)
    image.fill(newColor + (0,), None, pg.BLEND_RGBA_ADD)
    return image


def coordinate_difference(a, b):
    return (abs(a[0]-b[0])+abs(a[1]-b[1]))


SCREEN_X: int = round(1920 * 0.5)
SCREEN_Y: int = round(1080 * 0.5)

pg.init()
screen = pg.display.set_mode((SCREEN_X, SCREEN_Y))
pg.display.set_caption("Operating System")
running: bool = True
clock = pg.time.Clock()
FPS = 60
PARTNER_DISTANCE = 99
SNAP_DISTANCE = 25
solid_pieces = set([Piece(False)])
moving_pieces = [Piece(True), Piece(True)]
hud = pg.font.SysFont("Arial", 18)

while running:
    ms_elapsed = clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for moving_piece in moving_pieces:
                if moving_piece.get_rect().collidepoint(event.pos):
                    moving_piece.moving = True

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for moving_piece in moving_pieces:
                if moving_piece.moving:
                    moving_piece.moving = False
                    moving_piece.snap()

        elif event.type == pg.MOUSEMOTION:
            for moving_piece in moving_pieces:
                moving_piece.motion(event)

        elif event.type == pg.KEYDOWN and event.key == pg.K_a:
            moving_pieces.append(Piece(True))

    draw_screen()
    pg.display.set_caption(
        f"Operating System {round(clock.get_fps(),1)} fps")

pg.quit()
sys.exit()
