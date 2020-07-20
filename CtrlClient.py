#!/usr/bin/env python3
#
# Last Change: Mon Jul 20, 2020 at 04:04 PM +0800

import importlib

from queue import Queue
from argparse import ArgumentParser

from NeoBurnIn.io.client import CtrlClient
from NeoBurnIn.io.logger import LoggingThread
from NeoBurnIn.base import parse_config, SensorEmitter
from NeoBurnIn.functional import parse_directive

from rpi.burnin.USBRelay import set_relay_state, get_all_device_paths


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

def emit_controller(controllers_dict):
    emitted_sinks = {}

    for label, controller_spec in controllers_dict.items():
        for name, spec in controller_spec.items():
            mod, cls = name.rsplit('.')
            controller = getattr(importlib.import_module(
                'NeoBurnIn.DataSink.' + mod), cls)
            emitted_sinks[label] = controller(**spec)

    return emitted_sinks


#########
# Setup #
#########

args = parse_input()
options = parse_config(args.configFile)

logging_queue = Queue()
logging_thread = LoggingThread(logging_queue, **options['log'])

sensors = SensorEmitter(options['sensors'])
sensors.init_sensors()

controllers = emit_controller(options['controllers'])
ctrl_rules = parse_directive(options['ctrlRules'])

client = CtrlClient(
    sensors.queue.async_q, sensors.stop_event, sensors.emitted_sensors,
    controllers=controllers, ctrlRules=ctrl_rules,
    **options['client']
)

if __name__ == "__main__":
    logging_thread.start()
    sensors.start()
    client.run()
    logging_thread.stop()

    # Turn on all USB relays when the client quits
    print('Turning on all USB relays...')
    for relay in get_all_device_paths():
        print('Turning on channels of relay {}'.format(relay.decode('utf-8')))
        for ch in range(args.relayChannel):
            set_relay_state(relay, ch)
            print('Channel {} is set to ON.'.format(ch))
