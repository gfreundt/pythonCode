from datetime import datetime as dt
from gft_utils import pygameUtils
from updates import soat_gui_speech, soat_gui_typed, soat_image_generator
from utils import date_to_db_format, log_action_in_db
from scrapers import scrape_soat
from copy import deepcopy as copy


def gather(db_oonn, db_cursor, monitor, update_data, gui_option="SPEECH"):

    monitor.log("Updating SOATS...", type=1)

    # if gui option is typed, initiate canvas
    if gui_option == "TYPED":
        canvas = pygameUtils(screen_size=(1050, 130))

    scraper = scrape_soat.Soat()
    # iterate on every placa and write to database
    for counter, (id_placa, placa) in enumerate(update_data, start=1):

        retry_attempts = 0
        # loop to catch scraper errors and retry limited times
        while retry_attempts < 3:
            try:
                # log action
                monitor.log(f"[{counter}/{len(update_data)}] SOAT: {placa}", type=3)

                # grab captcha image from website and save to temp file
                scraper.get_captcha()

                # send to manual captcha solving (typed or speech)
                if gui_option == "TYPED":
                    captcha = soat_gui_typed(canvas)
                elif gui_option == "SPEECH":
                    captcha = soat_gui_speech.get_captcha()

                response_soat = scraper.browser(placa=placa, captcha_txt=captcha)
                # wrong captcha - restart loop with same placa
                if response_soat == -2:
                    continue
                # scraper exceed limit of manual captchas - abort iteration
                elif response_soat == -1:
                    monitor.log(
                        f"< SOAT > Reached APESEG limit ({dt.now()}). Aborting operation.",
                        error=True,
                        type=1,
                    )
                    return
                # if there is data in response, enter into database, go to next placa
                elif response_soat:

                    # adjust date to match db format (YYYY-MM-DD)
                    new_record_dates_fixed = date_to_db_format(
                        data=response_soat.values()
                    )
                    print("what the func", new_record_dates_fixed)

                    # if soat data gathered succesfully, generate soat image and save in folder
                    img_name = soat_image_generator.generate(
                        db_cursor, id_placa=None, data=copy(new_record_dates_fixed)
                    )

                    _now = dt.now().strftime("%Y-%m-%d")

                    # insert data into table
                    _values = (
                        [id_placa] + list(new_record_dates_fixed) + [img_name] + [_now]
                    )

                    print("outside func", _values)
                    # delete all old records from member
                    db_cursor.execute(
                        f"DELETE FROM soats WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa}')"
                    )

                    # insert gathered record of member
                    db_cursor.execute(f"INSERT INTO soats VALUES {tuple(_values)}")

                    # update placas table with last update information
                    db_cursor.execute(
                        f"UPDATE placas SET LastUpdateSOAT = '{_now}' WHERE Placa = '{placa}'"
                    )

                # register action and skip to next record
                log_action_in_db(db_cursor, table_name="soats", idPlaca=id_placa)

                # no errors - update database and next member
                db_oonn.commit()
                break

            except KeyboardInterrupt:
                quit()

            except Exception:
                retry_attempts += 1
                monitor.log(f"< SOAT > Retrying {placa}.", error=True, type=1)

        else:
            # if code gets here, means scraping has encountred three consecutive errors, skip record
            monitor.log(
                f"< SOAT > Could not process {placa}. Skipping Record.",
                error=True,
                type=1,
            )
