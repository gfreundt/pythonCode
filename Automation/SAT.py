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


PATH = os.path.join("D:\pythonCode", "general", "SAT")
CHROMEDRIVER = os.path.join("D:\pythonCode", "chromedriver.exe")
URL = "https://www.sat.gob.pe/WebSiteV9/"
DRIVER = webdriver.Chrome(CHROMEDRIVER, options=set_options())

x = 0

while True:

    print(x)

    DRIVER.get(URL)
    DRIVER.set_window_position(1280, 0, windowHandle="current")

    time.sleep(2)
    plate = (
        "A"
        + chr(random.randint(65, 90))
        + chr(random.randint(65, 90))
        + chr(random.randint(48, 57))
        + chr(random.randint(48, 57))
        + chr(random.randint(48, 57))
    )
    DRIVER.find_element_by_id("txtPlacaIV").send_keys(plate)
    DRIVER.find_element_by_id("vehicular").click()
    time.sleep(4)
    DRIVER.switch_to.window(DRIVER.window_handles[-1])
    time.sleep(1)
    p = DRIVER.page_source
    DRIVER.save_screenshot(os.path.join(PATH, "temp.png"))
    crop = Image.open(os.path.join(PATH, "temp.png")).crop((597, 430, 686, 455))
    filename = uuid.uuid4().hex[:8] + ".png"
    crop.save(os.path.join(PATH, filename))

    x += 1
    if x > 50:
        quit()
