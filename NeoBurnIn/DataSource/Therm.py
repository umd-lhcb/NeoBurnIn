#!/usr/bin/env python3
#
# Last Change: Mon Jul 20, 2020 at 03:04 AM +0800

import logging

from pathlib import Path
from statistics import mean
from rpi.burnin.ThermSensor import ThermSensor

from NeoBurnIn.base import BaseDataSource, DataPassthru
from NeoBurnIn.base import time_now_formatted
from NeoBurnIn.base import DataStream

logger = logging.getLogger(__name__)


class ThermDataSource(ThermSensor, BaseDataSource):
    def __init__(self, stop_event, queue, *args, sensorPath=list(), **kwargs):
        sensor = [Path(p) for p in sensorPath]
        super().__init__(stop_event, queue, *args, sensor=sensor, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            therm = self.get()
            logger.debug('{} readout: {}'.format(self.displayName, therm))
            msg = DataPassthru(time_now_formatted(), self.displayName, therm)
            self.queue.put(msg)


class ThermDataFancySource(ThermDataSource):
    def __init__(self, *args,
                 numOfRecentDP=8, numOfInitOutlier=2, rejectThresh=8, **kwargs):
        self.numOfRecentDP = numOfRecentDP
        self.numOfInitOutlier = numOfInitOutlier
        self.rejectThresh = rejectThresh

        super().__init__(*args, **kwargs)

    def initial_sampling(self):
        raw_samples = [super().get(True) for i in
                       range(self.numOfRecentDP+self.numOfInitOutlier)]

        sample_mean = mean(raw_samples)
        distance_to_mean = [abs(i - sample_mean) for i in raw_samples]
        sorted_distance_idx = self.sorted_idx(distance_to_mean)

        # Remove the 2 data points that are furthest away from mean
        outlier_idx = sorted_distance_idx[-2:]
        self.sample = DataStream(
            [i for i in raw_samples if i not in outlier_idx],
            max_length=self.numOfRecentDP, update_json=False)
        logger.info('{} acquired {} initial good data points: {}'.format(
            self.displayName, self.numOfRecentDP, self.sample
        ))

    def run(self):
        self.initial_sampling()

        while not self.stop_event.wait(self.interval):
            therm = self.get()
            logger.debug('{} readout: {}'.format(self.displayName, therm))

            recent_mean = mean(self.sample)
            if abs(therm - recent_mean) > self.rejectThresh:
                logger.debug('{} readout {} rejected, with recent mean {}'.format(
                    self.displayName, therm, recent_mean
                ))
            else:
                self.sample.append(therm)
                msg = DataPassthru(
                    time_now_formatted(), self.displayName, therm)
                self.queue.put(msg)

    @staticmethod
    def sorted_idx(l):
        return [i[0] for i in sorted(enumerate(l), key=lambda x:x[1])]
