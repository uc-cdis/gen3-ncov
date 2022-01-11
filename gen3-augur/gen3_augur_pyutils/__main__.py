"""
Main entrypoint for gen3-augur_pyutils.
"""

import argparse

from gen3_augur_pyutils.common.logger import Logger
from gen3_augur_pyutils.subcommands import Gen3Query
from gen3_augur_pyutils.subcommands import ParseGenBank


def main(args=None, extra_subparser=None):
    """
    The main method for gen3-augur-pyutils.
    :param args:
    :param extra_subparser:
    :return:
    """
    # Setup logger
    Logger.setup_root_logger()

    # Get args
    p = argparse.ArgumentParser("Gen3 Augur Utils")
    subparsers = p.add_subparsers(dest="subcommad")
    subparsers.required = True

    ParseGenBank.add(subparsers=subparsers)
    Gen3Query.add(subparsers=subparsers)

    if extra_subparser:
        extra_subparser.add(subparsers=subparsers)

    options = p.parse_args(args)

    # Run
    options.func(options)

    # Finish


if __name__ == "__main__":
    main()
