def validate_battlefield(field):
    # TEST 1: Total number of squares
    if sum([j for i in field for j in i]) != 20:
        return False

    # TEST 2: No diagonal squares respect to each other filled
    for r, row in enumerate(field[:-1]):
        for s, square in enumerate(row[:-1]):
            if square == 1 and field[r + 1][s + 1] == 1:
                return False
    for r, row in enumerate(field[:-1]):
        for s, square in enumerate(row[1:], start=1):
            if square == 1 and field[r + 1][s - 1] == 1:
                return False

    # TEST 3A: Count ship size > 1 and amount (horizontally and vertically)
    fieldFlipped = [[i[k] for i in field] for k in range(10)]
    navy = []
    for direction in (field, fieldFlipped):
        found, size = False, 0
        for r, row in enumerate(direction):
            if found and size > 1:
                navy.append(size)
            found, size = False, 0
            for s, square in enumerate(row):
                if square == 1:
                    found, size = True, size + 1
                else:
                    if found and size > 1:
                        navy.append(size)
                    found, size = False, 0
        if found and size > 1:
            navy.append(size)

    # TEST 3B: Count submarines
    for r, row in enumerate(field):
        for s, _ in enumerate(row):
            total = 0
            for x in range(max(0, r - 1), min(9, r + 1) + 1):
                for y in range(max(0, s - 1), min(9, s + 1) + 1):
                    if field[x][y] == 1:
                        total += 1
            if field[r][s] == 1 and total == 1:
                navy.append(1)

    return True if list(sorted(navy)) == [1, 1, 1, 1, 2, 2, 2, 3, 3, 4] else False


battleField = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
]

battleField = [
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 0, 1, 1, 1, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

print(validate_battlefield(battleField))
