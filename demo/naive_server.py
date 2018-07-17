#!/usr/bin/env python
#
# Last Change: Mon Jul 16, 2018 at 05:29 PM -0400

from aiohttp import web

import sys
sys.path.insert(0, '..')

routes = web.RouteTableDef()


class NaiveServer(object):
    def __init__(self, host='localhost', port=45678):
        self.host = host
        self.port = port

        self.app = web.Application()

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)

    @routes.post('/datacollect')
    async def handler_data_collect(self, request):
        data = await request.text()
        print(data)
        return web.Response(text='Successfully received')


if __name__ == "__main__":
    server = NaiveServer()
    server.run()
