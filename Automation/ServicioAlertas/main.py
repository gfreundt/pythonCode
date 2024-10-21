import sys, os, time
import threading
import logging
import signal

# ensure pygame does not print welcome message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
# local imports
import members, updates, messages, alerts, scrapers, maintenance, monitor


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


def start_monitor():
    """Start monitor in independent thread."""
    MONITOR.start_monitor()
    return
    thread = threading.Thread(target=MONITOR.start_monitor)
    thread.start()


def side():
    # function used for testing
    print("************* RUNNING SIDE *************")
    MEMBERS = members.Members(LOG, MONITOR)
    MONITOR.show_stats(MEMBERS.kpis)
    time.sleep(5)
    return

    MEMBERS.create_30day_list()
    UPD = updates.Update(LOG, MEMBERS, MONITOR)
    UPD.all_updates = {"soats": [(1, "DNI", "08257907")]}
    # UPD.get_records_to_process()
    print(UPD.all_updates)
    UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
    return

    MONITOR.add_item("SOATS...", type=1)
    UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
    return

    MEMBERS.create_30day_list()
    MAINT = maintenance.Maintenance(LOG, MEMBERS)
    MAINT.soat_images()
    return


def launcher():
    """Program entry point. Executes actions depending on arguments ran at prompt.
    Valid arguments: FULL, MEMBER, UPDATE, MAN, AUTO, ALL, ALERT, EMAIL, MAINT"""

    # load member database
    MEMBERS = members.Members(LOG, MONITOR)
    # if "STATS" in sys.argv or "FULL" in sys.argv:
    #     MONITOR.show_stats(MEMBERS.stats)
    MEMBERS.create_30day_list()
    ALERT = alerts.Alerts(LOG, MEMBERS, MONITOR)

    # check email account for unsubscribe or resubscribe requests
    if "MEMBER" in sys.argv or "FULL" in sys.argv:
        MONITOR.add_item("Checking New Members...", type=0)
        # MEMBERS.sub_unsub()
        MEMBERS.add_new_members()

    # define records that require updating and perform updates (scraping)
    if "UPDATE" in sys.argv or "FULL" in sys.argv:
        UPD = updates.Update(LOG, MEMBERS, MONITOR)
        # required to update alert list to include in update list
        ALERT.get_alert_list()
        MONITOR.add_item("Getting Records to Process...", type=0)
        UPD.get_records_to_process()

        # automatic scrapers
        if "AUTO" in sys.argv or "ALL" in sys.argv or "FULL" in sys.argv:
            MONITOR.add_item("Updating records...", type=0)
            # generic Scrapers
            if UPD.all_updates["revtecs"]:
                MONITOR.add_item("Revision Tecnica...", type=1)
                UPD.gather_placa(
                    scraper=scrapers.Revtec(), table="revtecs", date_sep="/"
                )
            if UPD.all_updates["sutrans"]:
                MONITOR.add_item("SUTRAN...", type=1)
                UPD.gather_placa(
                    scraper=scrapers.Sutran(), table="sutrans", date_sep="/"
                )
            # specific Scrapers
            if UPD.all_updates["sunarps"]:
                MONITOR.add_item("SUNARP...", type=1)
                UPD.gather_sunarp(scraper=scrapers.Sunarp(), table="sunarps")
            if UPD.all_updates["brevetes"]:
                MONITOR.add_item("Brevete...", type=1)
                UPD.gather_brevete(
                    scraper=scrapers.Brevete(), table="brevetes", date_sep="/"
                )
            if UPD.all_updates["satimpCodigos"]:
                MONITOR.add_item("Impuestos SAT...", type=1)
                UPD.gather_satimp(scraper=scrapers.Satimp(), table="satimpCodigos")
            if UPD.all_updates["records"]:
                MONITOR.add_item("Record del Conductor...", type=1)
                UPD.gather_record(scraper=scrapers.RecordConductorImage())
            if UPD.all_updates["sunats"]:
                MONITOR.add_item("Consulta RUC de SUNAT...", type=1)
                UPD.gather_sunat(scraper=scrapers.Sunat(), table="sunats")

        # manual scrapers
        if "MAN" in sys.argv or "ALL" in sys.argv or "FULL" in sys.argv:
            if UPD.all_updates["satmuls"]:
                MONITOR.add_item("Multas SAT...", type=1)
                UPD.gather_satmul(
                    scraper=scrapers.Satmul(), table="satmuls", date_sep="/"
                )
            if UPD.all_updates["soats"]:
                MONITOR.add_item("SOATS...", type=1)
                UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")

        # continue only if all gathering threads have finished
        while any([i.is_alive() for i in UPD.threads]):
            print("waiting for threads")
            time.sleep(1.5)

    # define records that require messages, craft updates from templates and send email
    if "MSG" in sys.argv or "FULL" in sys.argv:
        MONITOR.add_item("Creating messages...", type=0)
        # update 30 day list before selecting which records require messages
        MEMBERS.create_30day_list()
        MSG = messages.Messages(LOG, MEMBERS, MONITOR)
        MSG.get_msg_lists()
        # compose and send alerts (if EMAIL switch on)
        MSG.send_msgs(EMAIL=not ("NOEMAIL" in sys.argv))

    # define records that require alerts, craft message and send sms
    if "ALERT" in sys.argv or "FULL" in sys.argv:
        MONITOR.add_item("Creating alerts...", type=0)
        ALERT.get_alert_list()
        # compose and send alerts (if SMS switch on)
        ALERT.send_alerts(SMS=not ("NOSMS" in sys.argv))

    # perform basic maintenance
    if "MAINT" in sys.argv or "FULL" in sys.argv:
        MAINT = maintenance.Maintenance(LOG, MEMBERS, MONITOR)
        MAINT.housekeeping()
        # MAINT.soat_images()
        # MAINT.sunarp_images()


def main():
    global MONITOR, LOG
    MONITOR = monitor.Monitor()
    start_monitor()
    # activate logger and log start of program
    LOG = start_logger()
    LOG.info("-" * 15 + "Start Program" + "-" * 15)
    # start main program
    if "SIDE" in sys.argv:
        side()
    else:
        launcher()
    MONITOR.add_item("-" * 10 + " End Program " + "-" * 10)
    # MONITOR.end_monitor()
    # log end of program and quit
    LOG.info("^" * 16 + " End Program " + "^" * 16)


if __name__ == "__main__":
    main()
    # stop Streamlit server
    # os.kill(os.getpid(), signal.SIGINT)
