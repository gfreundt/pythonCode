import sys, os
import csv, json
from datetime import datetime as dt, timedelta as td
import shutil
from copy import deepcopy as copy
import uuid
import threading


# Custom imports
# sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils


class Database:
    def __init__(self, **kwargs):
        # define database constants
        self.LOG = kwargs["logger"]
        self.BASE_PATH = os.path.join(os.getcwd(), "data")
        if kwargs.get("test") and kwargs["test"]:
            self.DATABASE_FILENAME = "complete_data_dev.json"
        else:
            self.DATABASE_FILENAME = "complete_data.json"
        self.DATABASE_NAME = os.path.join(self.BASE_PATH, self.DATABASE_FILENAME)
        self.DASHBOARD_NAME = os.path.join(self.BASE_PATH, "dashboard.csv")
        # MyDrive/pythonCode/Updater Data:
        self.GDRIVE_PATH_ID = "1Az6eM7Fr9MUqNhj-JtvOa6WOhYBg5Qbs"
        self.LOCK = threading.Lock()
        self.GOOGLE_UTILS = GoogleUtils()
        # create database backup (negative switch)
        if not (kwargs.get("no_backup") and not kwargs["no_backup"]):
            self.backup_database()
        # load database into memory
        self.load_database()
        self.len_database = len(self.database)

    def add_raw_csv_to_database(self, csv_path):
        """
        Loads (adds) a basic csv file into the general database with the correct structure.
        Fills dates with placeholder until data is scraped.
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
                vehiculos = [create_vehiculo(row)] if row[5] else []
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
        # self.update_database_correlatives()

    def backup_database(self):
        """Create local copy of database with random 8-letter text to avoid overwriting"""
        _filename = f"complete_data_backup_{str(uuid.uuid4())[:8]}.json"
        shutil.copyfile(
            self.DATABASE_NAME,
            os.path.join(os.curdir, "data", _filename),
            follow_symlinks=True,
        )
        self.LOG.info(f"Database backup complete. File = {_filename}.")

    def load_database(self):
        """Downloads latest database and stores into to memory as a list of dictionaries"""
        # Identify latest database file version on drive (adjust for time difference)
        files = self.GOOGLE_UTILS.get_drive_files(gdrive_path_id=self.GDRIVE_PATH_ID)
        parser = lambda i: dt(
            year=int(i[:4]),
            month=int(i[5:7]),
            day=int(i[8:10]),
            hour=int(i[11:13]),
            minute=int(i[14:16]),
            second=int(i[17:19]),
        ) - td(hours=5)
        latest_gdrive_file = sorted(
            [
                (f["title"], parser(f["modifiedDate"]), f)
                for f in files
                if self.DATABASE_FILENAME in f["title"]
            ],
            key=lambda i: i[1],
            reverse=True,
        )[0]

        self.GOOGLE_UTILS.download_from_drive(
            gdrive_object=latest_gdrive_file[2],
            local_path=os.path.join(self.BASE_PATH, self.DATABASE_FILENAME),
        )
        self.LOG.info(
            f"Replaced local database file with GDrive version: {latest_gdrive_file[1]}"
        )
        try:
            with open(self.DATABASE_NAME, mode="r") as file:
                self.database = json.load(file)
            self.LOG.info(f"Database loaded: File = {self.DATABASE_NAME}")
            self.LOG.info(f"Database records: {len(self.database):,}.")
        except:
            # identify latest backup
            _backups = [
                i
                for i in sorted(os.scandir(".\data"), key=lambda i: i.stat().st_ctime)
                if "data_backup" in str(i)
            ]

            # overwrite database file with latest backup
            shutil.copy(
                src=os.path.join(_backups[-2]),
                dst=self.DATABASE_NAME,
                follow_symlinks=True,
            )
            # erase backup file created in this session
            os.remove(_backups[-1])
            # write to log
            self.LOG.warning(f"Database recovered from {_backups[-2]}")
            # retry reading database from recovered file
            try:
                with open(self.DATABASE_NAME, mode="r") as file:
                    self.database = json.load(file)
                self.LOG.info(f"Database loaded: File = {self.DATABASE_NAME}")
                self.LOG.info(f"Database records: {len(self.database):,}.")
            except:
                self.LOG.error(f"Database corrupted. End Updater.")
                raise "Database corrupted. End Updater."

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
        self.LOG.info(
            f"DATABASE > Database Checked. {_fixes} fixed made (requires write)."
        )

    def write_database(self):
        """Writes complete updated database file from memory.
        Locks file to avoid race conditions between threads"""
        self.LOCK.acquire()
        with open(self.DATABASE_NAME, "w+") as file:
            json.dump(self.database, file, indent=4)
        self.LOCK.release()
        self.LOG.info(f"DATABASE > Database write.")
        try:
            self.export_dashboard()
        except:
            self.LOG.warning("DATABASE > Cannot generate KPI dashboard file.")

    def update_database_correlatives(self):
        """Updates correlatives for all records, writes database."""
        # open database if not loaded in memory
        try:
            self.database
        except:
            self.load_database()
        # assign correlatives 0-->
        for k, _ in enumerate(self.database):
            self.database[k]["correlative"] = k
        self.write_database()
        self.LOG.info(f"DATABASE > Correlatives updated.")

    def upload_to_drive(self):
        """Attempts to make a copy to local GDrive folder in PC. If not possible,
        use. Google Drive API to upload file directly."""
        try:
            self.GOOGLE_UTILS.upload_to_drive(
                local_path=self.DATABASE_NAME,
                gdrive_filename=self.DATABASE_FILENAME,
                gdrive_path_id=self.GDRIVE_PATH_ID,
            )
            self.GOOGLE_UTILS.upload_to_drive(
                local_path=self.DATABASE_NAME,
                gdrive_filename=f"UserData [Backup: {dt.now().strftime('%d%m%Y')}].json",
                gdrive_path_id=self.GDRIVE_PATH_ID,
            )
            self.LOG.info(f"DATABASE > GDrive upload complete.")
        except:
            self.LOG.warning(f"DATABASE > GDrive upload ERROR.")

    def export_dashboard(self):
        """Aggregates and tabulates data from database to produce KPIs.
        Saves KPIs into file to be used by dashboard."""

        kpis = [0 for _ in range(50)]

        for record in self.database:
            # total records
            kpis[0] += 1

            # build documento
            if record["documento"]["tipo"]:
                kpis[1] += 1
            if record["documento"]["tipo"] == "DNI":
                kpis[2] += 1
            elif record["documento"]["tipo"] == "CE":
                kpis[3] += 1
            else:
                kpis[4] += 1

            # build brevete
            if record["documento"]["brevete"]:
                _fecha = (
                    dt.strptime(
                        record["documento"]["brevete"]["fecha_hasta"], "%d/%m/%Y"
                    )
                    - dt.now()
                )
                if td(days=0) <= _fecha < td(days=180):
                    kpis[7] += 1
                if td(days=180) <= _fecha < td(days=360):
                    kpis[8] += 1
                if td(days=360) <= _fecha < td(days=540):
                    kpis[9] += 1
                if _fecha >= td(days=540):
                    kpis[10] += 1
                if _fecha < td(days=0):
                    kpis[11] += 1  # Total Vencido
            else:
                kpis[12] += 1  # Total sin data

            # build vehiculos
            if not record["vehiculos"]:
                kpis[13] += 1
            else:
                kpis[14] += 1
                for n in range(1, 4):
                    if len(record["vehiculos"]) == n:
                        kpis[n + 14] += 1
                        kpis[19] += n

            # build revisiones tecnicas
            for vehiculo in record["vehiculos"]:
                if vehiculo["rtecs"] and vehiculo["rtecs"][0]["fecha_hasta"]:
                    kpis[20] += 1
                    _fecha = (
                        dt.strptime(vehiculo["rtecs"][0]["fecha_hasta"], "%d/%m/%Y")
                        - dt.now()
                    )
                    if td(days=0) <= _fecha < td(days=90):
                        kpis[22] += 1
                    if td(days=90) <= _fecha < td(days=180):
                        kpis[23] += 1
                    if _fecha >= td(days=180):
                        kpis[24] += 1
                    else:
                        kpis[21] += 1

                    kpis[25] += _fecha < td(days=0)  # Total Vencido
                else:
                    kpis[26] += 1  # Total sin data

                # build multas
                _multas = vehiculo["multas"]
                if _multas["sutran"]:
                    kpis[27] += 1
                if _multas["sat"]:
                    kpis[28] += 1
                if _multas["mtc"]:
                    kpis[29] += 1

        kpis[6] = sum(kpis[7:11])  # Total Vigente
        kpis[5] = sum(kpis[6], kpis[11])
        kpis[18] = kpis[14] / kpis[0]  # Promedio vehiculos/usuario
        kpis[27] = sum(kpis[28:31])  # Total multas impagas

        # last update date and time
        _all_logs = sorted(
            os.scandir(os.path.join(os.getcwd(), "logs")),
            key=lambda i: os.path.getctime(i),
        )

        """ with open(_all_logs[-1], "r") as file:
            logs = file.readlines()
            for log in logs[::-1]:
                if "Database write" in log and not kpis[40]:
                    kpis[40] = log[:10]
                    kpis[41] = log[11:19]
                if "BREVETE > End" in log and not kpis[42]:
                    kpis[42] = int("".join([i for i in log[25:] if i.isdigit()]))
                if "REVTEC > End" in log and not kpis[43]:
                    kpis[43] = int("".join([i for i in log[25:] if i.isdigit()]))
                if "SUTRAN > End" in log and not kpis[44]:
                    kpis[44] = int("".join([i for i in log[25:] if i.isdigit()]))
        """
        # format all items
        response = []
        for item in kpis:
            if type(item) == int:
                response.append(f"{item:,}")
            elif type(item) == float:
                response.append(f"{item:.2f}")
            elif type(item) == dt:
                response.append(str(item))
            else:
                response.append(item)

                # add timestamp
                response.append[str(dt.now())]

        # write data to file to be used by dashboard
        with open(self.DASHBOARD_NAME, "a") as file:
            _writer = csv.writer(file, delimiter="|", quotechar="'")
            _writer.writerow(response)

        self.LOG.info(f"DATABASE > Dashboard data updated.")
