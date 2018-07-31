#!/usr/bin/env python
#
# Last Change: Tue Jul 31, 2018 at 09:54 AM -0400

import logging

import sys
sys.path.insert(0, '..')

from NeoBurnIn.io.server import DataServer
from NeoBurnIn.io.logging import log_handler_colored_console


####################
# Configure logger #
####################

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler_colored_console(level=logging.INFO))


if __name__ == "__main__":
    server = DataServer(host='0.0.0.0')
    server.run()
