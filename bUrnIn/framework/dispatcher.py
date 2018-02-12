#!/usr/bin/env python
#
# Last Change: Mon Feb 12, 2018 at 12:24 AM -0500

from bUrnIn.framework.base import Dispatcher
from bUrnIn.filters.base import apply_filters
from bUrnIn.filters.io import FilterLogWriter
from bUrnIn.filters.qc import FilterSplitData


class DispatcherServer(Dispatcher):
    '''
    Dispatch received data. This Dispatcher runs in a separated process.
    '''
    def __init__(self):
        self.filter_list = [FilterSplitData(), FilterLogWriter()]

    def dispatch(self):
        self.logger.info("Dispatcher starting.")
        while True:
            msg = self.queue.get()
            if msg is None:
                self.logger.info("Shutdown signal received, preparing dispatcher shutdown.")
                break

            else:
                data = self.decode(msg)
                self.filter(data)

    def decode(self, msg):
        data = msg.split('\n')
        # Remove trailing '' element if it exists
        data = data[:-1] if data[-1] == '' else data
        return data

    def filter(self, data):
        for entry in data:
            apply_filters(entry, self.filter_list)

    def email_antiflood(self, warning):
        pass
        # if self.last_sent_timestamp is None:
            # # We never sent any email before
            # self.log.critical(warning)
            # self.last_sent_timestamp = datetime.now()

        # else:
            # # If we have sent emails recently, don't send any email again
            # # This is to prevent email flooding
            # delta_t = \
                # (datetime.now() - self.last_sent_timestamp).total_seconds() / 60
            # self.log.debug(delta_t)

            # if delta_t >= self.log_email_interval:
                # self.log.critical(warning)
                # # Update the timestamp, only if we sent a new email.
                # self.last_sent_timestamp = datetime.now()
            # else:
                # pass
