from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time, sys
import csv, json
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io
import urllib
import shutil
from copy import deepcopy as copy
import uuid
import threading

import easyocr


# from pprint import pprint as print


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class Central:
    def __init__(self) -> None:
        self.count = 0
        self.errors = 0


def transform_csv_to_json(csv_path):
    # define function that creates dictionary structure of vehiculo
    create_vehiculo = lambda i: {
        "placa": i[4],
        "rtecs": [
            {
                "certificadora": "",
                "certificado": "",
                "fecha_desde": "",
                "fecha_hasta": "",
                "resultado": "",
                "estado": "",
                "servicio": "",
                "observaciones": "",
            }
        ],
    }
    create_record = lambda i: {
        "nombre": i[0].strip(),
        "documento": {"tipo": i[1], "numero": i[2]},
        "telefono": i[3],
        "vehiculos": vehiculos,
    }
    # open raw csv data file
    with open(csv_path, mode="r", encoding="utf-8-sig") as csv_file:
        csv_data = [
            [i.strip().upper() for i in j] for j in csv.reader(csv_file, delimiter=",")
        ]
    # process data to accumulate different placas for same person (record)
    json_data = []
    for k, row in enumerate(csv_data):
        # if no name in date, ignore record
        if not row[0]:
            continue
        # if first record, load into memory and go to next one
        if k == 0:
            previous_row = copy(row)
            vehiculos = [create_vehiculo(row)]
            continue
        # if name is the same as previous, accumulate placa, else write record
        if row[0] == previous_row[0]:
            vehiculos.append(create_vehiculo(row))
            continue
        else:
            json_data.append(create_record(previous_row))
            vehiculos = [create_vehiculo(row)]
            previous_row = copy(row)
    # wrap-up with last pending record
    json_data.append(create_record(previous_row))
    # write into json format file
    with open("rtec_data.json", "a+", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)


def run_full_update(database, start_record, end_record):
    # define Chromedrive
    WEBD = ChromeUtils().init_driver(headless=True, verbose=True, maximized=True)
    # open webpage for first time
    WEBD.get(URL)
    time.sleep(5)

    counter = 1
    for record_index, record in enumerate(
        database[start_record:end_record], start=start_record
    ):
        # print(f"from {start_record}:{end_record} = {record_index}")
        GLOBAL.count += 1
        print(f"{GLOBAL.count/len(database)*100:.2f}%", end="\r")
        # print(GLOBAL.count)
        try:
            actualizado = dt.strptime(
                record["vehiculos"][0]["rtecs_actualizado"], "%d/%m/%Y"
            )
        except:
            print(record)
            continue
        for pos, vehiculo in enumerate(record["vehiculos"]):
            placa = vehiculo["placa"]
            if record_needs_updating(vehiculo["rtecs"], actualizado):
                try:
                    update_database(
                        scrape_data=process(placa, WEBD),
                        database=database,
                        record=record_index,
                        pos=pos,
                    )
                    WEBD.get(URL)
                    time.sleep(1)
                    counter += 1
                except (NoSuchElementException, ElementNotInteractableException):
                    print(record)
                    GLOBAL.errors += 1
                    if GLOBAL.errors > 10:
                        print("Exceeded max error count. End Thread.")
                        quit()
                    else:
                        print(f"Error #{GLOBAL.errors} Caught. Sleep and Retry.")
                        time.sleep(60)

        # write database to disk every n captures
        if counter % WRITE_FREQUENCY == 0:
            write_database(database)

    # last write in case there are pending changes in memory
    write_database(database)


def record_needs_updating(rtecs, actualizado):
    """Checks if record meets criteria for updating"""

    # Check: last update was longer than n days from today
    if dt.now() - actualizado < td(days=DAYS_BEFORE_UPDATE):
        return False

    # Check: there is no data for rtecs
    if not rtecs:
        return True

    # Check: fecha_hasta is in the past (with margin)
    if dt.strptime(rtecs[0]["fecha_hasta"], "%d/%m/%Y") > dt.now() - td(
        days=DAYS_BEFORE_EXPIRY
    ):
        return False

    # If all tests succeed, update record
    return True


def process(placa, WEBD):
    retry = False
    while True:
        # get captcha in string format
        captcha_txt = ""
        while not captcha_txt:
            if retry:
                WEBD.refresh()
            _captcha_img_url = WEBD.find_element(By.ID, "imgCaptcha").get_attribute(
                "src"
            )
            _img = Image.open(
                io.BytesIO(urllib.request.urlopen(_captcha_img_url).read())
            )
            captcha_txt = ocr(_img)
            retry = True

        # enter data into fields and run
        WEBD.find_element(By.ID, "txtPlaca").send_keys(placa)
        time.sleep(0.5)
        WEBD.find_element(By.ID, "txtCaptcha").send_keys(captcha_txt)
        time.sleep(0.5)
        WEBD.find_element(By.ID, "BtnBuscar").click()
        time.sleep(2)

        # if captcha is not correct, refresh and restart cycle, if no data found, return None
        _alerta = WEBD.find_element(By.ID, "lblAlertaMensaje").text
        if "no es correcto" in _alerta:
            continue
        elif "encontraron resultados" in _alerta:
            return None
        else:
            break

    # extract data from table and parse relevant data
    response = {}
    data_index = (
        ("certificadora", 1),
        ("placa", 1),
        ("certificado", 2),
        ("fecha_desde", 3),
        ("fecha_hasta", 4),
        ("resultado", 5),
        ("vigencia", 6),
    )
    for data_unit, pos in data_index:
        response.update(
            {
                data_unit: WEBD.find_element(
                    By.XPATH,
                    f"/html/body/form/div[4]/div/div/div[2]/div[2]/div/div/div[6]/div[{'2' if data_unit == 'empresa' else '3'}]/div/div/div/table/tbody/tr[2]/td[{pos}]",
                ).text
            }
        )
    return [response]


def ocr(img):
    """Use offline EasyOCR to convert captcha image to text"""
    result = READER.readtext(img, text_threshold=0.5)
    return result[0][1] if len(result) > 0 and len(result[0]) > 0 else ""


def backup_database():
    shutil.copyfile(
        "rtec_data.json",
        f"rtec_data_backup_{str(uuid.uuid4())[:8]}.json",
        follow_symlinks=True,
    )


def load_database():
    with open("rtec_data.json", mode="r") as file:
        return json.load(file)


def update_database(scrape_data, database, record, pos):
    # update record of entire database with new rtec info and last update date
    database[record]["vehiculos"][pos]["rtecs"] = scrape_data
    database[record]["vehiculos"][pos]["rtecs_actualizado"] = dt.now().strftime(
        "%d/%m/%Y"
    )
    return database


def write_database(database):
    LOCK.acquire()
    with open("rtec_data.json", "w+") as file:
        json.dump(database, file, indent=4)
    LOCK.release()


def update_database_correlatives():
    database = load_database()
    for k, _ in enumerate(database):
        database[k]["correlative"] = k
    write_database(database)


def main():

    # create copy of database with distinct name before manipulating
    backup_database()

    # load current database into memory
    database = load_database()

    # iterate on all records in database and update the necessary ones, open n threads
    _block = len(database) // NUMBER_THREADS
    active_threads = []
    for thread in range(NUMBER_THREADS):
        _start = thread * _block
        _end = (
            len(database) if thread == (NUMBER_THREADS - 1) else (thread + 1) * _block
        )
        _t = threading.Thread(target=run_full_update, args=(database, _start, _end))
        active_threads.append(_t)
        _t.start()
    for single_thread in active_threads:
        single_thread.join()

    # once database has been updated, reset the correlatives
    # update_database_correlatives()


# define constants
WRITE_FREQUENCY = 50
DAYS_BEFORE_UPDATE = 7
DAYS_BEFORE_EXPIRY = 15
NUMBER_THREADS = 2

READER = easyocr.Reader(["es"], gpu=False)
URL = "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"
LOCK = threading.Lock()
GLOBAL = Central()

main()
