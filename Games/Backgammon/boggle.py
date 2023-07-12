import copy


def find_word(grid, word):
    word = word.upper()
    starting_coords = [
        (x, y)
        for y, _ in enumerate(grid)
        for x, _ in enumerate(grid[0])
        if grid[y][x] == word[0]
    ]
    if not starting_coords:
        return False
    original_grid = copy.deepcopy(grid)
    for coords in starting_coords:
        print(f"Starting from {coords}")
        if solve(grid, word[1:], 0, coords, original_grid):
            return True
    return False


def solve(grid, word, letter_pos, coords, original_grid):
    print(grid, word, letter_pos, coords)
    if letter_pos == len(word):
        return
    x, y = coords
    grid[y][x] = "@"
    list_of_neighbors = get_neighbors(grid, coords, word[letter_pos])
    if not list_of_neighbors:
        return False
    else:
        for neighbor in list_of_neighbors:
            solve(grid, word, letter_pos + 1, neighbor, original_grid)
            return
    return True


def get_neighbors(grid, coords, letter):
    x0, y0 = coords
    s = []
    for x in range(max(0, x0 - 1), min(len(grid[0]) - 1, x0 + 1) + 1):
        for y in range(max(0, y0 - 1), min(len(grid[0]) - 1, y0 + 1) + 1):
            # print(x0, y0, x, y)
            if (x0, y0) != (x, y) and grid[y][x] == letter:
                s.append((x, y))
    return s


grid = [
    ["I", "L", "A", "W"],
    ["B", "N", "G", "E"],
    ["I", "U", "A", "O"],
    ["A", "S", "R", "L"],
]

a = find_word(grid, "gnlibc")
print(a)
