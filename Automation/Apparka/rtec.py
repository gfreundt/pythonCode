from selenium.webdriver.common.by import By
import time, sys
from PIL import Image
import io
import urllib
from copy import deepcopy as copy

import easyocr
import csv, json


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


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
        "documento": {"tipo": i[1], "num_doc": i[2]},
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
    with open("test.json", "w+", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)


def process(placa):
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

        # if captcha is not correct, refresh and restart cycle
        if len(WEBD.find_element(By.ID, "lblAlertaMensaje").text) < 3:
            break

    # extract data from table and parse relevant data
    response = {}
    data_index = (
        ("empresa", 1),
        ("placa", 1),
        ("certificado", 2),
        ("desde", 3),
        ("hasta", 4),
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
    return response


def ocr(img):
    """Use offline EasyOCR to convert captcha image to text"""
    result = READER.readtext(img, text_threshold=0.5)
    return result[0][1] if len(result) > 0 and len(result[0]) > 0 else ""


def load_database():
    with open("rtec_data.json", mode="r") as file:
        return json.load(file)


def main():
    url = "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"
    WEBD.get(url)
    time.sleep(2)

    database = load_database()
    for record in database[667:670]:
        for vehiculo in record["vehiculos"]:
            print("*******", vehiculo["placa"])
            r = process(vehiculo["placa"])
            print(r)
            WEBD.get(url)
            time.sleep(2)


READER = easyocr.Reader(["es"], gpu=False)
WEBD = ChromeUtils().init_driver(headless=False, verbose=True, maximized=True)

main()
