#!/usr/bin/env python
#
# Last Change: Thu Jul 05, 2018 at 02:28 PM -0400

import sys
sys.path.insert(0, '..')

import pytest

from NeoBurnIn.base import DataStream


####################
# For 'DataStream' #
####################

@pytest.fixture
def data_stream():
    return DataStream(max_length=5)


def test_basic_append(data_stream):
    data_stream.append('test')
    assert data_stream == ['test']


def test_simple_json_str(data_stream):
    data_stream.append('test')
    assert data_stream.json_str == 'test'


def test_append_overflow(data_stream):
    # We append 6 times
    for i in range(0, 6):
        data_stream.append(str(i))
    assert data_stream == [str(i) for i in range(1, 6)]


def test_json_str_overflow(data_stream):
    expected_str = ','.join([str(i) for i in range(1, 6)])
    for i in range(0, 6):
        data_stream.append(str(i))
    assert data_stream.json_str == expected_str


@pytest.mark.xfail(reason="Not implemented yet.")
def test_pass_generator_as_an_argument():
    data_stream = DataStream(range(0, 6), max_length=5)
    assert data_stream == [i for i in range(1, 6)]
