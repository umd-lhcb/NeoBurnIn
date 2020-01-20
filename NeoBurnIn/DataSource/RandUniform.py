#!/usr/bin/env python
#
# Last Change: Sun Jan 19, 2020 at 07:57 PM -0500

import logging

from random import uniform
from threading import Thread

from NeoBurnIn.base import BaseDataSource, DataPassthru
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class RandUniformDataSource(Thread, BaseDataSource):
    def __init__(self, stop_event, queue, *args,
                 interval=1, chName='RAND', **kwargs):
        self.queue = queue
        self.stop_event = stop_event
        self.interval = interval
        self.chName = chName

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            msg = self.get()
            logger.debug(msg)
            self.queue.put(msg)

    def cleanup(self, timeout=10):
        self.join(timeout)
        logging.debug('Data source closed.')

    def get(self):
        return DataPassthru(time_now_formatted(), self.chName,
                            str(uniform(1, 10)))
