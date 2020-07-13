#!/usr/bin/env python
#
# Last Change: Sun Jul 12, 2020 at 11:45 PM +0800

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import standard_time_format


###################
# Parse arguments #
###################

def parse_input():
    parser = ArgumentParser(description='A time series plotter.')

    parser.add_argument('csv_file',
                        help='''
specify the path to burn-in log file.
    ''')

    parser.add_argument('-x', '--xlabel',
                        default='Time',
                        help='''
specify x label.
    ''')

    parser.add_argument('-y', '--ylabel',
                        default='Temperature [C]',
                        help='''
specify y label.
    ''')

    parser.add_argument('-a', '--aspect',
                        type=float,
                        default=0.02,
                        help='''
specify aspect ratio.
    ''')

    parser.add_argument('-o', '--output-dir',
                        default=None,
                        help='''
specify the output directory.
    ''')

    return parser.parse_args()


###########
# Helpers #
###########

def plot_time_series(output, time, value, xlabel, ylabel, aspect):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.set_aspect(aspect)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Tune the datatime axis
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d H%H'))

    ax.plot(time, value)

    fig.savefig(output, dpi=300, transparent=False, bbox_inches='tight')


# NOTE: This works for 2D CSV files only.
def read_data(csv_file):
    raw_time, raw_value = np.genfromtxt(
        csv_file, delimiter=',', dtype=str, skip_header=1, unpack=True,
        encoding='utf-8')

    time = np.array([datetime.strptime(i, standard_time_format)
                     for i in raw_time])
    value = raw_value.astype(np.float)

    return time, value


def gen_output_plot_name(csv_file, ext='.png'):
    csv_file = Path(csv_file)
    return csv_file.parent / (str(csv_file.stem)+ext)


if __name__ == '__main__':
    args = parse_input()

    time, value = read_data(args.csv_file)
    plot_time_series(gen_output_plot_name(args.csv_file), time, value,
                     args.xlabel, args.ylabel, args.aspect)
