import copy


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


def solver(grid):
    if len([i for line in grid for i in line if i == 0]) < 1:
        result.append(copy.deepcopy(grid))
    for x in range(9):
        for y in range(9):
            if grid[y][x] == 0:
                for n in range(1, 10):
                    grid[y][x] = n
                    if valid(grid):
                        solver(grid)
                    grid[y][x] = 0
                return grid

    return grid


def solve(grid):
    global result
    result = []
    solver(grid)
    return result[0]


def str_to_puzzle(s):
    puzzleSolution = []
    for i in range(len(s)):
        if i % 9 == 0:
            temp = []
            for j in s[i : i + 9]:
                temp.append(int(j))
            puzzleSolution.append(temp)
    return puzzleSolution


def same_row(i, j):
    if i // 9 == j // 9:
        return True
    return False


def same_col(i, j):
    if i % 9 == j % 9:
        return True
    return False


def same_block(i, j):
    if ((i // 9) // 3 == (j // 9) // 3) & ((i % 9) // 3 == (j % 9) // 3):
        return True
    return False


def sudoku_brute_force(s):
    # 1
    i = s.find("0")

    # 2
    cannotuse = {
        s[j]
        for j in range(len(s))
        if same_row(i, j) | same_col(i, j) | same_block(i, j)
    }
    every_possible_values = {str(i) for i in range(10)} - cannotuse

    # 3
    for val in every_possible_values:
        s = s[0:i] + val + s[i + 1 :]
        sudoku_brute_force(s)
        if s.find("0") == -1:
            print(str_to_puzzle(s))


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
"""
grid = [
    [9, 0, 0, 0, 8, 0, 0, 0, 1],
    [0, 0, 0, 4, 0, 6, 0, 0, 0],
    [0, 0, 5, 0, 7, 0, 3, 0, 0],
    [0, 6, 0, 0, 0, 0, 0, 4, 0],
    [4, 0, 1, 0, 6, 0, 5, 0, 8],
    [0, 9, 0, 0, 0, 0, 0, 2, 0],
    [0, 0, 7, 0, 3, 0, 2, 0, 0],
    [0, 0, 0, 7, 0, 5, 0, 0, 0],
    [1, 0, 0, 0, 4, 0, 0, 0, 7],
]


x = sudoku_brute_force(grid)
print(x)
