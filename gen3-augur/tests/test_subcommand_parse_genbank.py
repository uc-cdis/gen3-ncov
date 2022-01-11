"""Test gen3_augur_pyutils.subcommands.parse_genbank module"""
import logging
import unittest
from pathlib import Path

from gen3_augur_pyutils.common.io import IO
from gen3_augur_pyutils.subcommands import ParseGenBank

logger = logging.getLogger("__name__")


class TestSubcommandParseGenbank(unittest.TestCase):
    def test_parse_bg(self):
        dir_path = Path(__file__).resolve().parents[1]
        with IO.change_dir(dir_path):
            self.assertIsNone(
                ParseGenBank.parse_bg("data/test-genbank-rawbg/EU371562.gb", logger)
            )
            (meta, seq) = ParseGenBank.parse_bg(
                "data/test-genbank-rawbg/MT027062.gb", logger
            )
            self.assertEqual(meta["strain"], "2019-nCoV/USA-CA3/2020-MT027062.gb")
            self.assertIsNotNone(seq)


if __name__ == "__main__":
    unittest.main()
