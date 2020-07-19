#!/usr/bin/env python3
#
# Last Change: Sun Jul 19, 2020 at 11:49 PM +0800

from argparse import ArgumentParser
from queue import Queue

from NeoBurnIn.io.server import CtrlServer
from NeoBurnIn.io.logger import LoggingThread
from NeoBurnIn.base import parse_config

from rpi.burnin.USBRelay import set_relay_state, get_all_device_paths


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(
        description='A http server that controls various HW interfaces.'
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

    parser.add_argument(
        '--relay-channel',
        dest='relayChannel',
        help='''
        specify number of relay channels.
        ''',
        type=int,
        default=2
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

    # Turn on all USB relays when the server quits
    print('Turning on all USB relays...')
    for relay in get_all_device_paths():
        print('Turning on channels of relay {}'.format(relay.decode('utf-8')))
        for ch in range(args.relayChannel):
            set_relay_state(relay, ch)
            print('Channel {} is set to ON.'.format(ch))
