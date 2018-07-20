#!/usr/bin/env python
#
# Last Change: Fri Jul 20, 2018 at 04:20 PM -0400

import logging
import asyncio

from aiohttp import web
from random import uniform

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.server import GroundServer
from NeoBurnIn.io.logging import log_handler_console

####################
# Configure logger #
####################

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler_console(level=logging.DEBUG))


class NaiveServer(GroundServer):
    def register_routes(self):
        self.app.add_routes([
            web.post('/datacollect', self.handler_data_collect)
        ])

    def dispatch(self, msg):
        logger.info(msg)

    async def handler_data_collect(self, request):
        msg = await request.text()
        await asyncio.sleep(uniform(0, 1))
        self.dispatch(msg)
        return web.Response(text='Successfully received')


if __name__ == "__main__":
    server = NaiveServer()
    server.run()
