#!/usr/bin/env python
#
# Last Change: Thu Aug 16, 2018 at 01:39 AM -0400

import logging

from pathlib import Path

from NeoBurnIn.base import BaseDataSource
from NeoBurnIn.base import time_now_formatted
from submodules.RPiBurnIn.therm.ThermSensor import ThermSensor

logger = logging.getLogger(__name__)


class ThermDataSource(ThermSensor, BaseDataSource):
    def __init__(self, queue, *args, sensorPath=None, **kwargs):
        self.queue = queue

        super().__init__(*args, sensor=Path(sensorPath), **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            therm = self.get()
            logger.debug(therm)
            self.queue.put(therm)

    def get(self):
        therm = str(super().get())
        return time_now_formatted() + self.separator + \
            self.display_name + self.separator + \
            therm + self.line_end
