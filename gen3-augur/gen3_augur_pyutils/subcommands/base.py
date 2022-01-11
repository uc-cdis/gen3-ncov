"""
Abstract base class for all subcommands in gen3-augur-pyutils
based off of Kyle Hernandez's work (https://github.com/COV-IRT/dmwg-data-pyutils/).
@author: Yilin Xu <yilinxu@uchicago.edu>
"""
from abc import ABCMeta, abstractmethod

from gen3_augur_pyutils.common.types import ArgParserT, NamespaceT


class Subcommand(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def __add_arguments__(cls, parser: ArgParserT):
        """Add the argument to the parser"""

    @classmethod
    @abstractmethod
    def main(cls, options: NamespaceT) -> None:

        """
        The default function when the subcommand is selected. Return None if executed successfully.
        """

    @classmethod
    def __get_description__(cls):
        """
        Optionally returns description
        """
        return None

    @classmethod
    def __tool_name__(cls):
        """
        Tool name to use for the subparser
        """
        return cls.__name__

    @classmethod
    def add(cls, subparsers: ArgParserT) -> ArgParserT:
        """
        Add the given subcommand to the subparsers
        """
        subparser = subparsers.add_parser(
            name=cls.__tool_name__(), description=cls.__get_description__()
        )
        cls.__add_arguments__(subparser)
        subparser.set_defaults(func=cls.main)
        return subparser
