#!/usr/bin/env python3
#
# Last Change: Mon Jul 20, 2020 at 12:46 AM +0800

import pytest
import statistics

import sys
sys.path.insert(0, '..')

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
    for i in range(4):
        assert data_stream.append(i) is False
    for i in range(5, 8):
        assert data_stream.append(i) is True


def test_data_stream_pass_generator_as_an_argument():
    data_stream = DataStream(range(0, 6), max_length=5)
    assert data_stream == [i for i in range(1, 6)]


###############################
# For 'DataStats', learn once #
###############################

@pytest.fixture
def data_stats_once():
    return DataStats(max_length=5, learn_once=True)


def test_data_stats_once_append_not_full(data_stats_once):
    for i in range(0, 4):
        assert data_stats_once.append(i) is False


def test_data_stats_once_append_not_full_content(data_stats_once):
    for i in range(0, 4):
        data_stats_once.append(i) is False
    data_stats_once.append(4)
    assert data_stats_once == [0, 1, 2, 3, 4]
    assert data_stats_once.json_str == '0,1,2,3,4'


def test_data_stats_once_learn_first(data_stats_once):
    for i in range(0, 5):
        data_stats_once.append(i)
    assert data_stats_once.list_is_full is True
    assert data_stats_once.append(5) == (
        statistics.mean(range(5)), statistics.stdev(range(5)))


def test_data_stats_once_store_learning_stats(data_stats_once):
    for i in range(0, 6):
        data_stats_once.append(i)
    assert data_stats_once.reference_mean == statistics.mean(range(5))
    assert data_stats_once.reference_stdev == statistics.stdev(range(5))


def test_data_stats_once_never_recompute(data_stats_once):
    for i in range(0, 6):
        data_stats_once.append(i)
    assert data_stats_once.append(6) == (
        statistics.mean(range(5)), statistics.stdev(range(5)))


def test_data_stats_once_preserve_learning_stats(data_stats_once):
    for i in range(0, 14):
        data_stats_once.append(i)
    assert data_stats_once.reference_mean == statistics.mean(range(5))
    assert data_stats_once.reference_stdev == statistics.stdev(range(5))


def test_data_stats_once_never_recompute_ever(data_stats_once):
    for i in range(0, 7):
        data_stats_once.append(i)
    assert data_stats_once.append(7) == (
        statistics.mean(range(5)), statistics.stdev(range(5)))


#######################################
# For 'DataStats', learn continuously #
#######################################

@pytest.fixture
def data_stats_continuous():
    return DataStats(max_length=5, learn_once=False)


def test_data_stats_continuous_append_not_full(data_stats_continuous):
    for i in range(0, 4):
        assert data_stats_continuous.append(i) is False
    assert data_stats_continuous == [0, 1, 2, 3]
    assert data_stats_continuous.json_str == '0,1,2,3'


def test_data_stats_continuous_compute_first_stats(data_stats_continuous):
    for i in range(0, 5):
        data_stats_continuous.append(i)
    assert data_stats_continuous.append(5) == (
        statistics.mean(range(1, 6)), statistics.stdev(range(1, 6)))


def test_data_stats_continuous_store_learning_stats(data_stats_continuous):
    for i in range(0, 6):
        data_stats_continuous.append(i)
    assert data_stats_continuous.reference_mean == statistics.mean(range(1, 6))
    assert data_stats_continuous.reference_stdev == \
        statistics.stdev(range(1, 6))


def test_data_stats_continuous_compute_second_stats(data_stats_continuous):
    for i in range(0, 10):
        data_stats_continuous.append(i)
    assert data_stats_continuous.append(10) == (
        statistics.mean(range(6, 11)), statistics.stdev(range(6, 11)))


def test_data_stats_continuous_update_learning_stats(data_stats_continuous):
    for i in range(0, 24):
        data_stats_continuous.append(i)
    assert data_stats_continuous.reference_mean == \
        statistics.mean(range(19, 24))
    assert data_stats_continuous.reference_stdev == \
        statistics.stdev(range(19, 24))


def test_data_stats_continuous_compute_fourth_stats(data_stats_continuous):
    for i in range(0, 20):
        data_stats_continuous.append(i)
    assert data_stats_continuous.append(20) == (
        statistics.mean(range(16, 21)), statistics.stdev(range(16, 21)))
