#!/usr/bin/env python
#
# Last Change: Mon Jan 20, 2020 at 04:50 AM -0500

import logging

from pathlib import Path
from rpi.burnin.ThermSensor import ThermSensor

from NeoBurnIn.base import BaseDataSource, DataPassthru
from NeoBurnIn.base import time_now_formatted

logger = logging.getLogger(__name__)


class ThermDataSource(ThermSensor, BaseDataSource):
    def __init__(self, stop_event, queue, *args, sensorPath=None, **kwargs):
        super().__init__(stop_event, queue, *args,
                         sensor=Path(sensorPath), **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            therm = self.get()
            logger.debug(therm)
            if therm is not None:
                self.queue.put(therm)

    def get(self):
        therm = super().get()
        return DataPassthru(time_now_formatted(), self.displayName, therm)
