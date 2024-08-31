import io, os
import time
import threading
from datetime import datetime as dt
import pygame
from pygame.locals import *
import speech_recognition
from tkinter import Tk, Label
from PIL import Image, ImageTk

# local imports
import sunarp, soat_image
from gft_utils import SpeechUtils


def threader(func):
    """Decorator function that includes function in thread."""

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        time.sleep(2)
        thread.start()
        args[0].threads.append(thread)  # args[0] is UPDATE instance (self)
        return thread

    return wrapper


class Gui:
    """Manages PyGame window that captures manual captcha."""

    def __init__(self, zoomto, numchar) -> None:
        self.zoomto = zoomto
        self.numchar = numchar
        self.speech = speech_recognition.Recognizer()
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

    def get_speech2(self):
        while True:
            try:
                with speech_recognition.Microphone() as mic:
                    self.speech.adjust_for_ambient_noise(mic, duration=0.2)
                    _audio = self.speech.listen(mic)
                    text = self.speech.recognize_google(_audio)
                    text = text.lower().replace(" ", "")
                    with open(
                        os.path.join(
                            "D:\pythonCode",
                            "Resources",
                            "StaticData",
                            "military_alphabet.txt",
                        )
                    ) as file:
                        ma_index = [i.strip() for i in file.readlines()]
                        for word in ma_index:
                            text = text.replace(word, word[0])

                    print(f"Output: {text}")
                    if len(text) == 6:
                        return text
            except:
                if self.speech_driver_errors < 5:
                    self.speech = speech_recognition.Recognizer()
                    self.speech_driver_errors += 1
                else:
                    return None

    def get_speech(self):
        while True:
            text = SpeechUtils().get_speech()
            text = text.lower().replace(" ", "")
            if len(text) == 6:
                return text

    def show_captcha(self):
        window = Tk()
        window.geometry("1085x245")
        window.config(background="black")
        img = Image.open(io.BytesIO(self.captcha_img)).resize((1085, 245))
        _img = ImageTk.PhotoImage(master=window, image=img)
        label = Label(master=window, image=_img)
        label.grid(row=0, column=0)
        window.mainloop()

    def gui2(self, captcha_img):
        self.captcha_img = captcha_img
        t1 = threading.Thread(target=self.show_captcha, daemon=True)
        t1.start()
        return self.get_speech()

    def gui(self, canvas, captcha_img):
        TEXTBOX = pygame.Surface((80, 120))
        UPPER_LEFT = (10, 10)
        image = pygame.image.load(io.BytesIO(captcha_img)).convert()
        image = pygame.transform.scale(image, self.zoomto)
        canvas.MAIN_SURFACE.fill(canvas.COLORS["BLACK"])
        canvas.MAIN_SURFACE.blit(image, UPPER_LEFT)

        # return self.get_speech()

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

    def __init__(self, LOG, members, monitor) -> None:
        self.LOG = LOG
        self.MONITOR = monitor
        self.cursor = members.cursor
        self.conn = members.conn
        self.sql = members.sql
        self.day30_list = members.day30_list
        self.threads = []

    def get_records_to_process(self):

        # create dictionary with all tables as keys and empty list as value
        self.cursor.execute("SELECT * FROM '@tableInfo'")
        self.all_updates = {i[1]: [] for i in self.cursor.fetchall()}

        # 1. adds records that require a message and are within the scope of vencimiento

        # creates temporary tables with all members/placas that haven't received an email in 30+ days
        cmd = """ DROP TABLE IF EXISTS _regmsg_members;
                    CREATE TABLE _regmsg_members (IdMember_FK);
                    INSERT INTO _regmsg_members (IdMember_FK) SELECT IdMember FROM members JOIN (
	                SELECT IdMember AS x FROM members
                    EXCEPT
	                SELECT IdMember_FK FROM mensajes
		            JOIN mensajeContenidos
		            ON IdMensaje = IdMensaje_FK
		            WHERE fecha >= datetime('now','localtime', '-1 month')
			        AND (IdTipoMensaje_FK = 12 OR IdTipoMensaje_FK = 13)
	            )
                    ON members.IdMember = x;
				
                  DROP TABLE IF EXISTS _regmsg_placas;
                  CREATE TABLE _regmsg_placas (IdPlaca_FK);			
                  INSERT INTO _regmsg_placas (IdPlaca_FK) SELECT IdPlaca FROM placas 
                    JOIN (_regmsg_members)
                    ON placas.IdMember_FK = _regmsg_members.IdMember_FK"""
        self.cursor.executescript(cmd)

        # brevetes
        cmd = """ SELECT IdMember, DocTipo, DocNum FROM members JOIN (
                    SELECT IdMember_FK FROM brevetes WHERE IdMember_FK IN (
                        SELECT * FROM _regmsg_members) 
                        AND FechaHasta <= datetime('now','localtime', '+45 days'))
                    ON IdMember = IdMember_FK"""
        self.cursor.execute(cmd)
        self.all_updates["brevetes"] = self.cursor.fetchall()

        # soats, revtecs
        for table in ("soats", "revtecs"):
            cmd = f"""SELECT IdPlaca, Placa FROM placas JOIN (
                        SELECT IdPlaca_FK FROM {table} WHERE IdPlaca_FK IN (
                            SELECT * FROM _regmsg_placas)
                            AND FechaHasta <= datetime('now','localtime', '+45 days'))
                        ON IdPlaca = IdPlaca_FK"""
            self.cursor.execute(cmd)
            self.all_updates[table] = self.cursor.fetchall()

        # satimps
        cmd = """ SELECT IdMember, DocTipo, DocNum FROM members JOIN (
                        SELECT IdMember_FK FROM satimpCodigos
                        JOIN satimpDeudas
                        ON satimpCodigos.IdCodigo = satimpDeudas.IdCodigo_FK 
                    WHERE IdMember_FK IN (
                        SELECT * FROM _regmsg_members)
                        AND FechaHasta <= datetime('now','localtime', '+45 days'))
                    ON IdMember = IdMember_FK"""
        self.cursor.execute(cmd)
        self.all_updates["satimpCodigos"] = self.cursor.fetchall()

        # satmuls, sutrans
        self.cursor.execute(
            "SELECT IdPlaca, Placa FROM placas JOIN _regmsg_placas ON IdPlaca = IdPlaca_FK "
        )
        self.all_updates["satmuls"] = self.all_updates["sutrans"] = (
            self.cursor.fetchall()
        )

        # records
        self.cursor.execute(
            "SELECT IdMember, DocTipo, DocNum FROM members JOIN _regmsg_members ON IdMember = IdMember_FK"
        )
        self.all_updates["records"] = self.cursor.fetchall()

        # sunarps
        self.cursor.execute(
            "SELECT IdPlaca, Placa FROM placas JOIN (SELECT * FROM sunarps WHERE LastUpdate <= datetime('now','localtime', '-1 year')) ON IdPlaca = IdPlaca_FK"
        )
        self.all_updates["sunarps"] = self.cursor.fetchall()

        # sunats
        self.cursor.execute(
            "SELECT DocTipo, DocNum FROM members JOIN (SELECT * FROM sunats WHERE LastUpdate <= datetime('now','localtime', '-1 year')) ON IdMember = IdMember_FK"
        )
        self.all_updates["sunarps"] = self.cursor.fetchall()

        # 2. adds records that have no BIENVENIDA email

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

        # 3. add records that will be in alert list, to be updated before alert
        # TODO: add sunarps, sunats (1 year)

        # brevetes, satimps
        for table in [("brevetes", "BREVETE"), ("satimpCodigos", "SATIMP")]:
            cmd = f"""select members.IdMember, DocTipo, DocNum from members 
                       JOIN (select * from _alertaEnviar WHERE TipoAlerta = '{table[1]}')
                       ON IdMember = IdMember_FK"""
            self.cursor.execute(cmd)
            self.all_updates[table[0]] += self.cursor.fetchall()

        # soats, revtecs
        for table in [("soats", "SOAT"), ("revtecs", "REVTEC")]:
            cmd = f"""select placas.IdPlaca, placas.Placa from placas 
                       JOIN (select * from _alertaEnviar WHERE TipoAlerta = '{table[1]}')
                       ON IdPlaca = IdPlaca_FK"""
            self.cursor.execute(cmd)
            self.all_updates[table[0]] += self.cursor.fetchall()

        # eliminate duplicates
        self.all_updates = {i: set(j) for i, j in self.all_updates.items()}

        # log action
        self.LOG.info(f"Will update: {self.all_updates}")

        for k, v in self.all_updates.items():
            self.MONITOR.add_widget(f"{k}...{len(v)}", type=1)

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
        # scraper2 = scrapers.SoatImage()
        soat_image_generator = soat_image.SoatImage(self.LOG, self.cursor)

        # get captcha manually from user
        # canvas = pygameUtils(screen_size=(1050, 130))
        GUI = Gui(zoomto=(465, 105), numchar=6)
        # iterate on every placa and write to database
        for placa in self.all_updates["soats"]:
            retry_attempts = 0
            while True:
                try:
                    plac = placa[1]
                    captcha_img = scraper.get_captcha_img()
                    # captcha = GUI.gui(canvas, captcha_img)
                    captcha = GUI.gui2(captcha_img)
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
                            # img_name = scraper2.browser(placa=plac)
                            # generate image using Placa_FK
                            img_name = soat_image_generator.generate(id=placa[0])
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
                    self.MONITOR.add_widget(f"SOAT: {plac}", type=3)
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
        fields = self.get_fields("sunarps")
        # iterate on every placa and write to database
        for placa in self.all_updates["sunarps"]:
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
                        # add image filename
                        _img_filename = f"SUNARP_{placa[1]}.png"
                        sunarp.process_image(img_object, _img_filename)
                        fields = ["IdPlaca_FK", "ImgFilename", "LastUpdate"]
                        values = [
                            placa[0],
                            _img_filename,
                            dt.now().strftime("%Y-%m-%d"),
                        ]
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

                    self.MONITOR.add_widget(f"SOAT: {plac}", type=3)
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
                self.MONITOR.add_widget(f"RECORD: {doc[0]}", type=3)
                self.log_action(scraper=table, idMember=doc[0])
                self.conn.commit()

    # @threader
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
        for rec in self.all_updates[table1]:
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
                    self.MONITOR.add_widget(f"SATIMP: {doc_tipo}-{doc_num}", type=3)
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
        for rec in self.all_updates[table]:
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
                            self.MONITOR.add_widget(
                                f"BREVETE: {doc_tipo}-{doc_num}", type=3
                            )

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
    def gather_sunat(self, scraper, table, date_sep="-"):
        # get field list from table, do not consider fist one (ID Autogenerated)
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        fields = [i[0] for i in self.cursor.fetchall()[1:]]

        # iterate on all records that require updating and get scraper results
        for rec in self.all_updates[table]:
            retry_attempts = 0
            while True:
                try:
                    doc_tipo, doc_num = rec[1], rec[2]
                    new_record = scraper.browser(doc_tipo=doc_tipo, doc_num=doc_num)
                    if new_record:
                        # adjust date format for SQL (YYYY-MM-DD)
                        new_record_dates_fixed = self.fix_date_format(
                            data=new_record, sep=date_sep
                        )
                        print(new_record_dates_fixed)
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
                    self.MONITOR.add_widget(f"SUNAT: {doc_tipo}-{doc_num}", type=3)
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
        for rec in self.all_updates[table]:
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
                    self.MONITOR.add_widget(f"DOCS: {doc_tipo}-{doc_num}", type=3)
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
    def gather_placa(self, scraper, table, date_sep):
        # get field list from table, do not consider fist one (ID Autogenerated)
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        fields = [i[0] for i in self.cursor.fetchall()[1:]]

        # iterate on all records that require updating and get scraper results
        for rec in self.all_updates[table]:
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
                            # delete all old records from member
                            self.cursor.execute(
                                f"DELETE FROM {table} WHERE IdPlaca_FK = (SELECT IdPlaca FROM placas WHERE Placa = '{placa}')"
                            )
                            # insert gathered record of member
                            self.cursor.execute(cmd, values)
                            self.conn.commit()

                    # register action and skip to next record
                    self.MONITOR.add_widget(f"PLACA: {placa}", type=3)
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
