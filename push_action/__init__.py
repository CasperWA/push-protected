"""Push protected

This Python module is a helper module to interact with the GitHub API.
It is meant to only be used in the `push-protected` GitHub action.
"""

import logging
import os
import sys

__version__ = "2.16.0"
__author__ = "Casper Welzel Andersen"


LOGGER = logging.getLogger("push_action")

if os.getenv("INPUT_DEBUG", "").lower() in ("true", "1"):
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(logging.StreamHandler(sys.stderr))
