#!/usr/bin/env python3
#
# Last Change: Sat Jul 11, 2020 at 11:34 PM +0800

import janus
import importlib

from threading import Event
from queue import Queue
from argparse import ArgumentParser

from NeoBurnIn.io.client import CtrlClient
from NeoBurnIn.io.logger import LoggingThread
from NeoBurnIn.base import parse_config
from NeoBurnIn.functional import parse_directive


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


#########
# Setup #
#########

args = parse_input()
options = parse_config(args.configFile)

logging_queue = Queue()
logging_thread = LoggingThread(logging_queue, **options['log'])

sensors = SensorEmitter(options['sensors'])
sensors.init_sensors()

controllers = ControllerEmitter(options['controllers'])
controllers.init_controllers()
ctrl_rules = parse_directive(options['ctrlRules'])

client = CtrlClient(
    sensors.queue.async_q, sensors.stop_event, sensors.emitted_sensors,
    controllers=controllers.emitted_sinks, ctrlRules=ctrl_rules,
    **options['client']
)

if __name__ == "__main__":
    logging_thread.start()
    sensors.start()
    client.run()
    logging_thread.stop()
