#!/usr/bin/env python
#
# Last Change: Sun Oct 29, 2017 at 09:16 PM -0400

from time import sleep

import sys
sys.path.insert(0, '..')

from bUrnIn.server.transmission import TransmissionServer


class NaiveTransmissionServer(TransmissionServer):
    def client_handle(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    print(data)
                    sleep(5)
                else:
                    print('Client disconnected.')
                    raise ValueError('Client disconnected.')

            except ValueError:
                client.close()
                return False


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 4567

    server = NaiveTransmissionServer(HOST, PORT)
    server.listen()
