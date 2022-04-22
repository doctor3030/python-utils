from __future__ import absolute_import

__title__ = 'python-utils'
__author__ = 'Dmitry Amanov'
__copyright__ = 'Copyright 2022 Dmitry Amanov'

# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

from python_utils.async_utils import AsyncCommands, Command, Subprocess, OutputCallback

__all__ = [
    'AsyncCommands', 'Command', 'Subprocess', 'OutputCallback'
]
