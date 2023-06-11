from copy import deepcopy as copy


def printx(x):
    for i in x:
        print("".join(i))


def space_adjacent_test(r, c, m, test_for):
    return any(
        [
            m[r + move[0]][c + move[1]] == test_for
            for move in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ]
    )


def dry_ground(terrain):
    line = " " * len(terrain[0])
    m = [f" {i} ".replace(" ", "@") for i in [line] + list(terrain) + [line]]
    m = [[i for i in j] for j in m]
    height = 0
    response = []

    while "^" in "".join(["".join(i) for i in m]):

        # add number of dry spaces to answer
        response.append(
            len("".join(["".join([i for i in j if i != "-"]) for j in m]))
            - (2 * (len(m) + len(m[0])) - 4)
        )
        print(f"Day {height} {response}")
        printx(m)
        m2 = copy(m)
        # process mountain spaces (skip first round)
        if height > 0:
            for row in range(1, len(m) - 1):
                for col in range(1, len(m[0]) - 1):
                    if m[row][col] == "^" and space_adjacent_test(
                        row, col, m, test_for="-"
                    ):
                        m2[row][col] = "-"
        print("After Process Mouhntain")
        printx(m2)
        # process valley spaces
        previous_wet_spaces, wet_spaces = 0, 1
        while wet_spaces != previous_wet_spaces:
            previous_wet_spaces = len(
                "".join(["".join([i for i in j if i != "-"]) for j in m2])
            )
            for row in range(1, len(m) - 1):
                for col in range(1, len(m[0]) - 1):
                    if m2[row][col] == "@" and space_adjacent_test(
                        row, col, m2, test_for="-"
                    ):
                        m2[row][col] = "-"
            wet_spaces = len("".join(["".join([i for i in j if i != "-"]) for j in m2]))
        height += 1
        m = copy(m2)

    return response


terrain = (
    "  ^^^^^^             ",
    "^^^^^^^^       ^^^   ",
    "^^^^^^^  ^^^         ",
    "^^^^^^^  ^^^         ",
    "^^^^^^^  ^^^         ",
    "---------------------",
    "^^^^^                ",
    "   ^^^^^^^^  ^^^^^^^ ",
    "^^^^^^^^     ^     ^ ",
    "^^^^^        ^^^^^^^ ",
)

# print(space_adjacent_blank(3, 3))
# quit()

f = dry_ground(terrain)
print(f)
