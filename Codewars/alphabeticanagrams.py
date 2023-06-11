from math import factorial
import itertools as itt


def score(word):
    def inorder(word):
        return sorted([i for i in word])

    offset = 0
    dup = 4
    word = word.upper()
    score = 0
    for k, letter in enumerate(word):
        if word.count(letter) > 1:
            offset += 1
        else:
            offset = 0
        score += (
            inorder(word[k:]).index(letter)
            * factorial(len(word) - k - 1)
            // factorial(dup)
        ) + offset
    return score + 1


def rank(letter, word, k):
    return sorted(word[k:]).index(letter)
    return sorted(set(word[k:])).index(letter)


def combos_left(word, k):
    f = len(set(word[k + 1 :]))
    f = len(word[k + 1 :])
    print(f"{word[k+1:]=}  {k=}  {f=}  ")
    return factorial(f)


# test = ["ghxaza", "ghxzaa", "ghzaax", "ghzaxa"]


def scoring(word):

    count = 0
    while len(word) > 1:
        first = word[0]
        uniques = set(word)
        possibilities = factorial(len(word))
        for letter in uniques:
            possibilities /= factorial(word.count(letter))
        for letter in uniques:
            if letter < first:
                count += possibilities / len(word) * word.count(letter)
        word = word[1:]
    return int(count + 1)


def brute(word):
    all = sorted(list(set(["".join(i) for i in itt.permutations(word)])))
    unique = len(list(set(word)))
    rep = len(word) - unique
    return all, all.index(word) + 1, unique, rep


print(scoring("BOOKKEEPER"))
