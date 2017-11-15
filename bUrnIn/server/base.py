#!/usr/bin/env python
#
# Last Change: Wed Nov 15, 2017 at 11:58 AM -0500

import signal


class ChildProcessSignalHandler():
    '''
    A base server class that defers SIGINT and SIGTERM signals.
    It is assumed that any subclass will deal with above signals EXPLICITLY.
    '''
    def __init__(self):
        pass

    def signal_register(self):
        # SIGINT: Ctrl-C
        # SIGTERM: when a process is about to be killed
        signal.signal(signal.SIGINT, self.signal_handle)
        signal.signal(signal.SIGTERM, self.signal_handle)

    def signal_handle(self, signum, frame):
        print("Child process received SIGTERM/SIGINT. Igoring...")
