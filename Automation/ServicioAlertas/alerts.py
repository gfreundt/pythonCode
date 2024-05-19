import os
from gft_utils import GoogleUtils
from datetime import datetime as dt, timedelta as td
from jinja2 import Environment, FileSystemLoader
from pprint import pprint
import uuid


def date_check(fecha, delta):
    return dt.now() - dt.strptime(fecha, "%d/%m/%Y") >= td(days=delta)


def get_alert_lists(members):

    BREVETE_CHECKPOINTS = (-30, -15, -5, 0)
    REVTEC_CHECKPOINTS = (-10, -5, 0)
    SOAT_CHECKPOINTS = (-10, -5, 0)
    CURRENTQ = (dt.now().month - 1) // 3 + 1
    TODAY_STR = dt.now().strftime("%d/%m/%Y")

    timestamps = []
    welcome_list = []
    regular_list = []
    warning_list = []

    for j, member in enumerate(members):
        corr = member["Correlativo"]
        email_id = f"{member['Codigo']}|{str(uuid.uuid4())[-12:]}"
        # WELCOME: select members who have never received email (skip all other lists)
        if not member["Envios"]["Bienvenida"]:
            welcome_list.append(j)
            continue

        # REGULAR: similar structure to welcome email without introduction
        if (
            not member["Envios"]["Regular"]
            and date_check(member["Envios"]["Bienvenida"]["fecha"], delta=30)
        ) or (
            member["Envios"]["Regular"]
            and date_check(member["Envios"]["Regular"][-1]["fecha"], delta=30)
        ):
            regular_list.append(j)

        # WARNING: short email with warning that date is close or new record
        _m = member["Resultados"]
        _e = member["Envios"]
        warning = []

        # Brevete
        if (
            _m["Brevete"]
            and (dt.now() - dt.strptime(_m["Brevete"]["fecha_hasta"], "%d/%m/%Y")).days
            in BREVETE_CHECKPOINTS
        ):
            warning.append(
                f"Licencia de Conducir {_m['Brevete']['numero']} vence el {_m['Brevete']['fecha_hasta']}."
            )
            timestamps.append(
                (
                    j,
                    "Brevete",
                    {
                        "documento": _m["Brevete"]["numero"],
                        "fecha": TODAY_STR,
                        "hash": email_id,
                    },
                )
            )

        """
        # Satimp
        for satimp in _m["Satimp"]:
            for deuda in satimp["deudas"]:
                if not _e["Alertas"]["Satimp"] or (
                    _e["Alertas"]["Satimp"]
                    and date_check(_e["Alertas"]["Satimp"][-1]["fecha"], delta=15)
                ):
                    if int(deuda["ano"]) < dt.now().year or (
                        int(deuda["ano"]) == dt.now().year
                        and int(deuda["periodo"]) < CURRENTQ
                    ):
                        warning.append(
                            f"Impuesto Vehicular SAT vencido (Periodo {deuda['ano']}-{deuda['periodo']})\nDocumento: {deuda['documento']} de S/{deuda['total_a_pagar']}."
                        )
                        timestamps.append(
                            (
                                j,
                                "Satimp",
                                {
                                    "documento": deuda["documento"],
                                    "fecha": TODAY_STR,
                                    "hash": email_id,
                                },
                            )
                        )

                    elif (
                        int(deuda["ano"]) == dt.now().year
                        and int(deuda["periodo"]) == CURRENTQ
                    ):
                        warning.append(
                            f"Impuesto Vehicular SAT en periodo de pago (Periodo: {deuda['ano']}-{deuda['periodo']})\nDocumento: {deuda['documento']} de S/{deuda['total_a_pagar']}."
                        )
                        timestamps.append(
                            (
                                "Satimp",
                                {
                                    "documento": deuda["documento"],
                                    "fecha": TODAY_STR,
                                    "hash": email_id,
                                },
                            )
                        )
        """
        # Revtec
        if _m["Revtec"]:
            for revtec in _m["Revtec"]:
                if (
                    revtec
                    and (
                        (
                            dt.now() - dt.strptime(revtec[0]["fecha_hasta"], "%d/%m/%Y")
                        ).days
                    )
                    in REVTEC_CHECKPOINTS
                ):
                    warning.append(
                        f"Revision Tecnica de Vehiculo Placa {revtec[0]['placa']} vence el {revtec[0]['fecha_hasta']}."
                    )
                    timestamps.append(
                        (
                            j,
                            "Revtec",
                            {
                                "documento": revtec[0]["certificado"],
                                "fecha": TODAY_STR,
                                "hash": email_id,
                            },
                        )
                    )
        """
        # Sutran
        # TODO: filter by codigo (SATIMP too!)
        for k, sutran in enumerate(_m["Sutran"]):
            if sutran and (
                not _e["Alertas"]["Sutran"]
                or (
                    _e["Alertas"]["Sutran"]
                    and date_check(_e["Alertas"]["Sutran"][-1]["fecha"], delta=15)
                )
                and len(_m["Alertas"]["Sutran"]) < 4
            ):

                warning.append(
                    f"Multa Impaga en Sutran para Placa {member['Datos']['Placas'][k]}.\nDocumento: {sutran['documento']}."
                )
                timestamps.append(
                    (
                        j,
                        "Sutran",
                        {
                            "documento": sutran["documento"],
                            "fecha": TODAY_STR,
                            "hash": email_id,
                        },
                    )
                )
        """
        # Soat
        for soat in _m["Soat"]:
            if (
                soat
                and (dt.now() - dt.strptime(soat["fecha_fin"], "%d-%m-%Y")).days
                in SOAT_CHECKPOINTS
            ):
                warning.append(
                    f"Certificado SOAT de Vehiculo Placa {soat['placa']} vence el {soat['fecha_fin']}."
                )
                timestamps.append(
                    (
                        j,
                        "Soat",
                        {
                            "documento": soat["certificado"],
                            "fecha": TODAY_STR,
                            "hash": email_id,
                        },
                    )
                )

        # consolidate warnings by member
        if warning:
            warning_list.append((corr, warning))

    return welcome_list, regular_list, warning_list, timestamps


def send_alerts(
    LOG, members, welcome_list, regular_list, warning_list, EMAIL, timestamps
):

    messages = []

    # Welcome / Regular Messages
    environment = Environment(loader=FileSystemLoader("templates/"))
    template_welcome = environment.get_template("bienvenida.html")
    template_regular = environment.get_template("regular.html")
    template_alertas = environment.get_template("alerta.html")

    # compose welcome messages and add to mailing list
    for selected_member in welcome_list:
        member = members[selected_member]
        email_id = f"{member['Codigo']}|{str(uuid.uuid4())[-12:]}"
        content = compose_message1(member, template_welcome, email_id)

        messages.append(
            {
                "to": member["Datos"]["Correo"],
                "cc": "gabfre@gmail.com",
                "subject": "Bienvenido al Servicio de Alertas Perú",
                "body": content,
                "attachments": [],
            }
        )
        LOG.info(
            f'Welcome email to: {member["Datos"]["Nombre y Apellido"]} ({member["Datos"]["Documento Tipo"]}:{member["Datos"]["Número de Documento"]})'
        )

        # update sent email timestamps (if email switch on)
        if EMAIL:
            members[selected_member]["Envios"]["Bienvenida"].update(
                {"fecha": dt.now().strftime("%d/%m/%Y"), "hash": email_id}
            )

    # compose regular messages and add to mailing list
    for selected_member in regular_list:
        member = members[selected_member]
        email_id = f"{member['Codigo']}|{str(uuid.uuid4())[-12:]}"
        content = compose_message1(member, template_regular, email_id)

        messages.append(
            {
                "to": member["Datos"]["Correo"],
                "cc": "gabfre@gmail.com",
                "subject": "Tu Correo Mensual del Servicio de Alertas Perú",
                "body": content,
                "attachments": [],
            }
        )
        LOG.info(
            f'Regular email to: {member["Datos"]["Nombre y Apellido"]} ({member["Datos"]["Documento Tipo"]}:{member["Datos"]["Número de Documento"]})'
        )

        # update sent email timestamps (if email switch on)
        if EMAIL:
            members[selected_member]["Envios"]["Regular"].append(
                {"fecha": dt.now().strftime("%d/%m/%Y"), "hash": email_id}
            )

    # compose alerta messages and add to mailing list
    for selected_member, warnings in warning_list:
        member = members[selected_member]
        email_id = f"{member['Codigo']}|{str(uuid.uuid4())[-12:]}"
        content = compose_message2(member, warnings, template_alertas, email_id)

        messages.append(
            {
                "to": member["Datos"]["Correo"],
                "cc": "gabfre@gmail.com",
                "subject": "Aviso del Servicio de Alertas Perú",
                "body": content,
                "attachments": [],
            }
        )
        LOG.info(
            f'Regular email to: {member["Datos"]["Nombre y Apellido"]} ({member["Datos"]["Documento Tipo"]}:{member["Datos"]["Número de Documento"]})'
        )
    # update timestamps for all alerts sent (if email switch on)
    if EMAIL:
        for selected_member, alert_category, alert_info in timestamps:
            members[selected_member]["Envios"]["Alertas"][alert_category].append(
                alert_info
            )

    # save local htmls for debugging
    for msg, message in enumerate(messages):
        with open(
            os.path.join(os.curdir, "other", f"message{msg:02d}.html"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(message["body"])

    # send emails if switch on
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


def compose_message1(member, template, email_id):
    CURRENTQ = (dt.now().month - 1) // 3 + 1
    _combina_deudas_sat = [
        i["deudas"] for i in member["Resultados"]["Satimp"] if i["deudas"]
    ]

    if _combina_deudas_sat:
        _combina_deudas_sat = [
            (int(i["ano"]), int(i["periodo"])) for i in _combina_deudas_sat[0] if i
        ]

    # create list of alerts
    _alertas = [
        (
            "Licencia de Conducir vencida o vence en menos de 30 días."
            if member["Resultados"]["Brevete"]
            and dt.strptime(member["Resultados"]["Brevete"]["fecha_hasta"], "%d/%m/%Y")
            - dt.now()
            <= td(days=30)
            else ""
        ),
        (
            "Al menos una Revision Técnica vencida o vence en menos de 15 días."
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
            "Al menos un certificado SOAT vencido o vence en menos de 15 días."
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
                    i[0] < dt.now().year or (i[0] == dt.now().year and i[1] <= CURRENTQ)
                    for i in _combina_deudas_sat
                ]
            )
            else ""
        ),
        (
            "Al menos una multa impaga en SUTRAN."
            if any(i for i in member["Resultados"]["Sutran"])
            else ""
        ),
    ]

    # add list of Alertas or "Ninguna" if empty
    _alertas = [i for i in _alertas if i]
    _info = {"alertas": _alertas if _alertas else ["Ninguna"]}

    # add randomly generated email ID, nombre and lista placas for opening text
    _info.update(
        {
            "nombre_usuario": member["Datos"]["Nombre y Apellido"],
            "codigo_correo": email_id,
            "lista_placas": ", ".join(member["Datos"]["Placas"]),
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
    _s = []
    if _m:
        for satimp in _m:
            _s.append(
                {
                    "codigo": satimp["codigo"],
                    "deudas": satimp["deudas"],
                }
            )
        _info.update({"satimps": _s})
    else:
        _info.update({"satimps": {}})

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

    # pprint(_info)

    return template.render(_info)


def compose_message2(member, warnings, template, email_id):

    _info = {
        "nombre_usuario": member["Datos"]["Nombre y Apellido"],
        "codigo_correo": email_id,
        "lista_placas": ", ".join(member["Datos"]["Placas"]),
    }

    # add SATIMP information
    _info.update({"alertas": warnings})

    return template.render(_info)
