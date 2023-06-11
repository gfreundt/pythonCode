import pyautogui
import time
import platform
from copy import deepcopy as copy
from PIL import Image

import easyocr
import pytesseract as pyt

from itertools import permutations


class Info:
    def __init__(self) -> None:
        centers = [
            (1215, 1124),
            (1215, 1301),
            (1365, 1388),
            (1522, 1301),
            (1522, 1124),
            (1365, 1036),
        ]
        # self.centers = [(853, 688), (853, 811), (960, 877), (1066, 811), (1066, 688), (960, 626)]
        self.cut_size = (80, 80)
        self.letters = [
            {
                "alpha": " ",
                "centers": i,
                "edges": (
                    i[0] - self.cut_size[0] // 2,
                    i[1] - self.cut_size[1] // 2,
                    i[0] + self.cut_size[0] // 2,
                    i[1] + self.cut_size[1] // 2,
                ),
            }
            for i in centers
        ]
        self.dial_center = (centers[2][0], (centers[0][1] + centers[1][1]) // 2)
        self.slide_time = 0.4
        self.drive = "D:" if platform.node() == "power" else "C:"


def extract_letters():
    def post_processing(text):
        text = text.strip()
        text = text.replace("|", "I")
        text = text.replace("0", "O")
        text = text.replace(" ", "")
        text = "".join([i for i in text if i.isalpha()])
        return text

    # take screenshot
    pyautogui.screenshot().save("screenshot.png")
    img = Image.open("screenshot.png")

    # create blank image
    newImage = Image.new(
        "RGB", (len(app.letters) * app.cut_size[0], app.cut_size[1]), (50, 50, 50)
    )

    # crop individual letters and paste to blank image (only 6 for now)
    for k, letter in enumerate(app.letters):
        croppedImage = img.crop((letter["edges"]))
        newImage.paste(croppedImage, (k * app.cut_size[0], 0))
    newImage.save(f"combo.jpg")

    # try two ocr methods, keep the best
    result1 = post_processing(
        easyocr.Reader(["en"]).readtext(
            "combo.jpg", paragraph=False, decoder="beamsearch"
        )[0][1]
    )
    result2 = post_processing(pyt.image_to_string(Image.open("combo.jpg")))
    print(result1, result2)
    result = result1 if len(result1) == 6 else result2 if len(result2) == 6 else None
    return list(result.lower()) if result else None

    """
    gft-966@wordvision.iam.gserviceaccount.com
    """


def get_valid_words(letters):
    words = []
    for length in range(3, 7):
        words += ["".join(i) for i in permutations(letters, length) if len(i) > 2]
    with open("english50k.txt", mode="r") as file:
        all_words = [i.strip() for i in file.readlines()]
    return sorted(set([i for i in words if i in all_words]), key=lambda i: len(i))


def go_thru_letters(word):
    # get coordinates for sequence of letters
    temp_letters = copy(app.letters)
    coords = []
    for letter in word:
        for k, c in enumerate(temp_letters):
            if letter == c["alpha"]:
                coords.append(c["centers"])
                temp_letters.pop(k)
                break
    # click thru sequence of letter coordinates on app
    pyautogui.moveTo(coords[0][0], coords[0][1], app.slide_time)
    pyautogui.mouseDown(button="left")
    for c in coords[1:]:
        pyautogui.moveTo(c[0], c[1], app.slide_time)
    pyautogui.mouseUp(button="left")
    pyautogui.moveTo(app.dial_center[0], app.dial_center[1], app.slide_time)


# 0. Init
drive = "D:" if platform.node() == "power" else "C:"
pyt.pytesseract.tesseract_cmd = rf"{drive}\pythonCode\Tesseract-OCR\tesseract.exe"
print("Starting in 5 seconds...")
time.sleep(5)

# 1. Open App and Navigate to Game

while True:
    app = Info()

    # 2. Clear bonus words
    pyautogui.click(x=1110, y=245, clicks=1, button="left")  # click on bonus icon
    time.sleep(2)
    pyautogui.click(x=1380, y=1370, clicks=1, button="left")  # click "claim"
    time.sleep(2)
    pyautogui.click(x=1380, y=1490, clicks=1, button="left")  # click "back to puzzle"

    # 3. Cut and identify letters, store them in dictionary with coordinates
    letters, k = None, 0
    while not letters:
        letters = extract_letters()
        if not letters:
            pyautogui.click(x=1010, y=245, clicks=1, button="left")
            k += 1
            if k > 2:
                print("stopped!")
                quit()

    for i, j in zip(app.letters, letters):
        i.update({"alpha": j})

    # 4. Create list of words
    valid_words = get_valid_words(letters)

    # 5. Click and drag each word, click "NEXT"
    for word in valid_words:
        print(word)
        go_thru_letters(word)
    time.sleep(12)  # wait for animation and "next" to appear
    pyautogui.click(x=1380, y=1370, clicks=1, button="left")
    time.sleep(1)
    pyautogui.moveTo(1000, 1000, 0.2)  # move cursor out of the way for next screenshot
    time.sleep(5)  # wait for puzzle to load
