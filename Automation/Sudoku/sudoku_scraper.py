import sys
import time
from PIL import Image
from selenium.webdriver.common.by import By
import easyocr

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


def scrape():
    webd = ChromeUtils().init_driver(headless=True, verbose=False, maximized=True)
    for level in ("medium", "hard", "expert", "easy"):
        url = f"https://sudoku.com/{level}/"
        webd.get(url)
        for m in range(250):
            time.sleep(0.5)
            button = webd.find_element(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div[7]/div[4]/nav/div[2]/div[1]/div[1]",
            )
            button.click()
            time.sleep(0.5)
            webd.save_screenshot("erase.png")
            a = Image.open("erase.png").crop((1002, 208, 1002 + 750, 208 + 750))
            a.save("full.png")
            puzzle = extract()
            if len(puzzle) == 81:
                print(m, puzzle)
                with open("sudokudotcom.csv", "a+") as file:
                    file.write(f"{puzzle},{level.title()}\n")
            webd.refresh()


def extract():
    x = ""
    img = Image.open("full.png")
    for row in range(9):
        for col in range(9):
            digit_image = img.crop(
                (col * 83 + 2, row * 83 + 3, (col + 1) * 83 + 2, (row + 1) * 83 + 3)
            ).convert("L")
            digit_image.save("temp.png")
            time.sleep(0.2)
            result = READER.readtext(
                "temp.png",
                text_threshold=0.3,
                decoder="beamsearch",
                mag_ratio=2,
            )
            if len(result) > 0 and len(result[0]) > 0:
                x += result[0][1]
            else:
                x += "0"
    return x.strip()


READER = easyocr.Reader(["en"], gpu=False)
scrape()


"""
Point(x=494, y=398)
Point(x=569, y=471)

Point(x=1155, y=1059)
Point(x=1230, y=1132)

Point(x=489, y=390)
Point(x=1235, y=1137)

"""
