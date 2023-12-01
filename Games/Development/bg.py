import random
import pygame
from pygame.locals import *
import sys, os

import time

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import menus

pygame.init()


class Game:
    def __init__(self):
        # load general presets
        pygameUtils.__init__(self)
        # define pallette
        self.COLOR1 = self.COLORS["CYBER_BLUE01"]
        self.COLOR2 = self.COLORS["CYBER_BLUE02"]
        self.COLOR3 = self.COLORS["CYBER_BLUE03"]
        self.COLOR4 = self.COLORS["CYBER_BLUE04"]
        self.COLOR5 = self.COLORS["CYBER_BLUE05"]
        # setup surfaces and sub-surfaces
        self.PLAY_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.6, self.DISPLAY_HEIGHT)
        )
        self.INFO_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.4, self.DISPLAY_HEIGHT * 0.5)
        )
        self.MSG_SURFACE = pygame.Surface(
            (self.INFO_SURFACE.get_width() * 0.8, self.INFO_SURFACE.get_height() * 0.4)
        )

    def setup(self):
        self.BOARD_SURFACE = pygame.Surface((1000, 800))
        self.board = [
            0,
            -2,
            0,
            0,
            0,
            0,
            5,
            0,
            3,
            0,
            0,
            0,
            -5,
            5,
            0,
            0,
            0,
            -3,
            0,
            -5,
            0,
            0,
            0,
            0,
            2,
            0,
        ]
        self.x0 = 400
        self.y0_lower = 1000
        self.y0_upper = 400
        self.pip_size = 30
        self.col_selected = -1
        self.turn = -1
        self.move_in_progress = [3, 2]
        self.captured = [0, 0]

    def process_click(self, pos, button):
        def get_column(pos):
            for k, p in enumerate(self.positions_upper):
                if p.collidepoint(pos):
                    return k + 13
            for k, p in enumerate(self.positions_lower):
                if p.collidepoint(pos):
                    return 12 - k
            return -1

        col = get_column(pos)
        # check if no column selected
        if col == -1:
            self.col_selected = -1
            return

        # click to select FROM pip
        if self.col_selected == -1:
            if self.captured[0 if self.turn == 1 else 1]:
                _valid_fr = 0
                _valid_to = 0
            else:
                _valid_fr = [
                    k
                    for k, _ in enumerate(self.board)
                    if signs(self.board[k], -self.turn)
                ]
            self.valid_to = []
            # add valid to positions according to valid from pip
            for _die in self.move_in_progress:
                target = col + (_die * self.turn)
                if 1 <= target <= 25 and not (self.board[target] * self.turn > 1):
                    self.valid_to.append(target)

            print("to:", self.valid_to)

        # check if selected column is active turn pip color
        if self.col_selected == -1 and col in _valid_fr:
            self.col_selected = col
        elif self.col_selected >= 0 and col in self.valid_to:
            self.process_move(fr=self.col_selected, to=col)
            self.col_selected = -1
        else:
            self.col_selected = -1

        # check if turn finished
        if not self.move_in_progress:
            self.turn *= -1
            self.throw_dice()

    def throw_dice(self):
        die1 = random.randrange(1, 7)
        die2 = random.randrange(1, 7)
        self.move_in_progress = [die1] * 4 if die1 == die2 else [die1, die2]

    def process_move(self, fr, to):
        sign = self.board[fr] // abs(self.board[fr])
        self.board[fr] -= 1 * sign
        if self.board[to] * self.turn == 1:
            self.captured[0 if self.turn == 1 else 1] += 1
            self.board[to] = sign
        else:
            self.board[to] += 1 * sign
        # take die from moves
        self.move_in_progress.remove((fr - to) * sign)

    def update_display(self):
        # TODO: more than 5 PIPs
        self.PLAY_SURFACE.fill((15, 15, 15))
        # draw board
        self.BOARD_SURFACE.fill(self.COLOR1)
        self.PLAY_SURFACE.blit(source=self.BOARD_SURFACE, dest=(300, 300))
        # draw board vertical lines
        for _x in [0, 6, 12, 13]:
            pygame.draw.line(
                self.PLAY_SURFACE,
                self.COLORS["BLACK"],
                (
                    self.x0 + _x * self.pip_size * 2.1 - self.pip_size,
                    self.y0_upper - self.pip_size,
                ),
                (
                    self.x0 + _x * self.pip_size * 2.1 - self.pip_size,
                    self.y0_lower + self.pip_size,
                ),
                width=4,
            )
        # draw board triangles
        self.positions_upper, self.positions_lower = [], []
        for x in range(12):
            _points = [
                (
                    self.x0 + x * self.pip_size * 2.1 - self.pip_size,
                    self.y0_upper - self.pip_size,
                ),
                (
                    self.x0 + (x + 0.5) * self.pip_size * 2.1 - self.pip_size,
                    self.y0_upper + (self.y0_lower - self.y0_upper) // 2,
                ),
                (
                    self.x0 + (x + 1) * self.pip_size * 2.1 - self.pip_size,
                    self.y0_upper - self.pip_size,
                ),
            ]
            self.positions_upper.append(
                pygame.draw.polygon(
                    self.PLAY_SURFACE,
                    color=self.COLOR4 if x % 2 else self.COLOR5,
                    points=_points,
                )
            )
            _points = [
                (
                    self.x0 + x * self.pip_size * 2.1 - self.pip_size,
                    self.y0_lower + self.pip_size,
                ),
                (
                    self.x0 + (x + 0.5) * self.pip_size * 2.1 - self.pip_size,
                    self.y0_lower - (self.y0_lower - self.y0_upper) // 2,
                ),
                (
                    self.x0 + (x + 1) * self.pip_size * 2.1 - self.pip_size,
                    self.y0_lower + self.pip_size,
                ),
            ]
            self.positions_lower.append(
                pygame.draw.polygon(
                    self.PLAY_SURFACE,
                    color=self.COLOR4 if not (x % 2) else self.COLOR5,
                    points=_points,
                )
            )

        # draw in-play pips
        for x, pos in enumerate(self.board[12::-1] + self.board[13:]):
            for y in range(abs(pos)):
                if pos:
                    _center = (
                        self.x0 + (x % 13) * self.pip_size * 2.1 + 2,
                        (
                            self.y0_lower - y * self.pip_size * 2.03
                            if x < 13
                            else self.y0_upper + y * self.pip_size * 2.03
                        ),
                    )
                    if self.col_selected == x and y == abs(pos) - 1:
                        _color = (
                            self.COLORS["GREEN"] if pos < 0 else self.COLORS["YELLOW"]
                        )
                    else:
                        _color = (
                            self.COLORS["WHITE"] if pos < 0 else self.COLORS["MAROON"]
                        )
                    pygame.draw.circle(
                        self.PLAY_SURFACE,
                        color=_color,
                        center=_center,
                        radius=self.pip_size,
                    )
                    pygame.draw.circle(
                        self.PLAY_SURFACE,
                        color=self.COLORS["BLACK"],
                        center=_center,
                        radius=self.pip_size,
                        width=2,
                    )
        # draw captured pips
        for pip_count in range(sum(self.captured)):
            _center = (
                (self.PLAY_SURFACE.get_width() - (self.pip_size + 50) * pip_count) // 2,
                (self.y0_lower + self.y0_upper) // 2,
            )
            _color = (
                self.COLORS["MAROON"]
                if pip_count < self.captured[0]
                else self.COLORS["WHITE"]
            )
            pygame.draw.circle(
                self.PLAY_SURFACE,
                color=_color,
                center=_center,
                radius=self.pip_size,
            )
            pygame.draw.circle(
                self.PLAY_SURFACE,
                color=self.COLORS["BLACK"],
                center=_center,
                radius=self.pip_size,
                width=2,
            )
        self.MAIN_SURFACE.blit(source=self.PLAY_SURFACE, dest=(0, 0))

        text = self.FONTS["ROB20"].render(
            "   ".join([str(i) for i in self.move_in_progress]),
            True,
            self.COLORS["BLACK"],
            self.COLORS["GRAY"],
        )

        self.INFO_SURFACE.fill((self.COLORS["YELLOW"]))
        self.INFO_SURFACE.blit(text, dest=(100, 100))
        self.MAIN_SURFACE.blit(
            source=self.INFO_SURFACE, dest=(self.MAIN_SURFACE.get_width() * 0.6, 20)
        )
        pygame.display.flip()

    def check_win(self):
        pass

    def wrap_up(self):
        pass


def signs(a, b):
    if a and b:
        return True if a // abs(a) == b // abs(b) else False
    else:
        return False


def main():
    global GAME
    GAME = Game()
    GAME.stage = 1  # change to 0
    # main_menu = menus.boom(GAME)
    while True:  # main_menu.is_enabled():
        match GAME.stage:
            case 0:
                main_menu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            case 1:
                GAME.setup()
                GAME.stage = 2
            case 2:
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
                    GAME.update_display()
                    GAME.check_win()
            case 3:
                GAME.wrap_up()
                quit()
                GAME.stage = 0


if __name__ == "__main__":
    main()
