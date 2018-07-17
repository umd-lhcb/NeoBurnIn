#!/usr/bin/env python
#
# Last Change: Tue Jul 17, 2018 at 04:07 PM -0400

import asyncio
import aiohttp

from random import uniform
from time import sleep
from queue import Queue
from threading import Thread

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import time_now_formatted
from NeoBurnIn.base import BaseDataSource, BaseClient


class NaiveRandDataSource(BaseDataSource):
    def __init__(self, queue, ch_name='ch1'):
        self.queue = queue
        self.ch_name = ch_name

    def start(self, interval):
        self.thread = Thread(target=self.run, args=(interval,))
        self.thread.start()

    def run(self, interval):
        while True:
            sleep(interval)
            msg = self.get()
            print(msg)
            self.queue.put(msg)

    def get(self):
        return time_now_formatted() + '|' + self.ch_name + '|' + \
            str(uniform(1, 10))


class NaiveClient(BaseClient):
    def __init__(self, queue, ip='localhost', port='45678'):
        self.queue = queue

        self.url = 'http://{}:{}/datacollect'.format(ip, port)
        self.loop = asyncio.get_event_loop()

    def run(self):
        while True:
            # NOTE: this is a blocking call, which means that all messages will
            # be sent sequentially---no concurrency.
            msg = self.queue.get()
            data = bytearray(msg, 'utf8')
            self.loop.run_until_complete(self.post(data))

    async def post(self, data):
        async with aiohttp.ClientSession() as client:
            async with client.post(self.url, data=data) as resp:
                print(await resp.text())

    def loop_getter(self):
        return self.loop


if __name__ == "__main__":
    data_queue = Queue()
    datasource = NaiveRandDataSource(data_queue)
    client = NaiveClient(data_queue)

    datasource.start(1)
    client.run()
