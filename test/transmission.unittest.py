#!/usr/bin/env python
#
# Last Change: Tue May 22, 2018 at 05:17 PM -0400

import socket
import unittest

from time import sleep
from multiprocessing import Process as Container
from multiprocessing import Event
from multiprocessing import Queue
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


class MockLogger(object):
    def __init__(self, log_queue):
        self.logs = log_queue

    def info(self, msg):
        pass  # We don't need info-level logging

    def error(self, msg):
        self.logs.put(msg)

    def warning(self, msg):
        self.logs.put(msg)


# class TestTransferMsgSmSize(unittest.TestCase):
    # def setUp(self):
        # self.msgs = Queue()

        # port = get_free_tcp_port()
        # size = 3
        # server = ServerAsync("", port, self.msgs, size=size)
        # wait_event = Event()

        # self.container = Container(target=server.run, args=(wait_event,))
        # self.container.start()

        # # Need this to make sure server is properly initialized
        # wait_event.wait()
        # self.client = ClientTester("localhost", port)

    # def test_ascii_text(self):
        # ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        # self.client.send(ascii_text)
        # self.assertEqual(self.msgs.get(), ascii_text)

    # def test_utf8_text(self):
        # utf8_text = "苟利国家生死以"
        # self.client.send(utf8_text)
        # self.assertEqual(self.msgs.get(), utf8_text)

    # def doCleanups(self):
        # self.client.exit()
        # kill(self.container.pid, SIGTERM)


# class TestTransferMsgLgSize(unittest.TestCase):
    # def setUp(self):
        # self.msgs = Queue()

        # port = get_free_tcp_port()
        # size = 81920
        # server = ServerAsync("", port, self.msgs, size=size)
        # wait_event = Event()

        # self.container = Container(target=server.run, args=(wait_event,))
        # self.container.start()

        # wait_event.wait()
        # self.client = ClientTester("localhost", port)

    # def test_ascii_text(self):
        # ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        # self.client.send(ascii_text)
        # self.assertEqual(self.msgs.get(), ascii_text)

    # def test_utf8_text(self):
        # utf8_text = "苟利国家生死以"
        # self.client.send(utf8_text)
        # self.assertEqual(self.msgs.get(), utf8_text)

    # def doCleanups(self):
        # self.client.exit()
        # kill(self.container.pid, SIGTERM)


class TestTransTimeout(unittest.TestCase):
    def setUp(self):
        self.text = "苟利国家生死以"

        self.msgs = Queue()

        # We mock a logger to grab all logs generated in the subprocesses
        self.logs = Queue()
        self.logger = MockLogger(self.logs)

        port = get_free_tcp_port()
        server = ServerAsync("", port, self.msgs, max_retries=2, timeout=0.1)
        server.logger = self.logger
        wait_event = Event()

        self.container = Container(target=server.run, args=(wait_event,))
        self.container.start()

        wait_event.wait()
        self.client = ClientTester("localhost", port)

    def test_timeout_error(self):
        self.client.send(self.text, delay=0.5)
        self.assertEqual(self.msgs.qsize(), 0)
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Failed to receive: 1 time(s).')
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Failed to receive: 2 time(s).')
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Maximum retries exceeded. Transmission failed.')

    def test_timeout_once(self):
        self.client.send(self.text, delay=0.12)
        self.assertEqual(self.msgs.get(), self.text)
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Failed to receive: 1 time(s).')

    def test_msg_corrupted(self):
        self.client.send(self.text, corrupted=True)
        sleep(0.4)
        self.assertEqual(self.msgs.qsize(), 0)
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Failed to receive: 1 time(s).')
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Failed to receive: 2 time(s).')
        self.assertEqual(self.logs.get(),
                         'TimeoutError: Maximum retries exceeded. Transmission failed.')

    def doCleanups(self):
        self.client.exit()
        kill(self.container.pid, SIGTERM)


if __name__ == "__main__":
    unittest.main()
