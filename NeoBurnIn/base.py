#!/usr/bin/env python
#
# Last Change: Fri Jun 29, 2018 at 10:15 PM -0400

from datetime import datetime
from collections import defaultdict

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


def time_now_formatted():
    '''
    Generate standardized time that should be used throughout when storing
    datetime as string.
    '''
    return datetime.now().strftime(standard_time_format)


def nested_dict():
    '''
    Recursive defaultdict that handles variable depth keys.
    '''
    return defaultdict(nested_dict)
