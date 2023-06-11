from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image, ImageGrab
import os, time
import uuid
from tqdm import tqdm
import random
import easyocr


def set_options():
    options = WebDriverOptions()
    options.add_argument("--window-size=1280,1440")
    options.add_argument("--disable-gpu")
    options.add_argument("--silent")
    options.add_argument("--disable-notifications")
    options.add_argument("--incognito")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options


def ocr(image_path):
    """Use offline EasyOCR to convert captcha image to text"""
    READER = easyocr.Reader(["en"], gpu=False)
    result = READER.readtext(image_path)
    if len(result) > 0 and len(result[0]) > 0:
        return result[0][1]
    else:
        return ""


print(ocr("test.png"))
quit()


CHROMEDRIVER = os.path.join("C:\pythonCode", "chromedriver.exe")
URL = "https://slcp.mtc.gob.pe/"
DRIVER = webdriver.Chrome(CHROMEDRIVER, options=set_options())

DRIVER.get(URL)
time.sleep(20)

# DRIVER.implicitly_wait(0.5)
captcha = DRIVER.find_element("id", "imgCaptcha")
with open("test.png", mode="wb") as imagefile:
    imagefile.write(captcha.screenshot_as_png)
