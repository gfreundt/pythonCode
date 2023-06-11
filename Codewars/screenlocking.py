def patterns():
    EXP = {
        "AG": "D",
        "AC": "B",
        "AI": "E",
        "BH": "E",
        "CI": "F",
        "CG": "E",
        "CA": "B",
        "DF": "E",
        "FD": "E",
        "IA": "E",
        "IF": "C",
        "IG": "H",
        "HB": "E",
        "GA": "D",
        "GC": "E",
        "GI": "H",
    }
    return {(k + j): "" for k in "ABCDEFGHI" for j in "ABCDEFGHI" if k != j} | EXP


def valid_move(c, n, moves):

    # print("in", c, n, moves)
    if c == n:
        return False
    if [i for i in "ABCDEFGHI" if moves.count(i) > 1]:
        return False
    # if INDEX[c + n] != "":
    #     return False

    return True


def solve(current_letter, length, moves):

    print("top", moves, valid_combos)
    input()

    if len(moves) == length:
        valid_combos.append("".join(moves))
        return

    for next_letter in "ABCDEFGHI":

        # print(
        #     f"{current_letter=} {next_letter=} {valid_move(current_letter, next_letter, moves)}"
        # )

        if valid_move(current_letter, next_letter, moves):
            moves.append(next_letter)
            solve(next_letter, length, moves)
            moves = moves[:-1]
        # moves = moves[:-1]


def countPattersFrom(firstPoint, length):
    if length > 9 or length < 1:
        return 0
    used = [firstPoint]


INDEX = patterns()
valid_combos = []

start = "E"
steps = 3


v = solve(start, steps, [start])
print(v)
print(len(v))
