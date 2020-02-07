#!/usr/bin/env python
#
# Last Change: Fri Feb 07, 2020 at 09:21 PM +0800

import logging

from labSNMP.wrapper.Wiener import WienerControl

from NeoBurnIn.base import BaseDataSource, DataPassthru
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class CurrentMaratonDataSource(BaseDataSource):
    def __init__(self, stop_event, queue, interval, ipAddr,
                 displayName=None, psuChannels=list()):
        self.stop_event = stop_event
        self.queue = queue
        self.interval = interval
        self.displayName = displayName
        self.psuChannels = psuChannels

        self.psu = WienerControl(ipAddr)

    def run(self):
        while not self.stop_event.wait(self.interval):
            currs = self.get()
            for c in currs:
                self.queue.put(c)

    def get(self):
        result = []
        for ch in self.psuChannels:
            curr = self.psu.ChCurrent(ch)
            result.append(
                DataPassthru(time_now_formatted(), self.displayName+str(ch),
                             curr))
        return result
