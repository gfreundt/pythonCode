import os
from gft_utils import GoogleUtils
from datetime import datetime as dt, timedelta as td
from jinja2 import Environment, FileSystemLoader
from pprint import pprint
import uuid


def date_check(fecha, delta):
    return dt.now() - dt.strptime(fecha, "%d/%m/%Y") >= td(days=delta)


class Alerts:

    def __init__(self, LOG, members) -> None:
        self.LOG = LOG
        self.cursor = members.cursor
        self.conn = members.conn
        self.sql = members.sql

    def get_alert_lists(self):

        # 1. generate BIENVENIDA list (records with no previous BIENVENIDA email)
        cmd = """SELECT IdMember FROM members
                EXCEPT
                SELECT IdMember FROM (
                SELECT mensajes.IdMember_FK FROM mensajes JOIN mensajeContenidos ON mensajes.IdMensaje = mensajeContenidos.IdMensaje_FK
                WHERE IdTipoMensaje_FK = 12)
                JOIN members
                ON members.IdMember = IdMember_FK
                """

        self.cursor.execute(cmd)
        self.welcome_list = [i[0] for i in self.cursor.fetchall()]

        # 2. generate REGULAR list (records with previous REGULAR or BIENVENIDA email at least 1 month ago)
        cmd = """SELECT IdMember FROM members
                EXCEPT
	            SELECT IdMember_FK FROM mensajes
		            JOIN mensajeContenidos
		            ON IdMensaje = IdMensaje_FK
		            WHERE fecha >= date('now','-1 month')
			        AND (IdTipoMensaje_FK = 12 OR IdTipoMensaje_FK = 13)
                """

        self.cursor.execute(cmd)
        self.regular_list = [i[0] for i in self.cursor.fetchall()]

        # 3. generate WARNING list (only expiration records that meet date criteria)

        # TODO: make dates dynamic - low priority
        cmd = f"""  DROP TABLE IF EXISTS temp;
                    CREATE TABLE temp (CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo);

                    INSERT INTO temp (CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo)
                    SELECT CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo FROM members
                    JOIN (
                        SELECT * FROM placas 
                        JOIN (
                        SELECT idplaca_FK, FechaHasta, "SOAT" AS TipoAlerta FROM soats WHERE DATE('now', '10 days') = FechaHasta OR DATE('now', '5 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta
                        UNION
                        SELECT idplaca_FK, FechaHasta, "REVTEC" FROM revtecs WHERE DATE('now', '30 days') = FechaHasta OR DATE('now', '15 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta)
                        ON idplaca = IdPlaca_FK)
                    ON IdMember = IdMember_FK;

                    INSERT INTO temp (CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo)
                    SELECT CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo from members 
                        JOIN (
                            SELECT IdMember_FK, FechaHasta, "BREVETE" AS TipoAlerta FROM brevetes WHERE DATE('now', '60 days') = FechaHasta OR DATE('now', '30 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta
						UNION
							SELECT IdMember_FK, FechaHasta, "SATIMP" AS TipoAlerta FROM satimpDeudas 
							JOIN
							(SELECT * FROM satimpCodigos)
							ON IdCodigo_FK = IdCodigo
							WHERE DATE('now', '10 days') = FechaHasta OR DATE('now', '5 days') = FechaHasta OR DATE('now', '0 days') = FechaHasta)
                    ON IdMember = IdMember_FK;"""

        self.cursor.executescript(cmd)
        self.cursor.execute("SELECT * FROM temp")
        self.warning_list = self.cursor.fetchall()

    def send_alerts(self, EMAIL=False):
        messages = []

        # Welcome / Regular Messages
        environment = Environment(loader=FileSystemLoader("templates/"))
        template_welcome = environment.get_template("bienvenida.html")
        template_regular = environment.get_template("regular.html")
        template_alertas = environment.get_template("alerta.html")

        # compose welcome messages and add to mailing list

        # create table with all members that have anything expired or expiring within 30 days
        cmd = f"""DROP TABLE IF EXISTS _expira30dias;
                    CREATE TABLE _expira30dias (IdMember, CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo);

                    INSERT INTO _expira30dias (IdMember, CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo)
                    SELECT IdMember, CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo FROM members
                    JOIN (
                        SELECT * FROM placas 
                        JOIN (
                        SELECT idplaca_FK, FechaHasta, "SOAT" AS TipoAlerta FROM soats WHERE DATE('now', '30 days') >= FechaHasta
                        UNION
                        SELECT idplaca_FK, FechaHasta, "REVTEC" FROM revtecs WHERE DATE('now', '30 days') >= FechaHasta
                        UNION 
                        SELECT idplaca_FK, "", "SUTRAN" FROM sutrans
                        UNION 
                        SELECT idplaca_FK, "", "SATMUL" FROM satmuls)
                        ON idplaca = IdPlaca_FK)
                    ON IdMember = IdMember_FK;

                    INSERT INTO _expira30dias (IdMember, CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo)
                    SELECT IdMember, CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo from members 
                        JOIN (
                            SELECT IdMember_FK, FechaHasta, "BREVETE" AS TipoAlerta FROM brevetes WHERE DATE('now', '30 days') >= FechaHasta OR DATE('now', '30 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta
						UNION
							SELECT IdMember_FK, FechaHasta, "SATIMP" AS TipoAlerta FROM satimpDeudas 
							JOIN
							(SELECT * FROM satimpCodigos)
							ON IdCodigo_FK = IdCodigo
							WHERE DATE('now', '30 days') >= FechaHasta)
                    ON IdMember = IdMember_FK"""

        self.cursor.executescript(cmd)

        # loop all members in welcome list, compose message
        for IdMember in self.welcome_list:
            self.cursor.execute(f"SELECT * FROM members WHERE IdMember = {IdMember}")
            member = self.cursor.fetchone()

            self.cursor.execute(
                f"SELECT TipoAlerta, Placa FROM _expira30dias WHERE IdMember = {IdMember}"
            )
            _a = self.cursor.fetchall()
            if _a:
                alertas = {i[0]: i[1] for i in _a if i}
            self.cursor.execute(
                f"SELECT Placa FROM placas WHERE IdMember_FK = {IdMember}"
            )
            placas = [i[0] for i in self.cursor.fetchall()]

            email_id = f"{member[1]}|{str(uuid.uuid4())[-12:]}"
            content = self.compose_message3(
                member, template_welcome, email_id, alertas, placas
            )

            messages.append(
                {
                    "to": member[6],
                    "cc": "gabfre@gmail.com",
                    "subject": "Bienvenido al Servicio de Alertas Perú",
                    "body": content,
                    "attachments": [],
                }
            )
            self.LOG.info(f"Welcome email to: {member[6]} ({member[3]}:{member[4]})")

            # update sent email timestamps (if email switch on)
            if EMAIL:
                members[selected_member]["Envios"]["Bienvenida"].update(
                    {"fecha": dt.now().strftime("%d/%m/%Y"), "hash": email_id}
                )

        # compose regular messages and add to mailing list
        """for selected_member in regular_list:
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
                )"""

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
                and dt.strptime(
                    member["Resultados"]["Brevete"]["fecha_hasta"], "%d/%m/%Y"
                )
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
                        i[0] < dt.now().year
                        or (i[0] == dt.now().year and i[1] <= CURRENTQ)
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

    def compose_message3(self, member, template, email_id, alertas, placas):

        _txtal = []
        print(alertas)

        # create list of alerts
        for i in alertas:
            match i:
                case "BREVETE":
                    _txtal.append(
                        "Licencia de Conducir vencida o vence en menos de 30 días."
                    )
                case "SOAT":
                    _txtal.append(
                        f"Certificado SOAT de placa {alertas['SOAT']} vencido o vence en menos de 30 días."
                    )
                case "SATIMP":
                    _txtal.append(
                        "Impuesto Vehicular SAT vencido o vence en menos de 30 dias."
                    )
                case "REVTEC":
                    _txtal.append(
                        f"Revision Técnica de placa {alertas['REVTEC']} vencida o vence en menos de 30 días."
                    )
                case "SUTRAN":
                    _txtal.append(
                        f"Multa impaga en SUTRAN para placa {alertas['SUTRAN']}."
                    )
                case "SATMUL":
                    _txtal.append(f"Multa impaga en SAT para {alertas['SATMUL']}.")
                case "CALLAOMULTA":
                    _txtal.append(
                        "Al menos una multa impaga en Municipalidad del Callao."
                    )

        print(_txtal)

        # add list of Alertas or "Ninguna" if empty
        _info = {"alertas": _txtal if _txtal else ["Ninguna"]}

        # add randomly generated email ID, nombre and lista placas for opening text
        _info.update(
            {
                "nombre_usuario": member[2],
                "codigo_correo": email_id,
                "lista_placas": ", ".join(placas),
            }
        )

        # add revision tecnica information
        self.cursor.execute(
            f"SELECT * FROM revtecs WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
        )
        _revtecs = []
        for _m in self.cursor.fetchall():
            _revtecs.append(
                {
                    "certificadora": _m[2].split("-")[-1][:35],
                    "placa": _m[3],
                    "certificado": _m[4],
                    "fecha_desde": _m[5],
                    "fecha_hasta": _m[6],
                    "resultado": _m[7],
                    "vigencia": _m[8],
                }
            )
        _info.update({"revtecs": _revtecs})

        # add brevete information
        self.cursor.execute(
            f"SELECT * FROM brevetes WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
        )
        _m = self.cursor.fetchone()
        if _m:
            _info.update(
                {
                    "brevete": {
                        "numero": _m[3],
                        "clase": _m[2],
                        "formato": _m[4],
                        "fecha_desde": _m[5],
                        "fecha_hasta": _m[7],
                        "restricciones": _m[6],
                        "local": _m[8],
                    }
                }
            )
        else:
            _info.update({"brevete": {}})

        # add SUTRAN information
        _sutran = []
        self.cursor.execute(
            f"SELECT * FROM sutrans WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
        )
        for _m in self.cursor.fetchall():
            if _m:
                _sutran.append(
                    {
                        "placa": _m[1],
                        "documento": _m[2],
                        "tipo": _m[3],
                        "fecha_documento": _m[4],
                        "infraccion": (f"{_m[5]} - {_m[6]}"),
                    }
                )
            _info.update({"sutrans": _sutran})

        # add SATIMP information
        self.cursor.execute(
            f"SELECT * FROM satimpCodigos WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
        )

        _v = []
        for satimp in self.cursor.fetchall():
            self.cursor.execute(
                f"SELECT * FROM satimpDeudas WHERE IdCodigo_FK = {satimp[0]}"
            )
            _s = []
            for _x in self.cursor.fetchall():
                _s.append(
                    {
                        "ano": _x[2],
                        "periodo": _x[3],
                        "doc_num": _x[4],
                        "total_a_pagar": _x[5],
                    }
                )
            _v.append({"codigo": satimp[2]})
        _info.update({"satimps": _v})

        # add SOAT information
        _soats = []
        self.cursor.execute(
            f"SELECT * FROM soats WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
        )
        for _m in self.cursor.fetchall():
            _soats.append(
                {
                    "aseguradora": _m[2],
                    "fecha_desde": _m[3],
                    "fecha_hasta": _m[4],
                    "certificado": _m[5],
                    "placa": _m[6],
                    "uso": _m[7],
                    "clase": _m[8],
                    "vigencia": _m[9],
                    "tipo": _m[10],
                }
            )
        _info.update({"soats": _soats})

        # pprint(_info)

        return template.render(_info)
