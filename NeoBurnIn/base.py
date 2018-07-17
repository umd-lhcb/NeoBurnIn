#!/usr/bin/env python
#
# Last Change: Tue Jul 17, 2018 at 02:25 PM -0400

import abc

from datetime import datetime
from collections import defaultdict
from statistics import mean, stdev

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


####################
# Helper functions #
####################

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


##########################
# Data structure classes #
##########################

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


################
# Meta classes #
################

class BaseClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def post(self, data):
        '''
        Use HTTP POST method to transfer encoded data.
        '''

    @abc.abstractmethod
    def send(self, msg):
        '''
        Send message to remote host.
        '''

    @abc.abstractmethod
    def loop_getter(self):
        '''
        Return current event loop, if exists.
        '''


class BaseServer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run(self):
        '''
        Start the server.
        '''

    @abc.abstractmethod
    def dispatch(self, msg):
        '''
        Dispatch received, decoded msg.
        '''

    @abc.abstractmethod
    def loop_getter(self):
        '''
        Return current event loop, if exists.
        '''
