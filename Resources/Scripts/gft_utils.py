import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.chrome.service import Service


class ChromePreLoad:
    def init_driver(self=None, **kwargs):
        # set defaults that can be overridden by passed parameters
        parameters = {
            "incognito": False,
            "headless": False,
            "window-size": (1920, 1080),
        }.update(kwargs)

        options = WebDriverOptions()

        # configurable options
        if parameters["incognito"]:
            options.add_argument("--incognito")
        if parameters["headless"]:
            options.add_argument("--headless=new")
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

        _path = os.path.join("D:\pythonCode", "Resources", "chromedriver.exe")
        return webdriver.Chrome(service=Service(_path), options=options)
