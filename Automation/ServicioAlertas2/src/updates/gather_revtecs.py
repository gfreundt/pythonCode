from datetime import datetime as dt
from utils import date_to_db_format, log_action_in_db
from scrapers import scrape_revtec
import logging
import easyocr


def gather(db_cursor, monitor, update_data):

    # remove easyocr warnings in logger and start reader
    logging.getLogger("easyocr").setLevel(logging.ERROR)
    ocr = easyocr.Reader(["es"], gpu=False)

    monitor.log("Updating Revisón Tecnica...", type=1)

    # iterate on all records that require updating and get scraper results
    for counter, (id_placa, placa) in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(f"[{counter}/{len(update_data)}] REVTEC: {placa}", type=4)

                # send request to scraper
                revtec_response = scrape_revtec.browser(ocr=ocr, placa=placa)

                # stop processing if blank response from scraper
                if not revtec_response:
                    break

                # adjust date to match db format (YYYY-MM-DD)
                new_record_dates_fixed = date_to_db_format(
                    data=revtec_response.values()
                )

                # add foreign key and current date to scraper response
                _values = (
                    [id_placa]
                    + new_record_dates_fixed
                    + [dt.now().strftime("%Y-%m-%d")]
                )

                # delete all old records from member
                db_cursor.execute(
                    f"DELETE FROM revtecs WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa}')"
                )

                # insert new record into database
                db_cursor.execute(f"INSERT INTO revtecs VALUES {tuple(_values)}")

                # register action and skip to next record
                log_action_in_db(db_cursor, table_name="revtec", idPlaca=id_placa)
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(f"< REVTEC > Retrying Record {placa}.", type=3, error=True)

            # if code gets here, means scraping has encountred three consecutive errors, skip placa
            monitor.log(
                f"< REVTEC > Could not process {placa}. Skipping Record.",
                type=3,
                error=True,
            )
