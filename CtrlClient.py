#!/usr/bin/env python3
#
# Last Change: Mon Jul 20, 2020 at 02:11 AM +0800

import importlib

from queue import Queue
from argparse import ArgumentParser

from NeoBurnIn.io.client import CtrlClient
from NeoBurnIn.io.logger import LoggingThread
from NeoBurnIn.base import parse_config, SensorEmitter
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
