#!/usr/bin/env python
#
# Last Change: Thu Jul 05, 2018 at 02:06 PM -0400

from datetime import datetime
from collections import defaultdict
from statistics import mean, stdev

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
    '''
    Computer time difference.
    '''
    return (later_time - previous_time).total_seconds()


class DataStats(list):
    def __init__(self, max_length, renew, *args, **kwargs):
        self.max_length = max_length
        self.renew = renew

        self.reference = None

        super().__init__(*args, **kwargs)

    def append(self, item):
        length = len(self)

        if length == self.max_length:
            if not self.renew:
                self.pop(0)
            else:
                super().clear()
            stats = (mean(self), stdev(self))

        else:
            stats = None

        super().append(item)
        return stats


class DataStream(list):
    '''
    Store received data, up to max_length. Data will be appended to a string on
    append. The string will be used for json output, which will be used for
    visualization.
    '''
    def __init__(self, *args, max_length=5, **kwargs):
        self.max_length = max_length
        self.json_str = ''
        super().__init__(*args, **kwargs)

    def append(self, item):
        # Append unconditionally.
        super().append(item)

        # If the total length is strictly greater than designated upper limit,
        # pop the oldest item.
        if len(self) > self.max_length:
            self.pop(0)

        # This ensures that the datastream length is, maximally, equal to the
        # designated upper limit.
        self.json_str = ','.join(self)
