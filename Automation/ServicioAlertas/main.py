import json, sys, os
import logging
from pprint import pprint
import updates, alerts


def start_logger():
    # simple log using same file
    logging.basicConfig(
        filename=LOG_PATH,
        filemode="a",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    return _log


def load_members():
    # loads database
    with open(DATABASE, mode="r", encoding="utf-8") as file:
        return json.load(file)


def save_members(members):
    # writes database
    with open(DATABASE, mode="w+", encoding="utf-8") as file:
        json.dump(members, file, indent=4)
    LOG.info("Database updated succesfully.")


def side(members):

    docs_to_process, placas_to_process = updates.get_records_to_process(members)
    updates.gather_sunarp(members, placas_to_process)
    quit()

    for member in members:
        for soat in member["Resultados"]["Soat"]:
            if soat:
                print(soat["fecha_fin"])

    quit()


def main():
    members = load_members()
    side(members)
    # download raw list of all members from form and add new ones with default data
    if "UPDATE" in sys.argv:
        all_members = updates.load_raw_members(LOG)
        members = updates.add_new_members(
            LOG, all_members=all_members, existing_members=members
        )

        # run SOAT scrape first (if selected) then Automated scrapes (cannot run parallel because of VPN use)
        docs_to_process, placas_to_process = updates.get_records_to_process(members)
        if "SOAT" in sys.argv:
            members = updates.gather_soat(members, placas_to_process)
        members = updates.gather(
            LOG, members, docs_to_process, placas_to_process, responses
        )

        # save updated database from scraping
        save_members(members)

    if "ALERT" in sys.argv:
        # get list of records to process for each alert
        welcome_list, regular_list, warning_list, timestamps = alerts.get_alert_lists(
            members
        )
        # compose and send alerts
        members = alerts.send_alerts(
            LOG,
            members,
            welcome_list,
            regular_list,
            warning_list,
            EMAIL="EMAIL" in sys.argv,
            timestamps=timestamps,
        )

        # save updated database with timestamps and unique ids of sent alerts
        save_members(members)


if __name__ == "__main__":
    # select production or test database
    if not "TEST" in sys.argv:
        DATABASE = os.path.join(os.getcwd(), "data", "members.json")
    else:
        DATABASE = os.path.join(os.getcwd(), "data", "members_test.json")
    # activate logger and log start of program
    LOG_PATH = os.path.join(os.getcwd(), "logs", "alerts_log.txt")
    LOG = start_logger()
    LOG.info("Start Program.")

    # defin variable to be used by scraper threads
    responses = [[] for _ in range(4)]

    # run main program
    main()

    # log end of program
    LOG.info("-" * 20 + " End Program " + "-" * 20)

"""
Prouction Sequence:
- python main.py UPDATE SOAT
- pythom main.py ALERT EMAIL

Automated only:
- python main.py UPDATE

Testing Alerts only (no update)
- python main.py ALERT
"""
