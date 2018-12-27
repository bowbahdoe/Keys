import sys
import logging
from board import Board
from key import Key
from location import makeLocCartesian, only_cartesian_locations
from screen import Screen

import pygame
from pygame.locals import *

# These 2 need to be divisible by 8
DISPLAYHEIGHT = 600
DISPLAYWIDTH = 600
RESOLUTION = (DISPLAYHEIGHT,DISPLAYWIDTH)
FPS = 30

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
        self._to = todo

    def __call__(self, gamestate):
        pass

class Rotate:
    def __init__(self, *, team, at, facing):
        self._team = team
        self._at = at
        self._facing = facing

    def __call__(self, gamestate):
        pass

class Respawn:
    def __init__(self, *, team, at):
        self._team = team
        self._at = at

    def __call__(self, gamestate):
        pass

class NoOp:
    def __call__(self, gamestate):
        pass

def determine_move(*, clickloc, gamestate):
    board = gamestate.board

    if gamestate.teamPlaying is None:
        return NoOp()

    if not gamestate.isRespawningNow:
        if clickLoc in gamestate.validMoves:
            return Move(team = gamestate.teamPlaying,
                        from_ = gamestate.pieceSelected,
                        to = clickLoc)

        elif clickLoc in board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected).values():
            direc = _rev_dict(board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected))[clickLoc]
            return Rotate(team = gamestate.teamPlaying,
                          at = gamestate.pieceSelected,
                          facing = direc)
        else:
            return NoOp()
    else:
        return Respawn(team = gamestate.teamRespawning, at = clickLoc)

def handleKeyPress(*, clickLoc, gamestate):
    board = gamestate.board
    lockedPieceAtDest = board.getLocked(clickLoc)
    unlockedPieceAtDest = board.getUnlocked(clickLoc)

    print(determine_move(clickLoc = clickLoc, gamestate = gamestate))
    
    if not gamestate.isRespawningNow:
        if clickLoc in gamestate.validMoves:
            if unlockedPieceAtDest != None:
                if unlockedPieceAtDest.team != board.getUnlocked(gamestate.pieceSelected).team:
                    board.addLockedPieceToLocation(clickLoc, unlockedPieceAtDest)
            if lockedPieceAtDest != None:
                if lockedPieceAtDest.team == board.getUnlocked(gamestate.pieceSelected).team:
                    gamestate.setRespawnOn(lockedPieceAtDest.team)
                    gamestate.changeTurn() # HACK: Figure out how to flow this logic so the correct team is playing after respawn
                                           # This line relies on the turn being changed again below.
            board.movePieceToLocation(clickLoc, board.getUnlocked(gamestate.pieceSelected))

            gamestate.changeTurn()
            gamestate.pieceSelected = None

        elif clickLoc in board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected).values():
            direc = _rev_dict(board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected))[clickLoc]
            piece = board.getUnlocked(gamestate.pieceSelected)

            piece.direction = direc
            board.addPieceToLocation(board.getUnlocked(gamestate.pieceSelected).location,
                                     piece)
            gamestate.changeTurn()
            gamestate.pieceSelected = None

        elif board.isPieceAtLocation(clickLoc) \
            and board.getUnlocked(clickLoc).team == gamestate.teamPlaying:
            gamestate.pieceSelected = clickLoc
        else:
            gamestate.pieceSelected = None

    else:
        respawn_points = board.getFreeRespawnPointsForTeam(gamestate.teamRespawning)

        if clickLoc in respawn_points:
            if gamestate.teamRespawning == "gold":
                key = Key(clickLoc, "South", False, "gold")
                board.addPieceToLocation(clickLoc, key)
            elif gamestate.teamRespawning == "silver":
                key = Key(clickLoc, "North", False, "silver")
                board.addPieceToLocation(clickLoc, key)

            gamestate.setRespawnOff()
            board.collapse_locked()
            gamestate.changeTurn()

    print(gamestate.summarize())

def main():
    gamestate = GameState(Board.default())

    screen = Screen(fps=FPS, resolution=RESOLUTION, gamestate=gamestate)
    screen.init()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                handleKeyPress(
                    clickLoc=screen.getLocOfKeyPress(event),
                    gamestate=gamestate
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if gamestate.isGameOver:
            gamestate.reset()

        screen.update()

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

if __name__ == "__main__":
    setup_logging()
    main()
