#!/usr/bin/env python
#
# Last Change: Tue Aug 14, 2018 at 10:41 AM -0400

import logging
import queue

from tempfile import NamedTemporaryFile
from time import sleep

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.logging import LoggingThread
from NeoBurnIn.base import parse_config


###########
# Helpers #
###########

# Print file with color green
def cprint(msg):
    RESET = '\033[0m'
    GREEN = '\033[92m'
    print('{}{}{}{}'.format(RESET, GREEN, msg, RESET))


####################
# Configure logger #
####################

logger = logging.getLogger()


#########
# Setup #
#########

# The configuration file will not be distributed with this repo, due to the
# fact that it contain sensitive information i.e. password.
options = parse_config('NaiveLogger.yml')

logging_file = NamedTemporaryFile()
logging_queue = queue.Queue()

logging_thread = LoggingThread(
    logging_queue,
    logging_file.name, maxSize='100 MB', backupCount=1000,
    **options['log']
)

if __name__ == "__main__":
    logging_thread.start()

    # Note that logging handling is in a separate thread, so that printout may
    # be out of order.
    logger.info("Test message with level info.")
    logger.warning("Test message with level WARNING.")
    logger.critical("Test message with level CRITICAL.")
    print('This message should be printed out immediately by the master thread.')
    logger.critical("Test message with level CRITICAL, should be suppressed by email handler.")

    sleep(6)
    logger.critical("Test message with level CRITICAL, reprise.")

    logging_thread.stop()

    print('Now inspect the full logging file:')
    cprint(logging_file.read().decode("utf-8").strip('\n'))
    logging_file.close()
