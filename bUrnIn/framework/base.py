#!/usr/bin/env python
#
# Last Change: Mon Feb 05, 2018 at 06:34 PM -0500

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
    def __init__(self, msg_queue, logger_name, datalogger_name):
        self.msg_queue = msg_queue
        self.logger = logging.getLogger(logger_name)
        self.datalogger = logging.getLogger(datalogger_name)

        super(Dispatcher, self).__init__()

    def start(self):
        self.logger.info("Dispatcher starting.")
        dispatcher = Container(target=self.dispatch)
        dispatcher.start()
        self.process = dispatcher

    def dispatch(self):
        while True:
            msg = self.msg_queue.get()
            if msg is None:
                self.logger.info("Shutdown signal received, preparing dispatcher shutdown.")
                break

            else:
                data = self.decode(msg)
                self.filter(data)

    def decode(self, msg):
        data = msg.split('\n')
        # Remove trailing '' element if it exists
        data = data[:-1] if data[-1] == '' else data
        return data

    def filter(self, data):
        pass


class Server(SignalHandler):
    '''
    A template server class.
    '''
    def __init__(self, ip, port, msg_queue, logger_name,
                 timeout, size, max_retries):
        self.ip = ip
        self.port = port
        self.msg_queue = msg_queue
        self.timeout = timeout
        self.size = size
        self.max_retries = max_retries

        self.logger = logging.getLogger(logger_name)

        super(Server, self).__init__()

    def start(self):
        pass

    def client_accept(self, client_reader, client_writer):
        pass

    def client_handle(self, client_reader, client_writer):
        pass

    def signal_handle(self, signum, frame):
        raise KeyboardInterrupt
