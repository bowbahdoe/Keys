#Copyright 2014 Ethan McCue
#All rights reserved to MacaulayCore
#import Board

try:
    import pygame
except(ImportError):
    import pyj2d as pygame

class Key:
    def __init__(self, location, direction, isLocked, team, selected=False):
        self.loc = location
        self.dir = direction
        self.isLocked = isLocked
        self.team = team
        self.isSelected = selected

        if self.team == "gold":
            self.baseTex = pygame.image.load("img/yellow1.png")
            self.texture = pygame.image.load("img/yellow1.png")
        else:
            self.baseTex = pygame.image.load("img/silver1.png")
            self.texture = pygame.image.load("img/silver1.png")
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

    def getLocation(self):
        return self.loc

    def setLocation(self, loc):
        self.loc = loc

    def getDirection(self):
        return self.dir

    def setDirection(self, dir):
        self.dir = dir
        self._rotateTexture()


    def isLocked(self):
        return self.isLocked

    def setLocked(self, locked):
        '''True or False'''
        if self.team=="gold":
            self.texture = pygame.image.load("img/gold_lock.png")
        else:
            self.texture = pygame.image.load("img/silver_lock.png")

        if locked:
            self.isLocked = True
        else:
            self.isLocked = False

    def getTeam(self):
        return self.team

    def setTeam(self, team):
        if self.team == "gold":
            self.texture = pygame.image.load("img/key-icon.png")
        else:
            self.texture = pygame.image.load("img/silver1.png")

    def select(self):
        self.isSelected = not self.isSelected

    def getTexture(self):
        return self.texture
