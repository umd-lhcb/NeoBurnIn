#!/usr/bin/env python
#
# Last Change: Sun Oct 29, 2017 at 06:32 PM -0400

import signal


class BaseSignalHandler():
    def __init__(self):
        self.signal_handle()

    def signal_handle(self):
        self.stop = False

        # SIGINT: Ctrl-C
        # SIGTERM: when a process is about to be killed
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.stop = True
