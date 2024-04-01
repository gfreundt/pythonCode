from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time, sys
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib
import logging
import easyocr
from gft_utils import ChromeUtils

# remove easyocr warnings
logging.getLogger("easyocr").setLevel(logging.ERROR)


class Revtec:
    URL = "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"

    def __init__(self, **kwargs):
        # self.counter = 0
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.DB = kwargs["database"]
        self.LOG = kwargs["logger"]
        self.MONITOR = kwargs["monitor"]
        self.options = kwargs["options"]
        self.thread_num = kwargs["threadnum"]

    def run_full_update(self):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA."""

        # log start of process
        self.LOG.info(f"REVTEC > Begin.")

        # create list of all records that need updating with priorities
        records_to_update = self.list_records_to_update()

        self.MONITOR.threads[self.thread_num]["total_records"] = len(records_to_update)

        # if no records to update, log end of process
        if not records_to_update:
            self.LOG.info(f"REVTEC > End (Did not start). No records to process.")
            return
        else:
            self.LOG.info(f"REVTEC > Will process {len(records_to_update):,} records.")

        # define Chromedriver and open url for first time
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, incognito=True
        )
        self.WEBD.get(self.URL)
        time.sleep(2)

        rec = 0  # only in case for loop doesn't run

        # iterate on all records that require updating
        for rec, (record_index, position) in enumerate(records_to_update):
            # update monitor dashboard data
            self.MONITOR.threads[self.thread_num]["current_record"] = rec + 1

            # get scraper data, if webpage fails, wait, reload page and skip record
            _placa = self.DB.database[record_index]["vehiculos"][position]["placa"]
            try:
                new_record = self.scraper(placa=_placa)
            except KeyboardInterrupt:
                quit()
            except:
                self.LOG.warning(f"REVTEC > Skipped Record {rec}.")
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
            self.DB.database[record_index]["vehiculos"][position]["rtecs"] = new_record
            self.DB.database[record_index]["vehiculos"][position][
                "rtecs_actualizado"
            ] = dt.now().strftime("%d/%m/%Y")
            # timestamp
            self.MONITOR.threads[self.thread_num]["last_record_updated"] = time.time()

            # check monitor flags: timeout
            if self.MONITOR.timeout_flag:
                # self.DB.write_database()
                self.LOG.info(f"End RevTec (Timeout). Processed {rec+1} records.")
                self.WEBD.close()
                return

        # log end of process
        self.LOG.info(f"REVTEC > End (Complete). Processed: {rec+1} records.")

    def list_records_to_update(self, last_update_threshold=15):

        self.MONITOR.threads[self.thread_num]["lut"] = last_update_threshold

        to_update = [[] for _ in range(5)]

        for record_index, record in enumerate(self.DB.database):

            for veh_index, vehiculo in enumerate(record["vehiculos"]):
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
