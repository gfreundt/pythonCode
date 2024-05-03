import sys
from gft_utils import GoogleUtils
from datetime import datetime as dt, timedelta as td
from jinja2 import Environment, FileSystemLoader
from pprint import pprint
import uuid


def get_alert_lists(members):

    BREVETE_CHECKPOINTS = (-30, -15, -5, 0)
    REVTEC_CHECKPOINTS = (-10, -5, 0)
    SOAT_CHECKPOINTS = (-10, -5, 0)
    CURRENTQ = (dt.now().month - 1) // 3 + 1

    welcome_list = []
    regular_list = []
    # warn list order: brevete, satimp, revtec, sutran, soat
    warn_list = [[] for _ in range(5)]
    warn_list = {i["Correlativo"]: [] for i in members}

    for j, member in enumerate(members):
        corr = member["Correlativo"]
        # WELCOME: select members who have never received email (skip all other lists)
        if not member["Envios"]["Bienvenida"]:
            welcome_list.append(j)
            continue

        # return welcome_list, [], []

        # REGULAR: similar structure to welcome email without introduction
        if dt.now() - dt.strptime(
            member["Envios"]["Bienvenida"]["fecha"], "%d/%m/%Y"
        ) >= td(days=30):
            regular_list.append(j)

        # WARNING: short email with warning that date is close or new record
        _m = member["Resultados"]
        _e = member["Envios"]

        # Brevete
        if (
            _m["Brevete"]
            and (dt.now() - dt.strptime(_m["Brevete"]["fecha_hasta"], "%d/%m/%Y")).days
            in BREVETE_CHECKPOINTS
        ):
            warn_list[corr].append(
                f"Licencia de Conducir {_m['Brevete']['numero']} vence el {_m['Brevete']['fecha_hasta']}."
            )

        # Satimp
        for m, codigo in enumerate(_m["Satimp"]):
            for n, deuda in enumerate(codigo["deudas"]):
                if int(deuda["ano"]) < dt.now().year or (
                    int(deuda["ano"]) == dt.now().year
                    and int(deuda["periodo"]) <= CURRENTQ
                ):
                    warn_list[corr].append(
                        f"Impuesto Vehicular SAT vencido o en periodo de pago."
                    )

        # Revtec
        if _m["Revtec"]:
            for revtec in _m["Revtec"]:
                # print(corr, revtec)
                if (
                    revtec
                    and (
                        (
                            dt.now() - dt.strptime(revtec[0]["fecha_hasta"], "%d/%m/%Y")
                        ).days
                    )
                    in REVTEC_CHECKPOINTS
                ):
                    warn_list[corr].append(
                        f"Revision Tecnica de Vehiculo Placa {revtec[0]['placa']} vence el {revtec[0]['fecha_hasta']}."
                    )

        # Sutran
        for k, sutran in enumerate(_m["Sutran"]):
            if (
                _e["Alertas"]["Sutran"]
                and dt.now() - dt.strptime(_e["Alertas"]["Sutran"][-1], "%d/%m/%Y")
                >= td(days=15)
                and len(_m["Alertas"]["Sutran"]) < 4
            ):

                warn_list[corr].append(
                    f"Multa Impaga en Sutran para Placa {_m['Datos']['Placas'][k]}\nDocumento: {sutran['Documento']}"
                )

        # Soat
        for soat in _m["Soat"]:
            if (
                soat
                and (dt.now() - dt.strptime(soat["fecha_fin"], "%d-%m-%Y")).days
                in SOAT_CHECKPOINTS
            ):
                warn_list[corr].append(
                    f"Certificado SOAT de Vehiculo Placa {soat['placa']} vence el {soat['fecha_fin']}."
                )

    pprint(warn_list)

    return welcome_list, regular_list, warn_list


def send_alerts(LOG, members, welcome_list, regular_list, warning_list, EMAIL):
    CURRENTQ = (dt.now().month - 1) // 3 + 1
    messages = []

    # Welcome Message
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("welcome.html")

    for mem, selected_member in enumerate(welcome_list):
        member = members[selected_member]

        _combina_deudas_sat = [
            i["deudas"] for i in member["Resultados"]["Satimp"] if i["deudas"]
        ]

        if _combina_deudas_sat:
            _combina_deudas_sat = [
                (int(i["ano"]), int(i["periodo"])) for i in _combina_deudas_sat[0] if i
            ]

        # create list of alerts (5 possible)
        _alertas = [
            (
                "Licencia de Conducir vencida o vence en menos de 30 días."
                if member["Resultados"]["Brevete"]
                and dt.strptime(
                    member["Resultados"]["Brevete"]["fecha_hasta"], "%d/%m/%Y"
                )
                - dt.now()
                <= td(days=30)
                else ""
            ),
            (
                "Al menos una Revision Tecnica vencida o vence en menos de 15 días."
                if any(
                    [
                        member["Resultados"]["Revtec"]
                        and dt.strptime(i[0]["fecha_hasta"], "%d/%m/%Y") - dt.now()
                        <= td(days=15)
                        for i in member["Resultados"]["Revtec"]
                        if i
                    ]
                )
                else ""
            ),
            (
                "SOAT vence en menos de 15 días."
                if any(
                    [
                        member["Resultados"]["Soat"]
                        and dt.strptime(i["fecha_fin"], "%d-%m-%Y") - dt.now()
                        <= td(days=15)
                        for i in member["Resultados"]["Soat"]
                        if i
                    ]
                )
                else ""
            ),
            (
                "Impuesto Vehicular SAT vencido o en periodo de pago."
                if any(
                    [
                        i[0] < dt.now().year
                        or (i[0] == dt.now().year and i[1] <= CURRENTQ)
                        for i in _combina_deudas_sat
                    ]
                )
                else ""
            ),
            (
                "Multa impaga en SUTRAN."
                if any(i for i in member["Resultados"]["Sutran"])
                else ""
            ),
        ]

        # add list of Alertas or "Ninguna" if empty
        _alertas = [i for i in _alertas if i]
        _info = {"alertas": _alertas if _alertas else ["Ninguna"]}

        # add randomly generated email ID, nombre and lista placas for opening text
        email_id = f"{member['Codigo']}|{str(uuid.uuid4())[-12:]}"
        lista_placas = ", ".join(member["Datos"]["Placas"])
        _info.update(
            {
                "nombre_usuario": member["Datos"]["Nombre y Apellido"],
                "codigo_correo": email_id,
                "lista_placas": lista_placas,
            }
        )

        # add revision tecnica information
        _revtecs = []
        for _m in member["Resultados"]["Revtec"]:
            if _m:
                _revtecs.append(
                    {
                        "certificadora": _m[0]["certificadora"].split("-")[-1][:35],
                        "placa": _m[0]["placa"],
                        "certificado": _m[0]["certificado"],
                        "fecha_desde": _m[0]["fecha_desde"],
                        "fecha_hasta": _m[0]["fecha_hasta"],
                        "resultado": _m[0]["resultado"],
                        "vigencia": _m[0]["vigencia"],
                    }
                )
        _info.update({"revtecs": _revtecs})

        # add brevete information
        _m = member["Resultados"]["Brevete"]
        if _m:
            _info.update(
                {
                    "brevete": {
                        "numero": _m["numero"],
                        "clase": _m["clase"],
                        "formato": _m["tipo"],
                        "fecha_desde": _m["fecha_expedicion"],
                        "fecha_hasta": _m["fecha_hasta"],
                        "restricciones": _m["restricciones"],
                        "local": _m["centro"],
                    }
                }
            )
        else:
            _info.update({"brevete": {}})

        # add SUTRAN information
        _sutran = []
        for k, _m in enumerate(member["Resultados"]["Sutran"]):
            if _m:
                _sutran.append(
                    {
                        "placa": member["Datos"]["Placas"][k],
                        "documento": _m["documento"] if _m else [],
                        "tipo": _m["tipo"] if _m else [],
                        "fecha_documento": _m["fecha_documento"] if _m else [],
                        "infraccion": (
                            f"{_m['codigo_infraccion']} - {_m['clasificacion']}"
                            if _m
                            else []
                        ),
                    }
                )
        _info.update({"sutrans": _sutran})

        # add SATIMP information
        _m = member["Resultados"]["Satimp"]
        if _m:
            _info.update(
                {
                    "satimp": {
                        "codigo": _m[0]["codigo"],
                        "deudas": _m[0]["deudas"],
                    }
                }
            )
        else:
            _info.update({"satimp": {}})

        # add SOAT information
        _soats = []
        for _m in member["Resultados"]["Soat"]:
            if _m:
                _soats.append(
                    {
                        "aseguradora": _m["aseguradora"],
                        "fecha_desde": _m["fecha_inicio"],
                        "fecha_hasta": _m["fecha_fin"],
                        "certificado": _m["certificado"],
                        "placa": _m["placa"],
                        "uso": _m["uso"],
                        "clase": _m["clase"],
                        "vigencia": _m["vigencia"],
                        "tipo": _m["tipo"],
                    }
                )
        _info.update({"soats": _soats})

        content = template.render(_info)
        messages.append(
            {
                "to": member["Datos"]["Correo"],
                "cc": "gabfre@gmail.com",
                "subject": "Bienvenido al Servicio de Alertas Perú",
                "body": content,
                "attachments": [],
            }
        )

        # update sent email information only if email switch on
        if EMAIL:
            members[selected_member]["Envios"]["Bienvenida"].update(
                {"fecha": dt.now().strftime("%d/%m/%Y"), "hash": email_id}
            )

        # log each new member
        LOG.info(
            f'Email included to {member["Datos"]["Nombre y Apellido"]} ({member["Datos"]["Documento Tipo"]}:{member["Datos"]["Número de Documento"]})'
        )

    # save in local file for debugging
    with open("messages.txt", "w") as file:
        for i in messages:
            file.write(i["body"])
            file.write("=" * 50)
        LOG.info("Local messages.txt file saved.")

    if EMAIL:
        try:
            GoogleUtils().send_gmail(
                fr="servicioalertaperu@gmail.com", messages=messages
            )
            LOG.info("Emails sent succesfully.")
        except:
            LOG.error('ERROR sending emails - Review "Envios" in database.')
    else:
        LOG.warning("Emails not sent. SWITCH OFF.")

    return members
