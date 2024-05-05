import sys, os, time, csv, json
from datetime import datetime as dt, timedelta as td
import threading
import logging

# from copy import deepcopy as copy
import platform

# custom imports
from gft_utils import GoogleUtils, ChromeUtils
import updaters
import database  # , revtec, sutran, brevete, satimp
import api

# import and activate Flask, change logging level to reduce messages
# from flask import Flask, render_template, request

# app = Flask(__name__)
# logging.getLogger("werkzeug").setLevel(logging.ERROR)

from copy import deepcopy as copy
from pprint import pprint


class Monitor:
    def __init__(self) -> None:
        self.UPDATE_FREQUENCY = 1  # seconds
        self.WRITE_FREQUENCY = 900  # seconds
        self.STALL_TIME = 180  # seconds
        self.DASHBOARD_NAME = os.path.join(os.getcwd(), "data", "dashboard.csv")
        self.threads = []
        self.timeout_flag = False
        self.dash_data = ""
        self.device = str(platform.system()).strip()
        self.PARAMETERS_PATH = "parameters.json"
        with open(self.PARAMETERS_PATH, mode="r") as file:
            self.params = json.load(file)

    def supervisor(self, options):
        self.kill_em_all = False
        self.options = options
        self.last_pending = 0
        self.last_write = time.time()
        self.start_time = dt.now() - td(seconds=1)  # add one sec to avoid div by zero

        # register start of process and off flag
        self.timer_on = time.time()
        self.timeout_flag = False
        self.stalled = False

        # get latest dashboard
        self.update_dashboard()

        # permanent management of status
        while True:
            # check if enough time elapsed to write database
            if time.time() - self.last_write > self.WRITE_FREQUENCY:
                DB.write_database()
                LOG.info(self.api_data)
                self.update_dashboard()
                self.last_write = time.time()

            # check for timeout exceeded or kill button pressed and turn on flag
            if (
                time.time() - self.timer_on > self.options["timeout_time"]
                or self.kill_em_all
            ):
                self.timeout_flag = True
                return

            # check if individual thread is alive
            inactive_threads = 0
            for th, thread in enumerate(self.threads):
                if not thread["thread"].is_alive():
                    self.threads[th]["info"]["status"] = "INACTIVE"
                    inactive_threads += 1

            # check if all threads are in "INACTIVE" mode and activate soft kill
            if inactive_threads == len(self.threads):
                # TODO: create own flag
                self.timeout_flag = True

            # process data to update status of threads
            self.api_data = self.generate_status()

            # update wait time
            time.sleep(self.UPDATE_FREQUENCY)

    def generate_status(self):
        _elapsed = time.time() - self.timer_on
        _write_elapsed = time.time() - self.last_write
        _timeout_in = td(seconds=self.options["timeout_time"] - _elapsed)

        # build header
        data = [
            {
                "elapsed": str(td(seconds=_elapsed))[:-7],
                "timeout_in": str(_timeout_in)[:-7],
                "timeout_time": str(dt.now() + _timeout_in)[11:-7],
                "last_write": str(dt.now() - td(seconds=_write_elapsed))[11:-7],
            }
        ]

        # build body
        for th, thread in enumerate(self.threads):
            info = thread["info"]

            if (
                thread["info"]["status"] == "INACTIVE"
                and info.get("finished")
                and "Ended" not in info["finished"]
            ):
                self.threads[th]["info"]["finished"] = f"Ended: {str(dt.now())[:-7]}"
            _process = info["name"]
            _lut = info["lut"]
            _captcha = (
                f"{info['current_record']*100/max(info['captcha_attempts'],1):.1f}%"
            )
            _cur_rec = f"{info['current_record']:,}"
            _pend_recs = f"{info['total_records']-info['current_record']:,}"
            _restarts = f"{info['restarts']:,}"
            _complet = (
                (f"{info['current_record']*100/max(info['total_records'],1):.1f}%")
                if info["total_records"] > 0
                else "100%"
            )
            _rate = max(info["current_record"] * 3600 / _elapsed, 1)
            _eta = (
                str(
                    dt.now()
                    + td(hours=(info["total_records"] - info["current_record"]) / _rate)
                )[:-7]
                if thread["info"]["status"] == "ACTIVE"
                else info.get("finished", "")
            )
            data.append(
                {
                    "process": _process,
                    "lut": _lut,
                    "captcha": _captcha,
                    "cur_rec": _cur_rec,
                    "pend_recs": _pend_recs,
                    "complet": _complet,
                    "status": thread["info"]["status"],
                    "restarts": _restarts,
                    "rate": f"{_rate:.1f} ",
                    "eta": _eta,
                }
            )
        return data

    def update_dashboard(self):
        with open(self.DASHBOARD_NAME, "r") as file:
            _reader = csv.reader(file, delimiter="|", quotechar="'")
            self.dash_data = [i for i in _reader][0]


def start_logger(test=False):
    _date = str(dt.now())[:19].replace(":", ".")
    _filename = os.path.join(
        os.getcwd(),
        "logs",
        f"updater [{_date}].log" if not test else f"updater_dev [{_date}].log",
    )
    logging.basicConfig(
        filename=_filename,
        filemode="w",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    return _log


def updater_options():
    options = {"timeout_time": 42600, "updater_delay": 7}
    # no options entered.
    if len(sys.argv) == 1:
        return options
    # iterate all options entered and build options dictionary (start with default values)
    for arg in sys.argv[1:]:
        if "-time:" in arg:
            options["timeout_time"] = int(arg.split(":")[-1])
    return options


def send_gmail():
    try:
        GOOGLE_UTILS.send_gmail(
            fr="gabfre@gmail.com",
            to="gfreundt@gmail.com",
            subject="UserData Process",
            body=f"Finished Process on {dt.now()}.\nRevTec: {MONITOR.total_records_revtec}\nBrevete: {MONITOR.total_records_brevete}",
        )
        LOG.info(f"GMail sent.")
    except:
        LOG.warning(f"Gmail ERROR.")


def start_monitors(options):
    # placeholder port data until another thread populates it
    MONITOR._port = 0
    # start monitor (controls timeouts and generates status data)
    _monitor = threading.Thread(target=MONITOR.supervisor, args=(options,), daemon=True)
    _monitor.start()
    # starts server to be able to access data via browser
    _api = threading.Thread(target=api.main, args=(MONITOR, LOG), daemon=True)
    _api.start()
    # starts browser on lower right of screen (not on RPI)
    if MONITOR.device == "Windows":
        _stats_view = threading.Thread(
            target=api.stats_view, args=(MONITOR,), daemon=True
        )
        _stats_view.start()


def start_updaters(requested_updaters, options):
    URLS = {
        "satimp": "https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx",
        "brevete": "https://licencias.mtc.gob.pe/#/index",
        "revtec": "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx",
        "sutran": "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/",
    }
    LUTS = {"satimp": 60, "brevete": 60, "revtec": 30, "sutran": 15}

    for threadnum, updater in enumerate(requested_updaters):
        _parameters = {
            "updater": updater,
            "url": URLS[updater],
            "database": DB,
            "logger": LOG,
            "monitor": MONITOR,
            "options": options,
            "threadnum": threadnum,
        }
        _instance = updaters.Updater(_parameters)
        _thread = threading.Thread(target=_instance.run_full_update)
        _info = {
            "name": updater,
            "lut": LUTS[updater],
            "start_time": dt.now(),
            "captcha_attempts": 0,
            "total_records": 0,
            "current_record": 0,
            "last_record_updated": time.time(),
            "stalled": False,
            "complete": False,
            "status": "ACTIVE",
            "restarts": 0,
            "finished": str(dt.now()),
        }
        MONITOR.threads.append({"thread": _thread, "info": _info})
        _thread.start()
        time.sleep(options["updater_delay"])

    # join updater threads
    for thread in MONITOR.threads:
        thread["thread"].join()


def main():
    # select updaters to run according to parameters or set all updaters if no parameters entered
    arguments = sys.argv[1:]
    arguments = [i["name"] for i in MONITOR.params["scrapers"]]

    # parse through all starting options (timeout, etc)
    options = updater_options()

    # begin all threads
    start_monitors(options)
    start_updaters(arguments, options)

    # write db when processes are over (finished all records, timeout or soft interrupt)
    DB.write_database()

    # wrap-up: make a copy of database file to GDrive
    DB.upload_to_drive()


def side():

    s = []

    for i in DB.database:
        try:
            x = i["vehiculos"][0]["rtecs"][0]["certificadora"]
            if len(x) > 6:
                s.append(x)
        except:
            pass

    a = set(s)
    for i in a:
        print(i)

    return

    to_update = [[] for _ in range(4)]

    for record_index, record in enumerate(DB.database):
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

    return

    v = 0
    for rec, record in enumerate(DB.database):
        for veh_index, vehiculo in enumerate(record["vehiculos"]):

            if vehiculo["rtecs"] and type(vehiculo["rtecs"]) != list:
                pprint(DB.database[rec])
                DB.database[rec]["vehiculos"][veh_index]["rtecs"] = copy(
                    [vehiculo["rtecs"]]
                )
                print("---------------")
                pprint(DB.database[rec])
                print("++++++++++++++++")
                v += 1
                input()
    print(v)

    # DB.write_database()


if __name__ == "__main__":
    # start logger and register program start
    LOG = start_logger()
    LOG.info("Updater Begin.")

    # init monitor, database and Google functions (drive, gmail, etc)
    DB = database.Database(no_backup=False, test=False, logger=LOG)
    MONITOR = Monitor()
    GOOGLE_UTILS = GoogleUtils()

    # side()
    # quit()

    # run main code
    main()

    # register program end
    LOG.info("Updater End.")
