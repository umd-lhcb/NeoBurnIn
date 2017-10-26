#!/usr/bin/env python
#
# Last Change: Wed Oct 18, 2017 at 03:49 PM -0400

import socket
import threading


class ThreadedServer():
    def __init__(self, host, port,
                 max_connection=5, timeout=60, log_dir='/var/log/bUrnIn'):
        self.host = host
        self.port = port
        self.max_connection = max_connection
        self.timeout = timeout

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(self.max_connection)
        while True:
            client, address = self.sock.accept()
            client.settimeout(self.timeout)
            threading.Thread(target=self.listenToClient,
                             args=(client, address)).start()

    def listenToClient(self, client, address):
        pass
