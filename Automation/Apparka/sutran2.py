from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime as dt, timedelta as td
import time


def rtu(DB, last_update_threshold):
    to_update = []
    for record_index, record in enumerate(DB.database):
        vehiculos = record["vehiculos"]
        for veh_index, vehiculo in enumerate(vehiculos):
            actualizado = dt.strptime(
                vehiculo["multas"]["sutran_actualizado"], "%d/%m/%Y"
            )

            # Skip all records than have already been updated in last day
            if dt.now() - actualizado < td(days=1):
                continue

            # Priority 0: last update over 30 days
            if dt.now() - actualizado >= td(days=last_update_threshold):
                to_update[0].append((record_index, veh_index))

    return to_update


def scraper(WEBD, placa):
    captcha_attempts = 0

    while True:
        # capture captcha image from frame name
        _iframe = WEBD.find_element(By.CSS_SELECTOR, "iframe")
        WEBD.switch_to.frame(_iframe)
        captcha_txt = (
            WEBD.find_element(By.ID, "iimage").get_attribute("src").split("=")[-1]
        )
        captcha_txt = captcha_txt.replace("%C3%91", "Ñ")

        # enter data into fields and run
        WEBD.find_element(By.ID, "txtPlaca").send_keys(placa)
        time.sleep(0.2)
        elements = (
            WEBD.find_elements(By.ID, "TxtCodImagen"),
            WEBD.find_elements(By.ID, "BtnBuscar"),
        )
        if not elements[0] or not elements[1]:
            WEBD.refresh()
            continue
        else:
            elements[0][0].send_keys(captcha_txt)
            time.sleep(0.2)
            elements[1][0].click()
        time.sleep(0.5)

        # captcha tries counter
        captcha_attempts += 1

        # if no text response, restart
        elements = WEBD.find_elements(By.ID, "LblMensaje")
        if elements:
            _alerta = WEBD.find_element(By.ID, "LblMensaje").text
        else:
            WEBD.refresh()
            continue
        # if no pendings, clear webpage for next iteration and return None
        if "pendientes" in _alerta:
            WEBD.refresh()
            time.sleep(0.2)
            return []
        else:
            break

    response = {}
    data_index = (
        ("documento", 1),
        ("tipo", 2),
        ("fecha_documento", 3),
        ("codigo_infraccion", 4),
        ("clasificacion", 5),
    )
    for data_unit, pos in data_index:
        response.update(
            {
                data_unit: WEBD.find_element(
                    By.XPATH,
                    f"/html/body/form/div[3]/div[3]/div/table/tbody/tr[2]/td[{pos}]",
                ).text
            }
        )
    # clear webpage for next search
    WEBD.refresh()
    time.sleep(0.2)

    return response, captcha_attempts
