#!/usr/bin/env python3
#
# Last Change: Mon Jun 29, 2020 at 02:42 AM +0800

import pytest

import sys
sys.path.insert(0, '..')

from NeoBurnIn.base import DataStream
from NeoBurnIn.base import DataStats
from NeoBurnIn.io.server import DataServer


######################
# For 'stash_create' #
######################

@pytest.fixture
def stash():
    server = DataServer()
    return server.stash


def test_initial_value(stash):
    assert stash['overall'] == {
        'time': [],
        'data': []
    }


def test_default_value_to_a_new_key(stash):
    assert stash['something'] == {
        'time': DataStream(max_length=1000),
        'data': DataStats(max_length=1000)
    }


def test_appendable(stash):
    assert stash['something']['data'].append(1) is False
    assert stash['something']['data'].json_str == '1'
