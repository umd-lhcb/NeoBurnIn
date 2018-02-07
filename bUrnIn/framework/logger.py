#!/usr/bin/env python
#
# Last Change: Tue Feb 06, 2018 at 07:28 PM -0500

from multiprocessing import Process as Container

import logging
import logging.handlers
import logging.config

from bUrnIn.framework.base import SignalHandler


def parse_size_limit(size):
    size_dict = {'B': 1, 'KB': 1024, 'MB': 1024*1024}
    size_parsed = size.split(' ')
    return int(size_parsed[0]) * size_dict[size_parsed[1]]


def log_queue_configure(log_queue, log_level='INFO'):
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'queue': {
                'class': 'logging.handlers.QueueHandler',
                'queue': log_queue,
            },
        },
        'root': {
            'level': log_level,
            'handlers': ['queue']
        },
    }
    logging.config.dictConfig(config)


def log_config_generate(log_file,
                        email_recipients, email_credentials,
                        data_file,
                        data_file_max_size='50 MB',
                        data_file_backup_count=9999):
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(processName)-8s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': log_file,
                'formatter': 'detailed'
            },
            'console': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
            },
            'email': {
                'class': 'logging.handlers.SMTPHandler',
                'formatter': 'detailed',
                'level': 'CRITICAL',
                'fromaddr': email_credentials[0],
                'mailhost': ('smtp.gmail.com', 587),
                'toaddrs': email_recipients,
                'subject': '[BurnIn] Summary/An error has occurred',
                'credentials': email_credentials,
                'secure': ()
            },
            # For logging the actual data
            'datafile': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': data_file,
                'maxBytes': parse_size_limit(data_file_max_size),
                'backupCount': int(data_file_backup_count)
            }
        },
        'loggers': {
            'data': {
                'handlers': ['datafile']
            }
        },
        'root': {
            'handlers': ['console', 'file', 'email']
        }
    }
    return config


class LoggingQueueHandler(object):
    '''
    A simple handler for logging events to a queue.
    '''
    def handle(self, record):
        logger = logging.getLogger(record.name)
        logger.handle(record)


class LoggerMP(SignalHandler):
    '''
    Logger for multiprocessing. This process runs in a separate process.

    '''
    def __init__(self, log_queue, log_config, stop_event):
        self.log_queue = log_queue
        self.stop_event = stop_event

        logging.config.dictConfig(log_config)

        super(LoggerMP, self).__init__()

    def start(self):
        listener = Container(target=self.listen)
        listener.start()
        self.container = listener

    def listen(self):
        listener = logging.handlers.QueueListener(
            self.log_queue, LoggingQueueHandler())
        listener.start()

        self.stop_event.wait()
        listener.stop()
