"""Module for defining types for type annotations.
Adapted from Kyle Hernandez's work (https://github.com/COV-IRT/dmwg-data-pyutils/).
@author: Yilin Xu <yilinxu@uchicago.edu>
"""
from typing import NewType
from argparse import ArgumentParser, Namespace
from pandas import DataFrame
from logging import Logger

# ArgParser types, Namespace types and DataFrame types
ArgParserT = NewType("ArgParserT", ArgumentParser)
NamespaceT = NewType("NamespaceT", Namespace)
DataFrameT = NewType("DataFrameT", DataFrame)

# Logger types
LoggerT = NewType("LoggerT", Logger)
