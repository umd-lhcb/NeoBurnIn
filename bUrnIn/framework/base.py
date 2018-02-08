#!/usr/bin/env python
#
# Last Change: Thu Feb 08, 2018 at 01:23 PM -0500

import signal
import logging
import logging.config

from multiprocessing import Process as Container
from datetime import datetime

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


def time_now_formatted():
    return datetime.now().strftime(standard_time_format)


class SignalHandler(object):
    '''
    This class defers SIGINT and SIGTERM signals.
    It is assumed that any subclass would deal with that explicitly.
    This is a delicate matter, as each instance of 'SignalHandler' would deal
    the termination signal in the reverse order of their instantiation.
    '''
    def __init__(self):
        self.signal_register()

    def signal_register(self):
        # SIGINT: Ctrl-C.
        # SIGTERM: when a process is about to be killed.
        signal.signal(signal.SIGINT, self.signal_handle)
        signal.signal(signal.SIGTERM, self.signal_handle)

    def signal_handle(self, signum, frame):
        # WARNING: Ignoring termination requests
        pass


class Dispatcher(SignalHandler):
    '''
    A template dispatcher class.
    '''
    def __init__(self, queue, logger_name='log'):
        self.queue = queue

        self.logger = logging.getLogger(logger_name)

        super().__init__()

    def start(self):
        dispatcher = Container(target=self.dispatch)
        dispatcher.start()
        self.container = dispatcher

    def dispatch(self):
        pass


class Server(SignalHandler):
    '''
    A template server class.
    '''
    def __init__(self, ip, port, msg_queue,
                 timeout, size, max_retries,
                 logger_name='log'):
        self.ip = ip
        self.port = port
        self.msg_queue = msg_queue
        self.timeout = timeout
        self.size = size
        self.max_retries = max_retries

        self.logger = logging.getLogger(logger_name)

        super().__init__()

    def start(self):
        pass

    def client_accept(self, client_reader, client_writer):
        pass

    def client_handle(self, client_reader, client_writer):
        pass

    def signal_handle(self, signum, frame):
        raise KeyboardInterrupt
