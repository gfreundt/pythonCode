import os
import sqlite3


def db(monitor):
    """Used to download new members and add them to local database, manage unsubscribe
    requests and create 30-day list"""

    # connect to database, enable db threading
    SQLDATABASE = os.path.join("..", "data", "members.db")
    conn = sqlite3.connect(SQLDATABASE, check_same_thread=False)
    monitor.log(f"Succesfully read {os.path.abspath(SQLDATABASE)} database.", type=1)

    # return connection and cursor
    return conn, conn.cursor()
