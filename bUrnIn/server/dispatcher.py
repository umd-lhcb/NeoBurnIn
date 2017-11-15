#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 11:59 AM -0500

import logging
import logging.config

from multiprocessing import Process as Container
from sqlite3 import OperationalError

from bUrnIn.io.sqlite import sql_init
from bUrnIn.server.base import ChildProcessSignalHandler
from bUrnIn.server.logging import generate_config_worker


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
        pass

    def dispatch(self):
        while True:
            try:
                data = self.msgs.get()

                if data is None:
                    self.log.info("Preparing dispatcher shutdown on receiving shutdown control message.")
                    break
                else:
                    self.filter(data)

            except KeyboardInterrupt:
                self.log.info('Preparing dispatcher shutdown on receiving KeyboardInterrupt.')
                # self.log.info('Preparing dispatcher shutdown on receiving {}.'.format(err.__class__.__name__))
                break

    def start(self):
        dispatcher = Container(target=self.dispatch)
        dispatcher.start()
        self.dispatcher_process = dispatcher
