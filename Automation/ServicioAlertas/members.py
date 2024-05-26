import os, sys, json
import openpyxl
import sqlite3
from copy import deepcopy as copy
import uuid
from pygame.locals import *

from gft_utils import GoogleUtils


class Members:

    def __init__(self, LOG) -> None:
        self.LOG = LOG
        # select production or test database
        if not "TEST" in sys.argv:
            SQLDATABASE = os.path.join(os.getcwd(), "data", "members.sqlite")
        else:
            SQLDATABASE = os.path.join(os.getcwd(), "data", "membersTEST.sqlite")

        # connect to database
        self.conn = sqlite3.connect(SQLDATABASE, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # only when building - take way later
        # self.restart_database()

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

            self.conn.commit()

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

    def sql(self, table, fields):
        qmarks = ",".join(["?" for _ in range(len(fields))])
        return f"REPLACE INTO {table} ({','.join(fields)}) VALUES ({qmarks})"

    def load_scripts(self):
        # Placeholder if we start loading more scripts into it
        SQLSCRIPTS = os.path.join(os.getcwd(), "sql_script1.sql")
        with open(SQLSCRIPTS, mode="r", encoding="utf-8") as file:
            self.SCRIPTS = json.load(file)

    def restart_database(self):
        SQLSCRIPT1 = os.path.join(os.getcwd(), "static", "sql_script1.sql")
        with open(SQLSCRIPT1, mode="r", encoding="utf-8") as file:
            cmd = file.read()
        self.cursor.executescript(cmd)
