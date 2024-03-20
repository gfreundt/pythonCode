import sys, os
import csv, json
from datetime import datetime as dt, timedelta as td
import shutil
from copy import deepcopy as copy
import uuid
import threading
from pprint import pprint


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils


class Database:
    def __init__(self, logger, no_backup=False, test=False):
        # define database constants
        self.LOG = logger
        if not test:
            self.DATABASE_NAME = os.path.join(os.getcwd(), "data", "rtec_data.json")
        else:
            self.DATABASE_NAME = os.path.join(os.getcwd(), "data", "rtec_data_dev.json")
        self.DASHBOARD_NAME = os.path.join(os.getcwd(), "data", "dashboard.json")
        self.LOCK = threading.Lock()
        self.GOOGLE_UTILS = GoogleUtils()
        # create database backup (negative switch)
        if not no_backup:
            self.backup_database()
        # load database into memory
        self.load_database()
        self.len_database = len(self.database)

    def add_raw_csv_to_database(self, csv_path):
        """
        Loads (adds) a basic csv file with structure NOMBRE, TIPODOC, DOCNUM, TELEFONO, PLACA
        into the general database with the correct structure.
        CSV format: nombre, tipo_documento, num_documento, telefono, correo, placa.
        """

        # define local functions that create dictionary structure of vehiculo and record
        create_record = lambda i: {
            "correlative": 0,
            "nombre": i[0].strip(),
            "documento": {
                "tipo": i[1],
                "numero": i[2],
                "brevete": None,
                "brevete_actualizado": "01/01/2018",
            },
            "telefono": i[4],
            "correo": i[3].lower(),
            "vehiculos": vehiculos,
        }
        create_vehiculo = lambda i: {
            "placa": i[5] if len(i) == 6 else None,
            "rtecs": None,
            "rtecs_actualizado": "01/01/2019",
            "multas": {
                "sutran": None,
                "sat": None,
                "mtc": None,
                "sutran_actualizado": "01/01/2020",
                "sat_actualizado": "01/01/2021",
                "mtc_actualizado": "01/01/2022",
            },
        }
        # load raw csv data file
        with open(csv_path, mode="r", encoding="utf-8") as csv_file:
            csv_data = [
                [i.strip().upper() for i in j]
                for j in csv.reader(csv_file, delimiter=",")
            ]
        print(
            f"Merging {self.len_database:,} existing records with {len(csv_data):,} new."
        )
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
        # load database into memory and combine dictionaries
        self.database += json_data
        # write combined data
        self.write_database()
        # redo correlatives
        self.update_database_correlatives()

    def backup_database(self):
        """Create local copy of database with random 8-letter text to avoid overwriting"""
        _filename = f"rtec_data_backup_{str(uuid.uuid4())[:8]}.json"
        shutil.copyfile(
            self.DATABASE_NAME,
            os.path.join(os.curdir, "data", _filename),
            follow_symlinks=True,
        )
        self.LOG.info(f"Database backup complete. File = {_filename}.")

    def load_database(self):
        """Opens database and stores into to memory as a list of dictionaries"""
        with open(self.DATABASE_NAME, mode="r") as file:
            self.database = json.load(file)
        self.LOG.info(f"Database loaded: File = {self.DASHBOARD_NAME}")

    def fix_database_errors(self):
        """Checks database and puts placeholder data in empty critical fields.
        Database must be opened prior.
        Changes will not be permanent unless database is written."""
        # TODO: fechas multas
        _fixes = 0
        for rec, record in enumerate(self.database):
            if not record["documento"]["brevete_actualizado"]:
                self.database[rec]["documento"]["brevete_actualizado"] = "01/01/2000"
                _fixes += 1
            for veh, vehiculo in enumerate(record["vehiculos"]):
                if not vehiculo["rtecs_actualizado"]:
                    self.database[rec]["vehiculos"][veh][
                        "rtecs_actualizado"
                    ] = "01/01/2000"
                    _fixes += 1
        self.LOG.info(f"Database Checked. {_fixes} fixed made (requires write).")

    def write_database(self):
        """Writes complete updated database file from memory.
        Locks file to avoid race conditions between threads"""
        self.LOCK.acquire()
        with open(self.DATABASE_NAME, "w+") as file:
            json.dump(self.database, file, indent=4)
        self.LOCK.release()
        # self.MONITOR.last_pending = 0
        self.LOG.info(f"Database write.")

    def update_database_correlatives(self):
        """Opens database, updates correlatives for all records, writes database and closes"""
        self.load_database()
        for k, _ in enumerate(self.database):
            self.database[k]["correlative"] = k
        self.LOG.info(f"Correlatives updated.")
        self.write_database()

    def upload_to_drive(self):
        """Attempts to make a copy to GDrive folder in PC. If not possible,
        use Google Drive API to upload file directly."""
        try:
            shutil.copy(
                self.DATABASE_NAME, self.GDRIVE_BACKUP_PATH, follow_symlinks=True
            )
        except:
            try:
                self.GOOGLE_UTILS.upload_to_drive(
                    local_path=self.DATABASE_NAME,
                    drive_filename=f"UserData [Backup: {dt.now().strftime('%d%m%Y')}].json",
                )
                self.LOG.info(f"GDrive upload complete.")
            except:
                self.LOG.warning(f"GDrive upload ERROR.")

    def export_dashboard(self):
        """Aggregates and tabulates data from database to produce KPIs.
        Saves KPIs into file to be used by dashboard."""
        a = [0 for _ in range(10)]
        b = [0 for _ in range(10)]
        c = [0 for _ in range(10)]
        d = [0 for _ in range(10)]
        e = [0 for _ in range(10)]
        f = [0 for _ in range(10)]
        g = [0 for _ in range(10)]
        h = [0 for _ in range(10)]

        for record in self.database:
            # total records
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
                    d[n + 1] += 1

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

            d[0] = d[1] + d[2]
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

        response = {
            "a0": f"{a[0]:,}",
            "b0": f"{sum(b[1:]):,}",
            "b1": f"{b[1]:,}",
            "b2": f"{b[2]:,}",
            "b3": f"{b[3]:,}",
            "c0": f"{c[1] + c[6] + c[7]:,}",
            "c1": f"{c[1]:,}",
            "c2": f"{c[2]:,}",
            "c3": f"{c[3]:,}",
            "c4": f"{c[4]:,}",
            "c5": f"{c[5]:,}",
            "c6": c[6],
            "c7": c[7],
            "d1": d[1],
            "d2:": sum(d[3:6]),
            "d3": d[3],
            "d17": d[4],
            "d18": d[5],
            "d19": f"{(d[1]+d[3]+d[4]*2+d[5]*3)/a[0]:.2f}",
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
            "Creado": str(dt.now()),
        }

        # write data to file to be used by dashboard
        with open(self.DASHBOARD_NAME, "w") as file:
            json.dump(response, file, indent=4)
