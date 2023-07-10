import copy
import itertools
from tqdm import tqdm


class Grid:
    def __init__(self, grid_size, spos) -> None:
        self.size = grid_size
        self.blank_grid = [[0 for i in range(grid_size)] for j in range(grid_size)]
        self.grid = self.init_grid(copy.deepcopy(self.blank_grid), grid_size, spos)
        self.nummax = 0
        self.xmax = []
        self.ymax = []

    def init_grid(self, grid, n, spos):
        iloc = n // 2
        for pos in spos:
            grid[iloc - pos[0]][iloc - pos[1]] = 1
        # gprint("Starting Position", grid)
        return grid


def gprint(title, grid):
    g = len(grid[0]) * 3 - 1
    print(f'\n{" " + title + " ":+^{g}}')
    for i in grid:
        print(" ".join([f"{j:02d}" for j in i]).replace("00", ".."))


def rotate_grid(grid):
    rotated = copy.deepcopy(grid)
    size = len(grid[0]) - 1
    for y, line in enumerate(grid):
        for x, item in enumerate(line):
            rotated[size - x][y] = grid[y][x]
    return rotated


def reduce_grid(grid):
    igrid = [[grid[j][i] for j, _ in enumerate(grid)] for i, _ in enumerate(grid)]
    c = []
    for g in (grid, igrid):
        for line, line_data in enumerate(g):
            if [i for i in line_data if i != 0]:
                lower_limit = int(line)
                break
        for line, line_data in enumerate(g[::-1]):
            if [i for i in line_data if i != 0]:
                upper_limit = len(grid) - int(line)
                break
        c.append((lower_limit, upper_limit))

    new_grid = [
        [grid[c[0][0] + i][c[1][0] + j] for j, _ in enumerate(grid[c[1][0] : c[1][1]])]
        for i, _ in enumerate(grid[c[0][0] : c[0][1]])
    ]
    return new_grid, len(new_grid), len(new_grid[0])


def valid_squares(grid, next):
    G.ogrid = copy.deepcopy(G.blank_grid)
    result = []
    for x in range(1, G.size - 1):
        for y in range(1, G.size - 1):
            if grid[y][x] == 0:
                s = 0
                for i in range(x - 1, x + 2):
                    for j in range(y - 1, y + 2):
                        if (i, j) != (x, y):
                            s += grid[j][i]
                if s == next:
                    result.append((x, y))
                G.ogrid[y][x] = s
    return result


def solve(grid, n):
    for opt in valid_squares(grid, n):
        grid[opt[1]][opt[0]] = n
        solve(grid, n + 1)
        if n > G.nummax:
            G.nummax = int(n)
            G.final_grid = copy.deepcopy(grid)
        _, xmax, ymax = reduce_grid(grid)
        G.xmax.append(xmax)
        G.ymax.append(ymax)
        grid[opt[1]][opt[0]] = 0


def generate_configs(n, xmax, ymax):
    if n == 2:
        return [[(-2, -2), (0, 0)], [(-2, 0), (0, 0)], [(0, 1), (0, 0)]]
    if n == 3:
        return [[(-1, -1), (1, 1), (1, -1)], [(-1, -1), (1, 0), (1, -1)]]
    if n == 4:
        return [
            [(-1, -1), (1, 1), (1, -1), (1, 0)],
            [(-1, -1), (1, 0), (1, -1), (0, 1)],
        ]


def gc(n, xmax, ymax):
    size = max(xmax, ymax)**2
    # create list of all possible combinations and only append with correct n
    #k = [list(i) for i in tqdm(itertools.product(range(2), repeat=size)) if sum(i) == n-1]
    s = []
    for i in range(size):
        for j in range(i,size):
            if i != j:
                t = [0 for _ in range(size)]
                t[i] = 1
                t[j] = 1
                s.append(t)
    return s
    # add coordinate (0,0)
    #for i in s:
    #    i[size//2] = 1
    # filter all that not have correct n after add
    k = [i for i in s if sum(i) == n]
    return k

def gc2(n, xmax, ynax, starting, size, d):
    if d > n:
        return
    else:
        d += 1
    for i in range(starting, size):
        


def main(n, x=0, y=0):
    global G
    xmax, ymax, snummax = [], [], []
    configs = generate_configs(n, x, y)
    for spos in configs:
        G = Grid(11, spos)
        solve(G.grid, 2)
        xmax.append(max(G.xmax))
        ymax.append(max(G.ymax))
        snummax.append(G.nummax)
        # print(f"Max N: {G.nummax} -- Max Grid Size: {max(G.xmax)},{max(G.ymax)}")
        # gprint("Best Result", reduce_grid(G.final_grid)[0])
    accum_results.append(
        {"Q": n, "MaxN": max(snummax), "GridXmax": max(xmax), "GridYmax": max(ymax)}
    )
    return max(xmax), max(ymax)


v = gc(2, 3, 3)
print(v)
quit()

accum_results = []

x, y = main(2, 0, 0)
x, y = main(3, x, y)
x, y = main(4, x, y)
print(accum_results)

t = copy.deepcopy(G.grid)
gprint("Rotate", t)
for i in range(4):
    t = rotate_grid(t)
    s = reduce_grid(t)[0]
    gprint("Rotate", t)
    gprint("Rotate reduced", s)
