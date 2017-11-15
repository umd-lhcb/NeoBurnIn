#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 10:59 AM -0500

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

    logger = LoggerForMultiProcesses(logs, stop_event,
        handlers=['file', 'console', 'email'],
        recipients=['syp@umd.edu', 'yipengsun@ucla.edu'])
    logger.start()

    log = logging.getLogger()
    log.info('This is a test message.')
    log.error('A fake error has occurred!')

    stop_event.set()
    logger.listener_process.join()
