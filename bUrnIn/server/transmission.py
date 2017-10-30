#!/usr/bin/env python
#
# Last Change: Sun Oct 29, 2017 at 10:20 PM -0400

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
        # This allows OS to immediately reuse the address without waiting for
        # the existing socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(self.max_connections)

        while not self.stop:
            try:
                client, address = self.sock.accept()
                client.settimeout(self.timeout)

                threading.Thread(target=self.client_handle,
                                 args=(client, address)).start()

            except OSError as err:
                if err.errno is 9:
                    # This is likely due to a SIGINT or SIGTERM signal
                    # and we are trying to shut down the server now
                    pass

                else:
                    raise(err)

        # Exit gracefully
        # Make sure all threads are properly closed
        for t in threading.enumerate():
            if t.daemon:
                t.join()

    def client_handle(self, client, address):
        pass

    def exit(self, signum, frame):
        self.stop = True
        self.sock.close()
        print("Termination signal received, prepare to exit...")
