#!/usr/bin/env python3
#
# Last Change: Fri Jun 26, 2020 at 02:35 AM +0800

import logging

from random import uniform
from threading import Thread

from NeoBurnIn.base import BaseDataSource, DataPassthru
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class RandUniformDataSource(Thread, BaseDataSource):
    def __init__(self, stop_event, queue, *args,
                 interval=1, displayName='RAND', **kwargs):
        self.queue = queue
        self.stop_event = stop_event
        self.interval = interval
        self.displayName = displayName

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
        return DataPassthru(time_now_formatted(), self.displayName,
                            uniform(1, 10))


class RandUniformDataSourceMul(Thread, BaseDataSource):
    def __init__(self, stop_event, queue, *args,
                 interval=1, displayName='RAND', psuChannels=list(range(1, 12)),
                 **kwargs):
        self.queue = queue
        self.stop_event = stop_event
        self.interval = interval
        self.displayName = displayName
        self.psuChannels = psuChannels

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            currs = self.get()
            for c in currs:
                self.queue.put(c)

    def cleanup(self, timeout=10):
        self.join(timeout)
        logging.debug('Data source closed.')

    def get(self):
        result = []
        for ch in self.psuChannels:
            result.append(
                DataPassthru(time_now_formatted(), self.displayName+str(ch),
                             uniform(1, 2)))
        return result
