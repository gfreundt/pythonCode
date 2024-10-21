import sys, os, time
import signal

import side
import monitoring
from members import init_db, add_members, process_unsub
from updates import get_records_to_update, gather_all
from messages import get_message_recipients, craft_messages, send_messages

# local imports
import maintenance

# TODO: display $review on web page


def launcher(monitor):
    """Program entry point. Executes actions depending on arguments ran at prompt.
    Valid arguments: FULL, MEMBER, UPDATE, MAN, AUTO, ALL, ALERT, EMAIL, MAINT"""

    # establish database connection
    db_conn, db_cursor = init_db.db(monitor)

    # check for new members, unsub/resub requests and generate 30-day list
    if "MEMBER" in sys.argv or "FULL" in sys.argv:
        # add to monitor display
        monitor.log("Checking New Members...", type=0)
        # add new members from online form
        add_members.add(db_cursor, monitor)
        # process unsub/resub requests
        process_unsub.process(db_cursor, monitor)
        # save database changes
        db_conn.commit()

    # define records that require updating and perform updates (scraping)
    if "UPDATE" in sys.argv or "FULL" in sys.argv:
        # get members that will require alert to include in records that require update

        # required_alerts = ALERT.get_alert_list(db_cursor)

        # add to monitor display
        monitor.log("Getting Records to Process...", type=1)
        # query db and find records that require updating
        all_updates = get_records_to_update.get_records(db_cursor)
        # add to monitor display
        monitor.log("Updating records...", type=1)
        # gather data for all record types
        gather_all.gather_threads(db_conn, db_cursor, monitor, all_updates)
        # save database changes
        db_conn.commit()

        return

    # craft and send messages and alerts to required destinations
    if "MSG" in sys.argv or "FULL" in sys.argv:
        monitor.log("Creating messages...", type=1)
        welcome_recipients, regular_recipients = get_message_recipients.recipients(
            db_cursor
        )
        # compose emails and write them to outbound folder
        craft_messages.craft(db_cursor, monitor, welcome_recipients, regular_recipients)
        send_messages.send(db_cursor, monitor)

    # define records that require alerts, craft messages and save them
    if "ALERT" in sys.argv or "FULL" in sys.argv:
        monitor.log("Creating alerts...", type=0)
        # get members that require alerting
        required_alerts = ALERT.get_alert_list(db_cursor)
        # compose alerts and write them to outbound folder
        messages.craft_alerts.craft_alerts(required_alerts, LOG, MONITOR)

    # perform basic maintenance
    if "MAINT" in sys.argv or "FULL" in sys.argv:
        MAINT = maintenance.Maintenance(LOG, MEMBERS, MONITOR)
        MAINT.housekeeping()
        MAINT.soat_images()
        # MAINT.sunarp_images()

    db_conn.commit()


def main():

    # instanciate and start monitoring / logging
    monitor = monitoring.Monitor()

    monitor.log("-" * 15 + "Start Program" + "-" * 15, type="0B")

    # start main program
    if "SIDE" in sys.argv:
        side.side(monitor)
    else:
        launcher(monitor)

    # log end of program and quit
    monitor.log("-" * 15 + " End Program " + "-" * 15)

    # stop Streamlit server
    time.sleep(3)
    os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    main()


# idcoidog fk = 126 131 134
