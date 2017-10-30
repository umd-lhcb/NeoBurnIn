#!/usr/bin/env python
#
# Last Change: Mon Oct 30, 2017 at 02:36 PM -0400

from time import sleep
import socket
import unittest

import sys
sys.path.insert(0, '..')

from bUrnIn.server.transmission import TransmissionServer


class NaiveTransmissionClient():
    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        self.host = host
        self.port = port

    def send(self, msg):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.sendall(bytes(msg + "\n", "utf-8"))

        finally:
            self.sock.close()


class NaiveTransmissionServer(TransmissionServer):
    def dispatcher(self, msg, address):
        self.testresults.append(msg)
        sleep(1)


class TestTransferMsg(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        self.server = NaiveTransmissionServer("", 0)
        self.server.listen()

    def test_ascii_str(self):
        self.assertEqual(self.a, 2)


if __name__ == "__main__":
    # host, port = "0.0.0.0", 4567
    # size = 20

    # server = NaiveTransmissionServer(host, port, size=1)
    # server.listen()
    unittest.main()
