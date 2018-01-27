#!/usr/bin/env python
#
# Last Change: Tue Dec 12, 2017 at 03:51 PM -0500

import logging
import logging.config

from multiprocessing import Event, Queue
from random import uniform

import sys
sys.path.insert(0, '..')

from bUrnIn.server.logging import generate_config_worker, LoggerForMultiProcesses


if __name__ == "__main__":
    logs = Queue()
    stop_event = Event()
    logging.config.dictConfig(generate_config_worker(logs, 'DEBUG'))

    logger = LoggerForMultiProcesses(logs, stop_event,
        recipients=['syp@umd.edu', 'yipengsun@ucla.edu'],
        credentials=['burnin.umd.lhb@gmail.com', 'burnin@umd@lhcb'])
    logger.start()

    # Test actual logging messages
    log = logging.getLogger()
    log.info('This is a test message.')
    # log.error('A fake error has occurred!')
    # log.critical('A fake critical error has occurred!')

    # Test data log
    datalog = logging.getLogger('data')
    for i in range(0, 100):
        datalog.info('COL1, COL2, COL3, COL4: {}'.format(uniform(0, 100)))

    stop_event.set()
    logger.listener_process.join()
