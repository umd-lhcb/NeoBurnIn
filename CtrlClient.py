#!/usr/bin/env python
#
# Last Change: Sun Jan 19, 2020 at 04:16 PM -0500

import janus
import importlib

from threading import Event
from argparse import ArgumentParser

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.client import CtrlClient
from NeoBurnIn.io.logger import configure_client_logger
from NeoBurnIn.base import parse_config


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A http client that configures sensors and sends collected data and control commands to remote servers.'
    )

    parser.add_argument(
        '--config-file',
        dest='configFile',
        help='''
        specify configuration file.
        ''',
        type=str,
        default='CtrlClient.yml'
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
        for sensor_spec in self.sensors_list:
            for name, spec in sensor_spec.items():
                mod, cls = name.rsplit('.')
                sensor = getattr(importlib.import_module(
                    'NeoBurnIn.DataSource.' + mod), cls)
                self.emitted_sensors.append(sensor(
                    self.stop_event, self.queue.sync_q, **spec))

    def start(self):
        for sensor in self.emitted_sensors:
            sensor.start()


class ControllerEmitter(object):
    def __init__(self, controllers_dict):
        self.emitted_sinks = {}

        self.controllers_dict = controllers_dict

    def init_controllers(self):
        for label, controller_spec in self.controllers_dict.items():
            for name, spec in controller_spec.items():
                mod, cls = name.rsplit('.')
                controller = getattr(importlib.import_module(
                    'NeoBurnIn.DataSink.' + mod), cls)
                self.emitted_sinks[label] = controller(**spec)

        return self.emitted_sinks


#########
# Setup #
#########

args = parse_input()
options = parse_config(args.configFile)

configure_client_logger(**options['log'])

sensors = SensorEmitter(options['sensors'])
sensors.init_sensors()

client = CtrlClient(
    sensors.queue.async_q, sensors.stop_event, sensors.emitted_sensors,
    **options['client']
)

if __name__ == "__main__":
    sensors.start()
    client.run()
