import time
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import base64
import numpy as np
from PIL import Image
from io import BytesIO


class Wordle:
    def __init__(self):
        # define variables
        self.allWords = [
            i.strip().upper() for i in open("wordleDictionary.txt", "r").readlines()
        ]
        self.rank = self.frequency()
        self.GREEN = [106, 170, 100, 255]
        self.YELLOW = [201, 180, 88, 255]
        self.GRAY = [120, 124, 126, 255]
        self.WHITE = [255, 255, 255, 255]
        self.BLACK = [0, 0, 0, 255]
        self.reset()
        # define options for Chromedriver and open URL
        options = WebDriverOptions()
        options.add_argument("--silent")
        options.add_argument("--disable-notifications")
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        web_url = "https://www.nytimes.com/games/wordle/index.html"
        chromedriver_uri = (
            "C:\pythonCode\chromedriver.exe"
            if "Windows" in platform.uname().system
            else "/home/gft/pythonCode/chromedriver.exe"
        )
        self.webd = webdriver.Chrome(service=Service(chromedriver_uri), options=options)

        self.webd.get(web_url)

        # testing only
        time.sleep(3)
        button = self.webd.find_elements(
            By.XPATH, "/html/body/div/div/div/div/div[3]/button[2]"
        )
        if button:
            button[0].click()
            time.sleep(3)
        button = self.webd.find_elements(By.CLASS_NAME, "Modal-module_closeIcon__TcEKb")
        if button:
            button[0].click()
            time.sleep(3)

        # load virtual keyboard dictionary of elements
        self.keys = {
            i: j
            for i, j in zip(
                "QWERTYUIOPASDFGHJKL@ZXCVBNM<",
                self.webd.find_elements(By.CLASS_NAME, "Key-module_key__kchQI"),
            )
        }
        # load list of row elements
        self.rows = self.webd.find_elements(By.CLASS_NAME, "Row-module_row__pwpBq")

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
        self.tryWord = "AROSE"

    def write(self, word, enter=True):
        for letter in word:
            self.keys[letter].click()
            time.sleep(0.5)
        if enter:
            self.keys["@"].click()
            time.sleep(0.5)

    def process_colors(self, active_row):
        img = np.array(
            Image.open(
                BytesIO(base64.b64decode(self.rows[active_row].screenshot_as_base64))
            )
        )

        for position in range(5):
            pixel = img[46][25 + 62 * position]
            if np.array_equal(pixel, self.GREEN):
                self.green_letter(position)
            elif np.array_equal(pixel, self.YELLOW):
                self.yellow_letter(position)
            elif np.array_equal(pixel, self.GRAY):
                self.gray_letter(position)

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
    start = time.perf_counter()
    WORDLE = Wordle()
    turn = 0
    while turn <= 5:
        # print(f"Turn: {turn}")
        try:
            WORDLE.write(WORDLE.tryWord)
        except:
            print(
                f"Found {WORDLE.tryWord} in {turn} tries ({time.perf_counter()-start:.1f} seconds)."
            )
            return
        time.sleep(5)
        WORDLE.process_colors(turn)
        possible_words = [i for i in WORDLE.allWords if WORDLE.word_possible(i)]
        WORDLE.get_next_best_word(possible_words)
        turn += 1

    print("Chances Exhausted")


main()
