#Copyright 2014 Ethan McCue
#All rights reserved to MacaulayCore

import pygame

GOLD_UNLOCKED_TEXTURE = pygame.image.load("img/yellow1.png")
SILVER_UNLOCKED_TEXTURE = pygame.image.load("img/silver1.png")
GOLD_LOCKED_TEXTURE = pygame.image.load("img/gold_lock.png")
SILVER_LOCKED_TEXTURE = pygame.image.load("img/silver_lock.png")

class Key:
    def __init__(self, location, direction, isLocked, team, selected=False):
        self.location = location
        self._direction = direction
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
            if self._direction == "East":
                self.texture = pygame.transform.rotate(self.baseTex,45)
            if self._direction == "SouthEast":
                self.texture = pygame.transform.rotate(self.baseTex,360)
            if self._direction == "South":
                self.texture = pygame.transform.rotate(self.baseTex,-40)
            if self._direction == "SouthWest":
                self.texture = pygame.transform.rotate(self.baseTex,-90)
            if self._direction == "West":
                self.texture = pygame.transform.rotate(self.baseTex,-135)
            if self._direction == "NorthWest":
                self.texture = pygame.transform.rotate(self.baseTex,-180)
            if self._direction == "North":
                self.texture = pygame.transform.rotate(self.baseTex,135)
            if self._direction == "NorthEast":
                self.texture = pygame.transform.rotate(self.baseTex,90)


        else:
            if self._direction == "East":
                self.texture = pygame.transform.rotate(self.baseTex,-45)
            if self._direction == "SouthEast":
                self.texture = pygame.transform.rotate(self.baseTex,-90)
            if self._direction == "South":
                self.texture = pygame.transform.rotate(self.baseTex,-135)
            if self._direction == "SouthWest":
                self.texture = pygame.transform.rotate(self.baseTex,-180)
            if self._direction == "West":
                self.texture = pygame.transform.rotate(self.baseTex,135)
            if self._direction == "NorthWest":
                self.texture = pygame.transform.rotate(self.baseTex,90)
            if self._direction == "North":
                self.texture = pygame.transform.rotate(self.baseTex,45)
            if self._direction == "NorthEast":
                self.texture = pygame.transform.rotate(self.baseTex,0)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, newDir):
        self._direction = newDir
        self._rotateTexture()

    def lock(self):
        if self.team == "gold":
            self.texture = GOLD_LOCKED_TEXTURE
        else:
            self.texture = SILVER_LOCKED_TEXTURE

        self.isLocked = True

    def select(self):
        self.isSelected = not self.isSelected
