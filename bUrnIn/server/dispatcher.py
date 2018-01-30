#!/usr/bin/env python
#
# Last Change: Tue Jan 30, 2018 at 01:03 PM -0500

import logging
import logging.config

from multiprocessing import Process as Container
from datetime import datetime

from bUrnIn.server.base import ChildProcessSignalHandler
from bUrnIn.server.logging import generate_config_worker

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


class Dispatcher(ChildProcessSignalHandler):
    '''
    Dispatch received data. This Dispatcher runs in a separated process.
    '''
    def __init__(self,
                 msgs, logs,
                 log_level='INFO',
                 log_email_interval=60,
                 hardware_failure=5,
                 channel_failure=-1):
        self.signal_register()
        self.msgs = msgs
        self.log_email_interval = log_email_interval
        self.hardware_failure = hardware_failure
        self.channel_failure = channel_failure

        # For email anti-flooding
        self.last_sent_timestamp = None

        # Initialize loggers
        logging.config.dictConfig(generate_config_worker(logs, log_level))
        self.log = logging.getLogger()
        self.datalog = logging.getLogger('data')

    def filter(self, msg):
        entries = msg.split('\n')

        # Remove trailing '' element, if it exists
        entries = entries[:-1] if entries[-1] == '' else entries

        self.log.debug('Message processing started...')
        for entry in entries:
            try:
                # We require '|' to be the delimiter inside an entry
                date, ch_name, value = entry.split('|')[:-1]
            except Exception as err:
                self.log.error("{}: Corrupted data: {}.".format(
                    err.__class__.__name__, entry))
                break

            # Make sure the datetime is valid
            try:
                # timestamp = datetime.strptime(
                    # date, standard_time_format).timestamp()
                datetime.strptime(date, standard_time_format)
            except Exception as err:
                self.log.error("{}: Corrupted date entry: {}.".format(
                    err.__class__.__name__, date
                ))
                break

            try:
                value = float(value)

                if value >= self.hardware_failure:
                    warning = "WARNING: A hardware failure is detected: The {} reads a voltage of {}".format(
                        ch_name, value
                    )
                    self.log.error(warning)
                    self.email_antiflood(warning)
            except Exception as err:
                self.log.error("{}: Corrupted value entry: {}.".format(
                    err.__class__.__name__, value
                ))
                break

            try:
                self.datalog.info('{}, {}, {}'.format(
                    date, ch_name, value))
            except Exception as err:
                self.log.error("{}: Cannot write to CSV file.".format(
                    err.__class__.__name__
                ))
                break
        self.log.debug('Message processing finished...')

    def email_antiflood(self, warning):
        if self.last_sent_timestamp is None:
            # We never sent any email before
            self.log.critical(warning)
            self.last_sent_timestamp = datetime.now()

        else:
            # If we have sent emails recently, don't send any email again
            # This is to prevent email flooding
            delta_t = \
                (datetime.now() - self.last_sent_timestamp).total_seconds() / 60
            self.log.debug(delta_t)

            if delta_t >= self.log_email_interval:
                self.log.critical(warning)
                # Update the timestamp, only if we sent a new email.
                self.last_sent_timestamp = datetime.now()
            else:
                pass

    def dispatch(self):
        while True:
            data = self.msgs.get()

            if data is None:
                self.log.debug("Shutdown signal received, Prepare dispatcher shutdown.")
                break
            else:
                self.filter(data)

    def start(self):
        dispatcher = Container(target=self.dispatch)
        dispatcher.start()
        self.dispatcher_process = dispatcher
