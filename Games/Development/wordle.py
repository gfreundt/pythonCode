from copy import deepcopy as copy
from colorama import Fore, Back, Style
from random import choice
import string
import time
from tqdm import tqdm


def eval_try(test_word, target_word):
    """2 = GREEN, 1 = YELLOW, 0 = GREY"""
    temp_target_word = copy(target_word)
    results = [0 for _ in range(5)]

    # test greens
    for k, (test_letter, target_letter) in enumerate(zip(test_word, target_word)):
        if test_letter == target_letter:
            results[k] = 2
            temp_target_word[k] = "_"
            test_word[k] = "?"

    # test yellows
    k = 0
    while k < 5:
        if test_word[k] in temp_target_word:
            results[k] = 1
            for j, letter in enumerate(temp_target_word):
                if letter == test_word[k]:
                    temp_target_word[j] = "_"
                    break
        k += 1

    # return list with 5 items (0, 1 or 2)
    return results


def show_progress(test_word, progress):
    output = []
    for letter, p in zip(test_word, progress):
        _partial = Fore.WHITE + letter
        if p == 2:
            output.append(Back.GREEN + _partial)
        if p == 1:
            output.append(Back.YELLOW + _partial)
        if p == 0:
            output.append(Back.LIGHTBLUE_EX + _partial)
    return "".join(output)


def get_all_words(length):
    with open("10kwords.txt", "r") as file:
        return [i.strip().upper() for i in file.readlines() if len(i.strip()) == 5]


def get_random_word(all_words):
    word = choice(all_words)
    return word


def update_options(options, test_word, latest_test_results):
    for k, (letter, test_result) in enumerate(zip(test_word, latest_test_results)):
        if test_result == 2:
            options[k] = [letter]
        elif test_result == 1:
            try:
                options[k].remove(letter)
                options[-1].append(letter)
            except:
                pass
        else:
            for k in range(5):
                try:
                    # TODO: what if both letters are gray?
                    if test_word.count(letter) == 1:
                        options[k].remove(letter)
                except ValueError:
                    pass

    return options


def possible_words(options, all_words):

    def test_word(word, options):
        for must_be in options[-1]:
            if must_be not in word:
                return False
        for letter, available in zip(word, options):
            if letter not in available:
                return False
        return True

    possible_words = []
    for w in all_words:
        word = list(w)
        if test_word(word, options):
            possible_words.append(w)
    return possible_words


def get_test_word(available_words):
    # first round
    if available_words == all_words:
        return choice(possible_starting_words)

    # if close to words, send direct guess
    # if not close to word, send word that does not include known letter
    if len(available_words) < 5:
        return choice(available_words)

    return get_random_word(all_words=all_words)


def main():
    for attempts in range(5):
        while True:
            test_word = input().upper()
            if test_word in all_words:
                break

        progress = eval_try(test_word=list(test_word), target_word=list(target_word))
        print(attempts, show_progress(test_word, progress))

        print(Style.RESET_ALL)

    print(target_word)


def main2():

    global available_words
    available_letters = [[i for i in string.ascii_uppercase] for _ in range(5)] + [[]]
    attempts = 0
    while len(available_words) > 1:
        test_word = get_test_word(available_words)
        available_letters = update_options(
            available_letters,
            test_word,
            eval_try(test_word=list(test_word), target_word=list(target_word)),
        )
        available_words = possible_words(available_letters, available_words)
        attempts += 1
    return available_words, attempts


possible_starting_words = ["CLEAR"]  # , "STORE", "CLOUD", "PAINT"]
all_words = get_all_words(length=5)


total = 0
iters = 5000
for _ in tqdm(range(iters)):
    available_words = copy(all_words)
    target_word = get_random_word(all_words=all_words)
    a, b = main2()
    total += b

print(iters, total / iters)

quit()

f = time.perf_counter()
for _ in range(10):
    available_words = copy(all_words)
    target_word = get_random_word(all_words=all_words)
    a = main2()
    print(a, target_word)
    if target_word not in a:
        print("oops")

print(time.perf_counter() - f)
