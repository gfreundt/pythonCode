from copy import deepcopy as copy


def check_complete_grid(grid):
    global answer_grid
    for y, line in enumerate(grid):
        for x, _ in enumerate(line):
            if grid[x][y] == 0:
                return False
    answer_grid = copy(grid)
    return True


def valid_grid(grid):
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


def solve():
    check_complete_grid(gridx)
    for x in range(9):
        for y in range(9):
            if gridx[y][x] == 0:
                for n in range(1, 10):
                    gridx[y][x] = n
                    if valid_grid(gridx):
                        solve()
                        gridx[y][x] = 0
                    else:
                        gridx[y][x] = 0
                return


def sudoku_solver():
    solve()
    return answer_grid


gridx = [
    [0, 0, 6, 1, 0, 0, 0, 0, 8],
    [0, 8, 0, 0, 9, 0, 0, 3, 0],
    [2, 0, 0, 0, 0, 5, 4, 0, 0],
    [4, 0, 0, 0, 0, 1, 8, 0, 0],
    [0, 3, 0, 0, 7, 0, 0, 4, 0],
    [0, 0, 7, 9, 0, 0, 0, 0, 3],
    [0, 0, 8, 4, 0, 0, 0, 0, 6],
    [0, 2, 0, 0, 5, 0, 0, 8, 0],
    [1, 0, 0, 0, 0, 2, 5, 0, 0],
]

a = sudoku_solver()
print(a)
