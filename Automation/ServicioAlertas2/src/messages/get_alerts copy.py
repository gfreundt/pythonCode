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


def craft_alerts(required_alerts, log, monitor):

    # erase all alert text files from previous times
    for existing in os.listdir(os.path.join(os.curdir, "templates")):
        if "sms" in existing:
            os.remove(os.path.join(os.curdir, "templates", existing))

    # loop all members in alert list, compose message
    for k, alert_data in enumerate(required_alerts):
        content = compose_text(alert_data)
        # write locally for debugging
        with open(
            os.path.join(os.curdir, "outbound", f"wapp{k:03d}.txt"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content)

    monitor.add_item(f"Total New Alerts: {len(required_alerts)}", type=1)

    log.warning("SMS not sent. SWITCH OFF.")


def compose_text(self, member):

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
