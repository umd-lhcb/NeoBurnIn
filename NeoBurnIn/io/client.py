#!/usr/bin/env python
#
# Last Change: Fri Jul 20, 2018 at 01:42 PM -0400

import logging
import asyncio
import aiohttp

from NeoBurnIn.base import ThreadTerminator, BaseClient

logger = logging.getLogger(__name__)


class Client(ThreadTerminator, BaseClient):
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
                self.send(msg)
                self.queue.task_done()
            except KeyboardInterrupt:
                break

        self.cleanup()

    def cleanup(self):
        # Kill all sub-threads first
        self.killall()

        # Now process all remaining info in the queue
        logger.debug('Process all remaining items in the queue')
        while not self.queue.empty():
            msg = self.queue.get()
            self.send(msg)
            self.queue.task_done()
            logger.debug('An item has been processed.')

        # All existing items have been processed. All items added after the
        # termination is issued will not be processed.
        # self.queue.join()

    def send(self, msg):
        data = bytearray(msg, 'utf8')
        self.loop.run_until_complete(self.post(data))

    def loop_getter(self):
        return self.loop

    async def post(self, data):
        async with aiohttp.ClientSession() as client:
            async with client.post(self.url, data=data) as resp:
                logger.debug(resp.status)
                logger.debug(await resp.text())
