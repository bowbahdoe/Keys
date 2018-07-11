import sys
import logging_setup
import logging
import itertools
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
        self.teamRespawning = None

    def setRespawnOn(self,team):
        self.teamRespawning = team

    def setRespawnOff(self):
        self.teamRespawning = None

    @property
    def isRespawningNow(self):
        return self.teamRespawning != None

class Turn:
    def __init__(self):
        self.teamPlaying = "gold"
        self.pieceSelected = None

    def change(self):
        if self.teamPlaying == "gold":
            self.teamPlaying = "silver"
        else:
            self.teamPlaying = "gold"

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
    x = cartesian_loc[0] - 1
    y = cartesian_loc[1] - 1
    pygame.draw.rect(
        display,
        color,
        (x * SWIDTH, y * SHEIGHT, SWIDTH, SHEIGHT),
        5
    )

def handleKeyPress(event, *, board, turn, respawn):
    isRespawning = respawn.isRespawningNow
    alphaNumLoc = getLocOfKeyPress(event)

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
        turn.change()
    elif makeLocCartesian(alphaNumLoc) in ROTATEPOINTS and not isRespawning:
        direc = board.getDirectionIndicatedByRotatePoint(makeLocCartesian(alphaNumLoc))
        piece = board.getUnlocked(turn.pieceSelected)

        piece.direction = direc
        board.addPieceToLocation(board.getUnlocked(turn.pieceSelected).location,
                                 piece)
        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        turn.change()

    elif board.isPieceAtLocation(alphaNumLoc) \
        and board.getUnlocked(alphaNumLoc).team == turn.teamPlaying \
        and not isRespawning:
        turn.pieceSelected = alphaNumLoc
        validMoves = board.validMovesOfKeyAtLoc(alphaNumLoc)
        validMoves.sort()
        SQUARESTOHIGHLIGHT.sort()
        rotatePrelim = board.getRotatePointsofKeyAtLoc(alphaNumLoc)
        if validMoves != SQUARESTOHIGHLIGHT:
            SQUARESTOHIGHLIGHT[:] =[]
            ROTATEPOINTS[:] = []
        for move in validMoves:
            if move in SQUARESTOHIGHLIGHT:
                SQUARESTOHIGHLIGHT.remove(move)
            else:
                SQUARESTOHIGHLIGHT.append(move)

        for i in rotatePrelim:
            if i in ROTATEPOINTS:
                ROTATEPOINTS.remove(i)
            else:
                ROTATEPOINTS.append(i)

    elif not isRespawning:
        SQUARESTOHIGHLIGHT[:] = []
        ROTATEPOINTS[:] = []

    if respawn.isRespawningNow:
        for i in board.getFreeRespawnPointsForTeam(respawn.teamRespawning):
            if i not in RESPAWNPOINTS:
                RESPAWNPOINTS.append(makeLocCartesian(i))
        if makeLocCartesian(alphaNumLoc) in RESPAWNPOINTS:
            if respawn.teamRespawning == "gold":
                key = Key(alphaNumLoc,"South",False,"gold")
                board.addPieceToLocation(alphaNumLoc,key)
            elif respawn.teamRespawning == "silver":
                key = Key(alphaNumLoc,"North",False,"silver")
                board.addPieceToLocation(alphaNumLoc,key)
            RESPAWNPOINTS[:] = []
            respawn.setRespawnOff()
            board.collapse_locked()

def getLocOfKeyPress(event):
    log = logging.getLogger(__name__)
    log.debug("User clicked at %s", event.pos)
    clickX, clickY = event.pos
    return makeLocAlphaNumeric((clickY // SHEIGHT + 1, clickX // SWIDTH + 1))

class Screen:
    def __init__(self, *, board, resolution):
        self.board = board
        self.resolution = resolution

    def init(self):
        pygame.init()
        pygame.display.set_caption("Keys")
        self._display = pygame.display.set_mode(self.resolution)
        self.update()

    @property
    def _background(self):
        background = self._transparent_surface()
        drawBoard(background)
        return background

    @property
    def _unlocked_keys(self):
        unlocked_keys = self._transparent_surface()
        drawKeysOnBoard(unlocked_keys, self.board)
        return unlocked_keys

    @property
    def _locked_keys(self):
        locked_keys = self._transparent_surface()
        drawLockedKeysOnBoard(locked_keys, self.board)
        return locked_keys

    @property
    def display(self):
        if self._display == None:
            raise Exception("The display has not been created yet")
        else:
            return self._display

    def _transparent_surface(self):
        surface = pygame.Surface(self.resolution, pygame.SRCALPHA, 32)
        surface.convert_alpha()
        return surface

    def update(self):
        def draw(surface):
            self.display.blit(surface, (0, 0))

        draw(self._background)
        draw(self._locked_keys)
        draw(self._unlocked_keys)

        for location in ROTATEPOINTS:
            highlightSquare(self.display, (location[1], location[0]), (23,223,12))
        for location in SQUARESTOHIGHLIGHT:
            highlightSquare(self.display, (location[1], location[0]), (213,23,12))
        for location in RESPAWNPOINTS:
            highlightSquare(self.display, (location[1], location[0]), (233,34,223))

        pygame.display.update()

def main():
    respawn = Respawn()
    turn = Turn()
    board = Board.default()


    screen = Screen(resolution=RESOLUTION, board=board)
    screen.init()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                handleKeyPress(
                    event=event,
                    board=board,
                    turn=turn,
                    respawn=respawn
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if board.isGameOver:
            board.reset()

        screen.update()
        fpsclock.tick(FPS)


if __name__ == "__main__":
    main()
