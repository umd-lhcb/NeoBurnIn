#!/usr/bin/env python
#
# Last Change: Mon Jan 20, 2020 at 02:46 AM -0500

import pytest

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import DataPassthru
from NeoBurnIn.functional import parse_directive


############################
# For functor construction #
############################

@pytest.fixture
def data():
    return DataPassthru('2020-01-20', 'TEST_CASE1', 6)


def test_directive1(data):
    directive = [
        {
            'match': {'name': "TEST_CASE\\d+", "valueGt": 5},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data) is True


def test_directive2(data):
    directive = [
        {
            'match': {'name': "TEST_CASE\\d+", "valueGt": 7},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data) is False


def test_directive3(data):
    directive = [
        {
            'match': {'name': "TEAST_CASE\\d+", "valueGt": 7},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data) is False
