#!/usr/bin/env python3
#
# Last Change: Mon Jan 20, 2020 at 05:02 AM -0500

import pytest

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import DataPassthru
from NeoBurnIn.functional import parse_directive
from NeoBurnIn.DataSink import Test


############################
# For functor construction #
############################

@pytest.fixture
def data():
    return DataPassthru('2020-01-20', 'TEST_CASE1', 6)


def test_directive_match_true_true(data):
    directive = [
        {
            'match': {'name': "TEST_CASE\\d+", "valueGt": 5},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data) is True


def test_directive_match_true_false(data):
    directive = [
        {
            'match': {'name': "TEST_CASE\\d+", "valueGt": 7},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data) is False


def test_directive_match_false_true(data):
    directive = [
        {
            'match': {'name': "TEAST_CASE\\d+", "valueGt": 7},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    parsed = parse_directive(directive)
    combined_functor = list(parsed.keys())[0]

    assert combined_functor(data) is False


def test_directive_action(data):
    directive = [
        {
            'match': {'name': "TEAST_CASE\\d+", "valueGt": 7},
            'action': {'sink': 'tester1', 'state': 'off', 'ch': 1}
        }]
    controllers = {
        'tester1': Test.TestSink('localhost', '45679')
    }
    parsed = parse_directive(directive)
    executor = list(parsed.values())[0]

    assert executor(controllers) == 'http://localhost:45679/test/1/off'
