"""Tests the gen3_augur_pyutils.subcommands.base module"""
import unittest

from utils import cleanup_files, capture_output

from gen3_augur_pyutils.__main__ import main
from gen3_augur_pyutils.subcommands import Subcommand


class TestSubcommand(unittest.TestCase):
    class Example(Subcommand):
        @classmethod
        def __add_arguments__(cls, subparser):
            pass

        @classmethod
        def __main__(cls, options):
            pass

        @classmethod
        def __get_description__(cls):
            return "Example description"

    def test_get_name(self):
        self.assertEqual(TestSubcommand.Example.__tool_name__(), "Example")
        self.assertIsNone(Subcommand.__get_description__())

    def test_no_inputs(self):
        with capture_output() as (_, stderr):
            with self.assertRaises(SystemExit) as context:
                main(args=["Example"])
        self.assertTrue("invalid choice: 'Example'" in stderr.getvalue())

    def test_extra_subparser(self):
        with capture_output() as (_, stderr):
            with self.assertRaises(SystemExit) as context:
                main(args=["Example", "--fake"], extra_subparser=TestSubcommand.Example)
        self.assertTrue("unrecognized arguments: --fake" in stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
