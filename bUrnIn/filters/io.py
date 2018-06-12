#!/usr/bin/env python
#
# Last Change: Tue Jun 12, 2018 at 03:04 AM -0400

import sqlite3
import logging

from bUrnIn.filters.base import Filter
from bUrnIn.filters.base import FilterExitCode


def sql_init(db):
    conn = sqlite3.connect(db)

    c = conn.cursor()
    c.execute('''
              CREATE TABLE data
              (date text, timestamp real, ch_name text, value real)
              ''')

    conn.commit()
    conn.close()


class FilterSQLWriter(Filter):
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        super().__init__()

    def do(self, data):
        date, ch_name, value = data
        self.write(date, ch_name, value)
        return (data, FilterExitCode().ok)

    def exit(self):
        self.conn.commit()
        self.conn.close()

    def write(self, date, ch_name, value):
        c = self.conn.cursor()
        c.execute("INSERT INTO data VALUES ('%s', '%s', %s)"
                  % (date, ch_name, value))


class FilterLogWriter(Filter):
    def __init__(self, data_logger_name='data'):
        super().__init__(logger_name=data_logger_name)

    def do(self, data):
        self.logger.info("%s,%s,%s" % data)
        return (data, FilterExitCode().ok)
