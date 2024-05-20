import json, sys, os
import logging
from pprint import pprint
import updates, alerts
import sqlite3


class Database:

    def __init__(self) -> None:
        # select production or test database
        if not "TEST" in sys.argv:
            SQLDATABASE = os.path.join(os.getcwd(), "data", "members.sqlite")
        else:
            SQLDATABASE = os.path.join(os.getcwd(), "data", "membersTEST.sqlite")

        # connect to database
        self.conn = sqlite3.connect(SQLDATABASE)
        self.cursor = self.conn.cursor()

        # only when building - take way later
        self.restart_database()

    def sql(self, table, fields):
        qmarks = ",".join(["?" for _ in range(len(fields))])
        return f"INSERT INTO {table} ({','.join(fields)}) VALUES ({qmarks})"

    def load_scripts(self):
        # Placeholder if we start loading more scripts into it
        SQLSCRIPTS = os.path.join(os.getcwd(), "sql_script1.sql")
        with open(SQLSCRIPTS, mode="r", encoding="utf-8") as file:
            self.SCRIPTS = json.load(file)

    def restart_database(self):
        SQLSCRIPT1 = os.path.join(os.getcwd(), "sql_script1.sql")
        with open(SQLSCRIPT1, mode="r", encoding="utf-8") as file:
            cmd = file.read()
        self.cursor.executescript(cmd)


def start_logger():
    # simple log using same file
    LOG_PATH = os.path.join(os.getcwd(), "logs", "alerts_log.txt")
    logging.basicConfig(
        filename=LOG_PATH,
        filemode="a",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    return _log


def side(members):

    f = [i["Datos"]["Placas"][0] for i in members]
    print(f)
    return
    docs_to_process, placas_to_process = updates.get_records_to_process(members)

    # placas_to_process = [(0, 0, 0, 0, "ABV123")]

    updates.gather_auto(members, placas_to_process)
    # updates.gather_satmul(members, placas_to_process)

    return members

    for member in members:
        for soat in member["Resultados"]["Soat"]:
            if soat:
                print(soat["fecha_fin"])

    quit()


def main():

    MEMBERS = updates.Members(LOG, DB)
    MANUAL = updates.ManualUpdates(LOG, DB)
    AUTO = updates.AutoUpdates(LOG, DB)

    if "UPDATE" in sys.argv:
        # download raw list of all members from form and add new ones
        MEMBERS.add_new_members()
        # select docs and placas to update
        MEMBERS.get_records_to_process()

        # TEST ONLY
        # MANUAL.gather_soat()
        MANUAL.gather_sunarp()
        return

        # run MANUAL (requires user action) scrapes first
        if "MAN" in sys.argv:
            MANUAL.gather_soat()
            MANUAL.gather_sunarp()
            MANUAL.gather_satmul()
        # run AUTO (do not require user action) scrapes after
        AUTO.launch_threads()

    if "ALERT" in sys.argv:
        # get list of records to process for each alert
        welcome_list, regular_list, warning_list, timestamps = alerts.get_alert_lists()
        # compose and send alerts
        alerts.send_alerts(
            LOG,
            members,
            welcome_list,
            regular_list,
            warning_list,
            EMAIL="EMAIL" in sys.argv,
            timestamps=timestamps,
        )


if __name__ == "__main__":

    # activate logger and log start of program

    LOG = start_logger()
    LOG.info("Start Program.")

    DB = Database()

    # define variable to be used by scraper threads
    # responses = [[] for _ in range(10)]

    # run main program
    main()
    DB.conn.commit()
    DB.conn.close()

    # log end of program
    LOG.info("-" * 20 + " End Program " + "-" * 20)

"""
ProDuction Sequence:
- python main.py UPDATE MAN
- pythom main.py ALERT EMAIL

Automated only:
- python main.py UPDATE

Testing Alerts only (no update)
- python main.py ALERT
"""
