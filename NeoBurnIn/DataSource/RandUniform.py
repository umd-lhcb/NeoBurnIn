#!/usr/bin/env python
#
# Last Change: Thu Jul 19, 2018 at 04:25 PM -0400

from threading import Thread
from random import uniform

from NeoBurnIn.base import BaseDataSource
from NeoBurnIn.base import time_now_formatted


class RandUniformDataSource(BaseDataSource):
    ch_prefix = 'CHANNEL'
    separator = '|'
    line_end  = '\n'

    def __init__(self, queue, stop_event,
                 num_of_chs=1, printout=True):
        self.queue = queue
        self.stop_event = stop_event
        self.num_of_chs = num_of_chs
        self.printout = printout

        self.stopped = False

    def start(self, interval):
        self.thread = Thread(target=self.run, args=(interval, ))
        self.thread.start()
        self.cleanup()

    def run(self, interval):
        while not self.stop_event.wait(interval):
            msg = self.get()
            if self.printout:
                print(msg)
            self.queue.put(msg)

    def get(self):
        msg = ''
        for ch_num in range(1, self.num_of_chs+1):
            msg += self.get_single_channel(ch_num)
        return msg

    def is_stopped(self):
        return self.stopped

    def get_single_channel(self, ch_num):
        return time_now_formatted() + self.separator + \
            self.ch_prefix + ch_num + self.separator + \
            str(uniform(1, 10)) + self.line_end

    def cleaanup(self):
        self.thread.join()
        self.stopped = True
