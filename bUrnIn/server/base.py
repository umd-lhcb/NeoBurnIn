#!/usr/bin/env python
#
# Last Change: Mon Oct 30, 2017 at 12:49 PM -0400

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


class BaseLogger():
    '''
    A base logger that
    '''
    def __init__(self):
        pass
