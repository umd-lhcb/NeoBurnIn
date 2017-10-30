#!/usr/bin/env python
#
# Last Change: Mon Oct 30, 2017 at 12:15 AM -0400

from time import sleep

import sys
sys.path.insert(0, '..')

from bUrnIn.server.transmission import TransmissionServer


class NaiveTransmissionServer(TransmissionServer):
    def dispatcher(self, msg, address):
        print(msg)
        sleep(1)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 4567

    server = NaiveTransmissionServer(HOST, PORT)
    server.listen()
