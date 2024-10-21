from datetime import datetime as dt
from utils import log_action_in_db
from scrapers import scrape_satimp
import logging
import easyocr


def gather(db_cursor, monitor, update_data):

    # remove easyocr warnings in logger and start reader
    logging.getLogger("easyocr").setLevel(logging.ERROR)
    ocr = easyocr.Reader(["es"], gpu=False)

    monitor.log("Updating Impuestos SAT...", type=1)

    # iterate on all records that require updating and get scraper results
    for counter, (id_member, doc_tipo, doc_num) in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(
                    f"[{counter}/{len(update_data)}] SATIMPS: {doc_tipo} {doc_num}",
                    type=1,
                )

                # send request to scraper
                new_records = scrape_satimp.browser(
                    ocr, doc_tipo=doc_tipo, doc_num=doc_num
                )

                # if no error in scrape, delete any prior satimp data of this member in both tables
                db_cursor.executescript(
                    f"""DELETE FROM satimpDeudas WHERE IdCodigo_FK =
                          (SELECT IdCodigo FROM satimpCodigos WHERE IdMember_FK = '{id_member}');
                        
                        DELETE FROM satimpCodigos WHERE IdMember_FK = '{id_member}'"""
                )

                for new_record in new_records:

                    # add foreign key and current date to scraper response
                    _values = [
                        id_member,
                        new_record["codigo"],
                        dt.now().strftime("%Y-%m-%d"),
                    ]

                    # insert gathered record of member
                    db_cursor.execute(
                        f"INSERT INTO satimpCodigos (IdMember_FK, Codigo, LastUpdate) VALUES {tuple(_values)}"
                    )

                    # get id created to use as foreign id in satimpDeudas table
                    _c = new_record["codigo"]
                    db_cursor.execute(
                        f"SELECT * FROM satimpCodigos WHERE Codigo = '{_c}'"
                    )
                    _id = db_cursor.fetchone()[0]

                    # loop through all deudas for new id created (if any)
                    for deuda in new_record["deudas"]:

                        # add new foreign key to response and add to database
                        _values = [_id] + list(deuda.values())
                        db_cursor.execute(
                            f"INSERT INTO satimpDeudas VALUES {tuple(_values)}"
                        )

                        # register action and log
                        log_action_in_db(
                            db_cursor, table_name="satimpDeudas", idMember=id_member
                        )

                # register action and go to next record
                log_action_in_db(
                    db_cursor, table_name="satimpCodigos", idMember=id_member
                )
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(f"< SATIMP > Retrying {doc_tipo}-{doc_num}.")

            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< SATIMP > Could not process {doc_tipo}-{doc_num}. Skipping Record.",
                error=True,
            )
