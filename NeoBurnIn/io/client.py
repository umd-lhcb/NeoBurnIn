#!/usr/bin/env python
#
# Last Change: Thu Jul 26, 2018 at 12:32 AM -0400

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
        logger.info('Kill all sub-threads first.')
        self.killall()

        pending_tasks = asyncio.Task.all_tasks()
        for task in pending_tasks:
            task.cancel()
            self.loop.run_until_complete(task)

        logger.info('Process all remaining items in the queue, possibly none.')
        while not self.queue.empty():
            self.loop.run_until_complete(self.send())
            logger.info('An item has been processed.')

        logger.info('Finally, stop the loop.')
        self.loop.stop()

    def loop_getter(self):
        return self.loop

    async def handle_single_msg(self):
        try:
            # Proceed if more client sessions are allowed; otherwise block.
            await self.sem.acquire()

            # Schedule send msg to the remote host.
            # Functionality-wise, this is equivalent to 'asyncio.ensure_future'.
            self.loop.create_task(self.send())

            # Recursively handle all messages, up to maxConcurrency
            self.handler = self.loop.create_task(
                self.handle_single_msg())

        except Exception as err:
            logger.debug(
                'The recursive msg handler has been interrupted with the following exception: {}'.format(
                    err.__class__.__name__
                ))

    async def send(self):
        try:
            data = bytearray(await self.queue.get(), 'utf8')
            logger.debug('Got a new message, start transmission...')

            await self.post(data)
            self.queue.task_done()

            # NOTE: here we have to decouple semaphore acquire and release
            self.sem.release()

        except Exception as err:
            logger.debug(
                'The sender has been interrupted with the following exception: {}'.format(
                    err.__class__.__name__
                ))

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

        except asyncio.CancelledError:
            logging.info('Transmission canceled by cleanup sequence, adding msg back to the queue')
            await self.queue.put(data.decode('utf8'))

        except Exception as err:
            logger.warning(
                'Transmission for the following msg failed, with the following exception {}: {}'.format(
                    err.__class__.__name__, data.decode('utf8')
                ))
