#!/usr/bin/env python
#
# Last Change: Sun Oct 29, 2017 at 08:59 PM -0400

from time import sleep
from datetime import datetime

import sys
sys.path.insert(0, '..')

from bUrnIn.server.base import BaseSignalHandler

time_fmt = "%Y-%m-%d %H:%M:%S"

class NaiveSignalHandler(BaseSignalHandler):
    def start(self):
        while not self.stop:
            current_time = datetime.now().strftime(time_fmt)
            print("I am still alive at: {}".format(current_time))
            sleep(2)

        # Kill itself gracefully
        print("Termination signal received, exit gracefully...")


if __name__ == "__main__":
    handler = NaiveSignalHandler()
    handler.start()
