#!/usr/bin/env python
#
# Last Change: Sun Jul 12, 2020 at 09:36 PM +0800

from argparse import ArgumentParser, Action
from datetime import datetime
from sys import exit
from re import search
from collections import defaultdict as ddict


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

    parser.add_argument('output_dir',
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
    result = ddict(lambda: list([['time', 'value']]))

    with open(log_file) as f:
        pass


if __name__ == '__main__':
    args = parse_input()
