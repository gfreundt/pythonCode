import os
import sqlite3

from pprint import pprint


class Database:

    def __init__(self, dev):
        self.start(dev=dev)
        self.load_members()

    def start(self, monitor=None, dev=True):
        """Connect to database. Use development database by default."""

        # production
        SQLDATABASE = os.path.join("..", "data", "members.db")
        if dev:
            # development
            SQLDATABASE = os.path.join("..", "data", "dev", "members.db")

        self.conn = sqlite3.connect(SQLDATABASE, check_same_thread=False)
        self.cursor = self.conn.cursor()

        if monitor:
            monitor.log(
                f'Using {"DEVELOPMENT" if dev else "PRODUCTION"} database.', type=1
            )
            monitor.log(
                f"Succesfully read {os.path.abspath(SQLDATABASE)} database.", type=1
            )

    def load_members(self):
        self.cursor.execute("SELECT * FROM members")
        self.users = self.cursor.fetchall()
