#!/usr/bin/env python
#
# Last Change: Sun Jul 12, 2020 at 10:05 PM +0800

from argparse import ArgumentParser, Action
from datetime import datetime
from sys import exit
from re import search
from collections import defaultdict as ddict
from os import makedirs
from pathlib import Path
from csv import writer

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import standard_time_format


###################
# Parse arguments #
###################

TIME_FMT = '%Y-%m-%d:%H'


class TimeFmtToDatetimeObj(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        try:
            setattr(namespace, self.dest, datetime.strptime(value, TIME_FMT))
        except ValueError:
            print('Invalid date time string: {}.'.format(value))
            exit(1)


def parse_input():
    parser = ArgumentParser(description='A burn-in log parser.')

    parser.add_argument('log_file',
                        help='''
specify the path to burn-in log file.
    ''')

    parser.add_argument('-o', '--output-dir',
                        default='.',
                        help='''
specify the output directory.
    ''')

    parser.add_argument('-b', '--begin',
                        action=TimeFmtToDatetimeObj,
                        required=True,
                        help='''
specify the begin date time when the data will be extracted.
The date format should be of the following format: YYYY-MM-DD:HH.
    ''')

    parser.add_argument('-e', '--end',
                        action=TimeFmtToDatetimeObj,
                        required=True,
                        help='''
specify the end date time when the data will be extracted.
The date format should be of the following format: YYYY-MM-DD:HH.
    ''')

    return parser.parse_args()


###########
# Helpers #
###########


def extract_data(log_file, begin, end):
    data = ddict(lambda: list([['time', 'value']]))

    with open(log_file) as f:
        for l in f:
            match = search(r'Received: (.*)$', l)
            if match:
                time, name, value = match.group(1).split('|')

                time_obj = datetime.strptime(time, standard_time_format)

                if begin <= time_obj <= end:
                    data[name].append([time, float(value)])

    return data


def write_data(output_dir, data, begin, end):
    output_dir = Path(output_dir) / Path('{}_{}'.format(
        begin.strftime(TIME_FMT), end.strftime(TIME_FMT)
    ))
    makedirs(output_dir, exist_ok=True)

    for filename, value in data.items():
        with open(output_dir / Path(filename+'.csv'), 'w') as f:
            data_writer = writer(f)
            data_writer.writerows(value)


if __name__ == '__main__':
    args = parse_input()

    data = extract_data(args.log_file, args.begin, args.end)
    write_data(args.output_dir, data, args.begin, args.end)
