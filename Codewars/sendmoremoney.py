from tqdm import tqdm


def unpack(phrase):
    must_be_one = (
        phrase[-1][0] if len(phrase[-1]) > max([len(i) for i in phrase[:-1]]) else None
    )
    vars = set([j for i in phrase for j in i])
    return {i: -1 for i in vars}, set([i[0] for i in phrase]), must_be_one


def test(phrase, vals, not_zero, must_be_one):
    if must_be_one and vals[must_be_one] != 1:
        return False
    for t in not_zero:
        if vals[t] == 0:
            return False
    pre_total = sum([get_value(i, vals) for i in phrase[:-1]])
    total = get_value(phrase[-1], vals)
    return True if total == pre_total else False


def get_value(word, vals):
    return sum([vals[i] * 10**-k for k, i in enumerate(word, start=-len(word) + 1)])


def main():
    vals, not_zero, must_be_one = unpack(phrase)
    for val in tqdm(range(10 ** len(vals))):
        string = f"{val:0{len(vals)}d}"
        val_list = [i for i in str(string)]
        repeated = [i for i in val_list if val_list.count(i) > 1]
        if not repeated:
            val = {i: int(string[k]) for k, i in enumerate(vals)}
            if test(phrase, val, not_zero, must_be_one):
                return val


phrase = [
    "SEND",
    "MORE",
    "MONEY",
]  # {'E': 5, 'S': 9, 'Y': 2, 'N': 6, 'D': 7, 'M': 1, 'O': 0, 'R': 8}
# phrase = ["TO", "GO", "OUT"] # {'G': 8, 'T': 2, 'U': 0, 'O': 1}
# phrase = [
#     "SO",
#     "MANY",
#     "MORE",
#     "MEN",
#     "SEEM",
#     "TO",
#     "SAY",
#     "THAT",
#     "THEY",
#     "MAY",
#     "SOON",
#     "TRY",
#     "TO",
#     "STAY",
#     "AT",
#     "HOME",
#     "SO",
#     "AS",
#     "TO",
#     "SEE",
#     "OR",
#     "HEAR",
#     "THE",
#     "SAME",
#     "ONE",
#     "MAN",
#     "TRY",
#     "TO",
#     "MEET",
#     "THE",
#     "TEAM",
#     "ON",
#     "THE",
#     "MOON",
#     "AS",
#     "HE",
#     "HAS",
#     "AT",
#     "THE",
#     "OTHER",
#     "TEN",
#     "TESTS",
# ]
# phrase = ["HOCUS", "POCUS", "PRESTO"] # {'C': 8, 'P': 1, 'R': 0, 'T': 7, 'H': 9, 'S': 6, 'O': 2, 'U': 3, 'E': 5}
answer = main()
print(answer)
