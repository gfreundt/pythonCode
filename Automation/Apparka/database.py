from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time, sys, os
import csv, json
from datetime import datetime as dt, timedelta as td
from PIL import Image
import io, urllib, shutil
from copy import deepcopy as copy
import uuid
import threading
import easyocr
from tqdm import tqdm
import logging
import random
import pyautogui

from pprint import pprint as print


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils, GoogleUtils


class Database:
    def __init__(self, MONITOR, no_backup=False):
        # define database constants
        self.DATABASE_NAME = os.path.join(os.getcwd(), "data", "rtec_data.json")
        self.LOCK = threading.Lock()
        self.MONITOR = MONITOR
        self.CHROME_UTILS = GoogleUtils()
        # create database backup (negative switch)
        if not no_backup:
            self.backup_database()
        # load database into memory
        self.load_database()
        self.len_database = len(self.database)

    def add_raw_csv_to_database(self, csv_path):
        """Loads (adds) a basic csv file with structure NOMBRE, TIPODOC, DOCNUM, TELEFONO, PLACA
        into the general database with the correct structure"""

        # define local functions that create dictionary structure of vehiculo and record
        create_record = lambda i: {
            "nombre": i[0].strip(),
            "documento": {
                "tipo": i[1],
                "numero": i[2],
                "brevete": None,
                "brevete_actualizado": "01/01/2018",
            },
            "telefono": i[3],
            "vehiculos": vehiculos,
        }
        create_vehiculo = lambda i: {
            "placa": i[4],
            "rtecs": None,
            "rtec_actualizado": "01/01/2019",
            "multas": {
                "sutran": None,
                "sat": None,
                "mtc": None,
                "sutran_actualizado": "06/03/2024",
                "sat_actualizado": "01/01/2021",
                "mtc_actualizado": "01/01/2022",
            },
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
        with open(self.DATABASE_NAME, "a", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4)

    def backup_database(self):
        """Create local copy of database with random 8-letter text to avoid overwriting"""
        _filename = f"rtec_data_backup_{str(uuid.uuid4())[:8]}.json"
        shutil.copyfile(
            self.DATABASE_NAME,
            os.path.join(os.curdir, "data", _filename),
            follow_symlinks=True,
        )
        self.MONITOR.log.info(f"Database backup complete. File = {_filename}.")

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
        self.MONITOR.last_pending = 0
        self.MONITOR.log.info(f"Database write.")

    def update_database_correlatives(self):
        """Opens database, updates correlatives for all records, writes database and closes"""
        self.load_database()
        for k, _ in enumerate(self.database):
            self.database[k]["correlative"] = k
        self.MONITOR.log.info(f"Correlatives updated.")
        self.write_database()

    def upload_to_drive(self):
        print("Uploading to GDrive.....")
        try:
            self.GOOGLE_UTILS.upload_to_drive(
                local_path=self.DATABASE_NAME,
                drive_filename=f"UserData [Backup: {dt.now().strftime('%d%m%Y')}].json",
            )
            self.MONITOR.log.info(f"GDrive upload complete.")
        except:
            self.MONITOR.log.warning(f"GDrive upload ERROR.")

    def export_dashboard(self):
        a = [0 for _ in range(10)]
        b = [0 for _ in range(10)]
        c = [0 for _ in range(10)]
        d = [0 for _ in range(10)]
        e = [0 for _ in range(10)]
        f = [0 for _ in range(10)]
        g = [0 for _ in range(10)]
        h = [0 for _ in range(10)]

        for rec, record in enumerate(self.database):
            a[0] += 1
            # build documento
            if record["documento"]["tipo"] == "DNI":
                b[1] += 1
            elif record["documento"]["tipo"] == "CE":
                b[2] += 1
            else:
                b[3] += 1

            # build brevete
            if record["documento"]["brevete"]:
                _fecha = (
                    dt.strptime(
                        record["documento"]["brevete"]["fecha_hasta"], "%d/%m/%Y"
                    )
                    - dt.now()
                )
                if td(days=0) <= _fecha <= td(days=180):
                    c[2] += 1
                if td(days=180) < _fecha <= td(days=360):
                    c[3] += 1
                if td(days=360) < _fecha <= td(days=540):
                    c[4] += 1
                if _fecha > td(days=540):
                    c[5] += 1
                c[1] = sum(c[2:6])  # Total Vigente
                c[6] += _fecha < td(days=0)  # Total Vencido
            else:
                c[7] += 1  # Total sin data

            # build vehiculos
            for n in range(4):
                if len(record["vehiculos"]) == n:
                    d[n + 2] += 1

            # build revisiones tecnicas
            for vehiculo in record["vehiculos"]:
                if vehiculo["rtecs"]:
                    try:
                        _fecha = (
                            dt.strptime(vehiculo["rtecs"][0]["fecha_hasta"], "%d/%m/%Y")
                            - dt.now()
                        )
                    except:
                        print(record["correlative"])
                    if td(days=0) <= _fecha <= td(days=90):
                        e[3] += 1
                    if td(days=90) < _fecha <= td(days=180):
                        e[4] += 1
                    if _fecha > td(days=180):
                        e[5] += 1

                    e[6] += _fecha < td(days=0)  # Total Vencido
                else:
                    e[7] += 1  # Total sin data

                # build multas
                _multas = vehiculo["multas"]
                if _multas["sutran"]:
                    f[1] += 1
                if _multas["sat"]:
                    f[2] += 1
                if _multas["mtc"]:
                    f[3] += 1

            e[2] = sum(e[3:6])  # Total Vigente
            e[1] = e[2] + e[6] + e[7]
            f[0] = sum(f[1:])

        # last update date and time
        with open("updater.log", "r") as file:
            logs = file.read()
            for log in logs[::-1]:
                if "database write" in log.lower():
                    g[0] = log[:10]
                    g[1] = log[11:19]
                    break

        response = (
            {
                "Usuarios Totales": a[0],
                "Documento": sum(b[1:]),
                "DNI": b[1],
                "CE": b[2],
                "DOC<otros>": b[3],
                "Brevete": c[1] + c[6] + c[7],
                "BRVigente": c[1],
                "BRVenc6": c[2],
                "BRVenc6-12": c[3],
                "BRVenc12-18": c[4],
                "BRVenc18+": c[5],
                "BRVencido": c[6],
                "BR<otros>": c[7],
                "NoReg": d[1],
                "Reg:": sum(d[3:6]),
                "VR1": d[3],
                "VR2": d[4],
                "VR3": d[5],
                "Promedio": f"{(d[1]+d[3]+d[4]*2+d[5]*3)/a[0]:.2f}",
                "RTVigente": e[2],
                "RT3": e[3],
                "RT3-6": e[4],
                "RT6+": e[5],
                "RTVencida": e[6],
                "NoRT": e[7],
                "MulTOT": f[0],
                "MulSUT": f[1],
                "MulSAT": f[2],
                "MulMTC": f[3],
                "Creado": dt.now(),
            },
        )

        return response
