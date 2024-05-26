import sys, os
import logging
import members, updates, alerts
import scrapers


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


def side():
    MEMBERS = members.Members(LOG)
    # MEMBERS.add_new_members()
    # MEMBERS.restart_database()
    # return
    UPDATES = updates.Update(LOG, MEMBERS)

    # import sunarp

    # c = sunarp.ocr_and_parse(
    #     "D:\pythonCode\Automation\ServicioAlertas\data\images\SUNARP_BEX012.png"
    # )
    # return
    # select docs and placas to update
    UPDATES.get_records_to_process()

    # Generic Scrapers - AUTO:
    # UPDATES.gather_with_docs(scraper=scrapers.Brevete(), table="brevetes")
    # UPDATES.gather_with_placa(scraper=scrapers.Revtec(), table="revtecs")
    # UPDATES.gather_with_placa(scraper=scrapers.Sutran(), table="sutrans")
    # UPDATES.gather_with_placa(scraper=scrapers.CallaoMulta(), table="callaoMultas")

    # Specific Scrapers - AUTO:
    # UPDATES.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")

    # Specfic Scrapers - MANUAL:
    # UPDATES.gather_satmul(scraper=scrapers.Satmul(), table="satmuls")
    # UPDATES.gather_soat(scraper=scrapers.Soat(), table="soats")
    # UPDATES.gather_sunarp(scraper=scrapers.Sunarp(), table="sunarps")

    # Pending
    # UPDATES.gather_jneMultas(scraper=scrapers.jneMultas(), table="jnes")
    # UPDATES.gather_osiptel(scraper=scrapers.osiptelLineas(), table="osipteles")
    # Siniestralidad SBS


def main():

    # load member database
    MEMBERS = members.Members()

    if "CHECKNEW" in sys.argv:
        # check online form for new members and add them to database
        MEMBERS.add_new_members()

    if "UPDATE" in sys.argv:
        # instanciate updates
        UPDATES = updates.Update(LOG, MEMBERS)
        # select docs and placas to update
        UPDATES.get_records_to_process()

        # manual scrapers first (serial)
        if "MAN" in sys.argv:
            UPDATES.gather_satmul(scraper=scrapers.Satmul(), table="satmuls")
            UPDATES.gather_soat(scraper=scrapers.Soat(), table="soats")
            UPDATES.gather_sunarp(scraper=scrapers.Sunarp(), table="sunarps")

        # auto scrapers (threaded)
        if "AUTO" in sys.argv:
            # Generic Scrapers
            UPDATES.gather_with_docs(scraper=scrapers.Brevete(), table="brevetes")
            UPDATES.gather_with_placa(scraper=scrapers.Revtec(), table="revtecs")
            UPDATES.gather_with_placa(scraper=scrapers.Sutran(), table="sutrans")
            UPDATES.gather_with_placa(
                scraper=scrapers.CallaoMulta(), table="callaoMultas"
            )
            # Specific Scrapers
            UPDATES.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")

    if "ALERT" in sys.argv:
        ALERTS = alerts.Alerts()
        # get list of records to process for each alert
        welcome_list, regular_list, warning_list, timestamps = alerts.get_alert_lists()
        # compose and send alerts
        alerts.send_alerts(
            LOG,
            MEMBERS,
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

    # run main program
    side()
    # main()

    # log end of program
    LOG.info("-" * 20 + " End Program " + "-" * 20)
