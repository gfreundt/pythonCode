class Success:
    def __init__(self) -> None:
        self.exit_code = -1
        self.entry_visited = []
        self.exit_visited = []


def available_moves(maze, pos, visited):
    x, y = pos
    response = []
    # N, S, W, E
    for ox, oy in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
        # check if out of bounds
        if (0 <= ox < len(maze)) and (0 <= oy < len(maze)):
            # check if wall ("W")
            if maze[oy][ox] == ".":
                # check if already visited
                if (ox, oy) not in visited:
                    response.append((ox, oy))
    return response


def solve(maze, pos, end_pos, visited, solved):
    # _ = input()
    if pos == end_pos:
        return True
    visited.append(pos)
    moves = available_moves(maze, pos, visited)
    for move in moves:
        # if move not in visited:
        if move in visited:
            break
        solved = solve(maze, move, end_pos, visited, solved)
        if solved:
            break
    return solved


def thread_function(maze, pos, end_pos, visited):
    solved = solve(maze, pos, end_pos, visited, False)
    process.exit_code = 1 if solved else 0


def path_finder(maze):
    import sys
    import threading

    sys.setrecursionlimit(15000)
    global process
    process = Success()
    maze = maze.split("\n")

    init_coord = (0, 0)
    end_coord = (len(maze[0]) - 1, len(maze) - 1)

    # start ENTRY forward thread
    entry_thread = threading.Thread(
        target=thread_function, args=(maze, init_coord, end_coord, [init_coord])
    )
    entry_thread.daemon = True
    entry_thread.start()

    # start EXIT backward thread
    exit_thread = threading.Thread(
        target=thread_function, args=(maze, end_coord, init_coord, [end_coord])
    )
    exit_thread.daemon = True
    exit_thread.start()

    # wait for either process to produce a True/False result and return value
    while process.exit_code == -1:
        pass
    return True if process.exit_code == 1 else False


maze = "\n".join([".W...", ".W...", ".W.W.", "...W.", "...W."])
# maze = "\n".join([".W...", "W....", ".....", ".....", "....."])
maze = "\n".join([".W...", ".W...", ".W.W.", "...WW", "...W."])
maze = "\n".join([".W...", ".W...", ".W.W.", "...WW", "...W."])

maze = "\n".join(
    [
        "..W....WW.WWW..W..W..W.W...W...W.W...W..W..W.W.W.....W.........W.W.W..W....W..W...W....W.WW..WW.",
        ".......WW.....WW...............WW.W..W..W...W.WW.W.....W..W.W..........WWW...W.W.W...W..W.......",
        ".WW....W..W.W..W.W..W......W..........W.W................WW.W..W........W.....W......W.WW..WWW..",
        "..WWW...W....................W....W.WWWW...WW......W.WWWW..W.W..WWW.W..W......WWWW..W.......W.W.",
        "......W...W.............W......W.....W.W.W....W......W......W....W....W............WW...WW..WWW.",
        "...WW.W.W..WW..W..W.....WWW..WW........W..W..W..W.....W.W.W.....WW.WWW..WWWW...W......W....W...W",
        ".W....WW..WW.WW.....WW......WWW.....W.WW...........W.W........W...W....W.W.W...W.....W..WW....W.",
        "..W...W.....W.W.........WW.......W.W..W.....WW.W..WW....W.W......W...W.WW.WW......W..W.W...W.WW.",
        "W..W....W...W.........W.W.WW.....W......W.W........WW.W.W...WW...WWW..W.W......W......WW.W......",
        "W.W....WW.......W.........W..............WW...W.....W.......WW......W..W..WW.WW..W.....W...WW...",
        "..W..W.....W..W.W...W..........W.W...W.WWW.....W..........W.....WW.........WWW...W....W.....W...",
        "WW..W.W.....W.WW...W....W.W.......W...WWW....W....W..WW...W.W.......W....W.......WW..W.W.W.W.W..",
        "..W.WWWW..W.W.W......WW..WW........W....W..W.W......W...W..W......WWWW.....W..........WWW.W.W..W",
        ".WW.W.....WW....W.........W.W.WW...WW.W.W...W..W.W......W.W..W.....W........W.W.........W.W...WW",
        "W...W.W.....WWW.WW..W..WW.WW....WW....W......W...W..WW....WWW..W......WW......W..WWW..W...WW....",
        "....W..WW...WW...WW..W.W.........WW.W.W...W.W...W..WWW...........W..W..W.....W.W..W.W.W........W",
        ".....W....W.W...W.WW.......W..W.W.W.WW.........W.W.W..W......W..W.......WW....W..W...W.W...W...W",
        "W..WW...W....W.....W.WWW..W..W...WW...WWW.W...WWW........WW.......W...WWW...W.W.....W........W..",
        "W.WW.......W.WWW.W.........W..W.......W.....WW...WW.........W.WWW..WW...W....W.......WWW.....W.W",
        "...W....W...WW.W..WW....WW..W....W.W..........WW...W.WW...W...WW.W.........W..W.....W...WWW...WW",
        "...WWWW..W..W.WW...W...WWWWWW.W.W....W........W.W.............W..WWW.WWW..W..WWW.WW....WW..W..WW",
        "W.W..W.W.....W......W.......W...W..WW.....W...W.....W.........WW....W.WWWWW..W.W.....W.WWW.....W",
        "W...W...WWW........WW.W..WW..W........W.W........W.WWWWWW.W..W.WWWW....W.W..W.W..WW..W....W.WW..",
        "..............W....WW........WWW...W..W..W.W.......W..W.W.......W....W....WW.........WW...W..W..",
        "...W.W..................W.W.WW..W.....WWW....W...W..W....W.......W..W..WW..W..WW....WW.W....W..W",
        "..WWW...W...W.W..W......W........W.WWWW..........WW.W..W..........WW.WW.W..W..W.....W......W.W..",
        "W...W...W.WWW....W.WW..WW.......WWWW...WWW.WWW.......W.W....W....W.......W.W.....WWW...WW....W.W",
        "W.W....W..W.WW..WWW.W..W....W.WW...W.W...W.......WW....W.WW.............W...WW.WW....W.WWW......",
        ".....W.WW...W.....WWW............WWWW....W.W..W..W...W.WW..W......WW.W.W..W...........W.W....WW.",
        "W.W..W.W.WW.WW....WW..WW.....WWWW.......W.....W.......WWW..WWWW..W.W...WW....W.W......W..W.WW...",
        ".W....W......W..W....W.W.W.WW.W.WW..W.WWW.W.............WW....W.W...WWW.....WW..W.W.....WW..W...",
        "W.W............W..W..W...W..W.W........W...WWW...W.W.W..WW.W.......WW...W....WW...WWWW.W.W....WW",
        ".WW.....W......WW.W...W.W....W.W..W..W.W.W.WW...W..W..WW..WW....W....W...W...W.WW....W..W.......",
        "....WW.W......W..W.W......W.....W...W......WW....WW.W.....WW...W....W..W.......W......WW..WW....",
        ".WWW...WW..WWW.............WW..W.W..W.WW...W.....W...W.WW..WW.....W....W.W..W.......WWW....W.W..",
        "W.W..WW...W..W..........W.W......W....................WW......W...W......W..W..W...W...WW...WWW.",
        ".....W.W..WWWW....W...........W..W..W...W.W.W......WW.WW........WW..W....W.W...W.W.....W......W.",
        "....W.W....W.....W........W...W.....W......W..W..........WW...WW.WW.W...W.WW.W..W.WW...W.W....W.",
        "........W.WW.......................WW....WWW...W.W......W..W..........W.WWW..WWW.........W.W....",
        ".W......W......W.W...W.....W.....W..................WW.WW......................W..W......W..W...",
        "...............WW.W.W.......W.WW.....WWWW.......W..............W..WWW...W.W.W...W.WW...WW....WWW",
        ".W..W...WW....WW...............W........WW...W..W..W................W..........W.W.W..WWWW......",
        ".W.W...W.W....WW..W.............WWW..WWW..W.W.WWW..WW.........W..WW....W...........W.W..W.W..W..",
        "..WW.....WW.....W........WW..WW.W....WW....W.W....W..W...W...W.WW....W.....W..W....WW.W.WW.W....",
        "..W.W.W....W....WW.......W.W..W...........WWW...WWWW...W...W..W...WW.WW.W.WW.W.W.........WWW...W",
        "...................WW...W.....W...W.............W...WW.......W..W...W......W.W....W....WW.......",
        "....W.WWW.....WW.......W.WW.WWW.W.......WW.W.W.WW.W.....W.W....W........WWW........W.....WWW...W",
        "W......W..........W.......WW..W......W..W.W.....WWW...W.W..W............W.W...W..WW....WW.W.....",
        "W........W.......W....W.....W.W.WW..W..W..WW..W...W.....W.W.....W..............WW...W....W.WW..W",
        "......WW.W.W....W.W.W..W....W.WW.............WW.WW....W..W...W...W..WW.......WWW.W...W......W...",
        "...W...W...WW.W.W..W......W.W....W.W.......W..W..WWW.WWWW.W...W..W.....W..W...W...W.W........W..",
        ".W..W...W...W..W....W.WW....W.W........W.....WW.........W......W.....W.W.WW...W...W..W..W..W.W..",
        ".....W......W..WW.W...W.WW.W..W....WW...W......W..W...........W.....W.W...W..W..W..W..W.W.WWW...",
        "......WW.WW.....WWW....................WW.W.......W..W.....W..W...WW.W..W..W.W.W.......W.WW.W..W",
        "........W..W....WW.....W.W...W...W........W.W.W.W...W..W..W.W.WW..W.W.......WW.W....W...........",
        "W....W...WWWW.W.........W..W...WW.......WWW.W......W..W....W.....WW.W.W.....W...W..W..W.W..W....",
        "W..W.WW....W...W....W..W.W....WW..W.........WWW.......W....WW..W.......W............W.W.WW......",
        "...WW......W.......W.W....W..WWW.......WW...W..W..W.........W.W..W...W..W...W.W...........WW.W..",
        ".......W..WWW.WW........WW..W.WW.W.....WWW......WW..WW.W........W...W.....WWW.W..W..W...W..WW..W",
        ".....W.W..WW...W......W.WW.W.W...WW....WWW...W.WW...WW......W...WWW.........W........W..W....W..",
        "...W..WWW..WWW..W.....W.W........W..W.W.W.W.WW.W......W.WW.....W........W.W.WW....W.W...W.W.W..W",
        "...WW..WWWWW.W........WW...W..W.W..W.W..............W..WWW.W......W......W..WW.W.......W..W....W",
        "W..W..W.....W..WW...W..WW.....W..W...W.....WWW.W....WW....W..W...W.W...W...........WWWW.W...W...",
        "....WW.WW..W.....W...W..........W.W..WW......WW...............W....W........WW....W..........W.W",
        "WWWW.......W.WWW.WWW...W.W..WW.WW..W.........W..W.......WWW...WW.W.W...WWW.............W..WWW..W",
        "..WW.......W......W..W...W.W.WWW...W.....W..W..........W...........W.WWW.W..WW..W..........WW.W.",
        "W......W.W..WWW.WW..W...........W.WW.W.......WW..W..WW.W.W....W....WW.......WW..W...W.W.....W.W.",
        "W....W..W...W......W.WWW...W....W.W.W.WW...W..W..W.WW....W..WWW......W..W.W.......W.......W.W...",
        "..WW.......W.WW..W...WW.W.......W...WW..WW..WWWW..W......WW............W.W..WW.........W.WW....W",
        "..W...WW...W.....W.W....WWW..W......W..WW.WWW......W.W..W...W..W.W.....WW.WWW.W....W.WW.....WW..",
        "W.........W.W.W......W...W..WW.W..WW..W..W.W..W.................WWW.....W..W....WWW....W.W.W...W",
        ".W..W..W.W.W..W.......WW.W..WW...........W.W....W.W.....WW.............W.W....W.W.....W.....W..W",
        "W....W....W....W.WW.........W.W.WW.W.W.W....WWW......W......W.....W..W.....WW.....W..W......W...",
        "WW..WWW.......W.W.W..W....WW..W....W...W....WW....W.W....WW....W..WW.....W........W.......W...WW",
        "...WWW..W.W.....W..WW.....WW...........W........WW...W...W...W..W.....W.W.......W.WW.WW...W.....",
        "......W..W...WW..W....WW..W.W.W...W..WWW..W...W......W...W.WWWWWW......W.......WW...W.WW........",
        ".W......W...W..W.................W.......WWWW........W.....W..W.WW....W..W.........WW.W........W",
        "WW..W.WW.WWWW......WWWWW.W.WWWWWW......W....W.......W..W.W..WW.WW....W.W.W.W..WW..W.......W.....",
        "...WW..W.....WWW....W..W.WWW...WWW...WW...............WW.W...W..W.WW.....W..W...WWWW.W.WW....W..",
        "W...W........WWWW...W.WWWW..W..W.WW..WW...........WW.W.......W............W..W.............W.W..",
        "......W.W.W.W........W...W.WW...WW....W..W.W..W...WW.WW......W...WWW.W...W........W..W..W..W..WW",
        "....W............W.W.W.W.......W.W.W.WW.W..WW.W.....WW........W......WW.....W.......WWWWW...W.W.",
        ".W..W.....W.......W.........W....W...........W..WW.W.....W........W...W.......WWW.....W...WW.W..",
        "WW...WW....WW......W.W..W.......W.W.WWW.....W..W..W..W...W..W..W.W..W....W.W..W...W.WW.WW.W.....",
        "..W.......W.............WWW..W.W..W...W.W.......WW..W...W....W..W.W..W..W...W.....W..WW....W..W.",
        ".W..W.W....WWW...W....W..W....................WW..WW.........W..WW....W....WW.....W.W.W.W......W",
        "WW..W.W...W.......W.........W....W.....W..W...W....W.W.....W.....WW..W.........W..W.........W..W",
        "..W..WW.W.W...W.......W......W.....W...W.W.W.W....W.........W.WWW.W.W.........W.W......W.WW..W.W",
        "W..W.WWW.....W..WWW..W...W......W.W........W.W.WWW............WW...W.W.......W..W.W.WWW.W.....W.",
        "...W..W......W....WW......WWW.W.W....WW..W...W........W..W..W.W.........W..W..W..W.....WW..W....",
        "W...WWW..W.W................W.W.....W..W....WW.W..W.W..WW.......W.....W...W..W..W..WW...........",
        "WWW....WWW.W...WW..W..WW.W...WW.W..........WWW.....W.......W...W..W...........W........W.WW.....",
        ".WW..........WWW...W....W..WWWW.W..WW..........W..W..W.....W...W.W...W....WW....W.W..W..W..WW...",
        "..WW.W.W.WW.W.W...W....W..W....W.W.....W...............WW...W...W....W....WWWW.WWW............WW",
        "W.W.W.W.W..W.......W..W...W...WW..W.....WW........W..W.......W.....W.W.........WWWW....W...W..W.",
        "W...W.............W..........W.......W....WW.WW...W...WW.WW..W.WW....WW..WW.W...W......WWW..WW..",
    ]
)
maze = "\n".join(
    [
        ".W.WW.W..WWWW...W...W......W....W",
        "WW..........W...WW.W...W...W.....",
        "W.....W...........W...WWWW.......",
        ".W..W.W........W........W....W...",
        "..WW....W.W.WW...W.....W..W..WW..",
        "........W..W...WW......W....WW.W.",
        ".W....W...WW.....W....W.W..W.W.W.",
        "W.......W...W..WWW....WW.W..WW...",
        "...W..W.W..W....W.....W...W.W..W.",
        ".W.W...W..W...WW.W.W...WWW..W...W",
        "....WWWW.......W............W...W",
        ".W..W...WWW.W...WW.........WW..W.",
        ".....W......W.W..W.....W.........",
        ".W..WW.....W...W.WW....W..W..W.WW",
        ".WW..W.W.W.W.........W..W.....WW.",
        "....W...W...W....W...W.W.W.W.W...",
        "..W..W.WW.......W.....W...W......",
        "W......W.W.W...WWW.........W...WW",
        "...W..W.......W.W.........W......",
        "W........W.W................W.W..",
        "...WW.W..W...WW.W....WW.W.W..W..W",
        "..WWW....W..W.W................WW",
        ".W..........W.W.W..WW.W.W.W....W.",
        "..WW.......WW..W...WW..........W.",
        ".....W...W.W.W.......WW......W...",
        ".........W..W...WWW.WW..WW......W",
        "...W..WWWW.........W...........W.",
        ".....W...W...WW.....W.W..W.......",
        ".W...W..W...W....W.....WWW..W...W",
        "W..W...W..W...W..WW..W........W..",
        "...W..W..W...W..WW.....W..W.....W",
        ".W......W..WW.....W...WW.........",
        "..........W.W..W.W....WW......W..",
    ]  # is False
)

print(maze)
print(path_finder(maze))
