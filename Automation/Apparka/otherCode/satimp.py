from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time, sys
from datetime import datetime as dt, timedelta as td
import easyocr
from PIL import Image
import io, urllib


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class Satimp:
    # define class constants
    URL = "https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx"

    def __init__(self, database, logger, monitor, options) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.DB = database
        self.LOG = logger
        self.MONITOR = monitor

    def run_full_update(self):
        """Iterates through a certain portion of database and updates RTEC data for each PLACA.
        Designed to work with Threading."""

        # log start of process
        self.LOG.info(f"SAT_IMPUESTOS > Begin.")

        # create list of all records that need updating with priorities
        records_to_update = self.list_records_to_update()
        self.MONITOR.total_records[3] = len(records_to_update)

        self.LOG.info(
            f"SAT_IMPUESTOS > Will process {len(records_to_update):,} records."
        )

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
            open = True
            for rec, record_index in enumerate(records_to_update):
                # update monitor dashboard data
                self.MONITOR.current_record[3] = rec + 1
                # get scraper data, if webpage fails skip record
                _doc_num = self.DB.database[record_index]["documento"]["numero"]
                _doc_tipo = self.DB.database[record_index]["documento"]["tipo"]
                if _doc_tipo != "DNI":
                    self.LOG.warning(f"SAT_IMPUESTOS > Skipped Record {rec} (CE).")
                try:
                    new_record = self.scraper(
                        doc_num=_doc_num, doc_tipo=_doc_tipo, opening=open
                    )
                    open = False
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
                    and self.DB.database[record_index]["documento"][
                        "deuda_tributaria_sat"
                    ]
                ):
                    continue

                self.DB.database[record_index]["documento"][
                    "deuda_tributaria_sat"
                ] = new_record
                self.DB.database[record_index]["documento"][
                    "deuda_tributaria_sat_actualizado"
                ] = dt.now().strftime("%d/%m/%Y")

                # check monitor flags: timeout
                if self.MONITOR.timeout_flag:
                    self.LOG.info(
                        f"SAT_IMPUESTOS > End (Timeout). Processed {rec} records."
                    )
                    self.WEBD.close()
                    return

        # log end of process
        self.LOG.info(f"SAT_IMPUESTOS > End (Complete). Processed: {rec} records.")

    def list_records_to_update(self):

        to_update = [[] for _ in range(2)]

        for record_index, record in enumerate(self.DB.database):
            sat_impuestos = record["documento"]["deuda_tributaria_sat"]
            actualizado = dt.strptime(
                record["documento"]["deuda_tributaria_sat_actualizado"], "%d/%m/%Y"
            )

            # Skip all records than have already been updated in last 22 hours
            if dt.now() - actualizado < td(days=1):
                continue

            # Priority 0: last update over 30 days
            if dt.now() - actualizado >= td(days=30):
                to_update[0].append(record_index)

        # flatten list to records in order
        return [i for j in to_update for i in j]

    def scraper(self, doc_tipo, doc_num, opening=False):

        if opening:
            # navigate to to Tributo Detalles page with internal URL
            time.sleep(2)
            _target = (
                "https://www.sat.gob.pe/VirtualSAT/modulos/TributosResumen.aspx?tri=T&mysession="
                + self.WEBD.current_url.split("=")[-1]
            )
            self.WEBD.get(_target)

        while True:
            # capture captcha image from webpage store in variable
            self.WEBD.get_screenshot_as_file("captcha_tmp.png")
            _img = Image.open("captcha_tmp.png")
            _img = _img.crop((1385, 690, 1510, 725))
            _img.save("captcha_tmp.png")
            # convert image to text using OCR
            _captcha = self.READER.readtext("captcha_tmp.png", text_threshold=0.5)
            captcha_txt = (
                _captcha[0][1] if len(_captcha) > 0 and len(_captcha[0]) > 0 else ""
            )

            time.sleep(0.5)
            # select alternative option from dropdown to reset it
            drop = Select(self.WEBD.find_element(By.ID, "tipoBusqueda"))
            drop.select_by_value("busqCodAdministrado")
            time.sleep(0.5)
            # select Busqueda por Documento from dropdown
            drop = Select(self.WEBD.find_element(By.ID, "tipoBusqueda"))
            drop.select_by_value("busqTipoDocIdentidad")

            time.sleep(0.5)
            # dropdown tipo de documento
            # drop = Select(
            #     self.WEBD.find_element(
            #         By.XPATH,
            #         "/html/body/form/div[3]/section/div/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/select",
            #     )
            # )
            # # select between DNI and CE
            # drop.select_by_value("4" if doc_tipo == "CE" else "1")

            # clear field and enter DNI/CE
            x = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtDocumento")
            x.send_keys(doc_num)

            # enter captcha
            y = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtCaptcha")
            y.clear()
            y.send_keys(captcha_txt)
            time.sleep(0.5)

            # click BUSCAR
            x = self.WEBD.find_element(By.CLASS_NAME, "boton")
            x.click()
            time.sleep(1)

            x = self.WEBD.find_element(
                By.ID, "ctl00_cplPrincipal_lblMensajeCantidad"
            ).text
            if x:
                break
            else:
                y = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtCaptcha")
                y.clear()  # send_keys(Keys.BACKSPACE * 6)

        _qty = int("".join([i for i in x if i.isdigit()]))
        if _qty == 0:
            return None

        response = []
        for row in range(_qty):
            codigo = self.WEBD.find_element(
                By.ID, f"ctl00_cplPrincipal_grdAdministrados_ctl0{row+2}_lnkCodigo"
            ).text

            x = self.WEBD.find_element(
                By.ID, f"ctl00_cplPrincipal_grdAdministrados_ctl0{row+2}_lnkNombre"
            )
            x.click()
            time.sleep(0.5)

            _deudas = []
            self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_rbtMostrar_2").click()
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
