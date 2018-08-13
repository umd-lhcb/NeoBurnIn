#!/usr/bin/env python
#
# Last Change: Mon Aug 13, 2018 at 03:42 PM -0400

import janus

from threading import Event
from argparse import ArgumentParser

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.client import DataClient
from NeoBurnIn.DataSource.RandUniform import RandUniformDataSource
from NeoBurnIn.io.logging import configure_client_logger


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A http client that configures sensors and sends collected data to remote server.'
    )

    parser.add_argument(
        '--config-file',
        help='''
        specify configuration file.
        ''',
        type=str,
        default=3
    )

    return parser.parse_args()


####################
# Configure logger #
####################

configure_client_logger()


if __name__ == "__main__":
    args = parse_input()
    data_queue = janus.Queue()
    stop_event = Event()
    thread_list = []

    rand_data_source = RandUniformDataSource(data_queue.sync_q, stop_event,
                                             numOfChs=args.numOfChs)
    rand_data_source.start(args.sleep)
    thread_list.append(rand_data_source)

    client = DataClient(data_queue.async_q, stop_event,
                        host=args.host,
                        thread_list=thread_list,
                        maxConcurrency=args.maxConcurrency)
    client.run()
