from datetime import datetime as dt
from gft_utils import pygameUtils
from updates import soat_gui_speech, soat_gui_typed, soat_image_generator
from utils import date_to_db_format, log_action_in_db
from scrapers import scrape_soat
from copy import deepcopy as copy


def gather(db_oonn, db_cursor, dash, update_data, gui_option="SPEECH"):

    CARD = 5

    # log first action
    dash.log(
        card=CARD,
        title=f"Certificados Soat [{len(update_data)}]",
        status=1,
        progress=0,
        text="Inicializando",
        lastUpdate="Actualizado:",
    )

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
                dash.log(card=CARD, text=f"Procesando: {placa}")

                # grab captcha image from website and save to temp file
                scraper.get_captcha()

                # send to manual captcha solving (typed or speech)
                if gui_option == "TYPED":
                    captcha = soat_gui_typed(canvas)
                elif gui_option == "SPEECH":
                    captcha = soat_gui_speech.get_captcha()

                # captcha timeout - manual user not there to enter captcha, skip process
                if captcha == -1:
                    dash.log(
                        card=CARD,
                        title="Certificados Soat",
                        status=0,
                        text="Timeout (usuario)",
                        lastUpdate=dt.now(),
                    )
                    return

                # with captcha manually resolved, proceed to scraping
                response_soat = scraper.browser(placa=placa, captcha_txt=captcha)

                # wrong captcha - restart loop with same placa
                if response_soat == -2:
                    continue

                # scraper exceed limit of manual captchas - abort iteration
                elif response_soat == -1:
                    dash.log(
                        card=CARD,
                        title="Certificados Soat",
                        status=0,
                        text="Detenido por limite Apeseg.",
                        lastUpdate=dt.now(),
                    )
                    return

                # if there is data in response, enter into database, go to next placa
                elif response_soat:

                    # adjust date to match db format (YYYY-MM-DD)
                    new_record_dates_fixed = date_to_db_format(
                        data=response_soat.values()
                    )

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

                # update dashboard with progress and last update timestamp
                dash.log(
                    card=CARD,
                    progress=int((counter / len(update_data)) * 100),
                    lastUpdate=dt.now(),
                )

                # no errors - update database and next member
                db_oonn.commit()
                break

            except KeyboardInterrupt:
                quit()

            except Exception:
                retry_attempts += 1
                dash.log(
                    card=CARD,
                    text=f"|ADVERTENCIA| Reintentando [{retry_attempts}/3]: {placa}",
                )

        # if code gets here, means scraping has encountred three consecutive errors, skip record
        dash.log(card=CARD, msg=f"|ERROR| No se pudo procesar {placa}.")

        # log last action
    dash.log(
        card=CARD,
        title="Certificados Soat",
        status=0,
        text="Inactivo",
        lastUpdate=dt.now(),
    )
