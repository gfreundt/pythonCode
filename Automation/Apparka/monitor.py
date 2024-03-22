import sys, os
import time
from datetime import datetime as dt, timedelta as td
from colorama import Fore, Back, Style
import threading

# custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils
import api


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
        self.API = api.Api()
        threading.Thread(target=api, daemon=True).start()

    def supervisor(self, options):
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

            # check for timeout and turn on flag if exceeded
            if time.time() - self.timer_on > options["timeout_time"]:
                self.timeout_flag = True

            # display status of threads on console
            self.test = self.print_thread_status()

    def print_thread_status(self):
        _elapsed = time.time() - self.timer_on
        _timeout_in = td(seconds=self.options["timeout_time"] - _elapsed)
        print(
            f"{Back.BLUE} Elapsed Time: {str(td(seconds=_elapsed))[:-7]} | Timeout in {str(_timeout_in)[:-7]}.{Style.RESET_ALL}\n"
        )
        for k, thread in enumerate(self.threads):
            _color = Back.GREEN if thread.is_alive() else Back.RED
            _title = f"Process {self.process_names[k]}"
            _numbers = f"{self.current_record[k]:,}/{self.total_records[k]:,} ({self.current_record[k]*100/max(1,self.total_records[k]):.1f}%)"
            _status = f"{'[ACTIVE]' if thread.is_alive() else '[INACTIVE]'}"
            _rate = _elapsed / max(self.current_record[k], 1)
            _eta = dt.now() + td(
                seconds=(self.total_records[k] - self.current_record[k]) * _rate
            )
            _stats = f"[Rate: {_rate:.1f} sec/item] [ETA: {str(_eta)[:-7]}]"

            print(
                f"{_color} {_title:<10} {_numbers:>20} {_status:^8} {_stats>50} {Style.RESET_ALL}"
            )

        # wait and clear screen
        time.sleep(self.UPDATE_FREQUENCY)
        os.system("cls")

    def api(self):
        self.data = "dfdfdfdfdfdfd"
        self.API.run(self.data)
