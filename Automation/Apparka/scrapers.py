from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime as dt, timedelta as td
import easyocr
import logging
from gft_utils import ChromeUtils

from PIL import Image
import io, urllib
import random


# remove easyocr warnings
logging.getLogger("easyocr").setLevel(logging.ERROR)


class Scraper:

    def __init__(self, parameters):
        self.URL = parameters["url"]
        self.SCRAPER = parameters["scraper"]
        self.DB = parameters["database"]
        self.LOG = parameters["logger"]
        self.MONITOR = parameters["monitor"]
        self.options = parameters["options"]
        self.thread_num = parameters["threadnum"]
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.restarts = 0
        self.consecutive_errors = 0
        self.log_name = self.SCRAPER.upper()
        self.SWITCH_TO_LIMITED = 1200  # records
        self.limited_scrape = True  # TODO:flexible

    def run_full_update(self):
        # first run is normal
        self.full_update()

        # restart wrapper
        while self.restarts <= 3:
            if self.MONITOR.threads[self.thread_num]["info"]["complete"]:
                self.LOG.info(f"{self.log_name} > End.")
                return
            else:
                time.sleep(3)
                self.restarts += 1
                self.LOG.info(f"{self.log_name} > Restart #{self.restarts}.")
                self.full_update()

        self.LOG.info(f"{self.log_name} > Restart Limit. End Process.")

    def full_update(self):
        # log start of process
        self.LOG.info(f"{self.log_name} > Begin.")

        # create list of all records that need updating in order of priority
        records_to_update = self.records_to_update()
        self.MONITOR.threads[self.thread_num]["info"]["total_records"] = len(
            records_to_update
        )

        self.LOG.info(
            f"{self.log_name} > Will process {len(records_to_update):,} records."
        )

        # define Chromedriver and open url for first time
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.WEBD.get(self.URL)
        time.sleep(3)

        rec = 0
        # iterate on all records that require updating
        for rec, record_index in enumerate(records_to_update):

            # check monitor flags: timeout -- return
            if self.MONITOR.timeout_flag:
                self.LOG.info(
                    f"{self.log_name} > End (Timeout). Processed {rec} records."
                )
                self.WEBD.close()
                self.MONITOR.threads[self.thread_num]["info"]["complete"] = True
                return

            # update monitor dashboard data
            self.MONITOR.threads[self.thread_num]["info"]["current_record"] = rec + 1

            # get scraper data
            new_record = self.get_new_record(rec, record_index)

            # if error from scraper then if limit of consecutive errors, restart updater, else next record
            if new_record is None:
                if self.consecutive_errors > 4:
                    return
                else:
                    continue

            # insert data into database
            self.update_record(record_index, new_record)

        # natural end of process (all records processed before timeout)
        self.LOG.info(f"{self.log_name} > End (Complete). Processed: {rec} records.")
        self.MONITOR.threads[self.thread_num]["complete"] = True
        return

    def records_to_update(self):
        lut = self.MONITOR.threads[self.thread_num]["info"]["lut"]
        to_update = [[] for _ in range(10)]

        for record_index, record in enumerate(self.DB.database):

            match self.SCRAPER:

                case "satimp":
                    relevant_date = record["documento"][
                        "deuda_tributaria_sat_actualizado"
                    ]

                case "brevete":
                    relevant_date = record["documento"]["brevete_actualizado"]

            actualizado = dt.strptime(relevant_date, "%d/%m/%Y")

            # Skip all records than have already been updated in last 24 hours
            if dt.now() - actualizado < td(days=1):
                continue

            match self.SCRAPER:
                case "satimp":
                    # Skip all records with no DNI/CE
                    if not record["documento"]["numero"]:
                        continue

                    # Priority 0: last update over 30 days
                    if dt.now() - actualizado >= td(days=lut):
                        to_update[0].append(record_index)

                case "brevete":
                    # Skip all records with no DNI/CE
                    if not record["documento"]["numero"]:
                        continue

                    # Priority 0: brevete will expire in 3 days or has expired in the last 30 days
                    if record["documento"]["brevete"]:
                        hasta = dt.strptime(
                            record["documento"]["brevete"]["fecha_hasta"], "%d/%m/%Y"
                        )
                        if td(days=-3) <= dt.now() - hasta <= td(days=30):
                            to_update[0].append(record_index)

                    # Priority 1: no brevete information and last update was 10+ days ago
                    if not record["documento"][
                        "brevete"
                    ] and dt.now() - actualizado >= td(days=lut):
                        to_update[1].append(record_index)

                    # Priority 2: brevete will expire in more than 30 days and last update was 10+ days ago
                    if dt.now() - hasta > td(days=30) and dt.now() - actualizado >= td(
                        days=lut
                    ):
                        to_update[2].append(record_index)

        # flatten list to records in order
        return [i for j in to_update for i in j]

    def get_new_record(self, rec, record_index):
        _doc_num = self.DB.database[record_index]["documento"]["numero"]
        _doc_tipo = self.DB.database[record_index]["documento"]["tipo"]

        try:
            match self.SCRAPER:
                case "satimp":
                    new_record = self.scraper(doc_num=_doc_num, doc_tipo=_doc_tipo)
                    self.consecutive_errors = 0
                    return new_record
                case "brevete":
                    new_record = self.scraper(doc_num=_doc_num)
                    # clear webpage for next iteration and small wait
                    time.sleep(1)
                    self.WEBD.back()
                    time.sleep(0.2)
                    self.WEBD.refresh()

        except KeyboardInterrupt:
            quit()
        # except:
        #     self.LOG.warning(f"{self.log_name} > Skipped Record {rec} (scraper error).")
        #     self.consecutive_errors += 1
        #     if self.consecutive_errors > 3:
        #         self.WEBD.close()
        #         return
        #     time.sleep(1)
        #     self.WEBD.refresh()
        #     time.sleep(1)

    def update_record(self, record_index, new_record):

        match self.SCRAPER:

            case "satimp":
                self.DB.database[record_index]["documento"][
                    "deuda_tributaria_sat"
                ] = new_record
                self.DB.database[record_index]["documento"][
                    "deuda_tributaria_sat_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")
            case "brevete":
                self.DB.database[record_index]["documento"]["brevete"] = new_record
                self.DB.database[record_index]["documento"][
                    "brevete_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")

        # update timestamp
        self.MONITOR.threads[self.thread_num]["info"][
            "last_record_updated"
        ] = time.time()

    def scraper(self, doc_tipo=None, doc_num=None):

        match self.SCRAPER:

            case "satimp":

                # navigate to to Tributo Detalles page with internal URL
                if not self.WEBD.find_elements(By.ID, "ctl00_cplPrincipal_lblTitulo"):
                    time.sleep(2)
                    _target = (
                        "https://www.sat.gob.pe/VirtualSAT/modulos/TributosResumen.aspx?tri=T&mysession="
                        + self.WEBD.current_url.split("=")[-1]
                    )
                    self.WEBD.get(_target)

                while True:
                    self.WEBD.refresh()
                    y = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtCaptcha")
                    y.clear()
                    # captura captcha image from webpage store in temp file
                    _captcha_img_url = self.WEBD.find_element(
                        By.XPATH,
                        "/html/body/form/div[3]/section/div/div/div[2]/div[3]/div[5]/div/div[1]/div[2]/div/img",
                    )
                    _captcha_img_url.screenshot("captcha_satimp.png")

                    # apply OCR to temp file
                    _captcha = self.READER.readtext(
                        "captcha_satimp.png", text_threshold=0.5
                    )
                    captcha_txt = (
                        _captcha[0][1]
                        if len(_captcha) > 0 and len(_captcha[0]) > 0
                        else ""
                    )
                    captcha_txt = "".join(
                        [i.upper() for i in captcha_txt if i.isalnum()]
                    )

                    # select alternative option from dropdown to reset it
                    drop = Select(self.WEBD.find_element(By.ID, "tipoBusqueda"))
                    drop.select_by_value("busqCodAdministrado")
                    time.sleep(0.5)
                    # select Busqueda por Documento from dropdown
                    drop.select_by_value("busqTipoDocIdentidad")
                    time.sleep(0.5)

                    # select tipo documento (DNI/CE) from dropdown
                    drop = Select(
                        self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_ddlTipoDocu")
                    )
                    drop.select_by_value("4" if doc_tipo == "CE" else "2")
                    time.sleep(0.5)

                    # clear field and enter DNI/CE
                    x = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtDocumento")
                    x.clear()
                    x.send_keys(doc_num)

                    # enter captcha
                    y = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtCaptcha")
                    y.clear()
                    y.send_keys(captcha_txt)
                    time.sleep(0.5)

                    # click BUSCAR
                    x = self.WEBD.find_element(By.CLASS_NAME, "boton")
                    x.click()
                    time.sleep(0.5)

                    # captcha tries counter
                    self.MONITOR.threads[self.thread_num]["info"][
                        "captcha_attempts"
                    ] += 1

                    x = self.WEBD.find_element(
                        By.ID, "ctl00_cplPrincipal_lblMensajeCantidad"
                    ).text
                    if x:
                        break

                _qty = int("".join([i for i in x if i.isdigit()]))
                if _qty == 0:
                    return []

                response = []
                for row in range(_qty):
                    codigo = self.WEBD.find_element(
                        By.ID,
                        f"ctl00_cplPrincipal_grdAdministrados_ctl0{row+2}_lnkCodigo",
                    ).text

                    x = self.WEBD.find_element(
                        By.ID,
                        f"ctl00_cplPrincipal_grdAdministrados_ctl0{row+2}_lnkNombre",
                    )
                    x.click()
                    time.sleep(0.5)

                    _deudas = []
                    self.WEBD.find_element(
                        By.ID, "ctl00_cplPrincipal_rbtMostrar_2"
                    ).click()
                    time.sleep(0.5)

                    for i in range(2, 10):
                        _placeholder = f"ctl00_cplPrincipal_grdEstadoCuenta_ctl0{i}_lbl"
                        y = f"{_placeholder}Anio"
                        x = self.WEBD.find_elements(By.ID, y)
                        if x:
                            _fila = {
                                "ano": x[0].text,
                                "periodo": self.WEBD.find_element(
                                    By.ID, f"{_placeholder}Periodo"
                                ).text,
                                "documento": self.WEBD.find_element(
                                    By.ID, f"{_placeholder}Documento"
                                ).text,
                                "total_a_pagar": self.WEBD.find_element(
                                    By.ID, f"{_placeholder}Deuda"
                                ).text,
                            }
                            _deudas.append(_fila)

                    self.WEBD.back()
                    time.sleep(1)
                    self.WEBD.back()
                    time.sleep(1)
                    response.append({"codigo": int(codigo), "deudas": _deudas})

                time.sleep(0.5)
                x = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_btnNuevaBusqueda")
                x.click()

                time.sleep(0.5)

                return response

            case "brevete":

                retry_captcha = False
                # outer loop: in case captcha is not accepted by webpage, try with a new one
                while True:
                    captcha_txt = ""
                    # inner loop: in case OCR cannot figure out captcha, retry new captcha
                    while not captcha_txt:
                        if retry_captcha:
                            self.WEBD.refresh()
                            time.sleep(1)
                        # capture captcha image from webpage and store in variable
                        try:
                            _captcha_img_url = self.WEBD.find_element(
                                By.XPATH,
                                "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[3]/div[2]/img",
                            ).get_attribute("src")
                            _img = Image.open(
                                io.BytesIO(
                                    urllib.request.urlopen(_captcha_img_url).read()
                                )
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
                            time.sleep(1)
                            self.WEBD.get(self.URL)
                            time.sleep(1)

                    # enter data into fields and run
                    self.WEBD.find_element(By.ID, "mat-input-1").send_keys(doc_num)
                    self.WEBD.find_element(By.ID, "mat-input-0").send_keys(captcha_txt)
                    self.WEBD.find_element(By.ID, "mat-checkbox-1").click()
                    self.WEBD.find_element(
                        By.XPATH,
                        "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[5]/div[1]/button",
                    ).click()
                    time.sleep(1)

                    # captcha tries counter
                    self.MONITOR.threads[self.thread_num]["info"][
                        "captcha_attempts"
                    ] += 1

                    # if captcha is not correct, refresh and restart cycle, if no data found, return None
                    _alerta = self.WEBD.find_elements(By.ID, "swal2-html-container")
                    if _alerta and "persona natural" in _alerta[0].text:
                        # click on "Ok" to close pop-up
                        self.WEBD.find_element(
                            By.XPATH, "/html/body/div/div/div[6]/button[1]"
                        ).click()
                        time.sleep(0.5)
                        return []
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
                    response = []

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
                    response.update(
                        {"record_num": _recordnum[9:] if _recordnum else None}
                    )

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
                        self.LOG.info(
                            f"BREVETE > Registo ejemplo de papeletas impagas: {doc_num}."
                        )
                    response.update({"papeletas_impagas": _pimpagas})
                except:
                    return response

                return response
