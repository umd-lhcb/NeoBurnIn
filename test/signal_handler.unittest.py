#!/usr/bin/env python
#
# Last Change: Tue Oct 31, 2017 at 12:10 AM -0400

from time import sleep
from multiprocessing import Process

import unittest
import os
import signal

import sys
sys.path.insert(0, '..')

from bUrnIn.server.base import BaseSignalHandler


class SignalHandler(BaseSignalHandler):
    def start(self):
        while not self.stop:
            sleep(1)    # This operations is likely atomic

        # Exit with a special code for testing
        sys.exit(13)


class TestKill(unittest.TestCase):
    def test_kill_by_SIGINT(self):
        handler = SignalHandler()
        server = Process(target=handler.start, args=())
        server.start()
        sleep(1.5)

        os.kill(server.pid, signal.SIGINT)
        server.join()

        self.assertEqual(13, server.exitcode)

    def test_kill_by_SIGTERM(self):
        handler = SignalHandler()
        server = Process(target=handler.start, args=())
        server.start()
        sleep(1.5)

        os.kill(server.pid, signal.SIGTERM)
        server.join()

        self.assertEqual(13, server.exitcode)


if __name__ == "__main__":
    unittest.main()
