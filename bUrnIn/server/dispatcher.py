#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 09:01 PM -0500

from multiprocessing import Process as Container
from sqlite3 import OperationalError

from bUrnIn.io.time import time_stamp
from bUrnIn.io.sqlite import sql_init


class Dispatcher():
    '''
    Dispatch received data. This Dispatcher runs in a separated process.
    '''
    def __init__(self,
                 msgs=None, errs=None, emails=None,
                 db_filename='',
                 time_format="%Y-%m-%d %H:%M:%S:%f"):
        # If the following message is received, shut down the dispatcher.
        self.stop_token = None

        self.msgs = msgs
        self.errs = errs
        self.emails = emails

        self.db_filename = db_filename
        self.time_format = time_format

        # Initialize sqlite database
        try:
            sql_init(self.db_filename)
        except OperationalError:
            pass  # This is due to table already exists.

    def dispatch(self):
        while True:
            data = self.msgs.get()

            if data is self.stop_token:
                break
            else:
                pass

    def start(self):
        dispatcher = Container(target=self.dispatch)
        dispatcher.start()
