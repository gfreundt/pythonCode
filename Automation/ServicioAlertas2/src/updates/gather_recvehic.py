from datetime import datetime as dt
from scrapers import scrape_recvehic
from utils import log_action_in_db
import logging
import easyocr

# remove easyocr warnings in logger
logging.getLogger("easyocr").setLevel(logging.ERROR)


def gather(db_cursor, monitor, update_data):

    # remove easyocr warnings in logger and start reader
    logging.getLogger("easyocr").setLevel(logging.ERROR)
    ocr = easyocr.Reader(["es"], gpu=False)

    monitor.log("Updating Record del Conductor...", type=1)

    # iterate on all records that require updating and get scraper results
    for counter, (id_member, doc_tipo, doc_num) in enumerate(update_data, start=1):

        # records are only available for members with DNI
        if doc_tipo != "DNI":
            monitor.log(
                f"[{counter}/{len(update_data)}] RECORD: {doc_tipo} {doc_num} (Skipping Not DNI)",
                type=3,
            )
            continue

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(
                    f"[{counter}/{len(update_data)}] RECORD: {doc_tipo} {doc_num}",
                    type=4,
                )

                # send request to scraper
                _img_filename = scrape_recvehic.browser(
                    doc_num=doc_num, ocr=ocr, monitor=monitor
                )

                # register action
                log_action_in_db(db_cursor, table_name="revtec", idMember=id_member)

                # update memberLastUpdate table with last update information
                _now = dt.now().strftime("%Y-%m-%d")
                db_cursor.execute(
                    f"UPDATE membersLastUpdate SET LastUpdateRecord = '{_now}' WHERE IdMember_FK = '{id_member}'"
                )

                # stop processing if blank response from scraper
                if not _img_filename:
                    break

                # add foreign key and current date to response
                _values = (id_member, _img_filename, _now)

                # delete all old records from member
                db_cursor.execute(
                    f"""    DELETE FROM recordConductores WHERE IdMember_FK =
                            (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}'
                                AND DocNum = '{doc_num}')"""
                )

                # insert record into database
                db_cursor.execute(f"INSERT INTO recordConductores VALUES {_values}")

                # no errors - next member
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(f"< RECORD > Retrying {doc_tipo}-{doc_num}.", type=3)

        else:
            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< RECORD > Could not process {doc_tipo}-{doc_num}. Skipping Record.",
                error=True,
            )
