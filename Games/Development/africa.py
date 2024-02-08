import sys, os, time
from datetime import datetime as dt
from random import randrange, choice
import pygame
from pygame.locals import *

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import game_shell as shell

pygame.init()


class Game:
    def __init__(self, game_name) -> None:
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
        (self.STONES_PER_PIT, self.END_GAME_EARLY) = self.parameters
        # initial values
        self.board = [self.STONES_PER_PIT for _ in range(0, 14)]
        self.board[6], self.board[13] = 0, 0
        self.turn = choice((1, 2))
        self.pos = 14  # out of range for game start only
        # create main game button
        shell.main_game_button(self, "QUIT")
        # create click areas
        self.click_areas = [False for _ in range(14)]
        # wait for selection flag
        self.wait_selection = True
        # inital time
        self.time_start = dt.now()
        # player 2 strategy
        self.AI_STRATEGY = randrange(0, 3)

    def move(self):
        if self.wait_selection:
            # if player's turn wait for selection
            if self.turn == 1:
                return
            # if computer's turn take action depending on pre-selected strategy
            elif self.turn == 2:
                self.wait_selection = False
                time.sleep(1)
                match self.AI_STRATEGY:
                    case 0:  # random selection
                        self.pos = choice(
                            [k for k in range(7, 13) if self.board[k] > 0]
                        )
                    case 1:  # lowest number (tiebreaker: closest to home)
                        self.pos = [
                            k
                            for k in range(7, 13)
                            if self.board[k]
                            == min([i for i in self.board[7:13] if i > 0])
                        ][-1]
                    case 2:  # highest number (tiebreaker: furthest to home)
                        self.pos = [
                            k
                            for k in range(7, 13)
                            if self.board[k] == max(self.board[7:13])
                        ][0]

        while True:
            # pick up all stones from starting pit
            stones = self.board[self.pos]
            self.board[self.pos] = 0
            # go clockwise dropping one stone in each pit, skipping opponent's home
            while stones > 0:
                self.pos += 1
                if self.turn == 2 and self.pos == 6:
                    self.pos = 7
                elif (self.turn == 1 and self.pos == 13) or (self.pos == 14):
                    self.pos = 0
                self.board[self.pos] += 1
                stones -= 1

            # last stone lands on active player's home
            if self.turn == 1 and self.pos == 6 or self.turn == 2 and self.pos == 13:
                self.wait_selection = True
                return False

            # last stone lands on empty pit
            elif self.board[self.pos] == 1:
                # steals from opposite pit
                if self.turn == 2 and 7 <= self.pos <= 12:
                    self.board[13] += self.board[12 - self.pos]
                    self.board[12 - self.pos] = 0
                elif self.turn == 1 and 0 <= self.pos <= 5:
                    self.board[6] += self.board[-(self.pos - 12)]
                    self.board[-(self.pos - 12)] = 0

                # switch active player
                self.turn = 1 if self.turn == 2 else 2
                time.sleep(0.05)
                self.wait_selection = True
                return False

            # last stone lands on non-empty pit
            pass

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
        self.score = self.board[6]
        for x, pit in enumerate(self.board):
            _text = self.FONTS["ROB80"].render(
                f"{pit:02d}", True, self.COLORS["WHITE"], self.COLORS["BLACK"]
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
                f"< {self.score}>",
                "NUN40",
            ),
        ]
        shell.update_info_surface(GAME, _message)
        pygame.display.flip()

        # execute move and return if game ends
        if self.stage == 2:
            self.move()

    def process_click(self, pos, button):
        # clicked on quit button
        if shell.check_if_main_game_button_pressed(self, pos):
            return
        for k, click_check in enumerate(self.click_areas):
            if click_check.collidepoint(pos):
                if (
                    (self.turn == 1 and 0 <= k <= 5)
                    or (self.turn == 2 and 7 <= k <= 12)
                ) and self.board[k] > 0:
                    self.pos = k
                    self.wait_selection = False

    def process_key(self, key):
        return

    def check_end(self):
        # check if game over (empty pits in one player's side)
        if sum(self.board[0:6]) == 0 or sum(self.board[7:13]) == 0:
            # add remaining stones to each player's home
            self.board[6] += sum(self.board[0:6])
            self.board[13] += sum(self.board[7:13])
            # set all pits to 0
            self.board[0:6] = self.board[7:13] = [0 for _ in range(0, 6)]
        # check if game over (condition set to check if one player's score is unreachable)
        elif not (
            self.END_GAME_EARLY
            and (
                self.board[6] > sum(self.board) / 2
                or self.board[13] > sum(self.board) / 2
            )
        ):
            return

        self.stage = 3
        if self.board[6] > self.board[13]:
            self.end_criteria = "won"
        elif self.board[6] < self.board[13]:
            self.end_criteria = "lost"
        else:
            self.end_criteria = "tied"

    def wrap_up(self):
        shell.wrap_up(self)

    def high_score(self):
        if self.end_criteria == "won":
            shell.update_high_scores(self)


if __name__ == "__main__":
    GAME = Game("africa")
    shell.main(GAME)
    pygame.quit()
