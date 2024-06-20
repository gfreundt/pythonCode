import sys, os
import logging

# local imports
import members, updates, alerts, scrapers


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

    # ALERTS = alerts.Alerts(LOG, MEMBERS)
    # get list of records to process for each alert
    # ALERTS.get_alert_lists()
    # print(ALERTS.welcome_list)
    # print(ALERTS.regular_list)

    UPDATES = updates.Update(LOG, MEMBERS)
    UPDATES.all_updates = {"satimpCodigos": [(10, "DNI", "08257907")]}

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
    # UPDATES.get_records_to_process()

    # Generic Scrapers - AUTO:
    # UPDATES.gather_docs(scraper=scrapers.Brevete(), table="brevetes", date_sep="/")
    # UPDATES.gather_placa(scraper=scrapers.Revtec(), table="revtecs", date_sep="/")
    # UPDATES.gather_with_placa(scraper=scrapers.Sutran(), table="sutrans", date_sep="/")
    # UPDATES.gather_with_placa(scraper=scrapers.CallaoMulta(), table="callaoMultas")

    # Specific Scrapers - AUTO:
    UPDATES.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")

    # Specfic Scrapers - MANUAL:
    # UPDATES.gather_satmul(scraper=scrapers.Satmul(), table="satmuls", date_sep="/")
    # UPDATES.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
    # UPDATES.all_updates = {"sunarps": [(6, "AJP209"), (26, "AUK208")]}
    # UPDATES.gather_sunarp2(scraper=scrapers.Sunarp(), table="sunarps")

    # Pending
    # UPDATES.gather_jneMultas(scraper=scrapers.jneMultas(), table="jnes")
    # UPDATES.gather_osiptel(scraper=scrapers.osiptelLineas(), table="osipteles")
    # Siniestralidad SBS


def main():
    """Program entry point. Executes actions depending on arguments ran at prompt.
    Valid arguments: CHECKSUB, CHECKNEW, UPDATE, MAN, AUTO, ALL, ALERT, EMAIL"""

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
        # manual scrapers first (not threaded)
        if "MAN" in sys.argv or "ALL" in sys.argv:
            UPD.gather_satmul(scraper=scrapers.Satmul(), table="satmuls", date_sep="/")
            UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
            # UPD.gather_sunarp(scraper=scrapers.Sunarp(), table="sunarps")
        # automatic scrapers  second (threads)
        if "AUTO" in sys.argv or "ALL" in sys.argv:
            # generic Scrapers
            UPD.gather_docs(scraper=scrapers.Brevete(), table="brevetes", date_sep="/")
            UPD.gather_placa(scraper=scrapers.Revtec(), table="revtecs", date_sep="/")
            UPD.gather_placa(scraper=scrapers.Sutran(), table="sutrans", date_sep="/")
            UPD.gather_placa(scraper=scrapers.CallaoMulta(), table="callaoMultas")
            # specific Scrapers
            UPD.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")

    # define records that require alerts, craft updates from templates and send email
    if "ALERT" in sys.argv:
        ALERTS = alerts.Alerts(LOG, MEMBERS)
        ALERTS.get_alert_lists()
        # compose and send alerts (if EMAIL switch on)
        ALERTS.send_alerts(EMAIL="EMAIL" in sys.argv)


if __name__ == "__main__":
    # activate logger and log start of program
    LOG = start_logger()
    LOG.info("-" * 15 + "Start Program" + "-" * 15)
    # start main program
    side()
    # main()
    # log end of program and quit
    LOG.info("^" * 16 + " End Program " + "^" * 16)
