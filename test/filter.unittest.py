#!/usr/bin/env python
#
# Last Change: Sun Feb 11, 2018 at 10:57 PM -0500

import unittest

import sys
sys.path.insert(0, '..')

from bUrnIn.filters.base import apply_filters
from bUrnIn.filters.base import Filter
from bUrnIn.filters.base import FilterExitCode


class FilterTester(Filter):
    def __init__(self):
        self.used = False

        super().__init__()

    def do(self, data):
        self.used = True
        if data is None:
            return (0, FilterExitCode().error)
        else:
            return (data, FilterExitCode().ok)


class TestApplyFilters(unittest.TestCase):
    def setUp(self):
        self.filter_list = [FilterTester(), FilterTester()]

    def test_apply_filters_ok(self):
        test_data = 'Test'
        (data, exit_code) = apply_filters(test_data, self.filter_list)
        self.assertEqual(data, test_data)
        self.assertEqual(exit_code, FilterExitCode().ok)
        self.assertTrue(self.filter_list[0].used)
        self.assertTrue(self.filter_list[1].used)

    def test_apply_filters_error(self):
        test_data = None
        (data, exit_code) = apply_filters(test_data, self.filter_list)
        self.assertEqual(data, 0)
        self.assertEqual(exit_code, FilterExitCode().error)
        self.assertTrue(self.filter_list[0].used)
        self.assertFalse(self.filter_list[1].used)


if __name__ == "__main__":
    unittest.main()
