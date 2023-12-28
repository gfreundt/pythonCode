import pygame
from pygame.locals import *
import random
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
        # load palette and colors
        self.PALETTE = self.PALETTES["CYBER_BLUE"]
        self.LOCAL_COLORS = {
            "R": self.COLORS["RED"],
            "B": self.COLORS["BROWN"],
            "G": self.COLORS["GREEN"],
            "Y": self.COLORS["YELLOW"],
            "M": self.COLORS["MAROON"],
            "L": self.COLORS["BLUE"],
            " ": self.COLORS["GRAY"],
        }
        # setup surfaces and sub-surfaces
        shell.define_main_surfaces(self)

        # load images
        shell.load_generic_images(self)
        self.BOTTLE_IMAGE = pygame.transform.scale(
            pygame.image.load("liquids_empty-bottle.png"), (128, 128)
        )
        self.BOTTLE_SELECTED_IMAGE = pygame.transform.scale(
            pygame.image.load("liquids_empty-bottle-selected.png"), (128, 128)
        )

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (
            self.full_bottles,
            self.empty_bottles,
            self.bottle_size,
            self.colors,
        ) = self.parameters
        # initial values
        self.selected_bottle = False
        self.fr = -1
        self.moves_counter = 1
        self.difficulty = self.full_bottles * self.colors // self.empty_bottles
        self.score = 0
        # fill bottles with random liquid content
        _randomize_colors = list(self.LOCAL_COLORS.keys())[:-1]
        random.shuffle(_randomize_colors)
        with_liquid = "".join(
            [
                i * ((self.full_bottles // self.colors) * self.bottle_size)
                for i in _randomize_colors[: self.colors]
            ]
        )
        allAvailable = list(
            with_liquid
            + " " * (self.full_bottles * self.bottle_size - len(with_liquid))
        )
        random.shuffle(allAvailable)
        allAvailable += list([" "] * self.bottle_size * self.empty_bottles)
        self.collection = [
            allAvailable[i * self.bottle_size : (i + 1) * self.bottle_size]
            for i in range(self.full_bottles + self.empty_bottles)
        ]
        # move empty spaces to top
        for k, bottle in enumerate(self.collection):
            if " " in bottle:
                self.collection[k] = sorted(self.collection[k], reverse=False)
        # create initial pygame entities
        self.surfaces = [
            self.update_entity(self.BOTTLE_IMAGE.copy(), bottle)
            for bottle in self.collection
        ]
        # create main game button
        shell.main_game_button(self, "QUIT")
        # start timer
        self.time_start = dt.now()

    def update_display(self):
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])
        for row in range(len(self.collection) // 10 + 1):
            for col in range(min(10, len(self.collection) - 10 * row)):
                self.MAIN_SURFACE.blit(
                    source=self.surfaces[row * 10 + col],
                    dest=(100 + 100 * col, 100 + 200 * row),
                )
        # update INFO surface
        self.score = len(
            [
                i
                for i in self.collection
                if i.count(i[0]) == self.bottle_size and i[0] != " "
            ]
        )
        _message = [
            ("Board Statistics", "", "NUN40B"),
            ("Bottles", f"< {self.full_bottles + self.empty_bottles} >", "NUN40"),
            ("Bottle Size", f"< {self.bottle_size} >", "NUN40"),
            ("Colors", f"< {self.colors} >", "NUN40"),
            (
                "Difficulty",
                f"< {self.difficulty} >",
                "NUN40",
            ),
            ("",),
            ("Game Statistics", "", "NUN40B"),
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
        # clicked on bottle
        bottle = self.get_selected_bottle(pos)
        if bottle > -1:
            if self.selected_bottle:
                self.transfer(self.fr, to=bottle)
                self.selected_bottle = False
                # change bottle color to unselected
                self.surfaces[self.fr] = self.update_entity(
                    self.BOTTLE_IMAGE.copy(), self.collection[self.fr]
                )
                self.fr = -1
            else:
                self.fr = bottle
                self.selected_bottle = True
                # change bottle color to selected
                self.surfaces[self.fr] = self.update_entity(
                    self.BOTTLE_SELECTED_IMAGE.copy(), self.collection[self.fr]
                )

    def get_selected_bottle(self, pos):
        for k, bottle in enumerate(self.surfaces):
            if bottle.get_rect(
                topleft=(100 + 100 * (k % 10), 100 + 200 * (k // 10))
            ).collidepoint(pos):
                return k
        return -1

    def transfer(self, fr, to):
        # capture errors
        if fr >= len(self.collection) or to >= len(self.collection):
            # bottle out of range
            return True
        elif fr == to:
            # must be different bottles
            return True
        elif self.collection[fr].count(" ") == len(self.collection[0]):
            # nothing in FROM bottle
            return True
        elif self.collection[to].count(" ") == 0:
            # TO bottle is full
            return True

        # move content from bottle to bottle
        bottle_from, bottle_to = self.collection[fr], self.collection[to]
        pos_from = 0
        for k, c in enumerate(bottle_from):
            if c == " ":
                pos_from = k + 1
        for k, c in enumerate(bottle_to):
            if c == " ":
                pos_to = k
        bottle_to[pos_to] = bottle_from[pos_from]
        bottle_from[pos_from] = " "

        # update pygame entities
        self.surfaces[fr] = self.update_entity(self.surfaces[fr], bottle_from)
        self.surfaces[to] = self.update_entity(self.surfaces[to], bottle_to)

        # update other game variables
        self.moves_counter += 1

    def update_entity(self, surface, content):
        height = 90 // self.bottle_size
        for y0, color in enumerate(content):
            pygame.draw.rect(
                surface, self.LOCAL_COLORS[color], (36, 30 + y0 * height, 56, height)
            )
        return surface

    def check_end(self):
        # not won
        for bottle in self.collection:
            if bottle.count(bottle[0]) < self.bottle_size:
                return
        # winner
        GAME.end_criteria = "won"
        GAME.stage = 3

    def wrap_up(self):
        # kept as function in case extra code needs to be inserted
        shell.wrap_up(GAME)


if __name__ == "__main__":
    GAME = Game("liquids")
    shell.main(GAME)
    pygame.quit()
