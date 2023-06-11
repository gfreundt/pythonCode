import copy


def find_first_letter(grid, letter):
    return [
        (x, y)
        for y, row in enumerate(grid)
        for x, col in enumerate(row)
        if col == letter
    ]


def check_neighbours(grid, pos):
    neighbors = []
    for x in range(max(0, pos[0] - 1), min(len(grid) - 1, pos[0] + 1) + 1):
        for y in range(max(0, pos[1] - 1), min(len(grid) - 1, pos[1] + 1) + 1):
            if grid[y][x] != "@":
                neighbors.append((x, y))
    return neighbors


def solve(grid, pos, word, step, solved):
    grid[pos[1]][pos[0]] = "@"
    neighbours = check_neighbours(grid, pos)
    if step - 1 == len(word) - 1:
        return True
    for let in neighbours:
        if word[step] == grid[let[1]][let[0]]:
            solved = solve(grid, let, word, step + 1, solved)
    return solved


def find_word(grid, word):
    original_grid = copy.deepcopy(grid)
    allpos = find_first_letter(grid, word[0])
    if len(word) == 1:
        return True if allpos else False
    if allpos:
        for pos in allpos:
            grid = copy.deepcopy(original_grid)
        return solve(grid, pos, word, step=1, solved=False)
    else:
        return False


def f1():
    testBoard = [
        ["E", "A", "R", "A"],
        ["N", "L", "E", "C"],
        ["I", "A", "I", "S"],
        ["B", "Y", "O", "R"],
    ]

    print(find_word(testBoard, "F"), True, "Test for C")
    print(find_word(testBoard, "EAR"), True, "-- Test for EAR")
    print(find_word(testBoard, "EARS"), False, "-- Test for EARS")
    print(find_word(testBoard, "BAILER"), True, "-- Test for BAILER")
    print(
        find_word(testBoard, "RSCAREIOYBAILNEA"), True, "-- Test for RSCAREIOYBAILNEA"
    )
    print(find_word(testBoard, "CEREAL"), False, "-- Test for CEREAL")
    print(find_word(testBoard, "ROBES"), False, "-- Test for ROBES")


f1()
