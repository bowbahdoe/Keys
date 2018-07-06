import functools
import logging
from location import makeLocCartesian

log = logging.getLogger(__name__)

def only_cartesian_locations(method):
    """Function decorator to ease transition from
    the old system where locations are represented
    as either a list of two numbers or a chess-like
    string description.

    Assumes that the first argument to the method is the
    location and turns any alpha numeric location to
    cartesian."""
    @functools.wraps(method)
    def wrapped(self, loc, *args, **kwargs):
        if type(loc) == str:
            log.info("String location intercepted in method %s: %s", method, loc)
            loc = makeLocCartesian(loc)
        return method(self, loc, *args, **kwargs)

    return wrapped
