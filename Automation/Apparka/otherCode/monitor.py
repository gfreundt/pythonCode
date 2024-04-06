import sys, os, csv
import time
from datetime import datetime as dt, timedelta as td
from colorama import Fore, Back, Style
import threading
import logging
from flask import Flask, render_template, request


logging.getLogger("werkzeug").setLevel(logging.ERROR)

# custom imports
# sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils


class Monitor:
    def __init__(self, database) -> None:
        self.UPDATE_FREQUENCY = 1  # seconds
        self.WRITE_FREQUENCY = 900  # seconds
        self.DASHBOARD_NAME = os.path.join(os.getcwd(), "data", "dashboard.csv")
        # self.writes = 0
        # self.pending_writes = 0
        self.GOOGLE_UTILS = GoogleUtils()
        self.threads = []
        self.total_records = [1 for _ in range(4)]
        self.current_record = [0 for _ in range(4)]
        self.process_names = ["Brevete", "RevTec", "Sutran", "SAT Deuda Tributaria"]
        self.DB = database

    def api(self, options):
        api()

    def supervisor(self, options):
        global api_data
        global kill_em_all
        kill_em_all = False
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

        while True:
            # check if enough time elapsed to write database
            if time.time() - self.last_write > self.WRITE_FREQUENCY:
                self.DB.write_database()
                self.update_dashboard()
                self.last_write = time.time()

            # check for timeout exceeded or kill button pressed and turn on flag
            if time.time() - self.timer_on > options["timeout_time"] or kill_em_all:
                self.DB.write_database()
                self.timeout_flag = True
                return

            # display status of threads on console
            api_data = self.generate_thread_status()

            # wait
            time.sleep(self.UPDATE_FREQUENCY)

    def generate_thread_status(self):
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
        for k, thread in enumerate(self.threads):
            _active = True if thread.is_alive() else False
            _process = f" {self.process_names[k]} "
            _cur_rec = f" {self.current_record[k]:,} "
            _tot_recs = f" {self.total_records[k]:,} "
            _complet = (
                f" {self.current_record[k]*100/max(1,self.total_records[k]):.1f}%"
            )
            _status = f"{' ACTIVE ' if thread.is_alive() else  ' INACTIVE '}"
            _rate = max(self.current_record[k] * 3600 / _elapsed, 1)
            _eta = str(
                dt.now()
                + td(hours=(self.total_records[k] - self.current_record[k]) / _rate)
            )[:-7]
            data.append(
                {
                    "active": _active,
                    "process": _process,
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
        global dash_data
        with open(self.DASHBOARD_NAME, "r") as file:
            _reader = csv.reader(file, delimiter="|", quotechar="'")
            dash_data = [i for i in _reader]


app = Flask(__name__)


@app.route("/status")
def status():
    return render_template("status.html", data=api_data)


@app.route("/killemall", methods=["POST"])
def killemall():
    global kill_em_all
    kill_em_all = True
    return render_template("status.html", data=api_data)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", data=dash_data)


def api():
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
