#!/usr/bin/env python
#
# Last Change: Sun Jul 12, 2020 at 10:51 PM +0800

import numpy as np
import matplotlib.pyplot as plt

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

    parser.add_argument('-o', '--output-dir',
                        default=None,
                        help='''
specify the output directory.
    ''')

    return parser.parse_args()


###########
# Helpers #
###########

def plot_time_series(output, time, value, xlabel, ylabel):
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.plot(time, value)
    plt.tight_layout()
    fig.savefig(output)


def read_data(csv_file):
    return np.genfromtxt(
        csv_file, delimiter=',', dtype=None, skip_header=1, unpack=True,
        converters={
            0: lambda x: datetime.strptime(
                x.decode('utf-8'), standard_time_format)
        })


def gen_output_plot_name(csv_file, ext='.png'):
    csv_file = Path(csv_file)
    return csv_file.parent / csv_file.stem+ext


if __name__ == '__main__':
    args = parse_input()

    time, value = read_data(args.csv_file)
    plot_time_series(gen_output_plot_name(args.csv_file), time, value,
                     args.xlabel, args.ylabel)
