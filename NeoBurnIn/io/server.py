#!/usr/bin/env python
#
# Last Change: Mon Jun 29, 2020 at 02:46 AM +0800

import logging
import datetime as dt
import aiohttp_cors
import aiojobs
import asyncio

from aiohttp import web
from collections import defaultdict
from datetime import datetime

from rpi.burnin.USBRelay import set_relay_state, ON, OFF
from rpi.burnin.USBRelay import get_all_device_paths
from labSNMP.wrapper.Wiener import WienerControl

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
        web.run_app(self.app, host=self.host, port=self.port, access_log=None)

    def loop_getter(self):
        return None

    def register_routes(self):
        pass


class DataServer(GroundServer):
    def __init__(self, *args,
                 stdevRange=3, thermChName='THERM', thermAlarmThresh=60,
                 heartBeatInterval=360, checkHeatbeatInterval=60,  # in seconds
                 **kwargs):
        self.stdevRange = stdevRange
        self.thermChName = thermChName
        self.thermAlarmThresh = thermAlarmThresh
        self.heartBeatInterval = heartBeatInterval
        self.checkHeatbeatInterval = checkHeatbeatInterval

        self.stash = self.stash_create()
        self.last_received = datetime.now()

        super().__init__(*args, **kwargs)

    ###############
    # App factory #
    ###############

    async def app_factory(self):
        self.scheduler = await aiojobs.create_scheduler()
        await self.scheduler.spawn(self.check_heartbeat())
        return self.app

    def run(self):
        web.run_app(self.app_factory(),
                    host=self.host, port=self.port, access_log=None)

    ###########################################
    # Check whether the sender is still alive #
    ###########################################

    async def check_heartbeat(self):
        while True:
            now = datetime.now()
            time_delta = (now-self.last_received).total_seconds()
            logger.info('Checking if client is alive at {}'.format(
                now.strftime(standard_time_format)
            ))

            if time_delta >= self.heartBeatInterval:
                logger.critical('Current time is {}. The client has been inactive for {} seconds!'.format(
                    now.strftime(standard_time_format), time_delta))

            await asyncio.sleep(self.checkHeatbeatInterval)

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
                self.handler_stats_timeseries
            ),
            web.post(
                '/get/{ch_name}',
                self.handler_stats_timeseries
            ),
            web.post(
                '/stats/timeseries/{ch_name}',
                self.handler_stats_timeseries
            ),
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

    async def handler_stats_timeseries(self, request):
        ch_name = request.match_info['ch_name']

        try:
            data_dump = {
                'time': self.stash[ch_name]['time'],
                'data': self.stash[ch_name]['data'],
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

                # First check if this data point is OK.
                if ch_name == self.thermChName:  # Thermal threshold check
                    if value >= self.thermAlarmThresh:
                        logger.critical('Over temperature! The current reading of {} deg C is greater than threshold {} deg C'.format(value, self.thermAlarmThresh))

                elif self.stash[ch_name]['data'].reference_exists:
                    mean = self.stash[ch_name]['data'].reference_mean
                    envelop = self.stash[ch_name]['data'].reference_stdev * \
                        self.stdevRange
                    if value <= mean-envelop or value >= mean+envelop:
                        logger.critical('Channel {} measured a value of {}, which is outside of {} stds.'.format(
                            ch_name, value, self.stdevRange
                        ))

                # Store the data and time
                self.stash[ch_name]['data'].append(value)
                self.stash[ch_name]['time'].append(
                    self.convert_to_bokeh_time(date))

                # Update heart beat
                self.last_received = datetime.now()

    @staticmethod
    def split_input(msg, delimiter='\n'):
        splitted = msg.split(delimiter)
        return splitted[:-1] if splitted[-1] == '' else splitted

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

    def stash_create(self):
        '''
        Store data. If a root-level key does not exist, create it, along with
        specified empty leaves.
        '''
        return defaultdict(self.default_item)

    @staticmethod
    def default_item(item_length=1000):
        return {
            'time': DataStream(max_length=item_length),
            'data': DataStats(max_length=item_length),
        }


class CtrlServer(GroundServer):
    def __init__(self, *args,
                 minTimeOut=60, psuChannels=list(range(1, 13)), **kwargs):
        self.minTimeOut = minTimeOut
        self.psuChannels = [str(i) for i in psuChannels]

        self.relay_timer = None
        self.test_timer = None
        self.psu_timer = None

        super().__init__(*args, **kwargs)

    ###############
    # HTTP routes #
    ###############

    def register_routes(self):
        self.app.add_routes([
            web.post(
                '/relay/{dev_name}/{ch_name}/{state}',
                self.handler_relay_ctrl
            ),
            web.post(
                '/relay/list',
                self.handler_relay_list
            ),
            web.post(
                '/psu/{dev_ip_addr}/{ch_name}/{state}',
                self.handler_psu_ctrl
            ),
            web.post(
                '/test/{ch_name}/{state}',
                self.handler_test
            ),
        ])

    async def handler_relay_ctrl(self, request):
        dev_name = bytes(request.match_info['dev_name'], 'utf-8')
        ch_name = int(request.match_info['ch_name'])
        raw_state = request.match_info['state']
        state = self.translate_relay_state(raw_state)

        allowed_to_control = self.execute_if_not_too_recent(
            'relay_timer', self.minTimeOut)

        if not allowed_to_control:
            logger.warning('Operation denied for changing relay state to {}'.format(
                raw_state
            ))
            return web.Response(text='Operation denied: Previous operation too recent.')

        elif state:
            try:
                ret_code = set_relay_state(dev_name, ch_name, state)
                logger.info('Turning {} USB relay channel {}'.format(
                    raw_state.lower(), ch_name))

                # NOTE: The magic number 9 indicates when the relay control
                # operation was successful.
                if ret_code != 9:
                    logger.critical('Relay control failed with error code: {}'.format(
                        ret_code
                    ))
                    return web.Response(text='Failed with error code {}'.format(
                        ret_code
                    ))
                else:
                    return web.Response(text='Success')

            except Exception as err:
                warning = 'Relay control error: {}'.format(
                    err.__class__.__name__
                )
                logger.warning(warning)
                return web.Response(text=warning)

        else:
            return web.Response(text='Invalid state: {}'.format(raw_state))

    async def handler_relay_list(self, request):
        devs = '\n'.join([p.decode('utf-8') for p in get_all_device_paths()])
        return web.Response(text=devs)

    async def handler_psu_ctrl(self, request):
        dev_ip_addr = request.match_info['dev_ip_addr']
        ch_name = request.match_info['ch_name']
        state = request.match_info['state']

        allowed_to_control = self.execute_if_not_too_recent(
            'psu_timer', self.minTimeOut)

        psu = WienerControl(dev_ip_addr)

        if not allowed_to_control:
            logger.warning('Operation denied for changing PSU channel {} to state {}'.format(
                ch_name, state
            ))
            return web.Response(text='Operation denied: Previous operation too recent.')

        elif state == 'on':
            if ch_name == 'all':
                for c in self.psuChannels:
                    psu.PowerOnCh(c)
            else:
                psu.PowerOnCh(ch_name)

            logger.info('Turning {} PSU channel {}'.format(state, ch_name))

        elif state == 'off':
            if ch_name == 'all':
                for c in self.psuChannels:
                    psu.PowerOffCh(c)
            else:
                psu.PowerOffCh(ch_name)
            logger.info('Turning {} PSU channel {}'.format(state, ch_name))

        else:
            return web.Response(text='Unknown state: {}'.format(state))

        return web.Response(text='Success')

    async def handler_test(self, request):
        ch_name = request.match_info['ch_name']
        state = request.match_info['state']

        allowed_to_control = self.execute_if_not_too_recent(
            'test_timer', self.minTimeOut
        )

        if not allowed_to_control:
            logger.warning('Test command denied: Too frequent.')
            return web.Response(text='Operation denied: Previous operation too recent.')

        else:
            logger.info('Test command with channel: {} and state: {}'.format(
                ch_name, state
            ))
            return web.Response(text='Success')

    ###############################
    # Helpers for device controls #
    ###############################

    def execute_if_not_too_recent(self, timer_name, timer_period):
        cur_time = datetime.now()

        prev_time = getattr(self, timer_name)
        if prev_time:
            if (cur_time-prev_time).total_seconds() >= timer_period:
                setattr(self, timer_name, cur_time)
                return True
            else:
                return False

        else:
            setattr(self, timer_name, cur_time)
            return True

    @staticmethod
    def translate_relay_state(state):
        if state.lower() == 'off':
            return OFF
        elif state.lower() == 'on':
            return ON
        else:
            return None

    #######################################
    # Implement required abstract methods #
    #######################################

    def dispatch(self):
        pass
