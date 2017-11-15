#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 08:56 AM -0500

import logging
import logging.config

from multiprocessing import Event, Queue

import sys
sys.path.insert(0, '..')

from bUrnIn.io.logging import generate_config_worker, LoggerForMultiProcesses


if __name__ == "__main__":
    logs = Queue()
    stop_event = Event()
    logging.config.dictConfig(generate_config_worker(logs, 'DEBUG'))

    log_listener = LoggerForMultiProcesses(
        logs, stop_event,
        level='DEBUG', handlers=['file', 'console', 'email'])
    log_listener.start()

    logger = logging.getLogger()
    logger.debug('This is a test message.')

    stop_event.set()
    log_listener.listener_process.join()
