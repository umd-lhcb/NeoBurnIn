#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 01:43 PM -0500

from time import sleep
from subprocess import Popen

import socket
import unittest

import sys
sys.path.insert(0, '..')

from bUrnIn.server.transmission import TransmissionServer


class TransmissionClientTester():
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


class TransmissionServerTester(TransmissionServer):
    def dispatcher(self, data, msgs, errs):
        print("something's here...")
        data = data[:-3]  # Remove the 'EOM' character
        msgs.put(data)


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))  # Get any available port

    _, port = tcp.getsockname()
    tcp.close()

    return port


class TestTransferMsgSmSize(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        server_port = get_free_tcp_port()
        size = 3

        self.server = TransmissionServerTester("", server_port, size=size)
        self.server.listen()

        self.client = TransmissionClientTester("localhost", server_port)

    def test_ascii_text(self):
        ascii_text = "Gou Li Guo Jia Sheng Si Yi"
        self.client.send(ascii_text)
        self.assertEqual(self.server.msgs.get(), ascii_text)

    def test_utf8_text(self):
        utf8_text = "苟利国家生死以"
        self.client.send(utf8_text)
        self.assertEqual(self.server.msgs.get(), utf8_text)

    def doCleanups(self):
        self.client.exit()

        # # FIXME: A dirty workaround
        # kill = Popen(["kill", "-9", str(self.server.pid)])
        # kill.wait()

        self.server.exit()


if __name__ == "__main__":
    unittest.main(failfast=True)
