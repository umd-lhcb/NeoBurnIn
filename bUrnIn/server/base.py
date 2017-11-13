#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 11:28 AM -0500

import signal


class BaseSignalHandler():
    '''
    A base server class that defers SIGINT and SIGTERM signals.
    It is assumed that any subclass will deal with above signals EXPLICITLY.
    '''
    def __init__(self):
        self.stop = False

        # SIGINT: Ctrl-C
        # SIGTERM: when a process is about to be killed
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.stop = True
