import sys
import time
from datetime import datetime as dt, timedelta as td
from colorama import Fore, Back, Style

# custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils


class Monitor:
    def __init__(self) -> None:
        self.UPDATE_FREQUENCY = 5  # seconds
        self.writes = 0
        self.pending_writes = 0
        self.DEFAULT_TIMEOUT = 7200
        self.GOOGLE_UTILS = GoogleUtils()
        self.threads = []

    def individual(self, timeout_time=7200):
        # register start of process and off flag
        self.timer_on = time.time()
        self.timeout_flag = False
        self.stalled = False

        while True:
            # check for time out and turn on flag if exceeded
            if time.time() - self.timer_on > timeout_time:
                self.timeout_flag = True

            # pause to reduce running speed
            time.sleep(5)

    def top_level(self):
        self.last_pending = 0
        self.last_change = dt.now()
        self.start_time = dt.now() - td(seconds=1)  # add second to avoid div by zero

        # turn on permanent monitor
        while True:
            # display status of threads on console
            status = "Status: "
            for thread in self.threads:
                status += f"| {Back.GREEN + ' ACTIVE ' if thread.is_alive() else Back.RED + ' INACTIVE '} "
            print(status, end="\r")
            print(Style.RESET_ALL)

            time.sleep(5)

        while True:
            # determine if process has stalled if no new records written in time period, change flag
            if self.pending_writes > self.last_pending:
                self.last_pending = int(self.pending_writes)
                self.last_change = dt.now()
            if self.last_change + td(seconds=120) < dt.now():
                self.stalled = True
            # build and output status string (check for div by zero)
            if self.correct_captcha + self.wrong_captcha == 0:
                _captcha_rate = 1
            else:
                _captcha_rate = self.correct_captcha / (
                    self.correct_captcha + self.wrong_captcha
                )

            _nrr = (
                (self.writes + self.pending_writes)
                * 60
                / (dt.now() - self.start_time).total_seconds()
            )

            status = f"[{str(dt.now()-self.start_time)[:-7]}] Process: {self.progress} / {DATABASE.len_database} [{(DATABASE.len_database-self.progress)/(_nrr+0.0001):.0f} min left]\n"
            status += f"[Written: {str(self.writes)}] [Pending Write: {str(self.pending_writes)}]\n"
            status += f"[Since Last Change: {(dt.now()-self.last_change).total_seconds():.0f} sec]\n"
            status += f"[Captcha Rate: {_captcha_rate*100:.1f}%] [Errors: {str(self.errors)}]\n"
            status += f"[New Record Rate: {_nrr:.1f} rec/m]\n"
            status += f'[{"STALLED" if self.stalled else "ACTIVE"}]'
            # print(status)

            time.sleep(self.UPDATE_FREQUENCY)
            # os.system("cls")

    def send_gmail(self):
        try:
            self.GOOGLE_UTILS.send_gmail(
                "gfreundt@gmail.com",
                "UserData Process",
                f"Finished Process on {dt.now()}.\nRevTec: {self.total_records_revtec}\nBrevete: {self.total_records_brevete}",
            )
            self.log.info(f"GMail sent.")
        except:
            self.log.warning(f"Gmail ERROR.")
