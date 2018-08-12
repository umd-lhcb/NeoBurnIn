#!/usr/bin/env python
#
# Last Change: Sat Aug 11, 2018 at 10:50 PM -0400

import logging
import datetime as dt
import aiohttp_cors

from aiohttp import web
from collections import defaultdict

from NeoBurnIn.base import BaseServer
from NeoBurnIn.base import DataStream, DataStats
from NeoBurnIn.base import standard_time_format


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
        self.stash = self.stash_create()

        super().__init__(*args, **kwargs)

    ###############
    # HTTP routes #
    ###############

    def register_routes(self):
        self.app.add_routes([
            web.post(
                '/datacollect',
                self.handler_data_collect
            ),
            web.get(
                '/get/{ch_name}',
                self.handler_get_json
            ),
            web.post(
                '/get/{ch_name}',
                self.handler_get_json
            )
        ])

        # Add CORS support
        self.cors = aiohttp_cors.setup(self.app, defaults={
            '*': aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*',
                max_age=21600
            )
        })

        for route in list(self.app.router.routes()):
            self.cors.add(route)

    async def handler_get_json(self, request):
        try:
            data_dump = {
                'time': self.stash[request.match_info['ch_name']]['time'],
                'data': self.stash[request.match_info['ch_name']]['data']
            }
            return web.json_response(data_dump)

        except Exception as err:
            logger.warning('Cannot form json response due to {}'.format(
                err.__class__.__name__
            ))
            raise web.HTTPNotFound

    async def handler_data_collect(self, request):
        msg = await request.text()
        self.dispatch(msg)
        return web.Response(text='Successfully received.')

    ############
    # Dispatch #
    ############

    def dispatch(self, msg):
        splitted = self.split_input(msg)
        for entry in splitted:
            date, ch_name, value = self.validate_input(entry)

            # Proceed only if the data entry is valid
            if date is not None:
                # Log the whole entry
                logger.info('Received: {}'.format(entry))

                # First store the data.
                results = self.stash[ch_name]['data'].append(value)
                if results is not False:
                    self.stash[ch_name]['summary'].append(results[0])

                # Now check if this data point is OK.
                if self.stash[ch_name]['data'].reference_exists:
                    mean = self.stash[ch_name]['data'].reference_mean
                    envelop = self.stash[ch_name]['data'].reference_stdev * \
                        self.stdev_range
                    if value <= mean-envelop or value >= mean+envelop:
                        logger.critical('Channel {} measured a value of {}, which is outside of {} stds.'.format(
                            ch_name, value, self.stdev_range
                        ))

                # Store the time, unconditionally.
                self.stash[ch_name]['time'].append(
                    self.convert_to_bokeh_time(date))

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
            return (None, None, None)

        try:
            date = dt.datetime.strptime(date, standard_time_format)
        except Exception:
            logger.error('Datetime is not formatted correctly: {}'.format(date))
            return (None, None, None)

        try:
            value = float(value)
        except Exception:
            logger.error('Measured value is corrupt: {}'.format(value))
            return (None, None, None)

        return (date, ch_name, value)

    @staticmethod
    def convert_to_bokeh_time(date, scale=1000):
        epoch_date = dt.datetime.utcfromtimestamp(0)
        return scale * (date - epoch_date).total_seconds()

    #############################
    # Create initial data stash #
    #############################

    def stash_create(self, overall_stats_length=10000):
        '''
        Store data. If a root-level key does not exist, create it, along with
        specified empty leaves.
        '''
        stash = defaultdict(self.default_item)
        stash['overall'] = DataStream(max_length=overall_stats_length)
        return stash

    @staticmethod
    def default_item(item_length=1000):
        return {
            'summary': DataStream(max_length=item_length),
            'time': DataStream(max_length=item_length),
            'data': DataStats(max_length=item_length)
        }
