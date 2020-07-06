#!/usr/bin/env python3
#
# Last Change: Mon Jan 20, 2020 at 05:58 AM -0500

import logging

from rpi.burnin.USBRelay import get_all_device_paths
from NeoBurnIn.base import BaseDataSink

logger = logging.getLogger(__name__)


class RelaySink(BaseDataSink):
    def __init__(self, host, port, entry='relay',
                 automaticDiscovery=True, relayIdx=0, relayDevId=None):
        self.host = host
        self.port = port
        self.entry = entry

        if automaticDiscovery:
            relays = list(map(lambda x: x.decode('utf8'),
                              get_all_device_paths()))
            self.relay = relays[relayIdx]
        else:
            self.relay = relayDevId

    def on(self, ch):
        return 'http://{}:{}/{}/{}/{}/{}'.format(
            self.host, self.port, self.entry, self.relay, ch, 'on'
        )

    def off(self, ch):
        return 'http://{}:{}/{}/{}/{}/{}'.format(
            self.host, self.port, self.entry, self.relay, ch, 'off'
        )
