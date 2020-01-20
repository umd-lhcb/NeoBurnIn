#!/usr/bin/env python
#
# Last Change: Mon Jan 20, 2020 at 02:36 AM -0500

import pytest

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import DataPassthru
from NeoBurnIn.functional import name, parse_directive


################
# For functors #
################

@pytest.fixture
def data():
    return DataPassthru('2020-01-20', 'TEST_CASE1', 3.1415)


def test_name_match_non_terminal(data):
    assert name(data, 'TEST_CASE\\d+') == data


def test_name_match_terminal(data):
    assert name(data, 'TEST_CASE\\d+', final=True) is True


def test_name_not_match_non_terminal(data):
    assert name(data, 'TEAST_CAS') is None


def test_name_not_match_terminal(data):
    assert name(data, 'TEAST_CAS', final=True) is False


############################
# For functor construction #
############################

def data_alt():
    return DataPassthru('2020-01-20', 'TEST_CASE1', 6)


def test_directive1(data_alt):
    directive = [
        {
            'match': {'name': "TEST_CASE\\d+", "valueGt": 5},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data_alt) is True


def test_directive2(data_alt):
    directive = [
        {
            'match': {'name': "TEST_CASE\\d+", "valueGt": 7},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data_alt) is False

from NeoBurnIn.functional import *

directive = [
    {
        'match': {'name': "TEST_CASE\\d+", "valueGt": 5},
        'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
    }]
parsed = parse_directive(directive)
combined_functor = list(parsed.keys())[0]
