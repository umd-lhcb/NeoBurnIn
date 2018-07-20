#!/usr/bin/env python
#
# Last Change: Fri Jul 20, 2018 at 01:52 PM -0400

import logging

from threading import Thread
from random import uniform

from NeoBurnIn.base import BaseDataSource
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class RandUniformDataSource(BaseDataSource):
    ch_prefix = 'CHANNEL'
    separator = '|'
    line_end  = '\n'

    def __init__(self, queue, stop_event,
                 num_of_chs=1):
        self.queue = queue
        self.stop_event = stop_event
        self.num_of_chs = num_of_chs

    def start(self, interval):
        self.thread = Thread(target=self.run, args=(interval, ))
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
            self.ch_prefix + ch_num + self.separator + \
            str(uniform(1, 10)) + self.line_end
