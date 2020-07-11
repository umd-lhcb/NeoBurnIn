#!/usr/bin/env python
#
# Last Change: Sat Jul 11, 2020 at 11:44 PM +0800

from argparse import ArgumentParser, Action
from datetime import datetime
from sys import exit


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

    parser.add_argument('date_fmt',
                        action=TimeFmtToDatetimeObj,
                        help='''
specify the begin date time when the data will be extracted.
The date format should be of the following format: YYYY-MM-DD:HH.
    ''')

    return parser.parse_args()


###########
# Helpers #
###########


if __name__ == '__main__':
    args = parse_input()
