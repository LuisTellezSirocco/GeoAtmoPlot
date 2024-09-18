"""
Logging Functions

These module defines the logging mechanism.
"""
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

from pyatmo.settings import LOGGER_NAME


def setup_logger(
        logger_name: str = LOGGER_NAME,
        file_name: Optional[str] = None,
        level_terminal=logging.INFO,
        level_file=logging.DEBUG,
        max_file_size=10 * 1024 * 1024,  # 10 MB
        backup_count=5,
        truncate: bool = True,
) -> logging.Logger:
    """
    Sets up a structured logger with both console and file handlers.

    This function initializes a logger with a specified name and configures it with console and file handlers.
    It supports structured logging by wrapping messages with additional keyword arguments into a JSON format.
    The file handler supports log rotation, limiting the log file size, and optionally truncating the log file at setup.

    Parameters:
    -----------
    logger_name : str
        The name of the logger.
    file_name : Optional[str], optional
        The path to the log file. If None, file logging is disabled.
    level_terminal : int, optional
        The logging level for the console handler.
    level_file : int, optional
        The logging level for the file handler.
    max_file_size : int, optional
        The maximum size of the log file in bytes before it is rotated.
    backup_count : int, optional
        The number of backup files to keep.
    truncate : bool, optional
        If True, the log file is truncated at setup. Default is True.

    Returns:
    --------
    logging.Logger
        The configured logger.

    Examples:
    ---------
    >>> logger = setup_logger('my_logger', 'app.log')
    >>> logger.info('This is an info message')
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    class StructuredMessage:
        def __init__(self, message, **kwargs):
            self.message = message
            self.kwargs = kwargs

        def __str__(self):
            return '%s %s' % (self.message, json.dumps(self.kwargs))

    def structlog(msg, *args, **kwargs):
        return StructuredMessage(msg, **kwargs)

    logger.structlog = structlog

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level_terminal)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)

    # File handler
    if file_name:
        try:
            if truncate and os.path.exists(file_name):
                os.remove(file_name)

            fh = RotatingFileHandler(
                file_name,
                mode="a",  # Always append, we've already handled truncation if needed
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            fh.setLevel(level_file)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s - %(filename)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            fh.setFormatter(file_formatter)
            logger.addHandler(fh)
        except Exception as e:
            logger.error(f"Error creating file handler: {e}", exc_info=True)

    logger.propagate = False
    return logger


def get_logger(module_name: str, logger_name: str = LOGGER_NAME) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        module_name (str): The name of the module requesting the logger.
        logger_name (str, optional): The name of the parent logger. Defaults to LOGGER_NAME.

    Returns:
        logging.Logger: A logger instance for the specified module.

    Raises:
        ValueError: If module_name is empty.
    """
    if not module_name:
        raise ValueError("module_name cannot be empty")
    return logging.getLogger(logger_name).getChild(module_name)

# ==================================================================================================
# EJEMPLO DE USO USANDO DATOS ESTRUCTURADOS
# logger = setup_logger(file_name='app.log')
# logger.info(logger.structlog("User logged in", user_id=12345, ip="192.168.1.1"))
# try:
#     1/0
# except Exception as e:
#     logger.error("An error occurred", exc_info=True)
# ==================================================================================================

# ==================================================================================================
# SETUP_LOGGER UTILIZADO PREVIAMENTE
# ==================================================================================================

# def setup_logger(
#         logger_name: str = LOGGER_NAME,
#         file_name: str = None,
#         level_terminal=logging.DEBUG,
#         level_file=logging.DEBUG,
#         mode="w",
# ) -> logging.Logger:
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(logging.DEBUG)
#
#     # Clear existing handlers
#     logger.handlers.clear()
#
#     # Check if StreamHandler already exists
#     if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
#         ch = logging.StreamHandler()
#         ch.setLevel(level_terminal)
#         formatter = logging.Formatter("%(asctime)s\t%(message)s", datefmt="%H:%M:%S")
#         ch.setFormatter(formatter)
#         logger.addHandler(ch)
#
#     if file_name is not None:
#         # Check if FileHandler already exists
#         if not any(isinstance(h, logging.FileHandler) and h.baseFilename == file_name for h in
#                    logger.handlers):
#             try:
#                 fh = logging.FileHandler(file_name, mode=mode)
#                 fh.setLevel(level_file)
#                 formatter = logging.Formatter(
#                     "%(asctime)s\t%(name)s\t%(levelname)s: %(message)s",
#                     datefmt="%Y/%m/%d %H:%M:%S",
#                 )
#                 fh.setFormatter(formatter)
#                 logger.addHandler(fh)
#             except Exception as e:
#                 logger.error(f"Error creating file handler: {e}")
#
#     # Prevent propagation to avoid duplicate logging
#     logger.propagate = False
#
#     return logger




