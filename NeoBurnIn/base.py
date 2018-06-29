#!/usr/bin/env python
#
# Last Change: Thu Jun 28, 2018 at 11:06 PM -0400

import signal
import logging
import logging.config

from multiprocessing import Process as Container
from datetime import datetime
from collections import defaultdict

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


def time_now_formatted():
    '''
    Generate standardized time that should be used throughout when storing
    datetime as string.
    '''
    return datetime.now().strftime(standard_time_format)


def nested_dict():
    '''
    Recursive defaultdict that handles variable depth keys.
    '''
    return defaultdict(nested_dict)


class SignalHandler(object):
    '''
    This class register a SIGINT and SIGTERM handler.
    This is a delicate matter, as only the last registered handler would be
    effective for multiprocessing programs.
    For multithread programs, only *one* thread should register.
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
    def __init__(self, controller, ip, port,
                 timeout=3, size=4096, max_retries=3,
                 logger_name='log'):
        self.controller = controller

        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.size = size
        self.max_retries = max_retries

        self.logger = logging.getLogger(logger_name)

        super().__init__()

    async def client_handle(self, client_reader, client_writer):
        pass
