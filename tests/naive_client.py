#!/usr/bin/env python
#
# Last Change: Sun Oct 29, 2017 at 07:02 PM -0400

import socket
import sys


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


if __name__ == "__main__":
    host, port = "127.0.0.1", 4567
    msg = " ".join(sys.argv[1:])
    client = NaiveTransmissionClient(host, port)
    client.send(msg)
