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
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.WARNING)
    return _log

    """import logging.config
    logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True})"""


def scraper_options():
    options = {"timeout_time": 21000}  # 5 hours 50 minutes
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


def main():
    # select scrapers to run according to parameters or set all scrapers if no parameters entered
    arguments = sys.argv
    VALID_OPTIONS = ["RTEC", "BREVETE", "SUTRAN"]
    if not any([i in VALID_OPTIONS for i in sys.argv]):
        arguments = VALID_OPTIONS

    options = scraper_options()

    # start supervisor monitor in daemon thread
    _monitor = threading.Thread(target=MONITOR.supervisor, args=(options,), daemon=True)
    _monitor.start()

    # start required scrapers
    if "BREVETE" in arguments:
        br = brevete.Brevete(database=DB, logger=LOG, monitor=MONITOR, options=options)
        MONITOR.threads.append(threading.Thread(target=br.run_full_update))

    if "RTEC" in arguments:
        re = revtec.RevTec(database=DB, logger=LOG, monitor=MONITOR, options=options)
        MONITOR.threads.append(threading.Thread(target=re.run_full_update))

    if "SUTRAN" in arguments:
        su = sutran.Sutran(database=DB, logger=LOG, monitor=MONITOR, options=options)
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


def side():

    # start supervisor monitor in daemon thread
    _monitor = threading.Thread(
        target=MONITOR.supervisor, args=({"timeout_time": 300},), daemon=True
    )
    _monitor.start()

    import time

    time.sleep(30)
    return

    for rec, record in enumerate(DB.database):
        if record["vehiculos"] == None:
            DB.database[rec]["vehiculos"] = []

    DB.write_database()


if __name__ == "__main__":
    # start logger and register program start
    LOG = start_logger(test=False)
    LOG.warning("Updater Begin.")

    # init monitor, database and Google functions (drive, gmail, etc)
    DB = database.Database(no_backup=False, test=False, logger=LOG)
    MONITOR = monitor.Monitor(database=DB)
    GOOGLE_UTILS = GoogleUtils()

    # side()
    # quit()

    # run main code
    main()

    # register program end
    LOG.info("Updater End.")
