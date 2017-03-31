import logging
logging.basicConfig()

from enum import Enum

logger = logging.getLogger('loopabull')
logger.setLevel(logging.INFO)


class Result(Enum):
    runfinished = 1
    runerrored = 2
    unrouted = 3
    error = 4

# vim: set expandtab sw=4 sts=4 ts=4
