from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time, sys, os
import csv, json
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib, shutil
from copy import deepcopy as copy
import uuid
import threading
import easyocr


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils

quit()


class Monitor:
    def __init__(self) -> None:
        self.UPDATE_FREQUENCY = 3
        self.progress = 0
        self.correct_captcha = self.wrong_captcha = 0
        self.errors = 0
        self.writes = 0
        self.pending_writes = 0
        self.stalled = False

    def monitor_with_threads(self, threads):
        while True:
            status = f"[{dt.now().strftime('%H:%M:%S')}] Processed: {self.progress} | Thread-"
            for k, thread in enumerate(threads):
                status += f"{k} ACTIVE" if thread.is_alive() else f"{k} STOPPED"
                status += (
                    f" [Errors: {str(self.errors[k])}] [Writes: {str(self.writes[k])}]"
                )
                status += " | "
            print(status, end="\r")
            time.sleep(self.UPDATE_FREQUENCY)

    def monitor_without_threads(self):
        self.last_pending = 0
        self.last_change = dt.now()
        self.start_time = dt.now() - td(seconds=1)  # add second to avoid div by zero

        # turn on permanent monitor
        while True:
            # determine if process has stalled if no new records written in time period, change flag
            if self.pending_writes > self.last_pending:
                self.last_pending = int(self.pending_writes)
                self.last_change = dt.now()
            if self.last_change + td(seconds=120) < dt.now():
                self.stalled = True
            # build and output status string (check for div by zero)
            if self.correct_captcha + self.wrong_captcha == 0:
                _captcha_rate = 1
            else:
                _captcha_rate = self.correct_captcha / (
                    self.correct_captcha + self.wrong_captcha
                )

            status = f"[{str(dt.now()-self.start_time)[:-7]}] Process: {self.progress} / {DATABASE.len_database}\n"
            status += f"[Written: {str(self.writes)}] [Pending Write: {str(self.pending_writes)}]\n"
            status += f"[Since Last Change: {(dt.now()-self.last_change).total_seconds():.0f} sec]\n"
            status += f"[Captcha Rate: {_captcha_rate*100:.1f}%] [Errors: {str(self.errors)}]\n"
            status += f"[New Record Rate: {((self.writes+self.pending_writes)*60/(dt.now()-self.start_time).total_seconds()):.1f} rec/m]\n"
            status += f'[{"STALLED" if self.stalled else "ACTIVE"}]'
            print(status)

            time.sleep(self.UPDATE_FREQUENCY)
            os.system("cls")


class Database:
    def __init__(self):
        # define database constants
        self.DATABASE_NAME = os.path.join(os.curdir, "data", "rtec_data.json")
        self.LOCK = threading.Lock()
        # backup database and load in memory
        self.backup_database()
        self.load_database()
        self.len_database = len(self.database)

    def add_raw_csv_to_database(self, csv_path):
        """Loads (adds) a basic csv file with structure NOMBRE, TIPODOC, DOCNUM, TELEFONO, PLACA
        into the general database with the correct structure"""

        # define local functions that create dictionary structure of vehiculo and record
        create_vehiculo = lambda i: {
            "placa": i[4],
            "rtecs": None,
            "rtec_actualizado": "01/01/2020",
        }
        create_record = lambda i: {
            "nombre": i[0].strip(),
            "documento": {"tipo": i[1], "numero": i[2]},
            "telefono": i[3],
            "vehiculos": vehiculos,
        }
        # load raw csv data file with structure NOMBRE, TIPODOC, DOCNUM, TELEFONO, PLACA
        with open(csv_path, mode="r", encoding="utf-8-sig") as csv_file:
            csv_data = [
                [i.strip().upper() for i in j]
                for j in csv.reader(csv_file, delimiter=",")
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
        # write (add) into json format file
        with open(self.DATABASE_NAME, "a+", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4)

    def backup_database(self):
        """Create local copy of database with random 8-letter text to avoid overwriting"""
        shutil.copyfile(
            self.DATABASE_NAME,
            os.path.join(
                os.curdir, "data", f"rtec_data_backup_{str(uuid.uuid4())[:8]}.json"
            ),
            follow_symlinks=True,
        )
        print("<<< Database Backup Complete >>>")

    def load_database(self):
        """Opens database and stores into to memory as a list of dictionaries"""
        with open(self.DATABASE_NAME, mode="r") as file:
            self.database = json.load(file)

    def write_database(self):
        """Writes complete updated database file from memory. Locks file to avoid race conditions between threads"""
        self.LOCK.acquire()
        with open(self.DATABASE_NAME, "w+") as file:
            json.dump(self.database, file, indent=4)
        self.LOCK.release()
        MONITOR.last_pending = 0

    def update_database_correlatives(self):
        """Opens database, updates correlatives for all records, writes database and closes"""
        self.load_database()
        for k, _ in enumerate(self.database):
            self.database[k]["correlative"] = k
        self.write_database()

    def dashboard(self):
        self.load_database()
        with_documento = with_brevete = with_rtec = 0
        brevete_actualizado = rtec_actualizado = total_rtecs = 0
        brevete_null = 0
        text = ""
        for record in self.database:
            if record["documento"]["numero"]:
                with_documento += 1
            if record["documento"]["brevete"]:
                with_brevete += 1
            if record["vehiculos"] and record["vehiculos"][0]["rtecs"]:
                with_rtec += 1
            if dt.strptime(
                record["documento"]["brevete_actualizado"], "%d/%m/%Y"
            ) < dt.now() - td(days=7):
                brevete_actualizado += 1
            if dt.strptime(
                record["vehiculos"][0]["rtecs_actualizado"], "%d/%m/%Y"
            ) < dt.now() - td(days=7):
                rtec_actualizado += 1
            if record["documento"]["brevete"] == None and dt.now() - dt.strptime(
                record["documento"]["brevete_actualizado"], "%d/%m/%Y"
            ) <= td(days=30):
                brevete_null += 1

        text += f"[Total Records: {self.len_database}]\n"
        text += f"Tienen Documento: {with_documento} ({with_documento*100/self.len_database:.2f}%)\n"
        text += f"Tienen Brevete: {with_brevete} ({with_brevete*100/self.len_database:.2f}%)\n"
        text += f"Tienen RTec: {with_rtec} ({with_rtec*100/self.len_database:.2f}%)\n"
        text += f"Brevete Actualizado: {brevete_actualizado} ({brevete_actualizado*100/self.len_database:.2f}%)\n"
        text += f"RTec Actualizado: {rtec_actualizado} ({rtec_actualizado*100/self.len_database:.2f}%)\n"
        text += f"Null Actualizado Last 30 days: {brevete_null}\n"

        print(text)


class RevTec:
    # define class constants
    WRITE_FREQUENCY = 50
    DAYS_BEFORE_UPDATE = 7
    DAYS_BEFORE_EXPIRY = 15
    NUMBER_THREADS = 10
    URL = "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"

    def __init__(self) -> None:
        self.counter = 0
        self.READER = easyocr.Reader(["es"], gpu=False)

    def run(self):
        # iterate on all records in database and update the necessary ones, open n threads
        _block = DATABASE.len_database // self.NUMBER_THREADS
        active_threads = []
        for thread in range(self.NUMBER_THREADS):
            _start = thread * _block
            _end = (
                len(DATABASE.database)
                if thread == (self.NUMBER_THREADS - 1)
                else (thread + 1) * _block
            )
            _t = threading.Thread(target=self.full_update, args=(DATABASE._start, _end))
            active_threads.append(_t)
            _t.start()

        _monitor = threading.Thread(
            target=MONITOR.monitor_with_threads, args=(active_threads,), daemon=True
        )
        _monitor.start()

        for single_thread in active_threads:
            single_thread.join()

        # once database has been updated, reset the correlatives
        DATABASE.update_database_correlatives()

    def full_update(self, start_record, end_record):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        # define Chromedriver
        WEBD = ChromeUtils().init_driver(headless=True, verbose=False, maximized=True)

        # open url for first time
        WEBD.get(self.URL)
        time.sleep(5)

        # iterate on every record in indicated range, then on every PLACA in each record, update if necessary
        _counter = 1
        for record_index, record in enumerate(
            DATABASE.database[start_record:end_record], start=start_record
        ):
            self.counter += 1
            print(f"{self.counter/len(DATABASE.database)*100:.2f}%", end="\r")
            for pos, vehiculo in enumerate(record["vehiculos"]):
                try:
                    actualizado = dt.strptime(vehiculo["rtecs_actualizado"], "%d/%m/%Y")
                except:
                    print(f"**** Database Error with {vehiculo}. Skipping record.")
                    continue
                placa = vehiculo["placa"]
                if self.record_needs_updating(vehiculo["rtecs"], actualizado):
                    try:
                        # update rtec data
                        DATABASE.database[record_index]["vehiculos"][pos]["rtecs"] = (
                            self.scraper(placa)
                        )
                        # update last update data
                        DATABASE.database[record_index]["vehiculos"][pos][
                            "rtecs_actualizado"
                        ] = dt.now().strftime("%d/%m/%Y")
                        # clear url for next iteration and small wait
                        WEBD.get(self.URL)
                        time.sleep(0.5)
                        _counter += 1
                    except (NoSuchElementException, ElementNotInteractableException):
                        MONITOR.errors += 1
                        time.sleep(5)

            # write database to disk every n captures
            if _counter % self.WRITE_FREQUENCY == 0:
                DATABASE.write_database()

        # last write in case there are pending changes in memory
        DATABASE.write_database()

    def record_needs_updating(self, rtecs, actualizado):
        """Checks if record meets criteria for updating"""

        # Check: last update was longer than n days from today
        if dt.now() - actualizado < td(days=self.DAYS_BEFORE_UPDATE):
            return False

        # Check: there is no data for rtecs
        if not rtecs:
            return True

        # Check: fecha_hasta is in the past (with margin)
        if dt.strptime(rtecs[0]["fecha_hasta"], "%d/%m/%Y") > dt.now() - td(
            days=self.DAYS_BEFORE_EXPIRY
        ):
            return False

        # If all tests succeed, update record
        return True

    def scraper(self, placa):
        retry = False
        while True:
            # get captcha in string format
            captcha_txt = ""
            while not captcha_txt:
                if retry:
                    self.WEBD.refresh()
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
                retry = True

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
        return [response]


class Brevete:
    # define class constants
    WRITE_FREQUENCY = 20
    DAYS_BEFORE_UPDATE = 7
    DAYS_BEFORE_EXPIRY = 15
    NUMBER_THREADS = 1
    MAX_CHROMEDRIVER_EXCEPTIONS = 120
    URL = "https://licencias.mtc.gob.pe/#/index"

    def __init__(self) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)

    def run(self):
        # start monitor in new thread
        _monitor = threading.Thread(target=MONITOR.monitor_without_threads, daemon=True)
        _monitor.start()

        # iterate on all records in database and update the necessary ones, no threading
        self.full_update(0, DATABASE.len_database)

        # once database has been updated, reset the correlatives
        DATABASE.update_database_correlatives()

    def full_update(self, start_record, end_record):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        MONITOR.stalled = True
        while MONITOR.stalled:
            MONITOR.stalled = False
            MONITOR.progress = 0

            # define Chromedriver
            self.WEBD = ChromeUtils().init_driver(
                headless=True, verbose=False, incognito=True
            )

            # open url for first time
            self.WEBD.get(self.URL)
            time.sleep(2)

            # iterate on every DNI in every record in indicated range, update if necessary
            for record_index, record in enumerate(
                DATABASE.database[start_record:end_record], start=start_record
            ):
                # check if record requires update and proceed with update
                try:

                    if self.record_needs_updating(
                        record["documento"]["brevete"],
                        dt.strptime(
                            record["documento"]["brevete_actualizado"], "%d/%m/%Y"
                        ),
                    ):
                        # update brevete data
                        DATABASE.database[record_index]["documento"]["brevete"] = (
                            self.scraper(dni=record["documento"]["numero"])
                        )
                        # update last update data
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
                            self.WEBD.close()
                            time.sleep(10)
                            MONITOR.last_change = dt.now()
                            break
                    MONITOR.progress += 1

                except (NoSuchElementException, ElementNotInteractableException):
                    # error with webpage, reload
                    time.sleep(3)
                    self.WEBD.get(self.URL)
                    time.sleep(3)

            # last write in case there are pending changes in memory
            DATABASE.write_database()

    def record_needs_updating(self, brevete, actualizado):
        """Checks if record meets criteria for updating"""

        # Check: last update was longer than n days from today
        if dt.now() - actualizado < td(days=self.DAYS_BEFORE_UPDATE):
            return False

        # Check: there is no data for rtecs
        if not brevete:
            return True

        # Check: fecha_hasta is in the past (with margin)
        if dt.strptime(brevete["fecha_hasta"], "%d/%m/%Y") > dt.now() - td(
            days=self.DAYS_BEFORE_EXPIRY
        ):
            return False

        # All else update record
        return True

    def scraper(self, dni):
        retry = False
        while True:
            # get captcha in string format
            captcha_txt = ""
            while not captcha_txt:
                if retry:
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
                    retry = True
                except ValueError:
                    # captcha image did not load, reset webpage
                    MONITOR.errors += 1
                    self.WEBD.refresh()
                    time.sleep(1.5)
                    self.WEBD.get(self.URL)
                    time.sleep(1.5)
                    # self.WEBD.refresh()

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
            # if element is not present, there is no data for that DOCUMENTO
            response = None

        # clear webpage for next iteration and small wait
        time.sleep(1)
        self.WEBD.back()
        time.sleep(0.5)
        self.WEBD.refresh()
        time.sleep(1)

        return response


class Sunarp:
    # define class constants
    WRITE_FREQUENCY = 20
    DAYS_BEFORE_UPDATE = 7
    DAYS_BEFORE_EXPIRY = 15
    NUMBER_THREADS = 1
    MAX_CHROMEDRIVER_EXCEPTIONS = 120
    URL = "https://www.sunarp.gob.pe/ConsultaVehicular/"


def main():
    os.system("cls")
    DATABASE.dashboard()
    # revtec = RevTec()
    brevete = Brevete()
    brevete.run()


if __name__ == "__main__":
    DATABASE = Database()
    MONITOR = Monitor()
    main()
