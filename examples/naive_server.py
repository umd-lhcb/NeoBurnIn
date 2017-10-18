#!/usr/bin/env python
#
# Last Change: Wed Oct 18, 2017 at 10:54 AM -0400

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
                    raise ValueError('Client disconnected')

            except client.close():
                return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 4567

    server = ThreadedServer(HOST, PORT)
    server.listen()
