#!/usr/bin/env python
#
# Last Change: Sun Jan 19, 2020 at 04:13 PM -0500

import logging

from NeoBurnIn.base import BaseDataSink

logger = logging.getLogger(__name__)


class TestSink(BaseDataSink):
    def __init__(self, host, port, entry='test'):
        self.host = host
        self.port = port
        self.entry = entry

    def on(self, ch):
        return 'http://{}/{}/{}/{}/{}'.format(
            self.host, self.port, self.entry, ch, 'on'
        )

    def off(self, ch):
        return 'http://{}/{}/{}/{}/{}'.format(
            self.host, self.port, self.entry, ch, 'off'
        )
