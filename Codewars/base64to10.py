from typing import List, Set, Tuple

# return a filtered set of words
def wordle(wordlist: Set[str], guesses: List[Tuple[str]]) -> Set[str]:
    def valid(word):
        for a, b in zip(word, combinations):
            if a not in b:
                return False
        return True

    absent = (
        set(
            [
                test_word[k]
                for test_word, result in guesses
                for k, ans in enumerate(result)
                if ans == "-"
            ]
        )
        if guesses
        else []
    )

    available = [chr(i) for i in range(ord("A"), ord("Z") + 1) if chr(i) not in absent]
    combinations = [available for i, _ in enumerate(wordlist[0])]

    for test_word, result in guesses:
        for k, ans in enumerate(result):
            if ans == "G":
                combinations[k] = [test_word[k]]

    return set([i for i in wordlist if valid(i)])


wordlist = ["SHEEP", "KINKY", "SWEET", "MAUVE", "FLUNG", "SKEET"]
guesses = [("SPOIL", "G----"), ("STEAD", "GYG--"), ("SEETH", "GYGY-")]

print(wordle(wordlist, []))
