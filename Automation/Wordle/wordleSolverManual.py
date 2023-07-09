import time
import os
import random
import keyboard

import base64
import numpy as np
from PIL import Image, ImageGrab
from io import BytesIO


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
        self.GREEN = [106, 170, 100]
        self.YELLOW = [201, 180, 88]
        self.GRAY = [120, 124, 126]
        self.WHITE = [255, 255, 255]
        self.BLACK = [0, 0, 0, 255]
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
        self.tryWord = random.choice(
            ["AROSE", "REACT", "ADIEU", "LATER", "SIRED", "TEARS", "ALONE"]
        )

    def write_word(self):
        time.sleep(1)
        keyboard.press_and_release("e")
        time.sleep(1)
        keyboard.press_and_release("backspace")
        for letter in self.tryWord:
            time.sleep(1)
            keyboard.press_and_release(letter)
            time.sleep(random.randint(5, 12) / 10)
        keyboard.press_and_release("enter")

    def process_colors(self, row):
        img = np.asarray(ImageGrab.grab())

        x0, y0 = 3203, 1023
        box = 92
        gap = 11

        total_green = 0

        for position in range(5):
            pixel = img[y0 + row * (box + gap) + 5][x0 + position * (box + gap) + 5]
            if np.array_equal(pixel, self.GREEN):
                self.green_letter(position)
                total_green += 1
            elif np.array_equal(pixel, self.YELLOW):
                self.yellow_letter(position)
            elif np.array_equal(pixel, self.GRAY):
                self.gray_letter(position)

        if total_green == 5:
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
    print("Select the Wordle Window in the next 5 seconds")
    time.sleep(5)

    WORDLE = Wordle()
    turn = 0
    while turn <= 5:
        print(f"Turn: {turn}. Trying {WORDLE.tryWord}")
        WORDLE.write_word()
        time.sleep(5)
        if WORDLE.process_colors(turn):
            return
        possible_words = [i for i in WORDLE.allWords if WORDLE.word_possible(i)]
        WORDLE.get_next_best_word(possible_words)
        turn += 1

    print("Chances Exhausted")


main()
