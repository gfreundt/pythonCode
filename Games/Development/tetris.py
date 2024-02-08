import pygame
from pygame.locals import *
from random import randrange, choice
import sys, os
from datetime import datetime as dt
from datetime import timedelta as td
import time
from copy import deepcopy as copy
import numpy as np

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import game_shell as shell

pygame.init()


class Game:
    def __init__(self, game_name):
        self.game = game_name
        # load general presets
        pygameUtils.__init__(self)
        # load palette and colors
        self.PALETTE = self.PALETTES["CYBER_BLUE"]
        self.SHAPE_COLORS = (
            self.COLORS["BLACK"],
            self.COLORS["TETRIS_RED"],
            self.COLORS["TETRIS_GREEN"],
            self.COLORS["TETRIS_YELLOW"],
            self.COLORS["TETRIS_ORANGE"],
            self.COLORS["TETRIS_DARK_BLUE"],
            self.COLORS["TETRIS_LIGHT_BLUE"],
            self.COLORS["TETRIS_PURPLE"],
        )
        # setup surfaces and sub-surfaces
        shell.define_main_surfaces(self)
        # load images
        shell.load_generic_images(self)
        self.EMPTY_GRID_SQUARE = pygame.Surface((30, 30))
        self.EMPTY_GRID_SQUARE.fill(self.COLORS["BLACK"])
        self.EMPTY_PLAY_SQUARE = self.EMPTY_GRID_SQUARE.copy()
        self.EMPTY_PLAY_SQUARE.fill(self.COLORS["GRAY"])
        self.LOCKED_SQUARE = self.EMPTY_GRID_SQUARE.copy()
        self.LOCKED_SQUARE.fill(self.PALETTE[2])
        self.FALLING_SQUARE = self.EMPTY_GRID_SQUARE.copy()
        self.FALLING_SQUARE.fill(self.PALETTE[0])

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (self.height, self.width, self.game_level, self.show_next) = self.parameters
        # initial values
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.PIECES = (
            [[1, 1, 0], [0, 1, 1]],
            [[0, 2, 2], [2, 2, 0]],
            [[3, 3], [3, 3]],
            [[4, 4, 4], [4, 0, 0]],
            [[5, 5, 5], [0, 0, 5]],
            [[6, 6, 6, 6]],
            [[0, 7, 0], [7, 7, 7]],
        )
        self.falling_piece = False
        self.next_piece = choice(self.PIECES)
        self.score = 0

        self.difficulty = round(
            (100 * self.width / self.height) * (1 + self.game_level / 10), 2
        )
        self.x_margin = (self.PLAY_SURFACE.get_width() - self.width * 32) // 2
        self.y_margin = (self.PLAY_SURFACE.get_height() - self.height * 32) // 2

        # create main game button
        shell.main_game_button(self, "QUIT")
        # start timer
        self.time_start = dt.now()
        self.last_time = dt.now()

    def check_locked(self):
        for r in range(self.height):
            for s in range(self.width):
                if self.grid[r][s] > 0 and (
                    r + 1 == self.height or self.grid[r + 1][s] < 0
                ):
                    self.grid = [
                        [
                            -self.grid[y][x] if self.grid[y][x] > 0 else self.grid[y][x]
                            for x in range(self.width)
                        ]
                        for y in range(self.height)
                    ]
                    self.falling_piece = False
                    # scores highest if time to lock piece is shorter (anyhing less than 1 sec is capped at 1 sec)
                    self.score += 10 / max(
                        1, (dt.now() - self.falling_piece_timestamp).total_seconds()
                    )
                    return True

    def next_frame(self):
        # if no piece falling, generate new one
        if not self.falling_piece:
            self.falling_piece = copy(self.next_piece)
            self.next_piece = choice(self.PIECES)
            for r, row in enumerate(self.falling_piece):
                for s, q in enumerate(row):
                    self.grid[r][
                        s + (self.width - len(self.falling_piece[0])) // 2
                    ] += q
            self.falling_piece_timestamp = dt.now()
            return

        # check for line complete, erase it
        for r, row in enumerate(self.grid):
            if all([True if i < 0 else False for i in row]):
                self.grid.pop(r)
                self.grid.insert(0, [0 for i in range(self.width)])
                self.game_level += 0.5

        # regulate falling speed
        if dt.now() - self.last_time > td(seconds=1 / self.game_level):
            # lock pieces if necessary
            self.check_locked()
            # drop piece one line down
            self.move_piece(dy=1)
            self.last_time = dt.now()

    def move_piece(self, dx=0, dy=0):
        _grid = [
            [self.grid[y][x] if self.grid[y][x] < 0 else 0 for x in range(self.width)]
            for y in range(self.height)
        ]
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] > 0:
                    # check for out of bounds
                    if (x + dx < 0 or x + dx == self.width) or (y + dy == self.height):
                        return
                    # check if sqyare occupied
                    if self.grid[y + dy][x + dx] < 0:
                        return
                    # move sqUare
                    _grid[y + dy][x + dx] = self.grid[y][x]

        # if all validations ok...
        self.grid = copy(_grid)
        return True  # only for drop

    def rotate_piece(self):
        try:
            _grid = np.array(
                [
                    [
                        self.grid[y][x] if self.grid[y][x] < 0 else 0
                        for x in range(self.width)
                    ]
                    for y in range(self.height)
                ]
            )
            _p = [
                (x, y)
                for x in range(self.width)
                for y in range(self.height)
                if self.grid[y][x] > 0
            ]
            xs = [i[0] for i in _p]
            ys = [i[1] for i in _p]
            # control edge case
            if not xs or not ys:
                return
            # select matrix in grid that contains piece and rotate
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            matrix = np.rot90(
                np.array(
                    [
                        [self.grid[y][x] for x in range(x0, x1 + 1)]
                        for y in range(y0, y1 + 1)
                    ]
                )
            )
            _grid[y0 : y0 + (x1 - x0 + 1), x0 : x0 + (y1 - y0 + 1)] = matrix
            # if all validations ok...
            self.grid = copy(_grid)

        except:
            return

    def drop_piece(self):
        while True:
            self.move_piece(dy=1)
            if self.check_locked():
                return

    def update_display(self):
        # next movement
        self.next_frame()
        # play screen
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])
        for r, row in enumerate(self.grid):
            for s, sq in enumerate(row):
                square = self.EMPTY_GRID_SQUARE.copy()
                if sq != 0:
                    square.fill(self.SHAPE_COLORS[abs(sq)])
                self.MAIN_SURFACE.blit(
                    source=square, dest=(self.x_margin + 32 * s, self.y_margin + 32 * r)
                )
        # show next piece
        if self.show_next:
            for r, row in enumerate(self.next_piece):
                for s, sq in enumerate(row):
                    square = self.EMPTY_PLAY_SQUARE.copy()
                    if sq != 0:
                        square.fill(self.SHAPE_COLORS[abs(sq)])
                    self.MAIN_SURFACE.blit(
                        source=square,
                        dest=(
                            (self.PLAY_SURFACE.get_width() - len(row) * 32) // 2
                            + s * 32,
                            self.y_margin - 150 + 32 * r,
                        ),
                    )
        # update INFO surface
        _message = [
            ("Board Statistics", "", "NUN40B"),
            ("Width", f"< {self.width} >", "NUN40"),
            ("Height", f"< {self.height} >", "NUN40"),
            (
                "Difficulty",
                f"< {self.difficulty} >",
                "NUN40",
            ),
            ("",),
            ("Game Statistics", "", "NUN40B"),
            ("Level", f"< {self.game_level}>", "NUN40"),
            ("Play Time", f"< {str(dt.now() - self.time_start)[:-5]}>", "NUN40"),
            (
                "Score",
                f"< {self.score:.1f}>",
                "NUN40",
            ),
        ]
        shell.update_info_surface(GAME, _message)

        pygame.display.flip()

    def process_click(self, pos, button):
        # clicked on control button
        if shell.check_if_main_game_button_pressed(self, pos):
            return

    def process_key(self, key):
        if key == K_RIGHT:
            self.move_piece(dx=1)
        elif key == K_LEFT:
            self.move_piece(dx=-1)
        elif key == K_DOWN:
            self.move_piece(dy=1)
        elif key == K_UP:
            self.rotate_piece()
        elif key == K_SPACE:
            self.drop_piece()

    def check_end(self):
        _condition = any(
            [True if i < 0 else False for i in (self.grid[0] + self.grid[1])]
        )
        if not self.falling_piece and _condition:
            self.stage = 3
            self.end_criteria = "lost"

    def wrap_up(self):
        shell.wrap_up(self)

    def high_score(self):
        shell.update_high_scores(self)


if __name__ == "__main__":
    GAME = Game("tetris")
    shell.main(GAME)
    pygame.quit()
