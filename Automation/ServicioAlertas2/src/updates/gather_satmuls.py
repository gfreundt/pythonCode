from datetime import datetime as dt
from utils import date_to_db_format, log_action_in_db
from scrapers import scrape_satmul


def gather(db_conn, db_cursor, monitor, update_data):

    monitor.log("Updating Multas SAT...", type=1)

    # iterate on every placa and write to database
    for counter, (id_placa, placa) in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(f"[{counter}/{len(update_data)}] SATMUL: {placa}", type=3)

                # send request to scraper
                response_satmul = scrape_satmul.browser(placa=placa)

                # if there is data in response, enter into database, go to next placa
                for response in response_satmul:

                    # adjust date to match db format (YYYY-MM-DD)
                    new_record_dates_fixed = date_to_db_format(data=response.values())
                    _values = (
                        [id_placa]
                        + new_record_dates_fixed
                        + [dt.now().strftime("%Y-%m-%d")]
                    )

                    # delete all old records from member
                    db_cursor.execute(
                        f"DELETE FROM satmuls WHERE IdPlaca_FK = '{id_placa}'"
                    )

                    # insert new record into database
                    db_cursor.execute(f"INSERT INTO satmuls VALUES {tuple(_values)}")

                # register action
                log_action_in_db(db_cursor, table_name="satmuls", idPlaca=id_placa)

                # no errors - update database and next member
                db_conn.commit()
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(f"< SATMUL > Retrying {placa}.", error=True, type=1)

        else:
            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< SATMUL > Could not process {placa}. Skipping Record.",
                error=True,
                type=1,
            )
