#!/usr/bin/env python
#
# Last Change: Mon Aug 13, 2018 at 04:14 PM -0400

import janus

from threading import Event
from argparse import ArgumentParser
from pathlib import Path
from configparser import ConfigParser

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.client import DataClient
from NeoBurnIn.DataSource.RandUniform import RandUniformDataSource
from NeoBurnIn.io.logging import configure_client_logger


########################
# Parse arguments/file #
########################

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
        default='DataClient.cfg'
    )

    return parser.parse_args()


def parse_config(config_file):
    file = Path(config_file)
    if file.exists():
        parsed = ConfigParser()
        parsed.read(config_file)
        return parsed
    else:
        print("{}: configuration file does not exist.".format(config_file))
        sys.exit(1)


if __name__ == "__main__":
    # Read from input
    args = parse_input()
    cfg = parse_config(args.configFile)

    data_queue = janus.Queue()
    stop_event = Event()

    thread_list = []

    # rand_data_source = RandUniformDataSource(data_queue.sync_q, stop_event,
                                             # numOfChs=args.numOfChs)
    # rand_data_source.start(args.sleep)
    # thread_list.append(rand_data_source)

    # client = DataClient(data_queue.async_q, stop_event,
                        # host=args.host,
                        # thread_list=thread_list,
                        # maxConcurrency=args.maxConcurrency)
    # client.run()
