"""Module for custom logging. Adapted from Kyle Hernandez's
work (https://github.com/COV-IRT/dmwg-data-pyutils/).
@author: Yilin Xu <yilinxu@uchicago.edu>
"""

import logging
import sys
from gen3_augur_pyutils.common.types import LoggerT


class Logger(object):
    """
    Provides methods to track loggers
    """

    RootLogger = logging.getLogger("gen3_augur_pyutils")
    LoggerFormat = "[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s"

    @classmethod
    def setup_root_logger(cls) -> None:
        """Sets up the root logger and should only be called once."""
        for handle in Logger.RootLogger.handlers:
            Logger.RootLogger.removeHandler(handle)
            Logger.RootLogger.setLevel(level=Logger.LoggerLevel)

        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(Logger.LoggerFormat, datefmt="%Y%m%d %H:%M:%S")
        handler.setFormatter(formatter)
        Logger.RootLogger.addHandler(handler)

    LoggerLevel = logging.INFO

    @classmethod
    def get_logger(cls, name, file, stream=None) -> LoggerT:
        """Gets a logger with the given name and file path.  If a ``stream`` is not
        provided, the logger will be a child of the root logger, otherwise, a
        new logger is created using the given ``stream``."""
        if not stream:
            logger = Logger.RootLogger.getChild(name)
            file_handler = logging.FileHandler(file)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                Logger.LoggerFormat, datefmt="%Y%m%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            logger = logging.getLogger(name)
            handler = logging.StreamHandler(stream)
            formatter = logging.Formatter(Logger.LoggerFormat)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger


Logger.setup_root_logger()
