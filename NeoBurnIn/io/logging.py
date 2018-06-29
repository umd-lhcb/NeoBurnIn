#!/usr/bin/env python
#
# Last Change: Fri Jun 29, 2018 at 12:12 AM -0400
# Too bad. Impurities everywhere.

import logging
import logging.config
import logging.handlers

from BurnIn.base import standard_time_format


###################
# General helpers #
###################

def parse_size_limit(size):
    size_dict = {'B': 1, 'KB': 1024, 'MB': 1024*1024}
    size_parsed = size.split(' ')
    return int(size_parsed[0]) * size_dict[size_parsed[1]]


def configure_logger(config_dict):
    logging.config.dictConfig(config_dict)


def log_default_version(config_dict, version=1):
    config_dict['version'] = version


##############
# Formatters #
##############

def log_formatter_detailed(config_dict):
    settings = {
        'class': 'logging.Formatter',
        'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(processName)-8s %(message)s',
        'datefmt': standard_time_format
    }
    config_dict['formatters']['detailed'] = settings


############
# Handlers #
############

def log_handler_email(config_dict,
                      src_addr, dst_addrs,
                      credentials,
                      email_title='[BurnIn]: Summary / An error has occurred'
                      ):
    settings = {
        'level': 'CRITICAL',
        'class': 'logging.handlers.SMTPHandler',
        'formatter': 'detailed',
        'fromaddr': src_addr,
        'mailhost': ('smtp.gmail.com', 587),
        'toaddrs': dst_addrs,
        'subject': email_title,
        'credentials': credentials,
        'secure': ()
    }
    config_dict['handlers']['email'] = settings
