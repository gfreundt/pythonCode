from copy import deepcopy as copy
from tqdm import tqdm


def valid_grid(grid, test):
    test_grid = copy(grid)
    test_grid[test["row"]][test["col"]] = test["digit"]
    # check horizontal
    # for row in test_grid:
    row = test_grid[test["row"]]
    for i in range(1, 10):
        if row.count(i) > 1:
            return False
    # check vertical
    # for col in range(9):
    col = test["col"]
    row = [test_grid[i][col] for i in range(9)]
    for k in range(1, 10):
        if row.count(k) > 1:
            return False
    # check block
    for row in (0, 3, 6):
        for col in (0, 3, 6):
            # row = (test["row"] // 3) * 3
            # col = (test["col"] // 3) * 3
            block = [
                test_grid[i][j]
                for i in range(row, row + 3)
                for j in range(col, col + 3)
            ]
            for k in range(1, 10):
                if block.count(k) > 1:
                    return False
    # grid valid
    return True


def find_empty(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j
    return None


def solve(grid):
    find = find_empty(grid)
    if not find:
        return True
    row, col = find
    for num in range(1, 10):
        if valid_grid(grid, {"row": row, "col": col, "digit": num}):
            grid[row][col] = num
            if solve(grid):
                return grid
            grid[row][col] = 0
    return False


def flat_grid(grid):
    return "".join(["".join([str(i) for i in j]) for j in grid])


with open("sudokudotcom.csv", "r") as file:
    sudokus = [i.strip().split(",") for i in file.readlines()]

for sudoku in tqdm(sudokus):
    grid = [[int(sudoku[0][i + 9 * j]) for i in range(9)] for j in range(9)]
    s = solve(grid)
    if s:
        with open("sudoku_puzzles.csv", "a+") as file:
            file.write(f"{sudoku[0]},{flat_grid(s)},{sudoku[1]}\n")
