from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time, sys
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib
import easyocr
import random
import logging
from gft_utils import ChromeUtils

# remove easyocr warnings
logging.getLogger("easyocr").setLevel(logging.ERROR)


class Brevete:
    URL = "https://licencias.mtc.gob.pe/#/index"

    def __init__(self, **kwargs):
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.DB = kwargs["database"]
        self.LOG = kwargs["logger"]
        self.MONITOR = kwargs["monitor"]
        self.options = kwargs["options"]
        self.thread_num = kwargs["threadnum"]
        self.SWITCH_TO_LIMITED = 1200  # records

    def run_full_update(self):
        """Iterates through a certain portion of database and updates Brevete data for each PLACA."""

        # log start of process
        self.LOG.info(f"BREVETE > Begin.")

        # create list of all records that need updating, ease restrictions to get target number
        records_to_update = self.list_records_to_update()

        self.MONITOR.threads[self.thread_num]["total_records"] = len(records_to_update)

        # if volume is large, use less time-consuming scraper
        self.limited_scrape = (
            True if len(records_to_update) > self.SWITCH_TO_LIMITED else False
        )

        # if no records to update, log end of process
        if not records_to_update:
            self.LOG.info(f"BREVETE > End (Did not start). No records to process.")
            return
        else:
            self.LOG.info(
                f"BREVETE > Will process {len(records_to_update):,} records. {'Limited' if self.limited_scrape else 'Regular'} Scrape."
            )

        # define Chromedriver and open url for first time
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, incognito=True
        )
        self.WEBD.get(self.URL)
        time.sleep(2)

        rec = 0  # only in case for loop doesn't run

        # iterate on all records that require updating
        for rec, record_index in enumerate(records_to_update):
            # check monitor flags: timeout
            if self.MONITOR.timeout_flag:
                self.LOG.info(f"BREVETE > End (Timeout). Processed {rec+1} records.")
                return
            # update monitor status data
            self.MONITOR.threads[self.thread_num]["current_record"] = rec + 1

            # get scraper data, if webpage fails, refresh and skip record
            _dni = self.DB.database[record_index]["documento"]["numero"]
            try:
                new_record = self.scraper(dni=_dni)
                # clear webpage for next iteration and small wait
                time.sleep(1)
                self.WEBD.back()
                time.sleep(0.2)
                self.WEBD.refresh()
            except KeyboardInterrupt:
                return
            except:
                self.LOG.warning(f"BREVETE > Skipped Record {rec}.")
                self.WEBD.refresh()
                time.sleep(1)
                self.WEBD.get(self.URL)
                time.sleep(1)
                continue

            # if database has data and response is None, do not overwrite database
            if (
                not new_record
                and self.DB.database[record_index]["documento"]["brevete"]
            ):
                continue

            # update brevete data and last update in database
            self.DB.database[record_index]["documento"]["brevete"] = new_record
            self.DB.database[record_index]["documento"][
                "brevete_actualizado"
            ] = dt.now().strftime("%d/%m/%Y")
            # timestamp
            self.MONITOR.threads[self.thread_num]["last_record_updated"] = time.time()

            # check monitor flags: timeout
            if self.MONITOR.timeout_flag:
                self.LOG.info(f"BREVETE > End (Timeout). Processed {rec} records.")
                self.WEBD.close()
                return

        # log end of process
        self.LOG.info(f"BREVETE > End (Complete). Processed: {rec} records.")

    def list_records_to_update(self, last_update_threshold=60):

        self.MONITOR.threads[self.thread_num]["lut"] = last_update_threshold

        to_update = [[] for _ in range(3)]

        for record_index, record in enumerate(self.DB.database):
            brevete = record["documento"]["brevete"]
            actualizado = dt.strptime(
                record["documento"]["brevete_actualizado"], "%d/%m/%Y"
            )

            # Skip all records than have already been updated in last 22 hours
            if dt.now() - actualizado < td(days=1):
                continue

            # Priority 0: brevete will expire in 3 days or has expired in the last 30 days
            if brevete:
                hasta = dt.strptime(brevete["fecha_hasta"], "%d/%m/%Y")
                if td(days=-3) <= dt.now() - hasta <= td(days=30):
                    to_update[0].append(record_index)

            # Priority 1: no brevete information and last update was 10+ days ago
            if not brevete and dt.now() - actualizado >= td(days=last_update_threshold):
                to_update[1].append(record_index)

            # Priority 2: brevete will expire in more than 30 days and last update was 10+ days ago
            if dt.now() - hasta > td(days=30) and dt.now() - actualizado >= td(
                days=last_update_threshold
            ):
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

            # captcha tries counter
            self.MONITOR.threads[self.thread_num]["captcha_attempts"] += 1

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            _alerta = self.WEBD.find_elements(By.ID, "swal2-html-container")
            if _alerta and "persona natural" in _alerta[0].text:
                # click on "Ok" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                time.sleep(0.5)
                return None
            elif _alerta and "captcha" in _alerta[0].text:
                # click on "Ok" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                time.sleep(0.5)
                continue
            else:
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

        # skip rest of scrape if limited
        if self.limited_scrape:
            return response

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
            if "se encontraron" in _pimpagas:
                _pimpagas = None
            else:
                self.LOG.info(f"BREVETE > Registo ejemplo de papeletas impagas: {dni}.")
            response.update({"papeletas_impagas": _pimpagas})
        except:
            return response

        return response
