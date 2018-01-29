#!/usr/bin/env python
#
# Last Change: Mon Jan 29, 2018 at 05:53 PM -0500

from multiprocessing import Process as Container

import logging
import logging.handlers
import logging.config

from bUrnIn.server.base import ChildProcessSignalHandler

_B  = 1
_KB = 1024*_B
_MB = 1024*_KB


def generate_config_listener(logfile,
                             recipients, credentials,
                             datafile,
                             datafile_max_size, datafile_backup_count):
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
                'class': 'logging.FileHandler',
                'filename': logfile,
                # 'mode': 'w',
                'formatter': 'detailed'
            },
            'console': {
                'class': 'logging.StreamHandler',
            },
            'email': {
                'class': 'logging.handlers.SMTPHandler',
                'formatter': 'detailed',
                'level': 'CRITICAL',
                'fromaddr': credentials[0],
                'mailhost': ('smtp.gmail.com', 587),
                'toaddrs': recipients,
                'subject': '[BurnIn] An error has occurred',
                'credentials': credentials,
                'secure': ()
            },
            # For logging the actual data
            'datafile': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': datafile,
                'maxBytes': datafile_max_size,
                'backupCount': datafile_backup_count
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


def generate_config_worker(queue, level='INFO'):
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'queue': {
                'class': 'logging.handlers.QueueHandler',
                'queue': queue,
            },
        },
        'root': {
            'level': level,
            'handlers': ['queue']
        },
    }
    return config


class HandlerForMultiProcesses():
    '''
    A simple handler for logging events. It runs in a dedicated listener process
    and dispatches events to loggers based on the name in the received record,
    which is then further processed by the logging system.
    '''
    def handle(self, record):
        logger = logging.getLogger(record.name)
        logger.handle(record)


class LoggerForMultiProcesses(ChildProcessSignalHandler):
    '''
    Logger for multiprocessing.
    '''
    def __init__(self, queue, stop_event,
                 logfile='/tmp/bUrnIn-server.log',
                 recipients=[None], credentials=[None, None],
                 datafile='/tmp/bUrnIn-data.csv',
                 datafile_max_size=50*_MB, datafile_backup_count=9999):
        self.signal_register()
        self.queue = queue
        self.stop_event = stop_event
        self.config = generate_config_listener(
            logfile,
            recipients, credentials,
            datafile,
            datafile_max_size, datafile_backup_count
        )

    def listen(self):
        logging.config.dictConfig(self.config)

        listener = logging.handlers.QueueListener(
            self.queue, HandlerForMultiProcesses())
        listener.start()

        self.stop_event.wait()
        listener.stop()

    def start(self):
        listener_process = Container(target=self.listen)
        listener_process.start()
        self.listener_process = listener_process
