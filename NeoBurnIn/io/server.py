#!/usr/bin/env python
#
# Last Change: Fri Jul 20, 2018 at 04:17 PM -0400

import logging
import asyncio

from aiohttp import web

from NeoBurnIn.base import BaseServer


logger = logging.getLogger(__name__)


class GroundServer(BaseServer):
    def __init__(self, host='localhost', port=45678):
        self.host = host
        self.port = port

        self.app = web.Application()
        self.register_routes()

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)

    def loop_getter(self):
        return None

    def register_routes(self):
        pass
