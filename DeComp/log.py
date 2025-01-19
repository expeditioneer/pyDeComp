# pylint:disable=invalid-name

"""
Logging module for the DeComp libraries
This module can be overridden by the consumer application
"""

import errno
import logging
import os
import time

logger = logging.getLogger('DeComp')
logger.setLevel(logging.ERROR)

debug = logger.debug
error = logger.error
info = logger.info
warning = logger.warning


def set_logger(logfile_directory: str = '', level: int = logging.DEBUG) -> None:
    """
    Logger initialization function

    :param logfile_directory: optional filepath to save log output to
    :param level: logging level to set the file logger to
    """
    logger.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    formatter = logging.Formatter(log_format)

    # add the handlers to logger
    if logfile_directory:
        if not os.path.exists(logfile_directory):
            raise OSError(errno.ENOENT, f'Log file not found: {logfile_directory}')
        logname = os.path.join(logfile_directory, f"DeComp-{time.strftime('%Y%m%d-%H:%M')}.log")
        file_handler = logging.FileHandler(logname)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
