from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time, sys
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib
import easyocr
from tqdm import tqdm
import threading

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils
import monitor


class Sutran:
    # define class constants
    URL = "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/"

    def __init__(self) -> None:
        self.WRITE_FREQUENCY = 200
        self.NUMBER_OF_THREADS = 7
        self.READER = easyocr.Reader(["es"], gpu=False)

    def run_threads(self, nothreads=False):
        records_to_update = self.list_records_to_update()
        if nothreads:
            self.run_full_update(records_to_update)
        else:
            # split records to update among all threads equally, except last one that catches the tail
            _block_size = len(records_to_update) // (self.NUMBER_OF_THREADS - 1)
            thread_records_to_update = [
                records_to_update[i * _block_size : (i + 1) * _block_size]
                for i in range(self.NUMBER_OF_THREADS - 1)
            ]
            thread_records_to_update.append(
                records_to_update[_block_size * (self.NUMBER_OF_THREADS - 1) :]
            )
            threads = []
            for thread_num in range(self.NUMBER_OF_THREADS):
                _next_thread = threading.Thread(
                    target=self.run_full_update,
                    args=(
                        thread_records_to_update[thread_num],
                        thread_num,
                        _block_size,
                    ),
                )
                threads.append(_next_thread)
                _next_thread.start()
                time.sleep(5)
            # join all created threads
            for thread in threads:
                thread.join()

    def run_full_update(self, records_to_update, thread_num=-1, block_size=0):
        # calculate total number of records to process
        MONITOR.total_records_sutran = len(records_to_update)

        # log start of process
        if thread_num == -1:
            LOG.info(
                f"Begin SUTRAN (No Threading). Will process {MONITOR.total_records_sutran} records."
            )
        else:
            LOG.info(
                f"SUTRAN Thread {thread_num} begin. Will process {MONITOR.total_records_sutran} records."
            )

        # define Chromedriver and open url for first time
        self.WEBD = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True
        )
        self.WEBD.get(self.URL)
        time.sleep(2)

        # iterate on all records that require updating
        for rec, (record_index, position) in tqdm(
            enumerate(records_to_update, start=thread_num * block_size),
            total=len(records_to_update),
        ):
            MONITOR.progress = rec
            # get scraper data, if webpage fails skip record
            _placa = DATABASE.database[record_index]["vehiculos"][position]["placa"]
            try:
                new_record = self.scraper(placa=_placa, nt=thread_num)
            except KeyboardInterrupt:
                quit()
            except:
                continue

            # if database has data and response is None, do not overwrite database
            if (
                not new_record
                and DATABASE.database[record_index]["vehiculos"][position]["multas"][
                    "sutran"
                ]
            ):
                continue

            # update sutran data and last update in database (introduce random delta days for even distribution)
            # TODO: eliminate random in 30 days
            DATABASE.database[record_index]["vehiculos"][position]["multas"][
                "sutran"
            ] = new_record
            DATABASE.database[record_index]["vehiculos"][position]["multas"][
                "sutran_actualizado"
            ] = (dt.now() - td(days=random.randrange(0, 30))).strftime("%d/%m/%Y")

            MONITOR.pending_writes += 1

            # write database to disk every n captures
            if MONITOR.pending_writes % self.WRITE_FREQUENCY == 0:
                MONITOR.pending_writes = 0
                MONITOR.writes += self.WRITE_FREQUENCY
                DATABASE.write_database()

        # last write in case there are pending changes in memory
        DATABASE.write_database()

        # log end of process
        LOG.info(f"End Sutran.")

    def list_records_to_update(self):
        to_update = [[] for _ in range(2)]
        for record_index, record in enumerate(DATABASE.database):
            vehiculos = record["vehiculos"]
            for veh_index, vehiculo in enumerate(vehiculos):
                actualizado = dt.strptime(
                    vehiculo["multas"]["sutran_actualizado"], "%d/%m/%Y"
                )
                # Skip all records than have already been updated in last 24 hours
                if dt.now() - actualizado < td(days=1):
                    continue
                # Priority 0: last update over 30 days
                if dt.now() - actualizado >= td(days=30):
                    to_update[0].append((record_index, veh_index))

        # flatten list to records in order
        return [i for j in to_update for i in j]

    def scraper(self, placa, nt):
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

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            elements = self.WEBD.find_elements(By.ID, "LblMensaje")
            if elements:
                _alerta = self.WEBD.find_element(By.ID, "LblMensaje").text
            else:
                self.WEBD.refresh()
                continue
            # self.WEBD.switch_to.default_content()

            if "incorrecto" in _alerta:
                continue
            elif "pendientes" in _alerta:
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
        # clear webpage for next iteration and small wait
        self.WEBD.refresh()
        time.sleep(0.2)

        return response
