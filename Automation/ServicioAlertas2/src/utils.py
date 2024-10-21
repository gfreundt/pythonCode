from datetime import datetime as dt


def date_to_db_format(data):
    """Takes dd.mm.yyyy date formats with different separators and returns yyyy-mm-dd."""

    new_record_dates_fixed = []
    for data_item in data:
        # if record has date structure, alter it, everything else throws exception and no changes made
        try:
            sep = "/" if "/" in data_item else "-" if "-" in data_item else None
            new_record_dates_fixed.append(
                dt.strftime(dt.strptime(data_item, f"%d{sep}%m{sep}%Y"), "%Y-%m-%d")
            )
        except:
            new_record_dates_fixed.append(data_item)
    return new_record_dates_fixed


def log_action_in_db(db_cursor, table_name, idMember="", idPlaca=""):
    """Registers scraping action in actions table in database."""

    _values = (table_name, idMember, idPlaca, dt.now().strftime("%Y-%m-%d %H:%M:%S"))
    db_cursor.execute(f"INSERT INTO actions VALUES {_values}")
