#!/usr/bin/env python
#
# Last Change: Thu Jul 26, 2018 at 09:43 AM -0400

import abc

from datetime import datetime
from collections import defaultdict
from statistics import mean, stdev

standard_time_format = "%Y-%m-%d %H:%M:%S.%f"


###########
# Helpers #
###########

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


class ThreadTerminator(object):
    def __init__(self, stop_event, thread_list=[]):
        self.stop_event = stop_event
        self.thread_list = thread_list

    def killall(self):
        self.stop_event.set()
        for th in self.thread_list:
            # Blocking until all slave threads are terminated.
            th.cleanup()


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


####################
# Abstract classes #
####################

class BaseDataSource(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def start(self, interval):
        '''
        Run self.run in a thread.
        '''

    @abc.abstractclassmethod
    def run(self, interval):
        '''
        Continuously providing data at given INTERVAL. Running in the current
        thread.
        '''

    @abc.abstractclassmethod
    def get(self):
        '''
        Return readout data once, if supported.
        '''

    @abc.abstractmethod
    def cleanup(self):
        '''
        Join spawned thread.
        '''


class BaseClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run(self):
        '''
        Start client and send all received msgs from a queue.
        '''

    @abc.abstractmethod
    def cleanup(self):
        '''
        Do cleanups on exit. Typically it is needed to clear the queue.
        '''

    @abc.abstractmethod
    def send(self, msg):
        '''
        Send a single MSG.
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
        Dispatch received, decoded MSG.
        '''

    @abc.abstractmethod
    def loop_getter(self):
        '''
        Return current event loop, if exists.
        '''
