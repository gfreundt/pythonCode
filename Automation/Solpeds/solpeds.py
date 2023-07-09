from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time, sys
import keyboard
from subprocess import Popen

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils

# TODO: doesn't work with headless
# TODO: turn on and off VPN


def turn_on_vpn():
    Popen(r'"C:\Program Files\Palo Alto Networks\GlobalProtect\PanGPA.exe"')


def load_webdriver():
    """Define options for Chromedriver"""
    options = WebDriverOptions()
    # options.add_argument("--headless")
    options.add_argument("--silent")
    options.add_argument("--disable-notifications")
    options.add_argument("--incognito")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(
        service=Service(os.path.join(r"C:\pythonCode\Resources", "chromedriver.exe")),
        options=options,
    )


def login(webd):
    time.sleep(4)
    keyboard.write("gfreundt")
    keyboard.press_and_release("tab")
    keyboard.write("Subaru21")
    keyboard.press_and_release("enter")


def approve(webd):
    counter = 0
    list_of_approvals = []

    while True:
        WebDriverWait(webd, 10).until(
            EC.presence_of_element_located((By.ID, "TaskListFrame"))
        )
        webd.switch_to.frame("TaskListFrame")
        solpeds = webd.find_elements(By.ID, "GridView1$ctl02_table")
        if solpeds:
            details = solpeds[0].text
            counter += 1
            if "SOLPED" not in details:
                solpeds[0].click()
                time.sleep(2)
                second_click = webd.find_element(
                    By.XPATH, '//*[@id="SVMenuOperation_0"]/tbody/tr/td[2]'
                )
                second_click.click()
            else:
                solpeds[0].click()
        else:
            webd.quit()
            break
        time.sleep(3)
        keyboard.press_and_release("enter")
        time.sleep(10)
        button = WebDriverWait(webd, 10).until(
            EC.presence_of_element_located((By.ID, "Approve"))
        )
        button.click()
        list_of_approvals.append(details)
        time.sleep(10)

    if list_of_approvals:
        output = f"Completo con {counter} aprobaciones:"
        for a in list_of_approvals:
            output += f"{a}\n"
    else:
        output = "Nada que aprobar"

    return output


def main():
    url = "http://winshuttle.losportales.com.pe:82/prd/default.aspx"
    webd = ChromeUtils.init_driver(headless=False)
    webd.get(url)

    login(webd)
    output = approve(webd)

    print(output)


main()
