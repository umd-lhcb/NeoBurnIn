#!/usr/bin/env python
#
# Last Change: Sun Feb 11, 2018 at 11:30 PM -0500
# 'qc' stands for 'Quality Assurance'. These filters test if a given data is
# valid and within expectation.

from datetime import datetime

from bUrnIn.framework.base import standard_time_format
from bUrnIn.filters.base import Filter
from bUrnIn.filters.base import FilterExitCode


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
