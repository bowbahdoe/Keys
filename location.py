"""Helper functions for the Cartesian location hacking that is sprinkled everywhere."""

import functools
import logging

def makeLocCartesian(loc):
    locDic = { "A": 1,
               "B": 2,
               "C": 3,
               "D": 4,
               "E": 5,
               "F": 6,
               "G": 7,
               "H": 8 }

    return [locDic[loc[0]], int(loc[1])]

def makeLocAlphaNumeric(loc):
    locDic = { 1: 'A',
               2: 'B',
               3: 'C',
               4: 'D',
               5: 'E',
               6: 'F',
               7: 'G',
               8: 'H' }

    return "" + locDic[loc[0]] + str(loc[1])

def only_cartesian_locations(method):
    """Function decorator to ease transition from
    the old system where locations are represented
    as either a list of two numbers or a chess-like
    string description.

    Assumes that the first argument to the method is the
    location and turns any alpha numeric location to
    cartesian."""
    log = logging.getLogger(__name__)

    @functools.wraps(method)
    def wrapped(self, loc, *args, **kwargs):
        if type(loc) == str:
            log.info("String location intercepted in method %s: %s", method, loc)
            loc = makeLocCartesian(loc)
        return method(self, loc, *args, **kwargs)

    return wrapped
