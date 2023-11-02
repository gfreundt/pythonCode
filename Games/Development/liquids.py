# import pygame
# from pygame.locals import *
import random
from colorama import Fore, Back, Style

# pygame.init()


def display(collection):

    cc = {
        "A": Back.RED,
        "B": Back.BLUE,
        "C": Back.GREEN,
        "D": Back.YELLOW,
        "E": Back.MAGENTA,
        "F": Back.WHITE,
        "G": Back.CYAN,
        " ": Back.BLACK,
    }

    for k, b in enumerate(collection[0]):
        for i, j in enumerate(collection):
            print(f" {cc[collection[i][k]]} {Style.RESET_ALL} |", end="")
        print()
    print("-" * len(collection) * 4)
    print(" " + " ".join([f"{i:02d}|" for i, k in enumerate(collection)]))


def setup():
    full_bottles = 13
    empty_bottles = 3
    bottle_size = 6
    colors = 4
    icons = [chr(65 + i) for i in range(colors)]

    with_liquid = "".join([i * ((full_bottles // colors) * bottle_size) for i in icons])
    allAvailable = list(
        with_liquid + " " * (full_bottles * bottle_size - len(with_liquid))
    )

    random.shuffle(allAvailable)
    allAvailable += list([" "] * bottle_size * empty_bottles)

    collection = [
        allAvailable[i * bottle_size : (i + 1) * bottle_size]
        for i in range(full_bottles + empty_bottles)
    ]

    # spaces must be on top (fix later)
    for k, bottle in enumerate(collection):
        if " " in bottle:
            collection[k] = sorted(collection[k], reverse=False)
    # print(collections)
    return collection, bottle_size


def transfer(collection, fr, to):
    # capture all errors
    if fr >= len(collection) or to >= len(collection):
        print("Bottle out of range")
        return True
    if fr == to:
        print("Must be different bottles")
        return True
    if collection[fr].count(" ") == len(collection[0]):
        print("Error: nothing in FROM bottle")
        return True
    elif collection[to].count(" ") == 0:
        print("Error: TO bottle is full")
        return True

    # move content
    bottle_from, bottle_to = collection[fr], collection[to]
    pos_from = 0
    for k, c in enumerate(bottle_from):
        if c == " ":
            pos_from = k + 1
    for k, c in enumerate(bottle_to):
        if c == " ":
            pos_to = k
    bottle_to[pos_to] = bottle_from[pos_from]
    bottle_from[pos_from] = " "

    return False


def check_end(collection, bottle_size):
    for bottle in collection:
        if bottle.count(bottle[0]) < bottle_size:
            return False
    return True


def main():
    collection, bottle_size = setup()

    while True:
        display(collection)
        fr = int(input("From > "))
        to = int(input("To > "))
        error = transfer(collection, fr, to)
        if check_end(collection, bottle_size):
            print("success")
            return


main()
