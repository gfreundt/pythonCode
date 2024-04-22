import time
from datetime import datetime as dt, timedelta as td
import logging
from gft_utils import ChromeUtils
import scrapers

# remove easyocr warnings
logging.getLogger("easyocr").setLevel(logging.ERROR)


class Updater:

    def __init__(self, parameters):
        self.log_name = parameters["updater"].upper()
        self.URL = parameters["url"]
        self.DB = parameters["database"]
        self.LOG = parameters["logger"]
        self.MONITOR = parameters["monitor"]
        self.options = parameters["options"]
        self.thread_num = parameters["threadnum"]
        self.restarts = 0
        self.consecutive_errors = 0

        match parameters["updater"]:
            case "satimp":
                self.scraper = scrapers.Satimp(self.DB)
            case "brevete":
                self.scraper = scrapers.Brevete(self.DB, self.URL)
            case "revtec":
                self.scraper = scrapers.Revtec(self.DB)
            case "sutran":
                self.scraper = scrapers.Sutran(self.DB)

    def run_full_update(self):
        # first run is normal
        self.full_update()

        # restart wrapper
        while self.restarts <= 3:
            if self.MONITOR.threads[self.thread_num]["info"]["complete"]:
                return
            else:
                time.sleep(3)
                self.restarts += 1
                self.MONITOR.threads[self.thread_num]["info"][
                    "restarts"
                ] = self.restarts
                self.LOG.info(f"{self.log_name} > Restart #{self.restarts}.")
                self.full_update()

        self.LOG.info(f"{self.log_name} > Restart Limit. End Process.")

    def full_update(self):
        # log start of process
        self.LOG.info(f"{self.log_name} > Begin.")

        # create list of all records that need updating in order of priority
        records_to_update = self.records_to_update()
        self.MONITOR.threads[self.thread_num]["info"]["total_records"] = len(
            records_to_update
        )

        # if no records to update, log end of process
        if not records_to_update:
            self.LOG.info(
                f"{self.log_name} > End (Did not start). No records to process."
            )
            self.MONITOR.threads[self.thread_num]["info"]["complete"] = True
            return
        else:
            self.LOG.info(
                f"{self.log_name} > Will process {len(records_to_update):,} records."
            )

        # define Chromedriver and open url for first time
        self.scraper.WEBD = ChromeUtils().init_driver(
            headless=True, verbose=False, maximized=True
        )
        self.scraper.WEBD.get(self.URL)
        time.sleep(3)

        rec = 0  # only in case loop doesn't run
        # iterate on all records that require updating
        for rec, (record_index, position) in enumerate(records_to_update):
            # check monitor flags: timeout -- return
            if self.MONITOR.timeout_flag:
                self.LOG.info(
                    f"{self.log_name} > End (Timeout). Processed {rec} records."
                )
                self.scraper.WEBD.close()
                self.MONITOR.threads[self.thread_num]["info"]["complete"] = True
                return

            # update monitor dashboard data
            self.MONITOR.threads[self.thread_num]["info"]["current_record"] = rec + 1

            # get scraper data
            new_record, captcha_attempts = self.get_new_record(record_index, position)

            self.MONITOR.threads[self.thread_num]["info"][
                "captcha_attempts"
            ] += captcha_attempts

            # if error from scraper then if limit of consecutive errors, restart updater, else next record
            if new_record is None:
                if self.consecutive_errors > 4:
                    return
                else:
                    continue

            # insert data into database
            self.update_record(record_index, position, new_record)

        # natural end of process (all records processed before timeout)
        self.LOG.info(f"{self.log_name} > End (Complete). Processed: {rec} records.")
        self.MONITOR.threads[self.thread_num]["info"]["complete"] = True
        return

    def records_to_update(self):
        _lut = self.MONITOR.threads[self.thread_num]["info"]["lut"]
        to_update = self.scraper.records_to_update(_lut)
        return [i for j in to_update for i in j]

    def get_new_record(self, record_index, position):
        _doc_num = self.DB.database[record_index]["documento"]["numero"]
        _doc_tipo = self.DB.database[record_index]["documento"]["tipo"]

        if self.DB.database[record_index]["vehiculos"]:
            _placa = self.DB.database[record_index]["vehiculos"][position]["placa"]
        else:
            _placa = ""

        try:
            new_record, captcha_attempts = self.scraper.browser(
                doc_num=_doc_num, doc_tipo=_doc_tipo, placa=_placa
            )
            self.consecutive_errors = 0
            return new_record, captcha_attempts
        except KeyboardInterrupt:
            quit()
        except:
            # in case scraper crashes, skip record and add to error count
            self.LOG.warning(
                f"{self.log_name} > Skipped Record {record_index} (scraper error)."
            )
            self.consecutive_errors += 1
            return None, 0

    def update_record(self, record_index, position, new_record):
        self.scraper.update_record(record_index, position, new_record)
        # update timestamp
        self.MONITOR.threads[self.thread_num]["info"][
            "last_record_updated"
        ] = time.time()
