#!/usr/bin/env python3
#
# Last Change: Mon Jul 20, 2020 at 02:09 AM +0800

from argparse import ArgumentParser

from NeoBurnIn.io.client import DataClient
from NeoBurnIn.io.logger import configure_client_logger
from NeoBurnIn.base import parse_config, SensorEmitter


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
