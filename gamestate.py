class GameState:
    def __init__(self, board):
        self.teamRespawning = None
        self.teamPlaying = "gold"
        self.pieceSelected = None
        self.board = board

    def setRespawnOn(self,team):
        self.teamRespawning = team

    def setRespawnOff(self):
        self.teamRespawning = None

    @property
    def isRespawningNow(self):
        return self.teamRespawning != None

    def changeTurn(self):
        if self.teamPlaying == "gold":
            self.teamPlaying = "silver"
        else:
            self.teamPlaying = "gold"

    @property
    def validMoves(self):
        """Returns the valid moves of any selected piece"""
        return self.board.validMovesOfKeyAtLoc(self.pieceSelected)

    def summarize(self):
        return {
            "mode": determine_mode(self),
            "board": self.board.summarize()
        }

    def reset(self):
        self.teamRespawning = None
        self.teamPlaying = "gold"
        self.pieceSelected = None
        self.board.reset()

    @property
    def isGameOver(self):
        return self.board.isGameOver

    @property
    def winningTeam(self):
        return self.board.winningTeam

def determine_mode(gamestate):
    """NOTE: As of writing, makes use of some hacks. Be sure to clean up
    the logic here more."""
    if gamestate.teamPlaying == "gold":
        prefix = "GOLD_"
    else:
        prefix = "SILVER_"

    if gamestate.isGameOver:
        return gamestate.winningTeam.upper() + "_WIN"
    elif gamestate.isRespawningNow:
        return prefix + "RESPAWNING"
    else:
        return prefix + "PLAY"

def _rev_dict(d):
    return {v: k for k, v in d.items()}

class Move:
    def __init__(self, *, team, from_, to):
        self._team = team
        self._from = from_
        self._to = to

    def __call__(self, gamestate):
        board = gamestate.board
        lockedPieceAtDest = board.getLocked(self._to)
        unlockedPieceAtDest = board.getUnlocked(self._to)
        unlockedPieceAtSource = board.getUnlocked(self._from)

        if unlockedPieceAtSource is None or unlockedPieceAtSource.team != self._team:
            return

        if not gamestate.isRespawningNow and not gamestate.isGameOver:
            if self._to in gamestate.validMoves:
                if unlockedPieceAtDest is not None:
                    if unlockedPieceAtDest.team != unlockedPieceAtSource.team:
                        board.addLockedPieceToLocation(self._to, unlockedPieceAtDest)
                if lockedPieceAtDest is not None:
                    if lockedPieceAtDest.team == unlockedPieceAtSource.team:
                        gamestate.setRespawnOn(lockedPieceAtDest.team)
                        gamestate.changeTurn() # HACK: Figure out how to flow this logic so the correct team is playing after respawn
                                              # This line relies on the turn being changed again below.
                board.movePieceToLocation(self._to, board.getUnlocked(self._from))
                gamestate.changeTurn()

    def __repr__(self):
        return f"Move {{ team = {self._team}, from = {self._from}, to = {self._to} }}"

class Rotate:
    def __init__(self, *, team, at, facing):
        self._team = team
        self._at = at
        self._facing = facing

    def __call__(self, gamestate):
        board = gamestate.board
        piece = board.getUnlocked(self._at)

        if piece is None or piece.team != self._team or piece.direction == self._facing:
            return

        if not gamestate.isRespawningNow and not gamestate.isGameOver:
            piece.direction = self._facing
            board.addPieceToLocation(piece.location, piece)
            gamestate.changeTurn()

    def __repr__(self):
        return f"Rotate {{ team = {self._team}, at = {self._at}, facing = {self._facing} }}"

class Respawn:
    def __init__(self, *, team, at):
        self._team = team
        self._at = at

    def __call__(self, gamestate):
        board = gamestate.board
        if gamestate.isRespawningNow:
            respawn_points = board.getFreeRespawnPointsForTeam(self._team)

            if self._at in respawn_points:
                if gamestate.teamRespawning == "gold":
                    key = Key(self._at, "South", False, "gold")
                    board.addPieceToLocation(self._at, key)
                elif gamestate.teamRespawning == "silver":
                    key = Key(self._at, "North", False, "silver")
                    board.addPieceToLocation(self._at, key)

                gamestate.setRespawnOff()
                board.collapse_locked()
                gamestate.changeTurn()

    def __repr__(self):
        return f"Respawn {{ team = {self._team}, at = {self._at} }}"

class NoOp:
    def __call__(self, gamestate):
        pass

    def __repr__(self):
        return "NoOp"

class Reset:
    def __call__(self, gamestate):
        gamestate.reset()

    def __repr__(self):
        return "Reset"
