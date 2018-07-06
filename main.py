from __future__ import print_function

import sys
import logging_setup
import logging
from time import sleep
from board import Board
from key import Key
from location import makeLocCartesian, makeLocAlphaNumeric

log = logging.getLogger(__name__)

try:
    import pygame
    from pygame.locals import *
    JAVA = False
except(ImportError):
    import pyj2d as pygame
    from pyj2d.locals import *
    JAVA = True

try:
    import android
except(ImportError):
    android = None

if android:
    #(0,0) makes the display the size of the physical screen
    #On android, we want this (varying resolutions, etc)
    DISP = pygame.display.set_mode((0,0))
    DISPLAYHEIGHT = DISP.get_size()[0];
    DISPLAYWIDTH = DISP.get_size()[1];
else:
    #These 2 need to be divisible by 8
    DISPLAYHEIGHT = 600;
    DISPLAYWIDTH = 600;
    DISP = pygame.display.set_mode((DISPLAYHEIGHT,DISPLAYWIDTH))
SWIDTH = DISPLAYHEIGHT//8
SHEIGHT = DISPLAYWIDTH//8
FPS = 12
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
    def getIfRespawningNow(self):
        return self.isRespawningNow
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

def drawKeyAtLoc(DISP,key,loc):
    if key != None:
        texture = key.getTexture()
        loc = makeLocCartesian(loc)
        texture =pygame.transform.scale(texture,(DISPLAYHEIGHT//8,DISPLAYWIDTH//8))
        DISP.blit(texture,(SWIDTH*(loc[1]-1),SHEIGHT*(loc[0]-1)))

def drawKeysOnBoard(DISP,Board):
    x = ['A','B','C','D','E','F','G','H']
    for i in x:
        for e in range(8):
            loc = i+str(e + 1)
            key = Board.getPieceAtLocation(loc)
            drawKeyAtLoc(DISP,key,loc)

def drawLockedKeysOnBoard(DISP,Board):
    x = ['A','B','C','D','E','F','G','H']
    for i in x:
        for e in range(8):
            loc = i+str(e + 1)
            key = Board.getLockedPieceAtLocation(loc)
            drawKeyAtLoc(DISP,key,loc)

def drawBoard(DisplayObj,color1=(0,0,0),color2=(100,100,100)):
    DisplayObj.fill(color1)
    square_width = DISPLAYWIDTH // 8
    square_height = DISPLAYHEIGHT // 8

    for row in range(8):
        for column in range(8):
            if column % 2 == row % 2:
                pygame.draw.rect(
                    DisplayObj,
                    color2,
                    (column * square_height, row * square_width, square_height, square_width)
                )

def highlightSquare(loc,DisplayObj,color):
    '''loc is a cartesian cordinate'''
    RectHeight = DISPLAYHEIGHT//16
    RectWidth = DISPLAYHEIGHT//16
    x = loc[0]-1
    y = loc[1]-1
    pygame.draw.rect(DisplayObj,color,((x)*(SWIDTH),(SHEIGHT)*(y),SWIDTH,SHEIGHT),5)

def handleKeyPress(event,turn,respawn):
    shouldUpdate =1
    a = respawn.isRespawningNow
    z = getLocOfKeyPress(event)


    tchange = False

    lockedPieceAtDest = BOARD.getLockedPieceAtLocation(z)
    unlockedPieceAtDest = BOARD.getPieceAtLocation(z)
    if tuple(makeLocCartesian(z)) in SQUARESTOHIGHLIGHT and not a:
        if unlockedPieceAtDest!= None:

            if unlockedPieceAtDest.team != BOARD.getPieceAtLocation(turn.pieceSelected).team:
                BOARD.addLockedPieceToLocation(z,unlockedPieceAtDest)
        if lockedPieceAtDest != None:
            if lockedPieceAtDest.team == BOARD.getPieceAtLocation(turn.pieceSelected).team:
                respawn.setRespawnOn(lockedPieceAtDest.team)
                #BOARD.unlockPieceAtLocation(z)
        BOARD.movePieceToLocation(z,BOARD.getPieceAtLocation(turn.pieceSelected))

        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        tchange = True
    elif tuple(makeLocCartesian(z)) in ROTATEPOINTS and not a:
        direc = BOARD.getDirectionIndicatedByRotatePoint(makeLocCartesian(z))
        piece = BOARD.getPieceAtLocation(turn.pieceSelected)

        piece.setDirection(direc)
        BOARD.addPieceToLocation(BOARD.getPieceAtLocation(turn.pieceSelected).location,
                                 piece)
        SQUARESTOHIGHLIGHT[:] =[]
        ROTATEPOINTS[:] = []
        tchange = True
    elif BOARD.isPieceAtLocation(z) and BOARD.getPieceAtLocation(z).team == turn.getTurn() and not a:
        turn.setSelected(z)
        y = BOARD.getValidMovesOfKeyAtLoc(z)
        y.sort()
        SQUARESTOHIGHLIGHT.sort()
        rotatePrelim = BOARD.getRotatePointsofKeyAtLoc(z)
        if y != SQUARESTOHIGHLIGHT:
            SQUARESTOHIGHLIGHT[:] =[]
            ROTATEPOINTS[:] = []
        for i in y:

            remove = False
            if i in SQUARESTOHIGHLIGHT:
                SQUARESTOHIGHLIGHT.remove(i)
            else:
                SQUARESTOHIGHLIGHT.append(i)

            highlightSquare((i[1],i[0]),DISP,(213,23,12))
        for i in rotatePrelim:
            if i in ROTATEPOINTS:
                ROTATEPOINTS.remove(i)
            else:
                ROTATEPOINTS.append(i)
    elif not a:
        SQUARESTOHIGHLIGHT[:] = []
        ROTATEPOINTS[:] = []
    if respawn.isRespawningNow:
        for i in BOARD.getFreeRespawnPointsForTeam(respawn.getTeamRespawning()):
            if i not in RESPAWNPOINTS:
                RESPAWNPOINTS.append(makeLocCartesian(i))
        if (makeLocCartesian(z)) in RESPAWNPOINTS:
            if respawn.getTeamRespawning() == "gold":
                key = Key(z,"South",False,"gold")
                BOARD.addPieceToLocation(z,key)
            elif respawn.getTeamRespawning() == "silver":
                key = Key(z,"North",False,"silver")
                BOARD.addPieceToLocation(z,key)
            RESPAWNPOINTS[:] = []
            respawn.setRespawnOff()
            for place in BOARD.board:
                unlockedPiece = place[1]
                lockedPiece = place[2]
                if(not(unlockedPiece==None or lockedPiece==None)):
                    if lockedPiece.team == unlockedPiece.team:
                        place[2] = None
    if tchange:
        turn.change()

def getLocOfKeyPress(event):

    pos = [event.pos[0],event.pos[1]]
    if JAVA:
        pos = [event.pos[0]-3,event.pos[1]-25]

    returner = ""
    log.debug("User clicked at %s", pos)
    #Alpha part
    if pos[1] in range(SHEIGHT):
        returner += "A"
    elif pos[1] in range(((SHEIGHT)),(SHEIGHT)*2):
        returner += "B"
    elif pos[1] in range(((SHEIGHT)*2),(SHEIGHT)*3):
        returner += "C"
    elif pos[1] in range(((SHEIGHT)*3),(SHEIGHT)*4):
        returner += "D"
    elif pos[1] in range(((SHEIGHT)*4),(SHEIGHT)*5):
        returner += "E"
    elif pos[1] in range(((SHEIGHT)*5),(SHEIGHT)*6):
        returner += "F"
    elif pos[1] in range(((SHEIGHT)*6),(SHEIGHT)*7):
        returner += "G"
    elif pos[1] in range(((SHEIGHT)*7),(SHEIGHT)*8):
        returner += "H"

    #numeric Part
    if pos[0] in range(SWIDTH):
        returner += "1"
    elif pos[0] in range(((SWIDTH)),(SWIDTH)*2):
        returner += "2"
    elif pos[0] in range(((SWIDTH)*2),(SWIDTH)*3):
        returner += "3"
    elif pos[0] in range(((SWIDTH)*3),(SWIDTH)*4):
        returner += "4"
    elif pos[0] in range(((SWIDTH)*4),(SWIDTH)*5):
        returner += "5"
    elif pos[0] in range(((SWIDTH)*5),(SWIDTH)*6):
        returner += "6"
    elif pos[0] in range(((SWIDTH)*6),(SWIDTH)*7):
        returner += "7"
    elif pos[0] in range(((SWIDTH)*7),(SWIDTH)*8):
        returner += "8"

    return returner

def resetGame():
    print("resetting")
    sleep(3)
    BOARD.reset()
    BOARD.isResetting= False

def drawGameOverScreen(Display,background=(0,0,0),winner="none"):
    Display.fill((0,0,0))
    try:
        myfont = pygame.font.SysFont("monospace", 40)
        label = myfont.render(winner +" has lost", 3, (DISP,0,0))
        Display.blit(label, (SWIDTH, SHEIGHT))
    except:
        pass
    fpsclock.tick(1)
    pygame.display.update()

def main():
    if android:
        android.init()
        android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
    respawn = Respawn()
    turn = Turn()
    background = pygame.Surface((DISPLAYHEIGHT,DISPLAYWIDTH))
    drawBoard(background)
    shouldUpdate = 1
    pygame.init()

    pygame.display.set_caption("Keys")

    keys = pygame.Surface((DISPLAYHEIGHT,DISPLAYWIDTH))
    drawKeysOnBoard(keys,BOARD)

    DISP.blit(background,(0,0))
    DISP.blit(keys,(0,0))
    while True:

        if android:
            if android.check_pause():
                android.wait_for_resume()

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                handleKeyPress(event,turn,respawn)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            shouldUpdate = 1

        shouldUpdate = 1

        if shouldUpdate:
            DISP.blit(background,(0,0))
            drawLockedKeysOnBoard(DISP,BOARD)
            drawKeysOnBoard(DISP,BOARD)
            for i in ROTATEPOINTS:
                highlightSquare((i[1],i[0]),DISP,(23,223,12))
            for i in SQUARESTOHIGHLIGHT:
                highlightSquare((i[1],i[0]),DISP,(213,23,12))

            for i in RESPAWNPOINTS:
                highlightSquare((i[1],i[0]),DISP,(233,34,223))

            if BOARD.isGameOver():
                    fpsclock.tick(1)
                    BOARD.reset()

            pygame.display.update()
        fpsclock.tick(FPS)

BOARD = Board()
BOARD.setup()
shouldUpdate = 1


if __name__ == "__main__":
    main()
