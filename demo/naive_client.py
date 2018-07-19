#!/usr/bin/env python
#
# Last Change: Thu Jul 19, 2018 at 01:02 PM -0400

import logging
import janus

from random import uniform
from threading import Thread, Event

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import time_now_formatted
from NeoBurnIn.base import BaseDataSource
from NeoBurnIn.io.client import Client


class NaiveRandDataSource(BaseDataSource):
    def __init__(self, queue, stop_event, ch_name='ch1'):
        self.queue = queue
        self.stop_event = stop_event
        self.ch_name = ch_name

    def start(self, interval):
        self.thread = Thread(target=self.run, args=(stop_event, interval))
        self.thread.start()

    def run(self, stop_event, interval):
        while not stop_event.wait(interval):
            msg = self.get()
            print(msg)
            self.queue.put(msg)

    def get(self):
        return time_now_formatted() + '|' + self.ch_name + '|' + \
            str(uniform(1, 10))


if __name__ == "__main__":
    data_queue = janus.Queue()
    stop_event = Event()
    logger = logging.getLogger()
    thread_list = []

    rand_data_source = NaiveRandDataSource(data_queue.sync_q, stop_event)
    rand_data_source.start(0.01)

    thread_list.append(rand_data_source.thread)

    client = Client(data_queue.sync_q, logger, stop_event, thread_list=thread_list)
    client.run()
