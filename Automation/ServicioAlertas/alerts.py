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
		            WHERE fecha >= DATETIME('now','localtime','-1 month')
			        AND (IdTipoMensaje_FK = 12 OR IdTipoMensaje_FK = 13)
                """
        # filter this list to avoid repeating with welcome list
        self.cursor.execute(cmd)
        self.regular_list = [
            i[0] for i in self.cursor.fetchall() if i[0] not in self.welcome_list
        ]

        # 3. generate WARNING list (only expiration records that meet date criteria)

        # TODO: make dates dynamic - low priority
        cmd = f"""  DROP TABLE IF EXISTS temp;
                    CREATE TABLE temp (CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo);

                    INSERT INTO temp (CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo)
                    SELECT CodMember, NombreCompleto, Placa, FechaHasta, TipoAlerta, Correo FROM members
                    JOIN (
                        SELECT * FROM placas 
                        JOIN (
                        SELECT idplaca_FK, FechaHasta, "SOAT" AS TipoAlerta FROM soats WHERE DATETIME('now', 'localtime', '10 days') = FechaHasta OR DATE('now', '5 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta
                        UNION
                        SELECT idplaca_FK, FechaHasta, "REVTEC" FROM revtecs WHERE DATETIME('now', 'localtime','30 days') = FechaHasta OR DATE('now', '15 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta)
                        ON idplaca = IdPlaca_FK)
                    ON IdMember = IdMember_FK;

                    INSERT INTO temp (CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo)
                    SELECT CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo from members 
                        JOIN (
                            SELECT IdMember_FK, FechaHasta, "BREVETE" AS TipoAlerta FROM brevetes WHERE DATETIME('now', 'localtime', '60 days') = FechaHasta OR DATE('now', '30 days')= FechaHasta OR DATE('now', '0 days')= FechaHasta
						UNION
							SELECT IdMember_FK, FechaHasta, "SATIMP" AS TipoAlerta FROM satimpDeudas 
							JOIN
							(SELECT * FROM satimpCodigos)
							ON IdCodigo_FK = IdCodigo
							WHERE DATE('now', '10 days') = FechaHasta OR DATE('now', '5 days') = FechaHasta OR DATETIME('now', 'localtime', '0 days') = FechaHasta)
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

        # loop all members in welcome list, compose message
        for IdMember in self.welcome_list:
            self.cursor.execute(f"SELECT * FROM members WHERE IdMember = {IdMember}")
            member = self.cursor.fetchone()

            self.cursor.execute(
                f"SELECT TipoAlerta, Placa FROM _expira30dias WHERE IdMember = {IdMember}"
            )
            _a = self.cursor.fetchall()
            alertas = {i[0]: i[1] for i in _a if i} if _a else {}
            self.cursor.execute(
                f"SELECT Placa FROM placas WHERE IdMember_FK = {IdMember}"
            )
            placas = [i[0] for i in self.cursor.fetchall()]

            email_id = f"{member[1]}|{str(uuid.uuid4())[-12:]}"
            content = self.compose_message(
                member, template_welcome, email_id, alertas, placas
            )

            messages.append(
                {
                    "to": member[6],
                    "bcc": "gabfre@gmail.com",
                    "subject": "Bienvenido al Servicio de Alertas Perú",
                    "body": content,
                    "attachments": [],
                    "tipoMensaje": 12,
                    "idMember": int(IdMember),
                    "timestamp": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hashcode": email_id,
                }
            )

        # compose regular messages and add to mailing list
        for IdMember in self.regular_list:
            self.cursor.execute(f"SELECT * FROM members WHERE IdMember = {IdMember}")
            member = self.cursor.fetchone()

            self.cursor.execute(
                f"SELECT TipoAlerta, Placa FROM _expira30dias WHERE IdMember = {IdMember}"
            )
            _a = self.cursor.fetchall()
            alertas = {i[0]: i[1] for i in _a if i} if _a else {}
            self.cursor.execute(
                f"SELECT Placa FROM placas WHERE IdMember_FK = {IdMember}"
            )
            placas = [i[0] for i in self.cursor.fetchall()]

            email_id = f"{member[1]}|{str(uuid.uuid4())[-12:]}"
            content = self.compose_message(
                member, template_regular, email_id, alertas, placas
            )

            messages.append(
                {
                    "to": member[6],
                    "bcc": "gabfre@gmail.com",
                    "subject": "Informe Mensual del Servicio de Alertas Perú",
                    "body": content,
                    "attachments": [],
                    "tipoMensaje": 13,
                    "idMember": int(IdMember),
                    "timestamp": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hashcode": email_id,
                }
            )
            self.LOG.info(f"Welcome email to: {member[6]} ({member[3]}:{member[4]})")

        # # compose alerta messages and add to mailing list
        # for selected_member, warnings in warning_list:
        #     member = members[selected_member]
        #     email_id = f"{member['Codigo']}|{str(uuid.uuid4())[-12:]}"
        #     content = compose_message2(member, warnings, template_alertas, email_id)

        #     messages.append(
        #         {
        #             "to": member["Datos"]["Correo"],
        #             "cc": "gabfre@gmail.com",
        #             "subject": "Aviso del Servicio de Alertas Perú",
        #             "body": content,
        #             "attachments": [],
        #         }
        #     )
        #     LOG.info(
        #         f'Regular email to: {member["Datos"]["Nombre y Apellido"]} ({member["Datos"]["Documento Tipo"]}:{member["Datos"]["Número de Documento"]})'
        #     )

        # save local html for debugging
        for msg, message in enumerate(messages):
            with open(
                os.path.join(os.curdir, "other", f"message{msg:03d}.html"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(message["body"])

        # send emails if switch on
        if EMAIL:
            try:
                # results = [True, True]
                results = GoogleUtils().send_gmail(
                    fr="servicioalertaperu@gmail.com", messages=messages
                )
            except Exception:
                self.LOG.error("ERROR sending emails")

            # update mensaje and mensajeContenido tables depending on success reply from email attempt
            table, fields = "mensajes", ("IdMember_FK", "Fecha", "HashCode")
            table2, fields2 = "mensajeContenidos", ("IdMensaje_FK", "IdTipoMensaje_FK")
            for result, message in zip(results, messages):
                if result:
                    self.LOG.info(
                        f"Email sent to {message['to']} (IdMember = {message['idMember']}). Type: {message['tipoMensaje']}"
                    )
                    # populate mensaje tables
                    cmd = self.sql(table, fields)
                    values = (
                        message["idMember"],
                        message["timestamp"],
                        message["hashcode"],
                    )
                    self.cursor.execute(cmd, values)
                    # get just crated record
                    self.cursor.execute(
                        f"SELECT * FROM {table} WHERE HashCode = '{message['hashcode']}'"
                    )
                    _x = self.cursor.fetchone()
                    cmd = self.sql(table2, fields2)
                    values = _x[0], message["tipoMensaje"]
                    self.cursor.execute(cmd, values)
                else:
                    self.LOG.warning(f"ERROR sending email to {message['to']}.")
            self.conn.commit()

        else:
            self.LOG.warning("Emails not sent. SWITCH OFF.")

    def compose_message(self, member, template, email_id, alertas, placas):
        _txtal = []
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
                    _txtal.append("Multa impaga en Municipalidad del Callao.")

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
            f"SELECT * FROM sutrans JOIN placas ON IdPlaca = IdPlaca_FK WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
        )
        for _m in self.cursor.fetchall():
            if _m:
                _sutran.append(
                    {
                        "placa": _m[10],
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
            _v.append({"codigo": satimp[2], "deudas": _s})
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
                    "certificado": _m[6],
                    "placa": _m[5],
                    "uso": _m[7],
                    "clase": _m[8],
                    "vigencia": _m[9],
                    "tipo": _m[10],
                }
            )
        _info.update({"soats": _soats})

        # add SATMUL information
        _satmuls = []
        self.cursor.execute(
            f"SELECT * FROM satmuls WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
        )
        for _m in self.cursor.fetchall():
            _satmuls.append(
                {
                    "placa": _m[2],
                    "reglamento": _m[3],
                    "falta": _m[4],
                    "documento": _m[5],
                    "fecha_emision": _m[6],
                    "importe": _m[7],
                    "gastos": _m[8],
                    "descuento": _m[9],
                    "deuda": _m[10],
                    "estado": _m[11],
                    "licencia": _m[12],
                }
            )
        _info.update({"satmuls": _satmuls})

        return template.render(_info)
