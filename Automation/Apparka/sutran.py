from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time, sys
from datetime import datetime as dt, timedelta as td
import easyocr
from tqdm import tqdm
import threading
import random

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils
import monitor


class Sutran:
    # define class constants
    URL = "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/"
    WRITE_FREQUENCY = 50

    def __init__(self, database, logger, monitor, options) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.DB = database
        self.LOG = logger
        self.MONITOR = monitor
        self.TIMEOUT = 14430

    def run_full_update(self):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        # log start of process
        self.LOG.info(f"SUTRAN > Begin.")

        # create list of all records that need updating with priorities
        records_to_update = self.list_records_to_update()
        self.MONITOR.total_records[2] = len(records_to_update)

        self.LOG.info(f"SUTRAN > Will process {len(records_to_update)} records.")

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
                self.MONITOR.current_record[2] = rec + 1
                # get scraper data, if webpage fails skip record
                _placa = self.DB.database[record_index]["vehiculos"][position]["placa"]
                try:
                    new_record = self.scraper(placa=_placa)
                except KeyboardInterrupt:
                    quit()
                except:
                    self.LOG.warning("SUTRAN > Skipped Record {rec}.")
                    time.sleep(1)
                    self.WEBD.refresh()
                    time.sleep(1)
                    continue

                # if record has data and response is None, do not overwrite database
                # if (
                #     not new_record
                #     and self.DB.database[record_index]["vehiculos"][position]["multas"][
                #         "sutran"
                #     ]
                # ):
                #     continue

                # update sutran data and last update in database
                self.DB.database[record_index]["vehiculos"][position]["multas"][
                    "sutran"
                ] = new_record
                self.DB.database[record_index]["vehiculos"][position]["multas"][
                    "sutran_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")

                # check monitor flags: timeout
                if self.MONITOR.timeout_flag:
                    # self.DB.write_database()
                    self.LOG.info(f"SUTRAN > End (Timeout). Processed {rec} records.")
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
        self.LOG.info(f"SUTRAN > End (Complete). Processed: {rec} records.")

    def list_records_to_update(self):

        to_update = [[] for _ in range(2)]

        for record_index, record in enumerate(self.DB.database):
            vehiculos = record["vehiculos"]
            for veh_index, vehiculo in enumerate(vehiculos):
                actualizado = dt.strptime(
                    vehiculo["multas"]["sutran_actualizado"], "%d/%m/%Y"
                )

                # Skip all records than have already been updated in last 22 hours
                if dt.now() - actualizado < td(days=1):
                    continue

                # Priority 0: last update over 30 days
                if dt.now() - actualizado >= td(days=30):
                    to_update[0].append((record_index, veh_index))

        # flatten list to records in order
        return [i for j in to_update for i in j]

    def scraper(self, placa):
        while True:
            # capture captcha image from frame name
            _iframe = self.WEBD.find_element(By.CSS_SELECTOR, "iframe")
            self.WEBD.switch_to.frame(_iframe)
            captcha_txt = (
                self.WEBD.find_element(By.ID, "iimage")
                .get_attribute("src")
                .split("=")[-1]
            )
            captcha_txt = captcha_txt.replace("%C3%91", "Ñ")

            # enter data into fields and run
            self.WEBD.find_element(By.ID, "txtPlaca").send_keys(placa)
            time.sleep(0.2)
            elements = (
                self.WEBD.find_elements(By.ID, "TxtCodImagen"),
                self.WEBD.find_elements(By.ID, "BtnBuscar"),
            )
            if not elements[0] or not elements[1]:
                self.WEBD.refresh()
                continue
            else:
                elements[0][0].send_keys(captcha_txt)
                time.sleep(0.2)
                elements[1][0].click()
            time.sleep(0.5)

            # if no text response, restart
            elements = self.WEBD.find_elements(By.ID, "LblMensaje")
            if elements:
                _alerta = self.WEBD.find_element(By.ID, "LblMensaje").text
            else:
                self.WEBD.refresh()
                continue
            # if no pendings, clear webpage for next iteration and return None
            if "pendientes" in _alerta:
                self.WEBD.refresh()
                time.sleep(0.2)
                return None
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
                    data_unit: self.WEBD.find_element(
                        By.XPATH,
                        f"/html/body/form/div[3]/div[3]/div/table/tbody/tr[2]/td[{pos}]",
                    ).text
                }
            )
        # clear webpage for next search
        self.WEBD.refresh()
        time.sleep(0.2)

        return response
