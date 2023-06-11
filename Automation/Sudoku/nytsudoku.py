import easyocr
import pyautogui
from PIL import ImageGrab
import time
import numpy as np
import csv
from copy import deepcopy as copy


def capture():
    xstart, ystart = 505, 445
    xsize, ysize = 125, 125
    xstep, ystep = 135, 135

    time.sleep(3)
    # open web and scroll to appropriate position
    img = ImageGrab.grab()

    puzzle = []
    for i in range(9):
        row = []
        for j in range(9):
            x0, y0 = xstart + xstep * j, ystart + ystep * i
            x1, y1 = x0 + xsize, y0 + ysize
            print(i * 9 + j)
            s = easyocr.Reader(["en"], gpu=False).readtext(
                np.asarray(img.crop((x0, y0, x1, y1))), text_threshold=0.5
            )
            if s:
                row.append(int(s[0][1]))
            else:
                row.append(0)
        puzzle.append(row)
    return puzzle


def save(puzzle, origin, level):
    filename = "SudokuPuzzles.csv"
    data = [level] + [origin] + [j for i in puzzle for j in i]
    with open(filename, mode="a+", newline="") as outfile:
        csv.writer(outfile).writerow(data)


def check_valid(puzzle, i, row, col):
    rows = puzzle[int(row)]
    column = [puzzle[r][col] for r in range(9)]
    if i in rows or i in column:
        return False
    squareRow = (row // 3) * 3
    squareColumn = (col // 3) * 3
    square = [
        puzzle[y][z]
        for y in range(squareRow, squareRow + 3)
        for z in range(squareColumn, squareColumn + 3)
    ]
    return False if i in square else True


def find(puzzle):
    for i in range(0, 9):
        for j in range(0, 9):
            if puzzle[i][j] == 0:
                return i, j


def solve(puzzle):
    finds = find(puzzle)
    if finds:
        row, col = finds
    else:
        return True
    for i in range(1, 10):
        if check_valid(puzzle, i, row, col):
            puzzle[row][col] = i
            if solve(puzzle):
                return True
            puzzle[row][col] = 0
    # return False


def gaps(original, solved):
    gaps_puzzle = copy(solved)
    for i in range(0, 9):
        for j in range(0, 9):
            if original[i][j] != 0:
                gaps_puzzle[i][j] = 0
    return gaps_puzzle


def fill_puzzle(gp):
    # select normal input mode
    pyautogui.moveTo(1900, 460, 2)
    pyautogui.click()
    # fill empty squares in row
    for i in range(0, 9):
        for j in range(0, 9):
            digit = gp[i][j]
            if digit != 0:
                pyautogui.press(str(digit))
            pyautogui.press("right")
            time.sleep(0.5)
        # go back to the leftmost square and drop onw
        for _ in range(9):
            pyautogui.press("left")
            time.sleep(0.5)
        pyautogui.press("down")
        time.sleep(0.5)


def print_puzzle(puzzle):
    print()
    for row in puzzle:
        print(row)


def main():
    # get puzzle from webpage and save in csv file
    original_puzzle = capture()
    puzzle = copy(original_puzzle)
    save(puzzle, origin="NYT", level="E")

    # solve and create "filled gaps" grid
    solve(puzzle)
    solved_puzzle = copy(puzzle)
    gaps_puzzle = gaps(original_puzzle, solved_puzzle)

    # automate fill
    fill_puzzle(gaps_puzzle)


original_puzzle = [
    [0, 2, 0, 0, 0, 0, 0, 7, 0],
    [0, 0, 0, 5, 8, 0, 0, 0, 0],
    [4, 0, 0, 7, 1, 0, 0, 0, 0],
    [0, 8, 0, 6, 0, 0, 7, 9, 0],
    [0, 3, 9, 0, 0, 5, 2, 8, 0],
    [0, 0, 0, 0, 0, 0, 0, 3, 0],
    [1, 0, 0, 2, 0, 0, 9, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 3],
    [6, 5, 0, 0, 0, 0, 0, 0, 0],
]

time.sleep(5)
main()
