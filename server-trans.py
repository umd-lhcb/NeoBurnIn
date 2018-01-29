#!/usr/bin/env python
#
# Last Change: Mon Jan 29, 2018 at 06:00 PM -0500

import signal

from configparser import ConfigParser
from os import getcwd
from os.path import join
from multiprocessing import Queue, Event

from bUrnIn.server.transmission import TransmissionServerAsync
from bUrnIn.server.dispatcher import Dispatcher
from bUrnIn.server.logging import LoggerForMultiProcesses


def parse_config(cfg):
    config = ConfigParser()
    opts_dict = dict()

    config.read(cfg)

    for key in config:
        opts_dict[key] = config[key]

    return opts_dict


def on_exit(signum, frame):
    raise KeyboardInterrupt


if __name__ == "__main__":
    #######################
    # Parse configuration #
    #######################
    DEFAULT_CFG = join(getcwd(), 'server-trans.cfg')
    opts = parse_config(join(getcwd(), DEFAULT_CFG))

    ################################
    # Prepare inter-process queues #
    ################################
    msgs = Queue()
    logs = Queue()
    stop_event = Event()

    ################
    # Start logger #
    ################
    logger = LoggerForMultiProcesses(
        logs, stop_event,
        logfile=opts['log']['filename'],
        recipients=opts['email']['recipients'].split(','),
        credentials=[
            opts['email']['username'],
            opts['email']['password']
        ],
        datafile=opts['data']['filename'],
        datafile_max_size=opts['data']['max_size'],
        datafile_backup_count=opts['data']['backup_count']
    )
    logger.start()

    ####################
    # Start dispatcher #
    ####################
    dispatcher = Dispatcher(msgs, logs,
        log_level=opts['log']['level'],
        log_email_interval=float(opts['email']['interval']),
        hardware_failure=float(opts['filter']['hardware_failure']),
        channel_failure=float(opts['filter']['channel_failure'])
    )
    dispatcher.start()

    #################################################
    # Handle SIGTERM and SIGINT on the main process #
    #################################################
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    ############################################
    # Start the TCP server on the main process #
    ############################################
    server = TransmissionServerAsync(
        opts['main']['ip'], int(opts['main']['port']),
        msgs, logs,
        timeout=int(opts['main']['timeout'])
    )
    server.listen()

    ###########
    # Cleanup #
    ###########
    dispatcher.dispatcher_process.join()
    stop_event.set()
    logger.listener_process.join()
