#!/usr/bin/env python
#
# Last Change: Thu Jul 19, 2018 at 12:23 PM -0400

import asyncio
import aiohttp

from NeoBurnIn.base import ThreadTerminator, BaseClient


class Client(ThreadTerminator, BaseClient):
    def __init__(self, queue, logger, *args,
              ip='localhost', port='45678', **kwargs):
        self.queue = queue
        self.logger = logger

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
                self.queue.task_done()
            except KeyboardInterrupt:
                self.killall()
                break
        self.cleanup()

    def cleanup(self):
        while not self.queue.empty():
            msg = self.queue.get()
            self.send(msg)
            self.queue.task_done()

    def send(self, msg):
        data = bytearray(msg, 'utf8')
        self.loop.run_until_complete(self.post(data))

    def loop_getter(self):
        return self.loop

    async def post(self, data):
        async with aiohttp.ClientSession() as client:
            async with client.post(self.url, data=data) as resp:
                print(await resp.text())
