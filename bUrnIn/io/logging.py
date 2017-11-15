#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 11:07 AM -0500

from multiprocessing import Process as Container

import logging
import logging.handlers
import logging.config


def generate_config_listener(filename, recipients, level, handlers):
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
                'filename': filename,
                # 'mode': 'w',
                'formatter': 'detailed'
            },
            'console': {
                'class': 'logging.StreamHandler',
            },
            'email': {
                'class': 'logging.handlers.SMTPHandler',
                'formatter': 'detailed',
                'level': 'ERROR',
                'fromaddr': 'burnin.umd.lhb@gmail.com',
                'mailhost': ('smtp.gmail.com', 587),
                'toaddrs': recipients,
                'subject': '[BurnIn] An error as occurred',
                'credentials': ("burnin.umd.lhb@gmail.com", "burnin@umd@lhcb"),
                'secure': ()
            }
        },
        'root': {
            'level': level,
            'handlers': handlers
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


class LoggerForMultiProcesses():
    '''
    Logger for multiprocessing.
    '''
    def __init__(self, queue, stop_event,
                 level='INFO', handlers=['console'],
                 filename='/tmp/bUrnIn.log', recipients=['syp@umd.edu']):
        self.queue = queue
        self.stop_event = stop_event

        self.config = generate_config_listener(
            filename, recipients, level, handlers)

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
