#!/usr/bin/env python
#
# Last Change: Thu Jul 26, 2018 at 10:09 AM -0400

import logging
import asyncio

from aiohttp import web
from random import uniform
from argparse import ArgumentParser

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.server import GroundServer
from NeoBurnIn.io.logging import log_handler_colored_console


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A naive http server that adds random lags per request.'
    )

    parser.add_argument(
        '--randRange',
        help='''
        specify the range of random lags.
        ''',
        type=str,
        default='1,2'
    )

    return parser.parse_args()


####################
# Configure logger #
####################

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler_colored_console(level=logging.DEBUG))


#################
# Define server #
#################

class NaiveServer(GroundServer):
    def __init__(self, randRange, *args, **kwargs):
        randLower, randUpper = randRange.split(',')
        self.randLower = float(randLower)
        self.randUpper = float(randUpper)

        super().__init__(*args, **kwargs)

    def register_routes(self):
        self.app.add_routes([
            web.post('/datacollect', self.handler_data_collect)
        ])

    def dispatch(self, msg):
        logger.info(msg)

    async def handler_data_collect(self, request):
        msg = await request.text()
        sleep_interval = uniform(self.randLower, self.randUpper)
        await asyncio.sleep(sleep_interval)
        self.dispatch(msg)
        return web.Response(
            text='Received after sleeping for {} sec.'.format(sleep_interval))


if __name__ == "__main__":
    args = parse_input()
    server = NaiveServer(args.randRange, host='0.0.0.0')
    server.run()
