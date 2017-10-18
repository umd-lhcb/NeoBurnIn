#!/usr/bin/env python
#
# Last Change: Wed Oct 18, 2017 at 10:36 AM -0400

import socket


class Client():
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
