#!/usr/bin/env python
#
# Last Change: Tue Jul 17, 2018 at 12:44 PM -0400

import asyncio
import aiohttp

from datetime import datetime
from random import uniform
from time import sleep

import sys
sys.path.insert(0, '..')


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def msg_gen(ch_name):
    return get_current_datetime() + '|' + ch_name + '|' + str(uniform(1, 10))


class NaiveClient():
    def __init__(self, ip='localhost', port='45678'):
        self.url = 'http://{}:{}/datacollect'.format(ip, port)
        self.loop = asyncio.get_event_loop()

    async def client_send(self, msg):
        print(msg)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url,
                                   data=bytearray(msg, 'utf8')) as resp:
                print(resp.status)
                print(await resp.text())

    def send(self, msg):
        self.loop.run_until_complete(self.client_send(msg))


if __name__ == "__main__":
    client = NaiveClient()
    while True:
        try:
            msg = msg_gen(sys.argv[1])
            client.send(msg)
            sleep(1)

        except KeyboardInterrupt:
            break
