import random
import pygame
from pygame.locals import *
import sys, os
from datetime import datetime as dt

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
        # define pallette
        self.PALETTE = self.PALETTES["CYBER_BLUE"]
        self.COLOR_LIST = [
            self.COLORS["RED"],
            self.COLORS["GREEN"],
            self.COLORS["BLUE"],
            self.COLORS["YELLOW"],
            self.COLORS["ORANGE"],
            self.COLORS["PINK"],
            self.COLORS["GRAY"],
            self.COLORS["WHITE"],
        ]
        # setup surfaces and sub-surfaces
        shell.define_main_surfaces(self)
        # load images
        shell.load_generic_images(self)

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (
            self.colors,
            self.tokens,
            self.attempts,
        ) = self.parameters
        self.TOKEN_SIZE = 20

        self.active_colors = self.COLOR_LIST[self.colors]
        self.submit = False
        self.PLAYx, self.PLAYy = (200, 200)

        self.objective = [random.randrange(0, self.colors) for _ in range(self.tokens)]
        self.guess = [0 for _ in self.objective]
        self.guess_rect = []
        self.active_attempts = [[0, 0, 0, 0]]

        self.difficulty = 0  # place holder

        # create main game button
        shell.main_game_button(self, "QUIT")
        # start timer
        self.time_start = dt.now()

    def update_display(self):
        self.submit = False
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])

        # draw board
        for _y, guess in enumerate(self.active_attempts):
            # draw guess tokens
            self.guess_rect = []
            for x, token in enumerate(guess):
                _center = (
                    x * self.TOKEN_SIZE * 2.1 + 100 + self.PLAYx,
                    200 + self.PLAYy + 40 * _y,
                )
                _color = self.COLOR_LIST[token]
                self.guess_rect.append(
                    pygame.draw.circle(
                        self.MAIN_SURFACE,
                        color=_color,
                        center=_center,
                        radius=self.TOKEN_SIZE,
                    )
                )
                pygame.draw.circle(
                    self.MAIN_SURFACE,
                    color=self.COLORS["BLACK"],
                    center=_center,
                    radius=self.TOKEN_SIZE,
                    width=1,
                )

            # draw result tokens / submit button
            _result = self.get_result_color(guess)

            if _y < len(self.active_attempts) - 1:
                for pos, _color in enumerate(_result):
                    _center = (
                        pos * self.TOKEN_SIZE // 2 * 2.1 + 400 + self.PLAYx,
                        200 + self.PLAYy + 40 * _y,
                    )
                    pygame.draw.circle(
                        self.MAIN_SURFACE,
                        color=_color,
                        center=_center,
                        radius=self.TOKEN_SIZE // 2,
                    )
                    pygame.draw.circle(
                        self.MAIN_SURFACE,
                        color=self.COLORS["BLACK"],
                        center=_center,
                        radius=self.TOKEN_SIZE // 2,
                        width=1,
                    )
            else:
                self.button_submit = pygame.draw.rect(
                    self.MAIN_SURFACE,
                    self.COLORS["WHITE"],
                    (400 + self.PLAYx, 180 + _y * 50 + self.PLAYy, 100, 40),
                )

        # update INFO surface
        _message = [
            ("Board Statistics", "", "NUN40B"),
            ("Colors", f"< {GAME.colors} >", "NUN40"),
            ("Tokens", f"< {GAME.tokens} >", "NUN40"),
            ("Attempts", f"< {GAME.attempts} >", "NUN40"),
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

    def get_result_color(self, guess):
        _guess, _test, result = [], [], []
        # test for correct color and position
        for i, j in zip(guess, self.objective):
            if i == j:
                result.append(self.COLORS["BLACK"])
            else:
                _guess.append(i)
                _test.append(j)
        # test for correct color, wrong position
        while _guess and _test:
            if _guess[0] in _test:
                result.append(self.COLORS["WHITE"])
                _test.remove(_guess[0])
            _guess.pop(0)
        # add necessary blank circles
        result += [self.COLORS["GRAY"]] * (self.tokens - len(result))
        return result

    def process_click(self, pos, button):
        # clicked on control button
        if shell.check_if_main_game_button_pressed(self, pos):
            return
        _pos = (pos[0] - self.PLAYx, pos[1] - self.PLAYy)
        # click on "submit"
        if self.button_submit.collidepoint(pos):
            self.active_attempts.append(self.active_attempts[-1].copy())
            self.submit = True
        # click on token to change color
        for k, _rect in enumerate(self.guess_rect):
            if _rect.collidepoint(pos):
                self.active_attempts[-1][k] = (
                    self.active_attempts[-1][k] + 1
                ) % self.colors

    def check_end(self):
        if self.submit and self.active_attempts[-1] == self.objective:
            GAME.stage = 3

    def wrap_up(self):
        # kept as function in case extra code needs to be inserted
        shell.wrap_up(GAME)


if __name__ == "__main__":
    GAME = Game("mastermind")
    shell.main(GAME)
    pygame.quit()
