import sys
import logging
import itertools
import view
from board import Board
from key import Key
from location import makeLocCartesian, only_cartesian_locations
from screen import Screen

import pygame
from pygame.locals import *

#These 2 need to be divisible by 8
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

def determine_mode(gamestate):
    """NOTE: Broken with the rest of the implementation.
    Should return the current gamestate for use in making the logic
    more useable from an outside program. """
    if gamestate.teamPlaying == "gold":
        prefix = "GOLD_"
    else:
        prefix = "SILVER_"

    if gamestate.isRespawningNow:
        return prefix + "RESPAWNING"
    elif gamestate.board.isGameOver:
        return prefix + "WIN"
    else:
        return prefix + "PLAY"


def handleKeyPress(*, clickLoc, gamestate):
    board = gamestate.board
    lockedPieceAtDest = board.getLocked(clickLoc)
    unlockedPieceAtDest = board.getUnlocked(clickLoc)
    isRespawning = gamestate.isRespawningNow

    if not isRespawning:
        if clickLoc in board.validMovesOfKeyAtLoc(gamestate.pieceSelected):
            if unlockedPieceAtDest != None:
                if unlockedPieceAtDest.team != board.getUnlocked(gamestate.pieceSelected).team:
                    board.addLockedPieceToLocation(clickLoc, unlockedPieceAtDest)
            if lockedPieceAtDest != None:
                if lockedPieceAtDest.team == board.getUnlocked(gamestate.pieceSelected).team:
                    gamestate.setRespawnOn(lockedPieceAtDest.team)
            board.movePieceToLocation(clickLoc, board.getUnlocked(gamestate.pieceSelected))

            gamestate.changeTurn()
            gamestate.pieceSelected = None

        elif clickLoc in board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected).values():
            def rev_dict(d):
                return {v: k for k, v in d.items()}
            direc = rev_dict(board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected))[clickLoc]
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

        if gamestate.board.isGameOver:
            gamestate.board.reset()

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
