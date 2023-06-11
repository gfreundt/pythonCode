import time
import pyautogui
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


class Wordle:
    def __init__(self):
        # define variables
        self.allWords = [
            i.strip().upper() for i in open("wordleDictionary.txt", "r").readlines()
        ]
        self.rank = self.frequency()
        self.base_xpath = "/html/body/div[1]/div/section[1]/div/div[1]/div/div[1]/div/div/div[4]/div[6]/"
        self.buttons = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["<", "Z", "X", "C", "V", "B", "N", "M", "@"],
        ]
        self.GREEN = [121, 184, 81]
        self.YELLOW = [243, 194, 55]
        self.GRAY = [164, 174, 196]
        self.BLANK = [255, 255, 255]
        self.reset()
        # define options for Chromedriver and open URL
        options = WebDriverOptions()
        options.add_argument("--silent")
        options.add_argument("--disable-notifications")
        # options.add_argument("--incognito")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        web_url = "https://wordlegame.org/"
        self.webd = webdriver.Chrome(
            service=Service("C:\pythonCode\chromedriver.exe"), options=options
        )

        self.webd.set_window_position(1300, 0, windowHandle="current")
        self.webd.get(web_url)
        time.sleep(1)

    def reset(self):
        a_to_z = [chr(i) for i in range(65, 91)]
        self.solvedWord = [list(a_to_z) for _ in range(5)]  # avoid using same memory
        self.presentLetters, self.absentLetters, self.solvedLetters = (
            set(),
            set(),
            set(),
        )
        self.tryWord = "AROSE"

    def give_up(self):
        button = "/html/body/div[1]/div/section[1]/div/div[1]/div/div[1]/div/div/header/div[2]/button[2]"
        self.webd.find_element(By.XPATH, button).click()

    def frequency(self):
        count = [[chr(i), 0] for i in range(65, 91)]
        for word in self.allWords:
            for letter in word:
                i = ord(letter) - 65
                count[i][1] += 1
        return sorted(count, key=lambda i: i[1], reverse=True)

    def write(self, word, enter=True):
        for letter in word:
            self.click_key(letter)
            time.sleep(0.5)
        if enter:
            self.click_key("@")
        time.sleep(0.5)

    def click_key(self, letter):
        line_text = [i for i in self.buttons if letter in i][0]
        line = self.buttons.index(line_text) + 1
        pos = line_text.index(letter) + 1
        self.webd.find_element(
            By.XPATH, f"{self.base_xpath}div[{line}]/div[{pos}]"
        ).click()

    def process_colors(self, position):
        top_left_row0 = (2656, 271)
        box_size = (93, 93)
        boxes = [
            pyautogui.screenshot(
                region=(
                    top_left_row0[0] + i * box_size[0],
                    top_left_row0[1] + position * box_size[1],
                    box_size[0],
                    box_size[1],
                )
            )
            for i in range(5)
        ]
        for position, box in enumerate(boxes):
            pixel = np.asarray(box)[75, 75]
            if np.array_equal(pixel, self.GREEN):
                self.green_letter(position)
            elif np.array_equal(pixel, self.YELLOW):
                self.yellow_letter(position)
            elif np.array_equal(pixel, self.GRAY):
                self.gray_letter(position)
            else:
                return True

    def green_letter(self, position):
        letter = self.tryWord[position]
        self.solvedWord[position] = letter
        self.presentLetters.update(letter)
        self.solvedLetters.update(letter)

    def yellow_letter(self, position):
        letter = self.tryWord[position]
        if letter in self.solvedWord[position]:
            self.solvedWord[position].remove(letter)
            self.presentLetters.update(letter)

    def gray_letter(self, position):
        letter = self.tryWord[position]
        for pos, _ in enumerate(self.solvedWord):
            if letter in self.solvedWord[pos]:
                self.solvedWord[pos].remove(letter)
                self.absentLetters.update(letter)

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

    def get_next_best_word(self, wordList):
        scores = []
        for word in wordList:
            scores.append((word, self.calc_score(set(word))))
        result = sorted(scores, key=lambda i: i[1], reverse=True)
        self.tryWord = result[0][0]
        if len(result) > 1:
            self.tryWordAlternateList = [i[0] for i in result[1:]]

    def calc_score(self, option):
        score = 0
        for opt in option:
            i = [i[1] for i in self.rank if i[0] == opt][0]
            score += i
        return score


def main():
    turn = 0
    start = time.perf_counter()
    while turn <= 5:
        WORDLE.write(WORDLE.tryWord)
        time.sleep(5)
        if "poof" in WORDLE.webd.page_source:
            print("Solved: ", WORDLE.tryWord, f"{time.perf_counter() - start:.1f}")
            return
        if WORDLE.process_colors(turn):  # error in word, go to next word
            print("Word not Found")
            WORDLE.write("<<<<<", enter=False)
            time.sleep(3)
            WORDLE.tryWord = WORDLE.tryWordAlternateList.pop(0)

            continue
        possible_words = [i for i in WORDLE.allWords if WORDLE.word_possible(i)]
        WORDLE.get_next_best_word(possible_words)
        turn += 1


WORDLE = Wordle()
for i in range(20):
    print("Round", i)
    try:
        main()
    except:
        print("Error")
        WORDLE.give_up()
    time.sleep(5)
    WORDLE.write("")  # press ENTER
    WORDLE.reset()
