#!/usr/bin/env python3
#
# Last Change: Mon Jul 20, 2020 at 02:59 AM +0800

import abc
import sys
import yaml
import janus
import importlib

from datetime import datetime
from collections import defaultdict, namedtuple
from statistics import mean, stdev
from pathlib import Path
from threading import Event

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


def parse_config(config_file):
    '''
    Parse configuration file used for all clients/servers.
    '''
    if Path(config_file).exists():
        with open(config_file) as cfg:
            parsed = yaml.safe_load(cfg)
        return parsed

    else:
        print('{}: configuration file does not exist.'.format(config_file))
        sys.exit(1)


def parse_time_limit(time):
    '''
    Convert the string-based time, such as '1 HRS', to seconds.
    '''
    time_dict = {'SEC': 1, 'MIN': 60*1, 'HRS': 60*60}
    time_parsed = time.split(' ')
    return int(time_parsed[0]) * time_dict[time_parsed[1]]


class ThreadTerminator(object):
    '''
    Terminate all listed threads gracefully when this thread is shutdown.
    '''
    def __init__(self, stop_event, thread_list):
        self.stop_event = stop_event
        self.thread_list = thread_list

    def killall(self):
        self.stop_event.set()
        for th in self.thread_list:
            # Blocking until all slave threads are terminated.
            th.cleanup()


class SensorEmitter(object):
    '''
    Import and configure sensors.
    '''
    def __init__(self, sensors_list):
        self.stop_event = Event()
        self.queue = janus.Queue()
        self.emitted_sensors = []

        self.sensors_list = sensors_list

    def init_sensors(self):
        gpio_is_inited = False

        for sensor_spec in self.sensors_list:
            for name, spec in sensor_spec.items():
                mod, cls = name.rsplit('.')
                sensor = getattr(importlib.import_module(
                    'NeoBurnIn.DataSource.' + mod), cls)
                if 'WaterAlarm' in cls or 'FireAlarm' in cls:
                    if gpio_is_inited:
                        self.emitted_sensors.append(sensor(
                            self.stop_event, self.queue.sync_q,
                            gpio_init_cleanup=False, **spec))
                    else:
                        gpio_is_inited = True
                        self.emitted_sensors.append(sensor(
                            self.stop_event, self.queue.sync_q, **spec))

                else:
                    self.emitted_sensors.append(sensor(
                        self.stop_event, self.queue.sync_q, **spec))

    def start(self):
        for sensor in self.emitted_sensors:
            sensor.start()

    def join(self):
        for sensor in self.emitted_sensors:
            sensor.join()


##########################
# Data structure classes #
##########################

class DataStream(list):
    '''
    Store received data, up to 'max_length'. Data will be appended to a string
    on append. The string will be used for JSON output, which will be used for
    visualization.
    '''
    def __init__(self, iterable=None, max_length=5, update_json=True):
        self.max_length = max_length
        self.update_json = update_json

        self.json_str = ''
        self.list_is_full = False

        if iterable and len(iterable) > max_length:
            # Make sure the length of the list is correct
            iterable = iterable[len(iterable)-max_length:]

        if iterable:
            super().__init__(iterable)
        else:
            super().__init__()

    def append(self, item):
        # Append unconditionally.
        super().append(item)

        # If the total length is strictly greater than designated upper limit,
        # pop the oldest item.
        if self.list_is_full:  # NOTE this makes 'append' operation faster.
            self.pop(0)

        elif len(self) == self.max_length:
            self.list_is_full = True

        # Update the JSON string representation at append-time.
        if self.update_json:
            self.json_str = ','.join(str(x) for x in self)

        return self.list_is_full


class DataStats(DataStream):
    '''
    Store data, up to 'max_length', and generate mean and std with elements in
    the list when the list is full.

    If 'learn_once' is set to True, the mean and std computed when the list is
    full for the first time will be used as references throughout this object's
    life cycle.

    Otherwise the references mean and std will be updated with new data point
    continuously after the list is full.
    '''
    def __init__(self, *args, learn_once=False, **kwargs):
        if learn_once:  # NOTE: 'learn_once' is set on initialization once and only once.
            self.post_append = self.post_append_learn_once
        else:
            self.post_append = self.post_append_learn_continuously

        self.reference_exists = False
        self.reference_mean = None
        self.reference_stdev = None

        super().__init__(*args, **kwargs)

    def append(self, item):
        if super().append(item):  # Compute statistics only if the list is full.
            return self.post_append()
        else:
            return False

    def post_append_learn_once(self):
        if not self.reference_exists:  # If we've never updated the learning result, do it.
            return self.post_append_learn_continuously()
        else:
            return (self.reference_mean, self.reference_stdev)

    def post_append_learn_continuously(self):
        self.reference_mean, self.reference_stdev = mean(self), stdev(self)
        self.reference_exists = True
        return self.reference_mean, self.reference_stdev


DataPassthru = namedtuple('DataPassthru', ('date name value'),
                          defaults=(None,)*3)


####################
# Abstract classes #
####################

class BaseDataSource(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def run(self):
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


class BaseDataSink(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def on(self, ch):
        '''
        Set ch to on.
        '''

    @abc.abstractclassmethod
    def off(self, ch):
        '''
        Set ch to off.
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
