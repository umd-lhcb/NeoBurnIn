#!/usr/bin/env python
#
# Last Change: Sun Jan 19, 2020 at 12:41 AM -0500

from argparse import ArgumentParser
from queue import Queue

from NeoBurnIn.io.server import CtrlServer
from NeoBurnIn.io.logger import LoggingThread
from NeoBurnIn.base import parse_config


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A http server that stores collected data and streams them via a json interface.'
    )

    parser.add_argument(
        '--config-file',
        dest='configFile',
        help='''
        specify configuration file.
        ''',
        type=str,
        default='CtrlServer.yml'
    )

    return parser.parse_args()


#########
# Setup #
#########

args = parse_input()
options = parse_config(args.configFile)

logging_queue = Queue()
logging_thread = LoggingThread(logging_queue, **options['log'])

server = CtrlServer(**options['server'])

if __name__ == "__main__":
    logging_thread.start()
    server.run()
    logging_thread.stop()
