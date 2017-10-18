#!/usr/bin/env python
#
# Last Change: Wed Oct 18, 2017 at 12:41 PM -0400

import sys
sys.path.insert(0, '..')

from bUrnIn.client import Client

if __name__ == "__main__":
    host, port = "LinSun", 4567
    msg = " ".join(sys.argv[1:])
    client = Client(host, port)
    client.send(msg)
