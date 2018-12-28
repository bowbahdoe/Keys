import sys
import logging
from board import Board
from key import Key
from location import makeLocCartesian, only_cartesian_locations
from screen import Screen
from gamestate import GameState, Move, NoOp, Rotate, Respawn
import pygame
from pygame.locals import *

# These 2 need to be divisible by 8
DISPLAYHEIGHT = 600
DISPLAYWIDTH = 600
RESOLUTION = (DISPLAYHEIGHT,DISPLAYWIDTH)
FPS = 30

def determine_move(*, clickLoc, gamestate):
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
    log = logging.getLogger(__name__)

    move = determine_move(clickLoc = clickLoc, gamestate = gamestate)
    log.info(f"Executing Move: {move}")
    move(gamestate)

    board = gamestate.board
    lockedPieceAtDest = board.getLocked(clickLoc)
    unlockedPieceAtDest = board.getUnlocked(clickLoc)

    if not gamestate.isRespawningNow:
        if board.isPieceAtLocation(clickLoc) \
            and board.getUnlocked(clickLoc).team == gamestate.teamPlaying:
            gamestate.pieceSelected = clickLoc
        else:
            gamestate.pieceSelected = None
    else:
        pass

    log.info(f"Gamestate is now {gamestate.summarize()}")

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
