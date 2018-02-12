#!/usr/bin/env python
#
# Last Change: Sun Feb 11, 2018 at 09:50 PM -0500

import logging


def apply_filters(msg, filter_list):
    for filter in filter_list:
        (msg, exit_status) = filter.do(msg)
        if exit_status == FilterExitCode().error:
            break

    return (msg, exit_status)


class FilterExitCode(object):
    def __init__(self):
        self.ok = 0
        self.error = 1
        self.default = self.ok


class Filter(object):
    def __init__(self, logger_name='log'):
        self.logger = logging.getLogger(logger_name)

    def do(self, msg):
        msg_filtered = msg
        return (msg_filtered, FilterExitCode().default)
