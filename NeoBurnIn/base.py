#!/usr/bin/env python
#
# Last Change: Wed Jul 04, 2018 at 03:30 PM -0400

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


def time_delta_in_seconds(later_time, previous_time):
    return (later_time - previous_time).total_seconds()
