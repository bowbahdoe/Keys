#Copyright 2014 Ethan McCue
#All rights reserved to MacaulayCore
#import Board

try:
    import pygame
except(ImportError):
    import pyj2d as pygame

GOLD_UNLOCKED_TEXTURE = pygame.image.load("img/yellow1.png")
SILVER_UNLOCKED_TEXTURE = pygame.image.load("img/silver1.png")
GOLD_LOCKED_TEXTURE = pygame.image.load("img/gold_lock.png")
SILVER_LOCKED_TEXTURE = pygame.image.load("img/silver_lock.png")

class Key:
    def __init__(self, location, direction, isLocked, team, selected=False):
        self.location = location
        self.dir = direction
        self.isLocked = isLocked
        self.team = team
        self.isSelected = selected

        if self.team == "gold":
            self.baseTex = GOLD_UNLOCKED_TEXTURE
            self.texture = GOLD_UNLOCKED_TEXTURE
        else:
            self.baseTex = SILVER_UNLOCKED_TEXTURE
            self.texture = SILVER_UNLOCKED_TEXTURE
        self._rotateTexture()

        self.frame = 1

    def _rotateTexture(self):
        """Transforms the texture of this Key to match its team and rotation"""
        if self.team == "gold":
            if self.dir == "East":
                self.texture =pygame.transform.rotate(self.baseTex,45)
            if self.dir == "SouthEast":
                self.texture =pygame.transform.rotate(self.baseTex,360)
            if self.dir == "South":
                self.texture =pygame.transform.rotate(self.baseTex,-40)
            if self.dir == "SouthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-90)
            if self.dir == "West":
                self.texture =pygame.transform.rotate(self.baseTex,-135)
            if self.dir == "NorthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-180)
            if self.dir == "North":
                self.texture =pygame.transform.rotate(self.baseTex,135)
            if self.dir == "NorthEast":
                self.texture =pygame.transform.rotate(self.baseTex,90)


        else:
            if self.dir == "East":
                self.texture =pygame.transform.rotate(self.baseTex,-45)
            if self.dir == "SouthEast":
                self.texture =pygame.transform.rotate(self.baseTex,-90)
            if self.dir == "South":
                self.texture =pygame.transform.rotate(self.baseTex,-135)
            if self.dir == "SouthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-180)
            if self.dir == "West":
                self.texture =pygame.transform.rotate(self.baseTex,135)
            if self.dir == "NorthWest":
                self.texture =pygame.transform.rotate(self.baseTex,90)
            if self.dir == "North":
                self.texture =pygame.transform.rotate(self.baseTex,45)
            if self.dir == "NorthEast":
                self.texture =pygame.transform.rotate(self.baseTex,0)

    def getDirection(self):
        return self.dir

    def setDirection(self, dir):
        self.dir = dir
        self._rotateTexture()


    def isLocked(self):
        return self.isLocked

    def lock(self):
        if self.team == "gold":
            self.texture = GOLD_LOCKED_TEXTURE
        else:
            self.texture = SILVER_LOCKED_TEXTURE

        self.isLocked = True

    def select(self):
        self.isSelected = not self.isSelected

    def getTexture(self):
        return self.texture
