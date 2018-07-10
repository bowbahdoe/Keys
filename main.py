import sys
import logging_setup
import logging
import itertools
from time import sleep
from board import Board
from key import Key
from location import makeLocCartesian, makeLocAlphaNumeric, only_cartesian_locations

import pygame
from pygame.locals import *

#These 2 need to be divisible by 8
DISPLAYHEIGHT = 600
DISPLAYWIDTH = 600
RESOLUTION = (DISPLAYHEIGHT,DISPLAYWIDTH)
SWIDTH = DISPLAYWIDTH // 8
SHEIGHT = DISPLAYHEIGHT // 8
FPS = 30
fpsclock = pygame.time.Clock()

SQUARESTOHIGHLIGHT = []
ROTATEPOINTS = []
RESPAWNPOINTS = []

class Respawn:
    def __init__(self):
        self.isRespawningNow = False
        self.teamRespawning = None

    def setRespawnOn(self,team):
        self.teamRespawning = team
        self.isRespawningNow = True

    def setRespawnOff(self):
        self.teamRespawning = None
        self.isRespawningNow = False

    def getTeamRespawning(self):
        return self.teamRespawning

class Turn:
    def __init__(self):
        self.turn = "gold"
        self.pieceSelected = None

    def getTurn(self):
        return self.turn

    def change(self):
        if self.turn == "gold":
            self.turn = "silver"
        else:
            self.turn ="gold"

    def setSelected(self,loc):
        self.pieceSelected = loc

def drawKeyAtLoc(display, key, loc):
    if key != None:
        texture = key.texture
        texture = pygame.transform.scale(texture, (SHEIGHT, SWIDTH))
        display.blit(texture, (SWIDTH*(loc[1]-1), SHEIGHT*(loc[0]-1)))

def drawKeysOnBoard(display, board):
    for loc in all_locations():
        key = board.getUnlocked(loc)
        drawKeyAtLoc(display, key, loc)

def drawLockedKeysOnBoard(display, board):
    for loc in all_locations():
        key = board.getLocked(loc)
        drawKeyAtLoc(display, key, loc)

def all_locations():
    """Returns an iterator over all the possible cartesian locations
    on an 8x8 board"""
    return itertools.product(range(1, 9), range(1, 9))

def drawBoard(display, color1=(0,0,0), color2=(100,100,100)):
    display.fill(color1)
    for row in range(8):
        for column in range(8):
            if column % 2 == row % 2:
                pygame.draw.rect(
                    display,
                    color2,
                    (column * SHEIGHT, row * SWIDTH, SHEIGHT, SWIDTH)
                )

@only_cartesian_locations
def highlightSquare(display, cartesian_loc, color):
    x = cartesian_loc[0]-1
    y = cartesian_loc[1]-1
    pygame.draw.rect(
        display,
        color,
        (x * SWIDTH, y * SHEIGHT, SWIDTH, SHEIGHT),
        5
    )

def handleKeyPress(event, *, display, board, turn, respawn):
    isRespawning = respawn.isRespawningNow
    alphaNumLoc = getLocOfKeyPress(event)

    tchange = False

    lockedPieceAtDest = board.getLocked(alphaNumLoc)
    unlockedPieceAtDest = board.getUnlocked(alphaNumLoc)
    if makeLocCartesian(alphaNumLoc) in SQUARESTOHIGHLIGHT and not isRespawning:
        if unlockedPieceAtDest != None:
            if unlockedPieceAtDest.team != board.getUnlocked(turn.pieceSelected).team:
                board.addLockedPieceToLocation(alphaNumLoc,unlockedPieceAtDest)
        if lockedPieceAtDest != None:
            if lockedPieceAtDest.team == board.getUnlocked(turn.pieceSelected).team:
                respawn.setRespawnOn(lockedPieceAtDest.team)
        board.movePieceToLocation(alphaNumLoc,board.getUnlocked(turn.pieceSelected))

        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        tchange = True
    elif makeLocCartesian(alphaNumLoc) in ROTATEPOINTS and not isRespawning:
        direc = board.getDirectionIndicatedByRotatePoint(makeLocCartesian(alphaNumLoc))
        piece = board.getUnlocked(turn.pieceSelected)

        piece.direction = direc
        board.addPieceToLocation(board.getUnlocked(turn.pieceSelected).location,
                                 piece)
        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        tchange = True

    elif board.isPieceAtLocation(alphaNumLoc) \
        and board.getUnlocked(alphaNumLoc).team == turn.getTurn() \
        and not isRespawning:
        turn.setSelected(alphaNumLoc)
        validMoves = board.getValidMovesOfKeyAtLoc(alphaNumLoc)
        validMoves.sort()
        SQUARESTOHIGHLIGHT.sort()
        rotatePrelim = board.getRotatePointsofKeyAtLoc(alphaNumLoc)
        if validMoves != SQUARESTOHIGHLIGHT:
            SQUARESTOHIGHLIGHT[:] =[]
            ROTATEPOINTS[:] = []
        for move in validMoves:
            remove = False
            if move in SQUARESTOHIGHLIGHT:
                SQUARESTOHIGHLIGHT.remove(move)
            else:
                SQUARESTOHIGHLIGHT.append(move)
            highlightSquare(display, (move[1], move[0]), (213,23,12))

        for i in rotatePrelim:
            if i in ROTATEPOINTS:
                ROTATEPOINTS.remove(i)
            else:
                ROTATEPOINTS.append(i)

    elif not isRespawning:
        SQUARESTOHIGHLIGHT[:] = []
        ROTATEPOINTS[:] = []

    if respawn.isRespawningNow:
        for i in board.getFreeRespawnPointsForTeam(respawn.getTeamRespawning()):
            if i not in RESPAWNPOINTS:
                RESPAWNPOINTS.append(makeLocCartesian(i))
        if (makeLocCartesian(alphaNumLoc)) in RESPAWNPOINTS:
            if respawn.getTeamRespawning() == "gold":
                key = Key(alphaNumLoc,"South",False,"gold")
                board.addPieceToLocation(alphaNumLoc,key)
            elif respawn.getTeamRespawning() == "silver":
                key = Key(alphaNumLoc,"North",False,"silver")
                board.addPieceToLocation(alphaNumLoc,key)
            RESPAWNPOINTS[:] = []
            respawn.setRespawnOff()
            board.collapse_locked()

    if tchange:
        turn.change()

def getLocOfKeyPress(event):
    log = logging.getLogger(__name__)

    log.debug("User clicked at %s", event.pos)
    clickX, clickY = event.pos
    return makeLocAlphaNumeric((clickY // SHEIGHT + 1, clickX // SWIDTH + 1))

def main():
    respawn = Respawn()
    turn = Turn()
    board = Board()
    board.setup()

    pygame.init()

    pygame.display.set_caption("Keys")

    display = pygame.display.set_mode(RESOLUTION)

    background = pygame.Surface(RESOLUTION)
    drawBoard(background)
    display.blit(background, (0,0))


    keys = pygame.Surface(RESOLUTION)
    drawKeysOnBoard(keys, board)
    display.blit(keys, (0,0))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                handleKeyPress(
                    event=event,
                    display=display,
                    board=board,
                    turn=turn,
                    respawn=respawn
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        display.blit(background,(0,0))
        drawLockedKeysOnBoard(display, board)
        drawKeysOnBoard(display, board)
        for location in ROTATEPOINTS:
            highlightSquare(display, (location[1], location[0]), (23,223,12))
        for location in SQUARESTOHIGHLIGHT:
            highlightSquare(display, (location[1], location[0]), (213,23,12))
        for location in RESPAWNPOINTS:
            highlightSquare(display, (location[1], location[0]), (233,34,223))

        if board.isGameOver:
            board.reset()

        pygame.display.update()
        fpsclock.tick(FPS)


if __name__ == "__main__":
    main()
