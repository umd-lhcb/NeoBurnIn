#!/usr/bin/env python
#
# Last Change: Tue Jul 17, 2018 at 12:46 PM -0400

from aiohttp import web

import sys
sys.path.insert(0, '..')


class NaiveServer(object):
    def __init__(self, host='localhost', port=45678):
        self.host = host
        self.port = port

        self.app = web.Application()
        self.app.add_routes([
            web.post('/datacollect', self.handler_data_collect)
        ])

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)

    async def handler_data_collect(self, request):
        data = await request.text()
        print(data)
        return web.Response(text='Successfully received')


if __name__ == "__main__":
    server = NaiveServer()
    server.run()
