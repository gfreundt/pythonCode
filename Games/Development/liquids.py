import pygame
from pygame.locals import *
import random
import os, time

pygame.init()


class Environment:
    RESOURCES_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Fonts")
    # DISPLAY_WIDTH = pygame.display.Info().current_w
    # DISPLAY_HEIGHT = pygame.display.Info().current_h // 1.01
    BACKGROUND_COLOR = (128, 128, 128)
    FONT20 = pygame.font.Font(os.path.join(RESOURCES_PATH, "roboto.ttf"), 20)
    BOTTLE_IMAGE = pygame.transform.scale(
        pygame.image.load("\pythonCode\Games\Development\empty-bottle2.png"), (128, 128)
    )
    BLACK = (0, 0, 0)
    COLORS = {
        "R": (255, 0, 0),
        "B": (0, 0, 255),
        "G": (0, 255, 0),
        "Y": (225, 255, 0),
        "M": (106, 84, 12),
        " ": (255, 255, 255),
    }
    MAIN_SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


class Game:
    full_bottles = 34
    empty_bottles = 1
    bottle_size = 4
    colors = 4  # range 2-6
    selected_bottle = False


def display2():
    ENV.MAIN_SURFACE.fill(ENV.BACKGROUND_COLOR)
    for row in range(len(GAME.collection) // 10 + 1):
        for col in range(min(10, len(GAME.collection) - 10 * row)):
            ENV.MAIN_SURFACE.blit(
                source=GAME.surfaces[row * 10 + col],
                dest=(100 + 100 * col, 100 + 200 * row),
            )
            text = ENV.FONT20.render(
                f"{row*10+col:02d}", True, ENV.BLACK, ENV.BACKGROUND_COLOR
            )
            ENV.MAIN_SURFACE.blit(source=text, dest=(155 + 100 * col, 230 + 200 * row))
    pygame.display.flip()


def setup():
    full_bottles = 9
    empty_bottles = 1
    bottle_size = 4
    colors = 3  # range 2-6

    with_liquid = "".join(
        [
            i * ((full_bottles // colors) * bottle_size)
            for i in list(ENV.COLORS.keys())[:colors]
        ]
    )
    allAvailable = list(
        with_liquid + " " * (full_bottles * bottle_size - len(with_liquid))
    )
    random.shuffle(allAvailable)
    allAvailable += list([" "] * bottle_size * empty_bottles)
    GAME.collection = [
        allAvailable[i * bottle_size : (i + 1) * bottle_size]
        for i in range(full_bottles + empty_bottles)
    ]
    # spaces must be on top (fix later)
    for k, bottle in enumerate(GAME.collection):
        if " " in bottle:
            GAME.collection[k] = sorted(GAME.collection[k], reverse=False)
    # create initial pygame entities
    GAME.surfaces = [
        update_entity(ENV.BOTTLE_IMAGE.copy(), bottle) for bottle in GAME.collection
    ]

    return bottle_size


def process_click(pos):
    bottle = get_selected_bottle(pos)
    if bottle == -1:
        return
    if GAME.selected_bottle:
        transfer(GAME.fr, to=bottle)
        GAME.selected_bottle = False
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
    # fr, to = int(fr), int(to)
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


def update_entity(surface, content):
    height = 90 // GAME.colors
    for y0, color in enumerate(content):
        pygame.draw.rect(surface, ENV.COLORS[color], (36, 30 + y0 * height, 56, height))
    return surface


def check_end(bottle_size):
    for bottle in GAME.collection:
        if bottle.count(bottle[0]) < bottle_size:
            return False
    return True


def main():
    clock = pygame.time.Clock()
    delay = 10
    bottle_size = setup()
    end_game = False

    while not end_game:
        clock.tick(delay)
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN:
                pygame.quit()
                return
            elif event.type == MOUSEBUTTONDOWN:
                process_click(
                    pos=pygame.mouse.get_pos(),
                )
        if check_end(bottle_size):
            print("success")
            pygame.quit()
            return
        display2()


ENV = Environment()
GAME = Game()


main()
