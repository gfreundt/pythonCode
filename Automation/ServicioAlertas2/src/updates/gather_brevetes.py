from datetime import datetime as dt
from utils import date_to_db_format, log_action_in_db
from scrapers import scrape_brevete
import logging
import easyocr


def gather(db_cursor, monitor, update_data):

    # remove easyocr warnings in logger and start reader
    logging.getLogger("easyocr").setLevel(logging.ERROR)
    ocr = easyocr.Reader(["es"], gpu=False)

    monitor.log("Updating Brevetes...", type=1)

    # iterate on all records that require updating and get scraper results
    for id_member, doc_tipo, doc_num in update_data:

        # skip member if doc tipo is not DNI (CE mostly)
        if doc_tipo != "DNI":
            monitor.log(f"BREVETE (Skip - not DNI): {doc_tipo}-{doc_num}", type=3)
            continue

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # send request to scraper
                brevete_response, pimpagas_response = scrape_brevete.browser(
                    doc_num=doc_num, ocr=ocr
                )

                # stop processing if blank response from scraper
                if not brevete_response:
                    return

                # adjust date to match db format (YYYY-MM-DD)
                new_record_dates_fixed = date_to_db_format(
                    data=brevete_response.values()
                )

                # add foreign key and current date to scraper response
                _values = (
                    [id_member]
                    + new_record_dates_fixed
                    + [dt.now().strftime("%Y-%m-%d")]
                )

                # delete all old records from member
                db_cursor.execute(
                    f"DELETE FROM brevetes WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}' AND DocNum = '{doc_num}')"
                )

                # insert new record into database
                db_cursor.execute(f"INSERT INTO brevetes VALUES {tuple(_values)}")

                # log action
                monitor.log(f"BREVETE: {doc_tipo}-{doc_num}", type=4)

                # process list of papeletas impagas and put them in different table
                for papeleta in pimpagas_response:

                    # adjust date to match db format (YYYY-MM-DD)
                    papeleta_dates_fixed = date_to_db_format(
                        data=papeleta.values(), sep="/"
                    )

                    # add foreign key and current date to response
                    _values = (
                        [id_member]
                        + papeleta_dates_fixed
                        + [dt.now().strftime("%Y-%m-%d")]
                    )

                    # delete all old records from member
                    db_cursor.execute(
                        f"DELETE FROM mtcPapeletas WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}' AND DocNum = '{doc_num}')"
                    )

                    # insert record into database
                    db_cursor.execute(
                        f"INSERT INTO mtcPapeletas VALUES {tuple(_values)}"
                    )

                # register action and skip to next record
                log_action_in_db(db_cursor, table_name="brevetes", idMember=id_member)
                log_action_in_db(
                    db_cursor, table_name="mtcPapeletas", idMember=id_member
                )

                # no errors - next member
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(
                    f"< BREVETE > Retrying Record {doc_tipo}-{doc_num}. ",
                    type=3,
                    error=True,
                )

        else:
            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< BREVETES > Could not process {doc_tipo}-{doc_num}. Skipping Record.",
                type=3,
                error=True,
            )
