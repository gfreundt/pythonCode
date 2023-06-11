import numpy as np
from copy import deepcopy as copy
from tabulate import tabulate


def printx(g):
    print(tabulate(g))


def pre(clues):

    # define empty grid
    grid = [[0 for _ in range(6)] for _ in range(6)]

    #   extended grid including clues | grido: regular grid with all active options
    g = [[clues[23 - k]] + i + [clues[6 + k]] for k, i in enumerate(grid)]
    gridx = (
        [[" "] + list(clues[:6]) + [" "]] + g + [[" "] + list(clues[17:11:-1]) + [" "]]
    )

    Grid = np.array(grid)
    GridX = np.array(gridx)

    # printx(GridX)

    # fill the obvious (1 and 6 in sight) - horizontally
    for y in range(1, 7):
        if int(GridX[y, 0]) == 6:
            Grid[y - 1] = list(range(1, 7))
        elif int(GridX[y, 0]) == 1:
            Grid[y - 1][0] = 6
        if int(GridX[y, 7]) == 6:
            Grid[y - 1] = list(range(6, 0, -1))
        elif int(GridX[y, 7]) == 1:
            Grid[y - 1][5] = 6

    # fill the obvious (1 and 6 in sight) - vertically
    for x in range(1, 7):
        if int(GridX[0, x]) == 6:
            Grid[:, x - 1] = list(range(1, 7))
        elif int(GridX[0, x]) == 1:
            Grid[0][x - 1] = 6
        if int(GridX[7, x]) == 6:
            Grid[:, x - 1] = list(range(6, 0, -1))
        elif int(GridX[7, x]) == 1:
            Grid[5][x - 1] = 6

    GridO = update_grido(Grid)

    printx(GridO)

    return Grid


def update_grido(Grid):
    GridO = np.array([[range(1, 7) for _ in range(6)] for _ in range(6)])
    for y in range(6):
        for x in range(6):
            if int(Grid[y, x]) > 0:
                GridO[y, x] = [3, 4, 5]  # [int(Grid[y, x])]
    return GridO


def fixed(grid, adj, clues, grido):
    for k, c in enumerate(clues):
        if c == 1:
            grid[adj[k][0]][adj[k][1]] = 4
            grido[adj[k][0]][adj[k][1]] = [4]
        elif c == 4:
            grid[adj[k][0]][adj[k][1]] = 1
            grido[adj[k][0]][adj[k][1]] = [1]
    return grid, grido


def first_run(grid, adj, clues, grido):
    for k, _ in enumerate(grid):
        if clues[15 - k] == 3 and clues[4 + k] == 2:
            grid[k][2] = 4
            grido[k][2] = [4]
        if clues[15 - k] == 2 and clues[4 + k] == 3:
            grid[k][1] = 4
            grido[k][1] = [4]
        if clues[k] == 3 and clues[11 - k] == 2:
            grid[2][k] = 4
            grido[2][k] = [4]
        if clues[k] == 2 and clues[11 - k] == 3:
            grid[1][k] = 4
            grido[1][k] = [4]
    return grid, grido


def valid_grid(grid, clues):
    def sight(line):
        if line.count(0) > 0:
            return 0
        sight = 1
        max_height = line[0]
        for k, _ in enumerate(line[:-1]):
            if line[k + 1] > max_height:
                sight += 1
                max_height = line[k + 1]
        return sight

    inv_grid = [[i[col] for i in grid] for col in range(6)]

    list_of_sights = []
    for g in (grid, inv_grid):
        # test: all numbers in row/col are different
        for line in g:
            if [i for i in range(1, 7) if line.count(i) > 1]:
                return False
        # create list of all sights count
        for k, line in enumerate(g):
            list_of_sights.append(sight(line))
        for k, line in enumerate(g):
            list_of_sights.append(sight(line[::-1]))

    sights_given = clues[23:17:-1] + clues[6:12] + clues[:6] + clues[17:11:-1]

    # test if all non-0 sights match
    for i, j in zip(sights_given, list_of_sights):
        if i > 0 and j > 0 and i != j:
            return False

    return True


def solve(grid, clues, solved):

    complete_test = len([j for i in grid for j in i if j != 0]) == 6 ** 2
    if complete_test or solved:
        solved = True
        answer.append(copy(grid))
        return grid

    for r, row in enumerate(grid):
        for c, _ in enumerate(row):
            if grid[r][c] == 0:
                for t in range(1, 7):
                    grid[r][c] = t
                    if valid_grid(grid, clues):
                        grid = solve(grid, clues, solved)
                    grid[r][c] = 0
                return grid

    return grid


def solve_puzzle(clues):
    global answer
    answer = []

    grid = pre(clues)

    return grid
    grid = solve(grid, clues, solved=False)
    print(grid)
    print(answer)
    return tuple([tuple(i) for i in answer[0]])


n = 6
clues = (3, 2, 6, 1, 2, 1, 1, 2, 6, 3, 2, 2, 5, 1, 2, 2, 4, 3, 6, 2, 1, 2, 1, 4)
# clues = (3, 2, 6, 1, 2, 0, 0, 0, 0, 0, 4, 3, 1, 0, 6, 2, 1, 3, 0, 2, 0, 2, 3, 4)


a = solve_puzzle(clues)

print(a)
