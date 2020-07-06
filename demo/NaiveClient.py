#!/usr/bin/env python3
#
# Last Change: Mon Aug 20, 2018 at 09:55 PM -0400

import logging
import janus

from threading import Event
from argparse import ArgumentParser

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.client import DataClient
from NeoBurnIn.DataSource.RandUniform import RandUniformDataSource
from NeoBurnIn.io.logger import log_handler_colored_console


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A naive http client that sends pseudo-random data to given server.'
    )

    parser.add_argument(
        '--numOfChs',
        help='''
        specify number of pseudo-random channels.
        ''',
        type=int,
        default=3
    )

    parser.add_argument(
        '--sleep',
        help='''
        specify sleep time before generating next message.
        ''',
        type=float,
        default=0.5
    )

    parser.add_argument(
        '--maxConcurrency',
        help='''
        specify maximum number of allowed concurrent clients.
        ''',
        type=int,
        default=3
    )

    parser.add_argument(
        '--host',
        help='''
        specify remote server address.
        ''',
        type=str,
        default='localhost'
    )

    return parser.parse_args()


####################
# Configure logger #
####################

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler_colored_console(level=logging.DEBUG))


if __name__ == "__main__":
    args = parse_input()
    data_queue = janus.Queue()
    stop_event = Event()
    thread_list = []

    rand_data_source = RandUniformDataSource(data_queue.sync_q, stop_event,
                                             numOfChs=args.numOfChs,
                                             interval=args.sleep)
    rand_data_source.start()
    thread_list.append(rand_data_source)

    client = DataClient(data_queue.async_q, stop_event, thread_list,
                        host=args.host,
                        maxConcurrency=args.maxConcurrency)
    client.run()
