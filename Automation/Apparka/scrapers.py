from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime as dt, timedelta as td
import time
from PIL import Image
import io, urllib
import random
import easyocr


class Satimp:
    def __init__(self, db) -> None:
        self.DB = db
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.opening = True

    def records_to_update(self, last_update_threshold):
        to_update = [[]]
        for record_index, record in enumerate(self.DB.database):
            actualizado = dt.strptime(
                record["documento"]["deuda_tributaria_sat_actualizado"], "%d/%m/%Y"
            )
            # Skip all records than have already been updated in last day
            if dt.now() - actualizado < td(days=1):
                continue
            # Priority 0: last update over 30 days
            if dt.now() - actualizado >= td(days=last_update_threshold):
                to_update[0].append((record_index, 0))
        return to_update

    def update_record(self, record_index, position, new_record):
        self.DB.database[record_index]["documento"]["deuda_tributaria_sat"] = new_record
        self.DB.database[record_index]["documento"][
            "deuda_tributaria_sat_actualizado"
        ] = dt.now().strftime("%d/%m/%Y")

    def browser(self, doc_tipo, doc_num, placa):
        if not doc_num:
            return [], 0

        if self.opening:
            # navigate once to Tributo Detalles page with internal URL
            _target = (
                "https://www.sat.gob.pe/VirtualSAT/modulos/TributosResumen.aspx?tri=T&mysession="
                + self.WEBD.current_url.split("=")[-1]
            )
            self.WEBD.get(_target)
            time.sleep(2)
            self.opening = False

        captcha_attempts = 0

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
            _captcha = self.READER.readtext("captcha_satimp.png", text_threshold=0.5)
            captcha_txt = (
                _captcha[0][1] if len(_captcha) > 0 and len(_captcha[0]) > 0 else ""
            )
            captcha_txt = "".join([i.upper() for i in captcha_txt if i.isalnum()])

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
            captcha_attempts += 1

            x = self.WEBD.find_element(
                By.ID, "ctl00_cplPrincipal_lblMensajeCantidad"
            ).text
            if x:
                break

        _qty = int("".join([i for i in x if i.isdigit()]))
        if _qty == 0:
            return [], captcha_attempts

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

        return response, captcha_attempts


class Brevete:
    def __init__(self, db, reload_url) -> None:
        self.DB = db
        self.URL = reload_url
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.SWITCH_TO_LIMITED = 1200  # records
        self.limited_scrape = True  # TODO:flexible

    def records_to_update(self, last_update_threshold):
        to_update = [[] for _ in range(3)]

        for record_index, record in enumerate(self.DB.database):
            brevete = record["documento"]["brevete"]
            actualizado = dt.strptime(
                record["documento"]["brevete_actualizado"], "%d/%m/%Y"
            )

            # Skip all records than have already been updated in last 24 hours
            if dt.now() - actualizado < td(days=1):
                continue

            # Priority 0: brevete will expire in 15 days or has expired in the last 30 days
            if brevete:
                hasta = dt.strptime(brevete["fecha_hasta"], "%d/%m/%Y")
                if td(days=-15) <= dt.now() - hasta <= td(days=30):
                    to_update[0].append((record_index, 0))

            # Priority 1: last update was LUT days ago
            if dt.now() - actualizado >= td(days=last_update_threshold):
                to_update[1].append((record_index, 0))

            # # Priority 2: brevete will expire in more than 30 days and last update was 10+ days ago
            # if dt.now() - hasta > td(days=30) and dt.now() - actualizado >= td(
            #     days=last_update_threshold
            # ):
            #     to_update[2].append((record_index, 0))

        return to_update

    def update_record(self, record_index, position, new_record):
        self.DB.database[record_index]["documento"]["brevete"] = new_record
        self.DB.database[record_index]["documento"][
            "brevete_actualizado"
        ] = dt.now().strftime("%d/%m/%Y")

    def browser(self, doc_tipo, doc_num, placa):
        captcha_attempts = 0
        retry_captcha = False
        # outer loop: in case captcha is not accepted by webpage, try with a new one
        while True:
            captcha_txt = ""
            # inner loop: in case OCR cannot figure out captcha, retry new captcha
            while not captcha_txt:
                captcha_attempts += 1
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
            self.WEBD.find_element(By.ID, "mat-input-1").send_keys(doc_num)
            self.WEBD.find_element(By.ID, "mat-input-0").send_keys(captcha_txt)
            self.WEBD.find_element(By.ID, "mat-checkbox-1").click()
            self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/div[2]/app-home/div/mat-card[1]/form/div[5]/div[1]/button",
            ).click()
            time.sleep(1)

            # captcha tries counter

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            _alerta = self.WEBD.find_elements(By.ID, "swal2-html-container")
            if _alerta and "persona natural" in _alerta[0].text:
                # click on "Ok" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                # clear webpage for next iteration and small wait
                time.sleep(1)
                self.WEBD.back()
                time.sleep(0.2)
                self.WEBD.refresh()
                return [], captcha_attempts
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
            # clear webpage for next iteration and small wait
            time.sleep(1)
            self.WEBD.back()
            time.sleep(0.2)
            self.WEBD.refresh()
            return response, captcha_attempts

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
                self.LOG.info(
                    f"BREVETE > Registo ejemplo de papeletas impagas: {doc_num}."
                )
            response.update({"papeletas_impagas": _pimpagas})
        except:
            # clear webpage for next iteration and small wait
            time.sleep(1)
            self.WEBD.back()
            time.sleep(0.2)
            self.WEBD.refresh()
            return response, captcha_attempts

        return response, captcha_attempts


class Revtec:
    def __init__(self, db) -> None:
        self.DB = db
        self.READER = easyocr.Reader(["es"], gpu=False)

    def records_to_update(self, last_update_threshold):
        to_update = [[] for _ in range(4)]

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

        return to_update

    def update_record(self, record_index, position, new_record):
        self.DB.database[record_index]["vehiculos"][position]["rtecs"] = new_record
        self.DB.database[record_index]["vehiculos"][position][
            "rtecs_actualizado"
        ] = dt.now().strftime("%d/%m/%Y")

    def browser(self, doc_tipo, doc_num, placa):
        captcha_attempts = 0
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

            # captcha tries counter
            captcha_attempts += 1

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            _alerta = self.WEBD.find_element(By.ID, "lblAlertaMensaje").text
            if "no es correcto" in _alerta:
                continue
            elif "encontraron resultados" in _alerta:
                # clear webpage for next iteration and return None
                self.WEBD.refresh()
                time.sleep(0.5)
                return None, 0
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
                        f"/html/body/form/div[4]/div/div/div[2]/div[2]/div/div/div[6]/div[{'2' if data_unit == 'certificadora' else '3'}]/div/div/div/table/tbody/tr[2]/td[{pos}]",
                    ).text
                }
            )

        # clear webpage for next response
        time.sleep(1)
        self.WEBD.refresh()
        time.sleep(1)

        return response, captcha_attempts


class Sutran:
    def __init__(self, db) -> None:
        self.DB = db
        self.READER = easyocr.Reader(["es"], gpu=False)

    def records_to_update(self, last_update_threshold):
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

                # Priority 0: last update over n days
                if dt.now() - actualizado >= td(days=last_update_threshold):
                    to_update[0].append((record_index, veh_index))

        return to_update

    def update_record(self, record_index, position, new_record):
        self.DB.database[record_index]["vehiculos"][position]["multas"][
            "sutran"
        ] = new_record
        self.DB.database[record_index]["vehiculos"][position]["multas"][
            "sutran_actualizado"
        ] = dt.now().strftime("%d/%m/%Y")

    def browser(self, doc_tipo, doc_num, placa):
        captcha_attempts = 0
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

            # captcha tries counter
            captcha_attempts += 1

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
                return [], captcha_attempts
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

        return response, captcha_attempts
