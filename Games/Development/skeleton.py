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
        # change: (self.STONES_PER_PIT, self.END_GAME_EARLY) = self.parameters
        # initial values
        # TODO: fill these
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


if __name__ == "__main__":
    GAME = Game("")  # TODO: fill name
    shell.main(GAME)
    pygame.quit()
