#!/usr/bin/env python3
#
# Last Change: Sat Jul 11, 2020 at 11:34 PM +0800

import janus
import importlib

from threading import Event
from argparse import ArgumentParser

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
        self.stop_event = Event()
        self.queue = janus.Queue()
        self.emitted_sensors = []

        self.sensors_list = sensors_list

    def init_sensors(self):
        gpio_is_inited = False

        for sensor_spec in self.sensors_list:
            for name, spec in sensor_spec.items():
                mod, cls = name.rsplit('.')
                sensor = getattr(importlib.import_module(
                    'NeoBurnIn.DataSource.' + mod), cls)
                if 'WaterAlarm' in cls or 'FireAlarm' in cls:
                    if gpio_is_inited:
                        self.emitted_sensors.append(sensor(
                            self.stop_event, self.queue.sync_q,
                            gpio_init_cleanup=False, **spec))
                    else:
                        gpio_is_inited = True
                        self.emitted_sensors.append(sensor(
                            self.stop_event, self.queue.sync_q, **spec))

                else:
                    self.emitted_sensors.append(sensor(
                        self.stop_event, self.queue.sync_q, **spec))

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
