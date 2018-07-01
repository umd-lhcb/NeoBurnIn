#!/usr/bin/env python
#
# Last Change: Sun Jul 01, 2018 at 12:08 AM -0400
# Too bad. Impurities everywhere.

import logging
import logging.config
import logging.handlers

from NeoBurnIn.base import standard_time_format
from NeoBurnIn.base import nested_dict


###################
# General helpers #
###################

def parse_size_limit(size):
    size_dict = {'B': 1, 'KB': 1024, 'MB': 1024*1024}
    size_parsed = size.split(' ')
    return int(size_parsed[0]) * size_dict[size_parsed[1]]


def configure_logger(
    log_file,
    src_addr, dst_addrs, credentials,
    data_file, data_file_max_size, data_file_backup_count
):
    config_dict = nested_dict()

    log_default_version(config_dict)
    log_formatter_detailed(config_dict)

    log_handler_console(config_dict)
    log_handler_file(config_dict, log_file)
    log_handler_email(config_dict, src_addr, dst_addrs, credentials)
    log_handler_data(config_dict,
                     data_file,
                     data_file_max_size, data_file_backup_count)

    config_dict['loggers']['log']  = {'handlers': ['console', 'file', 'email']}
    config_dict['loggers']['data'] = {'handlers': ['datafile']}

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

def log_handler_console(config_dict, level='WARNING'):
    settings = {
        'level': level,
        'class': 'logging.StreamHandler'
    }
    config_dict['handlers']['console'] = settings


def log_handler_file(config_dict, log_file, formatter='detailed'):
    settings = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': log_file,
        'formatter': formatter
    }
    config_dict['handlers']['file'] = settings


def log_handler_email(config_dict,
                      src_addr, dst_addrs,
                      credentials,
                      level='CRITICAL',
                      email_title='[BurnIn]: Summary / An error has occurred'
                      ):
    settings = {
        'level': level,
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


# This is for data logging
def log_handler_data(config_dict,
                     data_file,
                     data_file_max_size, data_file_backup_count):
    settings = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': data_file,
        'maxBytes': parse_size_limit(data_file_max_size),
        'backupCount': int(data_file_backup_count)
    }
    config_dict['handlers']['datafile'] = settings
