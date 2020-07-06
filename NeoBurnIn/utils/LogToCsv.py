#!/usr/bin/env python3
#
# Last Change: Tue Aug 21, 2018 at 12:03 PM -0400

from pathlib import Path
from argparse import ArgumentParser
from collections import defaultdict


def log_to_list(log_filename, **kwargs):
    log_file = Path(log_filename).expanduser()  # so that '~' is expanded
    data_list = []

    with log_file.open() as f:
        for line in f:
            keep_line = test_keep_line(line, **kwargs)
            if keep_line is not None:
                data_list.append(keep_line)

    return data_list


def list_to_dict(data_list):
    data_dict = defaultdict(list)

    for entry in data_list:
        date, channel, value = entry.strip('\n').split('|')
        data_dict[channel].append((date, value))

    return data_dict


def test_keep_line(line, testers=[]):
    for t in testers:
        line = t(line)
        if line is None:
            break

    return line


###########
# Testers #
###########

def test_log_level(levels=['INFO']):
    def tester(line):
        return_val = None
        for l in levels:
            if l in line:
                return_val = line
                break
        return return_val

    return tester


def test_if_contain_data(signature='Received: '):
    def tester(line):
        line_splitted = line.split(signature)
        try:
            return line_splitted[1]
        except IndexError:
            return None

    return tester


##############
# CSV output #
##############

def dict_to_csv_files(output_dirname, data_dict):
    dir = Path(output_dirname).expanduser()

    for channel in data_dict.keys():
        file = dir / (channel+'.csv')
        filecontent = list_to_csv(['Time', channel], data_dict[channel])
        file.write_text(filecontent)


def list_to_csv(header, body):
    content = ','.join(header) + '\n'
    for line in body:
        content += ','.join(line) + '\n'
    return content


################################
# Parser for interactive usage #
################################

def parse_input():
    parser = ArgumentParser(
        description='Simple Python script to extract data from server log to csv.'
    )

    parser.add_argument(
        '-i', '--input',
        help='''
        specify input log file.
        ''',
        required=True,
    )

    parser.add_argument(
        '-o', '--output',
        help='''
        specify output csv file.
        ''',
        required=True,
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_input()

    testers = [test_log_level(), test_if_contain_data()]
    data = list_to_dict(log_to_list(args.input, testers=testers))
    dict_to_csv_files(args.output, data)
