#!/usr/bin/env python3
#
# Last Change: Wed Jun 17, 2020 at 07:07 PM +0800

import logging

from rpi.burnin.FireAlarm import FireAlarm
from rpi.burnin.WaterAlarm import WaterAlarm

from NeoBurnIn.base import BaseDataSource, DataPassthru
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class FireAlarmDataSource(FireAlarm, BaseDataSource):
    def __init__(self, stop_event, queue, *args,
                 displayName='FIRE_ALARM', **kwargs):
        self.queue = queue
        self.displayName = displayName
        super().__init__(stop_event, *args, **kwargs)

    def alarm(self):
        self.queue.put(DataPassthru(time_now_formatted(), self.displayName))

    def get(self):
        pass


class WaterAlarmDataSource(WaterAlarm, BaseDataSource):
    def __init__(self, stop_event, queue, *args,
                 displayName='WATER_ALARM', **kwargs):
        self.queue = queue
        self.displayName = displayName
        super().__init__(stop_event, *args, **kwargs)

    def alarm(self):
        self.queue.put(DataPassthru(time_now_formatted(), self.displayName))

    def get(self):
        pass
