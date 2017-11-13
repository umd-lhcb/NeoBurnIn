#!/usr/bin/env python
#
# Last Change: Wed Nov 08, 2017 at 11:16 AM -0500

import sqlite3


def sql_init(db):
    conn = sqlite3.connect(db)

    c = conn.cursor()
    c.execute('''
              CREATE TABLE data
              (date text, host text, measured text, value real)
              ''')

    conn.commit()
    conn.close()


def sql_write(db, hostname, timestamp, data):
    conn = sqlite3.connect(db, check_same_thread=False)
    c = conn.cursor()

    for key in data.keys():
        c.execute("INSERT INTO data VALUES ('{0}', '{1}', '{2}', {3})".format(
            timestamp, hostname, key, data[key]
        ))

    conn.commit()
    conn.close()
