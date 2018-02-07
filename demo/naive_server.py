#!/usr/bin/env python
#
# Last Change: Tue Feb 06, 2018 at 07:38 PM -0500

from multiprocessing import Queue

import sys
sys.path.insert(0, '..')

from bUrnIn.framework.server import ServerAsync
from bUrnIn.framework.base import Dispatcher


class NaiveDispatcher(Dispatcher):
    '''
    A simple dispatch that prints everything that throws at it.
    '''
    def dispatch(self):
        while True:
            msg = self.queue.get()

            if msg is not None:
                print(msg)
            else:
                break


if __name__ == "__main__":
    msg_queue = Queue()

    dispatcher = NaiveDispatcher(msg_queue)
    dispatcher.start()

    server = ServerAsync('localhost', 45678, msg_queue)
    server.start()

    dispatcher.container.join()
