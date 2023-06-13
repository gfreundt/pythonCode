from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time
import keyboard


def load_webdriver():
    """Define options for Chromedriver"""
    options = WebDriverOptions()
    # options.add_argument("--window-size=1920,1080")
    options.add_argument("--silent")
    options.add_argument("--disable-notifications")
    options.add_argument("--incognito")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(
        service=Service(os.path.join(r"C:\pythonCode\Resources", "chromedriver.exe")),
        options=options,
    )


def approve(solped):
    webd.get()


def login():
    time.sleep(5)
    keyboard.write("gfreundt")
    keyboard.press_and_release("tab")
    keyboard.write("Subaru21")
    keyboard.press_and_release("enter")


url = "http://winshuttle.losportales.com.pe:82/prd/default.aspx"
webd = load_webdriver()
webd.get(url)

login()

counter = 0

while True:
    WebDriverWait(webd, 10).until(
        EC.presence_of_element_located((By.ID, "TaskListFrame"))
    )
    webd.switch_to.frame("TaskListFrame")
    solpeds = webd.find_elements(By.ID, "GridView1$ctl02_table")
    print("elements:", solpeds)
    if solpeds:
        counter += 1
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
    time.sleep(10)

print(f"Completo con {counter} aprobaciones.")
