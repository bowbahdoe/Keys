import collections
import logging
from key import Key
from location import makeLocCartesian, only_cartesian_locations, \
    isLocOutOfBounds

class Board:
    '''Begin the ugliest attempt at making the logic for a chess board in
        the history of computer science'''
    def __init__(self):
        self._board = collections.defaultdict(
            lambda: { "locked": None, "unlocked": None }
        )

    def reset(self):
        self._board.clear()
        self._setup()


    @property
    def isGameOver(self):
        silver = 0
        gold = 0

        for zone in self._board.values():
            unlockedPiece = zone["unlocked"]
            if unlockedPiece != None:
                if unlockedPiece.team == "gold":
                    gold += 1
                else:
                    silver += 1

        return gold == 0 or silver == 0

    @only_cartesian_locations
    def movePieceToLocation(self, loc, piece):
        lastLoc = piece.location

        if self.isLockedPieceAtLocation(loc):
            self.lockPieceAtLocation(loc)
        self._board[lastLoc]["unlocked"] = None

        self._board[loc]["unlocked"] = piece

        piece.location = loc


    @only_cartesian_locations
    def addPieceToLocation(self, loc, piece):
        self._board[loc]["unlocked"] = piece
        piece.location = loc


    @only_cartesian_locations
    def addLockedPieceToLocation(self, loc, piece):
        piece.lock()
        self._board[loc]["locked"] = piece
        piece.location = loc

    @only_cartesian_locations
    def lockPieceAtLocation(self,loc):
        cell = self._board[loc]
        unlocked = cell["unlocked"]
        locked = cell["locked"]
        if unlocked != None and locked == None:
            unlocked.lock()
            cell["locked"] = unlocked
            cell["unlocked"] = None
        else:
            pass

    @only_cartesian_locations
    def removeLockedPiece(self, cartesian_loc):
        self._board[loc]["locked"] = None

    @only_cartesian_locations
    def isPieceAtLocation(self, loc):
        return self.getUnlocked(loc) != None

    @only_cartesian_locations
    def isLockedPieceAtLocation(self, loc):
        return self.getLocked(loc) != None

    @only_cartesian_locations
    def getUnlocked(self, loc):
        return self._board[loc].get("unlocked", None)

    @only_cartesian_locations
    def getLocked(self, loc):
        return self._board[loc].get("locked", None)

    @only_cartesian_locations
    def validMovesOfKeyAtLoc(self, loc):
        """Given a location, gives all the moves that a key there
        could make or an empty list if there isnt a piece there"""
        log = logging.getLogger(__name__)

        movers = {
            "North":     lambda x, y: (x - 1, y    ),
            "NorthWest": lambda x, y: (x - 1, y - 1),
            "NorthEast": lambda x, y: (x - 1, y + 1),
            "West":      lambda x, y: (x    , y - 1),
            "SouthWest": lambda x, y: (x + 1, y - 1),
            "South":     lambda x, y: (x + 1, y    ),
            "SouthEast": lambda x, y: (x + 1, y + 1),
            "East":      lambda x, y: (x    , y + 1)
        }


        key = self.getUnlocked(loc)

        if key == None:
            log.warn("No key at the given location")
            return []

        move_fn = movers.get(key.direction)

        if move_fn == None:
            log.warn("Invalid key direction given: %s", key.direction)
            return []

        available_moves = []
        next_loc = move_fn(*loc)
        while True:
            if isLocOutOfBounds(next_loc):
                return available_moves

            elif self.getUnlocked(next_loc) == None:
                available_moves.append(next_loc)
                next_loc = move_fn(*next_loc)

            elif self.getUnlocked(next_loc).team != key.team:
                available_moves.append(next_loc)
                return available_moves

            else:
                return available_moves

    @only_cartesian_locations
    def getDirectionIndicatedByRotatePoint(self, cartesian_loc):
        '''Seriosly, I need to do planning ahead before I
        do anything important. I always end up with about 20 stupid
        functions. Not-so-fun-ctions'''

        if cartesian_loc == self.oneright:
            return "East"
        elif cartesian_loc == self.downright:
            return "SouthEast"
        elif cartesian_loc == self.onebelow:
            return "South"
        elif cartesian_loc == self.downleft:
            return "SouthWest"
        elif cartesian_loc == self.oneleft:
            return "West"
        elif cartesian_loc == self.upright:
            return "NorthEast"
        elif cartesian_loc == self.upleft:
            return "NorthWest"
        elif cartesian_loc == self.oneabove:
            return "North"
        else:
            return None


    @only_cartesian_locations
    def getRotatePointsofKeyAtLoc(self, loc):
        key = self.getUnlocked(loc)

        if key == None:
            raise Exception("No key at the given location")

        x, y = loc

        returner = []
        self.oneright =   (x    , y + 1)
        self.downright =  (x + 1, y + 1)
        self.onebelow =   (x + 1, y    )
        self.downleft =   (x + 1, y - 1)
        self.oneleft =    (x    , y - 1)
        self.upright =    (x - 1, y + 1)
        self.upleft =     (x - 1, y - 1)
        self.oneabove =   (x - 1, y    )

        if key.direction != "North":
            returner.append(self.oneabove)
        else:
            self.oneabove = None
        if key.direction != "East":
            returner.append(self.oneright)
        else:
            self.oneright = None
        if key.direction != "SouthEast":
            returner.append(self.downright)
        else:
            self.downright = None
        if key.direction != "South":
            returner.append(self.onebelow)
        else:
            self.onebelow = None
        if key.direction != "SouthWest":
            returner.append(self.downleft)
        else:
            self.downleft = None
        if key.direction != "West":
            returner.append(self.oneleft)
        else:
            self.oneleft = None
        if key.direction != "NorthEast":
            returner.append(self.upright)
        else:
            self.upright = None
        if key.direction != "NorthWest":
            returner.append(self.upleft)
        else:
            self.upleft = None

        for loc in returner:
            if isLocOutOfBounds(loc):
                returner.remove(loc)

        return returner


    def getFreeRespawnPointsForTeam(self, team):
        gold = ["A2", "A4", "A6", "A8"]
        silver = ["H1", "H3", "H5", "H7"]

        def isRespawnFree(location):
            return self.getUnlocked(location) == None

        if team == "gold":
            return list(filter(isRespawnFree, gold))
        else:
            return list(filter(isRespawnFree, silver))

    @classmethod
    def default(cls):
        self = cls()
        self._setup()
        return self

    def _setup(self):
        gold1 = Key("A2", "South", False, "gold")
        gold2 = Key("A4", "South", False, "gold")
        gold3 = Key("A6", "South", False, "gold")

        self.addPieceToLocation("A2", gold1)
        self.addPieceToLocation("A4", gold2)
        self.addPieceToLocation("A6", gold3)

        silver1 = Key("H3", "North", False, "silver")
        silver2 = Key("H5", "North", False, "silver")
        silver3 = Key("H7", "North", False, "silver")

        self.addPieceToLocation("H3", silver1)
        self.addPieceToLocation("H5", silver2)
        self.addPieceToLocation("H7", silver3)

    def collapse_locked(self):
        """If a cell has a locked key and an unlocked key
        of the same team, deletes the locked key."""
        for cell in self._board.values():
            unlockedPiece = cell["unlocked"]
            lockedPiece = cell["locked"]
            if unlockedPiece != None and lockedPiece != None:
                if lockedPiece.team == unlockedPiece.team:
                    cell["locked"] = None
