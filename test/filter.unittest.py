#!/usr/bin/env python
#
# Last Change: Mon Feb 12, 2018 at 09:38 PM -0500

import unittest

import sys
sys.path.insert(0, '..')

from bUrnIn.filters.base import apply_filters
from bUrnIn.filters.base import Filter
from bUrnIn.filters.base import FilterExitCode
from bUrnIn.filters.qa import FilterDataSplit


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


class TestDataSplit(unittest.TestCase):
    def setUp(self):
        self.filter_list = [FilterDataSplit(), FilterTester()]

    def test_data_split(self):
        test_data = '2018-02-09 01:05:25.753840|ch0|2.34414987196'
        (data, exit_code) = apply_filters(test_data, self.filter_list)
        self.assertEqual(data[0], test_data.split('|')[0])
        self.assertEqual(data[2], float(test_data.split('|')[2]))
        self.assertTrue(self.filter_list[1].used)

    def test_data_split_alt_data(self):
        test_data = '2018-02-09 01:05:25.7|ch0|2'
        (data, exit_code) = apply_filters(test_data, self.filter_list)
        self.assertEqual(data[0], test_data.split('|')[0])
        self.assertEqual(data[2], float(test_data.split('|')[2]))
        self.assertTrue(self.filter_list[1].used)

    def test_data_split_wrong_date(self):
        test_data = '2018-02-09 01:05:25|ch0|2.34414987196'

        with self.assertLogs('log', level='INFO') as mock_logger:
            (data, exit_code) = apply_filters(test_data, self.filter_list)
            self.assertEqual(data, test_data)
            self.assertFalse(self.filter_list[1].used)

            self.assertEqual(
                mock_logger.output,
                ['ERROR:log:2018-02-09 01:05:25: Date is not in the correct format']
            )

    def test_data_split_wrong_value(self):
        test_data = '2018-02-09 01:05:25.1926|ch0|EXCITED'

        with self.assertLogs('log', level='INFO') as mock_logger:
            (data, exit_code) = apply_filters(test_data, self.filter_list)
            self.assertEqual(data, test_data)
            self.assertFalse(self.filter_list[1].used)

            self.assertEqual(
                mock_logger.output,
                ['ERROR:log:EXCITED: Value is not in the correct format']
            )


if __name__ == "__main__":
    unittest.main()
