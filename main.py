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
FPS = 30

SQUARESTOHIGHLIGHT = []
ROTATEPOINTS = []

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

def determine_mode(gamestate, board):
    """NOTE: Broken with the rest of the implementation.
    Should return the current gamestate for use in making the logic
    more useable from an outside program. """
    if gamestate.teamPlaying == "gold":
        prefix = "GOLD_"
    else:
        prefix = "SILVER_"

    if gamestate.isRespawningNow:
        return prefix + "RESPAWNING"
    elif board.isGameOver:
        return prefix + "WIN"
    else:
        return prefix + "PLAY"


def handleKeyPress(*, clickLoc, gamestate, board):
    isRespawning = gamestate.isRespawningNow
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
        def rev_dict(d):
            return {v: k for k, v in d.items()}
        direc = rev_dict(board.getRotatePointsofKeyAtLoc(gamestate.pieceSelected))[clickLoc]
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
        rotatePrelim = board.getRotatePointsofKeyAtLoc(clickLoc).values()
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


class Screen:
    def __init__(self, *, fps, gamestate, board, resolution):
        self.gamestate = gamestate
        self.board = board
        self.resolution = resolution
        self.fps = fps

    def init(self):
        pygame.init()
        pygame.display.set_caption("Keys")
        self._display = pygame.display.set_mode(self.resolution)
        self._fpsclock = pygame.time.Clock()
        self.update()
        return self

    def getLocOfKeyPress(self, event):
        log = logging.getLogger(__name__)
        log.debug("User clicked at %s", event.pos)
        clickX, clickY = event.pos
        board_location = (clickY // self._sheight + 1, clickX // self._swidth + 1)
        log.debug("Click Interpreted as being at %s", board_location)
        return board_location

    @property
    def _swidth(self):
        return self.resolution[0] // 8

    @property
    def _sheight(self):
        return self.resolution[1] // 8

    @property
    def _background(self):
        background = self._transparent_surface()
        self._drawBoard(background)
        return background

    @property
    def _unlocked_keys(self):
        unlocked_keys = self._transparent_surface()
        self._drawKeysOnBoard(unlocked_keys, self.board)
        return unlocked_keys

    @property
    def _locked_keys(self):
        locked_keys = self._transparent_surface()
        self._drawLockedKeysOnBoard(locked_keys, self.board)
        return locked_keys

    def _transparent_surface(self):
        surface = pygame.Surface(self.resolution, pygame.SRCALPHA, 32)
        surface.convert_alpha()
        return surface

    def update(self):
        def draw(surface):
            self._display.blit(surface, (0, 0))

        draw(self._background)
        draw(self._locked_keys)
        draw(self._unlocked_keys)


        for location in ROTATEPOINTS:
            self._highlightSquare(self._display, (location[1], location[0]), (23,223,12))

        for location in SQUARESTOHIGHLIGHT:
            self._highlightSquare(self._display, (location[1], location[0]), (213,23,12))

        for location in self.board.getFreeRespawnPointsForTeam(self.gamestate.teamRespawning):
            self._highlightSquare(self._display, (location[1], location[0]), (233,34,223))

        pygame.display.update()
        self._fpsclock.tick(self.fps)

    def _drawKeyAtLoc(self, display, key, loc):
        if key != None:
            texture = view.key_texture(key)
            texture = pygame.transform.scale(texture, (self._sheight, self._swidth))
            display.blit(texture, (self._swidth*(loc[1]-1), self._sheight*(loc[0]-1)))

    def _drawKeysOnBoard(self, display, board):
        for loc in Screen._all_locations():
            key = board.getUnlocked(loc)
            self._drawKeyAtLoc(display, key, loc)

    def _drawLockedKeysOnBoard(self, display, board):
        for loc in Screen._all_locations():
            key = board.getLocked(loc)
            self._drawKeyAtLoc(display, key, loc)

    @staticmethod
    def _all_locations():
        """Returns an iterator over all the possible cartesian locations
        on an 8x8 board"""
        return itertools.product(range(1, 9), range(1, 9))

    def _drawBoard(self, display, color1=(0,0,0), color2=(100,100,100)):
        display.fill(color1)
        for row in range(8):
            for column in range(8):
                if column % 2 == row % 2:
                    pygame.draw.rect(
                        display,
                        color2,
                        (column * self._sheight, row * self._swidth, self._sheight, self._swidth)
                    )


    @only_cartesian_locations
    def _highlightSquare(self, display, cartesian_loc, color):
        x = cartesian_loc[0] - 1
        y = cartesian_loc[1] - 1
        pygame.draw.rect(
            display,
            color,
            (x * self._swidth, y * self._sheight, self._swidth, self._sheight),
            5
        )

def main():
    gamestate = GameState()
    board = Board.default()


    screen = Screen(fps=FPS, resolution=RESOLUTION, gamestate=gamestate, board=board)
    screen.init()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                handleKeyPress(
                    clickLoc=screen.getLocOfKeyPress(event),
                    board=board,
                    gamestate=gamestate
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if board.isGameOver:
            board.reset()

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
