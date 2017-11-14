#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 09:14 PM -0500

import sys
sys.path.insert(0, '..')

from multiprocessing import Queue

from bUrnIn.server.transmission import TransmissionServerAsync
from bUrnIn.server.dispatcher import Dispatcher


class NaiveDispatcher(Dispatcher):
    '''
    A simple dispatch that prints everything that throws at it.
    '''
    def dispatch(self):
        while True:
            msg = self.msgs.get()

            if msg is self.stop_token:
                break
            else:
                print(msg)


if __name__ == "__main__":
    msgs = Queue()
    errs = Queue()
    emails = Queue()

    db_filename = ''
    time_format = ''

    server = TransmissionServerAsync('localhost', 45678, msgs, errs, emails,
                                     time_format)
    server.listen()

    dispatcher = NaiveDispatcher(msgs, errs, emails, db_filename, time_format)
    dispatcher.start()
