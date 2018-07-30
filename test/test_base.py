#!/usr/bin/env python
#
# Last Change: Mon Jul 30, 2018 at 11:27 AM -0400

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
    for i in range(5):
        assert data_stream.append(i) is False
    for i in range(6, 8):
        assert data_stream.append(i) is True


@pytest.mark.xfail(reason="Not implemented yet.")
def test_data_stream_pass_generator_as_an_argument():
    data_stream = DataStream(range(0, 6), max_length=5)
    assert data_stream == [i for i in range(1, 6)]


##################################
# For 'DataStats', partial defer #
##################################

@pytest.fixture
def data_stats_partial():
    return DataStats(max_length=5, defer_until_full_renewal=False)


def test_data_stats_partial_append_partial_not_full(data_stats_partial):
    for i in range(0, 5):
        assert data_stats_partial.append(i) is False


def test_data_stats_partial_append_partial_not_full_content(data_stats_partial):
    for i in range(0, 5):
        data_stats_partial.append(i) is False
    assert data_stats_partial == [0, 1, 2, 3, 4]
    assert data_stats_partial.json_str == '0,1,2,3,4'


def test_data_stats_partial_compute_first_stats(data_stats_partial):
    for i in range(0, 5):
        data_stats_partial.append(i)
    assert data_stats_partial.append(5) == (
        statistics.mean([1, 2, 3, 4, 5]),
        statistics.stdev([1, 2, 3, 4, 5])
    )


def test_data_stats_partial_store_learning_stats(data_stats_partial):
    for i in range(0, 6):
        data_stats_partial.append(i)
    assert data_stats_partial.reference_mean == \
        statistics.mean([1, 2, 3, 4, 5])
    assert data_stats_partial.reference_stdev == \
        statistics.stdev([1, 2, 3, 4, 5])


def test_data_stats_partial_compute_second_stats(data_stats_partial):
    for i in range(0, 6):
        data_stats_partial.append(i)
    assert data_stats_partial.append(6) == (
        statistics.mean([2, 3, 4, 5, 6]),
        statistics.stdev([2, 3, 4, 5, 6])
    )


def test_data_stats_partial_preserve_learning_stats(data_stats_partial):
    for i in range(0, 14):
        data_stats_partial.append(i)
    assert data_stats_partial.reference_mean == \
        statistics.mean([1, 2, 3, 4, 5])
    assert data_stats_partial.reference_stdev == \
        statistics.stdev([1, 2, 3, 4, 5])


def test_data_stats_partial_compute_third_stats(data_stats_partial):
    for i in range(0, 7):
        data_stats_partial.append(i)
    assert data_stats_partial.append(7) == (
        statistics.mean([3, 4, 5, 6, 7]),
        statistics.stdev([3, 4, 5, 6, 7])
    )


###############################
# For 'DataStats', full defer #
###############################

@pytest.fixture
def data_stats_full():
    return DataStats(max_length=5, defer_until_full_renewal=True)


def test_data_stats_full_append_partial_not_full(data_stats_full):
    for i in range(0, 5):
        assert data_stats_full.append(i) is False


def test_data_stats_full_append_partial_not_full_content(data_stats_full):
    for i in range(0, 5):
        data_stats_full.append(i) is False
    assert data_stats_full == [0, 1, 2, 3, 4]
    assert data_stats_full.json_str == '0,1,2,3,4'


def test_data_stats_full_compute_first_stats(data_stats_full):
    for i in range(0, 5):
        data_stats_full.append(i)
    assert data_stats_full.append(5) == (
        statistics.mean([1, 2, 3, 4, 5]),
        statistics.stdev([1, 2, 3, 4, 5])
    )


def test_data_stats_full_store_learning_stats(data_stats_full):
    for i in range(0, 6):
        data_stats_full.append(i)
    assert data_stats_full.reference_mean == \
        statistics.mean([1, 2, 3, 4, 5])
    assert data_stats_full.reference_stdev == \
        statistics.stdev([1, 2, 3, 4, 5])


def test_data_stats_full_after_first_full(data_stats_full):
    for i in range(0, 6):
        data_stats_full.append(i)
    for i in range(6, 10):
        assert data_stats_full.append(i) is False


def test_data_stats_full_compute_second_stats(data_stats_full):
    for i in range(0, 10):
        data_stats_full.append(i)
    assert data_stats_full.append(10) == (
        statistics.mean([6, 7, 8, 9, 10]),
        statistics.stdev([6, 7, 8, 9, 10]),
    )


def test_data_stats_full_preserve_learning_stats(data_stats_full):
    for i in range(0, 24):
        data_stats_full.append(i)
    assert data_stats_full.reference_mean == \
        statistics.mean([1, 2, 3, 4, 5])
    assert data_stats_full.reference_stdev == \
        statistics.stdev([1, 2, 3, 4, 5])


def test_data_stats_full_compute_third_stats(data_stats_full):
    for i in range(0, 15):
        data_stats_full.append(i)
    assert data_stats_full.append(15) == (
        statistics.mean([11, 12, 13, 14, 15]),
        statistics.stdev([11, 12, 13, 14, 15]),
    )


def test_data_stats_full_after_third_full(data_stats_full):
    for i in range(0, 16):
        data_stats_full.append(i)
    for i in range(16, 20):
        assert data_stats_full.append(i) is False


def test_data_stats_json_str_after_third_full(data_stats_full):
    for i in range(0, 16):
        data_stats_full.append(i)
    data_stats_full.append(17)
    assert data_stats_full.json_str == '12,13,14,15,17'


def test_data_stats_full_compute_fourth_stats(data_stats_full):
    for i in range(0, 20):
        data_stats_full.append(i)
    assert data_stats_full.append(20) == (
        statistics.mean([16, 17, 18, 19, 20]),
        statistics.stdev([16, 17, 18, 19, 20]),
    )
