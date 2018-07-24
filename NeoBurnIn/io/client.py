#!/usr/bin/env python
#
# Last Change: Tue Jul 24, 2018 at 01:04 AM -0400

import logging
import asyncio
import aiohttp

# from functools import partial

from NeoBurnIn.base import ThreadTerminator, BaseClient

logger = logging.getLogger(__name__)


class Client(ThreadTerminator, BaseClient):
    def __init__(self, queue, *args,
              ip='localhost', port='45678', maxConcurrency=5, **kwargs):
        self.queue = queue

        self.url = 'http://{}:{}/datacollect'.format(ip, port)
        self.sem = asyncio.BoundedSemaphore(maxConcurrency)
        self.loop = asyncio.get_event_loop()

        super().__init__(*args, **kwargs)

    def run(self):
        try:
            self.loop.run_until_complete(self.handle_single_msg())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.stop()
            self.cleanup()

    def cleanup(self):
        # Kill all sub-threads first
        self.killall()

        # Now process all remaining info in the queue
        # logger.debug('Process all remaining items in the queue')
        # with aiohttp.ClientSession() as session:
            # while not self.queue.empty():
                # self.loop.run_until_complete(self.send(session))
                # self.queue.task_done()
                # logger.debug('An item has been processed.')

        # All existing items have been processed. All items added after the
        # termination is issued will not be processed.
        # self.queue.join()

    # def send(self, session, msg):
        # data = bytearray(msg, 'utf8')
        # self.loop.run_until_complete(self.post(session, data))

    def loop_getter(self):
        return self.loop

    async def handle_single_msg(self):
        asyncio.ensure_future(self.send())

        # Proceed if more client sessions are allowed; otherwise block.
        await self.sem.acquire()
        asyncio.ensure_future(self.handle_single_msg())

    async def send(self):
        msg = await self.queue.get()
        logger.debug('Got a new message, start transmission...')
        data = bytearray(msg, 'utf8')
        await self.post(data)
        # FIXME: here we have to decouple semaphore acquire and release
        self.sem.release()

    async def post(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=data) as resp:
                logger.debug(await resp.text())
                return resp.status
