from itertools import count
import time
import random
import pyautogui
from PIL import Image
import time
from easyocr import Reader
import numpy as np
from colorama import Fore, Back, Style


class Card:
    def __init__(self, number, color):
        self.color = color
        self.number = number
        self.card = f"{self.number:02d}" + self.color
        # self.color = "RED" if self.suit in ("S", "C") else "BLACK"
        self.valid = True


class Table:
    def __init__(self, columns, game_number):
        self.columns = columns
        self.trans = ["000"] * 4
        self.piles = ["000"] * 4
        self.game_number = game_number


def create_deck(joker=False, shuffle=False):
    deck = [Card(i, j) for i in range(1, 14) for j in "RB"]
    if joker:
        pass  # TODO: add jokers
    if shuffle:
        random.shuffle(deck)
    return deck


def generate_random_table(deck):
    columns = []
    s = 0
    for q in [7] * 4 + [6] * 4:
        columns.append(deck[s : s + q])
        s += int(q)
    return Table(columns)


def image_to_text():
    def get_color(im):
        imArray = np.array(im).tolist()
        for i in imArray:
            for j in i:
                if (j[0], j[1], j[2]) == (0, 0, 0):
                    return "B"
        return "R"

    def clean(number):
        if not number:
            return 0
        for fix in [("J", 11), ("Q", 12), ("K", 13), ("A", 1), ("0", 12), ("99", 0)]:
            if number[0] == fix[0]:
                return fix[1]
        return int(number[0])

    # time.sleep(5)
    # image = pyautogui.screenshot()

    image = Image.open("table.jpg")

    # game number coordinates
    x_start, y_start = 1290, 50  # ?, ?
    x_size, y_size = 110, 30  # ?, ?
    image.crop((x_start, y_start, x_start + x_size, y_start + y_size)).save("temp.jpg")
    game_number = Reader(["en"], gpu=False).readtext(
        "temp.jpg",
        detail=0,
        text_threshold=0.5,
    )
    if not game_number:
        game_number = 0

    # column coordinates
    x_start, y_start = 255, 427  # 222, 560
    x_size, y_size = 38, 37  # 42, 70
    x_step, y_step = 266, 73  # 297, 82
    x0 = int(x_start)

    table = []
    # iterate each column
    for i in [7] * 4 + [6] * 4:  # [2, 2, 2]:
        y0 = int(y_start)
        # iterate each card per column
        col = []
        for _ in range(i):
            # iterate three crop attempts, break when one is correct
            for crop_size in (1, 1.5, 2):
                im = image.crop((x0, y0, x0 + x_size, y0 + int(y_size * crop_size)))
                im.save("temp.jpg")
                ocr_result = Reader(["en"], gpu=False).readtext(
                    "temp.jpg",
                    decoder="beamsearch",
                    batch_size=32,
                    detail=0,
                    text_threshold=0.5,
                )
                if ocr_result:
                    break
            # combine number and color
            col.append(Card(clean(ocr_result), get_color(im)))
            y0 += y_step
        x0 += x_step
        table.append(col)
    return table, game_number[0]


def capture_validation(table):

    all_cards = [i.card for col in table.columns for i in col]
    invalid_cards = [
        i
        for col in table.columns
        for i in col
        if i.card[0] == 0 or all_cards.count(i.card) > 2
    ]

    for i in invalid_cards:
        i.valid = False


def print_table(table):
    print(f"Game #{table.game_number}")
    for i in table.trans + table.piles:
        print(i + " ", end="")
    print("\n")
    max_col_size = max([len(i) for i in table.columns])
    for i in range(max_col_size):
        for col in table.columns:
            if i < len(col):
                # print(col[i].valid)
                if not col[i].valid:
                    style = Back.RED
                else:
                    style = Back.GREEN  # Style.RESET_ALL
                print(style + col[i].card + " ", end="")
        print()
    print(Style.RESET_ALL)


def main():
    table = Table(*image_to_text())
    capture_validation(table)
    print()
    print_table(table)


start = time.time()
main()
print(f"time: {time.time()-start}")
