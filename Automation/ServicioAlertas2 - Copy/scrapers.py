from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import logging
import time
from PIL import Image
import io, urllib
import os, re
import easyocr
import numpy as np
from statistics import mean
from gft_utils import PDFUtils, ChromeUtils

# remove easyocr warnings
logging.getLogger("easyocr").setLevel(logging.ERROR)


class Satimp:
    def __init__(self) -> None:
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True, incognito=False
        )
        self.WEBD.set_page_load_timeout(20)
        self.WEBD.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
        # navigate once to Tributo Detalles page with internal URL
        _target = (
            "https://www.sat.gob.pe/VirtualSAT/modulos/TributosResumen.aspx?tri=T&mysession="
            + self.WEBD.current_url.split("=")[-1]
        )
        self.WEBD.get(_target)
        time.sleep(2)

        self.READER = easyocr.Reader(["es"], gpu=False)

    def browser(self, **kwargs):
        doc_num = kwargs["doc_num"]
        doc_tipo = kwargs["doc_tipo"]

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
            _captcha_img_url.screenshot(
                os.path.join(os.curdir, "other", "captcha_satimp.png")
            )

            # apply OCR to temp file
            _captcha = self.READER.readtext(
                os.path.join(os.curdir, "other", "captcha_satimp.png"),
                text_threshold=0.5,
            )
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
            return []

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
                    periodo = self.WEBD.find_element(
                        By.ID, f"{_placeholder}Periodo"
                    ).text
                    ano = x[0].text
                    # build fecha_hasta based on ano and periodo
                    _f = ("03-31", "06-30", "09-30", "12-31")
                    fecha_hasta = f"{ano}-{_f[int(periodo)-1]}"
                    _fila = {
                        "ano": ano,
                        "periodo": periodo,
                        "documento": self.WEBD.find_element(
                            By.ID, f"{_placeholder}Documento"
                        ).text,
                        "total_a_pagar": self.WEBD.find_element(
                            By.ID, f"{_placeholder}Deuda"
                        ).text,
                        "fecha_hasta": fecha_hasta,
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


class Brevete:
    def __init__(self) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.limited_scrape = False
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=False
        )
        self.WEBD.set_page_load_timeout(20)

    def browser(self, **kwargs):
        doc_num = kwargs["doc_num"]
        reload_url = self.WEBD.current_url
        retry_captcha = False

        self.WEBD.get("https://licencias.mtc.gob.pe/#/index")
        time.sleep(1)
        self.WEBD.refresh()
        time.sleep(0.5)
        self.WEBD.get("https://licencias.mtc.gob.pe/#/index")
        time.sleep(0.5)
        # outer loop: in case captcha is not accepted by webpage, try with a new one
        while True:
            captcha_txt = ""
            # inner loop: in case OCR cannot figure out captcha, retry new captcha
            while not captcha_txt:
                if retry_captcha:
                    self.WEBD.refresh()
                    time.sleep(2)
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
                    self.WEBD.get(reload_url)
                    time.sleep(1.5)
                    self.WEBD.refresh()
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
                time.sleep(0.5)
                self.WEBD.refresh()
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
            response = {}

        # next tab (Puntos) - make sure all is populated before tabbing along (with timeout) and wait a little
        timeout = 0
        while not self.WEBD.find_elements(By.ID, "mat-tab-label-0-0"):
            time.sleep(1)
            timeout += 1
            if timeout > 10:
                return {}
        time.sleep(1.5)

        action = ActionChains(self.WEBD)
        try:
            # enter key combination to open tabs
            for key in (Keys.TAB * 5, Keys.RIGHT, Keys.ENTER):
                action.send_keys(key)
                action.perform()
                time.sleep(0.5)

            # extract data
            _puntos = self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[2]/div/div/mat-card/mat-card-content/div/app-visor-sclp/mat-card/mat-card-content/div/div[2]/label",
            )

            _puntos = int(_puntos.text.split(" ")[0]) if " " in _puntos.text else 0
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

            _pimpagas = self.WEBD.find_elements(
                By.XPATH,
                "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[4]/div/div/mat-card/mat-card-content/div/app-visor-papeletas/div/shared-table/div/div",
            )
            if _pimpagas and "se encontraron" in _pimpagas[0].text:
                _pimpagas = []
            elif not _pimpagas:
                d = self.WEBD.find_element(
                    By.XPATH,
                    "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[4]/div/div/mat-card/mat-card-content/div/app-visor-papeletas/div/shared-table/div/mat-table/mat-row[1]/mat-cell[1]/span",
                )
                d.click()
                time.sleep(1)

                _v = [
                    i.text.split("\n")
                    for i in self.WEBD.find_elements(
                        By.XPATH,
                        "/html/body/app-root/div[2]/app-search/div[2]/mat-tab-group/div/mat-tab-body[4]/div/div/mat-card/mat-card-content/div/app-visor-papeletas/div/shared-table/div/mat-table/mat-row",
                    )
                ]
                _pimpagas = [
                    {
                        "entidad": _v[0][1],
                        "papeleta": _v[0][2],
                        "fecha": _v[0][3],
                        "fecha_firme": _v[1][1].strip(),
                        "falta": _v[1][3].strip(),
                        "estado_deuda": _v[1][5].strip(),
                    }
                ]

            response.update({"papeletas_impagas": _pimpagas})
        except KeyboardInterrupt:
            pass
            # # clear webpage for next iteration and small wait
            # time.sleep(1)
            # self.WEBD.back()
            # time.sleep(0.2)
            # self.WEBD.refresh()
            # return response

        return response


class Revtec:
    def __init__(self) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.WEBD.get(
            "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"
        )
        time.sleep(3)

    def browser(self, **kwargs):
        placa = kwargs["placa"]
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
                return []
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

        if response["resultado"] == "DESAPROBADO":
            response["fecha_hasta"] = response["fecha_desde"]
            response["vigencia"] = "VENCIDO"

        # clear webpage for next response
        time.sleep(1)
        self.WEBD.refresh()
        time.sleep(1)

        return response


class Sutran:
    def __init__(self) -> None:
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.WEBD.get(
            "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/"
        )
        self.WEBD.set_page_load_timeout(20)
        time.sleep(3)

    def browser(self, **kwargs):
        placa = kwargs["placa"]
        self.WEBD.refresh()
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
            # if no pendings, return None
            if "pendientes" in _alerta:
                return []
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
        _mt = self.WEBD.find_element(By.ID, "lblTotalDeuda").text[3:]
        response.update({"monto_total": float(_mt)})
        return response


class SoatImage:

    def __init__(self):
        self.pdf = PDFUtils()
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True, incognito=False
        )
        self.WEBD.get("https://www.pacifico.com.pe/consulta-soat")
        time.sleep(3)
        # check for and accept Cookies message
        c = self.WEBD.find_elements(
            By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
        )
        if c:
            c[0].click()
        time.sleep(1)

    def browser(self, **kwargs):
        while True:
            # required data for scrape
            placa = kwargs["placa"]

            url = f"https://soat.pacifico.com.pe/certificado-soat/?numero-placa={placa}&consent=false&origen=Seguros-ParaTusBienes-ConsultaSOAT-Top-Hero-01-Boton-ConsultaSoatIngresaTuPlacaConsultar"
            self.WEBD.get(url)

            # placa not found
            z = self.WEBD.find_elements(
                By.XPATH,
                "/html/body/div[1]/div[1]/div/div[1]/div/div[2]/div[1]/div/h1",
            )
            if z:  # and "No tienes" in z[0].text:
                return ""

            # wair for button and click DESCARGAR for 10 seconds
            z = False
            count = 0
            while not z and count < 10:
                z = self.WEBD.find_elements(
                    By.XPATH,
                    "/html/body/div[1]/div[1]/div/div[1]/div/div/div[2]/div/div[4]/button",
                )
                time.sleep(1)
                count += 1

            try:
                z[0].click()
                time.sleep(2)
            except:
                return ""

            # wait up to 20 seconds while file is downloaded
            count = 0
            while (
                not any(
                    [
                        True if f"SOAT-{placa.upper()}" == i[:11] else False
                        for i in os.listdir(
                            os.path.join(r"C:\Users", "Gabriel", "Downloads")
                        )
                    ]
                )
                and count < 20
            ):
                time.sleep(1)
                count += 1

            # take downloaded PDF, process image and save in data folder
            try:
                from_dir = os.listdir(os.path.join(r"C:\Users", "Gabriel", "Downloads"))
                _file_name = [i for i in from_dir if f"SOAT-{placa.upper()}" == i[:11]]

                from_path = os.path.join(
                    r"C:\Users", "Gabriel", "Downloads", _file_name[0]
                )
                to_path = os.path.join(
                    r"D:\pythonCode",
                    "Automation",
                    "ServicioAlertas",
                    "data",
                    "images",
                    f"SOAT_{placa.upper()}.png",
                )

                img = self.pdf.pdf_to_png(from_path, scale=1.3).crop(
                    (135, 64, 635, 844)
                )

                # delete image with same name (previous version) from destination folder if it exists
                if os.path.exists(to_path):
                    os.remove(to_path)
                img.save(to_path)

                # delete original downloaded file (saves space and avoids "(1)" appended on filename in future)
                os.remove(from_path)

                return str(os.path.basename(to_path))

            except KeyboardInterrupt:
                return ""


class RecordConductorImage:

    def __init__(self):
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.pdf = PDFUtils()
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.WEBD.get("https://recordconductor.mtc.gob.pe/")
        time.sleep(2)

    def get_captcha(self):

        def invert(img):
            a = len(img)
            b = len(img[1])
            h = np.full((b, a), 0)
            for x in range(len(img)):
                for y in range(len(img[0])):
                    h[y][x] = int(img[x][y][0])
            return h

        def valid(text):
            if len(text) != 6:
                return False
            text1 = "".join(re.findall("[a-zA-Z0-9]", text))
            return text == text1

        def process(depth, f):
            img = np.asarray(f)
            copyimg = np.copy(a=img)
            for i, x in enumerate(img):
                for j, y in enumerate(x):
                    if max(y) > 150:
                        copyimg[i][j] = [0, 0, 0]
                    else:
                        copyimg[i][j] = [255, 255, 255]
            h = invert(copyimg)
            h = h.tolist()
            for x in range(len(h)):
                if h[x].count(255) < depth:
                    h[x] = [0] * len(copyimg)
            h = np.asarray(h).tolist()
            a = len(h) - 1
            b = len(h[0]) - 1
            k = [[h[i][j] for i in range(a)] for j in range(b)]
            return np.asarray(k, dtype=np.uint8)

        text = None
        max_cert = 0
        for depth in range(2, 7):
            f = Image.open(os.path.join(os.curdir, "other", "RCItemp.png"))
            img = process(depth=depth, f=f)
            c = self.READER.readtext(img, text_threshold=0.4)
            if c and valid(c[0][1]) and c[0][2] > max_cert:
                max_cert = c[0][2]
                text = c[0][1]
                text = text.replace("a", "g")
                text = text.replace("9", "g")
                text = text.replace("l", "1")
        return text

    def browser(self, **kwargs):
        doc_num = kwargs["doc_num"]
        retry_captcha = False

        # outer loop: in case captcha is not accepted by webpage, try with a new one
        while True:
            captcha_txt = ""
            # inner loop: in case OCR cannot figure out captcha, retry new captcha
            while not captcha_txt:
                if retry_captcha:
                    self.WEBD.refresh()
                    time.sleep(2)
                # capture captcha image from webpage and store in variable
                try:
                    with open(
                        os.path.join(os.curdir, "other", "RCItemp.png"), "wb"
                    ) as file:
                        file.write(
                            self.WEBD.find_element(
                                By.ID, "idxcaptcha"
                            ).screenshot_as_png
                        )
                    # _captcha_img_url = self.WEBD.find_element(
                    #     By.ID, "idxcaptcha"
                    # ).get_attribute("src")
                    # _img = Image.open(
                    #     io.BytesIO(urllib.request.urlopen(_captcha_img_url).read())
                    # )
                    # convert image to text using OCR
                    captcha_txt = self.get_captcha()
                    retry_captcha = True

                except ValueError:
                    # captcha image did not load, reset webpage
                    self.WEBD.refresh()
                    time.sleep(1.5)

            # enter data into fields and run
            self.WEBD.find_element(By.ID, "txtNroDocumento").send_keys(doc_num)
            self.WEBD.find_element(By.ID, "idCaptcha").send_keys(captcha_txt)
            time.sleep(3)
            self.WEBD.find_element(By.ID, "BtnBuscar").click()
            time.sleep(1)

            # if captcha is not correct, refresh and restart cycle, if no data found, return blank
            _alerta = self.WEBD.find_elements(By.ID, "idxAlertmensaje")
            if _alerta and "ingresado" in _alerta[0].text:
                # click on "Cerrar" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div[5]/div/div/div[2]/button"
                ).click()
                # clear webpage for next iteration and small wait
                time.sleep(1)
                self.WEBD.refresh()
                continue
            elif _alerta and "PERSONA" in _alerta[0].text:
                # click on "Ok" to close pop-up
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div[5]/div/div/div[2]/button"
                ).click()
                time.sleep(1)
                return ""
            else:
                break

        b = self.WEBD.find_elements(By.ID, "btnprint")
        try:
            b[0].click()
        except:
            return ""

        _file_name = "RECORD DE CONDUCTOR.pdf"
        # erase file from destination directory before downloading new one
        if os.path.exists(_file_name):
            os.remove(_file_name)

        # wait max time while file is downloaded
        count = 0
        while (
            not os.path.isfile(
                os.path.join(r"C:\Users", "Gabriel", "Downloads", _file_name)
            )
            and count < 10
        ):
            time.sleep(1)
            count += 1

        # take downloaded PDF, process image and save in data folder
        try:
            from_path = os.path.join(r"C:\Users", "Gabriel", "Downloads", _file_name)
            to_path = os.path.join(
                r"D:\pythonCode",
                "Automation",
                "ServicioAlertas",
                "data",
                "images",
                f"RECORD_{doc_num.upper()}.png",
            )

            img = self.pdf.pdf_to_png(from_path, scale=1.3)

            # delete image with same name (previous version) from destination folder if it exists
            if os.path.exists(to_path):
                os.remove(to_path)
            img.save(to_path)

            # delete original downloaded file (saves space and avoids "(1)" appended on filename in future)
            os.remove(from_path)

            return str(os.path.basename(to_path))

        except KeyboardInterrupt:
            return ""


class CallaoMulta:
    def __init__(self) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.WEBD.get("https://pagopapeletascallao.pe/")
        time.sleep(3)

    def browser(self, **kwargs):
        placa = kwargs["placa"]

        retry_captcha = False
        while True:
            # get captcha in string format
            captcha_txt = ""
            while not captcha_txt:
                if retry_captcha:
                    self.WEBD.refresh()
                    time.sleep(1)

                # captura captcha image from webpage store in variable
                _captcha_img = self.WEBD.find_element(
                    By.XPATH, "/html/body/div[3]/div[1]/div[3]/p/img"
                ).screenshot_as_png

                _img = Image.open(io.BytesIO(_captcha_img))
                imgs = [
                    _img.crop((i, 0, j, 40)).resize((110, 80))
                    for i, j in [(0, 55), (55, 110), (110, 165)]
                ]

                captcha_txt = ""
                # convert image to text using OCR
                for img in imgs:
                    _captcha = self.READER.readtext(np.asarray(img), text_threshold=0.5)
                    captcha = (
                        _captcha[0][1]
                        if len(_captcha) > 0 and len(_captcha[0]) > 0
                        else "X"
                    )
                    captcha_txt += captcha

                if not captcha_txt.isnumeric():
                    captcha_txt = False
                    retry_captcha = True
                else:
                    retry_captcha = False

            # enter data into fields and run
            self.WEBD.find_element(By.ID, "valor_busqueda").send_keys(placa)
            time.sleep(1)
            self.WEBD.find_element(By.ID, "captcha").send_keys(captcha_txt)
            time.sleep(0.5)
            self.WEBD.find_element(By.ID, "idBuscar").click()
            time.sleep(1)

            # captcha correct, no result
            x = self.WEBD.find_elements(By.XPATH, "/html/body/div[3]/div[2]/p")
            y = self.WEBD.find_elements(By.XPATH, "/html/body/div[3]/div[1]/div[6]/p")

            if x:
                # return empty
                time.sleep(0.5)
                return []
            elif y:
                # captcha error, retry
                time.sleep(0.5)
            else:
                # captcha ok, data found
                break

        # extract data from table and parse relevant data, return a dictionary with RTEC data for each PLACA
        # TODO: find record with data
        print("EEEEEEEEEEEEEEE", placa)
        response = "NAKALAPIRINAKA"

        # clear webpage for next response
        time.sleep(1)
        self.WEBD.refresh()
        time.sleep(1)

        return response


class Soat:

    def __init__(self) -> None:
        self.WEBD = ChromeUtils().init_driver(
            headless=True, maximized=True, verbose=False, incognito=True
        )
        self.WEBD.get("https://www.apeseg.org.pe/consultas-soat/")

    def get_captcha_img(self):
        self.WEBD.refresh()
        _img = self.WEBD.find_element(
            By.XPATH,
            "/html/body/div/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[1]/form/div[2]/img",
        )
        return _img.screenshot_as_png

    def browser(self, **kwargs):
        placa = kwargs["placa"]
        captcha_txt = kwargs["captcha_txt"]

        if not captcha_txt:
            _img = self.WEBD.find_element(
                By.XPATH,
                "/html/body/div/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[1]/form/div[2]/img",
            )
            return Image.open(io.BytesIO(_img.screenshot_as_png)).resize((465, 105))

        a = self.WEBD.find_element(
            By.XPATH,
            "/html/body/div/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[1]/form/div[1]/input",
        )
        a.send_keys(placa)

        c = self.WEBD.find_element(
            By.XPATH,
            "/html/body/div/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[1]/form/div[2]/input",
        )
        c.send_keys(captcha_txt)

        d = self.WEBD.find_element(
            By.XPATH,
            "/html/body/div/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[1]/form/button",
        )
        d.click()

        time.sleep(1)
        _iframe = self.WEBD.find_element(By.CSS_SELECTOR, "iframe")
        self.WEBD.switch_to.frame(_iframe)

        # Check if limit of scraping exceeded and wait
        limit_msg = self.WEBD.find_elements(By.XPATH, "/html/body")
        if limit_msg and "superado" in limit_msg[0].text:
            # self.WEBD.refresh()
            return -1

        # Check if error message pops up
        error_msg = self.WEBD.find_elements(
            By.XPATH, "/html/body/div[3]/div/div/div[2]"
        )

        # Error: wrong captcha
        if error_msg and "incorrecto" in error_msg[0].text:
            # self.WEBD.refresh()
            return -2

        # Error: no data for placa
        if error_msg and "registrados" in error_msg[0].text:
            # self.WEBD.refresh()
            return {}

        # No Error: proceed with data capture
        headers = (
            "aseguradora",
            "fecha_inicio",
            "fecha_fin",
            "placa",
            "certificado",
            "uso",
            "clase",
            "vigencia",
            "tipo",
            "fecha_venta",
            "fecha_anulacion",
        )
        response = {
            i: self.WEBD.find_element(
                By.XPATH,
                f"/html/body/div[2]/div/div/div/div[2]/table/tbody/tr[1]/td[{j}]",
            ).text.strip()
            for i, j in zip(headers, range(1, 11))
        }

        # get out of frame and click CERRAR
        self.WEBD.switch_to.default_content()
        e = self.WEBD.find_element(
            By.XPATH,
            "/html/body/div[1]/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[2]/div/div/div[3]/button",
        )
        e.click()

        return response


class Sunarp:

    def __init__(self) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True, incognito=True
        )
        # open first URL, wait and open second URL (avoids limiting requests)
        self.WEBD.get("https://www.gob.pe/sunarp")
        time.sleep(2)
        self.WEBD.get("https://www.sunarp.gob.pe/consulta-vehicular.html")
        time.sleep(1)

    def browser(self, **kwargs):
        """returns:
        -1 = captcha ok, image did not load (retry)
         1 = captcha ok, placa does not exist
         image object = captcha ok, placa ok
        """
        placa = kwargs["placa"]
        retry_captcha = False

        while True:
            # get captcha in string format
            captcha_txt = ""
            while not captcha_txt:
                if retry_captcha:
                    self.WEBD.refresh()
                    time.sleep(1)
                # capture captcha image from webpage store in variable
                _img = self.WEBD.find_element(By.ID, "image").get_attribute("src")
                _img = Image.open(io.BytesIO(urllib.request.urlopen(_img).read()))
                captcha_txt = self.process_captcha(_img)

                retry_captcha = True

            # enter data into fields and run
            self.WEBD.find_element(By.ID, "nroPlaca").send_keys(placa)
            time.sleep(0.5)
            self.WEBD.find_element(By.ID, "codigoCaptcha").send_keys(captcha_txt)
            time.sleep(0.5)
            self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/nz-content/div/app-inicio/app-vehicular/nz-layout/nz-content/div/nz-card/div/app-form-datos-consulta/div/form/fieldset/nz-form-item[3]/nz-form-control/div/div/div/button",
            ).click()
            time.sleep(1)

            # if captcha is not correct, refresh and restart cycle, if no data found, return None
            _alerta = self.WEBD.find_elements(By.ID, "swal2-html-container")
            if _alerta and "correctamente" in _alerta[0].text:
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                continue
            elif _alerta and "error" in _alerta[0].text:
                self.WEBD.find_element(
                    By.XPATH, "/html/body/div/div/div[6]/button[1]"
                ).click()
                return 1, None
            else:
                break

        # search for SUNARP image
        _card_image = self.WEBD.find_elements(
            By.XPATH,
            "/html/body/app-root/nz-content/div/app-inicio/app-vehicular/nz-layout/nz-content/div/nz-card/div/app-form-datos-consulta/div/img",
        )

        # no image found, return unsuccesful
        if not _card_image:
            self.WEBD.refresh()
            time.sleep(0.5)
            return -1, None

        # grab image and save in file, return succesful
        else:
            # load card image into memory
            image_object = Image.open(io.BytesIO(_card_image[0].screenshot_as_png))
            time.sleep(1)

            # press boton to start over
            q = self.WEBD.find_element(
                By.XPATH,
                "/html/body/app-root/nz-content/div/app-inicio/app-vehicular/nz-layout/nz-content/div/nz-card/div/app-form-datos-consulta/div/nz-form-item/nz-form-control/div/div/div/button",
            )
            q.click()

            return 0, image_object

    def process_captcha(self, img):
        # split image into six pieces and run OCR to each

        img.save(os.path.join(os.curdir, "other", "sunarp_temp.jpg"))

        READER = easyocr.Reader(["es"], gpu=False)
        WHITE = np.asarray((255, 255, 255, 255))
        BLACK = np.asarray((0, 0, 0, 0))

        img_object = Image.open(os.path.join(os.curdir, "other", "sunarp_temp.jpg"))

        original_img = np.asarray(img_object)
        original_img = np.asarray(
            [[WHITE if mean(i) > 165 else BLACK for i in j] for j in original_img],
            dtype=np.uint8,
        )

        a = len(original_img)
        b = len(original_img[1])

        h = np.full((b, a), 0)
        for x in range(len(original_img)):
            for y in range(len(original_img[0])):
                h[y][x] = int(original_img[x][y][0])

        stopx = []
        delta = -2
        check_for_next = False
        for x in range(180):
            if all([i == 0 for i in h[x]]) is check_for_next:
                stopx.append(x + delta)
                check_for_next = not check_for_next
                delta = delta * -1

        if len(stopx) % 2 == 1:
            stopx.append(179)

        phrase = ""
        for k in range(len(stopx) // 2):
            i = img_object.crop((stopx[2 * k], 0, stopx[2 * k + 1], 60))
            fn = os.path.join(os.curdir, "images", f"temp{k}.jpg")
            i.save(fn)
            c = READER.readtext(fn, text_threshold=0.4)
            if c:
                phrase += c[0][1]

        # ocr text correction
        phrase.replace("€", "C")

        return phrase.upper() if len(phrase) == 6 else ""


class Satmul:

    def __init__(self) -> None:
        self.WEBD = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True, incognito=False
        )
        self.WEBD.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
        time.sleep(2)
        _target = (
            "https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?tri=T&mysession="
            + self.WEBD.current_url.split("=")[-1]
        )
        self.WEBD.get(_target)
        time.sleep(2)

    def browser(self, **kwargs):
        placa = kwargs["placa"]
        # select alternative option from dropdown to reset it
        drop = Select(self.WEBD.find_element(By.ID, "tipoBusquedaPapeletas"))
        drop.select_by_value("busqLicencia")
        time.sleep(0.5)
        # select Busqueda por Documento from dropdown
        drop.select_by_value("busqPlaca")
        time.sleep(0.5)
        # enter placa
        c = self.WEBD.find_element(By.ID, "ctl00_cplPrincipal_txtPlaca")
        c.send_keys(placa)

        # wait until auto-clicking on button actually takes you to next page
        while self.WEBD.find_elements(By.ID, "ctl00_cplPrincipal_txtPlaca"):
            time.sleep(0.5)
            e = self.WEBD.find_elements(By.ID, "ctl00_cplPrincipal_CaptchaContinue")
            if e:
                try:
                    e[0].click()
                except:
                    pass

        time.sleep(2)
        v = self.WEBD.find_elements(By.ID, "ctl00_cplPrincipal_lblMensajeVacio")
        return_button = self.WEBD.find_element(By.ID, "menuOption10")

        if v and "No se encontraron" in v[0].text:
            return_button.click()
            return []

        n = 2
        responses = []
        xpath = lambda row, col: self.WEBD.find_elements(
            By.XPATH,
            f"/html/body/form/div[3]/section/div/div/div[2]/div[8]/div/div/div[1]/div/div/table/tbody/tr[{row}]/td[{col}]",
        )
        while xpath(n, 1):
            keys = [
                "placa",
                "reglamento",
                "falta",
                "documento",
                "fecha_emision",
                "importe",
                "gastos",
                "descuento",
                "deuda",
                "estado",
                "",
                "licencia",
                "doc_tipo",
                "doc_num",
            ]
            resp = {
                dict_key: xpath(n, k + 2)[0].text
                for k, dict_key in enumerate(keys)
                if k != 10
            }

            # search if ticket image exists
            imgs = self.WEBD.find_elements(
                By.ID, "ctl00_cplPrincipal_grdEstadoCuenta_ctl02_lnkImagen"
            )
            # no image found, empty filename string
            if not imgs:
                img_filename = ""
            # image found, grab image and save in file,
            else:
                img_filename = os.path.join(
                    r"D:\pythonCode",
                    "Automation",
                    "ServicioAlertas",
                    "data",
                    "images",
                    f"SATMUL_{placa.upper()}.png",
                )
                # navigate to page with image
                self.WEBD.get(imgs[0].get_attribute("href"))
                time.sleep(0.5)
                # save to file
                with open(img_filename, "wb") as file:
                    file.write(
                        self.WEBD.find_element(By.ID, "imgPapel").screenshot_as_png
                    )
                time.sleep(0.5)
                # back to papeleta screen
                self.WEBD.back()

            time.sleep(0.5)

            # add image filename to response
            resp.update({"img_filename": str(os.path.basename(img_filename))})
            responses.append(resp)
            n += 1

        # click return button for next placa
        return_button = self.WEBD.find_element(By.ID, "menuOption10")
        return_button.click()

        return responses


class Sunat:
    def __init__(self) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.WEBD.get(
            "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        )
        time.sleep(2)

    def browser(self, **kwargs):
        doc_tipo = kwargs["doc_tipo"]
        doc_num = kwargs["doc_num"]

        # TODO: carnet extranjeria
        self.WEBD.find_element(By.ID, "btnPorDocumento").click()
        time.sleep(2)
        self.WEBD.find_element(By.ID, "txtNumeroDocumento").send_keys(doc_num)
        self.WEBD.find_element(By.ID, "btnAceptar").click()
        time.sleep(3)
        self.WEBD.find_element(
            By.XPATH, "/html/body/div/div[2]/div/div[3]/div[2]/a/span"
        ).click()
        time.sleep(2)
        c = self.WEBD.find_elements(By.XPATH, "/html/body/div/div[2]/div/div[2]/div[2]")
        if c and "NO REGISTRA" in c[0].text:
            return []

        response = []
        for i in range(1, 9):
            d = self.WEBD.find_elements(
                By.XPATH, f"/html/body/div/div[2]/div/div[3]/div[2]/div[{i}]/div/div[2]"
            )
            if d:
                response.append(d[0].text)
        e = self.WEBD.find_elements(
            By.XPATH, "/html/body/div/div[2]/div/div[3]/div[2]/div[5]/div/div[4]/p"
        )
        if e:
            response.append(e[0].text)
        self.WEBD.find_element(
            By.XPATH, "/html/body/div/div[2]/div/div[2]/button"
        ).click()

        self.WEBD
        if len(response) == 9:
            return response
