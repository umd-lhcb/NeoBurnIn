#!/usr/bin/env python
#
# Last Change: Mon Oct 30, 2017 at 01:56 PM -0400

from time import sleep
import socket

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
        print(msg)
        sleep(1)


if __name__ == "__main__":
    host, port = "0.0.0.0", 4567
    size = 20

    server = NaiveTransmissionServer(host, port, size=1)
    server.listen()
