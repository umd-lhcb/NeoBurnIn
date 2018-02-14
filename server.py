#!/usr/bin/env python
#
# Last Change: Wed Feb 14, 2018 at 06:52 PM -0500

from configparser import SafeConfigParser
from os import getcwd
from os.path import join
from multiprocessing import Queue, Event

from bUrnIn.framework.logger import log_config_generate
from bUrnIn.framework.logger import LoggerMP
from bUrnIn.framework.dispatcher import DispatcherServer
from bUrnIn.framework.server import ServerAsync


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
    msg_queue  = Queue()
    log_queue  = Queue()
    stop_event = Event()

    ####################
    # Configure logger #
    ####################
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
    dispatcher = DispatcherServer(msg_queue)
    dispatcher.start()

    ############################################
    # Start the TCP server on the main process #
    ############################################
    server = ServerAsync(
        opts['main']['ip'], int(opts['main']['port']),
        msg_queue,
        timeout=int(opts['main']['timeout'])
    )
    server.start()

    ###########
    # Cleanup #
    ###########
    dispatcher.container.join()
    stop_event.set()
    logger.container.join()
