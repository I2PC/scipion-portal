import logging
from collections import Counter

logger = logging.getLogger(__name__)


def logCounter(msg, counter: Counter):
    logger.info(msg)

    for prot, diff in counter.items():
        logger.info("%s: %s" % (prot, diff))

def substractCounter(initialCounter: Counter, newCounter:Counter):
    """ Calcualte the difference from the 2 counter to update the protocos usage count.

        Default Counter method does not work because a missing protocol in newCounter (removed in a project) should
        decrease the count for that protocol:

        Init: prot1 = 2, prot2 = 2
        New: prot 3 = 3

        Should give as result:
            prot1=-2, prot2=2
    """