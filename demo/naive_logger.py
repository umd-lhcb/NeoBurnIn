#!/usr/bin/env python
#
# Last Change: Thu Feb 08, 2018 at 01:15 AM -0500

import logging
import logging.config

from tempfile import NamedTemporaryFile

import sys
sys.path.insert(0, '..')

from bUrnIn.framework.logger import log_config_generate


def cprint(msg):
    RESET = '\033[0m'
    GREEN = '\033[92m'
    print('{}{}{}{}'.format(RESET, GREEN, msg, RESET))


if __name__ == "__main__":
    log_file = NamedTemporaryFile()
    data_file = NamedTemporaryFile()

    log_config = log_config_generate(
        log_file.name,
        ['syp@umd.edu', 'yipengsun@ucla.edu'],
        ['burnin.umd.lhb@gmail.com', 'burnin@umd@lhcb'],
        data_file.name,
    )
    logging.config.dictConfig(log_config)

    logger = logging.getLogger('log')
    datalogger = logging.getLogger('data')

    logger.warning("Test message from 'log' logger.")
    datalogger.warning("Test message from 'data' logger.")
    logger.critical("Critical test message from 'log' logger.")

    print(log_file.read().decode("utf-8").strip('\n'))
    cprint(data_file.read().decode("utf-8").strip('\n'))

    log_file.close()
    data_file.close()
