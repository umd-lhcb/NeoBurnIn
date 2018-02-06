#!/usr/bin/env python
#
# Last Change: Mon Feb 05, 2018 at 07:25 PM -0500

from configparser import SafeConfigParser
from os import getcwd
from os.path import join
from multiprocessing import Queue, Event

from bUrnIn.framework.server import ServerAsync
from bUrnIn.framework.dispatcher import DispatcherServer
from bUrnIn.framework.logger import LoggerMP
from bUrnIn.framework.logger import log_queue_configure
from bUrnIn.framework.logger import log_config_generate


def parse_config(config):
    parsed = SafeConfigParser()
    parsed.read(config)
    return parsed


if __name__ == "__main__":
    #######################
    # Parse configuration #
    #######################
    config = join(getcwd(), 'server.cfg')
    opts = parse_config(join(getcwd(), config))

    ################################
    # Prepare inter-process queues #
    ################################
    msg_queue  = Queue(-1)
    log_queue  = Queue(-1)
    stop_event = Event()

    ####################
    # Configure logger #
    ####################
    log_queue_configure(log_queue, opts['log']['level'])
    log_config = log_config_generate(
        opts['log']['filename'],
        opts['email']['recipients'].split(','),
        [opts['email']['username'], opts['email']['password']],
        opts['data']['filename'],
        data_file_max_size=opts['data']['max_size'],
        data_file_backup_count=opts['data']['backup_count']
    )

    ################
    # Start logger #
    ################
    logger = LoggerMP(log_queue, log_config, stop_event)
    logger.start()

    ####################
    # Start dispatcher #
    ####################
    dispatcher = DispatcherServer(msg_queue, 'queue', 'data')
    dispatcher.start()

    ############################################
    # Start the TCP server on the main process #
    ############################################
    server = ServerAsync(opts['main']['ip'], int(opts['main']['port']),
        msg_queue, 'queue',
        timeout=int(opts['main']['timeout'])
    )
    server.start()

    ###########
    # Cleanup #
    ###########
    dispatcher.process.join()
    stop_event.set()
    logger.process.join()
