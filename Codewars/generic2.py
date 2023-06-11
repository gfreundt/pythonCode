def knight_path(start, end):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    moves = [start]
    while start != end:
        # print(f"{start=} {dx=} {dy=}")
        # input()
        xdir = -1 if end[0] < start[0] else 1
        ydir = -1 if end[1] < start[1] else 1
        # knight close to end
        if abs(dx) == 1 and abs(dy) == 1:
            dx = -dx
            dy = 2 * dy
        elif abs(dx) >= abs(dy):
            dx += 2 * xdir
            dy += ydir
        else:
            dx += xdir
            dy += 2 * ydir
        start = (end[0] + dx, end[1] + dy)
        moves.append(start)

    return moves


# f = knight_path((-5, -7), (8, 7))
f = knight_path((0, 0), (1, 3))
print(f)
