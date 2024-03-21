import sys, os
from datetime import datetime as dt, timedelta as td
import threading
import logging

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import GoogleUtils
import monitor, database, revtec, sutran, brevete


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
    _log = logging.getLogger()
    _log.setLevel(logging.INFO)
    return _log


def main():
    # select scrapers to run according to parameters or set all scrapers if no parameters entered
    arguments = sys.argv
    VALID_OPTIONS = ["RTEC", "BREVETE", "SUTRAN"]
    if not any([i in VALID_OPTIONS for i in sys.argv]):
        arguments = VALID_OPTIONS

    # start top-level monitor in daemon thread
    _monitor = threading.Thread(target=MONITOR.top_level, daemon=True)
    _monitor.start()

    # MONITOR.threads = []
    # start required scrapers
    if "RTEC" in arguments:
        re = revtec.RevTec(database=DB, logger=LOG)
        MONITOR.threads.append(threading.Thread(target=re.run_full_update))
    if "BREVETE" in arguments:
        br = brevete.Brevete(database=DB, logger=LOG)
        MONITOR.threads.append(threading.Thread(target=br.run_full_update))
    if "SUTRAN" in arguments:
        su = sutran.Sutran(database=DB, logger=LOG)
        MONITOR.threads.append(threading.Thread(target=su.run_full_update))

    for thread in MONITOR.threads:
        thread.start()
    for thread in MONITOR.threads:
        thread.join()

    # wrap-up: update correlative numbers and upload database file to Google Drive, email completion
    DB.update_database_correlatives()
    DB.upload_to_drive()
    # DB.export_dashboard()
    # MONITOR.send_gmail()


if __name__ == "__main__":
    # start logger and register program start
    LOG = start_logger(test=False)
    LOG.info("Updater Begin.")

    # init monitor, database and Google functions (drive, gmail, etc)
    DB = database.Database(no_backup=False, test=False, logger=LOG)
    br = brevete.Brevete(database=DB, logger=LOG)
    br.run_full_update()
    quit()

    MONITOR = monitor.Monitor()
    GOOGLE_UTILS = GoogleUtils()

    main()
    LOG.info("Updater End.")
