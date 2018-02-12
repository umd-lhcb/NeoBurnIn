#!/usr/bin/env python
#
# Last Change: Sun Feb 11, 2018 at 10:54 PM -0500
# 'qc' stands for 'Quality Assurance'. These filters test if a given data is
# valid and within expectation.

from bUrnIn.filters.base import Filter
from bUrnIn.filters.base import FilterExitCode


class FilterDataSplit(Filter):
    def do(self, msg):
        return msg.split(",")
