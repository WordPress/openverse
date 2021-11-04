"""
This module has public methods which are useful for storage operations.
"""
import logging


logger = logging.getLogger(__name__)


def get_source(source, provider):
    """
    Returns `source` if given, otherwise `provider`
    """
    if not source:
        source = provider

    return source
