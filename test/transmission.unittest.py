#!/usr/bin/env python
#
# Last Change: Thu May 10, 2018 at 03:18 PM -0400

import socket
import unittest

from time import sleep
from multiprocessing import Queue
from multiprocessing import Process as Container
from multiprocessing import Event
from os import kill
from signal import SIGTERM

import sys
sys.path.insert(0, '..')

from bUrnIn.framework.server import ServerAsync


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))  # Get any available port

    _, port = tcp.getsockname()
    tcp.close()

    return port


class ClientTester(object):
    def __init__(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        self.ip = ip
        self.port = port

        self.EOM = 'EOM'

    def send(self, msg, delay=0, corrupted=False):
        try:
            self.sock.connect((self.ip, self.port))
            sleep(delay)
            msg = msg + self.EOM if not corrupted else msg
            self.sock.sendall(bytes(msg, 'utf-8'))

        # NOTE: 'finally' is for clean-up, and will be always executed after
        #       'try'.
        finally:
            pass

    def exit(self):
        self.sock.close()


class TestTransferMsgSmSize(unittest.TestCase):
    def setUp(self):
        self.msgs = Queue()

        port = get_free_tcp_port()
        size = 3
        server = ServerAsync("", port, self.msgs, size=size)
        wait_event = Event()

        self.container = Container(target=server.start, args=(wait_event,))
        self.container.start()

        # Need this to make sure server is properly initialized
        wait_event.wait()
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
        wait_event = Event()

        self.container = Container(target=server.start, args=(wait_event,))
        self.container.start()

        wait_event.wait()
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


class TestTransTimeout(unittest.TestCase):
    def setUp(self):
        self.msgs = Queue()
        self.text = "Gou Li Guo Jia Sheng Si Yi"

        port = get_free_tcp_port()
        server = ServerAsync("", port, self.msgs, max_retries=2, timeout=0.1)
        wait_event = Event()

        self.container = Container(target=server.start, args=(wait_event,))
        self.container.start()

        wait_event.wait()
        self.client = ClientTester("localhost", port)

    def test_timeout_error(self):
        print('\nTesting Timeout, expecting 3 log lines:')
        self.client.send(self.text, delay=0.5)
        self.assertEqual(self.msgs.qsize(), 0)

    def test_timeout_once(self):
        print('\nTesting Timeout once, expecting 1 log line:')
        self.client.send(self.text, delay=0.2)
        self.assertEqual(self.msgs.get(), self.text)

    def test_msg_corrupted(self):
        print('\nTesting corrupted msg, expecting 3 log lines:')
        self.client.send(self.text, corrupted=True)
        sleep(0.3)
        self.assertEqual(self.msgs.qsize(), 0)

    def doCleanups(self):
        self.client.exit()
        kill(self.container.pid, SIGTERM)


if __name__ == "__main__":
    pass
    #unittest.main()
