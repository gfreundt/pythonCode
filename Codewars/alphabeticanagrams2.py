from math import factorial
from itertools import permutations
from time import perf_counter


def brute(word):
    a = ["".join(i) for i in sorted(set(permutations(word)))]
    return a.index(word) + 1


def elegant(word):
    repetitions = [factorial(word.count(i)) for i in set(word)]
    q = 1
    for c in repetitions:
        q *= c
    total_words = factorial(len(word)) / q

    accum = 0
    multipliers = [factorial(i) for i in range(len(word) - 1, 0, -1)] + [0]
    remaining_letters = sorted(word)

    # adding positions
    for k, w in enumerate(word):
        value = remaining_letters.index(w)
        accum += value * multipliers[k]
        remaining_letters.remove(w)

    # substracting positions for repeated letters

    return accum + 1


for s in permutations(sorted("book")):
    # start = perf_counter()
    print("brute/elegant:", s, brute("".join(s)), elegant("".join(s)))
    # print(perf_counter() - start)

    # start = perf_counter()
    # print("elegant:", elegant(s))
    # print(perf_counter() - start)
