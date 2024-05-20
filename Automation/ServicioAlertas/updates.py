import os, io, time
import openpyxl
from copy import deepcopy as copy
import threading
from datetime import datetime as dt, timedelta as td
import uuid
import pygame
from pygame.locals import *

import scrapers, sunarp
from gft_utils import ChromeUtils, GoogleUtils, pygameUtils


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


class Members:

    def __init__(self, LOG, DB) -> None:
        self.LOG = LOG
        self.cursor = DB.cursor
        self.conn = DB.conn
        self.sql = DB.sql

    def load_form_members(self):
        # download latest form responses
        G = GoogleUtils()
        _folder_id = "1Az6eM7Fr9MUqNhj-JtvOa6WOhYBg5Qbs"
        _file = [i for i in G.get_drive_files(_folder_id) if "members" in i["title"]][0]
        G.download_from_drive(_file, ".\data\members.xlsx")

        # open latest form responses
        wb = openpyxl.load_workbook(".\data\members.xlsx")
        sheet = wb["Form Responses 2"]
        raw_data = [
            {
                sheet.cell(row=1, column=j).value: sheet.cell(row=i + 1, column=j).value
                for j in range(2, sheet.max_column + 1)
            }
            for i in range(1, sheet.max_row)
        ]

        # clean data and join placas in one list
        for r, row in enumerate(copy(raw_data)):
            placas = []
            for col in row:
                if type(row[col]) == float:
                    raw_data[r][col] = str(int(row[col]))
                if type(raw_data[r][col]) == str and "@" in raw_data[r][col]:
                    raw_data[r][col] = raw_data[r][col].lower()
                if "Nombre" in col:
                    raw_data[r][col] = raw_data[r][col].title()
                if "Correo" in col:
                    raw_data[r]["Correo"] = raw_data[r].pop(col)
                if "Placa" in col:
                    if raw_data[r][col]:
                        placas.append(
                            raw_data[r][col].replace("-", "").replace(" ", "").upper()
                        )
                    del raw_data[r][col]
            raw_data[r].update(
                {
                    "Placas": placas,
                }
            )
        return raw_data

    def add_new_members(self):
        # download form and structure data to add to database
        form_members = self.load_form_members()

        # get DocNum from existing members as index to avoid duplicates
        self.cursor.execute("SELECT DocNum FROM members")
        existing_members_docs = [i[0] for i in self.cursor.fetchall()]

        # iterate on all members from online form and only add new ones (new DocNum)
        for member in form_members:
            # add basic information to members table
            if str(member["Número de Documento"]) not in existing_members_docs:
                cmd = self.sql(
                    "members",
                    [
                        "NombreCompleto",
                        "DocTipo",
                        "DocNum",
                        "Celular",
                        "Correo",
                        "CodMember",
                    ],
                )
                values = list(member.values())[:5] + [
                    "SAP-" + str(uuid.uuid4())[-6:].upper()
                ]
                self.cursor.execute(cmd, values)

                # get autoindex number to link to placas table
                cmd = f"SELECT * FROM members WHERE DocNum = '{values[2]}'"
                self.cursor.execute(cmd)
                idmember = self.cursor.fetchone()[0]

                # add placas to placas table
                for placa in member["Placas"]:
                    cmd = self.sql("placas", ["IdMember_FK", "Placa"])
                    values = [idmember] + [placa]
                    self.cursor.execute(cmd, values)

                self.LOG.info(
                    f"Appended new record: {idmember} - {member['Número de Documento']}"
                )

    def get_records_to_process(self):

        # process BIENVENIDA

        # get documentos with no bienvenida message
        cmd = """SELECT IdMember, DocTipo, DocNum FROM members
                EXCEPT
                SELECT IdMember, DocTipo, DocNum FROM (
                SELECT mensajes.IdMember_FK FROM mensajes JOIN mensajeContenidos ON mensajes.IdMensaje = mensajeContenidos.IdMensaje_FK
                WHERE IdTipoMensaje_FK = 12)
                JOIN members
                ON members.IdMember = IdMember_FK
                """
        self.cursor.execute(cmd)
        self.docs_to_process = self.cursor.fetchall()

        # get placas with no bienvenida message
        cmd = """SELECT IdMember, IdPlaca, Placa FROM placas
                JOIN (SELECT IdMember, DocTipo, DocNum FROM members
                EXCEPT
                SELECT IdMember, DocTipo, DocNum FROM (
                SELECT mensajes.IdMember_FK FROM mensajes JOIN mensajeContenidos ON mensajes.IdMensaje = mensajeContenidos.IdMensaje_FK
                WHERE IdTipoMensaje_FK = 12)
                JOIN members
                ON members.IdMember = IdMember_FK)
                ON placas.IdMember_FK = IdMember
                """
        self.cursor.execute(cmd)
        self.placas_to_process = self.cursor.fetchall()

        print(self.placas_to_process)
        print(self.docs_to_process)

        # process DOCS
        base_cmd = (
            lambda i: f"""
                SELECT IdMember, DocTipo, DocNum FROM ({i})
                JOIN members
                ON members.IdMember = IdMember_FK
                """
        )

        sutran = base_cmd("SELECT * FROM soat WHERE XXXXXXXXXXXXX date statement")
        brevete = base_cmd("SELECT * FROM brevete WHERE XXXXXXXXXXXXX date statement")
        satimp = base_cmd("SELECT * FROM satimp WHERE XXXXXXXXXXXXX date statement")

        # process PLACAS

        base_cmd = (
            lambda i: f"""SELECT IdMember, IdPlaca, Placa FROM placas
                JOIN (
                SELECT IdMember, DocTipo, DocNum FROM ({i})
                JOIN members
                ON members.IdMember = IdMember_FK)
                ON placas.IdMember_FK = IdMember
                """
        )

        soat = base_cmd("SELECT * FROM soat WHERE XXXXXXXXXXXXX date statement")
        satmul = base_cmd("SELECT * FROM satmul WHERE XXXXXXXXXXXXX date statement")


class ManualUpdates:

    def __init__(self, LOG, DB) -> None:
        self.LOG = LOG
        self.cursor = DB.cursor
        self.conn = DB.conn
        self.sql = DB.sql

    def gather_soat(self):
        # open URL and activate scraper
        URL = "https://www.apeseg.org.pe/consultas-soat/"
        WEBD = ChromeUtils().init_driver(headless=True, maximized=True, incognito=True)
        WEBD.get(URL)
        canvas = pygameUtils(screen_size=(1050, 130))
        SCRAPER = scrapers.Soat(WEBD)
        GUI = Gui(zoomto=(465, 105), numchar=6)

        # iterate on every placa and write to database
        for placa in self.placas_to_process:
            try:
                while True:
                    captcha_img = SCRAPER.get_captcha_img(WEBD)
                    captcha = GUI.gui(canvas, captcha_img)
                    response = SCRAPER.browser(placa=placa[2], captcha_txt=captcha)
                    # wrong captcha - restart loop with same placa
                    if response == -2:
                        WEBD.refresh()
                        continue
                    # exceed limit of manual captchas - abort iteration
                    elif response == -1:
                        return
                    # if there is data in response, enter into database, go to next placa
                    elif response:
                        cmd = self.sql(
                            "soats",
                            [
                                "IdPlaca_FK",
                                "Aseguradora",
                                "FechaInicio",
                                "FechaFin",
                                "PlacaValidate",
                                "Certificado",
                                "Uso",
                                "Clase",
                                "Vigencia",
                                "Tipo",
                                "FechaVenta",
                                "LastUpdate",
                            ],
                        )
                        values = (
                            [placa[1]]
                            + list(response.values())
                            + [dt.now().strftime("%Y-%m-%d")]
                        )
                        self.cursor.execute(cmd, values)
                        self.conn.commit()  # writes every time - maybe take away later
                        break
            except KeyboardInterrupt:
                quit()
            except:
                time.sleep(3)
                WEBD.refresh()
                break

    def gather_sunarp(self):
        # open first URL, wait and open second URL and activate scraper
        URL1 = "https://www.gob.pe/sunarp"
        URL2 = "https://www.sunarp.gob.pe/consulta-vehicular.html"
        WEBD = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True, incognito=True
        )
        WEBD.get(URL1)
        time.sleep(2)
        WEBD.get(URL2)
        time.sleep(1)
        canvas = pygameUtils(screen_size=(1070, 140))
        SCRAPER = scrapers.Sunarp(WEBD)
        GUI = Gui(zoomto=(500, 120), numchar=6)

        # iterate on every placa and write to database
        for placa in self.placas_to_process:
            try:
                while True:
                    captcha_img = SCRAPER.get_captcha_image()
                    captcha = GUI.gui(canvas, captcha_img)
                    response = SCRAPER.browser(placa=placa[2], captcha_txt=captcha)
                    # wrong captcha or correct catpcha, no image loaded - restart loop with same placa
                    if response < 0:
                        WEBD.refresh()
                        continue
                    # correct captcha, no data for placa - enter update attempt to database, go to next placa
                    elif response == 1:
                        cmd = self.sql("sunarps", ["IdPlaca_FK", "ImgUpdate"])
                        values = [placa[1], dt.now().strftime("%Y-%m-%d")]
                        self.cursor.execute(cmd, values)
                        self.conn.commit()  # writes every time - maybe take away later
                        break
                    # if there is data in response, enter into database, go to next placa
                    elif response:
                        # process image and save to disk, update database with file information
                        _img_filename = f"SUNARP_{placa[2]}.png"
                        sunarp.process_image(response, _img_filename)
                        cmd = self.sql(
                            "sunarps", ["IdPlaca_FK", "ImgFilename", "ImgUpdate"]
                        )
                        values = [
                            placa[1],
                            _img_filename,
                            dt.now().strftime("%Y-%m-%d"),
                        ]
                        self.cursor.execute(cmd, values)
                        self.conn.commit()  # writes every time - maybe take away later
                        # attempt ocr on image, update database with file information if succesful
                        ocr_result = sunarp.ocr_and_parse(_img_filename)
                        if ocr_result:
                            cmd = """UPDATE TABLE sunarps SET
                              IdPlaca_FK,
                              PlacaValidate,
                              Serie,
                              VIN,
                              Motor,
                              Color,
                              Marca,
                              Modelo,
                              PlacaVigente,
                              PlacaAnterior,
                              Estado,
                              Anotaciones,
                              Sede,
                              Propietarios,
                              Ano
                              LastUpdate
                              VALUES
                              (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                            values = (
                                [placa[1]]
                                + ocr_result
                                + [dt.now().strftime("%Y-%m-%d")]
                            )
                            self.cursor.execute(cmd, values)
                            break
            except KeyboardInterrupt:
                quit()
            # except:
            #     time.sleep(3)
            #     WEBD.refresh()
            #     break

    def gather_satmul(self):
        # open URL and activate scraper
        WEBD = ChromeUtils().init_driver(
            headless=False, verbose=False, maximized=True, incognito=False
        )
        WEBD.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
        _target = (
            "https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?tri=T&mysession="
            + WEBD.current_url.split("=")[-1]
        )
        time.sleep(2)
        WEBD.get(_target)
        SCRAPER = scrapers.Satmul()

        # iterate on every placa and write to database
        for placa in self.placas_to_process:
            try:
                while True:
                    response = SCRAPER.browser(placa=placa[2])
                    # unsuccesful scrape - restart loop with same placa
                    if response < 0:
                        WEBD.refresh()
                        continue
                    # if there is data in response, enter into database, go to next placa
                    elif response:
                        cmd = self.sql(
                            "satmul",
                            [
                                "IdPlaca_FK",
                                "Aseguradora",
                                "FechaInicio",
                                "FechaFin",
                                "PlacaValidate",
                                "Certificado",
                                "Uso",
                                "Clase",
                                "Vigencia",
                                "Tipo",
                                "FechaVenta",
                                "LastUpdate",
                            ],
                        )
                        values = (
                            [placa[1]]
                            + list(response.values())
                            + [dt.now().strftime("%Y-%m-%d")]
                        )
                        self.cursor.execute(cmd, values)
                        self.conn.commit()  # writes every time - maybe take away later
                        break
            except KeyboardInterrupt:
                quit()
            # except:
            #     time.sleep(3)
            #     WEBD.refresh()
            #     break


class AutoUpdates:

    def __init__(self, LOG, DB) -> None:
        self.LOG = LOG
        self.cursor = DB.cursor
        self.conn = DB.conn
        self.sql = DB.sql

    def launch_threads():
        scrapers = [
            "satimp",
            "brevete",
            "revtec",
            "sutran",
            "soatimage",
            "callaomulta",
            "osiptel",
        ]
        threads = [threading.Thread(target=f"gather_{s}") for s in scrapers]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def gather_brevete(self):
        scraper = scrapers.Brevete()
        WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
        WEBD.get("https://licencias.mtc.gob.pe/#/index")
        time.sleep(3)

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.docs_to_process):
            try:
                new_record, _ = scraper.browser(doc_tipo=rec[1], doc_num=rec[2])
                if new_record:
                    cmd = self.sql(
                        "brevetes",
                        [
                            "IdMember_FK",
                            "Clase",
                            "Numero",
                            "Tipo",
                            "FechaExp",
                            "Restricciones",
                            "FechaHasta",
                            "Centro",
                            "LastUpdate",
                        ],
                    )
                    values = (
                        [rec[2]]
                        + list(new_record["Brevete"].values())
                        + [dt.now().strftime("%Y-%m-%d")]
                    )
                    self.cursor.execute(cmd, values)
                    self.conn.commit()  # writes every time - maybe take away later
                    break
            except KeyboardInterrupt:
                quit()
            # except:
            #     self.LOG.warning(f"No proceso {rec}")
            #     scraper.WEBD.refresh()

            print(f"Brevete: {(k+1)/len(self.docs_to_process)*100:.1f}%")

    def gather_revtec(self):
        scraper = scrapers.Revtec()
        WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
        WEBD.get("https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx")
        time.sleep(3)

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.placas_to_process):
            try:
                new_record, _ = scraper.browser(placa=rec[2])
                if new_record:
                    cmd = self.sql(
                        "revtecs",
                        [
                            "Placa_FK",
                            "Certificadora",
                            "PlacaValidate",
                            "Certificado",
                            "FechaDesde",
                            "FechaHasta",
                            "Resultado",
                            "Vigencia",
                            "LastUpdate",
                        ],
                    )
                    values = (
                        [rec[2]]
                        + list(new_record.values())
                        + [dt.now().strftime("%Y-%m-%d")]
                    )
                    self.cursor.execute(cmd, values)
                    self.conn.commit()
                    break
            except KeyboardInterrupt:
                quit()
            # except:
            #     self.LOG.warning(f"No proceso {rec}")
            #     scraper.WEBD.refresh()

            print(f"RevTec: {(k+1)/len(self.docs_to_process)*100:.1f}%")

    def gather_sutran(self):
        scraper = scrapers.Sutran()
        WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
        WEBD.get(
            "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/"
        )
        time.sleep(3)

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.docs_to_process):
            try:
                new_record, _ = scraper.browser(doc_tipo=rec[1], doc_num=rec[2])
                if new_record:
                    cmd = self.sql(
                        "sutrans",
                        [
                            "IdPlaca_FK",
                            "Documento",
                            "Tipo",
                            "FechaDoc",
                            "CodigoInfrac",
                            "Clasificacion",
                            "LastUpdate",
                        ],
                    )
                    values = (
                        [rec[2]]
                        + list(new_record.values())
                        + [dt.now().strftime("%Y-%m-%d")]
                    )
                    self.cursor.execute(cmd, values)
                    self.conn.commit()
                    break
            except KeyboardInterrupt:
                quit()
            except:
                self.LOG.warning(f"No proceso {rec}")
                scraper.WEBD.refresh()

            print(f"Sutran: {(k+1)/len(self.docs_to_process)*100:.1f}%")

    def gather_soatimage(self):
        scraper = scrapers.SoatImage()
        WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
        WEBD.get("https://www.pacifico.com.pe/consulta-soat")
        time.sleep(3)

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.placas_to_process):
            try:
                new_record, _ = scraper.browser(placa=rec[2])
                if new_record:
                    cmd = self.sql(
                        "soats",
                        [
                            "IdPlaca_FK",
                            "Aseguradora",
                            "FechaInicio",
                            "FechaFin",
                            "PlacaValidate",
                            "Certificado",
                            "Uso",
                            "Clase",
                            "Vigencia",
                            "Tipo",
                            "FechaVenta",
                            "LastUpdate",
                        ],
                    )
                    values = (
                        [rec[2]]
                        + list(new_record.values())
                        + [dt.now().strftime("%Y-%m-%d")]
                    )
                    self.cursor.execute(cmd, values)
                    self.conn.commit()
                    break
            except KeyboardInterrupt:
                quit()
            # except:
            #     self.LOG.warning(f"No proceso {rec}")
            #     scraper.WEBD.refresh()

            print(f"SoatImage {(k+1)/len(self.docs_to_process)*100:.1f}%")

    def gather_callaomulta(self):
        scraper = scrapers.CallaoMulta()
        WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
        WEBD.get("https://pagopapeletascallao.pe/")
        time.sleep(3)

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.placas_to_process):
            try:
                new_record, _ = scraper.browser(placa=rec[2])
                if new_record:
                    cmd = """ """
                    self.cursor.execute(cmd, new_record)
            except KeyboardInterrupt:
                quit()
            except:
                self.LOG.warning(f"No proceso {rec}")
                scraper.WEBD.refresh()
                self.conn.commit()
                break

            print(f"CallaoMultas: {(k+1)/len(self.docs_to_process)*100:.1f}%")

    def gather_osiptel(self):
        # TODO
        return
        scraper = scrapers.Satimp()
        WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
        WEBD.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
        time.sleep(3)

        # iterate on all records that require updating and get scraper results
        for k, rec in enumerate(self.placas_to_process):
            try:
                new_record, _ = scraper.browser(placa=rec[2])
                if new_record:
                    cmd = """ """
                    self.cursor.execute(cmd, new_record)
            except KeyboardInterrupt:
                quit()
            except:
                self.LOG.warning(f"No proceso {rec}")
                scraper.WEBD.refresh()
                self.conn.commit()
                break

            print(f"Satimp: {(k+1)/len(self.docs_to_process)*100:.1f}%")
