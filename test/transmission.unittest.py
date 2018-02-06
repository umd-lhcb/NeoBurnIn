#!/usr/bin/env python
#
# Last Change: Tue Feb 06, 2018 at 06:55 PM -0500

import socket
import unittest

from time import sleep
from multiprocessing import Queue
from multiprocessing import Process as Container
from os import kill
from signal import SIGTERM

import sys
sys.path.insert(0, '..')

from bUrnIn.framework.server import ServerAsync


class ClientTester(object):
    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        self.host = host
        self.port = port

        self.EOM = 'EOM'

    def send(self, msg, delay=0):
        try:
            self.sock.connect((self.host, self.port))
            sleep(delay)
            self.sock.sendall(bytes(msg + self.EOM, 'utf-8'))

        # NOTE: 'finally' is for clean-up, and will be always executed after
        #       'try'.
        finally:
            pass

    def exit(self):
        self.sock.close()


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))  # Get any available port

    _, port = tcp.getsockname()
    tcp.close()

    return port


class TestTransferMsgSmSize(unittest.TestCase):
    def setUp(self):
        self.msgs = Queue()

        port = get_free_tcp_port()
        size = 3
        server = ServerAsync("", port, self.msgs, size=size)

        self.container = Container(target=server.start)
        self.container.start()
        sleep(0.5)  # Need this to make sure server is properly initialized

        self.client = ClientTester("localhost", port)

    def test_ascii_text(self):
        ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        self.client.send(ascii_text)
        self.assertEqual(self.msgs.get(), ascii_text)

    def test_utf8_text(self):
        utf8_text = "苟利国家生死以"
        self.client.send(utf8_text)
        self.assertEqual(self.msgs.get(), utf8_text)

    def doCleanups(self):
        self.client.exit()
        kill(self.container.pid, SIGTERM)


class TestTransferMsgLgSize(unittest.TestCase):
    def setUp(self):
        self.msgs = Queue()

        port = get_free_tcp_port()
        size = 81920
        server = ServerAsync("", port, self.msgs, size=size)

        self.container = Container(target=server.start)
        self.container.start()
        sleep(0.5)  # Need this to make sure server is properly initialized

        self.client = ClientTester("localhost", port)

    def test_ascii_text(self):
        ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        self.client.send(ascii_text)
        self.assertEqual(self.msgs.get(), ascii_text)

    def test_utf8_text(self):
        utf8_text = "苟利国家生死以"
        self.client.send(utf8_text)
        self.assertEqual(self.msgs.get(), utf8_text)

    def doCleanups(self):
        self.client.exit()
        kill(self.container.pid, SIGTERM)


if __name__ == "__main__":
    unittest.main()
