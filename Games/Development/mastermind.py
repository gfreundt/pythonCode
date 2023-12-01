import random
import pygame
from pygame.locals import *
import sys, os
from copy import deepcopy as copy

import time

# import win32gui

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import menus

pygame.init()

"""
def windowEnumerationHandler(hwnd, windows):
    windows.append((hwnd, win32gui.GetWindowText(hwnd)))


windows = []
win32gui.EnumWindows(windowEnumerationHandler, windows)

print(windows)

time.sleep(4)
g = [i[0] for i in windows if i[1] == "Zam"][0]
win32gui.SetForegroundWindow(g)
time.sleep(4)
quit()"""


class Game:
    def __init__(self):
        # load general presets
        pygameUtils.__init__(self)
        # define pallette
        self.COLOR_LIST = [
            self.COLORS["BLACK"],
            self.COLORS["YELLOW"],
            self.COLORS["GREEN"],
            self.COLORS["BLUE"],
            self.COLORS["RED"],
            self.COLORS["GRAY"],
            self.COLORS["GRAY"],
        ]
        # setup surfaces and sub-surfaces
        pygame.display.set_caption("Mastermind")
        self.PLAY_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.6, self.DISPLAY_HEIGHT)
        )
        self.INFO_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.4, self.DISPLAY_HEIGHT * 0.5)
        )
        self.MSG_SURFACE = pygame.Surface(
            (self.INFO_SURFACE.get_width() * 0.8, self.INFO_SURFACE.get_height() * 0.4)
        )
        self.PLAYx, self.PLAYy = (200, 200)

    def setup(self):
        self.TOKEN_SIZE = 20

        self.colors = 6
        self.active_colors = self.COLOR_LIST[self.colors]
        self.tokens = 4
        self.attempts = 10
        self.submit = False

        self.objective = [random.randrange(0, self.colors) for _ in range(self.tokens)]
        # self.objective = [3, 2, 1, 0]
        self.guess = [0 for _ in self.objective]
        self.guess_rect = []
        self.active_attempts = [[0, 0, 0, 0]]

    def update_display(self):
        self.submit = False
        self.PLAY_SURFACE.fill(self.COLORS["GRAY"])

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
                        self.PLAY_SURFACE,
                        color=_color,
                        center=_center,
                        radius=self.TOKEN_SIZE,
                    )
                )
                pygame.draw.circle(
                    self.PLAY_SURFACE,
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
                        self.PLAY_SURFACE,
                        color=_color,
                        center=_center,
                        radius=self.TOKEN_SIZE // 2,
                    )
                    pygame.draw.circle(
                        self.PLAY_SURFACE,
                        color=self.COLORS["BLACK"],
                        center=_center,
                        radius=self.TOKEN_SIZE // 2,
                        width=1,
                    )
            else:
                self.button_submit = pygame.draw.rect(
                    self.PLAY_SURFACE,
                    self.COLORS["WHITE"],
                    (400 + self.PLAYx, 180 + _y * 50 + self.PLAYy, 100, 40),
                )

        self.MAIN_SURFACE.blit(source=self.PLAY_SURFACE, dest=(self.PLAYx, self.PLAYy))

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
        result += [self.COLORS["LIGHT_BLUE"]] * (self.tokens - len(result))
        return result

    def process_click(self, pos, button):
        _pos = (pos[0] - self.PLAYx, pos[1] - self.PLAYy)
        # click on "submit"
        if self.button_submit.collidepoint(_pos):
            self.active_attempts.append(self.active_attempts[-1].copy())
            self.submit = True
        # click on token to change color
        for k, _rect in enumerate(self.guess_rect):
            if _rect.collidepoint(_pos):
                self.active_attempts[-1][k] = (
                    self.active_attempts[-1][k] + 1
                ) % self.colors

    def check_win(self):
        if self.submit and self.active_attempts[-1] == self.objective:
            GAME.stage = 3
        return

    def wrap_up(self):
        time.sleep(2)
        pygame.quit()


def main():
    global GAME
    GAME = Game()
    GAME.stage = 1  # change to 0
    # main_menu = menus.mastermind(GAME)
    while True:  # main_menu.is_enabled():
        match GAME.stage:
            case 0:
                main_menu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            case 1:
                GAME.setup()
                GAME.stage = 2
            case 2:
                GAME.update_display()
                events = pygame.event.get()
                for event in events:
                    if event.type == QUIT or (
                        event.type == KEYDOWN and event.key == 27
                    ):
                        GAME.stage = 3
                    elif event.type == MOUSEBUTTONDOWN:
                        GAME.process_click(
                            pos=pygame.mouse.get_pos(), button=event.button
                        )

                    GAME.check_win()
            case 3:
                GAME.wrap_up()
                return
                # GAME.stage = 0


if __name__ == "__main__":
    main()
