#!/usr/bin/env python
#
# Last Change: Tue Jul 31, 2018 at 09:51 AM -0400

import logging
import asyncio
import aiohttp

# from functools import partial

from NeoBurnIn.base import ThreadTerminator, BaseClient

logger = logging.getLogger(__name__)


class DataClient(ThreadTerminator, BaseClient):
    '''
    A http client that sends msgs in queue to remote server concurrently.
    It guarantees the queue is cleared on shutdown (but this cleanup operation
    may take an infinite amount of time), but does not guarantee maintaining the
    order of the messages.
    '''
    POST_API = 'datacollect'

    def __init__(self, queue, *args,
                 host='localhost', port='45678',
                 maxConcurrency=3,
                 **kwargs):
        self.queue = queue

        self.url = 'http://{}:{}/{}'.format(host, port, self.POST_API)
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

        except asyncio.CancelledError:
            logger.debug('Recursive msg handler cancellation has been requested.')

        except Exception as err:
            logger.debug(
                'Recursive msg handler has been interrupted with the following exception: {}'.format(
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

        except asyncio.CancelledError:
            logger.debug('Sender cancellation has been requested.')

        except Exception as err:
            logger.warning(
                'Sender has been interrupted with the following exception: {}'.format(
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
            logger.debug('Transmission canceled by cleanup sequence, putting the msg back to queue.')
            await self.queue.put(data.decode('utf8'))
            # We need to raise this error so that the task is marked as
            # canceled.
            raise

        except Exception as err:
            logger.warning(
                'Transmission for the following msg failed, with the following exception {}: {}'.format(
                    err.__class__.__name__, data.decode('utf8')
                ))
