import sys
from pprint import pprint

# local imports
from monitor import monitor
from members import add_members, process_unsub
from members.db_utils import Database
from updates import get_records_to_update, gather_all
from messages import get_message_recipients, craft_messages, send_messages
import maintenance

import time

# TODO: display $review on web page
# TODO: expand brevetes to include CE
# TODO: one table with last update for every scrape


def launcher(dash, db):
    """Program entry point. Executes actions depending on arguments ran at prompt.
    Valid arguments: FULL, MEMBER, UPDATE, MAN, AUTO, ALL, ALERT, EMAIL, MAINT
    """

    # check for new members, unsub/resub requests and generate 30-day list
    if "MEMBER" in sys.argv or "FULL" in sys.argv:
        # add to monitor display
        monitor.log("Checking New Members...", type=0)
        # add new members from online form
        add_members.add(db.cursor, monitor)
        # process unsub/resub requests
        process_unsub.process(db.cursor, monitor)
        # save database changes
        db.conn.commit()

    # define records that require updating and perform updates (scraping)
    if "UPDATE" in sys.argv or "FULL" in sys.argv:
        # get members that will require alert to include in records that require update

        # required_alerts = ALERT.get_alert_list(db_cursor)

        # add to monitor display
        dash.log(action="Getting Records to Process...")
        # query db and find records that require updating
        all_updates = get_records_to_update.get_records(db.cursor)

        pprint(all_updates)
        print([f"{i}: {len(all_updates[i])}" for i in all_updates])

        # return

        # add to monitor display
        dash.log(action="Updating records...")
        # gather data for all record types

        gather_all.gather_threads(db.conn, db.cursor, dash, all_updates)
        # save database changes
        db.conn.commit()

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

        db_conn.commit()

    # define records that require alerts, craft messages and save them
    if "ALERT" in sys.argv or "FULL" in sys.argv:
        monitor.log("Creating alerts...", type=0)
        # get members that require alerting
        required_alerts = ALERT.get_alert_list(db_cursor)
        # compose alerts and write them to outbound folder
        messages.craft_alerts.craft_alerts(required_alerts, LOG, MONITOR)

        db_conn.commit()

    # perform basic maintenance
    if "MAINT" in sys.argv or "FULL" in sys.argv:
        MAINT = maintenance.Maintenance(LOG, MEMBERS, MONITOR)
        MAINT.housekeeping()
        MAINT.soat_images()
        # MAINT.sunarp_images()

        db_conn.commit()


def main():

    # begin monitoring in independent thread
    dash = monitor.Dashboard()
    dash.run_in_background()

    # log start of script
    # mon.log("-" * 15 + "Start Program" + "-" * 15, type="0B")

    # connect to database
    db = Database(dev=False)

    # start main program
    launcher(dash, db)

    # log end of program and quit
    # mon.log("-" * 15 + " End Program " + "-" * 15)


if __name__ == "__main__":
    main()
    time.sleep(10)


# idcoidog fk = 126 131 134
