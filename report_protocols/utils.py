import logging
from collections import Counter

logger = logging.getLogger(__name__)

def logCounter(msg, counter: Counter):
    logger.info(msg)

    for prot, diff in counter.items():
        logger.info("%s: %s" % (prot, diff))
