from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import os, time, sys
import keyboard
from subprocess import Popen
import pyautogui
import pyperclip

import easyocr

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


def parse(text, start, end):
    if end in text:
        e = text.find(end) - 2
        txt = text[e - 100 : e].strip().split("\n")[-1]
        return txt
    else:
        return False

    s, e = text.find(start) + len(start) + 1, text.find(end) - 1
    txt = text[s:e].strip()
    print(txt, s, e)
    while "\n" in txt:
        txt = txt[txt.find("\n") + 2 :]
    return txt


def extract():
    idx = [
        ("apellidos", "conductor", "Apellidos"),
        ("nombre", "Apellidos", "Nombres"),
        ("clase", "Licencia:", "Clase y categ"),
        ("numero", "Clase y categ", "Número de licencia"),
        ("tipo", "mero de licencia", "Tipo de Licencia"),
        ("fecha_exp", "Tipo de Licencia", "Fecha de expedi"),
        ("restricciones", "expedici", "Restricciones"),
        ("fecha_vig", "", "Vigente hasta"),
        ("centro_emision", "", "Centro de emisi"),
        ("puntos", "", "puntos"),
        ("papeletas", "", "No se encontraron papeletas para el administrado"),
    ]

    with open("temp.txt", "r", encoding="utf-8") as file:
        text = file.read()
    # data = {i[0]: parse(text, i[1], i[2]) for i in idx}
    data = ",".join([parse(text, i[1], i[2]) for i in idx]) + "\n"
    return data


def process(url, dni):
    webd = ChromeUtils().init_driver(headless=False, verbose=True, maximized=True)
    webd.get(url)
    time.sleep(4)

    captcha_ok = False
    while not captcha_ok:
        # captura captcha, OCR it and enter into field
        pyautogui.screenshot(region=(1721, 824, 293, 69)).save("test.png")
        captcha = ocr("test.png")
        captchabox = webd.find_element(By.ID, "mat-input-0")
        captchabox.send_keys(captcha)

        # input DNI in field
        time.sleep(2)
        inputbox = webd.find_element(By.ID, "mat-input-1")
        inputbox.send_keys(dni)

        # accept conditions
        time.sleep(2)
        for _ in range(6):
            keyboard.press_and_release("tab")
            time.sleep(0.1)
        keyboard.press_and_release("space")

        # click on button
        time.sleep(2)
        button = webd.find_element(
            By.XPATH,
            "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[5]/div[1]/button",
        )
        button.click()

        # check if error popup (DNI not found or wrong captcha)
        time.sleep(3)
        _popup = webd.find_elements(By.ID, "swal2-html-container")
        if _popup:
            if "captcha" in _popup[0].text:
                captcha_ok = False
                webd.refresh()
                time.sleep(2)
            elif "natural" in _popup[0].text:
                webd.close()
                return False
        else:
            captcha_ok = True

    # extract information from webpage and write to temp file
    tabs = ((1304, 780), (1530, 780), (1777, 780), (2054, 780), (2332, 780))
    for k, tab in enumerate(tabs):
        pyautogui.click(tab)
        time.sleep(2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        with open("temp.txt", "w" if k == 0 else "a+", encoding="utf-8") as outfile:
            outfile.write(pyperclip.paste())
            outfile.write("\n")
            outfile.write("****************************************")
            outfile.write("\n")

    webd.close()
    return True


def ocr(image_path):
    """Use offline EasyOCR to convert captcha image to text"""
    READER = easyocr.Reader(["es"], gpu=False)
    result = READER.readtext(image_path)
    if len(result) > 0 and len(result[0]) > 0:
        return result[0][1]
    else:
        return ""


def output_file(data_ok, dni):
    with open("output.txt", "a+", encoding="utf-8") as outfile:
        if data_ok:
            outfile.write(extract())
        else:
            outfile.write(dni + "Sin data\n")


def main():
    # load DNI list
    DNIS = [i.strip() for i in open("dnis.txt", mode="r").readlines()]

    # open web page
    url = "https://licencias.mtc.gob.pe/#/index"

    # cycle all DNIS in reuqest and write to consolidated output file
    for dni in DNIS:
        result = process(url, dni)
        output_file(result, dni)


main()
