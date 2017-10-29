#!/usr/bin/env python
#
# Last Change: Sun Oct 29, 2017 at 06:53 PM -0400

import socket
import threading

from bUrnIn.server.base import BaseSignalHandler


class TransmissionServer(BaseSignalHandler):
    def __init__(self, host, port,
                 max_connections=10, timeout=5,
                 db_filename="",
                 log_filename=""):
        self.signal_handle()

        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.timeout = timeout
        self.db_filename = db_filename
        self.log_filename = log_filename

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(self.max_connections)

        while not self.stop:
            client, address = self.sock.accept()
            client.settimeout(self.timeout)

            threading.Thread(target=self.client_handle,
                             args=(client, address)).start()

            # Exit gracefully
            for t in threading.enumerate():
                if t.daemon:
                    t.join()

    def client_handle(self, client, address):
        pass
