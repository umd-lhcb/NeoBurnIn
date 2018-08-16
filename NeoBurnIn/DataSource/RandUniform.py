#!/usr/bin/env python
#
# Last Change: Thu Aug 16, 2018 at 12:01 AM -0400

import logging

from random import uniform

from NeoBurnIn.base import BaseDataSource
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class RandUniformDataSource(BaseDataSource):
    def __init__(self, queue, stop_event, *args,
                 interval=1, chPrefix='CHANNEL', numOfChs=1, **kwargs):
        self.queue = queue
        self.stop_event = stop_event
        self.interval = interval
        self.chPrefix = chPrefix
        self.numOfChs = numOfChs

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
        msg = ''
        for ch_num in range(1, self.numOfChs+1):
            msg += self.get_single_channel(str(ch_num))
        return msg

    def get_single_channel(self, ch_num):
        return time_now_formatted() + self.separator + \
            self.chPrefix + ch_num + self.separator + \
            str(uniform(1, 10)) + self.line_end
