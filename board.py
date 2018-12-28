import collections
import itertools
import logging
from key import Key
from location import makeLocCartesian, only_cartesian_locations, \
    is_out_of_bounds

class Board:
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

    @property
    def winningTeam(self):
        if not self.isGameOver:
            return None

        for zone in self._board.values():
            unlockedPiece = zone["unlocked"]
            if unlockedPiece != None:
                return unlockedPiece.team


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


    @staticmethod
    def all_locations():
        """Returns an iterator over all the possible cartesian locations
        on an 8x8 board"""
        return itertools.product(range(0, 8), range(0, 8))

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
        return self.getUnlocked(loc) is not None

    @only_cartesian_locations
    def isLockedPieceAtLocation(self, loc):
        return self.getLocked(loc) is not None

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

        if key is None:
            return []

        move_fn = movers.get(key.direction)

        if move_fn is None:
            log.warn("Invalid key direction given: %s", key.direction)
            return []

        available_moves = []
        next_loc = move_fn(*loc)
        while True:
            if is_out_of_bounds(next_loc):
                return available_moves

            elif self.getUnlocked(next_loc) is None:
                available_moves.append(next_loc)
                next_loc = move_fn(*next_loc)

            elif self.getUnlocked(next_loc).team != key.team:
                available_moves.append(next_loc)
                return available_moves

            else:
                return available_moves

    @only_cartesian_locations
    def getRotatePointsofKeyAtLoc(self, loc):
        key = self.getUnlocked(loc)

        if key == None:
            return {}

        x, y = loc
        rotate_map = {
            "North":      (x - 1, y    ),
            "East":       (x    , y + 1),
            "SouthEast":  (x + 1, y + 1),
            "South":      (x + 1, y    ),
            "SouthWest":  (x + 1, y - 1),
            "West":       (x    , y - 1),
            "NorthEast" : (x - 1, y + 1),
            "NorthWest":  (x - 1, y - 1)
        }

        rotate_map.pop(key.direction, None)
        for direction, location in list(rotate_map.items()):
            if is_out_of_bounds(location):
                rotate_map.pop(direction, None)

        return rotate_map


    def getFreeRespawnPointsForTeam(self, team):
        gold = ["A2", "A4", "A6", "A8"]
        silver = ["H1", "H3", "H5", "H7"]

        def isRespawnFree(location):
            return self.getUnlocked(location) == None

        if team == "gold":
            points = gold
        elif team == "silver":
            points = silver
        else:
            points = []

        return [ makeLocCartesian(loc) for loc in points
                                       if isRespawnFree(loc) ]

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
            if unlockedPiece is not None and lockedPiece is not None:
                if lockedPiece.team == unlockedPiece.team:
                    cell["locked"] = None

    def summarize(self):
        """Returns a JSON-friendly representation of this board"""
        summary = { "unlocked": [], "locked": [] }

        for location in self.all_locations():
            cell = self._board[location]

            unlocked_piece = cell["unlocked"]
            if unlocked_piece is not None:
                summary["unlocked"].append({
                    "location": {"x": location[0], "y": location[1]},
                    "team": unlocked_piece.team,
                    "direction": unlocked_piece.direction.lower()
                })

            locked_piece = cell["locked"]
            if locked_piece is not None:
                summary["locked"].append({
                    "location": {"x": location[0], "y": location[1]},
                    "team": locked_piece.team
                })

        return summary
