from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time, sys
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib
import threading
import easyocr
from tqdm import tqdm
import logging
import random


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils, GoogleUtils
import monitor, database, revtec


class RevTec:
    # define class constants
    WRITE_FREQUENCY = 200

    URL = "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"

    def __init__(self) -> None:
        self.counter = 0
        self.READER = easyocr.Reader(["es"], gpu=False)

    def run_full_update(self):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        # log start of process
        LOG.info(f"Begin RevTec Iteration {MONITOR.iteration}.")

        # create list of all records that need updating with priorities
        records_to_update, _threshold = self.list_records_to_update(target=2500)
        MONITOR.total_records_revtec = len(records_to_update)
        LOG.info(
            f"Will process {MONITOR.total_records_revtec} records. Threshold: {_threshold} days."
        )
        return

        process_complete = False
        while not process_complete:
            # set complete flag to True, changed if process stalled
            process_complete = True

            # define Chromedriver and open url for first time
            self.WEBD = ChromeUtils().init_driver(
                headless=False, verbose=False, maximized=True
            )
            self.WEBD.get(self.URL)
            time.sleep(2)

            # iterate on all records that require updating
            for rec, (record_index, position) in tqdm(
                enumerate(records_to_update), total=len(records_to_update)
            ):
                MONITOR.progress = rec
                # get scraper data, if webpage fails, wait, reload page and skip record
                _placa = DATABASE.database[record_index]["vehiculos"][position]["placa"]
                try:
                    new_record = self.scraper(placa=_placa)
                except KeyboardInterrupt:
                    quit()
                # except:
                #     time.sleep(0.5)
                #     self.WEBD.refresh()
                #     time.sleep(1)
                #     continue

                # if database has data and response is None, do not overwrite database
                if (
                    not new_record
                    and DATABASE.database[record_index]["vehiculos"][position]["rtecs"]
                ):
                    continue
                # update brevete data and last update in database
                DATABASE.database[record_index]["vehiculos"][position][
                    "rtecs"
                ] = new_record
                DATABASE.database[record_index]["vehiculos"][position][
                    "rtecs_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")

                MONITOR.pending_writes += 1

                # write database to disk every n captures
                if MONITOR.pending_writes % self.WRITE_FREQUENCY == 0:
                    MONITOR.pending_writes = 0
                    MONITOR.writes += self.WRITE_FREQUENCY
                    DATABASE.write_database()

                # if monitor detects that process is stalled, restart
                if MONITOR.stalled:
                    # set complete flag to False to force restart of updating process
                    process_complete = False
                    # close current webdriver session and wait
                    self.WEBD.close()
                    time.sleep(1)
                    # update monitor stats
                    MONITOR.last_change = dt.now()
                    break

        # last write in case there are pending changes in memory
        DATABASE.write_database()
        # log end of process
        LOG.info(f"End RevTec Iteration {MONITOR.iteration}.")

    def list_records_to_update(self, target=2500):

        flat_list = ["." for _ in range(target + 1)]
        last_update_threshhold = 5
        iterations = 0

        while len(flat_list) >= target and iterations < 15:
            to_update = [[] for _ in range(5)]

            for record_index, record in enumerate(DATABASE.database):
                vehiculos = record["vehiculos"]
                for veh_index, vehiculo in enumerate(vehiculos):
                    actualizado = dt.strptime(vehiculo["rtecs_actualizado"], "%d/%m/%Y")
                    rtecs = vehiculo["rtecs"]

                    # Skip all records than have already been updated in last 24 hours
                    if dt.now() - actualizado < td(days=1):
                        continue

                    # Priority 0: rtec will expire in 3 days or has expired in the last 30 days
                    if rtecs and rtecs[0]["fecha_hasta"]:
                        hasta = dt.strptime(rtecs[0]["fecha_hasta"], "%d/%m/%Y")
                        if td(days=-3) <= dt.now() - hasta <= td(days=30):
                            to_update[0].append((record_index, veh_index))

                    # Priority 1: rtecs with no fecha hasta
                    if rtecs and not rtecs[0]["fecha_hasta"]:
                        to_update[1].append((record_index, veh_index))

                    # Priority 2: no rtec information and last update was 10+ days ago
                    if not rtecs and dt.now() - actualizado >= td(
                        days=last_update_threshhold
                    ):
                        to_update[2].append((record_index, veh_index))

                    # Priority 3: rtec will expire in more than 30 days and last update was 10+ days ago
                    if dt.now() - hasta > td(days=30) and dt.now() - actualizado >= td(
                        days=last_update_threshhold
                    ):
                        to_update[3].append((record_index, veh_index))

            # build flat list of records in order
            flat_list = [i for j in to_update for i in j]

            # in case the amount of records exceed target, increase last update threshold days
            last_update_threshhold += 1
            iterations += 1

        return flat_list, last_update_threshhold

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

        # clear webpage for next iteration and small wait
        time.sleep(1)
        self.WEBD.refresh()
        time.sleep(1)

        return [response]


class Brevete:
    URL = "https://licencias.mtc.gob.pe/#/index"

    def __init__(self) -> None:
        # define class constants
        self.WRITE_FREQUENCY = 3
        # define OCR
        self.READER = easyocr.Reader(["es"], gpu=False)

    def run_full_update(self):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        # log start of process
        LOG.info(f"Begin Brevete Iteration {MONITOR.iteration}.")

        # create list of all records that need updating with priorities
        records_to_update = self.list_records_to_update()
        MONITOR.total_records_brevete = len(records_to_update)
        LOG.info(f"Will process {MONITOR.total_records_brevete} records.")

        process_complete = False
        while not process_complete:
            # set complete flag to True, changed if process stalled
            process_complete = True

            # define Chromedriver and open url for first time
            self.WEBD = ChromeUtils().init_driver(
                headless=False, verbose=False, incognito=True
            )
            self.WEBD.get(self.URL)
            time.sleep(2)

            # iterate on all records that require updating
            for rec, record_index in tqdm(
                enumerate(records_to_update), total=len(records_to_update)
            ):
                MONITOR.progress = rec

                # get scraper data, if webpage fails, refresh and skip record
                _dni = DATABASE.database[record_index]["documento"]["numero"]
                try:
                    new_record = self.scraper(dni=_dni)
                    # clear webpage for next iteration and small wait
                    time.sleep(1)
                    self.WEBD.back()
                    time.sleep(0.2)
                    self.WEBD.refresh()
                except:
                    self.WEBD.refresh()
                    time.sleep(1)
                    self.WEBD.get(self.URL)
                    time.sleep(1)
                    continue

                # if database has data and response is None, do not overwrite database
                if (
                    not new_record
                    and DATABASE.database[record_index]["documento"]["brevete"]
                ):
                    continue

                # update brevete data and last update in database
                DATABASE.database[record_index]["documento"]["brevete"] = new_record
                DATABASE.database[record_index]["documento"][
                    "brevete_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")

                # update monitor stats
                MONITOR.pending_writes += 1

                # write database to disk every n captures
                if MONITOR.pending_writes % self.WRITE_FREQUENCY == 0:
                    MONITOR.pending_writes = 0
                    MONITOR.writes += self.WRITE_FREQUENCY
                    DATABASE.write_database()

                # if monitor detects that process is stalled, restart
                if MONITOR.stalled:
                    # set complete flag to False to force restart of updating process
                    process_complete = False
                    # close current webdriver session and wait
                    self.WEBD.close()
                    time.sleep(1)
                    # update monitor stats
                    MONITOR.last_change = dt.now()
                    break

        # last write to capture any pending changes in database
        DATABASE.write_database()
        # log end of process
        LOG.info(f"End Brevete Iteration {MONITOR.iteration}.")

    def list_records_to_update(self):
        # switch to force updating all
        if "-all" in sys.argv:
            LOG.warning("-all switch selected.")
            return [i for i in range(DATABASE.len_database)]
        to_update = [[] for _ in range(3)]
        for record_index, record in enumerate(DATABASE.database):
            brevete = record["documento"]["brevete"]
            actualizado = dt.strptime(
                record["documento"]["brevete_actualizado"], "%d/%m/%Y"
            )

            # Skip all records than have already been updated in last 24 hours
            if dt.now() - actualizado < td(days=1):
                continue

            # Priority 0: brevete will expire in 3 days or has expired in the last 30 days
            if brevete:
                hasta = dt.strptime(brevete["fecha_hasta"], "%d/%m/%Y")
                if td(days=-3) <= dt.now() - hasta <= td(days=30):
                    to_update[0].append(record_index)

            # Priority 1: no brevete information and last update was 10+ days ago
            if not brevete and dt.now() - actualizado >= td(days=10):
                to_update[1].append(record_index)

            # Priority 2: brevete will expire in more than 30 days and last update was 10+ days ago
            if dt.now() - hasta > td(days=30) and dt.now() - actualizado >= td(days=10):
                to_update[2].append(record_index)

        # return flat list of records in order
        return [i for j in to_update for i in j]

    def scraper(self, dni):
        retry_captcha = False
        # outer loop: in case captcha is not accepted by webpage, try with a new one
        while True:
            captcha_txt = ""
            # inner loop: in case OCR cannot figure out captcha, retry new captcha
            while not captcha_txt:
                if retry_captcha:
                    self.WEBD.refresh()
                    time.sleep(1)
                # if monitor detects that process is stalled, exit scraper
                if MONITOR.stalled:
                    MONITOR.last_change = dt.now()
                    return
                # captura captcha image from webpage store in variable
                try:
                    _captcha_img_url = self.WEBD.find_element(
                        By.XPATH,
                        "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[3]/div[2]/img",
                    ).get_attribute("src")
                    _img = Image.open(
                        io.BytesIO(urllib.request.urlopen(_captcha_img_url).read())
                    )
                    # convert image to text using OCR
                    _captcha = self.READER.readtext(_img, text_threshold=0.5)
                    captcha_txt = (
                        _captcha[0][1]
                        if len(_captcha) > 0 and len(_captcha[0]) > 0
                        else ""
                    )
                    retry_captcha = True
                except ValueError:
                    # captcha image did not load, reset webpage
                    MONITOR.errors += 1
                    self.WEBD.refresh()
                    time.sleep(1.5)
                    self.WEBD.get(self.URL)
                    time.sleep(1.5)

            # enter data into fields and run
            self.WEBD.find_element(By.ID, "mat-input-1").send_keys(dni)
            self.WEBD.find_element(By.ID, "mat-input-0").send_keys(captcha_txt)
            self.WEBD.find_element(By.ID, "mat-checkbox-1").click()
            self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[5]/div[1]/button",
            ).click()
            time.sleep(1)

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            _alerta = self.WEBD.find_elements(By.ID, "swal2-html-container")
            if _alerta and "persona natural" in _alerta[0].text:
                MONITOR.correct_captcha += 1
                # click on "Ok" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                time.sleep(0.5)
                return None
            elif _alerta and "captcha" in _alerta[0].text:
                MONITOR.wrong_captcha += 1
                # click on "Ok" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                time.sleep(0.5)
                continue
            else:
                MONITOR.correct_captcha += 1
                break

        # extract data from table and parse relevant data, return a dictionary with RTEC data for each PLACA
        data_index = (
            ("clase", 6),
            ("numero", 7),
            ("tipo", 12),
            ("fecha_expedicion", 8),
            ("restricciones", 9),
            ("fecha_hasta", 10),
            ("centro", 11),
        )
        try:
            response = {}
            for data_unit, pos in data_index:
                response.update(
                    {
                        data_unit: self.WEBD.find_element(
                            By.ID,
                            f"mat-input-{pos}",
                        ).get_attribute("value")
                    }
                )
        except NoSuchElementException:
            response = None

        # next tab (Puntos)
        time.sleep(0.4)
        action = ActionChains(self.WEBD)
        try:
            # enter key combination to open tab
            keys = (
                Keys.TAB,
                Keys.TAB,
                Keys.TAB,
                Keys.TAB,
                Keys.TAB,
                Keys.RIGHT,
                Keys.ENTER,
            )
            for key in keys:
                action.send_keys(key)
                action.perform()
                time.sleep(random.randrange(0, 15) // 10)
            # extract data
            _puntos = self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[2]/div/div/mat-card/mat-card-content/div/app-visor-sclp/mat-card/mat-card-content/div/div[2]/label",
            ).text
            _puntos = int(_puntos.split(" ")[0]) if " " in _puntos else None
            response.update({"puntos": _puntos})

            # next tab (Record)
            time.sleep(0.8)
            action.send_keys(Keys.RIGHT)
            action.perform()
            time.sleep(0.7)
            action.send_keys(Keys.ENTER)
            action.perform()
            time.sleep(0.5)
            _recordnum = self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[3]/div/div/mat-card/mat-card-content/div/app-visor-record/div[1]/div/mat-card-title",
            ).text
            response.update({"record_num": _recordnum[9:] if _recordnum else None})

            # next tab (Papeletas Impagas)
            time.sleep(0.8)
            action.send_keys(Keys.RIGHT)
            action.perform()
            time.sleep(0.7)
            action.send_keys(Keys.ENTER)
            action.perform()
            time.sleep(0.5)
            _pimpagas = self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[4]/div/div/mat-card/mat-card-content/div/app-visor-papeletas/div/shared-table/div/div",
            ).text
            if "No se encontraron" in _pimpagas:
                _pimpagas = None
            else:
                LOG.info(f"papeletas impagas: {dni}")
            response.update({"papeletas_impagas": _pimpagas})
        except:
            return response
        print(response)
        return response


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


def start_logger(test=False):
    _filename = "updater_dev.log" if test else "updater.log"
    logging.basicConfig(
        filename=_filename,
        filemode="a",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    _log = logging.getLogger()
    _log.setLevel(logging.INFO)
    return _log


def main():
    # select scrapers to run according to parameters or set all scrapers if no parameters entered
    arguments = sys.argv
    VALID_OPTIONS = ["RTEC", "BREVETE", "SUTRAN"]
    if not any([i in VALID_OPTIONS for i in sys.argv]):
        arguments = VALID_OPTIONS

    # start top-level monitor in daemon thread
    _monitor = threading.Thread(target=MONITOR.top_level, daemon=True)
    _monitor.start()

    MONITOR.iteration = 0  # TODO: get rid of this variable

    arguments = ["RTEC"]

    # start required scrapers
    if "RTEC" in arguments:
        re = revtec.RevTec(database=DB, logger=LOG)
        re.run_full_update()
        quit()
    if "BREVETE" in arguments:
        br = Brevete()
        br.run_full_update()
        quit()
    if "SUTRAN" in arguments:
        su = Sutran()
        su.run_threads(nothreads=True)
        quit()

    # wrap-up: update correlative numbers and upload database file to Google Drive, email completion
    DB.update_database_correlatives()
    DB.upload_to_drive()
    # MONITOR.send_gmail()


if __name__ == "__main__":
    # start logger and register program start
    LOG = start_logger(test=True)
    LOG.info("Updater Begin.")

    # init monitor, database and Google functions (drive, gmail, etc)
    MONITOR = monitor.Monitor()
    DB = database.Database(no_backup=True, test=True, logger=LOG)
    GOOGLE_UTILS = GoogleUtils()

    # DB.fix_database_errors()
    # quit()

    # DATABASE.export_dashboard()
    # # DATABASE.add_raw_csv_to_database(r"data\raw_data2.csv")
    # quit()

    main()
    LOG.info("Updater End.")
