#!/usr/bin/env python
#
# Last Change: Tue Jul 17, 2018 at 11:00 AM -0400

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

    async def send(self, msg):
        async with aiohttp.ClientSession() as session:
            async with session.put(self.url,
                                   data=bytearray(msg, 'utf8')) as resp:
                print(resp.status)
                print(await resp.text())


if __name__ == "__main__":
    client = NaiveClient()
    while True:
        try:
            msg = msg_gen(sys.argv[1])
            print(msg)
            client.send(msg)
            sleep(1)

        except KeyboardInterrupt:
            break
