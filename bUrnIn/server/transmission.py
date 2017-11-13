#!/usr/bin/env python
#
# Last Change: Sun Nov 12, 2017 at 11:02 PM -0500

import socket
import threading
import sys

from sqlite3 import OperationalError

from bUrnIn.server.base import BaseSignalHandler
from bUrnIn.output.sqlite import sql_init


class TransmissionServer(BaseSignalHandler):
    '''
    Multi-threaded TCP server that is blocking.
    This server spawns client sockets in separate threads.
    It also handles SIGINT and SIGTERM so that it will wait for all threads to
    shut down before exit.
    '''
    def __init__(self, host, port,
                 size=4096, max_retries=3, max_connections=5, timeout=5,
                 ping_lifetime=600,
                 db_filename="",
                 log_filename=""):
        # Register handler for SIGINT and SIGTERM
        # so that this server can exit gracefully
        BaseSignalHandler.__init__(self)

        self.host = host
        self.port = port

        self.size = size
        self.max_retries = max_retries
        self.max_connections = max_connections
        self.timeout = timeout

        self.ping_lifetime = ping_lifetime
        self.db_filename = db_filename
        self.log_filename = log_filename

        # Provide a known client dict so that we can monitor when a client goes
        # offline

        # Provide locks for all clientsocket threads
        self.filelock = threading.Lock()
        self.dictlock = threading.Lock()

        # NOTE: our socket is a blocking socket
        #       once we receive a connection, we immediately create a dispatcher
        #       client socket to handle that and back to listening

        # SOCK_STREAM means that this is a TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This allows OS to immediately bind the socket without waiting for
        # the existing socket on the same IP address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        # Initialize sqlite database
        try:
            sql_init(self.db_filename)
        except OperationalError:
            pass  # This is due to table already exists

    def listen(self):
        self.sock.listen(self.max_connections)

        while not self.stop:
            try:
                clientsocket, address = self.sock.accept()
                # Here the clientsocket is a non-blocking one!
                # whereas our seversocket is blocking
                clientsocket.settimeout(self.timeout)

                handler = threading.Thread(target=self.client_handle,
                                           args=(clientsocket, address))
                # We set all clientsocket handler to be daemon threads
                # so that we can wait them to finish before exit the main
                # program
                handler.daemon = True
                handler.start()

            except OSError as err:
                if err.errno is 9:
                    # This is likely due to a SIGINT or SIGTERM signal
                    # and we are trying to shut down the server now
                    pass

                else:
                    # FIXME: need a logger
                    raise(err)

        # Exit gracefully:
        #   Make sure all threads are (properly) closed
        #   However if some threads malfunction, this process will need to be
        #   killed by external commands
        for t in threading.enumerate():
            if t.daemon:
                t.join()

        sys.exit(0)

    def client_handle(self, clientsocket, address):
        retries = 0

        # Here we design a very simple protocol:
        #   Messages can have variable length, but it's end is indicated by a
        #   'EOF' string.
        #   The rationale is that the minimum read size for a socket is,
        #   needless to say, 1. This means that the token should have a length
        #   of 1.
        #   We also require the message be encoded in UTF-8.

        EOM = b'EOF'  # binary representation
        msg = bytearray()
        while True:
            try:
                msg.extend(clientsocket.recv(self.size))

            except socket.timeout:
                # Keep trying until we reach the maximum retries
                print('Timeout')
                retries += 1

                if retries is self.max_retries:
                    self.logger(msg, address, socket.timeout)
                    break

            except socket.error as err:
                self.logger(msg, address, err)
                break

            else:
                # Note that we require the length of the message to be no less
                # than 3.
                if msg[-3:] is EOM:
                    self.dispatcher(bytes(msg).decode("utf-8"), address)
                    # We reached End-Of-Message
                    break

        clientsocket.close()

    def exit(self, signum, frame):
        print("Termination signal received, prepare to exit...")
        BaseSignalHandler.exit(self, signum, frame)
        self.sock.close()

    def logger(self, msg, address, err):
        pass

    def dispatcher(self, msg, address):
        pass
