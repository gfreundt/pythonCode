aimport time
import random
import sys, os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromePreLoad

webdriver = ChromePreLoad.init_driver()

webdriver.get("https://www.nytimes.com/games/wordle/index.html")


class Wordle:
    def __init__(self):
        # define variables
        self.allWords = [
            i.strip().upper() for i in open("wordleDictionary.txt", "r").readlines()
        ]
        print("Dictionary Loaded...")
        self.rank = self.frequency()
        self.reset()

    def frequency(self):
        count = [[chr(i), 0] for i in range(65, 91)]
        for word in self.allWords:
            for letter in word:
                i = ord(letter) - 65
                count[i][1] += 1
        return sorted(count, key=lambda i: i[1], reverse=True)

    def reset(self):
        a_to_z = [chr(i) for i in range(65, 91)]
        self.solvedWord = [list(a_to_z) for _ in range(5)]  # avoid using same memory
        self.presentLetters, self.absentLetters, self.solvedLetters = (
            set(),
            set(),
            set(),
        )

    def process_colors(self, final_word):
        self.color_code = []
        for k, letter in enumerate(self.tryWord):
            if letter == final_word[k]:
                self.green_letter(k)
            elif letter in final_word:
                self.yellow_letter(k)
            else:
                self.gray_letter(k)
        if self.color_code == [1, 1, 1, 1, 1]:
            return True

    def green_letter(self, position):
        # print("Green")
        letter = self.tryWord[position]
        self.solvedWord[position] = letter
        self.presentLetters.update(letter)
        self.solvedLetters.update(letter)
        self.color_code.append(1)

    def yellow_letter(self, position):
        # print("Yellow")
        letter = self.tryWord[position]
        if letter in self.solvedWord[position]:
            self.solvedWord[position].remove(letter)
            self.presentLetters.update(letter)
        self.color_code.append(0)

    def gray_letter(self, position):
        # print("Gray")
        letter = self.tryWord[position]
        for pos, _ in enumerate(self.solvedWord):
            if letter in self.solvedWord[pos]:
                self.solvedWord[pos].remove(letter)
                self.absentLetters.update(letter)
        self.color_code.append(-1)

    def word_possible(self, word):
        w = list(word)
        # check if all present are there and all absent are not there
        for absent in self.absentLetters:
            if absent in w:
                return False
        for present in self.presentLetters:
            if present not in w:
                return False
        # test known positions
        for k, w in enumerate(self.solvedWord):
            if w and word[k] not in w:
                return False
        # all checks complete
        return True

    def get_next_best_word(self, turn):
        scores = []
        for word in self.possible_words:
            scores.append((word, self.calc_score(set(word))))
        result = sorted(scores, key=lambda i: i[1], reverse=True)
        self.tryWord = result[0][0]

    def get_sweep_word(self):
        scores = []
        excluded_letters = [j for i, j in zip(self.color_code, self.tryWord) if i == 1]
        # print(excluded_letters)
        for word in self.allWords:
            if not any(i in excluded_letters for i in word):
                scores.append((word, self.calc_score(set(word))))
        result = sorted(scores, key=lambda i: i[1], reverse=True)
        self.tryWord = result[0][0]
        # print(scores)1
        # input()

    def calc_score(self, option):
        score = 0
        for opt in option:
            i = [i[1] for i in self.rank if i[0] == opt][0]
            score += i
        return score

    def solve(self, final_word):
        self.possible_words = self.allWords
        turn = 0
        while turn <= 100:
            print(self.tryWord)
            if self.process_colors(final_word):
                return turn + 1
            self.possible_words = [
                i for i in self.possible_words if self.word_possible(i)
            ]
            if False:  # turn == 1 and 1 in self.color_code:
                self.get_sweep_word()
            else:
                self.get_next_best_word(turn)
            turn += 1


def login():
    email = "gabfre@gmail.com"
    password = "A4Dh$yta#n#iDr_"

    button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/div/div/div[3]/a/button")
        )
    )
    button.click()
    time.sleep(3)

    input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    input.send_keys(email)
    time.sleep(0.5)
    input.send_keys(Keys.RETURN)

    input = wait.until(EC.presence_of_element_located((By.ID, "password")))
    input.send_keys(password)
    time.sleep(0.5)
    input.send_keys(Keys.RETURN)
    time.sleep(2)


time.sleep(100)


def main():
    os.chdir(os.path.join(r"\pythonCode", "Automation", "Wordle"))
    WORDLE = Wordle()
    starting_words = WORDLE.allWords
    random.shuffle(starting_words)
    starting_words = ["AROSE"]  # , "QUADS", "COLEY", "LEAFY", "HAITH"]
    for starting_word in starting_words:
        total_attempts, unsolved = 0, 0
        start = time.perf_counter()
        test = [i.upper().strip() for i in open("allWordleAnswers.txt").readlines()]
        test = ["SHYLY"]  # , "SPATE", "TOUGH", "POINT"]
        for word in test:
            WORDLE.tryWord = starting_word
            attempts = WORDLE.solve(word)
            # print("..............")
            if attempts > 6:
                attempts = 6
                unsolved += 1
            total_attempts += attempts
            WORDLE.reset()
        print(
            f"Starting Word: {starting_word} - Total Time: {time.perf_counter() - start:.2f} seconds - Average Attempts: {total_attempts / len(test):.4f} - Unsolved words: {unsolved} ({unsolved/len(test)*100:.3f}%)"
        )
        with open("startingWordSimulations.txt", "a") as ofile:
            ofile.write(
                f"{starting_word},{time.perf_counter() - start:.2f},{total_attempts / len(test):.4f},{unsolved}\n"
            )


main()
