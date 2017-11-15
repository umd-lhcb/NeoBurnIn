#!/usr/bin/env python
#
# Last Change: Mon Nov 13, 2017 at 09:07 PM -0500

from datetime import datetime

standard_time_format = "%Y-%m-%d %H:%M:%S:%f"


def time_stamp(time_format):
    return datetime.now().strftime(time_format)
