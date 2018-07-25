#!/usr/bin/env python
#
# Last Change: Wed Jul 25, 2018 at 12:39 AM -0400

import logging
import asyncio
import aiohttp

# from functools import partial

from NeoBurnIn.base import ThreadTerminator, BaseClient

logger = logging.getLogger(__name__)


class Client(ThreadTerminator, BaseClient):
    POST_API = 'datacollect'

    def __init__(self, queue, *args,
                 ip='localhost', port='45678',
                 maxConcurrency=3,
                 **kwargs):
        self.queue = queue

        self.url = 'http://{}:{}/{}'.format(ip, port, self.POST_API)
        self.sem = asyncio.Semaphore(maxConcurrency)
        self.loop = asyncio.get_event_loop()

        self.pending_send_tasks = dict()

        super().__init__(*args, **kwargs)

    def run(self):
        try:
            self.loop.run_until_complete(self.handle_single_msg())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        logger.debug('Kill all sub-threads first.')
        self.killall()

        pending_send_tasks = [self.pending_send_tasks[key] for key in
                              self.pending_send_tasks.keys()]
        for task in pending_send_tasks:
            self.loop.run_until_complete(task)

        logger.debug('Process all remaining items in the queue, possibly none.')
        while not self.queue.empty():
            self.loop.run_until_complete(self.send())
            logger.debug('An item has been processed.')

        logger.debug('Finally, stop the loop.')
        self.loop.stop()

    def loop_getter(self):
        return self.loop

    async def handle_single_msg(self, num_of_iteration=1):
        # Proceed if more client sessions are allowed; otherwise block.
        await self.sem.acquire()

        # Register 'send' tasks so that we have a handle on them, and can cancel
        # them gracefully on shutdown.
        send_task = self.loop.create_task(self.send(num_of_iteration))
        self.pending_send_tasks[num_of_iteration] = send_task

        # Recursively handle all messages, up to maxConcurrency
        self.handler = self.loop.create_task(
            self.handle_single_msg(num_of_iteration+1))

    async def send(self, task_dict_handle=None):
        data = bytearray(await self.queue.get(), 'utf8')
        logger.debug('Got a new message, start transmission...')

        await self.post(data)
        self.queue.task_done()

        if task_dict_handle is not None:
            self.pending_send_tasks.pop(task_dict_handle, None)

        # NOTE: here we have to decouple semaphore acquire and release
        self.sem.release()

    async def post(self, data):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data) as resp:
                    if resp.status != 200:
                        logger.warning(
                            'Transmission for the following msg failed, with a HTTP error code {}: {}'.format(
                                resp.status, data.decode('utf8')
                            ))
                    logger.debug(await resp.text())

        except Exception as err:
            logger.warning(
                'Transmission for the following msg failed, with the following exception {}: {}'.format(
                    err.__class__.__name__, data.decode('utf8')
                ))
