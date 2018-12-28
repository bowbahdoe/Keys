"""Helper functions for the Cartesian location hacking that is sprinkled everywhere."""

import functools
import logging

def makeLocCartesian(loc):
    locDic = { "A": 0,
               "B": 1,
               "C": 2,
               "D": 3,
               "E": 4,
               "F": 5,
               "G": 6,
               "H": 7 }

    return (locDic[loc[0]], int(loc[1]) - 1)

def makeLocAlphaNumeric(loc):
    locDic = { 0: 'A',
               1: 'B',
               2: 'C',
               3: 'D',
               4: 'E',
               5: 'F',
               6: 'G',
               7: 'H' }

    return "" + locDic[loc[0]] + str(loc[1] + 1)

def only_cartesian_locations(method):
    """Method decorator to ease transition from
    the old system where locations are represented
    as either a list of two numbers or a chess-like
    string description.

    Assumes that the first argument to the method is the
    location and turns any alpha numeric location to
    cartesian."""
    @functools.wraps(method)
    def wrapped(self, loc, *args, **kwargs):
        if type(loc) == str:
            loc = makeLocCartesian(loc)
        return method(self, loc, *args, **kwargs)

    return wrapped

def is_out_of_bounds(cartesian_loc):
    return cartesian_loc[0] > 7 or cartesian_loc[0] < 0 \
        or cartesian_loc[1] > 7 or cartesian_loc[1] < 0
