import os
import platform
import time
import random
from pathlib import Path




class ChromeUtils:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as WebDriverOptions
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.keys import Keys

    def init_driver(self=None, **kwargs):
        """Returns a ChromeDriver object with commonly used parameters allowing for some optional settings"""

        # set defaults that can be overridden by passed parameters
        parameters = {
            "incognito": False,
            "headless": False,
            "window-size": False,
            "load_profile": False,
        } | kwargs

        options = WebDriverOptions()

        # configurable options
        if parameters["incognito"]:
            options.add_argument("--incognito")
        if parameters["headless"]:
            options.add_argument("--headless=new")
        if parameters["load_profile"]:
            options.add_argument(
                r"--user-data-dir=C:\Users\gfreu\AppData\Local\Google\Chrome\User Data\Default\Profile 1"
            )
        if parameters["window-size"]:
            options.add_argument(
                f"--window-size={parameters['window-size'][0]},{parameters['window-size'][1]}"
            )

        # fixed options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--silent")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)

        # disabled options
        """
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        """

        _path = (
            os.path.join(
                f"{Path.home().drive}\pythonCode", "Resources", "chromedriver.exe"
            )
            if "Windows" in platform.uname().system
            else "/usr/bin/chromedriver"
        )
        return webdriver.Chrome(service=Service(_path), options=options)

    def slow_key_sender(self=None, **kwargs):
        """Inserts random small pauses between keystrokes to simulate human typing"""

        # TODO: default for return_key
        for key in kwargs["text"]:
            time.sleep(random.randint(1, 10) / 10)
            kwargs["element"].send_keys(key)
        if kwargs["return_key"]:
            time.sleep(0.4)
            kwargs["element"].send_keys(Keys.RETURN)

    def button_clicker(self, webdriver, type, element, timeout=20, fatal_error=False):
        """Waits for clickable element to load before clicking on it"""
        try:
            WebDriverWait(webdriver, timeout).until(
                EC.element_to_be_clickable((type, element))
            ).click()
        except TimeoutException:
            if fatal_error:
                print("Webpage failed to load.")
                quit()

class PygameUtils:
    def init_variables(self):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        RED = (171, 35, 40)
        GREEN = (0, 110, 51)
        BROWN = (102, 51, 0)
        BLUE = (0, 0, 153)
        LIGHT_BLUE = (51, 153, 255)
        GRAY = (120, 120, 120)
        BG = (25, 72, 80)
        BG_CONTROLS = (0, 102, 102)
        INV_COLORS = [(44, 93, 118), (74, 148, 186)]
        RESOURCES_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Fonts")

        DISPLAY_WIDTH = pygame.display.Info().current_w
        DISPLAY_HEIGHT = pygame.display.Info().current_h // 1.01
        FONT9 = pygame.font.Font(os.path.join(RESOURCES_PATH, "seguisym.ttf"), 9)
        FONT12 = pygame.font.Font(os.path.join(RESOURCES_PATH, "seguisym.ttf"), 12)
        FONT14 = pygame.font.Font(os.path.join(RESOURCES_PATH, "seguisym.ttf"), 14)
        FONT20 = pygame.font.Font(os.path.join(RESOURCES_PATH, "roboto.ttf"), 20)