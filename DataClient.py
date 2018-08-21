#!/usr/bin/env python
#
# Last Change: Mon Aug 20, 2018 at 09:55 PM -0400

import janus
import importlib

from threading import Event
from argparse import ArgumentParser

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.client import DataClient
from NeoBurnIn.io.logger import configure_client_logger
from NeoBurnIn.base import parse_config


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A http client that configures sensors and sends collected data to remote server.'
    )

    parser.add_argument(
        '--config-file',
        dest='configFile',
        help='''
        specify configuration file.
        ''',
        type=str,
        default='DataClient.yml'
    )

    return parser.parse_args()


###########
# Helpers #
###########

class SensorEmitter(object):
    def __init__(self, sensors_list):
        self.queue = janus.Queue()
        self.stop_event = Event()
        self.emitted_sensors = []

        self.sensors_list = sensors_list

    def init_sensors(self):
        for sensor_spec in self.sensors_list:
            for name, spec in sensor_spec.items():
                mod, cls = name.rsplit('.')
                sensor = getattr(importlib.import_module(
                    'NeoBurnIn.DataSource.' + mod), cls)
                self.emitted_sensors.append(sensor(
                    self.queue.sync_q, self.stop_event, **spec))

    def start(self):
        for sensor in self.emitted_sensors:
            sensor.start()


#########
# Setup #
#########

args = parse_input()
options = parse_config(args.configFile)

configure_client_logger(**options['log'])

sensors = SensorEmitter(options['sensors'])
sensors.init_sensors()

client = DataClient(
    sensors.queue.async_q, sensors.stop_event, sensors.emitted_sensors,
    **options['client']
)

if __name__ == "__main__":
    sensors.start()
    client.run()
