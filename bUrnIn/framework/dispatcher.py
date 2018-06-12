#!/usr/bin/env python
#
# Last Change: Tue Jun 12, 2018 at 03:34 AM -0400

from bUrnIn.framework.base import Dispatcher
from bUrnIn.filters.base import apply_filters
from bUrnIn.filters.io import FilterLogWriter
from bUrnIn.filters.qa import FilterDataSplit


class DispatcherServer(Dispatcher):
    '''
    Dispatch received data. This Dispatcher runs in a separated process.
    '''
    def __init__(self, msg_queue, filter_list=[FilterDataSplit(),
                                               FilterLogWriter()]):
        self.filter_list = filter_list

        super().__init__(msg_queue)

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
