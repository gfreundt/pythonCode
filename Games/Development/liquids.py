import pygame
from pygame.locals import *
import random
import sys, os

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import menus

pygame.init()


class Game:
    def __init__(self):
        # load general presets
        pygameUtils.__init__(self)
        self.BOTTLE_IMAGE = pygame.transform.scale(
            pygame.image.load("empty-bottle.png"), (128, 128)
        )
        self.COLOR1 = self.COLORS["CYBER_BLUE01"]
        self.COLOR2 = self.COLORS["CYBER_BLUE02"]
        self.COLOR3 = self.COLORS["CYBER_BLUE03"]
        self.COLOR4 = self.COLORS["CYBER_BLUE04"]
        self.COLOR5 = self.COLORS["CYBER_BLUE05"]
        self.LOCAL_COLORS = {
            "R": self.COLORS["RED"],
            "B": self.COLORS["BLUE"],
            "G": self.COLORS["GREEN"],
            "Y": self.COLORS["YELLOW"],
            "M": self.COLORS["MAROON"],
            " ": self.COLORS["WHITE"],
        }

    selected_bottle = False
    fr = -1
    moves_counter = 0

    def update_display(self):
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])
        for row in range(len(self.collection) // 10 + 1):
            for col in range(min(10, len(self.collection) - 10 * row)):
                self.MAIN_SURFACE.blit(
                    source=self.surfaces[row * 10 + col],
                    dest=(100 + 100 * col, 100 + 200 * row),
                )
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
        pygame.display.flip()

    def setup(self):
        with_liquid = "".join(
            [
                i * ((self.full_bottles // GAME.colors) * GAME.bottle_size)
                for i in list(self.LOCAL_COLORS.keys())[: self.colors]
            ]
        )
        allAvailable = list(
            with_liquid
            + " " * (self.full_bottles * self.bottle_size - len(with_liquid))
        )
        random.shuffle(allAvailable)
        allAvailable += list([" "] * self.bottle_size * self.empty_bottles)
        GAME.collection = [
            allAvailable[i * self.bottle_size : (i + 1) * self.bottle_size]
            for i in range(self.full_bottles + self.empty_bottles)
        ]
        # spaces must be on top (fix later)
        for k, bottle in enumerate(self.collection):
            if " " in bottle:
                self.collection[k] = sorted(self.collection[k], reverse=False)
        # create initial pygame entities
        self.surfaces = [
            update_entity(self.BOTTLE_IMAGE.copy(), bottle)
            for bottle in self.collection
        ]


def process_click(pos, button):
    bottle = get_selected_bottle(pos)
    if bottle > -1:
        if GAME.selected_bottle:
            transfer(GAME.fr, to=bottle)
            GAME.selected_bottle = False
            GAME.fr = -1
        else:
            GAME.fr = bottle
            GAME.selected_bottle = True


def get_selected_bottle(pos):
    for k, bottle in enumerate(GAME.surfaces):
        if bottle.get_rect(
            topleft=(100 + 100 * (k % 10), 100 + 200 * (k // 10))
        ).collidepoint(pos):
            return k
    return -1


def transfer(fr, to):
    # capture errors
    if fr >= len(GAME.collection) or to >= len(GAME.collection):
        print("Bottle out of range")
        return True
    if fr == to:
        print("Must be different bottles")
        return True
    if GAME.collection[fr].count(" ") == len(GAME.collection[0]):
        print("Error: nothing in FROM bottle")
        return True
    elif GAME.collection[to].count(" ") == 0:
        print("Error: TO bottle is full")
        return True

    # move content from bottle to bottle
    bottle_from, bottle_to = GAME.collection[fr], GAME.collection[to]
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
    GAME.surfaces[fr] = update_entity(GAME.surfaces[fr], bottle_from)
    GAME.surfaces[to] = update_entity(GAME.surfaces[to], bottle_to)

    # update other game variables
    GAME.moves_counter += 1


def update_entity(surface, content):
    height = 90 // GAME.bottle_size
    for y0, color in enumerate(content):
        pygame.draw.rect(
            surface, GAME.LOCAL_COLORS[color], (36, 30 + y0 * height, 56, height)
        )
    return surface


def check_end():
    for bottle in GAME.collection:
        if bottle.count(bottle[0]) < GAME.bottle_size:
            return False
    return True


def main():
    global GAME
    GAME = Game()

    mainmenu = menus.liquids(GAME)
    GAME.stage = 0

    while mainmenu.is_enabled():
        if GAME.stage == 0:
            mainmenu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            # print(GAME.full_bottles, GAME.empty_bottles, GAME.bottle_size, GAME.colors)
        elif GAME.stage == 1:
            GAME.setup()
            GAME.stage = 2
        elif GAME.stage == 2:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT or event.type == KEYDOWN:
                    # pygame.quit()
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    process_click(pos=pygame.mouse.get_pos(), button=event.button)
                GAME.update_display()

                if check_end():
                    print(f"Finished Successfully in {GAME.moves_counter} moves!")
                    return


if __name__ == "__main__":
    main()
