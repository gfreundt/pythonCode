from copy import deepcopy
import time


def print_grid(grid):
    for row in grid:
        line = ""
        for i in row:
            line = line + "X" if i else line + " "
        print(line)
    print("-" * 60)


def next_gen(grid):
    # grow grid out in every direction
    cols = len(grid[0])
    blank_horizontal = [[0 for _ in range(cols + 2)]]
    mid = [[0] + i + [0] for i in grid]
    grid = blank_horizontal + mid + blank_horizontal

    new_grid = deepcopy(grid)

    for row_pos, row in enumerate(new_grid):
        for col_pos, cell in enumerate(row):
            n = neighbors(row_pos, col_pos, grid)
            if cell and n not in (2, 3):
                new_grid[row_pos][col_pos] = 0
            elif not cell and n == 3:
                new_grid[row_pos][col_pos] = 1

    # clean edges

    for row in (new_grid[0], new_grid[-1]):
        for cell in (row[0], row[-1]):
            if cell:
                return new_grid

    new_grid = new_grid[1:-1]
    new_grid = [i[1:-1] for i in new_grid]

    return new_grid


def neighbors(row_pos, col_pos, grid):
    total = 0
    for r, row in enumerate(grid[row_pos - 1 : row_pos + 2]):
        for c, cell in enumerate(row[col_pos - 1 : col_pos + 2]):
            if cell and not (r == 1 and c == 1):
                total += 1
    return total


def test(grid):
    for row_pos, row in enumerate(grid):
        for col_pos, cell in enumerate(row):
            print(neighbors(row_pos, col_pos))
        print("-" * 20)


grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
print_grid(grid)

while True:
    grid = next_gen(grid)
    print_grid(grid)
    time.sleep(0.2)
