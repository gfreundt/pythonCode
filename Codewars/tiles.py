from copy import deepcopy as copy
import sys

sys.setrecursionlimit(500000)


class Init:
    def __init__(self, ar) -> None:
        self.exit = False
        self.sequence = [ar]
        self.control = []
        self.answer = []
        self.c = 0


def slide_puzzle(ar):
    def print_puzzle(ar):
        for i in ar:
            print(i)
        # print("-" * (len(ar) * 3))

    def print_solution():
        for array in vars.sequence:
            print_puzzle(array)
            print("  |\n  V")
        print(f"Steps: {len(vars.sequence)}")

    """ def is taking borders //// fix!!"""

    def select_possible_pieces(ar, control):
        length = len(ar)
        empty_pos = get_empty_pos(ar)
        pieces_pos = []
        for r, c in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (
                r + empty_pos[0] < length
                and c + empty_pos[1] < length
                and r >= 0
                and c >= 0
            ):
                pieces_pos.append((r + empty_pos[0], c + empty_pos[1]))

        print(pieces_pos)

        arrays = []
        for piece_pos in pieces_pos:
            ar_temp = switch_pieces(ar, piece_pos)
            if flat(ar_temp, string=True) not in control:
                chaos = eval_chaos(ar_temp, final_puzzle)
                arrays.append([chaos, piece_pos])
        return (j[1] for j in sorted(arrays, key=lambda i: (i[0], i[1])))

    def switch_pieces(ar, piece_pos):
        arx = copy(ar)
        empty_pos = get_empty_pos(ar)
        arx[empty_pos[0]][empty_pos[1]], arx[piece_pos[0]][piece_pos[1]] = (
            arx[piece_pos[0]][piece_pos[1]],
            arx[empty_pos[0]][empty_pos[1]],
        )
        return arx

    def get_empty_pos(ar):
        return [(k, n) for k, r in enumerate(ar) for n, c in enumerate(r) if c == 0][0]

    def flat(ar, string=False):
        if not string:
            return [str(j) for i in ar for j in i]
        else:
            return "".join([str(j) for i in ar for j in i])

    def get_final_puzzle(ar):
        final_puzzle = [
            [i * len(ar) + c for c in range(1, len(ar) + 1)] for i, _ in enumerate(ar)
        ]
        final_puzzle[-1][-1] = 0
        return final_puzzle

    def eval_chaos(ar, final_puzzle):
        f = sum(
            [0 if int(i) == int(j) else 1 for i, j in zip(flat(ar), flat(final_puzzle))]
        )

        g = sum([(len(ar) - i - 1) for i in get_empty_pos(ar)])
        return f, g

    def recursive(ar):

        # vars.c += 1
        # print("in", vars.c)

        # print(len(vars.sequence), vars.control, vars.exit)

        vars.control.append(flat(ar, string=True))

        print_puzzle(ar)
        input()
        # print(f"{depth=}")
        # print(f"{control=}")

        if ar == final_puzzle:
            print("success!")
            print_solution()
            vars.exit = True
        else:
            for piece_pos in select_possible_pieces(ar, vars.control):
                # print("using piece_pos", piece_pos)
                # print("ar previous to switch", ar)
                ar = switch_pieces(vars.sequence[-1], piece_pos)
                # print(ar, control)
                vars.sequence.append(ar)
                recursive(ar)
                if vars.exit:
                    return
                print("backtrack in for")
                vars.sequence = vars.sequence[:-1]
        # print("backtrack outside for")
        # vars.sequence = vars.sequence[:-1]

    final_puzzle = get_final_puzzle(ar)
    recursive(ar)

    while True:

        arrays = []

        print_puzzle(ar)

        if ar == final_puzzle:
            print("success!")
            quit()

        for piece_pos in select_possible_pieces(ar):
            ar_temp = switch_pieces(ar, piece_pos)
            if flat(ar_temp, string=True) not in control:
                chaos = eval_chaos(ar_temp, final_puzzle)
                arrays.append([chaos, ar_temp])
        best = sorted(arrays, key=lambda i: (i[0], i[1]))
        if best:
            best = best[0]
            ar = copy(best[1])
            control.append(flat(ar, string=True))
        else:
            print("failure!")
            quit()


p = [
    [3, 7, 14, 15, 10],
    [1, 0, 5, 9, 4],
    [16, 2, 11, 12, 8],
    [17, 6, 13, 18, 20],
    [21, 22, 23, 19, 24],
]

# p = [[4, 2, 3], [1, 5, 6], [7, 8, 0]]
# p = [[10, 3, 6, 4], [1, 5, 8, 0], [2, 13, 7, 15], [14, 9, 12, 11]]
# p = [[1, 2, 3, 4], [5, 0, 6, 8], [9, 10, 7, 11], [13, 14, 15, 12]]

p = [[1, 0, 3], [4, 5, 6], [7, 2, 8]]

vars = Init(p)
slide_puzzle(p)
