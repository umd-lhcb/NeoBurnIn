#!/usr/bin/env python
#
# Last Change: Wed Jun 27, 2018 at 02:11 PM -0400

from socket import gethostbyaddr, gethostname


def get_hostname():
    return gethostbyaddr(gethostname())[0]
