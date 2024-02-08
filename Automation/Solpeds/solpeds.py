from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import os, time, sys
import keyboard
from subprocess import Popen
import pyautogui

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


def turn_on_vpn():
    # start VPN Windows service
    Popen("net start pangps")
    time.sleep(3)
    # open interface on task bar
    Popen(r'"D:\Program Files\Palo Alto Networks\GlobalProtect\PanGPA.exe"')
    time.sleep(2)
    # click on connect and wait
    pyautogui.click(3620, 2035)
    time.sleep(15)


def turn_off_vpn():
    # stop VPN Windows service
    Popen("net stop pangps")


def login():
    keyboard.write("gfreundt")
    keyboard.press_and_release("tab")
    time.sleep(1)
    keyboard.write("Roboto21")
    keyboard.press_and_release("enter")


def approve(webd):
    while True:
        WebDriverWait(webd, 30).until(
            EC.presence_of_element_located((By.ID, "TaskListFrame"))
        )
        # go to solped listing frame
        webd.switch_to.frame("TaskListFrame")
        solpeds = webd.find_elements(By.ID, "GridView1$ctl02_table")
        if solpeds:
            # select last solped of first page
            pyautogui.click((510, 643))
            time.sleep(3)
            # dismiss non-IE alert if present
            try:
                webd.switch_to.alert.accept()
            except:
                pass
            time.sleep(3)
        else:
            webd.quit()
            return
        # back to main frame

        webd.switch_to.default_content()
        time.sleep(2)
        # press tab 50 times to ensure "Approve" button is clickable
        for _ in range(50):
            keyboard.press_and_release("tab")
            time.sleep(0.1)
        # approve
        try:
            webd.find_element(By.ID, "Approve").click()
        except ElementNotInteractableException:
            print("Cannot find Approve button")
            quit()

        # keep list of approvals
        time.sleep(3)


def main():
    # turn on GlobalProtect VPN manually
    turn_on_vpn()

    # open web page
    url = "http://winshuttle.losportales.com.pe:82/prd/default.aspx"
    webd = ChromeUtils().init_driver(headless=False, verbose=False)
    webd.get(url)

    # login credentials
    login()

    # do approvals (no output captured)
    approve(webd)

    # turn off GlobalProtect VPN
    turn_off_vpn()


main()
