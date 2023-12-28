import random
import pygame
from pygame.locals import *
from copy import deepcopy
import sys, os
from datetime import datetime as dt

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import menus2 as menus

pygame.init()


class Game:
    def __init__(self):
        # load general presets
        pygameUtils.__init__(self)
        # define palette
        self.PALETTE = self.PALETTES["CYBER_BLUE"]
        # setup surfaces and sub-surfaces
        self.PLAY_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.6, self.DISPLAY_HEIGHT)
        )
        self.INFO_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.4, self.DISPLAY_HEIGHT)
        )
        self.MSG_SURFACE = pygame.Surface(
            (
                self.INFO_SURFACE.get_width() * 0.8,
                self.INFO_SURFACE.get_height() * 0.265,
            )
        )
        # create all possible types of squares
        self.COVERED_SQUARE = pygame.Surface((30, 30))
        self.COVERED_SQUARE.fill(self.PALETTE[2])
        self.UNCOVERED_SQUARE = self.COVERED_SQUARE.copy()
        self.UNCOVERED_SQUARE.fill(self.PALETTE[0])
        self.FLAGGED_SQUARE = self.COVERED_SQUARE.copy()
        self.FLAGGED_SQUARE.fill(self.COLORS["MAROON"])
        self.BOMB2_SQUARE = self.COVERED_SQUARE.copy()
        self.BOMB2_SQUARE.fill(self.COLORS["DARK_MAROON"])
        self.BOMB1_SQUARE = self.FLAGGED_SQUARE.copy()
        pygame.draw.line(
            self.BOMB1_SQUARE, self.COLORS["GRAY"], (0, 0), (30, 30), width=3
        )
        pygame.draw.line(
            self.BOMB1_SQUARE, self.COLORS["GRAY"], (30, 0), (0, 30), width=3
        )
        self.BUTT1_POS = (2000, 1100)
        # load images
        self.end_images = [
            pygame.image.load("game_lost.png"),
            pygame.image.load("game_won.png"),
            pygame.image.load("game_quit.png"),
        ]

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (
            GAME.grid_x,
            GAME.grid_y,
            GAME.bomb_density,
            GAME.uncover_one_at_start,
        ) = GAME.parameters
        self.reveal = False
        self.x0 = (self.PLAY_SURFACE.get_width() - 32 * self.grid_x) // 2
        self.y0 = (self.PLAY_SURFACE.get_height() - 32 * self.grid_y) // 2
        self.total_bombs = int(self.grid_x * self.grid_y * self.bomb_density / 100)
        flat = [False] * (self.grid_x * self.grid_y - self.total_bombs) + [
            True
        ] * self.total_bombs
        random.shuffle(flat)
        self.minefield_bombs = [
            flat[i : i + self.grid_x]
            for i in range(0, (self.grid_x * self.grid_y), self.grid_x)
        ]
        self.minefield_numbers = [
            [self.calculate_number(row, i) for i in range(self.grid_x)]
            for row in range(self.grid_y)
        ]
        self.minefield_uncovered = [[False] * self.grid_x for _ in range(self.grid_y)]
        self.minefield_marked = deepcopy(self.minefield_uncovered)
        # auto-uncover first square if option selected and then neighbors
        if self.uncover_one_at_start:
            while True:
                i, row = random.randint(0, self.grid_x - 1), random.randint(
                    0, self.grid_y - 1
                )
                if (
                    self.minefield_numbers[row][i] == 0
                    and not self.minefield_bombs[row][i]
                ):
                    self.minefield_uncovered[row][i] = True
                    self.uncover_blank_neighbors()
                    break
        # calculate game difficulty level
        self.difficulty = (
            self.grid_x
            * self.grid_y
            * self.bomb_density
            / 100
            * (1 if self.uncover_one_at_start else 1.01)
        )
        # create main game button
        self.main_game_button("QUIT")
        # start timer
        self.time_start = dt.now()

    def main_game_button(self, button_text):
        _text = self.FONTS["NUN40B"].render(button_text, True, self.COLORS["WHITE"])
        _sfc = pygame.Surface((_text.get_width() * 1.25, 80))
        _sfc.fill(self.PALETTE[4])
        _sfc.blit(
            source=_text, dest=_text.get_rect(center=(_text.get_width() * 0.625, 40))
        )
        _pos = (
            self.PLAY_SURFACE.get_width()
            + (self.INFO_SURFACE.get_width() - _sfc.get_width()) // 2,
            1150,
        )
        self.main_button = (_sfc, _pos)

    def calculate_number(self, y, x):
        bomb_count = 0
        for row in range(max(0, y - 1), min(self.grid_y - 1, y + 1) + 1):
            for i in range(max(0, x - 1), min(self.grid_x - 1, x + 1) + 1):
                if self.minefield_bombs[row][i] and not (i == x and row == y):
                    bomb_count += 1
        return bomb_count

    def update_display(self):
        # update PLAY surface
        self.PLAY_SURFACE.fill((15, 15, 15))
        for row in range(self.grid_y):
            for i in range(self.grid_x):
                _t = ""
                if self.minefield_uncovered[row][i] or self.reveal:
                    square = self.UNCOVERED_SQUARE.copy()
                    if self.minefield_numbers[row][i] > 0:
                        _t = str(self.minefield_numbers[row][i])
                    text = self.FONTS["NUN24"].render(
                        _t, True, self.COLORS["BLACK"], self.PALETTE[0]
                    )
                    square.blit(source=text, dest=text.get_rect(center=(15, 15)))
                else:
                    if self.minefield_marked[row][i]:
                        square = self.FLAGGED_SQUARE.copy()
                    else:
                        square = self.COVERED_SQUARE.copy()

                if self.reveal:
                    if (
                        self.minefield_bombs[row][i] and self.minefield_marked[row][i]
                    ):  # square flagged correctly
                        square = self.FLAGGED_SQUARE.copy()
                    elif (
                        not self.minefield_bombs[row][i]
                        and self.minefield_marked[row][i]
                    ):  # square flagged incorrectly
                        square = self.BOMB1_SQUARE.copy()
                    elif (
                        self.minefield_bombs[row][i]
                        and not self.minefield_marked[row][i]
                    ):  # square not flagged
                        square = self.BOMB2_SQUARE.copy()

                self.PLAY_SURFACE.blit(
                    source=square, dest=(self.x0 + 32 * i, self.y0 + 32 * row)
                )
        self.MAIN_SURFACE.blit(source=self.PLAY_SURFACE, dest=(0, 0))

        # update INFO surface
        self.INFO_SURFACE.fill(self.PALETTE[2])
        self.messages = [
            ("Board Statistics", "", "NUN40B"),
            ("Squares", f"< {self.grid_x * self.grid_y:,} >", "NUN40"),
            ("Bombs", f"< {self.total_bombs} >", "NUN40"),
            (
                "Difficulty",
                f"< {self.difficulty} >",
                "NUN40",
            ),
            ("",),
            ("Game Statistics", "", "NUN40B"),
            ("Play Time", f"< {str(dt.now() - self.time_start)[:-5]}>", "NUN40"),
            (
                "Unmarked Bombs",
                f"< {self.total_bombs-len([i for row in self.minefield_marked for i in row if i])} >",
                "NUN40",
            ),
            (
                "Score",
                f"< {len([i for row in self.minefield_uncovered for i in row if i])/(self.grid_x*self.grid_y)*self.difficulty:.1f}>",
                "NUN40",
            ),
        ]
        # print crafted text
        self.MSG_SURFACE.fill(self.COLORS["BLACK"])  # self.PALETTE[2])
        for row, line in enumerate(self.messages):
            if not line[0]:
                line = ("", "", "NUN40")
            self.MSG_SURFACE.blit(
                self.FONTS[line[2]].render(
                    line[0],
                    True,
                    self.COLORS["WHITE"],
                    self.INFO_SURFACE.get_colorkey(),
                ),
                dest=(60, row * 40),
            )
            self.MSG_SURFACE.blit(
                self.FONTS[line[2]].render(
                    line[1],
                    True,
                    self.COLORS["WHITE"],
                    self.INFO_SURFACE.get_colorkey(),
                ),
                dest=(400, row * 40),
            )

        self.INFO_SURFACE.blit(
            source=self.MSG_SURFACE, dest=(self.INFO_SURFACE.get_width() * 0.1, 90)
        )
        # exit image
        if self.stage == 3:
            self.INFO_SURFACE.blit(
                source=self.end_images[self.end_criteria], dest=(240, 560)
            )
        self.MAIN_SURFACE.blit(
            source=self.INFO_SURFACE, dest=(self.DISPLAY_WIDTH * 0.6, 0)
        )
        # main game button
        self.MAIN_SURFACE.blit(source=self.main_button[0], dest=self.main_button[1])

        pygame.display.flip()

    def check_end(self):
        _uncovered = len([i for row in self.minefield_uncovered for i in row if not i])
        _marked = len([i for row in self.minefield_marked for i in row if i])
        if _uncovered == self.total_bombs and _uncovered == _marked:
            GAME.end_criteria = 1  # win game
            GAME.stage = 3

    def process_click(self, pos, button):
        # clicked on game square
        if pygame.Rect(self.PLAY_SURFACE.get_rect()).collidepoint(
            pygame.mouse.get_pos()
        ):
            x0, y0 = pos[0] - self.x0, pos[1] - self.y0
            i, row = x0 // 32, y0 // 32

            # check if click in separation between squares
            if x0 % 32 > 30 or y0 % 32 > 30:
                return
            # check if click outside of square
            if i < 0 or i >= self.grid_x or row < 0 or row >= self.grid_y:
                return
            # check if square already uncovered
            if self.minefield_uncovered[row][i]:
                return

            # left-click: open square if not marked
            if button == 1 and not GAME.minefield_marked[row][i]:
                # check if mine there
                if GAME.minefield_bombs[row][i]:
                    GAME.end_criteria = 0  # lose game
                    GAME.stage = 3
                else:
                    GAME.minefield_uncovered[row][i] = True
                    self.uncover_blank_neighbors()

            # right-click: mark/unmark square
            elif button == 3 and not GAME.minefield_uncovered[row][i]:
                GAME.minefield_marked[row][i] = (
                    False if GAME.minefield_marked[row][i] else True
                )
            return
        # clicked on control button
        if pygame.Rect(
            self.main_button[0].get_rect(topleft=self.main_button[1])
        ).collidepoint(pos):
            GAME.end_criteria = 2  # pressed QUIT button
            GAME.stage = 3

    def uncover_blank_neighbors(self):
        # uncover all squares adjacent to open blanks
        _change = True
        while _change:
            _change = False
            for row in range(self.grid_y):
                for i in range(self.grid_x):
                    if (
                        not GAME.minefield_numbers[row][i]
                        and GAME.minefield_uncovered[row][i]
                        and not GAME.minefield_marked[row][i]
                    ):
                        for y in range(
                            max(0, row - 1),
                            min(self.grid_y - 1, row + 1) + 1,
                        ):
                            for x in range(
                                max(0, i - 1),
                                min(self.grid_x - 1, i + 1) + 1,
                            ):
                                if not GAME.minefield_uncovered[y][x]:
                                    GAME.minefield_uncovered[y][x] = True
                                    _change = True

    def wrap_up(self):
        match self.end_criteria:
            case 0:  # Bomb Exploded (Lost)
                GAME.reveal = True

            case 1:  # Found all Bombs (Won)
                print("You Win!")
            case 2:  # ESC key / QUIT button pressed
                GAME.reveal = True

        self.main_game_button(" CONTINUE ")
        self.update_display()
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and pygame.Rect(
                    self.main_button[0].get_rect(topleft=self.main_button[1])
                ).collidepoint(pygame.mouse.get_pos()):
                    return


def main():
    global GAME
    GAME = Game()
    GAME.game = "boom"
    GAME.stage = 0
    main_menu = menus.menu(GAME)

    while main_menu.is_enabled():
        # print(GAME.stage)
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
                        GAME.end_criteria = 2
                        GAME.stage = 3
                    elif event.type == MOUSEBUTTONDOWN:
                        GAME.process_click(
                            pos=pygame.mouse.get_pos(), button=event.button
                        )
                GAME.update_display()
                GAME.check_end()
            case 3:
                GAME.wrap_up()
                GAME.stage = 0

    pygame.quit()


if __name__ == "__main__":
    main()
