"""Test gen3_augur_pyutils.common.combine_df module"""

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from gen3_augur_pyutils.common.combine_df import merge_multiple_columns


class TestCombine(unittest.TestCase):
    def test_combine_df(self):
        left_data = {"alphabet": ["a", "B", "c", "D", "E"]}
        left_df = pd.DataFrame(left_data)
        right_data = {
            "lower_alphabet": ["a", "b", "c", "d", "e"],
            "upper_alphabet": ["A", "B", "C", "D", "E"],
            "fruit": [
                "Apple",
                "Banana",
                "Cantaloupe",
                "Dragon Fruit",
                "Elephant Apple",
            ],
        }
        right_df = pd.DataFrame(right_data)
        combined_data = {
            "alphabet": ["a", "B", "c", "D", "E"],
            "fruit": [
                "Apple",
                "Banana",
                "Cantaloupe",
                "Dragon Fruit",
                "Elephant Apple",
            ],
        }
        combined_df = pd.DataFrame(combined_data)
        merged_df = merge_multiple_columns(
            left_df, right_df, "alphabet", ["lower_alphabet", "upper_alphabet"], "fruit"
        )
        assert_frame_equal(combined_df, merged_df)


if __name__ == "__main__":
    unittest.main()
