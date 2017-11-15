#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 08:40 AM -0500

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

    server = TransmissionServerAsync('localhost', 45678, msgs=msgs)
    server.start()

    dispatcher = NaiveDispatcher(msgs=msgs)
    dispatcher.start()
