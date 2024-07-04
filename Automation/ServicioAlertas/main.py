import sys, os
import logging
from pprint import pprint

# local imports
import members, updates, messages, alerts, scrapers, maintenance


def start_logger():
    """Start logger, always use same log file."""
    # TODO: include parameters to split file into smaller versions
    LOG_PATH = os.path.join(os.getcwd(), "logs", "alerts_log.txt")
    logging.basicConfig(
        filename=LOG_PATH,
        filemode="a",
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    return _log


def side():
    # function used for testing
    print("************* RUNNING SIDE *************")
    MEMBERS = members.Members(LOG)
    MEMBERS.create_30day_list()
    MAINT = maintenance.Maintenance(LOG, MEMBERS)
    MAINT.soat_images()
    return

    # ALERTS = alerts.Alerts(LOG, MEMBERS)
    # get list of records to process for each alert
    # ALERTS.get_alert_lists()
    # print(ALERTS.welcome_list)
    # print(ALERTS.regular_list)

    UPDATES = updates.Update(LOG, MEMBERS)
    # UPDATES.all_updates = {"brevetes": [(12, "DNI", "07760153")]}

    # UPDATES.gather_placa(scraper=scrapers.Sutran(), table="sutrans", date_sep="/")

    # UPDATES.get_records_to_process()
    # pprint(UPDATES.all_updates)
    # return
    # MEMBERS.add_new_members()
    # MEMBERS.restart_database()
    # return

    # import sunarp

    # c = sunarp.ocr_and_parse(
    #     "D:\pythonCode\Automation\ServicioAlertas\data\images\SUNARP_BEX012.png"
    # )
    # return
    # select docs and placas to update
    UPDATES.get_records_to_process()

    # Generic Scrapers - AUTO:

    # UPDATES.gather_placa(scraper=scrapers.Revtec(), table="revtecs", date_sep="/")
    # UPDATES.gather_with_placa(scraper=scrapers.Sutran(), table="sutrans", date_sep="/")
    # UPDATES.gather_with_placa(scraper=scrapers.CallaoMulta(), table="callaoMultas")

    # Specific Scrapers - AUTO:
    # UPDATES.gather_brevete(scraper=scrapers.Brevete(), table="brevetes", date_sep="/")
    # UPDATES.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")

    # Specfic Scrapers - MANUAL:
    # UPDATES.gather_satmul(scraper=scrapers.Satmul(), table="satmuls", date_sep="/")
    UPDATES.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
    # UPDATES.all_updates = {"sunarps": [(25, "LIA118")]}
    # print(UPDATES.all_updates)

    # UPDATES.gather_sunarp(scraper=scrapers.Sunarp(), table="sunarps")

    # Pending
    # UPDATES.gather_jneMultas(scraper=scrapers.jneMultas(), table="jnes")
    # UPDATES.gather_osiptel(scraper=scrapers.osiptelLineas(), table="osipteles")
    # Siniestralidad SBS

    UPDATES.gather_record(scraper=scrapers.RecordConductorImage())


def main():
    """Program entry point. Executes actions depending on arguments ran at prompt.
    Valid arguments: CHECKSUB, CHECKNEW, UPDATE, MAN, AUTO, ALL, ALERT, EMAIL, MAINT"""

    # load member database and renew 30-day list
    MEMBERS = members.Members(LOG)
    MEMBERS.create_30day_list()

    # check email account for unsubscribe or resubscribe requests
    if "CHECKSUB" in sys.argv:
        MEMBERS.sub_unsub()

    # check online form for new members and add them to database
    if "CHECKNEW" in sys.argv:
        MEMBERS.add_new_members()

    # define records that require updating and perform updates (scraping)
    if "UPDATE" in sys.argv:
        UPD = updates.Update(LOG, MEMBERS)
        UPD.get_records_to_process()
        pprint(UPD.all_updates)
        # manual scrapers first (not threaded)
        if "MAN" in sys.argv or "ALL" in sys.argv:
            UPD.gather_satmul(scraper=scrapers.Satmul(), table="satmuls", date_sep="/")
            UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
        # automatic scrapers  second (threads)
        if "AUTO" in sys.argv or "ALL" in sys.argv:
            # generic Scrapers
            UPD.gather_placa(scraper=scrapers.Revtec(), table="revtecs", date_sep="/")
            UPD.gather_placa(scraper=scrapers.Sutran(), table="sutrans", date_sep="/")
            # UPD.gather_placa(scraper=scrapers.CallaoMulta(), table="callaoMultas")
            # specific Scrapers
            UPD.gather_sunarp(scraper=scrapers.Sunarp(), table="sunarps")
            UPD.gather_brevete(
                scraper=scrapers.Brevete(), table="brevetes", date_sep="/"
            )
            UPD.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")
            UPD.gather_record(scraper=scrapers.RecordConductorImage())

    # define records that require messages, craft updates from templates and send email
    if "MSG" in sys.argv:
        MSG = messages.Messages(LOG, MEMBERS)
        MSG.get_msg_lists()
        # compose and send alerts (if EMAIL switch on)
        MSG.send_msgs(EMAIL="EMAIL" in sys.argv)

    # define records that require alerts, craft message and send sms
    if "ALERT" in sys.argv:
        ALERT = alerts.Alerts(LOG, MEMBERS)
        ALERT.get_alert_list()
        # compose and send alerts (if SMS switch on)
        ALERT.send_alerts(SMS="SMS" in sys.argv)

    # perform basic maintenance
    if "MAINT" in sys.argv:
        MAINT = maintenance.Maintenance(LOG, MEMBERS)
        MAINT.housekeeping()
        MAINT.soat_images()
        MAINT.sunarp_images()


if __name__ == "__main__":
    # activate logger and log start of program
    LOG = start_logger()
    LOG.info("-" * 15 + "Start Program" + "-" * 15)
    # start main program
    if "SIDE" in sys.argv:
        side()
    else:
        main()
    # log end of program and quit
    LOG.info("^" * 16 + " End Program " + "^" * 16)
