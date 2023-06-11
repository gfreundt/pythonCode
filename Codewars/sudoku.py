import copy


class Var:
    def __init__(self) -> None:
        self.results = []


def printg(grid):
    for i in grid:
        print(i)
    print("\n")


def valid(grid):
    # create vertical and 3x3 grids
    inv_grid = [[i[col] for i in grid] for col in range(9)]
    box_grid = [
        sum([line[3 * x : 3 * x + 3] for line in grid[3 * y : 3 * y + 3]], [])
        for x in range(3)
        for y in range(3)
    ]
    # validate
    for grids in (grid, inv_grid, box_grid):
        for line in grids:
            if [i for i in range(1, 10) if line.count(i) > 1]:
                return False
    return True


def solver():

    if len([i for line in grid for i in line if i == 0]) < 1:
        v.results.append(copy.deepcopy(grid))

    for x in range(9):
        for y in range(9):
            if grid[y][x] == 0:
                for n in range(1, 10):
                    grid[y][x] = n
                    if valid(grid):
                        solver()
                    else:
                        grid[y][x] = 0
                return


grid_solved = []

grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]
"""
grid = [
    [9, 1, 3, 6, 5, 0, 4, 2, 7],
    [2, 5, 4, 9, 1, 7, 6, 0, 3],
    [6, 8, 7, 4, 0, 2, 9, 1, 5],
    [5, 3, 0, 1, 0, 9, 7, 6, 4],
    [1, 6, 2, 3, 7, 4, 5, 9, 8],
    [4, 7, 9, 8, 6, 5, 1, 3, 2],
    [8, 9, 1, 7, 4, 3, 2, 5, 6],
    [7, 2, 6, 0, 0, 1, 3, 0, 9],
    [0, 0, 5, 2, 0, 0, 8, 7, 1],
]

grid = [
    [0, 1, 3, 6, 5, 0, 0, 2, 7],
    [2, 0, 4, 0, 1, 7, 6, 0, 3],
    [0, 8, 7, 4, 0, 2, 9, 1, 0],
    [0, 3, 0, 0, 0, 0, 7, 6, 4],
    [1, 6, 2, 3, 7, 4, 0, 9, 8],
    [4, 7, 9, 8, 6, 5, 1, 0, 0],
    [8, 9, 0, 0, 4, 3, 2, 0, 6],
    [7, 2, 0, 0, 0, 1, 3, 0, 9],
    [0, 0, 0, 2, 0, 0, 8, 7, 1],
]
"""


v = Var()
solver()
for i in v.results:
    printg(i)
