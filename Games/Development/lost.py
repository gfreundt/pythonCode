import pygame
from pygame.locals import *
from random import randint, choice
import sys, os
from datetime import datetime as dt
import time

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

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (
            self.width,
            self.height,
            self.unit_size,
        ) = self.parameters

        # initial values
        self.reveal = False
        self.difficulty = 0  # placeholder
        self.x_margin = (
            self.PLAY_SURFACE.get_width() - self.width * self.unit_size
        ) // 2
        self.y_margin = (
            self.PLAY_SURFACE.get_height() - self.height * self.unit_size
        ) // 2

        # create main game button
        shell.main_game_button(self, "QUIT")
        # start timer
        self.time_start = dt.now()

        # initiate grid of correct dimensions with all blanks
        self.grid = [
            [[0, 0, 0, 0] for _ in range(self.width)] for _ in range(self.height)
        ]
        # create random units along maze top and left edges
        for k in range(self.width):
            self.grid[0][k] = self.unit_generator()
            # close top border
            self.grid[0][k][0] = 1
        for k in range(self.height):
            self.grid[k][0] = self.unit_generator()
        for y in range(1, self.height):
            for x in range(1, self.width):
                invalid = True
                while invalid:
                    _unit = self.unit_generator()
                    if (
                        _unit[0] == self.grid[y - 1][x][2]
                        and _unit[3] == self.grid[y][x - 1][1]
                    ):
                        invalid = False
                self.grid[y][x] = _unit

        # close left, right borders
        for row in self.grid:
            row[0][3] = 1
            row[-1][1] = 1
        # close bottom border
        for unit in self.grid[-1]:
            unit[2] = 1

        # tunneler
        x = randint(2, self.width - 1)
        y = 0
        self.route = [(x, y)]
        # open entrance
        self.grid[y][x][0] = 0

        turns = 0
        while True:
            # random direction and distance
            d = choice(["down", "right", "up", "left"])
            # check edges
            if (
                (d == "up" and y == 0)
                or (d == "right" and x == self.width - 1)
                or (d == "left" and x == 0)
            ):
                continue
            elif y == self.height - 1:
                # open exit
                self.grid[y][x][2] = 0
                return

            match d:
                case "up":
                    _p, _q = 0, 2
                    _newx, _newy = (x, y - 1)
                case "down":
                    _p, _q = 2, 0
                    _newx, _newy = (int(x), int(y + 1))
                case "left":
                    _p, _q = 3, 1
                    _newx, _newy = (x - 1, y)
                case "right":
                    _p, _q = 1, 3
                    _newx, _newy = (int(x + 1), int(y))

            if (_newx, _newy) in self.route:
                turns += 1
                if turns > 4:
                    x, y = self.route.pop()
                continue

            self.grid[y][x][_p] = 0
            x, y = int(_newx), int(_newy)
            self.grid[y][x][_q] = 0
            self.route.append((x, y))

    def unit_generator(self):
        while True:
            _unit = [
                randint(0, 1),
                randint(0, 1),
                randint(0, 1),
                randint(0, 1),
            ]
            # return _unit

            if _unit == [0, 0, 0, 0] or _unit == [1, 1, 1, 1]:
                continue
            else:
                return _unit

    def update_display(self):
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])
        for y, row in enumerate(self.grid):
            for x, col in enumerate(row):
                for e, edge in enumerate(col):
                    if edge:
                        match e:
                            case 0:
                                start_pos = (
                                    self.x_margin + x * self.unit_size,
                                    self.y_margin + y * self.unit_size,
                                )
                                end_pos = (
                                    self.x_margin + (x + 1) * self.unit_size,
                                    self.y_margin + y * self.unit_size,
                                )
                            case 1:
                                start_pos = (
                                    self.x_margin + (x + 1) * self.unit_size,
                                    self.y_margin + y * self.unit_size,
                                )
                                end_pos = (
                                    self.x_margin + (x + 1) * self.unit_size,
                                    self.y_margin + (y + 1) * self.unit_size,
                                )
                            case 2:
                                start_pos = (
                                    self.x_margin + (x + 1) * self.unit_size,
                                    self.y_margin + (y + 1) * self.unit_size,
                                )
                                end_pos = (
                                    self.x_margin + x * self.unit_size,
                                    self.y_margin + (y + 1) * self.unit_size,
                                )
                            case 3:
                                start_pos = (
                                    self.x_margin + x * self.unit_size,
                                    self.y_margin + (y + 1) * self.unit_size,
                                )
                                end_pos = (
                                    self.x_margin + x * self.unit_size,
                                    self.y_margin + y * self.unit_size,
                                )

                        pygame.draw.line(
                            surface=self.MAIN_SURFACE,
                            color=self.COLORS["BLACK"],
                            start_pos=start_pos,
                            end_pos=end_pos,
                        )
        if self.reveal:
            for x, y in self.route:
                pygame.draw.circle(
                    self.MAIN_SURFACE,
                    color=self.COLORS["RED"],
                    center=(
                        self.x_margin + x * self.unit_size + self.unit_size // 2,
                        self.y_margin + y * self.unit_size + self.unit_size // 2,
                    ),
                    radius=self.unit_size // 4,
                )

        # update INFO surface
        _message = [
            ("Board Statistics", "", "NUN40B"),
            ("Width", f"< {GAME.width} >", "NUN40"),
            ("Size", f"< {GAME.unit_size} >", "NUN40"),
            ("Height", f"< {GAME.height} >", "NUN40"),
            (
                "Difficulty",
                f"< {GAME.difficulty} >",
                "NUN40",
            ),
            ("",),
            ("Game Statistics", "", "NUN40B"),
            ("Play Time", f"< {str(dt.now() - GAME.time_start)[:-5]}>", "NUN40"),
            (
                "Score",
                f"< {GAME.difficulty:.1f}>",
                "NUN40",
            ),
        ]
        shell.update_info_surface(GAME, _message)
        pygame.display.flip()

    def process_click(self, pos, button):
        # clicked on control button
        if shell.check_if_main_game_button_pressed(self, pos):
            return

        # TODO: gameplay

    def check_end(self):
        return
        # not won
        for bottle in self.collection:
            if bottle.count(bottle[0]) < self.bottle_size:
                return
        # winner
        GAME.end_criteria = 1
        GAME.stage = 3

    def wrap_up(self):
        # kept as function in case extra code needs to be inserted
        shell.wrap_up(GAME)


if __name__ == "__main__":
    GAME = Game("lost")
    shell.main(GAME)
    pygame.quit()
