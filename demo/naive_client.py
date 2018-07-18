#!/usr/bin/env python
#
# Last Change: Wed Jul 18, 2018 at 10:45 AM -0400

import asyncio
import aiohttp

from random import uniform
from queue import Queue
from threading import Thread, Event

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import time_now_formatted, ThreadTerminator
from NeoBurnIn.base import BaseDataSource, BaseClient


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


class NaiveClient(ThreadTerminator, BaseClient):
    def __init__(self, queue, *args,
                 ip='localhost', port='45678', **kwargs):
        self.queue = queue

        self.url = 'http://{}:{}/datacollect'.format(ip, port)
        self.loop = asyncio.get_event_loop()

        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            # NOTE: this is a blocking call, which means that all messages will
            # be sent sequentially---no concurrency.
            try:
                msg = self.queue.get()
                data = bytearray(msg, 'utf8')
                self.loop.run_until_complete(self.post(data))
            except KeyboardInterrupt:
                super().killall()
                break

    async def post(self, data):
        async with aiohttp.ClientSession() as client:
            async with client.post(self.url, data=data) as resp:
                print(await resp.text())

    def loop_getter(self):
        return self.loop


if __name__ == "__main__":
    data_queue = Queue()
    stop_event = Event()
    thread_list = []

    datasource = NaiveRandDataSource(data_queue, stop_event)
    datasource.start(1)

    thread_list.append(datasource.thread)

    client = NaiveClient(data_queue, stop_event, thread_list=thread_list)
    client.run()
