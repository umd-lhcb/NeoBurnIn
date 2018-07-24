#!/usr/bin/env python
#
# Last Change: Tue Jul 24, 2018 at 11:55 AM -0400

import logging
import asyncio
import aiohttp

# from functools import partial

from NeoBurnIn.base import ThreadTerminator, BaseClient

logger = logging.getLogger(__name__)


class Client(ThreadTerminator, BaseClient):
    POST_API = 'datacollect'

    def __init__(self, queue, *args,
              ip='localhost', port='45678', maxConcurrency=3, **kwargs):
        self.queue = queue

        self.url = 'http://{}:{}/{}'.format(ip, port, self.POST_API)
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
        while not self.queue.empty():
            self.loop.run_until_complete(self.send())
            logger.debug('An item has been processed.')

        # All existing items have been processed. All items added after the
        # termination is issued will not be processed.
        self.queue.join()
        logger.debug('Asynchronous queue joined.')

    def loop_getter(self):
        return self.loop

    # Recursively handle all messages, up to maxConcurrency
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
        self.queue.task_done()
        # FIXME: here we have to decouple semaphore acquire and release
        self.sem.release()

    async def post(self, data):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data) as resp:
                    if resp.status != 200:
                        logger.warning(
                            'Transmission for the following msg unsuccessful, with a HTTP error code {}: {}'.format(
                                resp.status, data.decode('utf8')
                            ))
                    logger.debug(await resp.text())

        except Exception as err:
            logger.warning(
                'Transmission for the following msg failed, with the following exception {}: {}'.format(
                    err.__class__.__name__, data.decode('utf8')
                ))
