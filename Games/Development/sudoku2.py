import sys, os, time
from datetime import datetime as dt
from random import randrange, choice, shuffle, sample
from copy import deepcopy as copy

from tqdm import tqdm

# import pygame
# from pygame.locals import *

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import game_shell as shell

# pygame.init()


class Game:
    def __init__(self, game_name) -> None:
        return
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
        # change: (self.STONES_PER_PIT, self.END_GAME_EARLY) = self.parameters
        # initial values
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.all = []
        with open("sudoku.txt", "r") as file:
            p = []
            for _ in range(500):
                g = file.readline().strip()
                if "Grid" not in g:
                    p.append([int(k) for k in g])
                else:
                    self.all.append(p)
                    p = []
        return
        # create main game button
        shell.main_game_button(self, "QUIT")
        # inital time
        self.time_start = dt.now()

    def update_display(self):
        # update play screen
        self.MAIN_SURFACE.fill(self.COLORS["BLACK"])
        # update active player tag
        _text = self.FONTS["ROB80"].render(
            f" Player {self.turn} turn ",
            True,
            self.COLORS["BLACK"],
            self.COLORS["GREEN"],
        )
        self.MAIN_SURFACE.blit(
            source=_text, dest=(500, 200 if self.turn == 2 else 1000)
        )
        # update pits and homes
        for x, pit in enumerate(self.board):
            _text = self.FONTS["ROB80"].render(
                "" if pit == "0" else f"{pit:02d}",
                True,
                self.COLORS["WHITE"],
                self.COLORS["BLACK"],
            )
            if x < 6:
                _dest = (1200 - 200 * x, 800)
            elif x == 6:
                _dest = (100, 600)
            elif x < 13:
                _dest = (200 * x - 1200, 400)
            elif x == 13:
                _dest = (1350, 600)
            self.click_areas[x] = self.MAIN_SURFACE.blit(source=_text, dest=_dest)
            pygame.draw.rect(
                self.MAIN_SURFACE,
                self.COLORS["RED"] if x == self.pos else self.COLORS["WHITE"],
                self.click_areas[x],
                1,
            )

        # update INFO surface
        _message = [
            ("Board Statistics", "", "NUN40B"),
            ("Total Stones", f"< {sum(self.board)} >", "NUN40"),
            (
                "Available Stones",
                f"< {sum(self.board)-(self.board[6]+self.board[13])} >",
                "NUN40",
            ),
            ("",),
            ("Play Time", f"< {str(dt.now() - self.time_start)[:-5]}>", "NUN40"),
            (
                "Score",
                f"< {self.board[6]}>",
                "NUN40",
            ),
        ]
        shell.update_info_surface(GAME, _message)
        pygame.display.flip()

    def process_click(self, pos, button):
        # clicked on quit button
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
        pass

    def wrap_up(self):
        shell.wrap_up(GAME)

    def generator(self, filled):
        # create fixed list of 1-9
        line = [i for i in range(1, 10)]
        # loop until valid grid is generated
        while True:
            # create empty grid
            self.grid = [[0 for _ in range(9)] for _ in range(9)]
            # variable to exit infinite loop if no viable solution found
            start = time.time()
            # fix first row with randomized numbers
            shuffle(line)
            self.grid[0] = copy(line)
            # populate rows 2-8 with random lines of 1-9 that are valid
            i = 1
            while i <= 7 and time.time() - start < 10:
                shuffle(line)
                self.grid[i] = copy(line)
                if self.valid_grid():
                    i += 1
            # if row 8 not populated, exited loop because of time limit, need to restart
            if i != 8:
                continue
            # calculate last row based on only digits left
            for i in range(9):
                for j in range(1, 10):
                    self.grid[8][i] = j
                    if self.valid_grid():
                        break
            # last check for valid grid, restart if not
            if self.valid_grid():
                break
        # remove blanks % of positions in grid
        for blank in sample(range(0, 81), int(81 * (1 - filled))):
            self.grid[blank // 9][blank % 9] = 0

    def valid_grid(self, test=None):
        test_grid = copy(self.grid)
        if test:
            test_grid[test["row"]][test["col"]] = test["digit"]
        # check horizontal
        for row in test_grid:
            for i in range(1, 10):
                if row.count(i) > 1:
                    return False
        # check vertical
        for col in range(9):
            row = [test_grid[i][col] for i in range(9)]
            for k in range(1, 10):
                if row.count(k) > 1:
                    return False
        # check block
        for row in (0, 3, 6):
            for col in (0, 3, 6):
                block = [
                    test_grid[i][j]
                    for i in range(row, row + 3)
                    for j in range(col, col + 3)
                ]
                for k in range(1, 10):
                    if block.count(k) > 1:
                        return False
        # grid valid
        return True

    def show_grid(self):
        for row in range(9):
            for col in range(9):
                _digit_txt = (
                    str(self.grid[row][col]) if self.grid[row][col] > 0 else " "
                )
                _text = GAME.FONTS["NUN40"].render(
                    _digit_txt, True, GAME.COLORS["WHITE"], GAME.COLORS["BLACK"]
                )
                GAME.MAIN_SURFACE.blit(
                    source=_text,
                    dest=(
                        100 + 50 * (col),
                        100 + 50 * (row),
                    ),
                )
            # draw horizontal grid lines
            pygame.draw.line(
                surface=GAME.MAIN_SURFACE,
                color=GAME.COLORS["WHITE"],
                start_pos=(100, 50 * row + 95),
                end_pos=(500, 50 * row + 95),
            )
            # draw vertical grid lines
            pygame.draw.line(
                surface=GAME.MAIN_SURFACE,
                color=GAME.COLORS["WHITE"],
                start_pos=(50 * row + 100, 50),
                end_pos=(50 * row + 100, 600),
            )
        pygame.draw.line(
            surface=GAME.MAIN_SURFACE,
            color=GAME.COLORS["WHITE"],
            start_pos=(95, 50 * (row + 1) + 95),
            end_pos=(535, 50 * (row + 1) + 95),
        )
        pygame.display.flip()
        time.sleep(10)

    def solve(self):
        find = self.find_empty()
        if not find:
            return True
        row, col = find
        for num in range(1, 10):
            if self.valid_grid({"row": row, "col": col, "digit": num}):
                self.grid[row][col] = num
                if self.solve():
                    return True
                self.grid[row][col] = 0
        return False

    def find_empty(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid)):
                if self.grid[i][j] == 0:
                    return i, j
        return None


def flat_grid(grid):
    return "".join(["".join([str(i) for i in j]) for j in grid])


if __name__ == "__main__":

    GAME = Game("sudoku")
    GAME.setup()
    with open("")
    GAME.solve()
    print(flat_grid(GAME.grid))
    quit()
    
    shell.main(GAME)
    pygame.quit()
