#!/usr/bin/env python
#
# Last Change: Mon Jul 30, 2018 at 10:24 AM -0400

import sys
sys.path.insert(0, '..')

import pytest

from NeoBurnIn.base import DataStream
from NeoBurnIn.base import DataStats


####################
# For 'DataStream' #
####################

@pytest.fixture
def data_stream():
    return DataStream(max_length=5)


def test_data_stream_basic_append(data_stream):
    data_stream.append('test')
    assert data_stream == ['test']


def test_data_stream_simple_json_str(data_stream):
    data_stream.append('test')
    assert data_stream.json_str == 'test'


def test_data_stream_append_overflow(data_stream):
    # We append 6 times
    for i in range(0, 6):
        data_stream.append(i)
    assert data_stream == [i for i in range(1, 6)]


def test_data_stream_json_str_overflow(data_stream):
    expected_str = ','.join([str(i) for i in range(1, 6)])
    for i in range(0, 6):
        data_stream.append(i)
    assert data_stream.json_str == expected_str


def test_data_stream_return_val_of_append(data_stream):
    for i in range(5):
        assert data_stream.append(i) is False
    for i in range(6, 8):
        assert data_stream.append(i) is True


@pytest.mark.xfail(reason="Not implemented yet.")
def test_data_stream_pass_generator_as_an_argument():
    data_stream = DataStream(range(0, 6), max_length=5)
    assert data_stream == [i for i in range(1, 6)]


###################
# For 'DataStats' #
###################

@pytest.fixture
def data_stats_partial():
    return DataStats(max_length=5, defer_until_full_renewal=False)


def test_data_stats_append_partial_not_full(data_stats_partial):
    for i in range(0, 5):
        assert data_stats_partial.append(i) is False


def test_data_stats_append_partial_not_full_content(data_stats_partial):
    for i in range(0, 5):
        data_stats_partial.append(i) is False
    assert data_stats_partial == [0, 1, 2, 3, 4]
    assert data_stats_partial.json_str == '0,1,2,3,4'
