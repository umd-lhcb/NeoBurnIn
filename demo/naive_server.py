#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 07:43 PM -0500

import signal

from multiprocessing import Queue, Event

import sys
sys.path.insert(0, '..')

from bUrnIn.server.transmission import TransmissionServerAsync
from bUrnIn.server.dispatcher import Dispatcher
from bUrnIn.server.logging import LoggerForMultiProcesses


def on_exit(signum, frame):
    raise KeyboardInterrupt


class NaiveDispatcher(Dispatcher):
    '''
    A simple dispatch that prints everything that throws at it.
    '''
    def filter(self, msg):
        print(msg)


if __name__ == "__main__":
    msgs = Queue()
    logs = Queue()
    stop_event = Event()

    logger = LoggerForMultiProcesses(logs, stop_event, log_handlers=['console'])
    logger.start()

    dispatcher = NaiveDispatcher(msgs, logs)
    dispatcher.start()

    # Handle SIGTERM and SIGINT
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    # Start the TCP server on the main process
    server = TransmissionServerAsync('localhost', 45678, msgs, logs)
    server.listen()

    # Cleanup
    dispatcher.dispatcher_process.join()
    stop_event.set()
    logger.listener_process.join()
