from datetime import datetime as dt
from utils import log_action_in_db
from scrapers import scrape_sunarp
import logging
import easyocr
from streamlit.runtime.scriptrunner import add_script_run_ctx


def gather(db_cursor, monitor, update_data, ctx=None):

    # start streamlit context manager if opened as thread
    if ctx:
        print("sunarps")
        add_script_run_ctx(ctx)

    # remove easyocr warnings in logger and start reader
    logging.getLogger("easyocr").setLevel(logging.ERROR)
    ocr = easyocr.Reader(["es"], gpu=False)

    monitor.log("Updating SUNARP...", type=1)

    # iterate on every placa and write to database
    for counter, (id_placa, placa) in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(f"[{counter}/{len(update_data)}] SUNARPS: {placa}", type=1)

                # send request to scraper
                response = scrape_sunarp.browser(placa=placa, ocr=ocr)

                # correct captcha, no data for placa - enter update attempt to review database, next placa
                if not response:
                    db_cursor.execute(
                        f"INSERT INTO '$review' (IdPlaca_FK, Reason) VALUES ({id_placa}, 'SUNARP')"
                    )
                    break

                # if there is data in response, enter into database, go to next placa
                _img_filename = f"SUNARP_{placa}.png"

                # add foreign key and current date to response
                _values = (
                    [id_placa]
                    + extract_data_from_image(_img_filename)
                    + [_img_filename, dt.now().strftime("%Y-%m-%d")]
                )

                # delete all old records from placa
                db_cursor.execute(
                    f"DELETE FROM sunarps WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa}')"
                )

                # insert new record into database
                db_cursor.execute(f"INSERT INTO sunarps VALUES {tuple(_values)}")

                # register action and skip to next record
                log_action_in_db(db_cursor, table_name="sunarps", idMember=id_placa)
                break

            except KeyboardInterrupt:
                quit()

            except:
                retry_attempts += 1
                monitor.log(f"< SATIMP > Retrying {placa}.")

        else:
            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< SUNARP > Could not process {placa}. Skipping Record.",
                error=True,
            )


def extract_data_from_image(img_filename):
    return [""] * 14
