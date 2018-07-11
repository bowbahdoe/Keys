import collections
import logging
from key import Key
from location import makeLocCartesian, makeLocAlphaNumeric, only_cartesian_locations, \
    isLocOutOfBounds

class Board:
    '''Begin the ugliest attempt at making the logic for a chess board in
        the history of computer science'''
    def __init__(self):
        '''oh god here we go'''
        self.board = [["A1",None,None],["A2",None,None],["A3",None,None],["A4",None,None],["A5",None,None],["A6",None,None],["A7",None,None],["A8",None,None],
                      ["B1",None,None],["B2",None,None],["B3",None,None],["B4",None,None],["B5",None,None],["B6",None,None],["B7",None,None],["B8",None,None],
                      ["C1",None,None],["C2",None,None],["C3",None,None],["C4",None,None],["C5",None,None],["C6",None,None],["C7",None,None],["C8",None,None],
                      ["D1",None,None],["D2",None,None],["D3",None,None],["D4",None,None],["D5",None,None],["D6",None,None],["D7",None,None],["D8",None,None],
                      ["E1",None,None],["E2",None,None],["E3",None,None],["E4",None,None],["E5",None,None],["E6",None,None],["E7",None,None],["E8",None,None],
                      ["F1",None,None],["F2",None,None],["F3",None,None],["F4",None,None],["F5",None,None],["F6",None,None],["F7",None,None],["F8",None,None],
                      ["G1",None,None],["G2",None,None],["G3",None,None],["G4",None,None],["G5",None,None],["G6",None,None],["G7",None,None],["G8",None,None],
                      ["H1",None,None],["H2",None,None],["H3",None,None],["H4",None,None],["H5",None,None],["H6",None,None],["H7",None,None],["H8",None,None]]
        #This deserves alot of explaination because it is the worst possible way to do this
        #
        #The board is a tuple of lists containing String objects in index[0] naming the location on the board
        #
        #          1|2|3|4|5|6|7|8
        #          _______________
        #        A|
        #        B|
        #        C|
        #        D|
        #        E|
        #        F|
        #        G|
        #        H|
        #
        #The second item in the list is any key object that may be on that location and if there is no key there it
        #will have a None value
        #
        #The third item is for storing any locked keys
        #otherwise it will be None

    def reset(self):
        for location in self.board:
            location[2] = None
            location[1] = None
        self.setup()


    @property
    def isGameOver(self):
        silver = 0
        gold = 0

        for location in self.board:
            unlockedPiece = location[1]
            if unlockedPiece != None:
                if unlockedPiece.team == "gold":
                    gold += 1
                else:
                    silver += 1

        return gold == 0 or silver == 0

    def _findLocationIndexById(self,ID):
        for square in self.board:
            if square[0] == ID:
                return self.board.index(square)

    def movePieceToLocation(self, loc, piece):
        lastLoc = piece.location
        lastLocOnBoard = self._findLocationIndexById(lastLoc)
        if self.isLockedPieceAtLocation(loc):
            self.lockPieceAtLocation(loc)
        self.board[lastLocOnBoard][1] = None
        newLocOnBoard = self._findLocationIndexById(loc)

        self.board[newLocOnBoard][1] = piece
        piece.location = loc


    def addPieceToLocation(self, loc, piece):
        newLocOnBoard = self._findLocationIndexById(loc)
        self.board[newLocOnBoard][1] = piece
        piece.location = loc


    def addLockedPieceToLocation(self, loc, piece):
        piece.lock()
        newLocOnBoard = self._findLocationIndexById(loc)
        self.board[newLocOnBoard][2] = piece
        piece.location = loc


    def lockPieceAtLocation(self,loc):
        location_index = self._findLocationIndexById(loc)
        if self.board[location_index][1] != None and self.board[2] == None:
            self.board[location_index][2] = self.board[location_index][1]
            self.board[location_index][1] = None
            self.board[location_index][2].lock()
        else:
            pass


    def unlockPieceAtLocation(self,loc):
        #TODO make it so the piece is reset to a spawn point instead of
        #just getting moved to the unlocked space
        Loc = self._findLocationIndexById(loc)
        if self.board[Loc][2]!= None:
            self.board[Loc][2] = None
        else:
            pass

    @only_cartesian_locations
    def removeLockedPiece(self, cartesian_loc):
        loc = self._findLocationIndexById(cartesian_loc)
        self.board[loc][2] = None

    def isPieceAtLocation(self,loc):
        loc = self._findLocationIndexById(loc)
        return self.board[loc][1] != None


    def isLockedPieceAtLocation(self,loc):
        loc = self._findLocationIndexById(loc)
        return self.board[loc][2] != None

    def getUnlocked(self, loc):
        if type(loc) != str:
            loc = makeLocAlphaNumeric(loc)

        if self.isPieceAtLocation(loc):
            loc = self._findLocationIndexById(loc)
            return self.board[loc][1]
        else:
            return None


    def getLocked(self, loc):
        if type(loc) != str:
            loc = makeLocAlphaNumeric(loc)

        if self.isLockedPieceAtLocation(loc):
            loc = self._findLocationIndexById(loc)
            return self.board[loc][2]
        else:
            pass


    @only_cartesian_locations
    def getValidMovesOfKeyAtLoc(self,loc):
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

        evolver_fn = movers.get(key.direction)

        if evolver_fn == None:
            log.warn("Invalid key direction given: %s", key.direction)
            return []


        available_moves = []
        next_loc = evolver_fn(*loc)
        while True:
            if isLocOutOfBounds(next_loc):
                return available_moves

            elif self.getUnlocked(next_loc) == None:
                available_moves.append(next_loc)
                next_loc = evolver_fn(*next_loc)

            elif self.getUnlocked(next_loc).team != key.team:
                available_moves.append(next_loc)
                return available_moves

            else:
                return available_moves

    def getDirectionIndicatedByRotatePoint(self, cartesian_loc):
        '''Seriosly, I need to do planning ahead before I
        do anything important. I always end up with about 20 stupid
        functions. Not-so-fun-ctions'''

        loc = tuple(cartesian_loc)

        if loc == self.oneright:
            return "East"
        elif loc == self.downright:
            return "SouthEast"
        elif loc == self.onebelow:
            return "South"
        elif loc == self.downleft:
            return "SouthWest"
        elif loc == self.oneleft:
            return "West"
        elif loc == self.upright:
            return "NorthEast"
        elif loc == self.upleft:
            return "NorthWest"
        elif loc == self.oneabove:
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


    def setup(self):
        '''This function, as of now, sets up the pieces how
            we have them at the beggining of a game'''
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
        for place in self.board:
            unlockedPiece = place[1]
            lockedPiece = place[2]
            if unlockedPiece != None and lockedPiece != None:
                if lockedPiece.team == unlockedPiece.team:
                    place[2] = None
