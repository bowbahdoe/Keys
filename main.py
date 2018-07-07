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
DISPLAYHEIGHT = 600;
DISPLAYWIDTH = 600;
DISP = pygame.display.set_mode((DISPLAYHEIGHT,DISPLAYWIDTH))
SWIDTH = DISPLAYWIDTH//8
SHEIGHT = DISPLAYHEIGHT//8
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
        drawKeyAtLoc(DISP, key, loc)

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

def handleKeyPress(event, board, turn, respawn):
    isRespawning = respawn.isRespawningNow
    alphaNumLoc = getLocOfKeyPress(event)


    tchange = False

    lockedPieceAtDest = board.getLocked(alphaNumLoc)
    unlockedPieceAtDest = board.getUnlocked(alphaNumLoc)
    if tuple(makeLocCartesian(alphaNumLoc)) in SQUARESTOHIGHLIGHT and not isRespawning:
        if unlockedPieceAtDest!= None:
            if unlockedPieceAtDest.team != board.getUnlocked(turn.pieceSelected).team:
                board.addLockedPieceToLocation(alphaNumLoc,unlockedPieceAtDest)
        if lockedPieceAtDest != None:
            if lockedPieceAtDest.team == board.getUnlocked(turn.pieceSelected).team:
                respawn.setRespawnOn(lockedPieceAtDest.team)
                #BOARD.unlockPieceAtLocation(alphaNumLoc)
        board.movePieceToLocation(alphaNumLoc,board.getUnlocked(turn.pieceSelected))

        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        tchange = True
    elif tuple(makeLocCartesian(alphaNumLoc)) in ROTATEPOINTS and not isRespawning:
        direc = board.getDirectionIndicatedByRotatePoint(makeLocCartesian(alphaNumLoc))
        piece = board.getUnlocked(turn.pieceSelected)

        piece.direction = direc
        board.addPieceToLocation(board.getUnlocked(turn.pieceSelected).location,
                                 piece)
        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        tchange = True
    elif board.isPieceAtLocation(alphaNumLoc) and board.getUnlocked(alphaNumLoc).team == turn.getTurn() and not isRespawning:
        turn.setSelected(alphaNumLoc)
        y = board.getValidMovesOfKeyAtLoc(alphaNumLoc)
        y.sort()
        SQUARESTOHIGHLIGHT.sort()
        rotatePrelim = board.getRotatePointsofKeyAtLoc(alphaNumLoc)
        if y != SQUARESTOHIGHLIGHT:
            SQUARESTOHIGHLIGHT[:] =[]
            ROTATEPOINTS[:] = []
        for i in y:

            remove = False
            if i in SQUARESTOHIGHLIGHT:
                SQUARESTOHIGHLIGHT.remove(i)
            else:
                SQUARESTOHIGHLIGHT.append(i)

            highlightSquare(DISP, (i[1],i[0]), (213,23,12))
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

    returner = ""
    #Alpha part
    if clickY in range(SHEIGHT):
        returner += "A"
    elif clickY in range(((SHEIGHT)),(SHEIGHT)*2):
        returner += "B"
    elif clickY in range(((SHEIGHT)*2),(SHEIGHT)*3):
        returner += "C"
    elif clickY in range(((SHEIGHT)*3),(SHEIGHT)*4):
        returner += "D"
    elif clickY in range(((SHEIGHT)*4),(SHEIGHT)*5):
        returner += "E"
    elif clickY in range(((SHEIGHT)*5),(SHEIGHT)*6):
        returner += "F"
    elif clickY in range(((SHEIGHT)*6),(SHEIGHT)*7):
        returner += "G"
    elif clickY in range(((SHEIGHT)*7),(SHEIGHT)*8):
        returner += "H"
    else:
        raise AssertionError(
            "The Y-Coordinate of the user's click was out of bounds.",
            event.pos
        )

    #numeric Part
    if clickX in range(SWIDTH):
        returner += "1"
    elif clickX in range(((SWIDTH)),(SWIDTH)*2):
        returner += "2"
    elif clickX in range(((SWIDTH)*2),(SWIDTH)*3):
        returner += "3"
    elif clickX in range(((SWIDTH)*3),(SWIDTH)*4):
        returner += "4"
    elif clickX in range(((SWIDTH)*4),(SWIDTH)*5):
        returner += "5"
    elif clickX in range(((SWIDTH)*5),(SWIDTH)*6):
        returner += "6"
    elif clickX in range(((SWIDTH)*6),(SWIDTH)*7):
        returner += "7"
    elif clickX in range(((SWIDTH)*7),(SWIDTH)*8):
        returner += "8"
    else:
        raise AssertionError(
            "The X-Coordinate of the user's click was out of bounds.",
            event.pos
        )

    return returner

def main():
    respawn = Respawn()
    turn = Turn()
    background = pygame.Surface((DISPLAYHEIGHT,DISPLAYWIDTH))
    drawBoard(background)
    pygame.init()

    pygame.display.set_caption("Keys")

    keys = pygame.Surface((DISPLAYHEIGHT,DISPLAYWIDTH))
    drawKeysOnBoard(keys,BOARD)

    DISP.blit(background,(0,0))
    DISP.blit(keys,(0,0))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                handleKeyPress(event, BOARD, turn,respawn)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        DISP.blit(background,(0,0))
        drawLockedKeysOnBoard(DISP,BOARD)
        drawKeysOnBoard(DISP,BOARD)
        for i in ROTATEPOINTS:
            highlightSquare(DISP, (i[1],i[0]), (23,223,12))
        for i in SQUARESTOHIGHLIGHT:
            highlightSquare(DISP, (i[1],i[0]), (213,23,12))

        for i in RESPAWNPOINTS:
            highlightSquare(DISP, (i[1],i[0]), (233,34,223))

        if BOARD.isGameOver():
            BOARD.reset()

        pygame.display.update()
        fpsclock.tick(FPS)

BOARD = Board()
BOARD.setup()



if __name__ == "__main__":
    main()
