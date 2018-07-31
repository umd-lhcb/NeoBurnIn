#!/usr/bin/env python
#
# Last Change: Tue Jul 31, 2018 at 09:58 AM -0400

import logging

from aiohttp import web

from NeoBurnIn.base import BaseServer
from NeoBurnIn.base import stash_create


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


class DataServer(GroundServer):
    def __init__(self, *args,
                 stdev_range=3, **kwargs):
        self.stdev_range = stdev_range
        self.stash = stash_create()

        super().__init__(*args, **kwargs)

    def register_routes(self):
        self.app.add_routes([
            web.post(
                '/datacollect',
                self.handler_data_collect),
            web.get(
                '/get/{ch_name}',
                self.handler_get_json)
        ])

    async def handler_get_json(self, request):
        try:
            json = {
                'time': self.stash[request.match_info['ch_name']]['time'],
                'data': self.stash[request.match_info['ch_name']]['data']
            }
            return web.json_response(json)

        except Exception as err:
            logger.warning('Cannot form json response due to {}'.format(
                err.__class__.__name__
            ))
            raise web.HTTPNotFound

    async def handler_data_collect(self, request):
        msg = await request.text()
        self.dispatch(msg)
        return web.Response(text='Successfully received.')

    def dispatch(self, msg):
        splitted = self.split_input(msg)
        for entry in splitted:
            date, ch_name, value = self.validate_input(entry)

            # First store the data
            results = self.stash[ch_name]['data'].append(value)
            if results is not False:
                self.stash[ch_name]['summary'].append(results[0])

            # Now check if this data point is ok
            if self.stash[ch_name]['data'].reference_exists:
                mean = self.stash[ch_name]['data'].reference_mean
                envelop = self.stash[ch_name]['data'].reference_stdev * \
                    self.stdev_range
                if value <= mean-envelop or value >= mean+envelop:
                    logger.critical('Channel {} measured a value of {}, which is outside of {} stds.'.format(
                        ch_name, value, self.stdev_range
                    ))

            # Store the time, unconditionally
            self.stash[ch_name]['time'].append(date)

    @staticmethod
    def split_input(msg, delimiter='\n'):
        splitted = msg.split(delimiter)
        if splitted[-1] == '':
            return splitted[:-1]
        else:
            return splitted

    @staticmethod
    def validate_input(entry, delimiter='|'):
        try:
            date, ch_name, value = entry.split(delimiter)
        except Exception:
            logger.error('Entry not correctly delimited: {}'.format(entry))

        try:
            value = float(value)
        except Exception:
            logger.error('Measured value is corrupt: {}'.format(value))

        return (date, ch_name, value)
