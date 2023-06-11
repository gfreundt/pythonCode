from itertools import permutations as perm
import time


def banana(s):
    if len(s) < 6:
        return []
    total = []
    dashes = set(list(perm(["-"] * (len(s) - 6) + [" "] * 6)))
    for config in dashes:
        word = "".join(["-" if i == "-" else s[k] for k, i in enumerate(config)])
        if "".join([i for i in word if i != "-"]) == "banana":
            total.append(word)
    return set(total)


def ban(s):
    end = len(s)
    for d1 in range(0, end - 2):
        for d2 in range(d1 + 1, end - 1):
            for d3 in range(d2 + 1, end):
                test_word = "".join(
                    ["-" if k in (d1, d2, d3) else s[k] for k, _ in enumerate(s)]
                )
                if "".join([i for i in test_word if i != "-"]) == "banana":
                    total.append(word)
                print(test_word)


def b(s):
    def creator(k):
        if -1 not in dash:
            test_word = "".join(["-" if k in dash else s[k] for k, _ in enumerate(s)])
            if "".join([i for i in test_word if i != "-"]) == "banana":
                total.append(test_word)
        if k == len(s) - 6:
            return total
        for x in range(k, k + 7):
            dash[k] = x
            creator(k + 1)
        return total

    dash = [-1 for i in range(len(s) - 6)]
    total = []
    return set(creator(0))


def bananas(s):
    def looper(dash_pos, pos, accum):
        a = "".join(["-" if k in dash_pos else i for k, i in enumerate(q)])
        b = "".join(["" if i in "-" else i for i in a])
        if b == "banana" and -1 not in dash_pos:
            accum.append(a)
        if pos == len(dash_pos):
            return accum
        start_num = dash_pos[pos - 1] + 1
        for x in (i for i in valid_pos if i >= start_num):
            dash_pos[pos] = x
            looper(dash_pos, pos + 1, accum)
        return accum

    # no "b" closer than 6 characters to the end of string
    q = ["-" if i == "b" and k > len(s) - 5 else i for k, i in enumerate(list(s))]
    # no "n" closer than 3 characters to beginning of string
    q = ["-" if i == "a" and k < 1 else i for k, i in enumerate(q)]

    # clean leading
    p = 0
    for f in ("b-", "ab-"):
        while q[p] not in f:
            q[p] = "-"
            p += 1
        p += 1

    # clean trailing
    p = len(q) - 1
    for f in ("a-", "an-"):
        while q[p] not in f:
            q[p] = "-"
            p -= 1
        p -= 1

    valid_pos = [i for i in range(len(q)) if q[i] != "-"]

    # basic check
    if s.count("a") < 3 or s.count("n") < 2 or s.count("b") < 1:
        return set([])

    init_dashes = [-1] * (len(valid_pos) - 6)
    return set(looper(init_dashes, 0, []))


# start = time.perf_counter()
# d = bananas("baanannbnaab")
# print("    permutation", d)
# print(time.perf_counter() - start)

start = time.perf_counter()
# c = bananas("abnnaannnnabn")
c = bananas("bbananana")
print("non-permutation", c)
print(time.perf_counter() - start)
