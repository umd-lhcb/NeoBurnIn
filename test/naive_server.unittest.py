#!/usr/bin/env python
#
# Last Change: Mon Oct 30, 2017 at 08:59 PM -0400

from time import sleep
from multiprocessing import Process

import socket
import unittest
import os
import signal

import sys
sys.path.insert(0, '..')

from bUrnIn.server.transmission import TransmissionServer


class NaiveTransmissionClient():
    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        self.host = host
        self.port = port

    def send(self, msg, delay=0):
        sleep(delay)
        try:
            self.sock.connect((self.host, self.port))
            self.sock.sendall(bytes(msg + "\n", "utf-8"))

        # NOTE: 'finally' is for clean-up, and will be always executed after
        #       'try'.
        finally:
            pass

    def exit(self):
        self.sock.close()


class NaiveTransmissionServer(TransmissionServer):
    def dispatcher(self, msg, address, err=None):
        msg = msg[:-1]    # Remove the '\n' character
        print(msg)


def server_loop(port, size, lock=None):
    server = NaiveTransmissionServer("localhost", port, size=size)
    server.listen()


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    _, port = tcp.getsockname()
    tcp.close()

    return port


class TestTransferMsgSmSize(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        self.server_port = get_free_tcp_port()
        self.server = Process(target=server_loop, args=(self.server_port, 3))
        self.server.start()

        self.client = NaiveTransmissionClient("localhost", self.server_port)

    def test_ascii_text(self):
        ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        self.client.send(ascii_text)
        # self.assertEqual(self.testresults.get(), ascii_text)

    def tearDown(self):
        self.client.exit()
        os.kill(self.server.pid, signal.SIGTERM)


if __name__ == "__main__":
    unittest.main(failfast=True)
