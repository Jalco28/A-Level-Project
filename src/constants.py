from math import radians
from datetime import datetime
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 1920*0.9, 1080*0.9
MINIGAME_WIDTH, MINIGAME_HEIGHT = SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.85
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (193, 199, 198)
RED = (240, 29, 29)
GREEN = (48, 194, 0)
BLUE = (5, 148, 237)
FPS = 60
GCSE = 0
ALEVEL = 1
REGULAR_PLAY = 0
ZEN_MODE = 1
MINIGAME = 0
MM_GRAVITY = 1
DD_TILE_CENTERS = [(429, 238), (429, 288), (429, 338), (429, 388), (429, 438), (429, 488), (429, 538), (429, 588), (479, 238), (479, 288), (479, 338), (479, 388), (479, 438), (479, 488), (479, 538), (479, 588), (529, 238), (529, 288), (529, 338), (529, 388), (529, 438), (529, 488), (529, 538), (529, 588), (579, 238), (579, 288), (579, 338), (579, 388), (579, 438), (579, 488), (579, 538), (
    579, 588), (629, 238), (629, 288), (629, 338), (629, 388), (629, 438), (629, 488), (629, 538), (629, 588), (679, 238), (679, 288), (679, 338), (679, 388), (679, 438), (679, 488), (679, 538), (679, 588), (729, 238), (729, 288), (729, 338), (729, 388), (729, 438), (729, 488), (729, 538), (729, 588), (779, 238), (779, 288), (779, 338), (779, 388), (779, 438), (779, 488), (779, 538), (779, 588)]
DD_TILE_CENTERS_TO_COORDS = dict(
    zip(DD_TILE_CENTERS, ((x, y) for x in range(8) for y in range(8))))
UA_USERNAMES = ['Alice',
                'Bob',
                'James',
                'Jodi',
                'Omar',
                'Callum',
                'George',
                'Lucas',
                'Ben',
                'Sasha',
                'Oscar',
                'Anthony',
                'Jack',
                'Finn',
                'Emily',
                'Holly',
                'Jayden',
                'Katie',
                'Leo',
                'Sam']
UA_PASSWORDS = ['password',
                'qwerty',
                'p@$$w0rd',
                'letmein',
                'dragon',
                'sunshine',
                'scratch_jr',
                '12345',
                'f00tb@all',
                '3302',
                'iamk00l_',
                'admin',
                'hello',
                'abc123',
                'qazwsx',
                'welcome',
                'k6e^DJA',
                'BaTmaN',
                'iluvdogs',
                'x@6a8qDU']
UA_TICK = 0
UA_CROSS = 1
UA_LOCK = 2
BF_WATCH = 0
BF_COPY = 1
CS_ANGLE_DELTA = radians(360/26)
CS_ANGLES = [i*CS_ANGLE_DELTA for i in range(27)]
CS_ANGLE_TO_INDEX = {angle: idx for idx, angle in enumerate(CS_ANGLES)}
CS_PHRASES = ['The mitochondria is the powerhouse of the cell',

              'RAM needs power to keep its contents',
              'RAM is volatile memory',
              'RAM is also called primary storage',

              'Secondary storage doesn\'t need power to keep its contents',
              'Secondary storage is non-volatile memory',
              'SSDs and hard drives are also called secondary storage',

              'Drivers allow peripheral devices to talk to the computer',
              'Data no longer needed in RAM is removed during \'garbage collection\'',
              'Disk defragmentation reorganises data on a hard drive',
              'Don\'t bother defragmenting an SSD!',
              'Back in my day we didn\'t have computers',
              'It\'s their job to play video games? Really?',
              'What\'s a you tube?',
              'You wouldn\'t steal a car...',
              f'Don\'t use {random.choice(["VBA", "COBOL", "Perl", "Pascal", "Fortran", "BASIC"])} in {datetime.now().year}',
              'You don\'t reuse passwords do you?'
              ]
DC_GRID_TOP_LEFT = ((MINIGAME_WIDTH/2)-(5.5*50), MINIGAME_HEIGHT-(50*13)-7)
# DC_TILES[PIECE_NAME][ROTATION_STATE] -> list of tile coords
DC_TILES = {
    'straight': {0: [(0, 2), (1, 2), (2, 2), (3, 2)],
                 1: [(2, 0), (2, 1), (2, 2), (2, 3)],
                 2: [(0, 2), (1, 2), (2, 2), (3, 2)],
                 3: [(2, 0), (2, 1), (2, 2), (2, 3)]},
    'square': {0: [(1, 1), (1, 2), (2, 1), (2, 2)],
               1: [(1, 1), (1, 2), (2, 1), (2, 2)],
               2: [(1, 1), (1, 2), (2, 1), (2, 2)],
               3: [(1, 1), (1, 2), (2, 1), (2, 2)]},
    'L': {0: [(0, 1), (0, 2), (1, 1), (2, 1)],
          1: [(0, 0), (1, 0), (1, 1), (1, 2)],
          2: [(0, 1), (1, 1), (2, 1), (2, 0)],
          3: [(1, 0), (1, 1), (1, 2), (2, 2)]},
    'reverseL': {0: [(0, 1), (1, 1), (2, 1), (2, 2)],
                 1: [(1, 0), (1, 1), (1, 2), (0, 2)],
                 2: [(0, 0), (0, 1), (1, 1), (2, 1)],
                 3: [(1, 0), (2, 0), (1, 1), (1, 2)]},
    'T': {0: [(0, 1), (1, 1), (1, 2), (2, 1)],
          1: [(1, 0), (1, 1), (1, 2), (0, 1)],
          2: [(1, 0), (0, 1), (1, 1), (2, 1)],
          3: [(1, 0), (1, 1), (2, 1), (1, 2)]},
    'Z': {0: [(0, 1), (1, 1), (1, 2), (2, 2)],
          1: [(2, 0), (2, 1), (1, 1), (1, 2)],
          2: [(0, 1), (1, 1), (1, 2), (2, 2)],
          3: [(2, 0), (2, 1), (1, 1), (1, 2)]},
    'reverseZ': {0: [(0, 2), (1, 2), (1, 1), (2, 1)],
                 1: [(1, 0), (1, 1), (2, 1), (2, 2)],
                 2: [(0, 2), (1, 2), (1, 1), (2, 1)],
                 3: [(1, 0), (1, 1), (2, 1), (2, 2)]}
}
DEBUG = False
