import os
import platform
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys


class ChromeUtils:
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
            os.path.join("D:\pythonCode", "Resources", "chromedriver.exe")
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