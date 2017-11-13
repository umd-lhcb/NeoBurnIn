#!/usr/bin/env python
#
# Last Change: Tue Oct 31, 2017 at 03:03 AM -0400

from time import sleep
from multiprocessing import Process, Queue
from subprocess import Popen

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
        self.output.put(msg)


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    _, port = tcp.getsockname()
    tcp.close()

    return port


class TestTransferMsgSmSize(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        server_port = get_free_tcp_port()
        size = 3

        self.server_instance = NaiveTransmissionServer("",
                                                       server_port, size=size)
        self.server_instance.output = Queue()

        self.server = Process(target=self.server_instance.listen, args=())
        self.server.start()

        self.client = NaiveTransmissionClient("localhost", server_port)

    def test_ascii_text(self):
        ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        self.client.send(ascii_text)
        self.assertEqual(self.server_instance.output.get(), ascii_text)

    def test_utf8_text(self):
        utf8_text = "苟利国家生死以"
        self.client.send(utf8_text)
        self.assertEqual(self.server_instance.output.get(), utf8_text)

    def doCleanups(self):
        self.client.exit()

        # FIXME: A dirty workaround
        kill = Popen(["kill", "-9", str(self.server.pid)])
        kill.wait()

        self.server_instance.sock.close()


class TestTransferMsgLgSize(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        server_port = get_free_tcp_port()
        size = 4096

        self.server_instance = NaiveTransmissionServer("",
                                                       server_port, size=size)
        self.server_instance.output = Queue()

        self.server = Process(target=self.server_instance.listen, args=())
        self.server.start()

        self.client = NaiveTransmissionClient("localhost", server_port)

    def test_ascii_text(self):
        ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        self.client.send(ascii_text)
        self.assertEqual(self.server_instance.output.get(), ascii_text)

    def test_utf8_text(self):
        utf8_text = "苟利国家生死以"
        self.client.send(utf8_text)
        self.assertEqual(self.server_instance.output.get(), utf8_text)

    def doCleanups(self):
        self.client.exit()

        # FIXME: A dirty workaround
        kill = Popen(["kill", "-9", str(self.server.pid)])
        kill.wait()

        self.server_instance.sock.close()


if __name__ == "__main__":
    unittest.main(failfast=True)
