import os
from datetime import datetime as dt, timedelta as td
from jinja2 import Environment, FileSystemLoader
import uuid
from comms import create_within_expiration


def craft(db_cursor, dash):

    # update table with all expiration information for message alerts
    create_within_expiration.update_table(db_cursor)

    # log action
    # dash()

    # load HTML templates
    environment = Environment(loader=FileSystemLoader("../templates/"))
    template_welcome = environment.get_template("bienvenida.html")
    template_regular = environment.get_template("regular.html")

    messages = []

    # loop all members that required a welcome message
    db_cursor.execute(
        "SELECT IdMember_FK FROM _necesitan_mensajes_usuarios WHERE Tipo = 'B'"
    )
    for IdMember in db_cursor.fetchall():
        messages.append(
            grab_message_info(
                db_cursor,
                IdMember[0],
                template=template_welcome,
                subject="Bienvenido al Servicio de Alertas Perú",
                msg_type=12,
            )
        )

    # loop all members that required a regular message
    db_cursor.execute(
        "SELECT IdMember_FK FROM _necesitan_mensajes_usuarios WHERE Tipo = 'R'"
    )
    for IdMember in db_cursor.fetchall():
        messages.append(
            grab_message_info(
                db_cursor,
                IdMember[0],
                template=template_regular,
                subject="Informe Mensual del Servicio de Alertas Perú",
                msg_type=13,
            )
        )

    # save crafted messages as HTML in outbound folder
    for message in messages:
        _file_path = os.path.join(
            "..", "outbound", f"message_{str(uuid.uuid4())[-6:]}.html"
        )
        with open(_file_path, "w", encoding="utf-8") as file:
            file.write(message)


def grab_message_info(db_cursor, IdMember, template, subject, msg_type):

    # get member information
    db_cursor.execute(f"SELECT * FROM members WHERE IdMember = {IdMember}")
    member = db_cursor.fetchone()

    # get message alerts
    db_cursor.execute(
        f"SELECT TipoAlerta, Placa, Vencido FROM _expira30dias WHERE IdMember = {IdMember}"
    )
    _a = db_cursor.fetchall()
    alertas = [[i[0], i[1], i[2]] for i in _a if i] if _a else []

    # get placas associated with member
    db_cursor.execute(f"SELECT Placa FROM placas WHERE IdMember_FK = {IdMember}")
    placas = [i[0] for i in db_cursor.fetchall()]

    # generate random email hash
    email_id = f"{member[1]}|{str(uuid.uuid4())[-12:]}"

    # create html format data
    return compose_message(
        db_cursor, member, template, email_id, subject, alertas, placas, msg_type
    )


def compose_message(
    db_cursor, member, template, email_id, subject, alertas, placas, msg_type
):

    _txtal = []
    _attachments = []
    _attach_txt = []
    _msgrecords = []
    _info = {}

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
    _info.update({"alertas": _txtal if _txtal else ["Ninguna"]})

    # add randomly generated email ID, nombre and lista placas for opening text
    _info.update(
        {
            "nombre_usuario": member[2],
            "codigo_correo": email_id,
            "lista_placas": ", ".join(placas),
        }
    )

    # add revision tecnica information
    db_cursor.execute(
        f"SELECT * FROM revtecs WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
    )
    _revtecs = []

    for _m in db_cursor.fetchall():

        _revtecs.append(
            {
                "certificadora": _m[1].split("-")[-1][:35],
                "placa": _m[2],
                "certificado": _m[3],
                "fecha_desde": date_friendly(_m[4]),
                "fecha_hasta": date_friendly(_m[5], delta=True),
                "resultado": _m[6],
                "vigencia": _m[7],
            }
        )
    _info.update({"revtecs": _revtecs})

    # add brevete information
    db_cursor.execute(
        f"SELECT * FROM brevetes WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
    )
    _m = db_cursor.fetchone()
    if _m:
        _info.update(
            {
                "brevete": {
                    "numero": _m[2],
                    "clase": _m[1],
                    "formato": _m[3],
                    "fecha_desde": date_friendly(_m[4]),
                    "fecha_hasta": date_friendly(_m[6], delta=True),
                    "restricciones": _m[5],
                    "local": _m[7],
                    "puntos": _m[8],
                    "record": _m[9],
                }
            }
        )
    else:
        _info.update({"brevete": {}})

    # add SUTRAN information
    _sutran = []
    db_cursor.execute(
        f"SELECT * FROM sutrans JOIN placas ON IdPlaca = IdPlaca_FK WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
    )
    for _m in db_cursor.fetchall():
        if _m:
            _sutran.append(
                {
                    "placa": _m[9],
                    "documento": _m[1],
                    "tipo": _m[2],
                    "fecha_documento": date_friendly(_m[3]),
                    "infraccion": (f"{_m[4]} - {_m[5]}"),
                }
            )
        _info.update({"sutrans": _sutran})

    # add SATIMP information
    db_cursor.execute(
        f"SELECT * FROM satimpCodigos WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
    )

    _v = []
    for satimp in db_cursor.fetchall():
        db_cursor.execute(f"SELECT * FROM satimpDeudas WHERE IdCodigo_FK = {satimp[0]}")
        _s = []
        for _x in db_cursor.fetchall():
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
    db_cursor.execute(
        f"SELECT * FROM soats WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
    )
    for _m in db_cursor.fetchall():
        _soats.append(
            {
                "aseguradora": _m[1],
                "fecha_desde": date_friendly(_m[2]),
                "fecha_hasta": date_friendly(_m[3], delta=True),
                "certificado": _m[5],
                "placa": _m[4],
                "uso": _m[6],
                "clase": _m[7],
                "vigencia": _m[8],
                "tipo": _m[9],
            }
        )
        # add image to attachment list
        _img_path = os.path.abspath(os.path.join("..", "data", "images", _m[11]))
        if os.path.isfile(_img_path):
            _attachments.append(str(_img_path))
            _attach_txt.append(
                f"Certificado Electrónico SOAT de Vehículo Placa {_m[4]}."
            )
            _msgrecords.append(15)
    _info.update({"soats": _soats})

    # add SATMUL information
    _satmuls = []
    db_cursor.execute(
        f"SELECT * FROM satmuls WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}) ORDER BY LastUpdate DESC"
    )
    for _m in db_cursor.fetchall():
        _satmuls.append(
            {
                "placa": _m[1],
                "reglamento": _m[2],
                "falta": _m[3],
                "documento": _m[4],
                "fecha_emision": date_friendly(_m[5]),
                "importe": _m[6],
                "gastos": _m[7],
                "descuento": _m[8],
                "deuda": _m[9],
                "estado": _m[10],
                "licencia": _m[11],
            }
        )
        # add image to attachment list
        _img_path = os.path.abspath(os.path.join("..", "data", "images", _m[14]))
        if os.path.isfile(_img_path):
            _attachments.append(str(_img_path))
            _attach_txt.append(
                f"Papeleta de Infracción de Tránsito de Vehículo Placa {_m[2]}."
            )
            _msgrecords.append(17)
    _info.update({"satmuls": _satmuls})

    # add PAPELETA information
    _papeletas = []
    db_cursor.execute(
        f"SELECT * FROM mtcPapeletas WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
    )
    for _m in db_cursor.fetchall():
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
    db_cursor.execute(
        f"""SELECT * FROM sunarps WHERE IdPlaca_FK IN (SELECT IdPlaca FROM placas WHERE IdMember_FK = {member[0]}
                AND IdMember_FK IN _newSunarpRequired) ORDER BY LastUpdate DESC"""
    )
    for _m in db_cursor.fetchall():
        # add image to attachment list
        _img_path = os.path.abspath(os.path.join("..", "data", "images", _m[15]))
        if os.path.isfile(_img_path):
            _attachments.append(str(_img_path))
            _attach_txt.append(
                f"Consulta Vehicular SUNARP de Vehículo Placa {_m[15][-10:-4]}."
            )
            _msgrecords.append(16)

    # add RECORD DE CONDUCTOR image
    db_cursor.execute(
        f"SELECT * FROM recordConductores WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
    )
    for _m in db_cursor.fetchall():
        # add image to attachment list
        _img_path = os.path.abspath(os.path.join("..", "data", "images", _m[1]))
        if os.path.isfile(_img_path):
            _attachments.append(str(_img_path))
            _attach_txt.append("Récord del Conductor MTC.")
            _msgrecords.append(14)

    # add SUNAT information
    _sunats = []
    db_cursor.execute(
        f"SELECT * FROM sunats WHERE IdMember_FK = {member[0]} ORDER BY LastUpdate DESC"
    )
    _m = db_cursor.fetchone()
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

    # subject title number of alerts
    _subj = (
        f"{len(_txtal)} ALERTAS"
        if len(_txtal) > 1
        else f"1 ALERTA" if len(_txtal) == 1 else "SIN ALERTAS"
    )

    # meta data
    _info.update({"to": member[6]})
    _info.update({"bcc": "gabfre@gmail.com"})
    _info.update({"subject": f"{subject} ({_subj})"})
    _info.update({"msg_types": [msg_type] + _msgrecords})
    _info.update({"idMember": int(member[0])})
    _info.update({"timestamp": dt.now().strftime("%Y-%m-%d %H:%M:%S")})
    _info.update({"hashcode": email_id})
    _info.update({"attachment_paths": _attachments})

    return template.render(_info)


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
