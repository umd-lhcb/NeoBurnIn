#!/usr/bin/env python
#
# Last Change: Tue Jul 24, 2018 at 01:01 AM -0400

import logging
import janus

from threading import Event

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.client import Client
from NeoBurnIn.DataSource.RandUniform import RandUniformDataSource
from NeoBurnIn.io.logging import log_handler_console

####################
# Configure logger #
####################

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler_console(level=logging.DEBUG))


if __name__ == "__main__":
    data_queue = janus.Queue()
    stop_event = Event()
    thread_list = []

    rand_data_source = RandUniformDataSource(data_queue.sync_q, stop_event,
                                             num_of_chs=3)
    rand_data_source.start(0.5)
    thread_list.append(rand_data_source)

    client = Client(data_queue.async_q, stop_event, thread_list=thread_list)
    client.run()

    # data_queue.sync_q.join()
    # logger.debug('sync q joined')
    # data_queue.async_q.join()
    # logger.debug('async q joined')
