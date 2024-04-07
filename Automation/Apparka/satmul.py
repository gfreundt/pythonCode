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
            # navigate to to Consulta Papeletas page with internal URL
            time.sleep(1)
            _target = (
                "https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?mysession="
                + self.WEBD.current_url.split("=")[-1]
            )
            self.WEBD.get(_target)
            opening = False
        time.sleep(2)

        # select alternative option from dropdown to reset it
        drop = Select(self.WEBD.find_element(By.ID, "tipoBusquedaPapeletas"))
        drop.select_by_value("busqPlaca")
        time.sleep(0.5)

        # enter Placa
        x = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtPlaca")
        x.send_keys("ABC123")

        # click Captcha
        _coords = (1392 + randrange(0, 37), 1004 + randrange(0, 34))
        _delay = 0.45 + randrange(0, 15) // 100
        pyautogui.moveTo(_coords[0], _coords[1], _delay)
        time.sleep(0.1)
        pyautogui.click()
        time.sleep(0.7)

        # click Buscar
        x = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_CaptchaContinue")
        x.click()
        time.sleep(30)


if __name__ == "__main__":
    x = Captcha()
    x.scraper()
