#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 12:29 PM -0500

import sqlite3


def sql_init(db):
    conn = sqlite3.connect(db)

    c = conn.cursor()
    c.execute('''
              CREATE TABLE data
              (date text, timestamp real, ch_name text, value real)
              ''')

    conn.commit()
    conn.close()


class SqlWorker():
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)

    def write(self, date, timestamp, ch_name, value):
        c = self.conn.cursor()
        c.execute("INSERT INTO data VALUES ('{0}', '{1}', '{2}', {3})".format(
            date, timestamp, ch_name, value
        ))

    def commit(self):
        self.conn.commit()
        self.conn.close()
