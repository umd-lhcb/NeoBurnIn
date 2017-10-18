#!/usr/bin/env python
#
# Last Change: Wed Oct 18, 2017 at 11:14 AM -0400

import sys
sys.path.insert(0, '..')

from bUrnIn.server import ThreadedServer


class NaiveThreadedServer(ThreadedServer):
    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    print(data)
                else:
                    print('Client disconnected.')
                    raise ValueError('Client disconnected.')

            except ValueError:
                client.close()
                return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 4567

    server = NaiveThreadedServer(HOST, PORT)
    server.listen()
