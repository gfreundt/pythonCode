import pygame
from pygame.locals import *
import random
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

        # load images
        self.BOTTLE_IMAGE = pygame.transform.scale(
            pygame.image.load("liquids_empty-bottle.png"), (128, 128)
        )
        self.BOTTLE_SELECTED_IMAGE = pygame.transform.scale(
            pygame.image.load("liquids_empty-bottle-selected.png"), (128, 128)
        )
        self.end_images = [
            "",
            pygame.image.load("boom_won.png"),
            pygame.image.load("boom_quit.png"),
        ]

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (
            GAME.full_bottles,
            GAME.empty_bottles,
            GAME.bottle_size,
            GAME.colors,
        ) = GAME.parameters
        # initial values
        self.selected_bottle = False
        self.fr = -1
        self.moves_counter = 1
        self.difficulty = self.full_bottles * self.colors // self.empty_bottles
        # fill bottles with random liquid content
        _randomize_colors = list(self.LOCAL_COLORS.keys())[:-1]
        random.shuffle(_randomize_colors)
        print(_randomize_colors)
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

    def update_display(self):
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])
        for row in range(len(self.collection) // 10 + 1):
            for col in range(min(10, len(self.collection) - 10 * row)):
                self.MAIN_SURFACE.blit(
                    source=self.surfaces[row * 10 + col],
                    dest=(100 + 100 * col, 100 + 200 * row),
                )
                """
                text = self.FONTS["ROB20"].render(
                    f"{row*10+col:02d}",
                    True,
                    self.COLORS["RED"]
                    if GAME.fr == (10 * row + col)
                    else self.COLORS["BLACK"],
                    self.COLORS["GRAY"],
                )
                self.MAIN_SURFACE.blit(
                    source=text, dest=(155 + 100 * col, 230 + 200 * row)
                )
                """

        # update INFO surface
        self.INFO_SURFACE.fill(self.PALETTE[2])
        self.messages = [
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
                f"< {self.difficulty/self.moves_counter:.1f}>",
                "NUN40",
            ),
        ]
        # print crafted text
        self.MSG_SURFACE.fill(self.COLORS["BLACK"])
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

    def process_click(self, pos, button):
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

        # clicked on control button
        if pygame.Rect(
            self.main_button[0].get_rect(topleft=self.main_button[1])
        ).collidepoint(pos):
            GAME.end_criteria = 2  # pressed QUIT button
            GAME.stage = 3

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
        GAME.end_criteria = 1
        GAME.stage = 3

    def wrap_up(self):
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
    GAME.game = "liquids"
    GAME.stage = 0
    mainmenu = menus.menu(GAME)

    while mainmenu.is_enabled():
        match GAME.stage:
            case 0:
                mainmenu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
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
