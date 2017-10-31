#!/usr/bin/env python
#
# Last Change: Mon Oct 30, 2017 at 03:13 PM -0400

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
            sleep(1)

        # Exit with a special code for testing
        sys.exit(13)


def server_loop():
    handler = SignalHandler()
    handler.start()


class TestKill(unittest.TestCase):
    def test_kill_by_SIGINT(self):
        server = Process(target=server_loop, args=())
        server.start()
        sleep(1.5)

        os.kill(server.pid, signal.SIGINT)
        server.join()

        self.assertEqual(13, server.exitcode)

    def test_kill_by_SIGTERM(self):
        server = Process(target=server_loop, args=())
        server.start()
        sleep(1.5)

        os.kill(server.pid, signal.SIGTERM)
        server.join()

        self.assertEqual(13, server.exitcode)


if __name__ == "__main__":
    unittest.main()
