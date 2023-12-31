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
        self.head_pos = self.width // 2, self.height // 2
        self.score = 0
        self.MOVES = [(0,1), (1,0), (0,-1), (-1,0)]

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

    def rotate_head(self):
        rot = 
        self.move_per_frame = 

    def process_click(self, pos, button):
        # clicked on control button
        if shell.check_if_main_game_button_pressed(self, pos):
            return

    def process_key(self, key):
        if key == K_RIGHT:
            self.rotate_head(1)
        elif key == K_LEFT:
            self.rotate_head(-1)

    def check_end(self):
        _condition = any(
            [True if i < 0 else False for i in (self.grid[0] + self.grid[1])]
        )
        if not self.falling_piece and _condition:
            self.stage = 3
            self.end_criteria = "lost"

    def wrap_up(self):
        shell.wrap_up(GAME)


if __name__ == "__main__":
    GAME = Game("viper")
    shell.main(GAME)
    pygame.quit()
