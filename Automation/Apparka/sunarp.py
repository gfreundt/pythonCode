from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time, sys, os
from datetime import datetime as dt, timedelta as td
from random import randrange
import easyocr
from google.cloud import vision
import numpy as np
from PIL import Image
from statistics import mean


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class Sunarp:
    # define class constants
    URL1 = "https://www.gob.pe/sunarp"
    URL2 = "https://www.sunarp.gob.pe/consulta-vehicular.html"

    def __init__(self, **kwargs) -> None:
        self.READER = easyocr.Reader(["es"], gpu=False)
        self.DB = kwargs["database"]
        self.LOG = kwargs["logger"]
        self.MONITOR = kwargs["monitor"]
        self.options = kwargs["options"]
        self.thread_num = kwargs["threadnum"]

        self.DB.counter = 0

    def run_full_update(self):

        # log start of process
        self.LOG.info(f"SUNARP > Begin.")

        # create list of all records that need updating with priorities
        records_to_update = self.list_records_to_update()

        self.MONITOR.threads[self.thread_num]["total_records"] = len(records_to_update)
        self.LOG.info(f"SUNARP > Will process {len(records_to_update):,} records.")

        # define Chromedriver and open url for first time
        self.WEBD = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True
        )
        self.WEBD.get(self.URL1)
        time.sleep(2)
        self.WEBD.get(self.URL2)
        time.sleep(2)

        rec = 0
        # iterate on all records that require updating
        for rec, (record_index, position) in enumerate(records_to_update):
            # check monitor flags: timeout
            if self.MONITOR.timeout_flag:
                self.LOG.info(f"SUNARP > End (Timeout). Processed {rec+1} records.")
                return

            # update monitor dashboard data
            self.MONITOR.threads[self.thread_num]["current_record"] = rec + 1

            # get scraper data, if webpage fails, wait, reload page and skip record
            _placa = self.DB.database[record_index]["vehiculos"][position]["placa"]
            try:
                new_record = self.scraper(placa=_placa)
            except KeyboardInterrupt:
                quit()
            except:
                self.LOG.warning(f"SUNARP > Skipped Record {rec}.")
                time.sleep(1)
                self.WEBD.refresh()
                time.sleep(1)
                continue

            # update brevete data and last update in database
            self.DB.database[record_index]["vehiculos"][position]["sunarp"] = new_record
            self.DB.database[record_index]["vehiculos"][position][
                "sunarp_actualizado"
            ] = dt.now().strftime("%d/%m/%Y")

            # timestamp
            self.MONITOR.threads[self.thread_num]["last_record_updated"] = time.time()

            # check monitor flags: timeout
            if self.MONITOR.timeout_flag:
                # self.DB.write_database()
                self.LOG.info(f"End SUNARP (Timeout). Processed {rec+1} records.")
                self.WEBD.close()
                return

        # log natural end of process
        self.LOG.info(f"SUNARP > End (Complete). Processed: {rec+1} records.")

    def list_records_to_update(self, last_update_threshold=365):
        self.MONITOR.threads[self.thread_num]["lut"] = last_update_threshold
        to_update = []
        for record_index, record in enumerate(self.DB.database):
            for veh_index, vehiculo in enumerate(record["vehiculos"]):
                if not "sunarp_actualizado" in vehiculo:
                    to_update.append(record_index, veh_index)

        return to_update

    def scraper(self, placa):
        while True:
            # enter PLACA
            x = self.WEBD.find_element(
                By.ID,
                "MainContent_txtNoPlaca",
            )
            x.send_keys(placa)
            time.sleep(2)

            # grab CAPTCHA image and OCR
            u = self.WEBD.find_element(By.ID, "ctl00_MainContent_captcha_Placa")
            u.screenshot("captcha_sunarp.png")
            ocr = self.detect_text("captcha_sunarp.png")
            if ocr:
                captcha_txt = ocr[0]
            else:
                self.WEBD.refresh()
                time.sleep(0.5)
                continue

            # enter CAPTCHA
            y = self.WEBD.find_element(By.ID, "MainContent_txtCaptchaValidPlaca")
            y.send_keys(captcha_txt)
            time.sleep(1)
            z = self.WEBD.find_element(By.ID, "MainContent_btnSearch")
            z.click()
            time.sleep(2)

            # grab SUNARP image and save in file and clean it -- if not present try with new captcha
            _card_image = self.WEBD.find_elements(By.ID, "MainContent_imgPlateCar")
            if not _card_image:
                self.WEBD.refresh()
                time.sleep(0.5)
            else:
                _filename = os.path.join(
                    "d:\pythonCode\Automation\Apparka\data", f"SUNARP_{placa}.png"
                )
                _card_image[0].screenshot(_filename)
                self.clean_image(_filename)  # outputs 'clean_sunarp.png'
                break

        # extract information from saved file
        response = self.parse_response(self.detect_text("clean_sunarp.png")[0])

        # press OTRA BUSQUEDA
        time.sleep(3)
        q = self.WEBD.find_element(By.ID, "MainContent_btnReturn")
        q.click()

        return response

    def clean_image(self, path):
        WHITE = np.asarray((255, 255, 255, 255))
        BLACK = np.asarray((0, 0, 0, 0))

        img = np.asarray(Image.open(path))
        img = np.asarray(
            [[WHITE if mean(i) > 160 else BLACK for i in j] for j in img],
            dtype=np.uint8,
        )
        img = Image.fromarray(img)
        img.save("clean_sunarp.png")  # , mode="RGBA")

    def parse_response(self, raw_response):
        z = []
        # split response in individual lines
        for line in raw_response.splitlines():
            # if line has colon, append as two different items
            if ":" in line:
                z.append(line.split(":")[0].strip())
                z.append(line.split(":")[1].strip())
            else:
                z.append(line)

        # eliminate empty items
        y = [i for i in z if i]

        # build structured response
        col = "SERIE" in y[2]
        response = {
            "placa_validacion": y[8] if col else y[2],
            "serie": y[9] if col else y[4],
            "vin": y[10] if col else y[6],
            "motor": y[11] if col else y[8],
            "color": y[12] if col else y[10],
            "marca": y[13] if col else y[12],
            "modelo": y[14],
            "año": self.get_year(y[10] if col else y[6]),
            "placa_vigente": y[16],
            "placa_anterior": y[18],
            "estado": y[20],
            "anotaciones": y[22],
            "sede": y[24],
            "propietarios": y[26:],
        }

        return response

    def get_year(self, vin):
        base_year = 2010 if vin[6].isalpha() else 1980
        offset_options = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "J",
            "K",
            "L",
            "M",
            "N",
        ]

    """
        Code	Year		Code	Year		Code	Year		Code	Year		Code	Year		Code	Year
A	1980		L	1990		Y	2000		A	2010		L	2020		Y	2030
B	1981		M	1991		1	2001		B	2011		M	2021		1	2031
C	1982		N	1992		2	2002		C	2012		N	2022		2	2032
D	1983		P	1993		3	2003		D	2013		P	2023		3	2033
E	1984		R	1994		4	2004		E	2014		R	2024		4	2034
F	1985		S	1995		5	2005		F	2015		S	2025		5	2035
G	1986		T	1996		6	2006		G	2016		T	2026		6	2036
H	1987		V	1997		7	2007		H	2017		V	2027		7	2037
J	1988		W	1998		8	2008		J	2018		W	2028		8	2038
K	1989		X	1999		9	2009		K	2019		X	2029		9	2039
    """

    def detect_text(self, path):
        # stop runaway API requests
        self.DB.counter += 1
        if self.DB.counter > 500:
            self.LOG.warning("SUNARP > Exceeded 500 Vision API Limit.")
            quit()

        client = vision.ImageAnnotatorClient()
        with open(path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        return [i.description for i in response.text_annotations]
