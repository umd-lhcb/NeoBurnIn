#!/usr/bin/env python
#
# Last Change: Tue Jul 17, 2018 at 05:46 PM -0400

from aiohttp import web

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import BaseServer


class NaiveServer(BaseServer):
    def __init__(self, host='localhost', port=45678):
        self.host = host
        self.port = port

        self.app = web.Application()
        self.app.add_routes([
            web.post('/datacollect', self.handler_data_collect)
        ])

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)

    def dispatch(self, msg):
        print(msg)

    def loop_getter(self):
        return None

    async def handler_data_collect(self, request):
        msg = await request.text()
        self.dispatch(msg)
        return web.Response(text='Successfully received')


if __name__ == "__main__":
    server = NaiveServer()
    server.run()
