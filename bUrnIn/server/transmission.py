#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 01:41 PM -0500

import socket
import sys

from multiprocessing import Process as Container
from multiprocessing import Queue
from sqlite3 import OperationalError
from datetime import datetime

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
                 db_filename="", log_filename=""):
        # Register handler for SIGINT and SIGTERM so that this server can exit
        # gracefully
        BaseSignalHandler.__init__(self)

        self.host = host
        self.port = port

        self.size = size
        self.max_retries = max_retries
        self.max_connections = max_connections
        self.timeout = timeout

        self.db_filename = db_filename
        self.log_filename = log_filename

        # Define a time stamp format
        self.time_format = '%Y-%m-%d %H:%M:%S:%f'

        # NOTE: our socket is a blocking socket
        #       once we receive a connection, we immediately create a dispatcher
        #       client socket to handle that and back to listening
        #       I also decide to use multiprocessing library, where the 'join'
        #       of spawned subprocesses is automatic.

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

        # Initialize two queues to store both messages and errors
        self.msgs = Queue()
        self.errs = Queue()

    def listen(self):
        self.sock.listen(self.max_connections)

        while not self.stop:
            try:
                client, _ = self.sock.accept()
                # Here the client is a non-blocking socket; whereas our server
                # socket is blocking
                client.settimeout(self.timeout)

                client_handler = Container(target=self.client_handle,
                                           args=(client, self.msgs, self.errs))
                client_handler.start()

            except OSError as err:
                if err.errno is 9:
                    # This is likely due to a SIGINT or SIGTERM signal and we
                    # are trying to shut down the server now
                    pass

                else:
                    self.errs.put((err, self.time_stamp(),
                                   "Some error occurred."))

        # Exit gracefully: All non-daemonic subprocesses will automatically be
        # joined
        sys.exit(0)

    def client_handle(self, client, msgs, errs):
        retries = 0

        # Here we design a very simple protocol:
        #   Messages can have variable length, but it's end is indicated by a
        #   'EOM' byte array.
        #   The rationale is that the minimum read size for a socket is,
        #   needless to say, 1. This means that the token should have a length
        #   of 1.
        #   We also require the message be encoded in UTF-8.

        EOM = bytearray(b'EOM')  # binary representation
        msg = bytearray()

        while True:
            try:
                msg.extend(client.recv(self.size))

            except socket.timeout:
                # Keep trying until we reach the maximum retries
                retries += 1
                # Also, clear the full buffer and start from scratch
                msg.clear()

                if retries is self.max_retries:
                    errs.put((socket.timeout, self.time_stamp(), msgs))
                    break

            except socket.error as err:
                errs.put((err, self.time_stamp(), msg))
                break

            else:
                # Note that we require the length of the message to be no less
                # than 3.
                if msg[-3:] is EOM:
                    msgs.put(bytes(msg).decode("utf-8"))
                    # We reached End-Of-Message
                    break

        client.close()

    def exit(self, signum, frame):
        print("Termination signal received, prepare to exit...")
        BaseSignalHandler.exit(self, signum, frame)
        self.sock.close()

    def time_stamp(self):
        return datetime.now().strftime(self.time_format)

    # These methods should be implemented by the real server
    def logger(self, data, errs):
        pass

    def dispatcher(self, data, msgs, errs):
        pass
