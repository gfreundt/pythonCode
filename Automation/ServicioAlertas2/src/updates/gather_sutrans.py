from datetime import datetime as dt
from utils import date_to_db_format, log_action_in_db
from scrapers import scrape_sutran
from streamlit.runtime.scriptrunner import add_script_run_ctx


def gather(db_cursor, monitor, update_data):

    # log action
    monitor.log("Updating SUTRAN...", type=1)

    # iterate on all records that require updating and get scraper results
    for counter, (id_placa, placa) in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(f"[{counter}/{len(update_data)}] SUTRANS: {placa}", type=1)

                # send request to scraper
                sutran_response = scrape_sutran.browser(placa=placa)

                _now = dt.now().strftime("%Y-%m-%d")

                # if no error in scrape, erase any prior records of this placa
                db_cursor.execute(
                    f"DELETE FROM sutrans WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa}')"
                )

                # update placas table with last update information
                db_cursor.execute(
                    f"UPDATE placas SET LastUpdateSUTRAN = '{_now}' WHERE Placa = '{placa}'"
                )

                # register action
                log_action_in_db(db_cursor, table_name="sutrans", idPlaca=id_placa)

                # if response is blank, skip to next placa
                if not sutran_response:
                    break

                # iterate on all multas
                for response in sutran_response:
                    new_record_dates_fixed = date_to_db_format(data=response.values())
                    _values = [id_placa] + new_record_dates_fixed + [_now]

                    # insert gathered record of member
                    db_cursor.execute(f"INSERT INTO sutrans VALUES {tuple(_values)}")

                # no errors - next placa
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(f"< SUTRAN > Retrying {placa}.", type=1, error=True)
                break

            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< SUTRAN > Could not process {placa}. Skipping Record.",
                type=1,
                error=True,
            )
