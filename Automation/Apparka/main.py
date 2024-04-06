import sys, os, time, csv
from datetime import datetime as dt, timedelta as td
import threading
import logging
from copy import deepcopy as copy

# custom imports
from gft_utils import GoogleUtils, ChromeUtils
import database_dev as database, revtec_dev as revtec, sutran_dev as sutran, brevete_dev as brevete, satimp_dev as satimp
import api

# production: import database, revtec, sutran, brevete, satimp

# import and activate Flask, change logging level to reduce messages
from flask import Flask, render_template, request

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


class Monitor:
    def __init__(self) -> None:
        self.UPDATE_FREQUENCY = 1  # seconds
        self.WRITE_FREQUENCY = 900  # seconds
        self.STALL_TIME = 180  # seconds
        self.DASHBOARD_NAME = os.path.join(os.getcwd(), "data", "dashboard.csv")
        self.threads = []
        self.timeout_flag = False
        self.dash_data = ""

    def supervisor(self, options):
        self.MAX_RESTARTS = 3
        self.kill_em_all = False
        self.options = options
        self.last_pending = 0
        self.last_write = time.time()
        self.start_time = dt.now() - td(seconds=1)  # add second to avoid div by zero

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
                self.update_dashboard()
                self.last_write = time.time()

            # check for timeout exceeded or kill button pressed and turn on flag
            if (
                time.time() - self.timer_on > options["timeout_time"]
                or self.kill_em_all
            ):
                DB.write_database()
                self.timeout_flag = True
                return

            try:
                # check for each process if stalled and turn on flag
                for k, thread in enumerate(self.threads):
                    if (
                        not thread["stalled"]
                        and time.time() - thread["last_record_updated"]
                        > self.STALL_TIME
                    ):
                        self.threads[k]["stalled"] = True
                        """
                        if self.MAX_RESTARTS > self.threads[k]["restarts"]:
                            self.threads[k]["restarts"] += 1
                            _t = copy(thread[k])
                            self.threads.append(_t)
                            _t["thread"].start()
                            LOG.warning(f"Restarted Thread {_t['name']}")
                        """

                # process data to update status of threads
                self.api_data = self.generate_status()

            except:
                pass

            # wait to restart status update
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
        for thread in self.threads:
            _status = (
                "INACTIVE"
                if not thread["thread"].is_alive()
                else "STALLED" if thread["stalled"] else "ACTIVE"
            )
            _process = thread["name"]
            _lut = thread["lut"]
            _cur_rec = f"{thread['current_record']:,}"
            _tot_recs = f"{thread['total_records']:,}"
            _complet = (
                f"{thread['current_record']*100/max(1,thread['total_records']):.1f}%"
            )
            _rate = max(thread["current_record"] * 3600 / _elapsed, 1)
            _eta = (
                str(
                    dt.now()
                    + td(
                        hours=(thread["total_records"] - thread["current_record"])
                        / _rate
                    )
                )[:-7]
                if _status == "ACTIVE"
                else str(_elapsed)
            )
            data.append(
                {
                    "process": _process,
                    "lut": _lut,
                    "cur_rec": _cur_rec,
                    "tot_recs": _tot_recs,
                    "complet": _complet,
                    "status": _status,
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


def scraper_options():
    options = {"timeout_time": 42600, "scraper_delay": 7}
    # no options entered
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
            "gfreundt@gmail.com",
            "UserData Process",
            f"Finished Process on {dt.now()}.\nRevTec: {MONITOR.total_records_revtec}\nBrevete: {MONITOR.total_records_brevete}",
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
    # starts browser on lower right of screen
    _stats_view = threading.Thread(target=api.stats_view, args=(MONITOR,), daemon=True)
    _stats_view.start()


def start_scrapers(arguments, options):
    # use exec to avoid rewriting parameters
    for k, var in enumerate(arguments):
        _params = f"(database=DB, logger=LOG, monitor=MONITOR, options=options, threadnum={k})"
        exec(
            f"global {var.lower()}x; {var.lower()}x = {var.lower()}.{var.title()}{_params}"
        )
        exec(
            f"MONITOR.threads.append({{'name': '{var.title()}','thread': threading.Thread(target={var.lower()}x.run_full_update, daemon=True)}})"
        )

    # add placeholders and start time to scraper thread data
    for k, thread in enumerate(MONITOR.threads):
        MONITOR.threads[k].update(
            {
                "start_time": dt.now(),
                "total_records": 0,
                "current_record": 0,
                "last_record_updated": time.time(),
                "stalled": False,
                "restarts": 0,
            }
        )

    # starts threads staggered to avoid webdriver conflicts
    for thread in MONITOR.threads:
        thread["thread"].start()
        time.sleep(options["scraper_delay"])

    # join scraper threads
    for thread in MONITOR.threads:
        thread["thread"].join()


def main():
    # select scrapers to run according to parameters or set all scrapers if no parameters entered
    arguments = sys.argv[1:]
<<<<<<< HEAD
    VALID_OPTIONS = ["REVTEC"]  # , "REVTEC", "BREVETE", "SUTRAN"]
=======
    VALID_OPTIONS = ["BREVETE"]  # , "REVTEC", "BREVETE", "SUTRAN"]
>>>>>>> e7bb5667b862b9ed4fc37d16af28cecb2a5e4f56
    if not any([i in VALID_OPTIONS for i in sys.argv]):
        arguments = VALID_OPTIONS

    # parse through all starting options (timeout, etc)
    options = scraper_options()

    # begin all threads
    start_monitors(options)
    start_scrapers(arguments, options)

    # wrap-up: make a copy of database file to GDrive
    DB.upload_to_drive()


def side():

    time.sleep(30)
    return

    for rec, record in enumerate(DB.database):
        if record["vehiculos"] == None:
            DB.database[rec]["vehiculos"] = []

    DB.write_database()


if __name__ == "__main__":
    # start logger and register program start
    LOG = start_logger(test=False)
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
