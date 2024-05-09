import scrapers
import json, sys, os
import openpyxl
from copy import deepcopy as copy
import time
from gft_utils import ChromeUtils, GoogleUtils
import threading
from datetime import datetime as dt, timedelta as td
from pprint import pprint
import uuid
import soat, sunarp, satmul


def load_form_members(LOG):
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


def add_new_members(LOG, form_members, members):
    correlativo = len(members)
    existing_members_docs = [i["Datos"]["Número de Documento"] for i in members]
    for all_member in form_members:
        if str(all_member["Número de Documento"]) not in existing_members_docs:
            _new_record = {
                "Correlativo": correlativo,
                "Codigo": "SAP-" + str(uuid.uuid4())[-6:].upper(),
                "Datos": all_member,
                "Resultados": {
                    "Satimp": [],
                    "Satimp_Actualizado": "01/01/1999",
                    "Brevete": {},
                    "Brevete_Actualizado": "01/01/1999",
                    "Revtec": [],
                    "Revtec_Actualizado": "01/01/1999",
                    "Sutran": [],
                    "Sutran_Actualizado": "01/01/1999",
                    "Soat": [],
                    "Soat_Actualizado": "01/01/1999",
                },
                "Envios": {
                    "Bienvenida": {},
                    "Regular": [],
                    "Alertas": {
                        "Brevete": [],
                        "Satimp": [],
                        "Revtec": [],
                        "Sutran": [],
                    },
                },
            }

            correlativo += 1
            members.append(_new_record)
            LOG.info(
                f"Appended new record: {_new_record['Correlativo']} - {_new_record['Datos']['Nombre y Apellido']}"
            )

    return members


def get_records_to_process(members):
    # TODO: beyond welcome
    docs_to_process, placas_to_process = [], []
    for member in members:
        if not member["Envios"]["Bienvenida"]:
            docs_to_process.append(
                (
                    member["Correlativo"],
                    -1,
                    member["Datos"]["Documento Tipo"],
                    member["Datos"]["Número de Documento"],
                    "",
                )
            )
            for k, placa in enumerate(member["Datos"]["Placas"]):
                placas_to_process.append((member["Correlativo"], k, "", "", placa))

    return docs_to_process, placas_to_process


def gather_soat(members, placas_to_process):
    SOAT = scrapers.Soat()
    scraper_responses = soat.main(SOAT, placas_to_process)

    new_response = [{"Soat": [[], [], []]} for _ in range(len(members))]
    for response in scraper_responses:
        rec, pos, data = response
        new_response[rec]["Soat"][pos] = data

    # delete dictionary keys that have no data to update
    new_responses = [
        {k: v for k, v in j.items() if v and v != [[], [], []]} for j in new_response
    ]

    for k, response in enumerate(new_responses):
        members[k]["Resultados"].update(response)
        members[k]["Resultados"]["Soat_Actualizado"] = dt.now().strftime("%d/%m/%Y")
    return members


def gather_sunarp(members, placas_to_process):
    SUNARP = scrapers.Sunarp()
    scraper_responses = sunarp.main(SUNARP, placas_to_process)

    new_response = [{"Sunarp": [[], [], []]} for _ in range(len(members))]
    for response in scraper_responses:
        rec, pos, data = response
        new_response[rec]["Sunarp"][pos] = data

    # delete dictionary keys that have no data to update
    new_responses = [
        {k: v for k, v in j.items() if v and v != [[], [], []]} for j in new_response
    ]

    for k, response in enumerate(new_responses):
        members[k]["Resultados"].update(response)
        members[k]["Resultados"]["Sunarp_Actualizado"] = dt.now().strftime("%d/%m/%Y")
    return members


def gather_satmul(members, placas_to_process):
    SATMUL = scrapers.Satmul()
    scraper_responses = satmul.main(SATMUL, placas_to_process)

    new_response = [{"Satmul": [[], [], []]} for _ in range(len(members))]
    for response in scraper_responses:
        rec, pos, data = response
        new_response[rec]["Satmul"][pos] = data

    # delete dictionary keys that have no data to update
    new_responses = [
        {k: v for k, v in j.items() if v and v != [[], [], []]} for j in new_response
    ]

    for k, response in enumerate(new_responses):
        members[k]["Resultados"].update(response)
        members[k]["Resultados"]["Satmul_Actualizado"] = dt.now().strftime("%d/%m/%Y")

    return members


def gather(LOG, members, docs_to_process, placas_to_process, responses):
    HEADERS = ["Satimp", "Brevete", "Revtec", "Sutran"]
    URLS = [
        "https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx",
        "https://licencias.mtc.gob.pe/#/index",
        "https://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx",
        "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/",
    ]
    scraper = [
        (scrapers.Satimp(None), docs_to_process),
        (scrapers.Brevete(None, URLS[1]), docs_to_process),
        (scrapers.Revtec(None), placas_to_process),
        (scrapers.Sutran(None), placas_to_process),
    ]
    threads = []
    for index, (url, scrap) in enumerate(zip(URLS, scraper)):
        _t = threading.Thread(
            target=full_update, args=(LOG, url, scrap[0], scrap[1], index, responses)
        )
        threads.append(_t)
        _t.start()

    for thread in threads:
        thread.join()

    # join responses in member list order
    new_response = [
        {"Satimp": {}, "Brevete": {}, "Revtec": [[], [], []], "Sutran": [[], [], []]}
        for _ in range(len(members))
    ]
    for response, header in zip(responses, HEADERS):
        for resp in response:
            rec, pos, data = resp
            if pos == -1:
                new_response[rec].update({header: data})
            else:
                new_response[rec][header][pos] = data

    # delete dictionary keys that have no data to update
    # TODO: Sutran?
    new_responses = [
        {k: v for k, v in j.items() if v and v != [[], [], []]} for j in new_response
    ]

    pprint(new_responses)

    for k, response in enumerate(new_responses):
        if response:
            members[k]["Resultados"].update(response)
            for header in HEADERS:
                members[k]["Resultados"][f"{header}_Actualizado"] = dt.now().strftime(
                    "%d/%m/%Y"
                )
    return members


def full_update(LOG, URL, scraper, data_to_process, index, responses):
    # define Chromedriver and open url for first time
    scraper.WEBD = ChromeUtils().init_driver(
        headless=True, verbose=False, maximized=True
    )
    scraper.WEBD.get(URL)
    time.sleep(3)

    # iterate on all records that require updating
    for k, data in enumerate(data_to_process):
        print(f"{index}: {(k+1)/len(data_to_process)*100:.1f}%")
        # get scraper data
        try:
            attempts, new_record = 0, ""
            while not new_record and attempts < 5:
                new_record, _ = scraper.browser(
                    doc_tipo=data[2], doc_num=data[3], placa=data[4]
                )
                responses[index].append((data[0], data[1], new_record))
                attempts += 1
        except KeyboardInterrupt:
            quit()
        except:
            LOG.warning(f"No proceso {data}")
            responses[index].append((data[0], data[1], ""))
