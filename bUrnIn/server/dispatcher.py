#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 12:54 PM -0500

import logging
import logging.config

from multiprocessing import Process as Container
from sqlite3 import OperationalError
from datetime import datetime

from bUrnIn.io.sqlite import sql_init, SqlWorker
from bUrnIn.server.base import ChildProcessSignalHandler
from bUrnIn.server.logging import generate_config_worker

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


class Dispatcher(ChildProcessSignalHandler):
    '''
    Dispatch received data. This Dispatcher runs in a separated process.
    '''
    def __init__(self, msgs, logs,
                 db_filename=''):
        self.signal_register()
        self.msgs = msgs
        self.db_filename = db_filename

        # Initialize a logger
        logging.config.dictConfig(generate_config_worker(logs))
        self.log = logging.getLogger()

        # Initialize sqlite database
        try:
            sql_init(self.db_filename)
        except OperationalError:
            pass  # This is due to table already exists.

    def filter(self, msg):
        # We require '|' to be the delimiter
        entries = msg.split('|')

        # Remove trailing '' element, if it exists
        entries = entries[:-1] if entries[-1] == '' else entries

        DatabaseWriter = SqlWorker(self.db_filename)
        for entry in entries:
            try:
                date, ch_name, value = entry
            except Exception as err:
                self.log.error("{}: Corrupted data: {}.".format(
                    err.__class__.__name__, entry))
                break

            try:
                timestamp = datetime.strptime(
                    date, standard_time_format).timestamp()
            except Exception as err:
                self.log.error("{}: Corrupted date entry: {}.".format(
                    err.__class__.__name__, date
                ))
                break

            try:
                value = float(value)
            except Exception as err:
                self.log.error("{}: Corrupted value entry: {}.".format(
                    err.__class__.__name__, value
                ))
                break

            try:
                DatabaseWriter.write(date, timestamp, ch_name, value)
            except Exception as err:
                self.log.error("{}: Cannot write to SQLite database.".format(
                    err.__class__.__name__
                ))
                break
        DatabaseWriter.commit()

    def dispatch(self):
        while True:
            data = self.msgs.get()

            if data is None:
                self.log.info("Preparing dispatcher shutdown on receiving shutdown control message.")
                break
            else:
                self.filter(data)

    def start(self):
        dispatcher = Container(target=self.dispatch)
        dispatcher.start()
        self.dispatcher_process = dispatcher
