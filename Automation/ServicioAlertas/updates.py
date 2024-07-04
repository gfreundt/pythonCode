import io
from copy import deepcopy as copy
import threading
from datetime import datetime as dt
import time
import pygame
from pygame.locals import *
from tqdm import tqdm

# local imports
import scrapers, sunarp
from gft_utils import pygameUtils


def threader(func):
    """Decorator function that includes function in thread."""

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class Gui:
    """Manages PyGame window that captures manual captcha."""

    def __init__(self, zoomto, numchar) -> None:
        self.zoomto = zoomto
        self.numchar = numchar
        self.numpad = (
            K_KP0,
            K_KP1,
            K_KP2,
            K_KP3,
            K_KP4,
            K_KP5,
            K_KP6,
            K_KP7,
            K_KP8,
            K_KP9,
        )

    def gui(self, canvas, captcha_img):
        TEXTBOX = pygame.Surface((80, 120))
        UPPER_LEFT = (10, 10)
        image = pygame.image.load(io.BytesIO(captcha_img)).convert()
        image = pygame.transform.scale(image, self.zoomto)
        canvas.MAIN_SURFACE.fill(canvas.COLORS["BLACK"])
        canvas.MAIN_SURFACE.blit(image, UPPER_LEFT)

        chars, col = [], 0
        while True:
            # pygame capture screen update
            charsx = f"{''.join(chars):<6}"
            for colx in range(6):
                text = canvas.FONTS["NUN80B"].render(
                    charsx[colx],
                    True,
                    canvas.COLORS["BLACK"],
                    canvas.COLORS["WHITE"],
                )
                TEXTBOX.fill(canvas.COLORS["WHITE"])
                TEXTBOX.blit(text, (12, 5))
                canvas.MAIN_SURFACE.blit(
                    TEXTBOX,
                    (
                        colx * 90 + UPPER_LEFT[0] + 20 + 500,
                        UPPER_LEFT[1],
                    ),
                )
            pygame.display.flip()

            # capture keystrokes and add to manual captcha input
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT or (event.type == KEYDOWN and event.key == 27):
                    quit()
                elif event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        if col == 0:
                            continue
                        chars = chars[:-1]
                        col -= 1
                    elif event.key in (K_SPACE, K_RETURN):
                        continue
                    elif event.key in self.numpad:
                        chars.append(str(self.numpad.index(event.key)))
                        col += 1
                    else:
                        try:
                            chars.append(chr(event.key))
                            col += 1
                        except Exception:
                            pass

            # if all chars are complete, return manual captcha as string
            if col == self.numchar:
                canvas.MAIN_SURFACE.fill(canvas.COLORS["GREEN"])
                pygame.display.flip()
                return "".join(chars)


class Update:

    def __init__(self, LOG, members) -> None:
        self.LOG = LOG
        self.cursor = members.cursor
        self.conn = members.conn
        self.sql = members.sql
        self.day30_list = members.day30_list
        self.lock = threading.Lock()

    def get_records_to_process(self):
        # create dictionary with all tables as keys and empty list as value
        self.cursor.execute("SELECT * FROM '@tableInfo'")
        self.all_updates = {i[1]: [] for i in self.cursor.fetchall()}

        # 1. add members that haven't received an email in 30+ days
        # docs
        cmd = [
            """SELECT IdMember, DocTipo, DocNum FROM members JOIN (
	            SELECT IdMember AS x FROM members
                EXCEPT
	            SELECT IdMember_FK FROM mensajes
		            JOIN mensajeContenidos
		            ON IdMensaje = IdMensaje_FK
		            WHERE fecha >= datetime('now','localtime', '-1 month')
			        AND (IdTipoMensaje_FK = 12 OR IdTipoMensaje_FK = 13)
	            )
                ON members.IdMember = x
                """
        ]

        # placas
        cmd.append(
            """SELECT IdPlaca, Placa FROM placas JOIN (
	            SELECT IdMember AS x FROM members 
                EXCEPT
	            SELECT IdMember_FK FROM mensajes
                    JOIN mensajeContenidos
		            ON IdMensaje = IdMensaje_FK
		            WHERE fecha >= datetime('now','localtime', '-1 month')
			        AND (IdTipoMensaje_FK = 12 OR IdTipoMensaje_FK = 13)
	            )
                ON placas.IdMember_FK = x
                """
        )

        # add same records to each scraper according to docs or placas
        for i in range(2):
            self.cursor.execute(cmd[i])
            _result = self.cursor.fetchall()
            self.cursor.execute(
                f"SELECT * FROM '@tableInfo' WHERE dataRequired = {i+1}"
            )
            self.all_updates.update(
                {i[1]: copy(_result) for i in self.cursor.fetchall()}
            )

        # TODO: create logic to avoid updating brevete, revtec not expiring within 30 days
        # filter soat from updating if not blank, expired or expiring within 30 days
        # _filter = [i[0] for i in self.day30_list if i[5] == "BREVETE"]
        # self.all_updates["brevetes"] = [
        #     i for i in self.all_updates["brevetes"] if i[0] in _filter
        # ]

        # _filter = [i[3] for i in self.day30_list if i[5] == "REVTEC"]
        # self.all_updates["revtecs"] = [
        #     i for i in self.all_updates["revtecs"] if i[1] in _filter
        # ]

        _filter = [i[1] for i in self.day30_list if i[3] == "SOAT"]
        self.all_updates["soats"] = [
            i for i in self.all_updates["soats"] if i[1] in _filter
        ]

        # select all sunarps that do not have a record yet
        self.cursor.execute(
            "SELECT IdPlaca, Placa FROM placas WHERE idPlaca NOT IN (SELECT IdPlaca_FK FROM sunarps)"
        )
        self.all_updates["sunarps"] = self.cursor.fetchall()

        # 2. add records that have no BIENVENIDA email
        # docs
        cmd = [
            """SELECT IdMember, DocTipo, DocNum FROM members
                EXCEPT
                SELECT IdMember, DocTipo, DocNum FROM (
                SELECT mensajes.IdMember_FK FROM mensajes JOIN mensajeContenidos ON mensajes.IdMensaje = mensajeContenidos.IdMensaje_FK
                WHERE IdTipoMensaje_FK = 12)
                JOIN members
                ON members.IdMember = IdMember_FK
                """
        ]

        # placas
        cmd.append(
            """SELECT IdPlaca, Placa FROM placas
                JOIN (SELECT IdMember, DocTipo, DocNum FROM members
                EXCEPT
                SELECT IdMember, DocTipo, DocNum FROM (
                SELECT mensajes.IdMember_FK FROM mensajes JOIN mensajeContenidos ON mensajes.IdMensaje = mensajeContenidos.IdMensaje_FK
                WHERE IdTipoMensaje_FK = 12)
                JOIN members
                ON members.IdMember = IdMember_FK)
                ON placas.IdMember_FK = IdMember
                """
        )

        # add same records to each scraper according to docs or placas
        for i in range(2):
            self.cursor.execute(cmd[i])
            _result = self.cursor.fetchall()
            self.cursor.execute(
                f"SELECT * FROM '@tableInfo' WHERE dataRequired = {i+1}"
            )
            for table in self.cursor.fetchall():
                self.all_updates[table[1]] += _result

        # eliminate duplicates
        self.all_updates = {i: set(j) for i, j in self.all_updates.items()}

        return

        # TODO: updates for alerts
        # 3. add records that will be in alert (expiration) and met time from last update (non-expiration)
        # docs
        self.cursor.execute(f"SELECT * FROM tableInfo WHERE DataRequired = 1")
        tables = self.cursor.fetchall()
        for table in tables:
            # non-expiration update
            if table[7]:
                cmd = f""" SELECT IdMember, DocTipo, DocNum FROM members JOIN (
                           SELECT IdMember AS x FROM members EXCEPT
                           SELECT IdMember_FK FROM actions WHERE Scraper = "{table[1]}" AND DATE('now', '{table[7]} days') <= Timestamp)
						   ON members.IdMember = x"""
            # expiration updates
            else:
                txt = ""
                for expiration in table[4:7]:
                    txt += f"OR DATE('now', '{expiration} days') = FechaHasta "
                cmd = f"""SELECT IdMember, DocTipo, DocNum FROM members JOIN 
                (SELECT IdMember_FK FROM {table[1]} WHERE FALSE {txt}) ON IdMember = IdMember_FK"""

            self.cursor.execute(cmd)
            self.all_updates[table[1]] += [i for i in self.cursor.fetchall()]

        # placas
        self.cursor.execute(f"SELECT * FROM tableInfo WHERE DataRequired = 2")
        tables = self.cursor.fetchall()
        for table in tables:
            # non-expiration update
            if table[7]:
                cmd = f"""SELECT IdPlaca, Placa FROM placas JOIN (
                            SELECT IdPlaca AS x FROM placas EXCEPT
                            SELECT IdPlaca_FK FROM actions WHERE Scraper = "{table[1]}" AND DATE('now', '{table[7]} days') <= Timestamp
                            ) ON placas.IdPlaca = x"""

            # expiration updates
            else:
                txt = ""
                for expiration in table[4:7]:
                    txt += f"OR DATE('now', '{expiration} days') = FechaHasta "
                cmd = f"""SELECT IdPlaca, Placa FROM placas JOIN
                (SELECT IdPlaca_FK FROM {table[1]} WHERE FALSE {txt}) ON IdPlaca = IdPlaca_FK"""

            self.cursor.execute(cmd)
            self.all_updates[table[1]] += [i for i in self.cursor.fetchall()]

    def log_action(self, scraper, idMember=None, idPlaca=None):
        """Registers scraping action in actions table in database."""
        cmd = self.sql("actions", ["Scraper", "IdMember_FK", "IdPlaca_FK", "Timestamp"])
        self.cursor.execute(
            cmd, [scraper, idMember, idPlaca, dt.now().strftime("%Y-%m-%d %H:%M:%S")]
        )
        self.conn.commit()

    def get_fields(self, table):
        """Returns all the fields in a table, ordered by creation."""
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        return [i[0] for i in self.cursor.fetchall()[1:]]

    def fix_date_format(self, data, sep=None):
        """Takes dd.mm.yyyy date formats with any separator and returns yyyy-mm-dd."""
        # TODO: check if list is necessary (update.py sends list at any point?)
        if not sep:
            return data
        new_record_dates_fixed = []
        for r in data:
            try:
                new_record_dates_fixed.append(
                    dt.strftime(dt.strptime(r, f"%d{sep}%m{sep}%Y"), "%Y-%m-%d")
                )
            except:
                new_record_dates_fixed.append(r)
        return new_record_dates_fixed

    def gather_soat(self, scraper, table, date_sep):
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields = self.get_fields(table)
        # set up scraper for image
        scraper2 = scrapers.SoatImage()
        # get captcha manually from user
        canvas = pygameUtils(screen_size=(1050, 130))
        GUI = Gui(zoomto=(465, 105), numchar=6)
        # iterate on every placa and write to database
        for placa in self.all_updates["soats"]:
            retry_attempts = 0
            while True:
                try:
                    plac = placa[1]
                    captcha_img = scraper.get_captcha_img()
                    captcha = GUI.gui(canvas, captcha_img)
                    response = scraper.browser(placa=plac, captcha_txt=captcha)
                    # wrong captcha - restart loop with same placa
                    if response == -2:
                        continue
                    # scraper exceed limit of manual captchas - abort iteration
                    elif response == -1:
                        return
                    # if there is data in response, enter into database, go to next placa
                    elif response:
                        # convert dates to yyyy-mm-dd format
                        new_record_dates_fixed = self.fix_date_format(
                            data=response.values(), sep=date_sep
                        )
                        # if soat data gathered succesfully, try to get soat image too
                        try:
                            img_name = scraper2.browser(placa=plac)
                        except:
                            img_name = ""
                        # insert data into table
                        cmd = self.sql(table, fields)
                        values = (
                            [placa[0]]
                            + list(new_record_dates_fixed)
                            + [img_name]
                            + [dt.now().strftime("%Y-%m-%d")]
                        )
                        # delete all old records from member
                        self.cursor.execute(
                            f"DELETE FROM {table} WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{plac}')"
                        )
                        # insert gathered record of member
                        self.cursor.execute(cmd, values)
                        self.conn.commit()
                    # log action into actios table
                    self.log_action(scraper="soats", idPlaca=placa[0])
                    break  # escape while True loop
                except KeyboardInterrupt:
                    quit()
                except Exception:
                    # try same place up to 3 times
                    retry_attempts += 1
                    if retry_attempts > 3:
                        self.LOG.warning(
                            f"< {table.upper()} > Could not process {placa}. Skipping Record."
                        )
                        break
                    else:
                        self.LOG.warning(f"< {table.upper()} > Retrying {placa}.")
                        continue

    @threader
    def gather_sunarp(self, scraper, table):
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields = self.get_fields(table)
        # iterate on every placa and write to database
        for placa in self.all_updates[table]:
            retry_attempts = 0
            try:
                while True:
                    response, img_object = scraper.browser(placa=placa[1])
                    # wrong captcha or correct catpcha, no image loaded - restart loop with same placa
                    if response == -1:
                        continue
                    # correct captcha, no data for placa - enter update attempt to database, go to next placa
                    elif response == 1:
                        self.cursor.execute(
                            f"INSERT INTO '$review' (IdPlaca_FK, Reason) VALUES ({placa[0]}, 'SUNARP')"
                        )
                        self.conn.commit()
                        break
                    # if there is data in response, enter into database, go to next placa
                    elif img_object:
                        # process image and save to disk, update database with file information
                        # add image filename and image date to record
                        _img_filename = f"SUNARP_{placa[1]}.png"
                        sunarp.process_image(img_object, _img_filename)
                        fields = ["IdPlaca_FK", "ImgFilename", "LastUpdate"]
                        values = [
                            placa[0],
                            _img_filename,
                            dt.now().strftime("%Y-%m-%d"),
                        ]
                        # add ocr results to record
                        # ocr_result = sunarp.ocr_and_parse(_img_filename)
                        # if ocr_result:
                        #     fields += [
                        #         "IdPlaca_FK",
                        #         "PlacaValidate",
                        #         "Serie",
                        #         "VIN",
                        #         "Motor",
                        #         "Color",
                        #         "Marca",
                        #         "Modelo",
                        #         "PlacaVigente",
                        #         "PlacaAnterior",
                        #         "Estado",
                        #         "Anotaciones",
                        #         "Sede",
                        #         "Propietarios",
                        #         "Ano",
                        #     ]
                        #     values += [placa[0]] + ocr_result

                        # delete all old records from placa
                        self.cursor.execute(
                            f"DELETE FROM {table} WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa[1]}')"
                        )
                        # insert gathered record of placa
                        cmd = self.sql(table, fields)
                        self.cursor.execute(cmd, values)
                        self.log_action(scraper=table, idPlaca=placa[0])
                        self.conn.commit()
                        break
            except KeyboardInterrupt:
                quit()
            except:
                retry_attempts += 1
                if retry_attempts > 3:
                    self.LOG.warning(
                        f"< {table.upper()} > Could not process {placa}. Skipping Record."
                    )
                    break
                else:
                    self.LOG.warning(f"< {table.upper()} > Retrying {placa}.")
                    continue

    def gather_satmul(self, scraper, table, date_sep):
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields = self.get_fields(table)
        # iterate on every placa and write to database
        for placa in self.all_updates[table]:
            retry_attempts = 0
            while True:
                try:
                    plac = placa[1]
                    responses = scraper.browser(placa=plac)
                    # if there is data in response, enter into database, go to next placa
                    if responses:
                        for response in responses:
                            # convert dates to SQL format
                            new_record_dates_fixed = self.fix_date_format(
                                data=response.values(), sep=date_sep
                            )
                            cmd = self.sql(table, fields)
                            values = (
                                [placa[0]]
                                + new_record_dates_fixed
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            # delete all old records from member
                            self.cursor.execute(
                                f"DELETE FROM {table} WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{plac}')"
                            )
                            # insert gathered record of member
                            self.cursor.execute(cmd, values)
                        self.conn.commit()

                    self.log_action(scraper=table, idPlaca=placa[0])

                    break
                except KeyboardInterrupt:
                    quit()
                except:
                    retry_attempts += 1
                    if retry_attempts > 3:
                        self.LOG.warning(
                            f"< {table.upper()} > Could not process {placa}. Skipping Record."
                        )
                        break
                    else:
                        self.LOG.warning(f"< {table.upper()} > Retrying {placa}.")
                        continue

    @threader
    def gather_record(self, scraper):
        table = "recordConductores"
        fields = ["IdMember_FK", "ImgFilename", "LastUpdate"]
        for doc in self.all_updates["records"]:
            _img_filename = scraper.browser(doc_num=doc[2])
            if _img_filename:
                values = [doc[0], _img_filename, dt.now().strftime("%Y-%m-%d")]
                # delete all old records from member
                self.cursor.execute(
                    f"DELETE FROM {table} WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc[1]}' AND DocNum = '{doc[2]}')"
                )
                # update database
                cmd = self.sql(table, fields)
                self.cursor.execute(cmd, values)
                self.log_action(scraper=table, idMember=doc[0])
                self.conn.commit()

    @threader
    def gather_osiptel(self):
        # TODO
        return

    @threader
    def gather_satimp(self, scraper, table):
        table1 = table
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields1 = self.get_fields(table1)
        table2 = "satimpDeudas"
        fields2 = self.get_fields(table2)

        # iterate on all records that require updating and get scraper results
        for k, rec in tqdm(enumerate(self.all_updates[table1])):
            retry_attempts = 0
            while True:
                try:
                    doc_tipo, doc_num = rec[1], rec[2]
                    new_record = scraper.browser(doc_tipo=doc_tipo, doc_num=doc_num)
                    # delete old records of member
                    self.cursor.execute(
                        f"DELETE FROM {table} WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}' AND DocNum = '{doc_num}')"
                    )
                    for nrec in new_record:
                        cmd = self.sql(table1, fields1)
                        values = [rec[0], nrec["codigo"], dt.now().strftime("%Y-%m-%d")]

                        # insert gathered record of member
                        self.cursor.execute(cmd, values)

                        # get id created
                        _c = nrec["codigo"]
                        self.cursor.execute(
                            f"SELECT * FROM {table1} WHERE Codigo = '{_c}'"
                        )
                        id = self.cursor.fetchone()[0]
                        # insert deudas for new id created (if any)
                        for deuda in nrec["deudas"]:
                            cmd = self.sql(table2, fields2)
                            values = [id] + list(deuda.values())
                            self.cursor.execute(
                                f"DELETE FROM {table2} WHERE IdCodigo_FK = '{id}'"
                            )
                            # insert gathered record of member
                            self.cursor.execute(cmd, values)
                            self.log_action(scraper=table2, idMember=rec[0])

                    self.conn.commit()
                    # register action and skip to next record
                    self.log_action(scraper=table1, idMember=rec[0])
                    break
                except KeyboardInterrupt:
                    quit()
                except:
                    retry_attempts += 1
                    if retry_attempts > 3:
                        self.LOG.warning(
                            f"< {table1.upper()} > Could not process {rec}. Skipping Record."
                        )
                        break
                    else:
                        self.LOG.warning(f"< {table1.upper()} > Retrying {rec}.")

    @threader
    def gather_brevete(self, scraper, table, date_sep=None):
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields1 = self.get_fields(table)
        fields2 = self.get_fields("mtcPapeletas")

        # iterate on all records that require updating and get scraper results
        for rec in tqdm(self.all_updates[table]):
            retry_attempts = 0
            while True:
                try:
                    doc_tipo, doc_num = rec[1], rec[2]
                    new_record = scraper.browser(doc_tipo=doc_tipo, doc_num=doc_num)
                    if new_record:
                        if type(new_record) is not list:
                            new_record = [new_record]
                        # loop on all responses given by scraper
                        for record in new_record:
                            # adjust date format for SQL (YYYY-MM-DD)
                            new_record_dates_fixed = self.fix_date_format(
                                data=record.values(), sep=date_sep
                            )
                            cmd = self.sql(table, fields1)
                            values = (
                                [rec[0]]
                                + new_record_dates_fixed[:-1]
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            # delete all old records from member
                            self.cursor.execute(
                                f"DELETE FROM {table} WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}' AND DocNum = '{doc_num}')"
                            )
                            # insert gathered record of member
                            self.cursor.execute(cmd, values)
                            self.conn.commit()

                    for papeleta in new_record_dates_fixed[-1]:
                        # adjust date format for SQL (YYYY-MM-DD)
                        papeleta_dates_fixed = self.fix_date_format(
                            data=papeleta.values(), sep=date_sep
                        )
                        cmd = self.sql("mtcPapeletas", fields2)
                        values = (
                            [rec[0]]
                            + papeleta_dates_fixed
                            + [dt.now().strftime("%Y-%m-%d")]
                        )
                        # delete all old records from member
                        self.cursor.execute(
                            f"DELETE FROM mtcPapeletas WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}' AND DocNum = '{doc_num}')"
                        )
                        # insert gathered record of member
                        self.cursor.execute(cmd, values)
                        self.conn.commit()

                    # register action and skip to next record
                    self.log_action(scraper=table, idMember=rec[0])
                    break
                except KeyboardInterrupt:
                    quit()
                except:
                    retry_attempts += 1
                    if retry_attempts > 3:
                        self.LOG.warning(
                            f"< {table.upper()} > Could not process {rec}. Skipping Record."
                        )
                        break
                    else:
                        self.LOG.warning(f"< {table.upper()} > Retrying {rec}.")

    @threader
    def gather_docs(self, scraper, table, date_sep=None):
        # get field list from table, do not consider fist one (ID Autogenerated)
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        fields = [i[0] for i in self.cursor.fetchall()[1:]]

        # iterate on all records that require updating and get scraper results
        for rec in tqdm(self.all_updates[table]):
            retry_attempts = 0
            while True:
                try:
                    doc_tipo, doc_num = rec[1], rec[2]
                    new_record = scraper.browser(doc_tipo=doc_tipo, doc_num=doc_num)
                    if new_record:
                        if type(new_record) is not list:
                            new_record = [new_record]
                        # loop on all responses given by scraper
                        for record in new_record:
                            # adjust date format for SQL (YYYY-MM-DD)
                            new_record_dates_fixed = self.fix_date_format(
                                data=record.values(), sep=date_sep
                            )
                            cmd = self.sql(table, fields)
                            values = (
                                [rec[0]]
                                + new_record_dates_fixed
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            # delete all old records from member
                            self.cursor.execute(
                                f"DELETE FROM {table} WHERE IdMember_FK = (SELECT IdMember FROM members WHERE DocTipo = '{doc_tipo}' AND DocNum = '{doc_num}')"
                            )
                            # insert gathered record of member
                            self.cursor.execute(cmd, values)
                            self.conn.commit()
                    # register action and skip to next record
                    self.log_action(scraper=table, idMember=rec[0])
                    break
                except KeyboardInterrupt:
                    quit()
                except:
                    retry_attempts += 1
                    if retry_attempts > 3:
                        self.LOG.warning(
                            f"< {table.upper()} > Could not process {rec}. Skipping Record."
                        )
                        break
                    else:
                        self.LOG.warning(f"< {table.upper()} > Retrying {rec}.")

    @threader
    def gather_placa(self, scraper, table, date_sep=None):

        # get field list from table, do not consider fist one (ID Autogenerated)
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        fields = [i[0] for i in self.cursor.fetchall()[1:]]

        # iterate on all records that require updating and get scraper results
        for k, rec in tqdm(enumerate(self.all_updates[table])):
            retry_attempts = 0
            while True:
                try:
                    placa = rec[1]
                    new_record = scraper.browser(placa=placa)
                    if new_record:
                        if type(new_record) is not list:
                            new_record = [new_record]
                        for record in new_record:
                            new_record_dates_fixed = self.fix_date_format(
                                data=record.values(), sep=date_sep
                            )
                            cmd = self.sql(table, fields)
                            values = (
                                [rec[0]]
                                + new_record_dates_fixed
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            # self.lock.acquire()
                            # delete all old records from member
                            self.cursor.execute(
                                f"DELETE FROM {table} WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa}')"
                            )
                            # insert gathered record of member
                            self.cursor.execute(cmd, values)
                            self.conn.commit()  # writes every time - maybe take away later
                            # self.lock.release()

                    # register action and skip to next record
                    self.log_action(scraper=table, idPlaca=rec[0])
                    break
                except KeyboardInterrupt:
                    quit()
                except:
                    retry_attempts += 1
                    if retry_attempts > 3:
                        self.LOG.warning(
                            f"< {table.upper()} > Could not process {rec}. Skipping Record."
                        )
                        break
                    else:
                        self.LOG.warning(f"< {table.upper()} > Retrying {rec}.")
