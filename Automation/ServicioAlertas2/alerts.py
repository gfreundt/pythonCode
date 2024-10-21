from gft_utils import WhatsAppUtils
from datetime import datetime as dt, timedelta as td
import os


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
        _deltatxt = f" [ {_delta:,} días ]" if _delta > 0 else "[ VENCIDO ]"
    return f"{_day}-{_month}-{_year}{_deltatxt}"


class Alerts:

    def __init__(self, LOG, members, MONITOR) -> None:
        self.LOG = LOG
        self.MONITOR = MONITOR
        self.cursor = members.cursor
        self.conn = members.conn
        self.alert_list = []
        self.WAPP = WhatsAppUtils()

    def get_alert_list(db_cursor, log, monitor):
        # generate list (only expiration records that meet date criteria)
        cmd = f"""  DROP TABLE IF EXISTS _alertaEnviar;
                    CREATE TABLE _alertaEnviar (CodMember, NombreCompleto, Celular, Placa, FechaHasta, TipoAlerta, Correo, IdMember_FK, IdPlaca_FK);

                    INSERT INTO _alertaEnviar (CodMember, NombreCompleto, Celular, Placa, FechaHasta, TipoAlerta, Correo, IdPlaca_FK)
                    SELECT CodMember, NombreCompleto, Celular, Placa, FechaHasta, TipoAlerta, Correo, IdPlaca FROM members
                    JOIN (
                        SELECT * FROM placas 
                        JOIN (
                        SELECT idplaca_FK, FechaHasta, "SOAT" AS TipoAlerta FROM soats WHERE DATE('now', 'localtime', '5 days') = FechaHasta OR DATE('now', 'localtime', '0 days') = FechaHasta
                        UNION
                        SELECT idplaca_FK, FechaHasta, "REVTEC" FROM revtecs WHERE DATE('now', 'localtime', '10 days')= FechaHasta OR DATE('now', 'localtime', '0 days')= FechaHasta)
                        ON idplaca = IdPlaca_FK)
                    ON IdMember = IdMember_FK;

                    INSERT INTO _alertaEnviar (CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo, IdMember_FK)
                    SELECT CodMember, NombreCompleto, FechaHasta, TipoAlerta, Correo, IdMember from members 
                        JOIN (
                            SELECT IdMember_FK, FechaHasta, "BREVETE" AS TipoAlerta FROM brevetes WHERE DATE('now', 'localtime', '30 days') = FechaHasta OR DATE('now', 'localtime', '0 days')= FechaHasta
						UNION
							SELECT IdMember_FK, FechaHasta, "SATIMP" AS TipoAlerta FROM satimpDeudas 
							JOIN
							(SELECT * FROM satimpCodigos)
							ON IdCodigo_FK = IdCodigo
							WHERE DATE('now', 'localtime', '10 days') = FechaHasta OR DATE('now', 'localtime', '0 days') = FechaHasta)
                    ON IdMember = IdMember_FK;"""

        db_cursor.executescript(cmd)
        db_cursor.execute("SELECT * FROM _alertaEnviar")
        return db_cursor.fetchall()

    def send_alerts(self, SMS=False):

        self.MONITOR.add_item(f"Total New Alerts: {len(self.alert_list)}", type=1)

        # erase txt from previous iterations
        for existing in os.listdir(os.path.join(os.curdir, "templates")):
            if "sms" in existing:
                os.remove(os.path.join(os.curdir, "templates", existing))

        # loop all members in alert list, compose message
        for k, member in enumerate(self.alert_list):
            content = self.compose_alert(member)
            # write locally for debugging
            with open(
                os.path.join(os.curdir, "templates", f"sms{k:03d}.txt"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(content)
            if SMS:
                self.WAPP.send_wapp(celnum=member[2], alert_txt=content)

        self.LOG.warning("SMS not sent. SWITCH OFF.")

    def compose_alert(self, member):
        _base_msg = "El Sistema de Alertas Perú te informa:\n"

        # create list of alerts
        match member[5]:
            case "BREVETE":
                msg = f"{_base_msg}{member[1]}, tu Licencia de Conducir vence el {date_friendly(member[4], delta=False)}."
            case "SOAT":
                msg = f"{_base_msg}{member[1]}, tu Certificado SOAT de placa *{member[3]}* vence el *{date_friendly(member[4], delta=False)}*."
            case "SATIMP":
                msg = f"{_base_msg}{member[1]}, tu Impuesto Vehicular SAT vence el {date_friendly(member[4], delta=False)}."
            case "REVTEC":
                msg = f"{_base_msg}{member[1]}, tu Revision Técnica de placa *{member[3]}* vence el *{date_friendly(member[4], delta=False)}*."

        return msg
