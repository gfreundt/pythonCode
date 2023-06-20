import time
import sys, os
import random

import base64
import numpy as np
from PIL import Image
from io import BytesIO

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class Wordle:
    def __init__(self):
        # define variables
        base_path = os.path.join(r"\pythonCode", "Automation", "Wordle")
        self.allWords = [
            i.strip().upper()
            for i in open(
                os.path.join(base_path, "wordleDictionary.txt"), "r"
            ).readlines()
        ]
        print("Dictionary Loaded...")
        self.rank = self.frequency()
        print("Frequency Calculated...")
        self.GREEN = [106, 170, 100, 255]
        self.YELLOW = [201, 180, 88, 255]
        self.GRAY = [120, 124, 126, 255]
        self.WHITE = [255, 255, 255, 255]
        self.BLACK = [0, 0, 0, 255]
        self.reset()
        # define options for Chromedriver and open URL
        self.webd = ChromeUtils.init_driver(headless=False)
        web_url = "https://www.nytimes.com/games/wordle/index.html"
        self.webd.get(web_url)
        self.login()
        print("Logging in completed")
        time.sleep(7)
        # load virtual keyboard dictionary of elements

        f = self.webd.find_elements(By.XPATH, "//*")

        for i in f:
            print("TEXT", i.text)
            print("-----")
            print("CLASS", i.get_attribute("class"))
            print("-----")
            print(i)
            print("****************")

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
        self.tryWord = random.choice(
            ["AROSE", "REACT", "ADIEU", "LATER", "SIRED", "TEARS", "ALONE"]
        )

    def slow_key_sender(self, element, text, return_key=False):
        for key in text:
            time.sleep(random.randint(1, 10) / 10)
            element.send_keys(key)
        if return_key:
            time.sleep(0.4)
            element.send_keys(Keys.RETURN)

    def clicker(self, webdriver, type, element, timeout=20, fatal_error=False):
        try:
            WebDriverWait(webdriver, timeout).until(
                EC.element_to_be_clickable((type, element))
            ).click()
        except TimeoutException:
            if fatal_error:
                print("Webpage failed to load.")
                quit()

    def login(self):
        email = "gabfre@gmail.com"
        password = "A4Dh$yta#n#iDr_"

        wait = WebDriverWait(self.webd, 100)

        # click on ACCEPT cookies
        self.clicker(self.webd, By.ID, element="pz-gdpr-btn-accept", fatal_error=False)
        time.sleep(3)
        # click on Log In button
        button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div/div/div/div/div[3]/a/button")
            )
        )
        button.click()
        time.sleep(3)
        # enter email
        input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        self.slow_key_sender(input, email, return_key=True)
        # enter password
        input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        self.slow_key_sender(input, password, return_key=True)
        time.sleep(2)

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

        # self.rows[active_row].screenshot(f"img_{active_row}.png")

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
        print(f"\nTurn: {turn}. Trying {WORDLE.tryWord}")
        # try:
        WORDLE.write(WORDLE.tryWord)
        """except:
            print(
                f"Found {WORDLE.tryWord} in {turn} tries ({time.perf_counter()-start:.1f} seconds)."
            )
            return"""
        time.sleep(3)
        WORDLE.process_colors(turn)
        possible_words = [i for i in WORDLE.allWords if WORDLE.word_possible(i)]
        WORDLE.get_next_best_word(possible_words)
        turn += 1

    print("Chances Exhausted")


main()
