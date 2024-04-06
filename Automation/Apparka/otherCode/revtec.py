from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time, sys
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib
import easyocr
from tqdm import tqdm
import threading
import random


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class RevTec:
    # define class constants
    URL = "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"

    def __init__(self, database, logger, monitor, options) -> None:
        self.counter = 0
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.DB = database
        self.LOG = logger
        self.MONITOR = monitor
        self.TIMEOUT = 14460

    def run_full_update(self):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        # log start of process
        self.LOG.info(f"REVTEC > Begin.")

        # create list of all records that need updating with priorities
        records_to_update = self.list_records_to_update()
        self.MONITOR.total_records[1] = len(records_to_update)

        self.LOG.info(f"REVTEC > Will process {len(records_to_update):,} records.")

        # begin update
        process_complete = False
        while not process_complete:
            # set complete flag to True, changed if process stalled
            process_complete = True

            # define Chromedriver and open url for first time
            self.WEBD = ChromeUtils().init_driver(
                headless=True, verbose=False, maximized=True
            )
            self.WEBD.get(self.URL)
            time.sleep(2)

            rec = 0
            # iterate on all records that require updating
            for rec, (record_index, position) in enumerate(records_to_update):
                # update monitor dashboard data
                self.MONITOR.current_record[1] = rec + 1
                # get scraper data, if webpage fails, wait, reload page and skip record
                _placa = self.DB.database[record_index]["vehiculos"][position]["placa"]
                try:
                    new_record = self.scraper(placa=_placa)
                except KeyboardInterrupt:
                    quit()
                except:
                    time.sleep(1)
                    self.WEBD.refresh()
                    time.sleep(1)
                    continue

                # if record has data and response is None, do not overwrite database
                if (
                    not new_record
                    and self.DB.database[record_index]["vehiculos"][position]["rtecs"]
                ):
                    continue

                # update brevete data and last update in database
                self.DB.database[record_index]["vehiculos"][position][
                    "rtecs"
                ] = new_record
                self.DB.database[record_index]["vehiculos"][position][
                    "rtecs_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")

                # check monitor flags: timeout
                if self.MONITOR.timeout_flag:
                    # self.DB.write_database()
                    self.LOG.info(f"End RevTec (Timeout). Processed {rec} records.")
                    self.WEBD.close()
                    return

                # check monitor flags: stalled
                if self.MONITOR.stalled:
                    # set complete flag to False to force restart of updating process
                    process_complete = False
                    # close current webdriver session and wait
                    self.WEBD.close()
                    time.sleep(5)
                    # update monitor stats
                    # self.MONITOR.last_change = dt.now()
                    break

        # last write in case there are pending changes in memory (only if for loop ran)
        if rec:
            self.DB.write_database()
        # log end of process
        self.LOG.info(f"REVTEC > End (Complete). Processed: {rec} records.")

    def list_records_to_update(self, last_update_threshold=7):

        to_update = [[] for _ in range(5)]

        for record_index, record in enumerate(self.DB.database):
            vehiculos = record["vehiculos"]

            for veh_index, vehiculo in enumerate(vehiculos):
                actualizado = dt.strptime(vehiculo["rtecs_actualizado"], "%d/%m/%Y")
                rtecs = vehiculo["rtecs"]

                # Skip all records than have already been updated in same date
                if dt.now() - actualizado <= td(days=1):
                    continue

                # Priority 0: rtec will expire in 3 days or has expired in the last 60 days
                if rtecs and rtecs[0]["fecha_hasta"]:
                    hasta = dt.strptime(rtecs[0]["fecha_hasta"], "%d/%m/%Y")
                    if td(days=-3) <= dt.now() - hasta <= td(days=60):
                        to_update[0].append((record_index, veh_index))

                # Priority 1: rtecs with no fecha hasta
                if rtecs and not rtecs[0]["fecha_hasta"]:
                    to_update[1].append((record_index, veh_index))

                # Priority 2: no rtec information and last update was 7+ days ago
                if not rtecs and dt.now() - actualizado >= td(
                    days=last_update_threshold
                ):
                    to_update[2].append((record_index, veh_index))

                # Priority 3: rtec will expire in more than 60 days and last update was 7+ days ago
                if dt.now() - hasta > td(days=60) and dt.now() - actualizado >= td(
                    days=last_update_threshold
                ):
                    to_update[3].append((record_index, veh_index))

        # build flat list of records in order
        return [i for j in to_update for i in j]

    def scraper(self, placa):
        retry_captcha = False
        while True:
            # get captcha in string format
            captcha_txt = ""
            while not captcha_txt:
                if retry_captcha:
                    self.WEBD.refresh()
                    time.sleep(1)
                # captura captcha image from webpage store in variable
                _captcha_img_url = self.WEBD.find_element(
                    By.ID, "imgCaptcha"
                ).get_attribute("src")
                _img = Image.open(
                    io.BytesIO(urllib.request.urlopen(_captcha_img_url).read())
                )
                # convert image to text using OCR
                _captcha = self.READER.readtext(_img, text_threshold=0.5)
                captcha_txt = (
                    _captcha[0][1] if len(_captcha) > 0 and len(_captcha[0]) > 0 else ""
                )
                retry_captcha = True

            # enter data into fields and run
            self.WEBD.find_element(By.ID, "txtPlaca").send_keys(placa)
            time.sleep(0.5)
            self.WEBD.find_element(By.ID, "txtCaptcha").send_keys(captcha_txt)
            time.sleep(0.5)
            self.WEBD.find_element(By.ID, "BtnBuscar").click()
            time.sleep(1)

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            _alerta = self.WEBD.find_element(By.ID, "lblAlertaMensaje").text
            if "no es correcto" in _alerta:
                continue
            elif "encontraron resultados" in _alerta:
                # clear webpage for next iteration and return None
                self.WEBD.refresh()
                time.sleep(0.5)
                return None
            else:
                break

        # extract data from table and parse relevant data, return a dictionary with RTEC data for each PLACA
        # TODO: capture ALL revisiones (not just latest) -- response not []
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
                    data_unit: self.WEBD.find_element(
                        By.XPATH,
                        f"/html/body/form/div[4]/div/div/div[2]/div[2]/div/div/div[6]/div[{'2' if data_unit == 'empresa' else '3'}]/div/div/div/table/tbody/tr[2]/td[{pos}]",
                    ).text
                }
            )

        # clear webpage for next response
        time.sleep(1)
        self.WEBD.refresh()
        time.sleep(1)

        return [response]
