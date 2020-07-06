#!/usr/bin/env python3
#
# Last Change: Mon Jan 20, 2020 at 04:59 AM -0500

import logging

from NeoBurnIn.base import BaseDataSink

logger = logging.getLogger(__name__)


class TestSink(BaseDataSink):
    def __init__(self, host, port, entry='test'):
        self.host = host
        self.port = port
        self.entry = entry

    def on(self, ch):
        return 'http://{}:{}/{}/{}/{}'.format(
            self.host, self.port, self.entry, ch, 'on'
        )

    def off(self, ch):
        return 'http://{}:{}/{}/{}/{}'.format(
            self.host, self.port, self.entry, ch, 'off'
        )
