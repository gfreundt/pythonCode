from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time, sys
from datetime import datetime as dt, timedelta as td
import pyautogui
from random import randrange


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class Captcha:
    # define class constants
    URL = "https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx"

    def __init__(self) -> None:
        self.WEBD = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True
        )
        self.WEBD.get(self.URL)

    def scraper(self, opening=True):
        if opening:
            # navigate to to Tributo Detalles page with internal URL
            time.sleep(1)
            _target = (
                "https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?mysession="
                + self.WEBD.current_url.split("=")[-1]
            )
            self.WEBD.get(_target)

        time.sleep(4)

        _cc = (1401, 1042)
        _rc = (randrange(100, 2500), randrange(200, 1800))
        pyautogui.moveTo(_rc)
        time.sleep(3)
        pyautogui.moveTo(_cc, duration=0.54)
        time.sleep(1.5)
        pyautogui.click()

        time.sleep(10)

        # x = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_CaptchaContinue")
        # x.click()


if __name__ == "__main__":
    x = Captcha()
    x.scraper()
