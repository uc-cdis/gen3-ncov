"""Tests the gen3_augur_pyutils.common.date module"""
import unittest
import datetime

from gen3_augur_pyutils.common.date import date_conform


class TestDate(unittest.TestCase):
    def test_date_conform(self):
        """
        Test date format '%d-%b-%Y', '%b-%Y', '%d-%b-%Y', '%Y-%m', '%Y'
        :return:
        """
        d1 = datetime.date(2020, 3, 19)
        date_string_1 = "19-Mar-2020"
        date_1 = date_conform(date_string_1)
        self.assertEqual(date_1, d1)

        d2 = datetime.date(2020, 3, 1)
        date_string_2 = "Mar-2020"
        date_2 = date_conform(date_string_2)
        self.assertEqual(date_2, d2)

        d3 = datetime.date(2020, 3, 19)
        date_string_3 = "2020-3-19"
        date_3 = date_conform(date_string_3)
        self.assertEqual(date_3, d3)

        d4 = datetime.date(2020, 3, 1)
        date_string_4 = "2020-3"
        date_4 = date_conform(date_string_4)
        self.assertEqual(date_4, d4)

        d5 = datetime.date(2020, 1, 1)
        date_string_5 = "2020"
        date_5 = date_conform(date_string_5)
        self.assertEqual(date_5, d5)


if __name__ == "__main__":
    unittest.main()
