#!/usr/bin/env python
#
# Last Change: Thu Jun 28, 2018 at 11:06 PM -0400

import logging
import logging.config

from tempfile import NamedTemporaryFile
from collections import defaultdict

import sys
sys.path.insert(0, '..')

from bUrnIn.base import nested_dict
from bUrnIn.io.logging import log_email_configure

# Configure logger
logger_settings = nested_dict()
log_email_configure(logger_settings,
                    'burnin.umd.lhb@gmail.com',
                    ['syp@umd.edu'],
                    'burnin@umd@lhcb',
                    )
logging.config.dictConfig(logger_settings)


def cprint(msg):
    RESET = '\033[0m'
    GREEN = '\033[92m'
    print('{}{}{}{}'.format(RESET, GREEN, msg, RESET))


if __name__ == "__main__":
    log_file = NamedTemporaryFile()
    data_file = NamedTemporaryFile()

    logger = logging.getLogger('log')
    datalogger = logging.getLogger('data')

    logger.warning("Test message from 'log' logger.")
    datalogger.warning("Test message from 'data' logger.")
    logger.critical("Critical test message from 'log' logger.")

    print(log_file.read().decode("utf-8").strip('\n'))
    cprint(data_file.read().decode("utf-8").strip('\n'))

    log_file.close()
    data_file.close()
