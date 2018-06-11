#!/usr/bin/env python
#
# Last Change: Mon Jun 11, 2018 at 04:07 AM -0400
# 'qa' stands for 'Quality Assurance'. These filters test if a given data is
# valid and within expectation.

import logging

from datetime import datetime

from bUrnIn.framework.base import standard_time_format
from bUrnIn.filters.base import Filter
from bUrnIn.filters.base import FilterExitCode


def parse_time_limit(time):
    time_dict = {'SEC': 1, 'MIN': 60*1, 'HRS': 60*60}
    time_parsed = time.split(' ')
    return int(time_parsed[0] * time_dict[time_parsed[1]])


def time_delta(later_time, previous_time):
    return (later_time - previous_time).total_seconds()


class FilterDataSplit(Filter):
    def do(self, data):
        try:
            date, ch_name, value = data.split("|")
        except Exception:
            self.logger.error("%s: Data entry not correctly delimited" % data)
            return (data, FilterExitCode().error)

        try:
            datetime.strptime(date, standard_time_format)
        except Exception:
            self.logger.error("%s: Date is not in the correct format" % date)
            return (data, FilterExitCode().error)

        try:
            value = float(value)
        except Exception:
            self.logger.error("%s: Value is not in the correct format" % value)
            return (data, FilterExitCode().error)

        return ((date, ch_name, value), FilterExitCode().ok)


class FilterDataLearn(Filter):
    def __init__(self):
        pass


class FilterDataMonitor(Filter):
    def __init__(self,
                 std_limit=4,
                 temp_limit=60,
                 learn_duration='10 MIN', check_duration='4 HRS',
                 log_email_interval='1 HRS',
                 temp_ch_names=list(),
                 stats_logger_name='stats'):
        self.std_limit = std_limit
        self.temp_limit = temp_limit
        self.learn_duration = parse_time_limit(learn_duration)
        self.check_duration = parse_time_limit(check_duration)
        self.log_email_interval = parse_time_limit(log_email_interval)

        self.temp_ch_list = temp_ch_names.split(',')
        self.statslogger = logging.getLogger(stats_logger_name)

        self.email_last_sent_timestamp = None
        self.first_received = None
        self.last_received = None
        self.learn_dict = dict()
        self.check_dict = dict()

        super().__init__()

    def do(self, data):
        timestamp = datetime.now()
        if self.first_received is None:
            self.first_received = timestamp
        if self.last_received is None:
            self.last_received = timestamp

        data_status = self.data_check(data, timestamp)
        self.data_learn(data, timestamp, data_status)

        self.last_received = timestamp

        return (data, data_status)

    def data_check(self, data, timestamp):
        date, ch_name, value = data
        if time_delta(timestamp, self.first_received) <= self.learn_duration:
            return FilterExitCode().ok

        elif ch_name in self.temp_ch_list and value >= self.temp_limit:
            error_msg = ''
            self.log_email(error_msg)
            return FilterExitCode().error

        elif abs(self.learn_dict[ch_name]['mean'] - value) >= \
                self.learn_dict[ch_name]['std'] * self.std_limit:
            error_msg = ''
            self.log_email(error_msg)
            return FilterExitCode().error

        else:
            return FilterExitCode.ok

    def data_learn(self, data, timestamp, data_status):
        date, ch_name, value = data
        pass

    def log_email(self, msg):
        if self.email_last_sent_timestamp is None:
            # We never sent any email before
            self.logger.critical(msg)
            self.email_last_sent_timestamp = datetime.now()

        else:
            # If we have sent emails recently, don't send any email again
            # This is to prevent email flooding
            delta_t = time_delta(datetime.now(), self.email_last_sent_timestamp)

            if delta_t >= self.log_email_interval:
                self.logger.critical(msg)
                # Update the timestamp, only if we sent a new email.
                self.email_last_sent_timestamp = datetime.now()
            else:
                self.logger.warning(msg)
