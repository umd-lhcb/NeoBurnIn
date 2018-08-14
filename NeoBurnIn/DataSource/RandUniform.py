#!/usr/bin/env python
#
# Last Change: Tue Aug 14, 2018 at 12:49 PM -0400

import logging

from threading import Thread
from random import uniform

from NeoBurnIn.base import BaseDataSource
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class RandUniformDataSource(BaseDataSource):
    separator = '|'
    line_end  = '\n'

    def __init__(self, queue, stop_event,
                 interval=1, chPrefix='CHANNEL', numOfChs=1):
        self.queue = queue
        self.stop_event = stop_event
        self.interval = interval
        self.chPrefix = chPrefix
        self.num_of_chs = numOfChs

    def start(self):
        self.thread = Thread(target=self.run, args=(self.interval, ))
        self.thread.start()

    def run(self, interval):
        while not self.stop_event.wait(interval):
            msg = self.get()
            logger.debug(msg)
            self.queue.put(msg)

    def cleanup(self, timeout=10):
        self.thread.join(timeout)
        logging.debug('Data source closed.')

    def get(self):
        msg = ''
        for ch_num in range(1, self.num_of_chs+1):
            msg += self.get_single_channel(str(ch_num))
        return msg

    def get_single_channel(self, ch_num):
        return time_now_formatted() + self.separator + \
            self.chPrefix + ch_num + self.separator + \
            str(uniform(1, 10)) + self.line_end
