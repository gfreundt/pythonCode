import sys, os
import time
from datetime import datetime as dt, timedelta as td
from colorama import Fore, Back, Style
import threading
from flask import Flask, render_template, request

app = Flask(__name__)

# custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils


class Monitor:
    def __init__(self, database) -> None:
        self.UPDATE_FREQUENCY = 1  # seconds
        self.WRITE_FREQUENCY = 900  # seconds
        self.writes = 0
        self.pending_writes = 0
        self.GOOGLE_UTILS = GoogleUtils()
        self.threads = []
        self.total_records = [1 for _ in range(3)]
        self.current_record = [0 for _ in range(3)]
        self.process_names = ["Brevete", "RevTec", "Sutran"]
        self.DB = database
        api_thread = threading.Thread(target=api, daemon=True)
        api_thread.start()

    def supervisor(self, options):
        global api_data
        self.options = options
        self.last_pending = 0
        self.last_write = time.time()
        self.start_time = dt.now() - td(seconds=1)  # add second to avoid div by zero

        # register start of process and off flag
        self.timer_on = time.time()
        self.timeout_flag = False
        self.stalled = False

        while True:
            # check if enough time elapsed to write database
            if time.time() - self.last_write > self.WRITE_FREQUENCY:
                self.DB.write_database()
                self.last_write = time.time()

            # check for timeout and turn on flag if exceeded
            if time.time() - self.timer_on > options["timeout_time"]:
                self.timeout_flag = True

            # display status of threads on console
            api_data = self.generate_thread_status()

            # wait and clear screen
            time.sleep(self.UPDATE_FREQUENCY)
            os.system("cls")

    def generate_thread_status(self):
        _elapsed = time.time() - self.timer_on
        _write_elapsed = time.time() - self.last_write
        _timeout_in = td(seconds=self.options["timeout_time"] - _elapsed)

        # build header
        data = [
            {
                "elapsed": str(td(seconds=_elapsed))[:-7],
                "timeout": str(_timeout_in)[:-7],
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
                f" ({self.current_record[k]*100/max(1,self.total_records[k]):.1f}%) "
            )
            _status = f"{' [ACTIVE] ' if thread.is_alive() else  ' [INACTIVE] '}"
            _rate = self.current_record[k] * 3600 / _elapsed
            _eta = str(
                dt.now()
                + td(seconds=(self.total_records[k] - self.current_record[k]) * _rate)
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


@app.route("/status")
def status():
    return render_template("status.html", data=api_data)


def api():
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
