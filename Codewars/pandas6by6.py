import pandas as pd
from copy import deepcopy as copy


def printx(g):
    print(g)


def pre(clues):

    # define empty grid
    grid = [[0 for _ in range(6)] for _ in range(6)]

    # gridx: extended grid including clues | grido: regular grid with all active options
    g = [[clues[23 - k]] + i + [clues[6 + k]] for k, i in enumerate(grid)]
    gridx = [[0] + list(clues[:6]) + [0]] + g + [[0] + list(clues[17:11:-1]) + [0]]
    grido = [[list(range(1, 7)) for _ in range(6)] for _ in range(6)]

    Grid = pd.DataFrame(grid)
    GridX = pd.DataFrame(gridx)
    GridO = pd.DataFrame(grido)

    # fill the obvious (1 and 6 in sight)

    test = GridX.loc[GridX[0] == 1]
    print(test)

    for y in range(1, 7):
        if row[0] == 6:
            Grid[k], GridO[k] = list(range(1, 7)), [list(range(1, 7))]
        elif row[0] == 1:
            Grid[k][0], GridO[k][0] = 6, [6]
        if row[7] == 6:
            Grid[k], GridO[k] = list(range(6, 0, -1)), [list(range(6, 0, -1))]
        elif row[7] == 1:
            Grid[k][5], GridO[k][5] = 6, [6]

    print(Grid)
    print(GridX)
    print(GridO)

    # fill the obvious (1 and 6 in sight)
    for k, row in enumerate(gridx[1:-1]):
        if row[0] == 6:
            grid[k], grido[k] = list(range(1, 7)), [list(range(1, 7))]
        elif row[0] == 1:
            grid[k][0], grido[k][0] = 6, [6]
        if row[7] == 6:
            grid[k], grido[k] = list(range(6, 0, -1)), [list(range(6, 0, -1))]
        elif row[7] == 1:
            grid[k][5], grido[k][5] = 6, [6]

    print(grid)

    return grid

    adj = {
        0: (0, 0),
        1: (0, 1),
        2: (0, 2),
        3: (0, 3),
        4: (0, 3),
        5: (1, 3),
        6: (2, 3),
        7: (3, 3),
        8: (3, 3),
        9: (3, 2),
        10: (3, 1),
        11: (3, 0),
        12: (3, 0),
        13: (2, 0),
        14: (1, 0),
        15: (0, 0),
    }
    grid, grido = fixed(grid, adj, clues, grido)
    grid, grido = first_run(grid, adj, clues, grido)
    return grid, grido


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
clues = (3, 2, 2, 3, 2, 1, 1, 2, 6, 3, 2, 2, 5, 1, 2, 2, 4, 3, 6, 2, 1, 2, 2, 4)

a = solve_puzzle(clues)

print(a)
