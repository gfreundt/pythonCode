import os
from gft_utils import GoogleUtils
from datetime import datetime as dt, timedelta as td
from jinja2 import Environment, FileSystemLoader
import uuid


def date_check(fecha, delta):
    return dt.now() - dt.strptime(fecha, "%d/%m/%Y") >= td(days=delta)


def date_friendly(fecha, delta=False):
    _months = (
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Oct",
        "Nov",
        "Dic",
    )
    _day = fecha[8:]
    _month = _months[int(fecha[5:7]) - 1]
    _year = fecha[:4]
    _deltatxt = ""
    if delta:
        _delta = int((dt.strptime(fecha, "%Y-%m-%d") - dt.now()).days)
        _deltatxt = f"[ {_delta:,} días ]" if _delta > 0 else "[ VENCIDO ]"
    return f"{_day}-{_month}-{_year} {_deltatxt}"


class Messages:

    def __init__(self, LOG, members, MONITOR) -> None:
        self.LOG = LOG
        self.MONITOR = MONITOR
        self.cursor = members.cursor
        self.conn = members.conn
        self.sql = members.sql
        self.welcome_list, self.regular_list = [], []

    def get_msg_lists(self):

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

    def send_msgs(self, EMAIL=False):
        messages = []

        # Welcome / Regular Messages
        environment = Environment(loader=FileSystemLoader("templates/"))
        template_welcome = environment.get_template("bienvenida.html")
        template_regular = environment.get_template("regular.html")

        # loop all members in welcome list
        for IdMember in self.welcome_list:
            self.cursor.execute(f"SELECT * FROM members WHERE IdMember = {IdMember}")
            member = self.cursor.fetchone()

            self.cursor.execute(
                f"SELECT TipoAlerta, Placa, Vencido FROM _expira30dias WHERE IdMember = {IdMember}"
            )
            _a = self.cursor.fetchall()
            alertas = [[i[0], i[1], i[2]] for i in _a if i] if _a else []
            self.cursor.execute(
                f"SELECT Placa FROM placas WHERE IdMember_FK = {IdMember}"
            )
            placas = [i[0] for i in self.cursor.fetchall()]

            email_id = f"{member[1]}|{str(uuid.uuid4())[-12:]}"
            content, attachments, numalertas, msgrecords = self.compose_message(
                member, template_welcome, email_id, alertas, placas
            )
            _subj = (
                f"{numalertas} ALERTAS"
                if numalertas > 1
                else f"1 ALERTA" if numalertas == 1 else "SIN ALERTAS"
            )
            messages.append(
                {
                    "to": member[6],
                    "bcc": "gabfre@gmail.com",
                    "subject": f"Bienvenido al Servicio de Alertas Perú ({_subj})",
                    "body": content,
                    "attachments": attachments,
                    "tipoMensajes": [12] + msgrecords,
                    "idMember": int(IdMember),
                    "timestamp": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hashcode": email_id,
                }
            )

            self.LOG.info(
                f"Welcome message crafted (not sent) to: {member[6]} ({member[3]}:{member[4]})"
            )

        # loop all members in regular list
        for IdMember in self.regular_list:

            self.cursor.execute(f"SELECT * FROM members WHERE IdMember = {IdMember}")
            member = self.cursor.fetchone()

            self.cursor.execute(
                f"SELECT TipoAlerta, Placa,Vencido FROM _expira30dias WHERE IdMember = {IdMember}"
            )
            _a = self.cursor.fetchall()
            alertas = [[i[0], i[1], i[2]] for i in _a if i] if _a else []
            self.cursor.execute(
                f"SELECT Placa FROM placas WHERE IdMember_FK = {IdMember}"
            )
            placas = [i[0] for i in self.cursor.fetchall()]

            email_id = f"{member[1]}|{str(uuid.uuid4())[-12:]}"
            content, attachments, numalertas, msgrecords = self.compose_message(
                member, template_regular, email_id, alertas, placas
            )
            _subj = (
                f"{numalertas} ALERTAS"
                if numalertas > 1
                else f"1 ALERTA" if numalertas == 1 else "SIN ALERTAS"
            )

            messages.append(
                {
                    "to": member[6],
                    "bcc": "gabfre@gmail.com",
                    "subject": f"Informe Mensual del Servicio de Alertas Perú ({_subj})",
                    "body": content,
                    "attachments": attachments,
                    "tipoMensajes": [13] + msgrecords,
                    "idMember": int(IdMember),
                    "timestamp": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hashcode": email_id,
                }
            )
            self.LOG.info(
                f"Regular message crafted (not sent) to: {member[6]} ({member[3]}:{member[4]})"
            )

        # erase html from previous iterations
        for existing in os.listdir(os.path.join(os.curdir, "templates")):
            if "message" in existing:
                os.remove(os.path.join(os.curdir, "templates", existing))

        self.MONITOR.add_widget(len(messages), type=2)

        for msg, message in enumerate(messages):
            # save local html for debugging
            with open(
                os.path.join(os.curdir, "templates", f"message{msg:03d}.html"),
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
            except KeyboardInterrupt:  # Exception:
                self.LOG.error("ERROR sending emails")

            # update mensaje and mensajeContenido tables depending on success reply from email attempt
            table, fields = "mensajes", ("IdMember_FK", "Fecha", "HashCode")
            table2, fields2 = "mensajeContenidos", ("IdMensaje_FK", "IdTipoMensaje_FK")
            for result, message in zip(results, messages):
                if result:
                    self.LOG.info(
                        f"Email sent to {message['to']} (IdMember = {message['idMember']}). Type: {message['tipoMensajes']}"
                    )
                    # populate mensaje tables
                    cmd = self.sql(table, fields)
                    values = (
                        message["idMember"],
                        message["timestamp"],
                        message["hashcode"],
                    )
                    self.cursor.execute(cmd, values)
                    # get just crafted record
                    self.cursor.execute(
                        f"SELECT * FROM {table} WHERE HashCode = '{message['hashcode']}'"
                    )
                    _x = self.cursor.fetchone()
                    for msgtype in message["tipoMensajes"]:
                        cmd = self.sql(table2, fields2)
                        values = _x[0], msgtype
                        self.cursor.execute(cmd, values)
                else:
                    self.LOG.warning(f"ERROR sending email to {message['to']}.")
            self.conn.commit()

        else:
            self.LOG.warning("Emails not sent. SWITCH OFF.")

    def compose_message(self, member, template, email_id, alertas, placas):
        _txtal = []
        _attachments = []
        _attach_txt = []
        _msgrecords = []

        # create list of alerts
        for i in alertas:
            match i[0]:
                case "BREVETE":
                    _txtal.append(
                        f"Licencia de Conducir {'vencida.' if i[2] else 'vence en menos de 30 días.'}"
                    )
                case "SOAT":
                    _txtal.append(
                        f"Certificado SOAT de placa {i[1]} {'vencido.' if i[2] else 'vence en menos de 30 días.'}"
                    )
                case "SATIMP":
                    _txtal.append(
                        f"Impuesto Vehicular SAT {'vencido.' if i[2] else 'vence en menos de 30 días.'}"
                    )
                case "REVTEC":
                    _txtal.append(
                        f"Revision Técnica de placa {i[1]} {'vencida.' if i[2] else 'vence en menos de 30 días.'}"
                    )
                case "SUTRAN":
                    _txtal.append(f"Multa impaga en SUTRAN para placa {i[1]}.")
                case "SATMUL":
                    _txtal.append(f"Multa impaga en SAT para {i[1]}.")
                case "MTCPAPELETA":
                    _txtal.append("Papeleta Impaga reportada en el MTC.")

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
                    "fecha_desde": date_friendly(_m[5]),
                    "fecha_hasta": date_friendly(_m[6], delta=True),
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
                        "fecha_desde": date_friendly(_m[5]),
                        "fecha_hasta": date_friendly(_m[7], delta=True),
                        "restricciones": _m[6],
                        "local": _m[8],
                        "puntos": _m[9],
                        "record": _m[10],
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
                        "placa": _m[11],
                        "documento": _m[2],
                        "tipo": _m[3],
                        "fecha_documento": date_friendly(_m[4]),
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
                    "fecha_desde": date_friendly(_m[3]),
                    "fecha_hasta": date_friendly(_m[4], delta=True),
                    "certificado": _m[6],
                    "placa": _m[5],
                    "uso": _m[7],
                    "clase": _m[8],
                    "vigencia": _m[9],
                    "tipo": _m[10],
                }
            )
            # add image to attachment list
            _img_path = os.path.join(os.curdir, "data", "images", _m[12])
            if os.path.isfile(_img_path):
                _attachments.append(str(_img_path))
                _attach_txt.append(
                    f"Certificado Electrónico SOAT de Vehículo Placa {_m[5]}."
                )
                _msgrecords.append(15)
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
                    "fecha_emision": date_friendly(_m[6]),
                    "importe": _m[7],
                    "gastos": _m[8],
                    "descuento": _m[9],
                    "deuda": _m[10],
                    "estado": _m[11],
                    "licencia": _m[12],
                }
            )
            # add image to attachment list
            _img_path = os.path.join(os.curdir, "data", "images", _m[15])
            if os.path.isfile(_img_path):
                _attachments.append(str(_img_path))
                _attach_txt.append(
                    f"Papeleta de Infracción de Tránsito de Vehículo Placa {_m[2]}."
                )
                _msgrecords.append(17)
        _info.update({"satmuls": _satmuls})

        # add PAPELETA information
        _papeletas = []
        self.cursor.execute(
            f"SELECT * FROM mtcPapeletas WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
        )
        for _m in self.cursor.fetchall():
            _papeletas.append(
                {
                    "entidad": _m[2],
                    "numero": _m[3],
                    "fecha": date_friendly(_m[4]),
                    "fecha_firme": date_friendly(_m[5]),
                    "falta": _m[6],
                    "estado_deuda": _m[7],
                }
            )
        _info.update({"papeletas": _papeletas})

        # add SUNARP image
        self.cursor.execute(
            f"""SELECT * FROM sunarps WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}
                AND IdMember_FK IN _newSunarpRequired) ORDER BY LastUpdate DESC"""
        )
        for _m in self.cursor.fetchall():
            # add image to attachment list
            _img_path = os.path.join(os.curdir, "data", "images", _m[17])
            if os.path.isfile(_img_path):
                _attachments.append(str(_img_path))
                _attach_txt.append(
                    f"Consulta Vehicular SUNARP de Vehículo Placa {_m[17][-10:-4]}."
                )
                _msgrecords.append(16)

        # add RECORD DE CONDUCTOR image
        self.cursor.execute(
            f"SELECT * FROM recordConductores WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
        )
        for _m in self.cursor.fetchall():
            # add image to attachment list
            _img_path = os.path.join(os.curdir, "data", "images", _m[1])
            if os.path.isfile(_img_path):
                _attachments.append(str(_img_path))
                _attach_txt.append("Récord del Conductor MTC.")
                _msgrecords.append(14)

        # add SUNAT information
        _sunats = []
        self.cursor.execute(
            f"SELECT * FROM sunats WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
        )
        _m = self.cursor.fetchone()
        if _m:
            _sunats = {
                "ruc": _m[2],
                "tipo_contribuyente": _m[3],
                "nombre_comercial": _m[5],
                "fecha_inscripcion": _m[6],
                "fecha_inicio_actividades": _m[10],
                "estado": _m[7],
                "condicion": _m[8],
            }
        else:
            _sunats = []

        _info.update({"sunats": _sunats})

        # add text list of Attachments or "Ninguno" if empty
        _info.update({"adjuntos": _attach_txt if _attach_txt else ["Ninguno"]})

        return template.render(_info), _attachments, len(_txtal), _msgrecords
