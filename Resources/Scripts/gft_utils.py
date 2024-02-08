import os
import platform
import time
import random


class ChromeUtils:
    def init_driver(self, **kwargs):
        """Returns a ChromeDriver object with commonly used parameters allowing for some optional settings"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as WebDriverOptions
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.keys import Keys

        # set defaults that can be overridden by passed parameters
        parameters = {
            "incognito": False,
            "headless": False,
            "window-size": False,
            "load_profile": False,
            "verbose": True,
            "no_driver_update": False,
            "maximized": False,
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
        if parameters["maximized"]:
            options.add_argument("--start-maximized")

        # fixed options
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.218 Safari/537.36"
        )
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
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        """

        _path = (
            os.path.join(
                f"{os.getcwd()[:2]}\pythonCode", "Resources", "chromedriver.exe"
            )
            if "Windows" in platform.uname().system
            else "/usr/bin/chromedriver"
        )

        # update driver to match browser version if necessary
        if not parameters["no_driver_update"]:
            self.driver_update(verbose=False)

        if parameters["verbose"]:
            print("gft_utils --> Chromedriver initiated")

        return webdriver.Chrome(service=Service(_path), options=options)

    def driver_update(self, **kwargs):
        """Compares current Chrome browser and Chrome driver versions and updates driver if necessary"""
        import subprocess
        import requests
        import json

        def target_drive():
            for drive in ("C:", "D:"):
                if os.path.exists(os.path.join(drive, "\pythonCode")):
                    return drive

        def check_chrome_version():
            result = subprocess.check_output(
                'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
            ).decode("utf-8")
            return result.split(" ")[-1].split(".")[0]

        def check_chromedriver_version():
            try:
                version = subprocess.check_output(f"{CURRENT_PATH} -v").decode("utf-8")
                return version.split(".")[0][-3:]
            except:
                return 0

        def download_chromedriver(target_version):
            # extract latest data from Google API
            api_data = json.loads(requests.get(GOOGLE_CHROMEDRIVER_API).text)

            # find latest build for current Chrome version and download zip file
            endpoints = api_data["milestones"][str(target_version)]["downloads"][
                "chromedriver"
            ]
            url = [i["url"] for i in endpoints if i["platform"] == "win64"][0]
            with open(TARGET_PATH, mode="wb") as download_file:
                download_file.write(requests.get(url).content)

            # delete current chromedriver.exe
            if os.path.exists(CURRENT_PATH):
                os.remove(CURRENT_PATH)

            # unzip downloaded file contents into Resources folder
            cmd = rf'Expand-Archive -Force -Path {TARGET_PATH} -DestinationPath "{BASE_PATH}"'
            subprocess.run(["powershell", "-Command", cmd])

            # move chromedriver.exe to correct folder
            os.rename(os.path.join(UNZIPPED_PATH, "chromedriver.exe"), CURRENT_PATH)

            # delete unnecesary files after unzipping
            os.remove(os.path.join(UNZIPPED_PATH, "LICENSE.chromedriver"))
            os.rmdir(UNZIPPED_PATH)
            os.remove(TARGET_PATH)

        # set defaults that can be overridden by passed parameters
        parameters = {
            "verbose": True,
        } | kwargs

        # define URIs
        GOOGLE_CHROMEDRIVER_API = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
        if "Windows" in platform.uname().system:
            BASE_PATH = os.path.join(rf"{target_drive()}\pythonCode", "Resources")
        else:
            BASE_PATH = r"/home/gfreundt/pythonCode/Resources"
        # BASE_PATH = os.path.join(rf"{target_drive()}\pythonCode", "Resources")
        CURRENT_PATH = os.path.join(BASE_PATH, "chromedriver.exe")
        TARGET_PATH = os.path.join(BASE_PATH, "chromedriver.zip")
        UNZIPPED_PATH = os.path.join(BASE_PATH, "chromedriver-win64")

        # get current browser and chromedriver versions
        driver = check_chromedriver_version()
        browser = check_chrome_version()
        if parameters["verbose"]:
            print(f"Driver: version {driver}\nBrowser: version {browser}.")

        # if versions don't match, get the correct chromedriver from repository
        if driver != browser:
            if parameters["verbose"]:
                print("Updating chromedriver.exe...")
            download_chromedriver(browser)
        else:
            if parameters["verbose"]:
                print("No need to update driver")

        # clean exit
        if parameters["verbose"]:
            print(">> Process Finished Succesfully <<")

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


class pygameUtils:
    def __init__(self) -> None:
        import pygame
        import json

        pygame.init()

        # load environment constants
        self.DISPLAY_WIDTH = pygame.display.Info().current_w
        self.DISPLAY_HEIGHT = pygame.display.Info().current_h
        self.MAIN_SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # split main surface in two halves
        self.LEFT_SURFACE = pygame.Surface(
            (self.MAIN_SURFACE.get_width() // 2, self.MAIN_SURFACE.get_height())
        )
        self.RIGHT_SURFACE = self.LEFT_SURFACE.copy()

        # load custom constants
        self.RESOURCES_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources")
        with open(
            os.path.join(self.RESOURCES_PATH, "ConfigData", "pygame_data.json"),
            mode="r",
        ) as file:
            data = json.load(file)
        self.COLORS = data["colors"]
        self.PALETTES = data["palettes"]
        _fonts = data["fonts"]
        self.FONTS = {
            i: pygame.font.Font(
                os.path.join(self.RESOURCES_PATH, "Fonts", _fonts[i]["ttf"]),
                _fonts[i]["size"],
            )
            for i in _fonts
        }
