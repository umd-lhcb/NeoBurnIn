#!/usr/bin/env python
#
# Last Change: Mon Jun 11, 2018 at 04:08 AM -0400

import logging


def apply_filters(data, filter_list):
    for filter in filter_list:
        (data, exit_status) = filter.do(data)
        if exit_status != FilterExitCode().ok:
            break

    return (data, exit_status)


class FilterExitCode(object):
    def __init__(self):
        self.ok = 0
        self.error = 1
        self.premature = 2
        self.default = self.ok


class Filter(object):
    def __init__(self, logger_name='log'):
        self.logger = logging.getLogger(logger_name)

    def do(self, data):
        data_filtered = data
        return (data_filtered, FilterExitCode().default)
