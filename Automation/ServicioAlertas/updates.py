import os, io, time
import openpyxl
from copy import deepcopy as copy
import threading
from datetime import datetime as dt, timedelta as td
import uuid
import pygame
from pygame.locals import *
from selenium.common.exceptions import NoSuchElementException

import scrapers, sunarp
from gft_utils import pygameUtils

from pprint import pprint


class Gui:

    def __init__(self, zoomto, numchar) -> None:
        self.zoomto = zoomto
        self.numchar = numchar

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
            numpad = (
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
                    elif event.key in numpad:
                        chars.append(str(numpad.index(event.key)))
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


def threader(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class Update:

    def __init__(self, LOG, members) -> None:
        self.LOG = LOG
        self.cursor = members.cursor
        self.conn = members.conn
        self.sql = members.sql
        self.lock = threading.Lock()

    def get_records_to_process(self):

        # create dictionary with all tables as keys and empty set as value
        self.cursor.execute("SELECT * FROM tableInfo")
        tables = self.cursor.fetchall()
        self.all_updates = {i[1]: set() for i in tables}

        # 1. process BIENVENIDA

        # query to get records with documentos
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

        # query to get records with placas
        cmd.append(
            """SELECT IdMember, IdPlaca, Placa FROM placas
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

        # put results by data type in all necessary scraper type
        for i in range(2):
            self.cursor.execute(cmd[i])
            _result = set(self.cursor.fetchall())
            self.cursor.execute(f"SELECT * FROM tableInfo WHERE dataRequired = {i+1}")
            tables = self.cursor.fetchall()
            self.all_updates.update({i[1]: _result for i in tables})

        # 2. get records from EXPIRATION and NON-EXPIRATION updates

        # sql template for extraction
        build_cmd = (
            lambda i, j: f"""
                SELECT IdMember, DocTipo, DocNum FROM ({i})
                JOIN members
                ON members.IdMember = Id{j}_FK;
                """
        )

        # get all necessary sracper types
        self.cursor.execute("SELECT * FROM tableInfo")
        tables = self.cursor.fetchall()

        # add required records table by table
        for table in tables:
            # non-expiration update
            if table[7]:
                txt = f"SELECT * FROM {table[1]} WHERE DATE('now', '{table[7]} days') > LastUpdate"
            # expiration update
            else:
                txt = f"SELECT * FROM {table[1]} WHERE FALSE "
                for expiration in table[4:7]:
                    if expiration:
                        txt += f"OR DATE('now', '{expiration} days') = LastUpdate "

            # build sql query to append records that require updating to list
            self.cursor.execute(build_cmd(txt, "Member" if table[2] == 1 else "Placa"))
            self.all_updates[table[1]].update(self.cursor.fetchall())

        self.all_updates["satmuls"] = [(14, 19, "BJK193")]

        pprint(self.all_updates)

        return

    def log_action(self, scraper, idMember=None, idPlaca=None):
        cmd = self.sql("actions", ["Scraper", "IdMember_FK", "IdPlaca_FK", "Timestamp"])
        self.lock.acquire()
        self.cursor.execute(
            cmd, [scraper, idMember, idPlaca, dt.now().strftime("%Y-%m-%d")]
        )
        self.conn.commit()
        self.lock.release()

    def get_fields(self, table):
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        return [i[0] for i in self.cursor.fetchall()[1:]]

    def gather_soat(self, scraper, table):
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields = self.get_fields(table)
        # set up scraper for image
        scraper2 = scrapers.SoatImage()
        # get captcha manually
        canvas = pygameUtils(screen_size=(1050, 130))
        GUI = Gui(zoomto=(465, 105), numchar=6)

        # iterate on every placa and write to database
        for placa in self.all_updates["soats"]:
            retry_attempts = 0
            while True:
                try:
                    captcha_img = scraper.get_captcha_img()
                    captcha = GUI.gui(canvas, captcha_img)
                    response = scraper.browser(placa=placa[2], captcha_txt=captcha)

                    # wrong captcha - restart loop with same placa
                    if response == -2:
                        continue
                    # exceed limit of manual captchas - abort iteration
                    elif response == -1:
                        return
                    # if there is data in response, enter into database, go to next placa
                    elif response:
                        # if soat data gathered succesfully, get soat image too
                        img_name = scraper2.browser(placa=placa[2])
                        cmd = self.sql(table, fields)
                        values = (
                            [placa[1]]
                            + list(response.values())
                            + [img_name]
                            + [dt.now().strftime("%Y-%m-%d")]
                        )
                        self.lock.acquire()

                        self.cursor.execute(cmd, values)
                        self.lock.release()
                        self.conn.commit()  # writes every time - maybe take away later

                    self.log_action(scraper="soats", idPlaca=placa[1])
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

    def gather_sunarp(self, scraper, table):
        canvas = pygameUtils(screen_size=(1070, 140))
        GUI = Gui(zoomto=(500, 120), numchar=6)

        # iterate on every placa and write to database
        for placa in self.all_updates["sunarps"]:
            try:
                while True:
                    captcha_img = scraper.get_captcha_image()
                    captcha = GUI.gui(canvas, captcha_img)
                    response = scraper.browser(placa=placa[2], captcha_txt=captcha)
                    # wrong captcha or correct catpcha, no image loaded - restart loop with same placa
                    if response is int and response < 0:
                        continue
                    # correct captcha, no data for placa - enter update attempt to database, go to next placa
                    elif response is int and response == 1:
                        break
                    # if there is data in response, enter into database, go to next placa
                    elif response:
                        # process image and save to disk, update database with file information
                        try:
                            # add image filename and image date to record
                            _img_filename = f"SUNARP_{placa[2]}.png"
                            sunarp.process_image(response, _img_filename)
                            fields = ["IdPlaca_FK", "ImgFilename", "ImgUpdate"]
                            values = [
                                placa[1],
                                _img_filename,
                                dt.now().strftime("%Y-%m-%d"),
                            ]

                            # add ocr results to record
                            ocr_result = sunarp.ocr_and_parse(_img_filename)
                            if ocr_result:
                                fields += [
                                    "IdPlaca_FK",
                                    "PlacaValidate",
                                    "Serie",
                                    "VIN",
                                    "Motor",
                                    "Color",
                                    "Marca",
                                    "Modelo",
                                    "PlacaVigente",
                                    "PlacaAnterior",
                                    "Estado",
                                    "Anotaciones",
                                    "Sede",
                                    "Propietarios",
                                    "Ano",
                                    "LastUpdate",
                                ]
                                values += (
                                    [placa[1]]
                                    + ocr_result
                                    + [dt.now().strftime("%Y-%m-%d")]
                                )

                            # update database
                            cmd = self.sql(table, fields)
                            self.lock.acquire()

                            self.cursor.execute(cmd, values)
                            self.lock.release()
                            self.log_action(scraper=table, idPlaca=placa[1])
                            self.conn.commit()
                            break
                        except KeyboardInterrupt:
                            self.LOG.warning(
                                f"Error processing Placa {placa}. Record skipped."
                            )
                            return
            except KeyboardInterrupt:
                quit()
            # except:
            #     time.sleep(3)
            #     WEBD.refresh()
            #     break

    def gather_satmul(self, scraper, table):
        # get field list from table, do not consider fist one (ID Autogenerated)
        fields = self.get_fields(table)
        # iterate on every placa and write to database
        for placa in self.all_updates[table]:
            retry_attempts = 0
            while True:
                try:
                    responses = scraper.browser(placa=placa[2])
                    # if there is data in response, enter into database, go to next placa
                    if responses:
                        for response in responses:
                            cmd = self.sql(table, fields)
                            values = (
                                [placa[1]]
                                + list(response.values())
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            self.lock.acquire()
                            self.cursor.execute(cmd, values)
                            self.lock.release()
                            self.log_action(scraper=table, idPlaca=placa[1])

                    self.conn.commit()  # writes every time - maybe take away later
                    break
                except KeyboardInterrupt:
                    quit()
                # except:
                #     retry_attempts += 1
                #     if retry_attempts > 3:
                #         self.LOG.warning(
                #             f"< {table.upper()} > Could not process {placa}. Skipping Record."
                #         )
                #         break
                #     else:
                #         self.LOG.warning(f"< {table.upper()} > Retrying {placa}.")
                #         continue

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
        for k, rec in enumerate(self.all_updates[table1]):
            retry_attempts = 0
            while True:
                try:
                    new_record = scraper.browser(doc_tipo=rec[1], doc_num=rec[2])
                    for nrec in new_record:
                        cmd = self.sql(table1, fields1)
                        values = [rec[0], nrec["codigo"], dt.now().strftime("%Y-%m-%d")]
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
                            self.lock.acquire()
                            self.cursor.execute(cmd, values)
                            self.lock.release()
                            self.log_action(scraper=table2, idMember=rec[0])
                            break

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
                        continue

            print(f"{table1}: {(k+1)/len(self.all_updates[table1])*100:.1f}%")

    @threader
    def gather_with_docs(self, scraper, table):

        # get field list from table, do not consider fist one (ID Autogenerated)
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        fields = [i[0] for i in self.cursor.fetchall()[1:]]

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.all_updates[table]):
            retry_attempts = 0
            while True:
                try:
                    new_record = scraper.browser(doc_tipo=rec[1], doc_num=rec[2])
                    if new_record:
                        if type(new_record) is not list:
                            new_record = [new_record]
                        for nr in new_record:
                            cmd = self.sql(table, fields)
                            values = (
                                [rec[0]]
                                + list(nr.values())
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            self.lock.acquire()
                            self.cursor.execute(cmd, values)
                            self.conn.commit()
                            self.lock.release()
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
                        continue

            print(f"{table}: {(k+1)/len(self.all_updates[table])*100:.1f}%")

    @threader
    def gather_with_placa(self, scraper, table):

        # get field list from table, do not consider fist one (ID Autogenerated)
        self.cursor.execute(
            f"SELECT name FROM pragma_table_info('{table}') ORDER BY cid;"
        )
        fields = [i[0] for i in self.cursor.fetchall()[1:]]

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.all_updates[table]):
            retry_attempts = 0
            while True:
                try:
                    new_record = scraper.browser(placa=rec[2])
                    if new_record:
                        cmd = self.sql(table, fields)
                        values = (
                            [rec[1]]
                            + list(new_record.values())
                            + [dt.now().strftime("%Y-%m-%d")]
                        )
                        self.lock.acquire()
                        self.cursor.execute(cmd, values)
                        self.conn.commit()  # writes every time - maybe take away later
                        self.lock.release()

                    # register action and skip to next record
                    self.log_action(scraper=table, idPlaca=rec[1])
                    break
                except KeyboardInterrupt:
                    quit()
                # except:
                #     retry_attempts += 1
                #     if retry_attempts > 3:
                #         self.LOG.warning(
                #             f"< {table.upper()} > Could not process {rec}. Skipping Record."
                #         )
                #         break
                #     else:
                #         self.LOG.warning(f"< {table.upper()} > Retrying {rec}.")
                #         continue

            print(f"{table}: {(k+1)/len(self.all_updates[table])*100:.1f}%")
