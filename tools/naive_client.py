#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 03:47 PM -0500


import socket

import sys
sys.path.insert(0, '..')


class NaiveTransmissionClient():
    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        self.host = host
        self.port = port

        self.EOM = 'EOM'

    def send(self, msg):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.sendall(bytes(msg + self.EOM, 'utf-8'))

        finally:
            self.sock.close()


if __name__ == "__main__":
    client = NaiveTransmissionClient('localhost', 45678)
    client.send(sys.argv[1])
