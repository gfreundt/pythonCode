import random
import csv
import os
import time
import sys

sys.setrecursionlimit = 10 ** 8


def print_maze(maze):
    os.system("cls")
    for row in maze:
        line = []
        for c in row:
            if c == 1:
                symbol = "█"
            elif c in (2, 3):
                symbol = "O"
            elif c == ".":
                symbol = "."
            else:
                symbol = " "
            line.append(symbol)
        print("".join(line))


def creator(height, width, saturation, save=False):
    array = [[1] * width]
    for _ in range(height - 2):
        line = [1]
        for _ in range(width - 2):
            pixel = 1 if random.randint(1, 100) <= saturation else 0
            line.append(pixel)
        line.append(1)
        array.append(line)
    array.append([1] * width)

    array[0][1] = 2
    array[height - 1][width - 2] = 3
    if save:
        with open("maze.csv", "w", newline="", encoding="utf-8") as outfile:
            csv.writer(outfile).writerows(array)
    return array


def get_possible_destinations(maze, pos, been_there):
    moves = []
    for hops in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        coords = (pos[0] + hops[0], pos[1] + hops[1])
        # print(pos, coords)
        pixel = maze[coords[0]][coords[1]]
        if pixel == 0 and pixel not in been_there:
            moves.append(coords)
        elif pixel == 3:
            return -1
    return moves


def solve_maze(maze, pos, path, been_there, solved):
    if maze[pos[0]][pos[1]] == 3 or solved:
        return True
    destinations = get_possible_destinations(maze, pos, been_there)
    if destinations == -1:
        return True
    for dest in destinations:
        path.append(dest)
        maze[dest[0]][dest[1]] = "."
        solved = solve_maze(
            maze, pos=dest, path=path, been_there=been_there, solved=solved
        )
        if solved:
            return True
        else:
            maze[dest[0]][dest[1]] = " "
    return False


def load_maze(filename="maze.csv"):
    with open(filename, "r") as file:
        return [[int(i) for i in j] for j in csv.reader(file)]


if __name__ == "__main__":
    # maze = load_maze("maze3.csv")
    maze = creator(100, 100, 30)
    start = time.time()
    solved = solve_maze(maze, pos=(0, 1), path=[], been_there=[], solved=False)
    print_maze(maze)
    print(f"Can be solved: {solved} in {time.time()-start:.3f}")
