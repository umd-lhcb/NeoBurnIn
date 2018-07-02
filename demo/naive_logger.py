#!/usr/bin/env python
#
# Last Change: Mon Jul 02, 2018 at 01:32 AM -0400

from configparser import SafeConfigParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from queue import Queue
from time import sleep

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.logging import LoggingThread


# Parse logger configuration
def parse_config(config_file):
    parsed = SafeConfigParser()
    parsed.read(config_file)
    return parsed


# Print file with color green
def cprint(msg):
    RESET = '\033[0m'
    GREEN = '\033[92m'
    print('{}{}{}{}'.format(RESET, GREEN, msg, RESET))


if __name__ == "__main__":
    # The configuration file will not be distributed with this repo, due to the
    # fact that it contain sensitive information i.e. password.
    # Its format is exactly the same as shown in 'server.cfg.example'.
    options = parse_config(Path('.') / 'naive_logger.cfg')

    logging_file = NamedTemporaryFile()
    logging_queue = Queue(-1)

    logging_thread = LoggingThread(
        logging_queue,
        logging_file.name, maxSize='100 MB', backupCount=1000,
        **options['log']
    )
    logging_thread.start()
    logger = logging_thread.logger

    logger.info("Test message with level info.")
    logger.warning("Test message with level WARNING.")
    logger.critical("Test message with level CRITICAL.")
    logger.critical("Test message with level CRITICAL, should be suppressed by email handler.")

    sleep(6)
    logger.critical("Test message with level CRITICAL, reprise.")

    print('Now inspect the full logging file:')
    cprint(logging_file.read().decode("utf-8").strip('\n'))

    logging_thread.stop()
    logging_file.close()
