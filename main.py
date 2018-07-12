import sys
import logging
import itertools
import view
from board import Board
from key import Key
from location import makeLocCartesian, only_cartesian_locations

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

class GameState:
    def __init__(self):
        self.teamRespawning = None
        self.teamPlaying = "gold"
        self.pieceSelected = None

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

def drawKeyAtLoc(display, key, loc):
    if key != None:
        texture = view.key_texture(key)
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

def handleKeyPress(event, *, gamestate, board):
    isRespawning = gamestate.isRespawningNow
    clickLoc = getLocOfKeyPress(event)

    lockedPieceAtDest = board.getLocked(clickLoc)
    unlockedPieceAtDest = board.getUnlocked(clickLoc)

    if clickLoc in SQUARESTOHIGHLIGHT and not isRespawning:
        if unlockedPieceAtDest != None:
            if unlockedPieceAtDest.team != board.getUnlocked(gamestate.pieceSelected).team:
                board.addLockedPieceToLocation(clickLoc, unlockedPieceAtDest)
        if lockedPieceAtDest != None:
            if lockedPieceAtDest.team == board.getUnlocked(gamestate.pieceSelected).team:
                gamestate.setRespawnOn(lockedPieceAtDest.team)
        board.movePieceToLocation(clickLoc, board.getUnlocked(gamestate.pieceSelected))

        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        gamestate.changeTurn()
    elif clickLoc in ROTATEPOINTS and not isRespawning:
        direc = board.getDirectionIndicatedByRotatePoint(clickLoc)
        piece = board.getUnlocked(gamestate.pieceSelected)

        piece.direction = direc
        board.addPieceToLocation(board.getUnlocked(gamestate.pieceSelected).location,
                                 piece)
        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        gamestate.changeTurn()

    elif board.isPieceAtLocation(clickLoc) \
        and board.getUnlocked(clickLoc).team == gamestate.teamPlaying \
        and not isRespawning:
        gamestate.pieceSelected = clickLoc
        validMoves = board.validMovesOfKeyAtLoc(clickLoc)
        validMoves.sort()
        SQUARESTOHIGHLIGHT.sort()
        rotatePrelim = board.getRotatePointsofKeyAtLoc(clickLoc)
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

    if gamestate.isRespawningNow:
        for i in board.getFreeRespawnPointsForTeam(gamestate.teamRespawning):
            if i not in RESPAWNPOINTS:
                RESPAWNPOINTS.append(makeLocCartesian(i))
        if clickLoc in RESPAWNPOINTS:
            if gamestate.teamRespawning == "gold":
                key = Key(clickLoc, "South", False, "gold")
                board.addPieceToLocation(clickLoc, key)
            elif gamestate.teamRespawning == "silver":
                key = Key(clickLoc, "North", False, "silver")
                board.addPieceToLocation(clickLoc, key)
            RESPAWNPOINTS[:] = []
            gamestate.setRespawnOff()
            board.collapse_locked()

def getLocOfKeyPress(event):
    log = logging.getLogger(__name__)
    log.debug("User clicked at %s", event.pos)
    clickX, clickY = event.pos
    return (clickY // SHEIGHT + 1, clickX // SWIDTH + 1)

class Screen:
    def __init__(self, *, gamestate, board, resolution):
        self.gamestate = gamestate
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
    gamestate = GameState()
    board = Board.default()


    screen = Screen(resolution=RESOLUTION, gamestate=gamestate, board=board)
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
                    gamestate=gamestate
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if board.isGameOver:
            board.reset()

        screen.update()
        fpsclock.tick(FPS)

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
