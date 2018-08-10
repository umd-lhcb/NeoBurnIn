#!/usr/bin/env python
#
# Last Change: Fri Aug 10, 2018 at 12:55 AM -0400

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
    server.stash_create()
    return server.stash


def test_initial_value(stash):
    assert stash['overall'] == DataStream(max_length=10000)


def test_default_value_to_a_new_key(stash):
    assert stash['something'] == {
        'summary': DataStream(max_length=1000),
        'time': DataStream(max_length=1000),
        'data': DataStats(max_length=1000)
    }


def test_appendable(stash):
    assert stash['something']['data'].append(1) is False
    assert stash['something']['data'].json_str == '1'
